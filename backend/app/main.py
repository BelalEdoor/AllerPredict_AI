import json
import os
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from fastapi.responses import JSONResponse
import re
# For future RAG/Chroma integration
from sentence_transformers import SentenceTransformer

# ==== Project settings ====
app = FastAPI(title="Product Analyzer API")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==== Load data ====
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_PATH = os.path.join(BASE_DIR, "data", "metadata.json")

with open(DATA_PATH, "r", encoding="utf-8") as f:
    PRODUCTS = json.load(f)

# ==== Models ====
class ProductQuery(BaseModel):
    product_name: str

class AnalysisOut(BaseModel):
    detected_allergens: List[str]
    risk_level: str
    ethical_score: int
    recommendations: List[str]

# ==== Helper functions ====
def calculate_risk(allergens: List[str]) -> str:
    if not allergens:
        return "low"
    elif len(allergens) <= 2:
        return "medium"
    else:
        return "high"

def get_ethical_score(product: dict) -> int:
    if product.get("ethical_notes"):
        return 70
    return 50


# ==== Endpoints ====
@app.get("/products")
async def get_products():
    return JSONResponse(content=PRODUCTS)

@app.post("/analyze_product", response_model=AnalysisOut)
async def analyze_product(query: ProductQuery):
    # Extract product name from natural language
    product_name = query.product_name

    # Partial match search for product
    product = next((p for p in PRODUCTS if product_name.lower() in p["name"].lower()), None)

    if not product:
        return AnalysisOut(
            detected_allergens=[],
            risk_level="unknown",
            ethical_score=0,
            recommendations=["Product not found."]
        )

    # Use data directly from JSON
    allergens = product.get("allergen_warnings", [])
    if isinstance(allergens, str):
        allergens = [a.strip() for a in allergens.split(",") if a.strip()]

    recommendations = product.get("recommendations", [])
    if isinstance(recommendations, str):
        recommendations = [r.strip() for r in recommendations.split(",") if r.strip()]

    ethical_score = get_ethical_score(product)
    risk_level = calculate_risk(allergens)

    return AnalysisOut(
        detected_allergens=allergens,
        risk_level=risk_level,
        ethical_score=ethical_score,
        recommendations=recommendations,
    )