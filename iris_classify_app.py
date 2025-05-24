from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import numpy as np

"""
This is a application that uses a simple FastAPI app to classify iris flowers into three species based on their features.
"""
# Load the trained model
model_path = "./models/iris_model.joblib"
model = joblib.load(model_path)

# Create a FastAPI app instance
app = FastAPI()

# Define request body structure
class InputData(BaseModel):
    sepal_length: float
    sepal_width: float
    petal_length: float
    petal_width: float

# Define a root GET endpoint
@app.get("/")
def read_root():
    return {"message": "Welcome to the Iris Classification API!"}

# Define a POST endpoint to simulate prediction
@app.post("/predict/")
def predict(data: InputData):
    # Preprocess the input data
    input_data = np.array([[data.sepal_length, data.sepal_width, data.petal_length, data.petal_width]])

    # Make a prediction
    prediction = model.predict(input_data)

    # Map the prediction to the species name
    species_mapping = {0: "setosa", 1: "versicolor", 2: "virginica"}
    predicted_species = species_mapping[prediction[0]]

    # Return the prediction
    return {"prediction": predicted_species}

# Run the app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("iris_classify_app:app", host="127.0.0.1", port=8000, reload=True)

