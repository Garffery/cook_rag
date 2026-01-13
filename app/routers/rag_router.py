# -*- coding:utf-8 -*-
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from rag_module import RecipeRAGSystem

router = APIRouter(prefix="/rag", tags=["rag"])

# Initialize RAG System
rag_system = None
startup_initialized = False
startup_error = None

try:
    rag_system = RecipeRAGSystem()
    rag_system.initialize_system()
    rag_system.build_knowledge_base()
    startup_initialized = True
except Exception as e:
    startup_error = str(e)

def ensure_rag():
    global rag_system
    if rag_system is None:
        rag_system = RecipeRAGSystem()
        rag_system.initialize_system()
        rag_system.build_knowledge_base()
    return rag_system

class AskRequest(BaseModel):
    question: str
    stream: bool = False

@router.get("/health")
async def health():
    return {"status": "ok", "initialized": startup_initialized, "error": startup_error}

@router.post("/build")
async def build():
    try:
        system = ensure_rag()
        system.initialize_system()
        system.build_knowledge_base()
        return {"status": "built"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/ask")
async def ask(request: AskRequest):
    try:
        if not request.question:
            raise HTTPException(status_code=400, detail="question required")
        
        system = ensure_rag()
        answer = system.ask_question(request.question, stream=False)
        return {"answer": answer}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
