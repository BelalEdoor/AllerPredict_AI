# 🛒 AllerPredict AI — RAG-Based Food Product Intelligence System

## 📌 Overview
**AllerPredict AI** is a Retrieval-Augmented Generation (RAG) application that analyzes food products based on three main criteria:

1. **Ingredient & Allergy Analysis**  
2. **Ethical Evaluation of the Company/Brand**  
3. **Product Recommendations & Alternatives**

The system retrieves structured product data from a vector database and uses an AI model to generate accurate, context-aware answers.

---

## 🚀 Features

### ✅ Ingredient & Allergy Detection
- Full ingredient list  
- Detected allergens (nuts, gluten, dairy, soy, etc.)  
- Warnings for dietary restrictions  

### ✅ Ethical Product Analyzer
- Environmental impact  
- Brand controversies  
- Ethical standing  

### ✅ Smart Recommendations
- Healthier alternatives  
- Local alternatives  
- Allergy-safe alternatives  

### ✅ Complete RAG Pipeline
- Embedding the food product dataset  
- Vector database retrieval  
- LLM generation grounded in real data  

---

## 🗂️ Dataset
The dataset contains **20 food products**, including:
- Snacks (Oreo, Doritos, Pringles)  
- Drinks (Pepsi, Coca-Cola)  
- Dairy (Almarai, Nadec)  
- Local Palestinian products (Safi Olive Oil, Canaan Tahini)  
- Chocolates (Snickers, Galaxy)

Each product includes:
- Name  
- Category  
- Ingredients  
- Allergen warnings  
- Ethical notes  
- Recommendations  


# AllerPredict – Backend (FastAPI)

This backend provides an AI-powered question-answering system.  
Users submit **text questions**, and the backend returns **AI-generated responses** using an NLP model.

---

## 🚀 Features
- Accepts user questions in plain text  
- Performs natural language processing  
- Returns structured answers  
- Supports multiple request types  
- Provides API documentation via Swagger UI  

---

## ⚙️ API Endpoints

### **POST /ask**
Send a user question to the AI model.

**Body:**
```json
{
  "question": "What foods cause peanut allergies?"
}
```

**Response:**
```json
{
  "answer": "Peanuts commonly cause allergic reactions due to protein XYZ..."
}
```

### **GET /health**
Check if the backend is running.

---

## ▶️ Run the Server
```bash
uvicorn app.main:app --reload
```

Backend runs at:
```
http://127.0.0.1:8000
```

Swagger docs:
```
http://127.0.0.1:8000/docs
```

---

## 🧠 Model
The NLP model is loaded in `model.py`.  
You can replace it with any LLM or custom model.

# AllerPredict – Frontend (React)

This is the web interface for the **AllerPredict AI Question Answering System**.  
Users type a question related to allergies, health, or food safety, and the app sends it to the backend for processing.

---

## 🚀 Features
- Text input box for user questions  
- Sends question to backend API  
- Displays AI-generated answer  
- Clean and simple UI (React + TailwindCSS)  

--- 

## 🧪 How It Works
1. User enters a question in the input field  
2. Clicks **Ask**  
3. Frontend sends POST request to `/ask`  
4. Backend returns an AI-generated response  
5. Response appears on the UI  

---

## 🔌 API Example (Axios)

```js
import axios from "axios";

export const ask = async (question) => {
  const response = await axios.post("http://127.0.0.1:8000/ask", {
    question: question
  });
  return response.data.answer;
};
```

---

## ▶️ Run the Frontend
```bash
npm install
npm run dev
```

Runs at:
```
http://localhost:5173
```


