from fastapi import FastAPI

from app.rutas import router

app = FastAPI(title="API de Materias", version="1.0.0")
app.include_router(router)


@app.get("/")
def raiz() -> dict:
    return {"api": "materias", "docs": "/docs"}