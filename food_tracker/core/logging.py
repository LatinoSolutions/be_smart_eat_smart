"""
logging.py - Append food entries to the daily CSV log and read them back.
"""

import csv
from datetime import datetime, date
from pathlib import Path

LOG_PATH = Path(__file__).parent.parent / "data" / "daily_log.csv"
CSV_FIELDS = ["date", "time", "item", "grams", "kcal", "protein", "carbs", "fat"]


def log_food_entry(
    item: str,
    grams: float,
    kcal: float,
    protein: float,
    carbs: float,
    fat: float,
    timestamp: datetime | None = None,
) -> None:
    """
    Append a single food entry to the daily log CSV.

    Args:
        item: Name of the food or meal.
        grams: Weight in grams (0 for predefined meals logged by name).
        kcal, protein, carbs, fat: Macro values.
        timestamp: Datetime of the entry; defaults to now.
    """
    if timestamp is None:
        timestamp = datetime.now()

    row = {
        "date": timestamp.strftime("%Y-%m-%d"),
        "time": timestamp.strftime("%H:%M"),
        "item": item,
        "grams": round(grams, 1),
        "kcal": round(kcal, 1),
        "protein": round(protein, 1),
        "carbs": round(carbs, 1),
        "fat": round(fat, 1),
    }

    # Create file with header if it doesn't exist
    file_exists = LOG_PATH.exists() and LOG_PATH.stat().st_size > 0
    with open(LOG_PATH, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)


def load_log_for_date(target_date: date | None = None) -> list[dict]:
    """
    Read all log entries for a given date.

    Args:
        target_date: The date to filter by; defaults to today.

    Returns:
        List of row dicts matching the date.
    """
    if target_date is None:
        target_date = date.today()

    date_str = target_date.strftime("%Y-%m-%d")

    if not LOG_PATH.exists():
        return []

    entries = []
    with open(LOG_PATH, "r", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("date") == date_str:
                entries.append(row)

    return entries


def delete_log_entry(target_date: date, index: int) -> bool:
    """
    Delete a log entry by its position among entries for a given date.

    Args:
        target_date: The date of the entry.
        index: Zero-based index within that day's entries.

    Returns:
        True if the entry was found and deleted, False otherwise.
    """
    if not LOG_PATH.exists():
        return False

    date_str = target_date.strftime("%Y-%m-%d")
    all_rows = []
    day_counter = 0
    deleted = False

    with open(LOG_PATH, "r", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("date") == date_str:
                if day_counter == index:
                    deleted = True  # Skip this row (delete it)
                else:
                    all_rows.append(row)
                day_counter += 1
            else:
                all_rows.append(row)

    if deleted:
        with open(LOG_PATH, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
            writer.writeheader()
            writer.writerows(all_rows)

    return deleted


def load_full_log() -> list[dict]:
    """Load all entries from the CSV log."""
    if not LOG_PATH.exists():
        return []
    with open(LOG_PATH, "r", newline="") as f:
        reader = csv.DictReader(f)
        return list(reader)
