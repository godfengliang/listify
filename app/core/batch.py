"""Batch listing generation from CSV."""

import csv
import io
import json
from app.core.generator import generate_listings


def parse_csv(csv_content: str) -> list[dict]:
    """Parse CSV content into list of product dicts."""
    reader = csv.DictReader(io.StringIO(csv_content))
    products = []
    for row in reader:
        products.append({
            "product_name": row.get("product_name", row.get("name", "")),
            "product_specs": row.get("product_specs", row.get("specs", row.get("description", ""))),
            "target_audience": row.get("target_audience", row.get("audience", "")),
            "key_selling_points": row.get("key_selling_points", row.get("selling_points", "")),
        })
    return products


def generate_batch(products: list[dict], language: str = "English") -> list[dict]:
    """Generate listings for multiple products. Returns list of results."""
    results = []
    for i, product in enumerate(products):
        if not product["product_name"].strip():
            results.append({"error": f"Row {i+1}: product_name is empty"})
            continue
        try:
            listing = generate_listings(
                product_name=product["product_name"],
                product_specs=product["product_specs"],
                target_audience=product["target_audience"],
                key_selling_points=product["key_selling_points"],
                language=language,
            )
            listing["_product_name"] = product["product_name"]
            results.append(listing)
        except Exception as e:
            results.append({"error": f"Row {i+1}: {str(e)}", "_product_name": product["product_name"]})
    return results


def results_to_csv(results: list[dict]) -> str:
    """Convert batch results to CSV format for download."""
    output = io.StringIO()
    writer = csv.writer(output)

    # Header
    writer.writerow([
        "product_name", "status",
        "amazon_title", "amazon_bullets", "amazon_description", "amazon_search_terms",
        "shopify_seo_title", "shopify_description", "shopify_meta_description", "shopify_url_handle",
        "temu_title", "temu_description", "temu_selling_points",
        "tiktok_title", "tiktok_description", "tiktok_video_script_hook", "tiktok_video_script_cta",
        "seo_keywords", "suggested_tags",
    ])

    for r in results:
        name = r.get("_product_name", "")
        if "error" in r:
            writer.writerow([name, "ERROR: " + r["error"]] + [""] * 18)
            continue

        amz = r.get("amazon", {})
        sfy = r.get("shopify", {})
        temu = r.get("temu", {})
        tk = r.get("tiktok_shop", {})
        script = tk.get("video_script", {})

        writer.writerow([
            name, "OK",
            amz.get("title", ""),
            " | ".join(amz.get("bullet_points", [])),
            amz.get("description", ""),
            amz.get("search_terms", ""),
            sfy.get("seo_title", ""),
            sfy.get("description", ""),
            sfy.get("meta_description", ""),
            sfy.get("url_handle", ""),
            temu.get("title", ""),
            temu.get("description", ""),
            " | ".join(temu.get("selling_points", [])),
            tk.get("title", ""),
            tk.get("description", ""),
            script.get("hook", ""),
            script.get("cta", ""),
            ", ".join(r.get("seo_keywords", [])),
            ", ".join(r.get("suggested_tags", [])),
        ])

    return output.getvalue()
