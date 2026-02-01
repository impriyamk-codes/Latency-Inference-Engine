from fastapi import FastAPI
from pydantic import BaseModel
from typing import List # <--- NEW IMPORT
import joblib
import time

app = FastAPI(title="TrueSight Latency Engine")

# Load Model (Once)
print("Loading Model...")
model = joblib.load("best_fake_news_model.pkl")
vectorizer = joblib.load("tfidf_vectorizer_best.pkl")
print("Model Loaded Successfully!")

# --- DATA STRUCTURES ---
class NewsRequest(BaseModel):
    text: str

class BatchNewsRequest(BaseModel): # <--- NEW CLASS
    texts: List[str]

# --- ENDPOINTS ---

@app.get("/")
def health_check():
    return {"status": "running"}

# 1. THE TAXI (Real-Time)
@app.post("/predict")
def predict(request: NewsRequest):
    start_time = time.time()
    vectorized_text = vectorizer.transform([request.text])
    prediction = model.predict(vectorized_text)[0]
    prob = model.predict_proba(vectorized_text)[0].max()
    end_time = time.time()
    
    return {
        "label": "REAL" if prediction == 1 else "FAKE",
        "confidence": float(prob),
        "latency_ms": (end_time - start_time) * 1000
    }

# 2. THE BUS (Batch Inference) <--- NEW ENDPOINT
@app.post("/predict_batch")
def predict_batch(request: BatchNewsRequest):
    start_time = time.time()
    
    # 1. Vectorize ALL texts at once (Super efficient)
    vectorized_texts = vectorizer.transform(request.texts)
    
    # 2. Predict ALL at once
    predictions = model.predict(vectorized_texts)
    probs = model.predict_proba(vectorized_texts).max(axis=1)
    
    end_time = time.time()
    total_latency = (end_time - start_time) * 1000
    
    # Create response list
    results = []
    for i, text in enumerate(request.texts):
        results.append({
            "text": text,
            "label": "REAL" if predictions[i] == 1 else "FAKE",
            "confidence": float(probs[i])
        })
    
    return {
        "batch_size": len(request.texts),
        "total_latency_ms": round(total_latency, 4),
        "avg_latency_per_item_ms": round(total_latency / len(request.texts), 4),
        "results": results
    }