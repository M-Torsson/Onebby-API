from fastapi import APIRouter, Query
from fastapi.responses import HTMLResponse, Response

from app.services.trusted_shops_feed import build_trusted_shops_csv, build_trusted_shops_preview_html


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


@router.get("/feeds/trusted-shops.html", tags=["feeds"], response_class=HTMLResponse)
def get_trusted_shops_feed_preview(
    limit: int = Query(100, ge=1, le=5000),
):
    html_content = build_trusted_shops_preview_html(limit=limit)
    return HTMLResponse(content=html_content)