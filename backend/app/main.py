import json
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional

app = FastAPI(title="Product Analyzer API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load products from JSON once at startup
with open("products.json", "r", encoding="utf-8") as f:
    PRODUCTS = json.load(f)


# Input model
class ProductQuery(BaseModel):
    product_id: Optional[int] = None  


# Output model
class AnalysisOut(BaseModel):
    detected_allergens: List[str]
    risk_level: str
    ethical_score: int
    recommendations: List[str]


@app.post("/analyze_product", response_model=AnalysisOut)
async def analyze_product(query: ProductQuery):

  
    if query.product_id:
        product = next((p for p in PRODUCTS if p["id"] == query.product_id), None)
        if not product:
            return {
                "detected_allergens": [],
                "risk_level": "unknown",
                "ethical_score": 0,
                "recommendations": ["Product not found."]
            }
        product_text = product["ingredients"]
    else:
        return {
            "detected_allergens": [],
            "risk_level": "unknown",
            "ethical_score": 0,
            "recommendations": ["No product ID provided."]
        }

    
    