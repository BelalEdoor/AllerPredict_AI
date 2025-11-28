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

