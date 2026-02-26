"""
FastAPI service exposing /predict-ticket endpoint for ML models.

Run with:
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8100
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from ml.predict import predict_ticket

PROJECT_ROOT = Path(__file__).resolve().parents[1]

app = FastAPI(title="AI-Powered Ticket Creation API")


class PredictRequest(BaseModel):
    text: str


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.post("/predict-ticket")
def predict_ticket_endpoint(body: PredictRequest) -> Dict[str, Any]:
    """
    Generate a structured ticket from user text using trained models.
    """
    try:
        result = predict_ticket(body.text)
        return result
    except FileNotFoundError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover - safety
        raise HTTPException(status_code=500, detail="Internal prediction error") from exc


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8100, reload=True)

