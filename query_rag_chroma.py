import json
from sentence_transformers import SentenceTransformer
import subprocess

EMB_MODEL = "all-MiniLM-L6-v2"
META_PATH = "metadata.json"
OLLAMA_MODEL = "phi3"

# Load resources :
def load_resources():
    model = SentenceTransformer(EMB_MODEL)

    with open(META_PATH, "r", encoding="utf-8") as f:
        meta = json.load(f)

    return model, meta

# Encode the query :
def encode_query(model, text):
    return model.encode([text])[0]

#  Query Chroma :
def query_chroma(meta, query_emb, model, top_k=2):
    scored = []
    for item in meta:

        doc_text = item["description"]  
        doc_emb = model.encode([doc_text])[0]

        score = sum(a*b for a,b in zip(query_emb, doc_emb))
        scored.append((score, item))

    scored.sort(reverse=True, key=lambda x: x[0])
    return scored[:top_k]

#  Ask Ollama :
def ask_ollama(context, question):
    prompt = f"""
You are a food product assistant. Use ONLY the following context to answer:

### CONTEXT ###
{context}

### QUESTION ###
{question}

Give a short, clear answer.
"""

    try:
        result = subprocess.run(
            ["ollama", "run", OLLAMA_MODEL],
            input=prompt.encode("utf-8"),
            stdout=subprocess.PIPE
        )
        return result.stdout.decode("utf-8")

    except Exception as e:
        return f"[ERROR calling Ollama] {e}"

# Main :
def main():
    question = input("Enter your question or product name: ")

    model, meta = load_resources()
    query_emb = encode_query(model, question)

    results = query_chroma(meta, query_emb, model)

    context = "\n\n".join([r[1]["description"] for r in results])

    print("\n CONTEXT \n", context)

    answer = ask_ollama(context, question)
    
    print("\n ANSWER \n", answer)

if __name__ == "__main__":
    main()
