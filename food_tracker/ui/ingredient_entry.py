"""
ingredient_entry.py - Log individual ingredients by weight and browse recipes.
"""

import streamlit as st

from core.foods import load_foods, load_recipes
from core.logging import log_food_entry
from core.macros import calculate_macros, calculate_recipe_macros
from core.recipes import batch_cook_plan


def render_ingredient_entry() -> None:
    """
    Render the ingredient-by-weight entry form and recipe browser.
    """
    st.header("Add Ingredient by Weight")

    food_db = load_foods()
    food_names = sorted(food_db.keys())

    col_food, col_grams, col_btn = st.columns([3, 2, 1])

    with col_food:
        selected = st.selectbox(
            "Ingredient",
            options=food_names,
            format_func=lambda x: x.replace("_", " ").title(),
            label_visibility="collapsed",
        )

    with col_grams:
        grams = st.number_input(
            "Grams",
            min_value=1,
            max_value=2000,
            value=100,
            step=5,
            label_visibility="collapsed",
        )

    # Show live macro preview
    if selected:
        preview = calculate_macros(selected, grams, food_db)
        st.caption(
            f"Preview: {preview['kcal']} kcal | "
            f"P {preview['protein']}g | "
            f"C {preview['carbs']}g | "
            f"F {preview['fat']}g"
        )

    with col_btn:
        if st.button("Add", key="add_ingredient", use_container_width=True):
            macros = calculate_macros(selected, grams, food_db)
            log_food_entry(
                item=selected.replace("_", " ").title(),
                grams=grams,
                kcal=macros["kcal"],
                protein=macros["protein"],
                carbs=macros["carbs"],
                fat=macros["fat"],
            )
            st.toast(
                f"Logged {grams}g of {selected.replace('_', ' ').title()}",
                icon="✅",
            )
            st.rerun()

    st.divider()

    # Recipe browser
    render_recipe_browser()


def render_recipe_browser() -> None:
    """
    Browse recipes, see per-serving macros, and log a serving.
    Also includes batch cooking planner.
    """
    st.header("Recipes")

    recipes = load_recipes()
    food_db = load_foods()

    if not recipes:
        st.caption("No recipes found.")
        return

    recipe_names = list(recipes.keys())

    selected_recipe = st.selectbox(
        "Select recipe",
        options=recipe_names,
        format_func=lambda x: recipes[x].get("label", x),
    )

    recipe = recipes[selected_recipe]
    total_servings = recipe.get("servings", 1)

    col_srv, col_log = st.columns([2, 1])
    with col_srv:
        servings = st.number_input(
            "Servings to log",
            min_value=1,
            max_value=20,
            value=1,
            step=1,
        )

    macros = calculate_recipe_macros(recipe, food_db, servings=servings)

    st.caption(
        f"Recipe yields {total_servings} serving(s).  "
        f"Logging **{servings}**: "
        f"{macros['kcal']} kcal | "
        f"P {macros['protein']}g | "
        f"C {macros['carbs']}g | "
        f"F {macros['fat']}g"
    )

    with col_log:
        if st.button("Log recipe", key="log_recipe", use_container_width=True):
            label = recipe.get("label", selected_recipe)
            log_food_entry(
                item=f"{label} x{servings}",
                grams=0,
                kcal=macros["kcal"],
                protein=macros["protein"],
                carbs=macros["carbs"],
                fat=macros["fat"],
            )
            st.toast(f"Logged {servings} serving(s) of {label}", icon="✅")
            st.rerun()

    # Ingredient breakdown
    with st.expander("Ingredient breakdown"):
        for ingredient, grams in recipe["ingredients"].items():
            ing_macros = calculate_macros(ingredient, grams, food_db)
            st.write(
                f"**{ingredient.replace('_', ' ').title()}** — {grams}g | "
                f"{ing_macros['kcal']} kcal | "
                f"P {ing_macros['protein']}g | "
                f"C {ing_macros['carbs']}g | "
                f"F {ing_macros['fat']}g"
            )

    st.divider()

    # Batch cooking planner
    st.subheader("Batch Cooking Planner")
    col_b, col_plan = st.columns([2, 2])

    with col_b:
        batches = st.number_input(
            "Batches to cook",
            min_value=1,
            max_value=10,
            value=2,
            step=1,
        )

    plan = batch_cook_plan(selected_recipe, batches=batches)
    if plan:
        with col_plan:
            st.write(f"**{plan['label']}** — {plan['total_servings']} servings total")

        st.caption(
            f"Total: {plan['total']['kcal']} kcal | "
            f"P {plan['total']['protein']}g | "
            f"C {plan['total']['carbs']}g | "
            f"F {plan['total']['fat']}g"
        )
        st.caption(
            f"Per serving: {plan['per_serving']['kcal']} kcal | "
            f"P {plan['per_serving']['protein']}g | "
            f"C {plan['per_serving']['carbs']}g | "
            f"F {plan['per_serving']['fat']}g"
        )
