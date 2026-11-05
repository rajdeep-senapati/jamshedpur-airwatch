"""Load and prepare Gold air-quality analytics for the dashboard."""

from pathlib import Path

import pandas as pd
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
GOLD_DATA_PATH = PROJECT_ROOT / "data" / "gold" / "daily_air_quality"


@st.cache_data
def load_gold_data() -> pd.DataFrame:
    """Load daily Gold analytics from Parquet."""
    if not GOLD_DATA_PATH.exists():
        raise FileNotFoundError(f"Gold dataset not found at: {GOLD_DATA_PATH}")

    df = pd.read_parquet(GOLD_DATA_PATH)

    if df.empty:
        raise ValueError("Gold dataset is empty.")

    df["date"] = pd.to_datetime(df["date"])

    return df.sort_values("date").reset_index(drop=True)
