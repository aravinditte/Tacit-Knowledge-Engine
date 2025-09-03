import pandas as pd
import joblib
from fastapi import FastAPI
from pydantic import BaseModel
import os
from fastapi.middleware.cors import CORSMiddleware

# --- New for Phase 1 ---
from process_miner import generate_process_map_data

app = FastAPI()

# --- CORS Configuration ---
origins = [
    "http://localhost",
    "http://localhost:3000",
    "https://mail.google.com",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Model Loading ---
pipeline = None
try:
    pipeline = joblib.load("gmail_model.pkl")
    print("✅ Model loaded successfully.")
except FileNotFoundError:
    print("❌ Error: gmail_model.pkl not found.")

# --- Data Models ---
class EmailContext(BaseModel):
    sender: str
    subject: str

class CapturedData(BaseModel):
    sender: str
    subject: str
    user_decision: str

# 🎯 New model for Teaching Mode
class FeedbackData(BaseModel):
    sender: str
    subject: str
    suggestion: str
    feedback: str # Will be 'accepted' or 'rejected'

# --- API Endpoints ---
@app.get("/")
def read_root():
    return {"message": "Tacit Knowledge Engine - Phase 1: Coach Mode Active"}

@app.post("/predict")
def predict_action(context: EmailContext):
    if not pipeline:
        return {"error": "Model not loaded."}
    df = pd.DataFrame([context.dict()])
    prediction = pipeline.predict(df)[0]
    print(f"🤖 Prediction: For sender '{context.sender}', predicted action is '{prediction}'")
    return {"predicted_action": prediction}

@app.post("/capture")
def capture_data(data: CapturedData):
    # This endpoint is still used for the initial data gathering
    # but is less important now that we have Coach Mode.
    DATA_FILE = "captured_data.csv"
    df = pd.DataFrame([data.dict()])
    if not os.path.exists(DATA_FILE):
        df.to_csv(DATA_FILE, index=False)
    else:
        df.to_csv(DATA_FILE, mode='a', header=False, index=False)
    print(f"✅ User action captured: '{data.user_decision}'")
    return {"status": "success"}

# 🎯 New endpoint for Teaching Mode
@app.post("/feedback")
def log_feedback(data: FeedbackData):
    """
    Receives feedback from the Mentor Bar and logs it.
    This is the core of "Teaching Mode".
    """
    FEEDBACK_FILE = "feedback_data.csv"
    df = pd.DataFrame([data.dict()])
    
    if not os.path.exists(FEEDBACK_FILE):
        df.to_csv(FEEDBACK_FILE, index=False)
    else:
        df.to_csv(FEEDBACK_FILE, mode='a', header=False, index=False)
        
    print(f"👍 Feedback received: Suggestion '{data.suggestion}' was '{data.feedback}'")
    return {"status": "feedback logged"}

@app.get("/process-map")
def get_process_map():
    return generate_process_map_data()