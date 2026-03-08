"""
quick_add.py - One-tap meal logging buttons for predefined meals.
"""

import streamlit as st

from core.foods import load_meals
from core.logging import log_food_entry


def render_quick_add() -> None:
    """
    Render a grid of quick-add buttons for predefined meals.
    Each button logs the meal immediately with a single tap.
    """
    st.header("Quick Add Meals")
    st.caption("Tap a meal to log it instantly.")

    meals = load_meals()

    # Lay out buttons in rows of 3
    items = list(meals.items())
    cols_per_row = 3

    for row_start in range(0, len(items), cols_per_row):
        row_items = items[row_start : row_start + cols_per_row]
        cols = st.columns(cols_per_row)

        for col, (meal_key, meal) in zip(cols, row_items):
            label = f"{meal.get('emoji', '')} {meal['label']}"
            with col:
                if st.button(label, key=f"quick_{meal_key}", use_container_width=True):
                    log_food_entry(
                        item=meal["label"],
                        grams=0,
                        kcal=meal["kcal"],
                        protein=meal["protein"],
                        carbs=meal["carbs"],
                        fat=meal["fat"],
                    )
                    st.toast(f"Logged: {meal['label']}", icon="✅")
                    st.rerun()
