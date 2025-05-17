from fastapi import FastAPI
from pydantic import BaseModel

"""
This is a simple FastAPI app that uses a linear regression model to predict a score based on two features.
"""

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

# Run the app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("simple_app:app", host="127.0.0.1", port=8000, reload=True)