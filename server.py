import os
import uvicorn
from fastapi import FastAPI
from dotenv import load_dotenv
from app.routers import rag_router

load_dotenv()

app = FastAPI()

app.include_router(rag_router)

if __name__ == "__main__":
    port = int(os.getenv("PORT", "9000"))
    uvicorn.run(app, host="127.0.0.1", port=port)
