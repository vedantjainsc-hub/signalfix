from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from app.demo.store import demo_store

app = FastAPI(title="SignalFix API", version="0.1.0")
INDEX_HTML = (Path(__file__).parent / "static" / "index.html").read_text(encoding="utf-8")


@app.get("/", response_class=HTMLResponse)
def reviewer_interface() -> str:
    return INDEX_HTML


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "signalfix-api"}


class ApprovalRequest(BaseModel):
    actor: str
    reason: str


@app.get("/api/v1/demo")
def demo() -> dict:
    return demo_store.view()


@app.post("/api/v1/demo/reset")
def reset_demo() -> dict:
    return demo_store.reset()


@app.post("/api/v1/demo/plans/{plan_id}/approve")
def approve_demo_plan(plan_id: str, request: ApprovalRequest) -> dict:
    try:
        plan, event = demo_store.approve(plan_id, request.actor, request.reason)
    except KeyError as error:
        raise HTTPException(status_code=404, detail="demo plan not found") from error
    except ValueError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error
    return {"plan": plan.model_dump(), "audit_event": event.model_dump()}
