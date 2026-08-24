import httpx
import pytest

from app.main import app


@pytest.mark.asyncio
async def test_root_serves_plain_language_reviewer_interface() -> None:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    assert "What changed?" in response.text
    assert "Why should I believe this?" in response.text
    assert "Approve bounded pilot" in response.text


@pytest.mark.asyncio
async def test_demo_endpoint_returns_complete_signal_to_decision_view() -> None:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/demo")

    assert response.status_code == 200
    payload = response.json()
    assert payload["signal"]["title"] == "Delayed purchase-dispute resolution"
    assert payload["signal"]["external_source"] == "cfpb"
    assert payload["signal"]["internal_source"] == "northstar_synthetic"
    assert payload["signal"]["status"] == "emerging"
    assert len(payload["evidence"]) == 3
    assert {item["role"] for item in payload["evidence"]} == {
        "central",
        "diverse",
        "counter",
    }
    assert len(payload["remediations"]) == 2
    assert payload["remediations"][0]["score"] >= payload["remediations"][1]["score"]
    assert payload["plan"]["status"] == "ready_for_review"
    assert payload["limitations"]


@pytest.mark.asyncio
async def test_demo_approval_updates_plan_and_records_audit_event() -> None:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        await client.post("/api/v1/demo/reset")
        approval = await client.post(
            "/api/v1/demo/plans/northstar-dispute-pilot/approve",
            json={
                "actor": "demo-operations-director",
                "reason": "Evidence, target, and stop condition reviewed",
            },
        )
        refreshed = await client.get("/api/v1/demo")

    assert approval.status_code == 200
    assert approval.json()["plan"]["status"] == "approved_pilot"
    assert approval.json()["audit_event"]["previous_status"] == "ready_for_review"
    assert refreshed.json()["plan"]["status"] == "approved_pilot"
    assert len(refreshed.json()["audit"]) == 1
