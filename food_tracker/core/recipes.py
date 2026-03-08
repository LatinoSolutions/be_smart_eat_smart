"""
recipes.py - Utilities for working with recipes (batch cooking, macro calculation).
"""

from core.foods import load_foods, load_recipes
from core.macros import calculate_recipe_macros


def get_recipe_nutrition(recipe_name: str, servings: int = 1) -> dict | None:
    """
    Get nutritional info for a named recipe.

    Args:
        recipe_name: Key from recipes.json.
        servings: Number of servings to calculate for.

    Returns:
        Dict with label, kcal, protein, carbs, fat — or None if not found.
    """
    recipes = load_recipes()
    food_db = load_foods()

    if recipe_name not in recipes:
        return None

    recipe = recipes[recipe_name]
    macros = calculate_recipe_macros(recipe, food_db, servings=servings)

    return {
        "label": recipe.get("label", recipe_name),
        "servings": servings,
        "total_servings": recipe.get("servings", 1),
        **macros,
    }


def list_recipes() -> list[str]:
    """Return all recipe names."""
    return list(load_recipes().keys())


def batch_cook_plan(recipe_name: str, batches: int = 1) -> dict | None:
    """
    Calculate macros for batch cooking N full batches of a recipe.

    Args:
        recipe_name: Key from recipes.json.
        batches: Number of full recipe batches to cook.

    Returns:
        Dict with total macros and per-serving breakdown.
    """
    recipes = load_recipes()
    food_db = load_foods()

    if recipe_name not in recipes:
        return None

    recipe = recipes[recipe_name]
    total_servings = recipe.get("servings", 1) * batches

    # Total macros for all batches
    total_macros = calculate_recipe_macros(recipe, food_db, servings=total_servings)
    # Per serving macros
    per_serving = calculate_recipe_macros(recipe, food_db, servings=1)

    return {
        "label": recipe.get("label", recipe_name),
        "batches": batches,
        "total_servings": total_servings,
        "total": total_macros,
        "per_serving": per_serving,
    }
