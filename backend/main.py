# Final Version for Phase 0

import pandas as pd
import joblib
from fastapi import FastAPI
from pydantic import BaseModel
import os

# --- Model Loading ---
# This happens once when the server starts up.
print("🧠 Loading the trained model...")
try:
    pipeline = joblib.load("gmail_model.pkl")
    print("✅ Model loaded successfully.")
except FileNotFoundError:
    print("❌ Error: gmail_model.pkl not found. Please run train.py first.")
    pipeline = None

# Initialize the FastAPI app
app = FastAPI()

# --- Data Models ---
# Defines the structure of the data the agent will send for prediction
class EmailContext(BaseModel):
    sender: str
    subject: str

# Defines the structure for capturing the user's final decision
class CapturedData(BaseModel):
    sender: str
    subject: str
    user_decision: str

# --- API Endpoints ---
@app.get("/")
def read_root():
    return {"message": "Tacit Knowledge Engine - Phase 0 Complete 🎉"}

@app.post("/predict")
def predict_action(context: EmailContext):
    """
    Receives email context from the agent and returns a predicted action.
    """
    if not pipeline:
        return {"error": "Model not loaded."}

    # Convert the incoming data into a DataFrame, just like in training
    df = pd.DataFrame([context.dict()])
    
    # Use the loaded pipeline to make a prediction
    prediction = pipeline.predict(df)[0]
    
    print(f"🤖 Prediction: For sender '{context.sender}', predicted action is '{prediction}'")
    return {"predicted_action": prediction}

@app.post("/capture")
def capture_data(data: CapturedData):
    """
    Receives the final user action from the agent and logs it.
    (This remains the same as before)
    """
    DATA_FILE = "captured_data.csv"
    df = pd.DataFrame([data.dict()])
    
    if not os.path.exists(DATA_FILE):
        df.to_csv(DATA_FILE, index=False)
    else:
        df.to_csv(DATA_FILE, mode='a', header=False, index=False)
        
    print(f"✅ User action captured: '{data.user_decision}'")
    return {"status": "success"}