"""
app.py - Entry point for the Daily Nutrition Tracker Streamlit app.

Run with:
    streamlit run app.py
"""

import sys
from pathlib import Path

# Ensure project root is on sys.path so relative imports work
sys.path.insert(0, str(Path(__file__).parent))

import streamlit as st

from ui.dashboard import render_dashboard
from ui.quick_add import render_quick_add
from ui.ingredient_entry import render_ingredient_entry
from ui.today_log import render_today_log
from ui.scan_food import render_food_scanner

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Daily Nutrition Tracker",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── PWA: manifest + service worker registration ──────────────────────────────
st.markdown(
    """
    <link rel="manifest" href="/static/manifest.json">
    <meta name="theme-color" content="#0e1117">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <meta name="apple-mobile-web-app-title" content="EatSmart">
    <link rel="apple-touch-icon" href="/static/icon-192.png">
    <script>
      if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register('/static/service_worker.js');
      }
    </script>
    """,
    unsafe_allow_html=True,
)

# ── Custom CSS: tighten spacing on mobile ─────────────────────────────────────
st.markdown(
    """
    <style>
        .block-container { padding-top: 1rem; padding-bottom: 1rem; }
        div[data-testid="stMetricValue"] { font-size: 1.4rem; }
        div[data-testid="stButton"] > button { height: 3rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Title ─────────────────────────────────────────────────────────────────────
st.title("Daily Nutrition Tracker")

# ── Layout: two-column on wide screens, stacked on mobile ────────────────────
left, right = st.columns([1, 1], gap="large")

with left:
    render_dashboard()
    st.divider()
    render_today_log()

with right:
    render_quick_add()
    st.divider()
    render_ingredient_entry()
    st.divider()
    render_food_scanner()
