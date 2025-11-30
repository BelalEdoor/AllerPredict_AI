# main.py
import json
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from fastapi.responses import JSONResponse
import os

app = FastAPI(title="Product Analyzer API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load products
DATA_PATH = os.path.join(os.getcwd(), "data", "metadata.json")
with open(DATA_PATH, "r", encoding="utf-8") as f:
    PRODUCTS = json.load(f)


# Models
class ProductQuery(BaseModel):
    product_name: str

class AnalysisOut(BaseModel):
    detected_allergens: List[str]
    risk_level: str
    ethical_score: int
    recommendations: List[str]

# Endpoints
@app.get("/products")
async def get_products():
    return JSONResponse(content=PRODUCTS)


@app.post("/analyze_product", response_model=AnalysisOut)
async def analyze_product(query: ProductQuery):
    product = next((p for p in PRODUCTS if p["name"].lower() == query.product_name.lower()), None)

    if not product:
        return AnalysisOut(
            detected_allergens=[],
            risk_level="unknown",
            ethical_score=0,
            recommendations=["Product not found."]
        )

    ingredients = product.get("ingredients", "")
    allergens = []

    return AnalysisOut(
        detected_allergens=allergens,
        risk_level="high" if allergens else "low",
        ethical_score=70,
        recommendations=["Avoid if you are allergic.", "Consult a specialist if unsure."],
    )
