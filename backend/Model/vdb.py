import json
from sentence_transformers import SentenceTransformer
from chromadb.utils import embedding_functions
import chromadb
import os

DATA_PATH = "./data/data.json"
CHROMA_DIR = "chroma_db"
META_PATH = "metadata.json"

# Load Data :
def load_data(path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if "products" in data:
        return data["products"]
    else:
        raise ValueError("JSON file must contain a 'products' list.")

#  Convert Product To Document :
def make_document(item):
    ingredients = ", ".join(item.get("ingredients", []))
    allergens = ", ".join(item.get("allergen_warnings", []))
    recommendations = ", ".join(item.get("recommendations", []))

    doc = (
        f"Name: {item.get('name')}\n"
        f"Category: {item.get('category')}\n"
        f"Brand: {item.get('brand')}\n"
        f"Description: {item.get('description')}\n"
        f"Ingredients: {ingredients}\n"
        f"Allergens: {allergens}\n"
        f"EthicalNotes: {item.get('ethical_notes')}\n"
        f"Recommendations: {recommendations}\n"
    )
    return doc

#  Build Chroma Index :
def build_chroma_index(items, model_name="all-MiniLM-L6-v2"):

    print("Loading embedding model:", model_name)

    model = SentenceTransformer(model_name)

    embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=model_name
    )

    # Create client using NEW Chroma API
    client = chromadb.PersistentClient(path=CHROMA_DIR)

    # Delete old collection if exists
    try:
        client.delete_collection("products")
        print("Old collection removed.")
    except:
        print("No old collection found. Creating a new one...")

    # Create new collection
    print("Creating collection: products")
    collection = client.create_collection(
        name="products",
        embedding_function=embedding_fn
    )

    # Prepare documents + metadata
    documents = []
    metadatas = []
    ids = []

    for index, it in enumerate(items):
        doc = make_document(it)
        documents.append(doc)
        ids.append(str(index))

       
        metadatas.append({
            "id": str(index),
            "name": it.get("name", ""),
            "category": it.get("category", ""),
            "brand": it.get("brand", ""),
            "description": it.get("description", ""),
            "ingredients": ", ".join(it.get("ingredients", [])),
            "allergen_warnings": ", ".join(it.get("allergen_warnings", [])),
            "ethical_notes": it.get("ethical_notes", ""),
            "recommendations": ", ".join(it.get("recommendations", []))
        })

    # Add to Chroma
    collection.add(
        documents=documents,
        metadatas=metadatas,
        ids=ids
    )

    # Save metadata
    with open(META_PATH, "w", encoding="utf-8") as f:
        json.dump(metadatas, f, indent=2, ensure_ascii=False)

    print("DONE!  Chroma DB created successfully.")
    print("Chroma saved at:", CHROMA_DIR)
    print("Metadata saved at:", META_PATH)

if __name__ == "__main__":
    items = load_data(DATA_PATH)
    build_chroma_index(items)
 