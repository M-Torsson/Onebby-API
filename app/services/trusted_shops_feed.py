from __future__ import annotations

import csv
import html
import io
import re
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


def get_trusted_shops_rows(limit: Optional[int] = None) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []

    with SOURCE_FEED_PATH.open("r", encoding="utf-8", newline="") as source_file:
        reader = csv.DictReader(source_file)

        for index, row in enumerate(reader, start=1):
            if limit is not None and index > limit:
                break
            rows.append({header: row.get(header, "") for header in FEED_HEADERS})

    return rows


def build_trusted_shops_csv(limit: Optional[int] = None) -> str:
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=FEED_HEADERS)
    writer.writeheader()

    for row in get_trusted_shops_rows(limit=limit):
        writer.writerow(row)

    return buffer.getvalue()


def build_trusted_shops_preview_html(limit: int = 100) -> str:
    rows = get_trusted_shops_rows(limit=limit)
    cards = "".join(_build_product_card(row) for row in rows)
    total_rows = len(rows)

    return f"""<!DOCTYPE html>
<html lang=\"it\">
<head>
  <meta charset=\"utf-8\">
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
  <title>Anteprima Feed Trusted Shops</title>
  <style>
    :root {{
      --bg: #f5f1e8;
      --panel: rgba(255, 252, 246, 0.9);
      --ink: #1c241f;
      --muted: #617168;
      --line: rgba(28, 36, 31, 0.12);
      --accent: #0f766e;
      --accent-soft: rgba(15, 118, 110, 0.12);
      --chip: #eef3ea;
      --shadow: 0 18px 50px rgba(31, 41, 36, 0.10);
    }}

    * {{ box-sizing: border-box; }}

    body {{
      margin: 0;
      font-family: \"IBM Plex Sans\", \"Segoe UI\", sans-serif;
      color: var(--ink);
      background:
        radial-gradient(circle at top left, rgba(15, 118, 110, 0.18), transparent 28%),
        radial-gradient(circle at top right, rgba(245, 158, 11, 0.16), transparent 30%),
        linear-gradient(180deg, #faf6ee 0%, var(--bg) 100%);
    }}

    .shell {{
      max-width: 1440px;
      margin: 0 auto;
      padding: 28px 20px 40px;
    }}

    .hero {{
      display: grid;
      grid-template-columns: 1.4fr 0.9fr;
      gap: 18px;
      margin-bottom: 22px;
    }}

    .panel {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 24px;
      box-shadow: var(--shadow);
      backdrop-filter: blur(12px);
    }}

    .intro {{ padding: 28px; }}

    .eyebrow {{
      display: inline-flex;
      gap: 8px;
      align-items: center;
      padding: 7px 12px;
      border-radius: 999px;
      background: var(--accent-soft);
      color: var(--accent);
      font-size: 13px;
      font-weight: 700;
      letter-spacing: 0.03em;
      text-transform: uppercase;
    }}

    h1 {{
      margin: 16px 0 12px;
      font-size: clamp(28px, 4vw, 48px);
      line-height: 1.05;
      letter-spacing: -0.03em;
    }}

    .lead {{
      margin: 0;
      color: var(--muted);
      font-size: 16px;
      line-height: 1.7;
      max-width: 70ch;
    }}

    .actions {{
      display: flex;
      gap: 12px;
      flex-wrap: wrap;
      margin-top: 18px;
    }}

    .button {{
      display: inline-flex;
      align-items: center;
      justify-content: center;
      min-height: 46px;
      padding: 0 16px;
      border-radius: 14px;
      text-decoration: none;
      font-weight: 700;
      border: 1px solid var(--line);
      color: var(--ink);
      background: white;
    }}

    .button.primary {{
      background: var(--accent);
      color: white;
      border-color: var(--accent);
    }}

    .stats {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 14px;
      padding: 22px;
      align-content: start;
    }}

    .stat {{
      padding: 18px;
      border-radius: 18px;
      background: rgba(255, 255, 255, 0.75);
      border: 1px solid var(--line);
    }}

    .stat-label {{
      color: var(--muted);
      font-size: 12px;
      text-transform: uppercase;
      letter-spacing: 0.06em;
      margin-bottom: 8px;
      font-weight: 700;
    }}

    .stat-value {{
      font-size: 30px;
      line-height: 1;
      font-weight: 800;
    }}

    .toolbar {{
      display: flex;
      gap: 14px;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 18px;
      padding: 16px 18px;
    }}

    .toolbar input {{
      width: min(420px, 100%);
      min-height: 46px;
      border-radius: 14px;
      border: 1px solid var(--line);
      padding: 0 14px;
      font: inherit;
      background: white;
    }}

    .grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
      gap: 18px;
    }}

    .card {{
      overflow: hidden;
      display: flex;
      flex-direction: column;
    }}

    .card-media {{
      aspect-ratio: 4 / 3;
      background: linear-gradient(135deg, #eff6f4, #f8f4eb);
      border-bottom: 1px solid var(--line);
    }}

    .card-media img {{
      width: 100%;
      height: 100%;
      object-fit: cover;
      display: block;
    }}

    .card-body {{
      padding: 18px;
      display: flex;
      flex-direction: column;
      gap: 12px;
      height: 100%;
    }}

    .chips {{
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
    }}

    .chip {{
      border-radius: 999px;
      background: var(--chip);
      color: var(--ink);
      padding: 6px 10px;
      font-size: 12px;
      font-weight: 700;
    }}

    .title {{
      margin: 0;
      font-size: 18px;
      line-height: 1.35;
    }}

    .title a {{
      color: inherit;
      text-decoration: none;
    }}

    .meta, .description {{
      margin: 0;
      color: var(--muted);
      line-height: 1.6;
      font-size: 14px;
    }}

    .price {{
      font-size: 24px;
      font-weight: 800;
      letter-spacing: -0.02em;
    }}

    .footer-link {{
      margin-top: auto;
      color: var(--accent);
      text-decoration: none;
      font-weight: 700;
    }}

    .empty {{
      display: none;
      margin-top: 18px;
      padding: 22px;
      text-align: center;
      color: var(--muted);
    }}

    @media (max-width: 960px) {{
      .hero {{ grid-template-columns: 1fr; }}
      .toolbar {{ flex-direction: column; align-items: stretch; }}
      .toolbar input {{ width: 100%; }}
    }}
  </style>
</head>
<body>
  <div class=\"shell\">
    <section class=\"hero\">
      <div class=\"panel intro\">
        <div class=\"eyebrow\">Anteprima Feed Trusted Shops</div>
        <h1>Visualizzazione prodotti invece del solo file CSV</h1>
        <p class=\"lead\">Questa pagina legge gli stessi dati del feed e li mostra come schede chiare con immagine, titolo, prezzo, disponibilita, brand, categoria e collegamento diretto. Il file CSV resta invariato.</p>
        <div class=\"actions\">
          <a class=\"button primary\" href=\"/api/feeds/trusted-shops.csv?limit={total_rows}\">Apri CSV</a>
          <a class=\"button\" href=\"/api/feeds/trusted-shops.html?limit=1000\">Apri 1000 prodotti</a>
        </div>
      </div>
      <div class=\"panel stats\">
        <div class=\"stat\">
          <div class=\"stat-label\">Prodotti visibili</div>
          <div class=\"stat-value\">{total_rows}</div>
        </div>
        <div class=\"stat\">
          <div class=\"stat-label\">Feed sorgente</div>
          <div class=\"stat-value\">CSV</div>
        </div>
        <div class=\"stat\">
          <div class=\"stat-label\">Modalita anteprima</div>
          <div class=\"stat-value\">HTML</div>
        </div>
        <div class=\"stat\">
          <div class=\"stat-label\">Categorie</div>
          <div class=\"stat-value\">Clean</div>
        </div>
      </div>
    </section>

    <section class=\"panel toolbar\">
      <div>
        <strong>Cerca prodotti</strong><br>
        <span style=\"color: var(--muted); font-size: 14px;\">Cerca per titolo, brand, categoria o GTIN</span>
      </div>
      <input id=\"search\" type=\"search\" placeholder=\"Cerca titolo, brand, categoria, GTIN...\">
    </section>

    <section id=\"grid\" class=\"grid\">{cards}</section>
    <section id=\"empty\" class=\"panel empty\">Nessun prodotto corrisponde alla ricerca corrente.</section>
  </div>

  <script>
    const searchInput = document.getElementById('search');
    const cards = Array.from(document.querySelectorAll('[data-search]'));
    const emptyState = document.getElementById('empty');

    searchInput.addEventListener('input', () => {{
      const query = searchInput.value.trim().toLowerCase();
      let visible = 0;

      for (const card of cards) {{
        const haystack = card.dataset.search;
        const match = !query || haystack.includes(query);
        card.style.display = match ? '' : 'none';
        if (match) visible += 1;
      }}

      emptyState.style.display = visible === 0 ? 'block' : 'none';
    }});
  </script>
</body>
</html>"""


def _build_product_card(row: dict[str, str]) -> str:
    title = html.escape(row.get("title", "") or "Prodotto senza titolo")
    brand = html.escape(row.get("brand", "") or "Brand non disponibile")
    category = html.escape(row.get("product_type", "") or "Categoria non disponibile")
    availability = html.escape(row.get("availability", "") or "Non disponibile")
    condition = html.escape(row.get("condition", "") or "Non disponibile")
    gtin = html.escape(row.get("gtin", "") or row.get("id", ""))
    price = html.escape(row.get("price", "") or "")
    link = html.escape(row.get("link", "") or "#", quote=True)
    image_link = html.escape(row.get("image_link", "") or "", quote=True)
    description = html.escape(_truncate_text(_strip_html_tags(row.get("description", "")), 180))
    search_text = html.escape(
        " ".join(
            [
                row.get("title", ""),
                row.get("brand", ""),
                row.get("product_type", ""),
                row.get("gtin", ""),
                row.get("id", ""),
            ]
        ).lower(),
        quote=True,
    )

    image_markup = (
        f'<img src="{image_link}" alt="{title}" loading="lazy">'
        if image_link
        else '<div style="height:100%;display:flex;align-items:center;justify-content:center;color:#617168;font-weight:700;">Nessuna immagine</div>'
    )

    return f"""
    <article class=\"panel card\" data-search=\"{search_text}\">
      <div class=\"card-media\">{image_markup}</div>
      <div class=\"card-body\">
        <div class=\"chips\">
          <span class=\"chip\">{brand}</span>
          <span class=\"chip\">{availability}</span>
          <span class=\"chip\">{condition}</span>
        </div>
        <h2 class=\"title\"><a href=\"{link}\" target=\"_blank\" rel=\"noreferrer\">{title}</a></h2>
        <div class=\"price\">{price}</div>
        <p class=\"meta\"><strong>Categoria:</strong> {category}</p>
        <p class=\"meta\"><strong>GTIN:</strong> {gtin}</p>
        <p class=\"description\">{description}</p>
        <a class=\"footer-link\" href=\"{link}\" target=\"_blank\" rel=\"noreferrer\">Apri scheda prodotto</a>
      </div>
    </article>"""


def _strip_html_tags(value: str) -> str:
    return re.sub(r"<[^>]+>", " ", value or "")


def _truncate_text(value: str, max_length: int) -> str:
    compact = re.sub(r"\s+", " ", value).strip()
    if len(compact) <= max_length:
        return compact
    return compact[: max_length - 1].rstrip() + "..."