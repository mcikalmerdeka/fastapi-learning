from fastapi import FastAPI
from pydantic import BaseModel
from transformers import pipeline

# Load the sentiment-analysis model from Hugging Face
model_name = "cardiffnlp/twitter-roberta-base-sentiment"
sentiment_pipeline = pipeline("sentiment-analysis", model=model_name)

# Create FastAPI app
app = FastAPI()

# Define request schema
class TextInput(BaseModel):
    text: str

# Label mapping for more human-readable outputs
label_mapping = {
    "LABEL_0": "negative",
    "LABEL_1": "neutral",
    "LABEL_2": "positive"
}

# Define a root GET endpoint
@app.get("/")
def root():
    return {"message": "Welcome to the Hugging Face ML API"}

# Define a POST endpoint to simulate prediction
@app.post("/predict/")
def predict(input_data: TextInput):
    
    # Use the model to make a prediction
    result = sentiment_pipeline(input_data.text)[0]  # returns a list with one dict
    
    # Map the label to human-readable form
    human_label = label_mapping.get(result["label"])
    
    return {
        "input_text": input_data.text,
        "label": human_label,
        "score": result["score"]
    }
