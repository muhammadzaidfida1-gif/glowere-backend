import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse, HTMLResponse
import httpx
import os

# ─────────────────────────────────────────────────────────────────────────────
# STEP 1: CONFIGURE YOUR APP DETAILS
# ─────────────────────────────────────────────────────────────────────────────
# Get these from Partner Dashboard > App Setup
API_KEY = "your_client_id"
API_SECRET = "your_client_secret"
SHOP_URL = "dygyem-en.myshopify.com"  # e.g., glowere-pk.myshopify.com

# Scopes needed for the chatbot
SCOPES = "read_customers,write_customers,write_inventory,read_inventory,read_orders,write_orders,read_products,write_products"
REDIRECT_URI = "http://localhost:3000/callback"

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
async def index():
    """Step 1: Redirect to Shopify authorization page."""
    auth_url = (
        f"https://{SHOP_URL}/admin/oauth/authorize?"
        f"client_id={API_KEY}&"
        f"scope={SCOPES}&"
        f"redirect_uri={REDIRECT_URI}"
    )
    return f"""
    <html>
        <head>
            <title>Glowere Token Helper</title>
            <style>
                body {{ font-family: sans-serif; display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh; background: #f4f6f8; }}
                .card {{ background: white; padding: 2rem; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); text-align: center; }}
                a {{ background: #008060; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px; font-weight: bold; }}
                a:hover {{ background: #006e52; }}
            </style>
        </head>
        <body>
            <div class="card">
                <h1>Glowere Shopify Auth</h1>
                <p>Click below to authorize your app for <b>{SHOP_URL}</b></p>
                <br/>
                <a href="{auth_url}">Authorize App</a>
            </div>
        </body>
    </html>
    """

@app.get("/callback")
async def callback(code: str, shop: str):
    """Step 2: Receive code and exchange for permanent access token."""
    print(f"📦 Received code: {code}")
    
    token_url = f"https://{shop}/admin/oauth/access_token"
    data = {
        "client_id": API_KEY,
        "client_secret": API_SECRET,
        "code": code
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(token_url, json=data)
        
    if response.status_code == 200:
        access_token = response.json().get("access_token")
        return HTMLResponse(content=f"""
        <html>
            <head>
                <style>
                    body {{ font-family: sans-serif; padding: 2rem; background: #f4f6f8; line-height: 1.6; }}
                    .card {{ background: white; padding: 2rem; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); max-width: 600px; margin: 0 auto; }}
                    code {{ background: #eee; padding: 4px 8px; border-radius: 4px; font-family: monospace; font-size: 1.2rem; color: #d02d2d; word-break: break-all; }}
                    .success {{ color: #008060; font-weight: bold; font-size: 1.5rem; }}
                </style>
            </head>
            <body>
                <div class="card">
                    <p class="success">🎉 Success!</p>
                    <p>Your permanent <b>Offline Access Token</b> is:</p>
                    <code>{access_token}</code>
                    <p><b>Next Steps:</b></p>
                    <ol>
                        <li>Copy the token above (it starts with <code>shpat_...</code>).</li>
                        <li>Add it to your Railway / Production environment variables as <code>SHOPIFY_ADMIN_API_TOKEN</code>.</li>
                        <li>You can now close this terminal and delete this script.</li>
                    </ol>
                </div>
            </body>
        </html>
        """)
    else:
        return {
            "error": "Failed to exchange token", 
            "details": response.json(),
            "status_code": response.status_code
        }

if __name__ == "__main__":
    print("🚀 Starting Token Helper on http://localhost:3000")
    print("Please ensure your App Redirection URL is set to: http://localhost:3000/callback")
    uvicorn.run(app, host="0.0.0.0", port=3000)
