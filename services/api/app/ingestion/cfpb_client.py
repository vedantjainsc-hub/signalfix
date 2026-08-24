from dataclasses import dataclass
from typing import Any

import httpx

CFPB_API_URL = "https://www.consumerfinance.gov/data-research/consumer-complaints/search/api/v1/"


@dataclass(frozen=True)
class CFPBPage:
    hits: list[dict[str, Any]]
    total: int
    last_updated: str | None


class CFPBClient:
    def __init__(self, http_client: httpx.AsyncClient, user_agent: str) -> None:
        self.http_client = http_client
        self.user_agent = user_agent

    async def fetch_complaints(
        self,
        *,
        product: str,
        received_from: str,
        received_before: str,
        narrative_only: bool,
        size: int,
    ) -> CFPBPage:
        response = await self.http_client.get(
            CFPB_API_URL,
            params={
                "product": product,
                "date_received_min": received_from,
                "date_received_max": received_before,
                "has_narrative": str(narrative_only).lower(),
                "size": size,
                "sort": "created_date_asc",
            },
            headers={"User-Agent": self.user_agent},
        )
        response.raise_for_status()
        payload = response.json()
        return CFPBPage(
            hits=payload["hits"]["hits"],
            total=payload["hits"]["total"]["value"],
            last_updated=payload.get("_meta", {}).get("last_updated"),
        )
