import json
from sentence_transformers import SentenceTransformer
import subprocess
import os

EMB_MODEL = "all-MiniLM-L6-v2"
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
META_PATH = os.path.join(BASE_DIR, "data", "metadata.json")

OLLAMA_MODEL = "phi3"

# Load resources + generate embeddings once
def load_resources():
    model = SentenceTransformer(EMB_MODEL)

    with open(META_PATH, "r", encoding="utf-8") as f:
        meta = json.load(f)

    # Generate embeddings once
    for item in meta:
        item["embedding"] = model.encode([item["description"]])[0].tolist()

    return model, meta

# Encode the query
def encode_query(model, text):
    return model.encode([text])[0]

# Query Chroma (top_k results)
def query_chroma(meta, query_emb, model, top_k=2):
    scored = []
    for item in meta:
        doc_emb = item["embedding"]
        score = sum(a*b for a,b in zip(query_emb, doc_emb))
        scored.append((score, item))
    
    scored.sort(reverse=True, key=lambda x: x[0])
    return scored[:top_k]


# Ask Ollama
def ask_ollama(context, question, meta):
    product = next((item for item in meta if item["name"].lower() == question.lower()), None)

    if not product:
        return json.dumps({
            "detected_allergens": [],
            "risk_level": "unknown",
            "ethical_score": 0,
            "recommendations": []
        })

    prompt = f"""
You are a food product assistant. Use ONLY the context below to answer.

### CONTEXT ###
{context}

### QUESTION ###
{question}

Respond ONLY with a STRICT valid JSON:
{{
  "detected_allergens": [],
  "risk_level": "",
  "ethical_score": 0,
  "recommendations":""
}}
No explanation. No text outside JSON.
"""

    try:
        result = subprocess.run(
            ["ollama", "run", OLLAMA_MODEL],
            input=prompt.encode("utf-8"),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=120  # زيادة timeout
        )

        raw = result.stdout.decode("utf-8").strip()

        # استخراج JSON من الاستجابة
        first = raw.find("{")
        last = raw.rfind("}")
        if first == -1 or last == -1:
            data = {}
        else:
            try:
                json_text = raw[first:last+1]
                data = json.loads(json_text)
            except:
                data = {}

        # detected_allergens
        detected = data.get("detected_allergens", [])
        if isinstance(detected, str):
            detected = [a.strip() for a in detected.split(",") if a.strip()]
        if not isinstance(detected, list):
            detected = []

        # risk_level
        risk_level = data.get("risk_level", "unknown")

        # ethical_score مع fallback
        ethical = data.get("ethical_score", None)
        if ethical is None:
            ethical = 70 if product.get("ethical_notes") else 50
        try:
            ethical = int(ethical)
        except:
            ethical = 0

        # recommendations دائمًا من metadata
        rec_raw = product.get("recommendations", "")
        if isinstance(rec_raw, str):
            recommendations = [r.strip() for r in rec_raw.split(",") if r.strip()]
        else:
            recommendations = []

        clean_json = {
            "detected_allergens": detected,
            "risk_level": risk_level,
            "ethical_score": ethical,
            "recommendations": recommendations
        }

        return json.dumps(clean_json, indent=2)

    except Exception as e:
        return json.dumps({
            "detected_allergens": [],
            "risk_level": "error",
            "ethical_score": 0,
            "recommendations": [f"ERROR: {e}"]
        })

# Optional: for local testing
if __name__ == "__main__":
    question = input("Enter your question or product name: ")
    model, meta = load_resources()
    query_emb = encode_query(model, question)
    results = query_chroma(meta, query_emb, model)
    context = "\n\n".join([r[1]["description"] for r in results])
    print("\n CONTEXT \n", context)
    answer = ask_ollama(context, question, meta)
    print("\n ANSWER \n", answer)
