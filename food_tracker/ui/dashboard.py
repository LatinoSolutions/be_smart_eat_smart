"""
dashboard.py - Daily macro dashboard: totals, targets, progress bars, fasting status.
"""

import json
from datetime import datetime, time
from pathlib import Path

import streamlit as st

from core.logging import load_log_for_date, delete_log_entry
from core.macros import sum_macros

CONFIG_PATH = Path(__file__).parent.parent / "config" / "settings.json"


def load_settings() -> dict:
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)


def _parse_time(t_str: str) -> time:
    """Parse HH:MM string to time object."""
    h, m = t_str.split(":")
    return time(int(h), int(m))


def render_fasting_indicator(settings: dict) -> None:
    """Display whether we are currently in the eating or fasting window."""
    now = datetime.now().time()
    fasting_start = _parse_time(settings["fasting_start"])
    fasting_end = _parse_time(settings["fasting_end"])

    # Fasting window spans midnight: active if now >= start OR now < end
    if fasting_start > fasting_end:
        in_fast = now >= fasting_start or now < fasting_end
    else:
        in_fast = fasting_start <= now < fasting_end

    if in_fast:
        st.info(
            f"Fasting window active  |  Eating resumes at {settings['fasting_end']}",
            icon="🌙",
        )
    else:
        st.success(
            f"Eating window active  |  Fasting starts at {settings['fasting_start']}",
            icon="✅",
        )


def render_dashboard() -> dict:
    """
    Render the daily macro dashboard.

    Returns the today's totals dict so other sections can use it.
    """
    settings = load_settings()
    entries = load_log_for_date()
    totals = sum_macros(entries)

    st.header("Today's Nutrition")

    render_fasting_indicator(settings)

    st.divider()

    # Macro summary cards
    kcal_target = settings["daily_calories_target"]
    protein_target = settings.get("protein_target", 0)
    carbs_target = settings.get("carbs_target", 0)
    fat_target = settings.get("fat_target", 0)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        remaining = kcal_target - totals["kcal"]
        delta_color = "normal" if remaining >= 0 else "inverse"
        st.metric(
            label="Calories",
            value=f"{totals['kcal']:.0f} kcal",
            delta=f"{remaining:.0f} remaining",
            delta_color=delta_color,
        )

    with col2:
        st.metric(
            label="Protein",
            value=f"{totals['protein']:.1f} g",
            delta=f"/ {protein_target} g target",
            delta_color="off",
        )

    with col3:
        st.metric(
            label="Carbs",
            value=f"{totals['carbs']:.1f} g",
            delta=f"/ {carbs_target} g target",
            delta_color="off",
        )

    with col4:
        st.metric(
            label="Fat",
            value=f"{totals['fat']:.1f} g",
            delta=f"/ {fat_target} g target",
            delta_color="off",
        )

    st.divider()

    # Progress bars
    st.subheader("Progress")

    def _progress(label: str, current: float, target: float, color_hint: str = "") -> None:
        ratio = min(current / target, 1.0) if target > 0 else 0.0
        pct = int(ratio * 100)
        st.write(f"**{label}** — {current:.0f} / {target} ({pct}%)")
        st.progress(ratio)

    _progress("Calories", totals["kcal"], kcal_target)
    _progress("Protein (g)", totals["protein"], protein_target)
    _progress("Carbs (g)", totals["carbs"], carbs_target)
    _progress("Fat (g)", totals["fat"], fat_target)

    st.divider()

    # Today's log table with delete buttons
    if entries:
        st.subheader("Today's Log")
        for i, entry in enumerate(entries):
            col_time, col_item, col_kcal, col_p, col_c, col_f, col_del = st.columns(
                [1, 2.5, 1, 1, 1, 1, 0.7]
            )
            col_time.write(entry.get("time", ""))
            col_item.write(entry.get("item", ""))
            col_kcal.write(f"{float(entry.get('kcal', 0)):.0f} kcal")
            col_p.write(f"P {float(entry.get('protein', 0)):.1f}g")
            col_c.write(f"C {float(entry.get('carbs', 0)):.1f}g")
            col_f.write(f"F {float(entry.get('fat', 0)):.1f}g")
            if col_del.button("✕", key=f"del_{i}", help="Remove entry"):
                from datetime import date
                delete_log_entry(date.today(), i)
                st.rerun()
    else:
        st.caption("No entries logged today yet.")

    return totals
