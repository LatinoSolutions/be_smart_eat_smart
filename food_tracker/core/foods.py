"""
foods.py - Load food definitions, predefined meals, and recipes from JSON files.
"""

import json
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"


def load_foods() -> dict:
    """Load ingredients with macro values per 100g."""
    path = DATA_DIR / "foods.json"
    with open(path, "r") as f:
        return json.load(f)


def load_meals() -> dict:
    """Load predefined meals for quick logging."""
    path = DATA_DIR / "meals.json"
    with open(path, "r") as f:
        return json.load(f)


def load_recipes() -> dict:
    """Load recipes defined as ingredient compositions."""
    path = DATA_DIR / "recipes.json"
    with open(path, "r") as f:
        return json.load(f)
