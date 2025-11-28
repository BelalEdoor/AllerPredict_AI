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

