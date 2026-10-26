# Jamshedpur AirWatch

A zero-cost, portfolio-grade data engineering project exploring air-quality trends in Jamshedpur, Jharkhand, around a practical question:

> **Do I need an air purifier in Jamshedpur?**

The project will build a reproducible PySpark pipeline from public air-quality observations into Bronze, Silver, and Gold data layers, then use SQL and descriptive analysis to investigate trends and communicate what the data can—and cannot—tell us.

## Important scope note

Outdoor AQI alone cannot determine whether an individual needs an air purifier. Indoor air quality, time spent indoors, building ventilation, health considerations, and pollutant-specific measurements matter too. This project is an analysis of available outdoor monitoring data, not medical advice or a definitive purifier recommendation.

## Project status

**Day 0 — repository setup.** Data-source coverage, supported dates, API access, and station availability for Jamshedpur have not yet been validated. No data-derived findings are claimed at this stage.

## Planned pipeline

1. **Source discovery** — verify public source terms, fields, geographic coverage, date range, and update cadence.
2. **Bronze** — retain raw source responses with ingestion metadata for traceability.
3. **Silver** — validate schema, parse timestamps, normalize station/pollutant fields, handle invalid records, and deduplicate.
4. **Gold** — publish analysis-ready tables for trends, station comparisons, and pollutant completeness.
5. **Analysis** — use Spark SQL to explore seasonality, variation, missingness, and threshold-based summaries where the data supports them.
6. **Quality and automation** — add tests and GitHub Actions checks so changes are repeatable.

## Planned repository layout

```text
data/
  raw/       # generated raw extracts (not committed)
  silver/    # cleaned data (not committed)
  gold/      # analytical outputs (not committed)
src/airwatch/
tests/
notebooks/
.github/workflows/
```

## Technology

- Python 3.11
- PySpark / Spark SQL
- Requests and python-dotenv
- pytest
- GitHub Actions
- Public air-quality data sources (to be verified before implementation)

## Getting started

### Prerequisites

Install Python 3.11, Git, and Java 17 (required by the planned local Spark setup).

### Create a virtual environment

**Windows PowerShell**
```powershell
git clone https://github.com/rajdeep-senapati/jamshedpur-airwatch.git
cd jamshedpur-airwatch
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
```

If PowerShell blocks virtual-environment activation, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` in that terminal, then activate again.

Never commit your real `.env` file or an API key. The repository only contains the placeholder `.env.example`.

## Data and reproducibility

Generated extracts and processing outputs are intentionally excluded from Git to avoid committing large files or data that may have source-specific redistribution restrictions. Source URLs, query parameters, collection timestamps, transformation rules, and quality checks will be documented as the pipeline is implemented.

## Success criteria

- A documented, reproducible ingestion path using a verified source.
- Explicit schema and data-quality checks.
- Deterministic Bronze-to-Silver-to-Gold transformations.
- Meaningful Spark SQL analysis with documented limitations.
- Automated tests and a clean GitHub Actions run.
- Clear provenance and no unsupported claim that outdoor AQI alone decides purifier need.

## License

MIT. See [LICENSE](LICENSE).
