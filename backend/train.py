import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier

print("🚀 Starting model training process...")

# --- 1. Load Data ---
try:
    df = pd.read_csv("captured_data.csv")
except FileNotFoundError:
    print("❌ Error: captured_data.csv not found. Please collect some data first.")
    exit()

print(f"✅ Data loaded successfully. Found {len(df)} records.")

# --- 2. Define Features and Target ---
X = df[['sender', 'subject']]
y = df['user_decision']

# --- 3. Preprocessing & Feature Engineering ---
preprocessor = ColumnTransformer(
    transformers=[
        ('subject_bow', CountVectorizer(), 'subject'),
        ('sender_cat', OneHotEncoder(handle_unknown='ignore'), ['sender'])
    ])

# --- 4. Define the Model ---
model = RandomForestClassifier(n_estimators=100, random_state=42)

# --- 5. Create a Pipeline ---
pipeline = Pipeline(steps=[('preprocessor', preprocessor),
                           ('classifier', model)])

# --- 6. Train the Model ---
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)

print("⏳ Training the model on your decisions...")
pipeline.fit(X_train, y_train)
print("✅ Model training complete.")

# --- 7. Evaluate and Save ---
accuracy = pipeline.score(X_test, y_test)
print(f"📊 Model Accuracy on test data: {accuracy:.2f}")

# Save the entire trained pipeline to a file.
joblib.dump(pipeline, "gmail_model.pkl")
print("💾 Model saved to gmail_model.pkl")