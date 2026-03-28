"""
Glowere Chatbot — FastAPI Backend
Chat logic: stateless, rule-based button-flow driven conversation.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import chat, orders, products, analysis

app = FastAPI(
    title="Glowere Chatbot API",
    description="AI Skincare Assistant backend for Glowere Shopify Store",
    version="1.0.0"
)

# Allow all origins for development; restrict to your Shopify domain in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router, prefix="/chat", tags=["Chat"])
app.include_router(orders.router, prefix="/orders", tags=["Orders"])
app.include_router(products.router, prefix="/products", tags=["Products"])
app.include_router(analysis.router, prefix="/analyze", tags=["Skin Analysis"])


@app.get("/")
def root():
    return {"status": "ok", "message": "Glowere Chatbot API is running 🌿"}
