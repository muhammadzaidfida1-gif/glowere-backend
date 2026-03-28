"""
Glowere — Products Route
Returns product list from Shopify Storefront API or falls back to local config.
"""

import os
import json
import httpx
from fastapi import APIRouter
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

_BASE = os.path.dirname(os.path.dirname(__file__))
with open(os.path.join(_BASE, "config", "products.json"), encoding="utf-8") as f:
    LOCAL_PRODUCTS = json.load(f)["products"]

SHOPIFY_STOREFRONT_TOKEN = os.getenv("SHOPIFY_STOREFRONT_API_TOKEN", "")
SHOPIFY_STORE_URL = os.getenv("SHOPIFY_STORE_URL", "")
SHOPIFY_API_VERSION = os.getenv("SHOPIFY_API_VERSION", "2024-01")

STOREFRONT_QUERY = """
{
  products(first: 20) {
    edges {
      node {
        id
        title
        descriptionHtml
        priceRange {
          minVariantPrice { amount currencyCode }
        }
        images(first: 1) {
          edges { node { url } }
        }
      }
    }
  }
}
"""


@router.get("")
async def get_products():
    if not SHOPIFY_STOREFRONT_TOKEN or not SHOPIFY_STORE_URL:
        # Fall back to local product config
        return {"source": "local", "products": LOCAL_PRODUCTS}

    url = f"https://{SHOPIFY_STORE_URL}/api/{SHOPIFY_API_VERSION}/graphql.json"
    headers = {
        "X-Shopify-Storefront-Access-Token": SHOPIFY_STOREFRONT_TOKEN,
        "Content-Type": "application/json",
    }

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(url, json={"query": STOREFRONT_QUERY}, headers=headers)

        if resp.status_code == 200:
            data = resp.json()
            edges = data.get("data", {}).get("products", {}).get("edges", [])
            products = []
            for edge in edges:
                node = edge["node"]
                img_edges = node.get("images", {}).get("edges", [])
                products.append({
                    "id": node["id"],
                    "name": node["title"],
                    "price": node["priceRange"]["minVariantPrice"]["amount"],
                    "currency": node["priceRange"]["minVariantPrice"]["currencyCode"],
                    "image": img_edges[0]["node"]["url"] if img_edges else None,
                })
            return {"source": "shopify", "products": products}

    except Exception:
        pass

    return {"source": "local", "products": LOCAL_PRODUCTS}
