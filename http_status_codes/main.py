from fastapi import FastAPI, HTTPException
from sqlalchemy.exc import OperationalError
from database import Base, engine
from routers import users
import uvicorn

app = FastAPI(title="FastAPI Status Code Starter")

Base.metadata.create_all(bind=engine)

app.include_router(users.router)


@app.exception_handler(OperationalError)
def db_down_handler(_, __):
    raise HTTPException(
        status_code=503,
        detail="Database unavailable"
    )


@app.get("/")
def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)