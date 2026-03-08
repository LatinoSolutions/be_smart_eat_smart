"""
scan_food.py - Barcode scanner using phone camera + OpenFoodFacts API.
"""

import io

import requests
import streamlit as st
from PIL import Image

from core.logging import log_food_entry


def _decode_barcode(image: Image.Image) -> str | None:
    """Return the first barcode string found in the image, or None."""
    try:
        import cv2
        import numpy as np
        from pyzbar.pyzbar import decode

        img_array = np.array(image.convert("RGB"))
        img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)

        decoded_objects = decode(img_bgr)
        if decoded_objects:
            return decoded_objects[0].data.decode("utf-8")
    except ImportError as e:
        st.error(f"Missing dependency: {e}. Run: pip install opencv-python pyzbar")
    return None


def _fetch_product(barcode: str) -> dict | None:
    """
    Query OpenFoodFacts for the barcode.
    Returns a dict with name + macros per 100 g, or None on failure.
    """
    url = f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json"
    try:
        resp = requests.get(url, timeout=8)
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as e:
        st.error(f"Network error fetching product data: {e}")
        return None

    if data.get("status") != 1:
        return None

    product = data.get("product", {})
    nutriments = product.get("nutriments", {})

    return {
        "name": product.get("product_name") or product.get("product_name_en") or "Unknown product",
        "kcal": nutriments.get("energy-kcal_100g") or nutriments.get("energy_100g", 0),
        "protein": nutriments.get("proteins_100g", 0),
        "carbs": nutriments.get("carbohydrates_100g", 0),
        "fat": nutriments.get("fat_100g", 0),
    }


def render_food_scanner() -> None:
    """Render the barcode scanner section."""
    st.header("Scan Food")

    photo = st.camera_input("Point camera at barcode")

    if photo is None:
        st.caption("Open the camera above and point it at a product barcode.")
        return

    image = Image.open(io.BytesIO(photo.getvalue()))
    barcode = _decode_barcode(image)

    if barcode is None:
        st.warning("No barcode detected. Try holding the camera steadier or moving closer.")
        return

    st.caption(f"Barcode: `{barcode}`")

    product = _fetch_product(barcode)

    if product is None:
        st.warning(f"Product `{barcode}` not found in OpenFoodFacts database.")
        return

    kcal = float(product["kcal"] or 0)
    protein = float(product["protein"] or 0)
    carbs = float(product["carbs"] or 0)
    fat = float(product["fat"] or 0)

    st.subheader(product["name"])

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Calories", f"{kcal:.0f} kcal")
    c2.metric("Protein", f"{protein:.1f} g")
    c3.metric("Carbs", f"{carbs:.1f} g")
    c4.metric("Fat", f"{fat:.1f} g")

    st.caption("Values shown per 100 g")

    if st.button("Add to Today", key="scan_add_to_log", use_container_width=True):
        log_food_entry(
            item=product["name"],
            grams=100,
            kcal=kcal,
            protein=protein,
            carbs=carbs,
            fat=fat,
        )
        st.toast(f"Logged: {product['name']} (100 g)", icon="✅")
        st.rerun()
