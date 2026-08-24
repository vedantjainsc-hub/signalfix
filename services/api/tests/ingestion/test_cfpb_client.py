import httpx
import pytest

from app.ingestion.cfpb_client import CFPBClient


@pytest.mark.asyncio
async def test_fetch_complaints_uses_bounded_reproducible_query() -> None:
    captured_request: httpx.Request | None = None

    async def handler(request: httpx.Request) -> httpx.Response:
        nonlocal captured_request
        captured_request = request
        return httpx.Response(
            200,
            json={
                "hits": {
                    "total": {"value": 1, "relation": "eq"},
                    "hits": [{"_source": {"complaint_id": "1"}}],
                },
                "_meta": {"last_updated": "2025-01-02T00:00:00Z"},
            },
        )

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(transport=transport) as http_client:
        client = CFPBClient(http_client=http_client, user_agent="signalfix-test@example.com")
        result = await client.fetch_complaints(
            product="Credit card",
            received_from="2024-01-01",
            received_before="2025-01-01",
            narrative_only=True,
            size=100,
        )

    assert captured_request is not None
    assert captured_request.headers["user-agent"] == "signalfix-test@example.com"
    params = captured_request.url.params
    assert params["product"] == "Credit card"
    assert params["date_received_min"] == "2024-01-01"
    assert params["date_received_max"] == "2025-01-01"
    assert params["has_narrative"] == "true"
    assert params["size"] == "100"
    assert params["sort"] == "created_date_asc"
    assert result.total == 1
    assert result.hits[0]["_source"]["complaint_id"] == "1"
    assert result.last_updated == "2025-01-02T00:00:00Z"
