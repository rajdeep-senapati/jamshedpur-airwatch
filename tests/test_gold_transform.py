from datetime import date, datetime, timedelta

from pyspark.sql import SparkSession
from pyspark.sql import functions as F

from scripts.build_gold import aqi_category


def test_aqi_category_boundaries():
    spark = SparkSession.builder.appName("AQICategoryTest").getOrCreate()

    try:
        values = [
            (0,),
            (50,),
            (51,),
            (100,),
            (101,),
            (150,),
            (151,),
            (200,),
            (201,),
            (300,),
            (301,),
        ]

        df = spark.createDataFrame(values, ["us_aqi"])
        result = [
            row["category"]
            for row in df.withColumn(
                "category", aqi_category(F.col("us_aqi"))
            ).collect()
        ]

        assert result == [
            "Good",
            "Good",
            "Moderate",
            "Moderate",
            "Unhealthy for Sensitive Groups",
            "Unhealthy for Sensitive Groups",
            "Unhealthy",
            "Unhealthy",
            "Very Unhealthy",
            "Very Unhealthy",
            "Hazardous",
        ]
    finally:
        spark.stop()


def test_gold_dataset_structure(tmp_path, monkeypatch):
    from scripts import build_gold

    spark = (
        SparkSession.builder.appName("GoldDatasetTest")
        .config("spark.sql.session.timeZone", "Asia/Kolkata")
        .getOrCreate()
    )

    input_path = tmp_path / "silver_input"
    output_path = tmp_path / "gold_output"

    try:
        rows = []
        start = datetime(2026, 1, 1)

        for hour in range(24):
            rows.append(
                (
                    "Open-Meteo",
                    22.8,
                    86.2,
                    "Asia/Kolkata",
                    start + timedelta(hours=hour),
                    date(2026, 1, 1),
                    160,
                    80,
                    50.0,
                    70.0,
                    20.0,
                    100.0,
                    10.0,
                    5.0,
                    0.5,
                )
            )

        columns = [
            "source",
            "latitude",
            "longitude",
            "timezone",
            "timestamp",
            "date",
            "us_aqi",
            "european_aqi",
            "pm2_5",
            "pm10",
            "nitrogen_dioxide",
            "ozone",
            "sulphur_dioxide",
            "carbon_monoxide",
        ]

        silver_df = spark.createDataFrame(rows, columns)
        silver_df.write.mode("overwrite").parquet(str(input_path))
    finally:
        spark.stop()

    monkeypatch.setattr(
        "sys.argv",
        [
            "build_gold.py",
            "--input",
            str(input_path),
            "--output",
            str(output_path),
        ],
    )

    build_gold.main()

    result_spark = SparkSession.builder.appName("GoldDatasetValidation").getOrCreate()

    try:
        df = result_spark.read.parquet(str(output_path))

        assert df.count() == 1
        assert df.select("date").distinct().count() == 1
        assert "avg_us_aqi" in df.columns
        assert "unhealthy_hours" in df.columns
        assert "daily_avg_category" in df.columns
        assert df.first()["total_hours"] == 24
        assert df.first()["unhealthy_hours"] == 24
        assert df.first()["daily_avg_category"] == "Unhealthy"
    finally:
        result_spark.stop()
