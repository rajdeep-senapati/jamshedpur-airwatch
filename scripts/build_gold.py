"""Build daily air-quality analytics from Silver Parquet data."""

from __future__ import annotations

import argparse
from pathlib import Path

from pyspark.sql import SparkSession
from pyspark.sql import functions as F

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = REPO_ROOT / "data" / "silver" / "air_quality_hourly"
DEFAULT_OUTPUT = REPO_ROOT / "data" / "gold" / "daily_air_quality"


def aqi_category(column):
    """Classify US AQI values using the standard US AQI bands."""
    return (
        F.when(column <= 50, "Good")
        .when(column <= 100, "Moderate")
        .when(column <= 150, "Unhealthy for Sensitive Groups")
        .when(column <= 200, "Unhealthy")
        .when(column <= 300, "Very Unhealthy")
        .otherwise("Hazardous")
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Aggregate hourly Silver data into daily Gold analytics."
    )
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    if not args.input.exists():
        raise FileNotFoundError(f"Silver dataset not found: {args.input}")

    spark = (
        SparkSession.builder.appName("JamshedpurAirWatch-GoldTransform")
        .config("spark.sql.session.timeZone", "Asia/Kolkata")
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("WARN")

    try:
        hourly = spark.read.parquet(str(args.input))

        required_columns = {
            "date", "us_aqi", "european_aqi", "pm2_5", "pm10",
            "nitrogen_dioxide", "ozone", "sulphur_dioxide",
            "carbon_monoxide",
        }
        missing = required_columns - set(hourly.columns)
        if missing:
            raise ValueError(f"Silver dataset is missing columns: {sorted(missing)}")

        daily = (
            hourly.groupBy("date")
            .agg(
                F.first("source").alias("source"),
                F.first("latitude").alias("latitude"),
                F.first("longitude").alias("longitude"),
                F.first("timezone").alias("timezone"),
                F.count("*").alias("total_hours"),
                F.avg("us_aqi").alias("avg_us_aqi"),
                F.min("us_aqi").alias("min_us_aqi"),
                F.max("us_aqi").alias("max_us_aqi"),
                F.avg("european_aqi").alias("avg_european_aqi"),
                F.avg("pm2_5").alias("avg_pm2_5"),
                F.avg("pm10").alias("avg_pm10"),
                F.avg("nitrogen_dioxide").alias("avg_nitrogen_dioxide"),
                F.avg("ozone").alias("avg_ozone"),
                F.avg("sulphur_dioxide").alias("avg_sulphur_dioxide"),
                F.avg("carbon_monoxide").alias("avg_carbon_monoxide"),
                F.sum(
                    F.when(F.col("us_aqi") > 150, 1).otherwise(0)
                ).alias("unhealthy_hours"),
            )
            .withColumn(
                "daily_avg_category",
                aqi_category(F.col("avg_us_aqi")),
            )
            .withColumn(
                "daily_max_category",
                aqi_category(F.col("max_us_aqi")),
            )
        )

        if daily.count() == 0:
            raise ValueError("No daily records were produced.")

        duplicate_dates = (
            daily.groupBy("date").count().filter(F.col("count") > 1).count()
        )
        if duplicate_dates:
            raise ValueError(f"Found {duplicate_dates} duplicate daily records.")

        output_path = args.output.resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)

        daily.orderBy("date").write.mode("overwrite").parquet(str(output_path))

        print(f"Hourly input rows: {hourly.count()}")
        print(f"Daily output rows: {daily.count()}")
        print(f"Gold Parquet saved to: {output_path}")
        print(
            "Note: Open-Meteo values are model-based grid estimates, "
            "not confirmed monitoring-station readings."
        )

        daily.orderBy("date").show(truncate=False)

    finally:
        spark.stop()


if __name__ == "__main__":
    main()
