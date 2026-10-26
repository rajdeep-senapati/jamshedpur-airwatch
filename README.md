# Jamshedpur AirWatch

A zero-cost, portfolio-grade data engineering project exploring air-quality trends around a practical question:

> **Do I need an air purifier in Jamshedpur?**

The pipeline uses Python and PySpark to ingest, validate, transform, and analyze public air-quality data in Bronze, Silver, and Gold layers.

## Important interpretation note

The initial source is the **Open-Meteo Air Quality API**. It returns model-based, grid-level estimates for the coordinates near Jamshedpur, not necessarily measurements from a physical monitoring station. We will label these values accordingly and will not present them as station observations.

Outdoor AQI alone cannot determine whether an individual needs an air purifier. Indoor air quality, ventilation, time spent indoors, and individual health considerations also matter. This project is an analysis of available outdoor data, not medical advice or a definitive purifier recommendation.

## Project status

**Day 1 — source validated for a small test request.** A seven-day request returned 168 hourly records, with returned grid coordinates near Jamshedpur and timezone `Asia/Kolkata`. Historical coverage and individual pollutant completeness will be checked as the pipeline develops. The source does not require an API key for this endpoint.

## Current source

- API documentation: https://open-meteo.com/en/docs/air-quality-api
- Endpoint: `https://air-quality-api.open-meteo.com/v1/air-quality`
- Initial variables: PM2.5, PM10, US AQI, European AQI, nitrogen dioxide, ozone, sulphur dioxide, and carbon monoxide.
- Initial extraction window: up to seven past days for a small, reproducible test.
- The ingestion script stores the source response and retrieval metadata in `data/raw/`; generated data is excluded from Git.

## Planned pipeline

1. **Bronze** — retain raw API responses and ingestion metadata for traceability.
2. **Silver** — validate schema, parse timestamps, normalize fields, check nulls/ranges, and deduplicate.
3. **Gold** — publish analysis-ready tables for hourly/daily trends, pollutant completeness, and AQI summaries.
4. **Analysis** — use Spark SQL to explore variation and patterns, clearly stating that the source is model-based.
5. **Quality and automation** — add tests and GitHub Actions checks so changes are repeatable.

## Repository layout

```text
data/
  raw/       # generated source extracts (not committed)
  silver/    # cleaned data (not committed)
  gold/      # analytical outputs (not committed)
src/airwatch/
scripts/
  ingest_open_meteo.py
tests/
notebooks/
.github/workflows/
```

## Technology

- Python 3.11
- PySpark / Spark SQL
- Requests
- pytest
- GitHub Actions
- Open-Meteo Air Quality API

## Getting started

### Prerequisites

Install Python 3.11, Git, and a Java version compatible with the installed PySpark version. The local Spark test was successful on the project author's Windows setup with Java 20.

### Set up the environment

**Windows PowerShell**
```powershell
git clone https://github.com/rajdeep-senapati/jamshedpur-airwatch.git
cd jamshedpur-airwatch
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Ingest a small raw extract

```powershell
python scripts/ingest_open_meteo.py --past-days 7
```

The script makes one API request and writes a timestamped JSON file under `data/raw/`. Use `--past-days 1` for a smaller test. The initial script intentionally caps the window at seven days.

No API key or `.env` file is needed for this source. If you previously created a local `.env` file for API Express, keep it out of Git and remove the unused key from it when convenient. Never commit secrets.

## Data provenance and reproducibility

Every raw extract records the source URL, request parameters, retrieval timestamp, requested and returned coordinates, timezone, and record count. Source responses and transformation outputs are intentionally excluded from Git to avoid committing generated files and to keep the repository reproducible.

## Success criteria

- A documented, reproducible ingestion path from a verified source.
- Explicit schema and data-quality checks.
- Deterministic Bronze-to-Silver-to-Gold transformations.
- Meaningful Spark SQL analysis with documented source limitations.
- Automated tests and a clean GitHub Actions run.
- No unsupported claim that modelled grid-level data is a physical station reading or that outdoor AQI alone decides purifier need.

## License

MIT. See [LICENSE](LICENSE).
