from __future__ import annotations

import csv
import io
from pathlib import Path
from typing import Optional


SOURCE_FEED_PATH = Path(__file__).resolve().parents[1] / "data" / "trusted_shops_feed.csv"


FEED_HEADERS = [
    "id",
    "title",
    "description",
    "price",
    "availability",
    "brand",
    "product_type",
    "image_link",
    "additional_image_link",
    "link",
    "condition",
    "gtin",
]


def build_trusted_shops_csv(limit: Optional[int] = None) -> str:
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=FEED_HEADERS)
    writer.writeheader()

    with SOURCE_FEED_PATH.open("r", encoding="utf-8", newline="") as source_file:
        reader = csv.DictReader(source_file)

        for index, row in enumerate(reader, start=1):
            if limit is not None and index > limit:
                break
            writer.writerow({header: row.get(header, "") for header in FEED_HEADERS})

    return buffer.getvalue()