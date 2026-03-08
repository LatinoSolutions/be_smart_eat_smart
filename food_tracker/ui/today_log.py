"""
today_log.py - Display today's food log entries with per-row delete capability.
"""

from datetime import date
from pathlib import Path

import pandas as pd
import streamlit as st

LOG_PATH = Path(__file__).parent.parent / "data" / "daily_log.csv"
CSV_FIELDS = ["date", "time", "item", "grams", "kcal", "protein", "carbs", "fat"]


def _load_df() -> pd.DataFrame:
    """Load the full CSV into a DataFrame. Returns empty frame if file missing."""
    if not LOG_PATH.exists() or LOG_PATH.stat().st_size == 0:
        return pd.DataFrame(columns=CSV_FIELDS)
    return pd.read_csv(LOG_PATH, dtype=str)


def _save_df(df: pd.DataFrame) -> None:
    """Write DataFrame back to CSV, preserving column order."""
    df.to_csv(LOG_PATH, index=False, columns=CSV_FIELDS)


def _today_str() -> str:
    return date.today().strftime("%Y-%m-%d")


def delete_entry(original_index: int) -> None:
    """
    Remove a row by its position in the full CSV (not just today's rows).
    Rewrites the CSV without that row and triggers a page refresh.
    """
    df = _load_df()
    df = df.drop(index=original_index).reset_index(drop=True)
    _save_df(df)
    st.rerun()


def render_today_log() -> None:
    """
    Render a table of today's log entries, each with a delete button.

    Layout per row:
        Time | Item | Grams | kcal | [✕]
    """
    st.subheader("Today's Log")

    df = _load_df()
    today = _today_str()
    today_mask = df["date"] == today
    today_df = df[today_mask]

    if today_df.empty:
        st.caption("No entries logged today yet.")
        return

    # Header row
    h_time, h_item, h_grams, h_kcal, h_del = st.columns([1.2, 3, 1.2, 1.2, 0.7])
    h_time.markdown("**Time**")
    h_item.markdown("**Item**")
    h_grams.markdown("**Grams**")
    h_kcal.markdown("**kcal**")
    h_del.markdown("")

    st.divider()

    # One row per entry — use original CSV index for safe deletion
    for original_idx, row in today_df.iterrows():
        c_time, c_item, c_grams, c_kcal, c_del = st.columns([1.2, 3, 1.2, 1.2, 0.7])

        c_time.write(row.get("time", ""))
        c_item.write(row.get("item", ""))

        grams = float(row.get("grams", 0))
        c_grams.write(f"{grams:.0f}g" if grams > 0 else "—")

        kcal = float(row.get("kcal", 0))
        c_kcal.write(f"{kcal:.0f}")

        if c_del.button("✕", key=f"todaylog_del_{original_idx}", help="Delete entry"):
            delete_entry(original_idx)
