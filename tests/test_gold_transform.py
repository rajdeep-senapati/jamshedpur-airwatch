from scripts.build_gold import aqi_category
from pyspark.sql import SparkSession
from pyspark.sql import functions as F


def test_aqi_category_boundaries():
    spark = SparkSession.builder.appName("AQICategoryTest").getOrCreate()
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
        for row in df.withColumn("category", aqi_category(F.col("us_aqi"))).collect()
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
    spark.stop()


def test_gold_dataset_structure():
    from pathlib import Path

    output = Path("data/gold/daily_air_quality")
    assert output.is_dir()

    spark = SparkSession.builder.appName("GoldDatasetTest").getOrCreate()

    try:
        df = spark.read.parquet(str(output))
        assert df.count() == 7
        assert df.select("date").distinct().count() == 7
        assert "avg_us_aqi" in df.columns
        assert "unhealthy_hours" in df.columns
        assert "daily_avg_category" in df.columns
        assert df.filter(F.col("total_hours") != 24).count() == 0
        assert df.filter(F.col("unhealthy_hours") > 24).count() == 0
    finally:
        spark.stop()
