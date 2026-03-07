from fastapi import APIRouter, Query
from fastapi.responses import Response

from app.services.trusted_shops_feed import build_trusted_shops_csv


router = APIRouter()


@router.get("/feeds/trusted-shops.csv", tags=["feeds"])
def get_trusted_shops_feed(
    limit: int | None = Query(None, ge=1, le=5000),
):
    csv_content = build_trusted_shops_csv(limit=limit)
    headers = {
        "Content-Disposition": 'inline; filename="trusted-shops-feed.csv"',
        "Cache-Control": "no-store",
    }
    return Response(content=csv_content, media_type="text/csv; charset=utf-8", headers=headers)