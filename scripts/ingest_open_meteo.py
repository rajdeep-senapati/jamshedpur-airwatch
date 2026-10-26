"""Download a small Open-Meteo air-quality extract into the Bronze/raw layer.

The API returns model-based grid estimates, not necessarily measurements from a
physical monitoring station. No API key is required for this endpoint.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests

BASE_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"
DEFAULT_OUTPUT_DIR = Path(__file__).resolve().parents[1] / "data" / "raw"
DEFAULT_LATITUDE = 22.8046
DEFAULT_LONGITUDE = 86.2029
DEFAULT_TIMEZONE = "Asia/Kolkata"
HOURLY_VARIABLES = [
    "pm2_5",
    "pm10",
    "us_aqi",
    "european_aqi",
    "nitrogen_dioxide",
    "ozone",
    "sulphur_dioxide",
    "carbon_monoxide",
]


def fetch_air_quality(past_days: int = 7, timeout: int = 30) -> dict[str, Any]:
    """Fetch hourly air-quality data for the Jamshedpur grid cell."""
    if not 1 <= past_days <= 7:
        raise ValueError("past_days must be between 1 and 7 for this initial extract.")

    params = {
        "latitude": DEFAULT_LATITUDE,
        "longitude": DEFAULT_LONGITUDE,
        "hourly": ",".join(HOURLY_VARIABLES),
        "past_days": past_days,
        "forecast_days": 0,
        "timezone": DEFAULT_TIMEZONE,
    }
    response = requests.get(BASE_URL, params=params, timeout=timeout)
    response.raise_for_status()
    payload = response.json()

    hourly = payload.get("hourly")
    if not isinstance(hourly, dict) or not isinstance(hourly.get("time"), list):
        raise ValueError("API response is missing the expected hourly.time array.")

    record_count = len(hourly["time"])
    if record_count == 0:
        raise ValueError("API returned no hourly records.")

    for variable in HOURLY_VARIABLES:
        values = hourly.get(variable)
        if not isinstance(values, list) or len(values) != record_count:
            raise ValueError(
                f"Expected '{variable}' to contain {record_count} values."
            )

    return {
        "metadata": {
            "source": "Open-Meteo Air Quality API",
            "source_url": BASE_URL,
            "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
            "location_label": "Jamshedpur, Jharkhand, India",
            "requested_coordinates": {
                "latitude": DEFAULT_LATITUDE,
                "longitude": DEFAULT_LONGITUDE,
            },
            "returned_coordinates": {
                "latitude": payload.get("latitude"),
                "longitude": payload.get("longitude"),
            },
            "timezone": payload.get("timezone"),
            "requested_past_days": past_days,
            "record_count": record_count,
            "data_character": (
                "Model-based grid estimates; not confirmed station observations."
            ),
            "request_parameters": params,
        },
        "response": payload,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Fetch hourly Open-Meteo air-quality data for Jamshedpur."
    )
    parser.add_argument(
        "--past-days",
        type=int,
        default=7,
        help="Number of past days to request (1-7; default: 7).",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Output directory (default: data/raw).",
    )
    args = parser.parse_args()

    extract = fetch_air_quality(past_days=args.past_days)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output_path = args.output_dir / f"open_meteo_air_quality_{timestamp}.json"
    output_path.write_text(
        json.dumps(extract, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print(f"Source: {extract['metadata']['source']}")
    print(f"Location: {extract['metadata']['location_label']}")
    print(f"Hourly records: {extract['metadata']['record_count']}")
    print(f"Returned grid coordinates: {extract['metadata']['returned_coordinates']}")
    print(f"Saved raw response to: {output_path}")
    print("Note: these are model-based grid estimates, not confirmed station readings.")


if __name__ == "__main__":
    main()
