"""
Glowere — Skin Analysis Route
Accepts an image upload, runs MobileNetV2 for skin type classification,
and returns product recommendations.
"""

import os
import json
import io
from fastapi import APIRouter, File, UploadFile, HTTPException
from PIL import Image
import torch
import torchvision.transforms as transforms
import torchvision.models as models
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

_BASE = os.path.dirname(os.path.dirname(__file__))
with open(os.path.join(_BASE, "config", "skin_mapping.json"), encoding="utf-8") as f:
    SKIN_MAPPING = json.load(f)

# ─── Model Setup ─────────────────────────────────────────────────────────────
# Labels matching training order (oily=0, dry=1, sensitive=2, combination=3)
LABELS = ["oily", "dry", "sensitive", "combination"]

# Transform pipeline matching ImageNet preprocessing
TRANSFORM = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

_model = None  # Lazy-load


def _get_model():
    global _model
    if _model is None:
        # Check if a fine-tuned checkpoint exists
        ckpt_path = os.path.join(_BASE, "model", "skin_classifier.pt")
        if os.path.exists(ckpt_path):
            # Load fine-tuned model
            m = models.mobilenet_v2(weights=None)
            m.classifier[1] = torch.nn.Linear(m.last_channel, 4)
            m.load_state_dict(torch.load(ckpt_path, map_location="cpu"))
        else:
            # Pretrained ImageNet — used in DEMO mode for image property heuristics
            m = models.mobilenet_v2(weights=models.MobileNet_V2_Weights.DEFAULT)
            m.classifier[1] = torch.nn.Linear(m.last_channel, 4)
            # No fine-tuned weights; will use image brightness heuristic as fallback
        m.eval()
        _model = m
    return _model


def _heuristic_skin_type(img: Image.Image) -> str:
    """
    DEMO fallback: approximate skin type from image statistics.
    Replaces the CNN when no trained checkpoint is available.
    High brightness + high saturation → oily
    Low brightness → dry
    High redness → sensitive
    else → combination
    """
    rgb = img.convert("RGB").resize((64, 64))
    pixels = list(rgb.getdata())
    r_avg = sum(p[0] for p in pixels) / len(pixels)
    g_avg = sum(p[1] for p in pixels) / len(pixels)
    b_avg = sum(p[2] for p in pixels) / len(pixels)
    brightness = (r_avg + g_avg + b_avg) / 3
    redness = r_avg - (g_avg + b_avg) / 2

    if brightness > 160:
        return "oily"
    elif redness > 20:
        return "sensitive"
    elif brightness < 90:
        return "dry"
    else:
        return "combination"


@router.post("")
async def analyze_skin(image: UploadFile = File(...)):
    if not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Please upload a valid image file.")

    contents = await image.read()
    try:
        img = Image.open(io.BytesIO(contents)).convert("RGB")
    except Exception:
        raise HTTPException(status_code=400, detail="Could not process the image.")

    ckpt_path = os.path.join(_BASE, "model", "skin_classifier.pt")

    if os.path.exists(ckpt_path):
        # Use the CNN model
        try:
            model = _get_model()
            tensor = TRANSFORM(img).unsqueeze(0)
            with torch.no_grad():
                output = model(tensor)
                pred = torch.argmax(output, dim=1).item()
            skin_type = LABELS[pred]
        except Exception:
            skin_type = _heuristic_skin_type(img)
    else:
        # DEMO mode — heuristic
        skin_type = _heuristic_skin_type(img)

    info = SKIN_MAPPING[skin_type]

    return {
        "skin_type": skin_type,
        "skin_label": info["skin_label"],
        "summary": info["summary"],
        "products": info["products"],
        "routine": info["routine"],
        "demo_mode": not os.path.exists(ckpt_path),
        "reply": (
            f"🔬 *Skin Analysis Result*\n\n"
            f"**{info['skin_label']}** detected!\n"
            f"{info['summary']}\n\n"
            f"Recommended products for you 👇"
        ),
    }
