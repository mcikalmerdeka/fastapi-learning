from fastapi import FastAPI
from pydantic import BaseModel

# Create a FastAPI app instance
app = FastAPI()

# Define request body structure
class InputData(BaseModel):
    feature1: float
    feature2: float

# Define a root GET endpoint
@app.get("/")
def read_root():
    return {"message": "Welcome to your first FastAPI ML API!"}

# Define a POST endpoint to simulate prediction
@app.post("/predict/")
def predict(data: InputData):

    # Simulate prediction logic (e.g., ML model)
    score = data.feature1 * 0.6 + data.feature2 * 0.4
    return {"input": data.model_dump(), "prediction": score}