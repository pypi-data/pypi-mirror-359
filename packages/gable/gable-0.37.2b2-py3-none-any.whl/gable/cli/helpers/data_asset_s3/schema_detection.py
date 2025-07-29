"""
schema_detection.py
===================
Robust S3 schema inference with DuckDB/Arrow.
 • Zero pandas
 • Wrapper/format detection by magic-bytes
 • Decompress only when DuckDB cannot stream the file as-is
"""

from __future__ import annotations
import io, os, tempfile, urllib.parse
from dataclasses import dataclass
from typing import Optional, Dict, Tuple

import boto3, duckdb, fastavro, pyarrow as pa
from mypy_boto3_s3 import S3Client
from loguru import logger
from botocore.exceptions import ClientError

from gable.cli.helpers.data_asset_s3.compression_handler import CompressionHandler, FileFormat, CompressionWrapper
from gable.cli.helpers.data_asset_s3.native_s3_converter  import NativeS3Converter, merge_schemas
from gable.cli.helpers.data_asset_s3.schema_profiler       import (
    get_data_asset_field_profiles_for_data_asset,
)
from gable.openapi import S3SamplingParameters, DataAssetFieldsToProfilesMapping

duckdb.query("INSTALL httpfs; LOAD httpfs;")
# duckdb.query("INSTALL orc;   LOAD orc;")  # load ORC extension only if used

# ───────────────────────── dataclasses ─────────────────────────
@dataclass
class S3DetectionResult:
    schema: dict
    data_asset_fields_to_profiles_map: Optional[DataAssetFieldsToProfilesMapping] = None


# ───────────────────────── helper: sniff 64 KB ─────────────────────────
def _sniff_wrapper_and_format(
    handler: CompressionHandler, key: str, head: bytes
) -> Tuple[CompressionWrapper, FileFormat]:
    """
    Return wrapper, format
    e.g. (CompressionWrapper.GZ, FileFormat.CSV) or (None, FileFormat.PARQUET)
    """
    real_fmt = handler.get_original_format(key, head)            # FileFormat enum
    wrapper = handler.detect_compression_by_magic_bytes(head)    # CompressionWrapper enum
    
    if wrapper == CompressionWrapper.NONE:
        # fall back to filename for wrapper (.gz/.zip/.snappy)
        for part in key.lower().split("."):
            if part in handler.COMPRESSION_EXTENSIONS:
                wrapper = CompressionWrapper.from_extension(part)
                break
    
    return wrapper, real_fmt


# ───────────────────────── helper: read via DuckDB ─────────────────────
def _relation_from_path(path: str, fmt: FileFormat, rows: int):
    """
    Return a DuckDB relation that contains *rows* sample rows.
    """
    if fmt in (FileFormat.CSV, FileFormat.TSV):
        delim = "\t" if fmt == FileFormat.TSV else ","
        q = f"SELECT * FROM read_csv_auto('{path}', delim='{delim}', header=True) LIMIT {rows}"
    elif fmt == FileFormat.JSON:
        q = f"SELECT * FROM read_json_auto('{path}') LIMIT {rows}"
    elif fmt == FileFormat.PARQUET:
        q = f"SELECT * FROM read_parquet('{path}') LIMIT {rows}"
    elif fmt == FileFormat.ORC:
        q = f"SELECT * FROM read_orc('{path}') LIMIT {rows}"
    elif fmt == FileFormat.AVRO:
        q = f"SELECT * FROM read_avro('{path}') LIMIT {rows}"
    else:
        raise ValueError(f"Unsupported format: {fmt}")
    return duckdb.query(q)


# ─────────────────────────── main routine ──────────────────────────────
def read_s3_files_with_schema_inference(
    *,
    s3_urls: list[str],
    row_sample_count: int,
    event_name: str,
    recent_file_count: int,
    skip_profiling: bool = False,
    s3_client: S3Client = None, # type: ignore
) -> Optional[S3DetectionResult]:
    s3 = s3_client or boto3.client("s3")
    handler   = CompressionHandler()
    converter = NativeS3Converter()
    data_map: Dict[str, Tuple[duckdb.DuckDBPyRelation | pa.Table, dict]] = {}

    for url in s3_urls:
        parsed  = urllib.parse.urlparse(url)
        bucket  = parsed.netloc
        key     = parsed.path.lstrip("/")
        ext_raw = os.path.splitext(key)[1].lower()

        # 0️⃣  sniff first 64 KB
        try:
            head_bytes = s3.get_object(
                Bucket=bucket, Key=key, Range="bytes=0-65535"
            )["Body"].read()
            if len(head_bytes) == 0:
                # explicit wording so we can assert on it in unit-tests
                logger.error(f"[SchemaDetect] skip {url}: empty S3 object – no data")
                # treat just like any other unusable sample: continue the loop
                continue
        except ClientError as e:
            # empty objects raise InvalidRange on a ranged GET → treat as zero bytes
            error_code = e.response.get("Error", {}).get("Code")
            if error_code == "InvalidRange":
                head_bytes = b""
            else:
                raise
        wrapper, fmt = _sniff_wrapper_and_format(handler, key, head_bytes)

        # fallback if extension was already good
        if fmt == FileFormat.UNKNOWN and ext_raw not in ("", ".gz", ".zip", ".snappy"):
            fmt = FileFormat.from_extension(ext_raw)

        if fmt == FileFormat.UNKNOWN:
            logger.error(f"[SchemaDetect] cannot determine format for {url}")
            continue

        # 1️⃣  Avro with *no* wrapper → Arrow + fastavro quickest
        if fmt == FileFormat.AVRO and wrapper == CompressionWrapper.NONE:
            whole = s3.get_object(Bucket=bucket, Key=key)["Body"].read()
            try:
                records = list(fastavro.reader(io.BytesIO(whole)))
            except Exception as e:                       # header-only, truncated, …
                logger.error(f"[SchemaDetect] skip {url}: {e}")
                continue

            if not records:                              # truly header-only
                logger.error(f"[SchemaDetect] skip {url}: no records after header")
                continue

            tbl = pa.Table.from_pylist(records[:row_sample_count])
            schema = converter.to_recap(tbl, event_name=event_name)
            data_map[url] = (tbl, schema)
            continue
        # 2️⃣  Decide whether DuckDB can stream directly
        can_stream_direct = (
            wrapper == CompressionWrapper.NONE
            or (wrapper == CompressionWrapper.GZ  and fmt in (FileFormat.CSV, FileFormat.TSV, FileFormat.JSON))
            or (wrapper == CompressionWrapper.ZST and fmt == FileFormat.PARQUET)
        )

        try:
            if can_stream_direct:
                s3_path = f"s3://{bucket}/{key}"
                rel     = _relation_from_path(s3_path, fmt, row_sample_count)
            else:
                # need local decompression (zip / snappy / mixed wrappers)
                local_path = handler.decompress_s3_file_to_local(
                    bucket, key, s3_client=s3_client
                )
                local_fmt = handler.get_original_format(local_path)
                rel = _relation_from_path(
                    local_path, local_fmt or fmt, row_sample_count
                )

            # sanity-check the relation; skip if the read failed
            rel.aggregate("COUNT(*)").fetchone()

        except Exception as e:
            logger.error(f"[SchemaDetect] skip {url}: {e}")
            continue

        schema           = converter.to_recap(rel, event_name=event_name)
        data_map[url] = (rel, schema)

    if not data_map:
        return None

    merged_schema = merge_schemas([s for _, s in data_map.values()])

    if skip_profiling:
        return S3DetectionResult(merged_schema)

    profiles = get_data_asset_field_profiles_for_data_asset(
        merged_schema,
        {k: v[0] for k, v in data_map.items()},
        event_name,
        S3SamplingParameters(
            rowSampleCount=row_sample_count,
            recentFileCount=recent_file_count,
        ),
    )
    return S3DetectionResult(merged_schema, profiles)


# ───────────────────────── tiny utilities (unchanged) ─────────────────────────
def strip_s3_bucket_prefix(bucket: str) -> str:
    return bucket[len("s3://") :] if bucket.startswith("s3://") else bucket


def append_s3_url_prefix(bucket: str, key: str) -> str:
    if key.startswith("s3://"):
        return key
    return f"s3://{bucket}/{key.lstrip('/')}"
