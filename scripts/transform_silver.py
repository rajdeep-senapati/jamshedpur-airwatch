"""Transform the latest Open-Meteo raw response into Silver Parquet using PySpark."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import DoubleType, StringType, StructField, StructType


REPO_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = REPO_ROOT / "data" / "raw"
DEFAULT_OUTPUT = REPO_ROOT / "data" / "processed" / "silver" / "air_quality_hourly"
POLLUTANT_COLUMNS = (
    "pm2_5",
    "pm10",
    "us_aqi",
    "european_aqi",
    "nitrogen_dioxide",
    "ozone",
    "sulphur_dioxide",
    "carbon_monoxide",
)


def latest_raw_file(raw_dir: Path = RAW_DIR) -> Path:
    """Return the most recently named Open-Meteo raw JSON file."""
    candidates = sorted(raw_dir.glob("open_meteo_air_quality_*.json"))
    if not candidates:
        raise FileNotFoundError(
            f"No raw Open-Meteo JSON files found in {raw_dir}. "
            "Run scripts/ingest_open_meteo.py first."
        )
    return candidates[-1]


def load_hourly_rows(input_path: Path) -> list[dict]:
    """Flatten Open-Meteo's parallel hourly arrays into one dictionary per hour."""
    with input_path.open("r", encoding="utf-8") as file:
        payload = json.load(file)

    metadata = payload.get("metadata", {})
    hourly = payload.get("response", {}).get("hourly")
    if not isinstance(hourly, dict) or not isinstance(hourly.get("time"), list):
        raise ValueError("Input JSON is missing response.hourly.time.")

    times = hourly["time"]
    expected_columns = ("time", *POLLUTANT_COLUMNS)
    missing_columns = [column for column in expected_columns if column not in hourly]
    if missing_columns:
        raise ValueError(f"Input JSON is missing hourly columns: {missing_columns}")

    bad_lengths = {
        column: len(hourly[column])
        for column in expected_columns
        if not isinstance(hourly[column], list) or len(hourly[column]) != len(times)
    }
    if bad_lengths:
        raise ValueError(f"Hourly arrays have inconsistent lengths: {bad_lengths}")

    rows = []
    for index, timestamp in enumerate(times):
        row = {
            "timestamp_local": timestamp,
            "source": metadata.get("source", "Open-Meteo Air Quality API"),
            "latitude": float(
                metadata.get("returned_coordinates", {}).get("latitude",
                payload["response"].get("latitude"))
            ),
            "longitude": float(
                metadata.get("returned_coordinates", {}).get("longitude",
                payload["response"].get("longitude"))
            ),
            "timezone": metadata.get("timezone", payload["response"].get("timezone", "Asia/Kolkata")),
        }
        for column in POLLUTANT_COLUMNS:
            row[column] = hourly[column][index]
        rows.append(row)
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Flatten raw Open-Meteo hourly data into a validated Silver Parquet dataset."
    )
    parser.add_argument("--input", type=Path, help="Raw JSON file; defaults to the latest file in data/raw.")
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"Silver Parquet output directory (default: {DEFAULT_OUTPUT}).",
    )
    args = parser.parse_args()

    input_path = args.input or latest_raw_file()
    if not input_path.is_file():
        raise FileNotFoundError(f"Input file does not exist: {input_path}")

    rows = load_hourly_rows(input_path)
    if not rows:
        raise ValueError("Input contains zero hourly records.")

    schema = StructType(
        [
            StructField("timestamp_local", StringType(), nullable=False),
            StructField("source", StringType(), nullable=False),
            StructField("latitude", DoubleType(), nullable=False),
            StructField("longitude", DoubleType(), nullable=False),
            StructField("timezone", StringType(), nullable=False),
            *[StructField(column, DoubleType(), nullable=True) for column in POLLUTANT_COLUMNS],
        ]
    )

    spark = (
        SparkSession.builder
        .appName("JamshedpurAirWatch-SilverTransform")
        .config("spark.sql.session.timeZone", "Asia/Kolkata")
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("WARN")

    try:
        df = spark.createDataFrame(rows, schema=schema)
        df = (
            df.withColumn(
                "timestamp",
                F.to_timestamp("timestamp_local", "yyyy-MM-dd'T'HH:mm"),
            )
            .withColumn("date", F.to_date("timestamp"))
            .drop("timestamp_local")
        )

        total_rows = df.count()
        distinct_timestamps = df.select("timestamp").distinct().count()
        invalid_timestamps = df.filter(F.col("timestamp").isNull()).count()
        null_pollutant_values = df.select(
            sum(F.col(column).isNull().cast("int") for column in POLLUTANT_COLUMNS).alias("null_count")
        ).first()["null_count"]

        if invalid_timestamps:
            raise ValueError(f"Found {invalid_timestamps} invalid timestamps.")
        if distinct_timestamps != total_rows:
            raise ValueError(
                f"Duplicate timestamps detected: {total_rows} rows but "
                f"{distinct_timestamps} distinct timestamps."
            )
        if null_pollutant_values:
            raise ValueError(
                f"Found {null_pollutant_values} null pollutant/AQI values; refusing to write Silver output."
            )

        output_path = args.output.resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        (
            df.orderBy("timestamp")
            .write
            .mode("overwrite")
            .partitionBy("date")
            .parquet(str(output_path))
        )

        print(f"Input: {input_path.resolve()}")
        print(f"Rows validated: {total_rows}")
        print(f"Distinct hourly timestamps: {distinct_timestamps}")
        print(f"Null pollutant/AQI values: {null_pollutant_values}")
        print(f"Silver Parquet saved to: {output_path}")
        print("Note: source values are model-based grid estimates, not confirmed station readings.")
    finally:
        spark.stop()


if __name__ == "__main__":
    main()
