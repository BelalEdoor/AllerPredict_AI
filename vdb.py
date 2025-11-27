# import the needed libraries :
import json
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.utils import embedding_functions
import os

DATA_PATH = "data.json"       
CHROMA_DIR = "chroma_db"      
META_PATH = "metadata.json"

#Loading the data :
def load_data(path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, dict) and "products" in data:
        items = data["products"]
    elif isinstance(data, list):
        items = data
    else:
        raise ValueError("Unknown json structure. Expect {'products': [...]} or a list.")
    return items

def make_document(item):
    ingredients = ", ".join(item.get("ingredients", []))
    allergens = ", ".join(item.get("allergen_warnings", [])) if item.get("allergen_warnings") else "None"
    recommendations = ", ".join(item.get("recommendations", []))
    doc = (
        f"Name: {item.get('name')}\n"
        f"Category: {item.get('category','')}\n"
        f"Brand: {item.get('brand','')}\n"
        f"Description: {item.get('description','')}\n"
        f"Ingredients: {ingredients}\n"
        f"Allergens: {allergens}\n"
        f"EthicalNotes: {item.get('ethical_notes','')}\n"
        f"Recommendations: {recommendations}\n"
    )
    return doc

def build_chroma_index(items, model_name="all-MiniLM-L6-v2"):
    print("Loading embedding model:", model_name)
    model = SentenceTransformer(model_name)
    
    # Building Chroma embedding function :
    embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=model_name)
    
    client = chromadb.Client(chromadb.config.Settings(
        persist_directory=CHROMA_DIR
    ))

    collection = client.get_or_create_collection(
        name="products",
        embedding_function=embedding_fn
    )

    documents = [make_document(it) for it in items]

    # prepare meta data : 
    metadata = []
    for i, it in enumerate(items):
        metadata.append({
            "id": str(i),
            "name": it.get("name", ""),
            "category": it.get("category", ""),
            "brand": it.get("brand", ""),
            "description": it.get("description", ""),
            "ingredients": ", ".join(it.get("ingredients", [])),
            "allergen_warnings": ", ".join(it.get("allergen_warnings", [])),
            "ethical_notes": it.get("ethical_notes", ""),
            "recommendations": ", ".join(it.get("recommendations", []))
        })

    # Add docs to chroma :
    ids = [str(i) for i in range(len(items))]
    collection.add(
        documents=documents,
        metadatas=metadata,
        ids=ids
    )

    with open(META_PATH, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    print("Chroma DB saved at:", CHROMA_DIR)
    print("Metadata saved at:", META_PATH)
    return CHROMA_DIR, META_PATH

if __name__ == "__main__":
    items = load_data(DATA_PATH)
    build_chroma_index(items)
