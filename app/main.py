from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.database import get_db
from app.celery_app import celery_app

app = FastAPI(title="PFM System")

@app.get("/")
def read_root():
    return {"message": "System is Online"}

@app.get("/health/db")
def test_db_connection(db: Session = Depends(get_db)):
    """Verifica se a API consegue falar com o Banco"""
    try:
        # Tenta executar uma query simples (SELECT 1)
        db.execute(text("SELECT 1"))
        return {"status": "ok", "database": "connected"}
    except Exception as e:
        return {"status": "error", "detail": str(e)}

@app.get("/health/worker")
def test_worker_task():
    """Dispara uma tarefa simples para o Celery"""
    # Valida se o Celery está respondendo
    return {"status": "celery configuration loaded", "broker": celery_app.conf.broker_url}