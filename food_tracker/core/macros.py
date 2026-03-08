"""
macros.py - Calculate macronutrients from food entries.
"""


def calculate_macros(food_name: str, grams: float, food_db: dict) -> dict:
    """
    Calculate macros for a given food and weight.

    Args:
        food_name: Key into the food database.
        grams: Weight in grams to calculate for.
        food_db: The loaded foods dictionary (macros per 100g).

    Returns:
        Dict with kcal, protein, carbs, fat — rounded to 1 decimal.
        Returns zeros if food not found.
    """
    if food_name not in food_db:
        return {"kcal": 0, "protein": 0, "carbs": 0, "fat": 0}

    food = food_db[food_name]
    ratio = grams / 100.0

    return {
        "kcal": round(food["kcal"] * ratio, 1),
        "protein": round(food["protein"] * ratio, 1),
        "carbs": round(food["carbs"] * ratio, 1),
        "fat": round(food["fat"] * ratio, 1),
    }


def calculate_recipe_macros(recipe: dict, food_db: dict, servings: int = 1) -> dict:
    """
    Calculate macros for a full recipe, divided by servings.

    Args:
        recipe: A recipe dict with 'ingredients' (name -> grams) and 'servings'.
        food_db: The loaded foods dictionary.
        servings: How many servings to calculate for (default 1).

    Returns:
        Dict with total kcal, protein, carbs, fat for the requested servings.
    """
    totals = {"kcal": 0.0, "protein": 0.0, "carbs": 0.0, "fat": 0.0}

    for ingredient, grams in recipe["ingredients"].items():
        macros = calculate_macros(ingredient, grams, food_db)
        for key in totals:
            totals[key] += macros[key]

    # Divide by total servings, multiply by requested servings
    recipe_servings = recipe.get("servings", 1)
    per_serving_ratio = servings / recipe_servings

    return {key: round(val * per_serving_ratio, 1) for key, val in totals.items()}


def sum_macros(entries: list[dict]) -> dict:
    """
    Sum macros across a list of log entries.

    Args:
        entries: List of dicts each containing kcal, protein, carbs, fat.

    Returns:
        Dict with summed totals.
    """
    totals = {"kcal": 0.0, "protein": 0.0, "carbs": 0.0, "fat": 0.0}
    for entry in entries:
        for key in totals:
            totals[key] += float(entry.get(key, 0))
    return {key: round(val, 1) for key, val in totals.items()}
