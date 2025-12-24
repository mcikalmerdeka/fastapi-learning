# main.py
import uvicorn
from fastapi import FastAPI
import users

import models
from database import engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="My API")

# Include the router
app.include_router(users.router)

@app.get("/")
async def root():
    return {"message": "Welcome to my API"}

# Run the app
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)