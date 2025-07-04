from fastapi import FastAPI
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
import os
import uvicorn
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Initialize LangChain LLM
llm = ChatOpenAI(model_name="gpt-4.1", api_key=os.getenv("OPENAI_API_KEY"))

# FastAPI app
app = FastAPI()

# Request body model
class PromptRequest(BaseModel):
    prompt: str

# Define a root GET endpoint
@app.get("/")
def root():
    return {"message": "Welcome to the LangChain LLM API"}

# Define a POST endpoint to generate a response
@app.post("/generate")
async def generate_response(request: PromptRequest):
    prompt = request.prompt

    # LangChain call
    messages = [HumanMessage(content=prompt)]
    response = llm(messages)

    return {"response": response.content}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
