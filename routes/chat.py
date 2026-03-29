"""
Glowere Chat Route — Rule-based, stateless conversation engine.
Handles all button flows and message logic.
"""

import json
import os
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

# Load product knowledge
_BASE = os.path.dirname(os.path.dirname(__file__))
with open(os.path.join(_BASE, "config", "products.json"), encoding="utf-8") as f:
    PRODUCT_DB = json.load(f)["products"]

WHATSAPP_URL = "https://wa.me/923048201937"


class ChatRequest(BaseModel):
    session_id: str
    action: Optional[str] = None    # button action key
    message: Optional[str] = None   # free-text message


class Button(BaseModel):
    label: str
    action: str


class ChatResponse(BaseModel):
    reply: str
    buttons: Optional[list] = None
    show_image_upload: Optional[bool] = False
    show_whatsapp: Optional[bool] = False
    whatsapp_url: Optional[str] = None
    products: Optional[list] = None   # list of recommended product dicts


def _product(name: str) -> dict:
    """Lookup product from DB by name (case-insensitive partial match)."""
    name_lower = name.lower()
    for p in PRODUCT_DB:
        if name_lower in p["name"].lower():
            return {"name": p["name"], "tagline": p["tagline"], "usage": p["usage"], "url": p.get("url")}
    return {"name": name, "tagline": "", "usage": "", "url": None}


def _products_for(*names: str) -> list:
    return [_product(n) for n in names]


# ─────────────────────────────────────────
# ACTION HANDLERS
# ─────────────────────────────────────────

def handle_welcome(_req: ChatRequest) -> dict:
    return {
        "reply": (
            "Hi 👋 Welcome to *Glowere*!\n"
            "I can help you find the right skincare, track orders, or answer any questions 😊\n\n"
            "What would you like to do?"
        ),
        "buttons": [
            {"label": "🔍 Find Right Product", "action": "find_product"},
            {"label": "🖼️ AI Skin Analysis", "action": "skin_analysis"},
            {"label": "😣 Acne / Pimples Help", "action": "acne_help"},
            {"label": "🌑 Pigmentation / Dark Spots", "action": "pigmentation_help"},
            {"label": "✨ Daily Glow Routine", "action": "daily_routine"},
            {"label": "📦 Track My Order", "action": "track_order"},
            {"label": "💬 Talk to Human", "action": "human_support"},
        ],
    }


def handle_find_product(_req: ChatRequest) -> dict:
    return {
        "reply": "Tell me your main skin concern 👇",
        "buttons": [
            {"label": "😣 Acne / Pimples", "action": "acne_help"},
            {"label": "🌑 Dark Spots / Pigmentation", "action": "pigmentation_help"},
            {"label": "😐 Dull / Uneven Skin", "action": "dull_skin_help"},
            {"label": "🌿 Daily Skincare", "action": "daily_routine"},
        ],
    }


def handle_acne_help(_req: ChatRequest) -> dict:
    return {
        "reply": (
            "For acne-prone skin, here's what I recommend 👇\n\n"
            "✅ *GloWin Anti Acne Face Wash* — deep cleanses pores twice daily\n"
            "✅ *GloWin Anti Acne Cream* — targets breakouts overnight\n"
            "✅ *GlowCare Sunscreen SPF 60* — must use in the morning with actives\n\n"
            "💡 If your skin is combination type, also add *GlowSkin Moisturizer* to avoid over-drying.\n\n"
            "Results usually improve within 3–4 weeks of consistent use 🌿"
        ),
        "products": _products_for(
            "GloWin Anti Acne Face Wash",
            "GloWin Anti Acne Cream",
            "GlowCare Sunscreen SPF 60",
        ),
        "buttons": [
            {"label": "📋 Full Routine", "action": "daily_routine"},
            {"label": "🛒 Place Order Help", "action": "order_help"},
            {"label": "💬 Talk to Human", "action": "human_support"},
        ],
    }


def handle_pigmentation_help(_req: ChatRequest) -> dict:
    return {
        "reply": (
            "For dark spots & pigmentation 👇\n\n"
            "✅ *GlowVit-C Vitamin C Serum 10%* — brightens & fades dark spots\n"
            "✅ *GlowMark Cream* — reduces marks & uneven tone\n"
            "✅ *GlowCare Sunscreen SPF 60* — CRITICAL to prevent new spots\n\n"
            "💡 Consistency + sunscreen is the key! Most customers see improvement in 4–6 weeks 🌟"
        ),
        "products": _products_for(
            "GlowVit-C Vitamin C Serum 10%",
            "GlowMark Cream",
            "GlowCare Sunscreen SPF 60",
        ),
        "buttons": [
            {"label": "📋 Full Routine", "action": "daily_routine"},
            {"label": "🛒 Place Order Help", "action": "order_help"},
            {"label": "💬 Talk to Human", "action": "human_support"},
        ],
    }


def handle_dull_skin_help(_req: ChatRequest) -> dict:
    return {
        "reply": (
            "For dull & uneven skin, here's what works 👇\n\n"
            "✅ *GlowMark Face Wash* — brightening daily cleanser\n"
            "✅ *GlowShine Whitening Cream* — whitening & brightening night treatment\n"
            "✅ *GlowCare Sunscreen SPF 60* — protect your glow during the day\n\n"
            "💡 You'll notice a visible difference in 3–4 weeks with regular use ✨"
        ),
        "products": _products_for(
            "GlowMark Face Wash",
            "GlowShine Whitening Cream",
            "GlowCare Sunscreen SPF 60",
        ),
        "buttons": [
            {"label": "📋 Full Routine", "action": "daily_routine"},
            {"label": "🛒 Place Order Help", "action": "order_help"},
            {"label": "💬 Talk to Human", "action": "human_support"},
        ],
    }


def handle_daily_routine(_req: ChatRequest) -> dict:
    return {
        "reply": (
            "🌅 *Morning Routine*\n"
            "1. GlowMark Face Wash (or GloWin for acne skin)\n"
            "2. GlowSkin Moisturizer\n"
            "3. GlowCare Sunscreen SPF 60 ☀️\n\n"
            "🌙 *Night Routine*\n"
            "1. Face Wash\n"
            "2. GlowVit-C Vitamin C Serum / Cream\n"
            "3. Glowpar Cream or GlowShine Cream\n\n"
            "Want me to make it minimal or more results-focused? 😊"
        ),
        "buttons": [
            {"label": "🎯 More Results-Focused", "action": "pigmentation_help"},
            {"label": "🌿 Keep It Minimal", "action": "minimal_routine"},
            {"label": "🛒 Place Order Help", "action": "order_help"},
        ],
    }


def handle_minimal_routine(_req: ChatRequest) -> dict:
    return {
        "reply": (
            "Here's a simple 3-step minimal routine 🌿\n\n"
            "☀️ Morning: *Face Wash + Sunscreen*\n"
            "🌙 Night: *Moisturizer*\n\n"
            "Simple, effective, and easy to stick to 😊\n"
            "Let me know if you want help placing the order or choosing the best option for your skin."
        ),
        "products": _products_for(
            "GlowMark Face Wash",
            "GlowCare Sunscreen SPF 60",
            "GlowSkin Moisturizer",
        ),
        "buttons": [
            {"label": "🛒 Place Order Help", "action": "order_help"},
            {"label": "💬 Talk to Human", "action": "human_support"},
        ],
    }


def handle_skin_analysis(_req: ChatRequest) -> dict:
    return {
        "reply": (
            "📸 *AI Skin Analysis*\n"
            "Upload a clear selfie (good lighting, no filter) so I can analyze your skin type 👇\n\n"
            "I'll recommend the perfect Glowere products for you!"
        ),
        "show_image_upload": True,
        "buttons": [],
    }


def handle_track_order(_req: ChatRequest) -> dict:
    return {
        "reply": (
            "Sure 😊 Please share your *order number* so I can check it for you.\n\n"
            "Your order number starts with # and you can find it in your confirmation SMS or email."
        ),
        "buttons": [
            {"label": "💬 Talk to Human Instead", "action": "human_support"},
        ],
    }


def handle_human_support(_req: ChatRequest) -> dict:
    return {
        "reply": (
            "For faster & personalized help, WhatsApp our team 👇\n\n"
            "📲 Our team is available to guide you personally 😊"
        ),
        "show_whatsapp": True,
        "whatsapp_url": WHATSAPP_URL,
        "buttons": [
            {"label": "🔙 Back to Menu", "action": "welcome"},
        ],
    }


def handle_order_help(_req: ChatRequest) -> dict:
    return {
        "reply": (
            "🛒 To place an order, visit our store and add products to your cart.\n\n"
            "✅ *Cash on Delivery* is available across Pakistan\n"
            "🚚 We deliver to all cities\n"
            "💯 All products are 100% genuine & quality-checked\n\n"
            "Need help choosing? I'm here! 😊"
        ),
        "buttons": [
            {"label": "🔍 Find Right Product", "action": "find_product"},
            {"label": "💬 Talk to Human", "action": "human_support"},
        ],
    }


def handle_faq(req: ChatRequest) -> dict:
    msg = (req.message or "").lower()
    if any(w in msg for w in ["cod", "cash", "payment"]):
        reply = "✅ Yes! *Cash on Delivery (COD)* is available across Pakistan. No advance payment needed 😊"
    elif any(w in msg for w in ["deliver", "shipping", "time", "days"]):
        reply = "🚚 We deliver across Pakistan. Delivery time may vary by city but is usually 3–5 working days."
    elif any(w in msg for w in ["real", "original", "genuine", "fake", "authentic"]):
        reply = "💯 All Glowere products are *100% genuine* and quality-checked. We guarantee authenticity."
    elif any(w in msg for w in ["result", "work", "effective", "how long"]):
        reply = "🌿 Results vary from person to person. With regular use, most customers see improvements in *3–6 weeks*."
    elif any(w in msg for w in ["price", "cost", "rate", "kitna"]):
        reply = "💰 For current prices, please visit our store or WhatsApp our team for the latest offers 😊"
    else:
        reply = (
            "I'd love to help! Could you tell me a bit more about your question? 😊\n\n"
            "Or you can WhatsApp our team for instant support."
        )
    return {
        "reply": reply,
        "buttons": [
            {"label": "🔙 Back to Menu", "action": "welcome"},
            {"label": "💬 Talk to Human", "action": "human_support"},
        ],
    }


# ─────────────────────────────────────────
# ACTION ROUTER
# ─────────────────────────────────────────

ACTION_MAP = {
    "welcome": handle_welcome,
    "find_product": handle_find_product,
    "acne_help": handle_acne_help,
    "pigmentation_help": handle_pigmentation_help,
    "dull_skin_help": handle_dull_skin_help,
    "daily_routine": handle_daily_routine,
    "minimal_routine": handle_minimal_routine,
    "skin_analysis": handle_skin_analysis,
    "track_order": handle_track_order,
    "human_support": handle_human_support,
    "order_help": handle_order_help,
}

SALES_CLOSER = "\n\n💬 Let me know if you want help placing the order or choosing the best option for your skin."


@router.post("", response_model=None)
async def chat(req: ChatRequest):
    action = (req.action or "").strip().lower()

    # Route to handler
    if action in ACTION_MAP:
        result = ACTION_MAP[action](req)
    elif req.message:
        result = handle_faq(req)
    else:
        result = handle_welcome(req)

    # Append sales closer to replies with products
    if result.get("products") and SALES_CLOSER not in result["reply"]:
        result["reply"] += SALES_CLOSER

    return ChatResponse(**result)
