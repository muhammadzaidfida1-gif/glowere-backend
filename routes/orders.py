"""
Glowere — Order Tracking Route
Calls Shopify Admin REST API to fetch order details.
"""

import os
import httpx
from fastapi import APIRouter, HTTPException
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

SHOPIFY_ADMIN_TOKEN = os.getenv("SHOPIFY_ADMIN_API_TOKEN", "")
SHOPIFY_STORE_URL = os.getenv("SHOPIFY_STORE_URL", "")
SHOPIFY_API_VERSION = os.getenv("SHOPIFY_API_VERSION", "2024-01")


@router.get("/{order_id}")
async def get_order(order_id: str):
    if not SHOPIFY_ADMIN_TOKEN or not SHOPIFY_STORE_URL:
        # Demo mode: no Shopify credentials configured
        return {
            "found": False,
            "reply": (
                "⚠️ Order tracking isn't connected yet.\n"
                "Please WhatsApp our team for your order status:\n"
                "📲 wa.me/923048201937"
            ),
        }

    url = f"https://{SHOPIFY_STORE_URL}/admin/api/{SHOPIFY_API_VERSION}/orders/{order_id}.json"
    headers = {"X-Shopify-Access-Token": SHOPIFY_ADMIN_TOKEN}

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(url, headers=headers)

        if resp.status_code == 404:
            return {
                "found": False,
                "reply": (
                    f"😕 I couldn't find order *#{order_id}*.\n"
                    "Please double-check the number or WhatsApp our team for help 😊\n"
                    "📲 wa.me/923048201937"
                ),
            }

        if resp.status_code != 200:
            raise HTTPException(status_code=resp.status_code, detail="Shopify API error")

        order = resp.json().get("order", {})
        status = order.get("fulfillment_status") or "processing"
        financial = order.get("financial_status", "")
        name = order.get("name", f"#{order_id}")
        total = order.get("total_price", "N/A")
        currency = order.get("currency", "PKR")

        status_emoji = {
            "fulfilled": "✅ Delivered",
            "partial": "📦 Partially Shipped",
            "unfulfilled": "🔄 Processing / Packing",
        }.get(status, "🔄 Processing")

        return {
            "found": True,
            "reply": (
                f"📦 *Order {name}*\n"
                f"Status: {status_emoji}\n"
                f"Payment: {financial.title()}\n"
                f"Total: {currency} {total}\n\n"
                "For detailed tracking, WhatsApp our team 😊"
            ),
        }

    except httpx.RequestError:
        return {
            "found": False,
            "reply": (
                "😕 I couldn't connect to our order system right now.\n"
                "Please WhatsApp our team for instant help:\n"
                "📲 wa.me/923048201937"
            ),
        }
