import json
from sentence_transformers import SentenceTransformer
import subprocess
import os
import numpy as np

# تعطيل تحذيرات fork
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# إعدادات
EMB_MODEL = "all-MiniLM-L6-v2"
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
META_PATH = os.path.join(BASE_DIR, "data", "metadata.json")
OLLAMA_MODEL = "mistral"
TOP_K = 3

# Load metadata + embeddings
def load_resources():
    model = SentenceTransformer(EMB_MODEL)

    with open(META_PATH, "r", encoding="utf-8") as f:
        meta = json.load(f)

    for item in meta:
        # تحسين embedding ليشمل كل عناصر المنتج
        full_text = (
            f"Name: {item.get('name','')}. "
            f"Category: {item.get('category','')}. "
            f"Ingredients: {item.get('ingredients','')}. "
            f"Allergens: {item.get('allergen_warnings','')}. "
            f"Description: {item.get('description','')}. "
            f"Ethics: {item.get('ethical_notes','')}"
        )
        item["embedding"] = model.encode([full_text])[0].tolist()

    return model, meta


# Encode user query
def encode_query(model, text):
    return model.encode([text])[0]


# Cosine similarity
def cosine_similarity(a, b):
    a = np.array(a)
    b = np.array(b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


# Retrieve top_k similar products
def query_chroma(meta, query_emb, top_k=TOP_K):
    scored = []
    for item in meta:
        score = cosine_similarity(query_emb, item["embedding"])
        scored.append((score, item))
    scored.sort(reverse=True, key=lambda x: x[0])
    return scored[:top_k]


# Find safe alternatives
def get_safe_alternatives(meta, product, max_alternatives=5):
    if not product:
        return []

    main_allergens = set(a.strip().lower() for a in product.get("allergen_warnings", "").split(",") if a.strip())
    main_category = product.get("category", "").lower()

    alternatives = []
    for item in meta:
        if item["name"].lower() == product["name"].lower():
            continue
        if item.get("category", "").lower() != main_category:
            continue

        item_allergens = set(a.strip().lower() for a in item.get("allergen_warnings","").split(",") if a.strip())

        if main_allergens & item_allergens:
            continue

        alternatives.append(item["name"])

    return alternatives[:max_alternatives]


# Ask Ollama
def ask_ollama(context, question):
    prompt = f"""
Analyze the following product:

Your response MUST contain exactly TWO sections only.
Do NOT repeat any information between the sections.

SECTION 1 (JSON):
Return ONLY valid JSON with these exact fields:
- detected_allergens: list
- risk_level: string
- ethical_score: integer
- recommendations: string

SECTION 2 (REPORT):
After the JSON, write a human-friendly product analysis report.
Do NOT repeat details already present in the JSON.
Focus on narrative explanation only.

Use this exact separator between the two sections:

Example output format:

{{
  "detected_allergens": [...],
  "risk_level": "...",
  "ethical_score": ...,
  "recommendations": "..."
}}

Here starts the human-friendly report...
"""

    result = subprocess.run(
        ["ollama", "run", OLLAMA_MODEL],
        input=prompt,
        text=True,
        capture_output=True
    )
    
    return result.stdout.strip()

# User-friendly report
def format_report(product_name, detected_allergens, risk_level, ethical_score, alternatives, ollama_text):
    report = f"==================== Product Analysis Report ====================\n"
    report += f"Product Name       : {product_name}\n"
    report += f"Detected Allergens : {', '.join(detected_allergens) if detected_allergens else 'None'}\n"
    report += f"Risk Level         : {risk_level}\n"
    report += f"Ethical Score      : {ethical_score} / 100\n"
    report += "\n"

    report += "Recommended Alternative Products:\n"
    report += f"  {', '.join(alternatives) if alternatives else 'No safe alternatives available'}\n\n"

    report += "AI Generated Notes:\n"
    report += f"{ollama_text}\n"
    report += "==================================================================\n"
    return report



# MAIN
if __name__ == "__main__":
    question = input("Enter your product name: ").strip()
    model, meta = load_resources()

    # Retrieve
    query_emb = encode_query(model, question)
    top_results = query_chroma(meta, query_emb)

    # Build context شامل لكل الداتا
    context = "\n\n".join([
        f"Product: {p['name']}\n"
        f"Category: {p['category']}\n"
        f"Ingredients: {p['ingredients']}\n"
        f"Allergens: {p['allergen_warnings']}\n"
        f"Ethics: {p['ethical_notes']}\n"
        f"Description: {p['description']}"
        for _, p in top_results
    ])

    # Locate the exact product
    product = next((i for i in meta if i["name"].lower() == question.lower()), None)

    detected_allergens = [a.strip() for a in product.get("allergen_warnings","").split(",") if a.strip()] if product else []
    risk_level = "low" if not detected_allergens else "medium"
    ethical_score = 70 if product and product.get("ethical_notes") else 50
    alternatives = get_safe_alternatives(meta, product)

    ollama_text = ask_ollama(context, question)

    
    report_text = format_report(question, detected_allergens, risk_level, ethical_score, alternatives, ollama_text)
    print("\nUSER-FRIENDLY REPORT\n", report_text)
