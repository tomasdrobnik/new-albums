#!/usr/bin/env python3
"""Weekly scraper for musicserver.cz "Nové desky" articles.

Extracts only artist, title and genre tags (no descriptions) and writes JSON
for the static checklist page in docs/.

Usage:
  python scraper/scrape.py                 # find newest article, skip if already stored
  python scraper/scrape.py --url <article> # parse a specific article
  python scraper/scrape.py --dry-run ...   # print summary, write nothing
  python scraper/scrape.py --html file.html --url <article>  # parse a saved file
"""
import argparse
import json
import re
import sys
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin
from urllib.request import Request, urlopen

from bs4 import BeautifulSoup, NavigableString, Tag

BASE = "https://musicserver.cz"
LISTING_URLS = [f"{BASE}/nove-desky/", f"{BASE}/rss/"]
UA = "new-albums-tracker/0.1 (personal, once a week)"
ARTICLE_RE = re.compile(r"/clanek/(\d+)/nove-desky-(\d+)-(\d{4})-[^\"'<>\s]*")

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "docs" / "data"

# Czech / variant genre labels -> canonical English tag. Unknown tags pass through lowercased.
TAG_MAP = {
    "alternativní rock": "alternative rock",
    "alternativní metal": "alternative metal",
    "industriální metal": "industrial metal",
    "klasická hudba": "classical",
    "moderní rock": "rock",
    "moderní metal": "metal",
    "klubová taneční hudba": "club dance",
    "alternativní r'n'b": "alternative r&b",
    "avantgardní pop": "avant-pop",
    "psychedelie": "psychedelic",
    "taneční hudba": "dance",
    "elektronická hudba": "electronic",
    "písničkář": "singer-songwriter",
    "alt pop": "alt pop",
    "hip hop": "hip hop",
    "oratorium": "classical",
    "elektronika": "electronic",
    "elektronický pop": "electropop",
    "psychedelický soul": "psychedelic soul",
    "psychedelický rock": "psychedelic rock",
    "alternativní folk": "alternative folk",
    "alternativní pop": "alternative pop",
    "alternativní country": "alt-country",
    "experimentální hudba": "experimental",
    "experimentální": "experimental",
    "filmová hudba": "soundtrack",
    "soundtrack": "soundtrack",
    "jazz": "jazz",
    "progresivní rock": "progressive rock",
    "instrumentální progresivní rock": "instrumental progressive rock",
    "klasický rock": "classic rock",
    "moderní death metal": "death metal",
    "neopsychedelie": "neo-psychedelia",
}
TOP_KINDS = {"main", "short", "also", "ep", "reissue"}


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()


def slug(s: str) -> str:
    return norm(s).replace(" ", "-")


def fetch(url: str) -> str:
    req = Request(url, headers={"User-Agent": UA, "Accept-Language": "cs,en;q=0.8"})
    with urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", errors="replace")


def find_latest_article() -> str:
    """Return URL of the newest 'Nové desky' article found on the listing page / RSS."""
    best = None
    for listing in LISTING_URLS:
        try:
            text = fetch(listing)
        except Exception as e:  # noqa: BLE001
            print(f"warn: cannot read {listing}: {e}", file=sys.stderr)
            continue
        for m in ARTICLE_RE.finditer(text):
            art_id = int(m.group(1))
            if best is None or art_id > best[0]:
                best = (art_id, urljoin(BASE, m.group(0)))
        if best:
            break
    if not best:
        raise SystemExit("no 'Nové desky' article link found (site layout changed?)")
    return best[1]


def html_to_lines(html: str) -> list[str]:
    """Flatten HTML into text lines. Bold becomes **..**, <li> gets '- ' prefix."""
    soup = BeautifulSoup(html, "html.parser")
    for t in soup(["script", "style", "noscript"]):
        t.decompose()
    out: list[str] = []
    block = {"p", "div", "br", "li", "tr", "td", "th", "h1", "h2", "h3", "h4", "ul", "ol", "table", "hr"}

    def walk(node):
        if isinstance(node, NavigableString):
            out.append(str(node))
            return
        if not isinstance(node, Tag):
            return
        name = node.name
        if name in block:
            out.append("\n")
        if name == "li":
            out.append("- ")
        if name in ("strong", "b"):
            out.append("**")
        for child in node.children:
            walk(child)
        if name in ("strong", "b"):
            out.append("**")
        if name in block:
            out.append("\n")

    walk(soup)
    text = "".join(out).replace("\xa0", " ")
    text = re.sub(r"\*\*\s*\*\*", "", text)  # empty bold
    lines = [re.sub(r"[ \t]+", " ", ln).strip() for ln in text.split("\n")]
    return [ln for ln in lines if ln]


def split_artist_title(s: str):
    s = s.strip().strip("*").strip()
    if " - " in s:
        a, t = s.split(" - ", 1)
        return a.strip(), t.strip()
    return None


def canon_tags(raw: str) -> list[str]:
    tags = []
    for part in re.split(r"\s*/\s*", raw):
        p = part.strip().lower()
        if not p:
            continue
        p = TAG_MAP.get(p, p)
        if p not in tags:
            tags.append(p)
    return tags


def parse(html: str, url: str) -> dict:
    lines = html_to_lines(html)

    # article window: from "Vydáno:" to "DOPORUČENÉ ČLÁNKY"/"Tweet"
    start = next((i for i, ln in enumerate(lines) if ln.startswith("Vydáno:")), 0)
    end = next((i for i, ln in enumerate(lines) if ln.startswith(("DOPORUČENÉ ČLÁNKY", "Tweet")) and i > start), len(lines))
    body = lines[start:end]

    published = None
    m = re.search(r"Vydáno:\s*(\d{2})\.(\d{2})\.(\d{4})", body[0]) if body else None
    if m:
        published = f"{m.group(3)}-{m.group(2)}-{m.group(1)}"
    release_note = next((ln.strip("*_ ") for ln in body if ln.lstrip("*_ ").startswith("V pátek")), None)

    wm = re.search(r"nove-desky-(\d+)-(\d{4})", url)
    week, year = (int(wm.group(1)), int(wm.group(2))) if wm else (None, None)

    albums: dict[str, dict] = {}

    def add(artist, title, kind, tags=None, raw_tags=""):
        key = slug(artist) + "__" + slug(title)
        if key in albums:
            if tags and not albums[key]["tags"]:
                albums[key]["tags"], albums[key]["tags_raw"] = tags, raw_tags
            return
        albums[key] = {
            "id": key,
            "artist": artist,
            "title": title,
            "kind": kind,
            "tags": tags or [],
            "tags_raw": raw_tags,
        }

    mode = "main"
    i = 0
    while i < len(body):
        ln = body[i]
        low = ln.lower().strip("*_| ")

        # section switches
        if low == "v krátkosti":
            mode = "short"; i += 1; continue
        if low == "dále vychází":
            mode = "also"; i += 1; continue
        if mode in ("also", "vinyl", "ep", "reissue"):
            if low.startswith("vychází na vinylu"):
                mode = "vinyl"; i += 1; continue
            if low.rstrip(":") == "ep":
                mode = "ep"; i += 1; continue
            if low.rstrip(":") == "reedice":
                mode = "reissue"; i += 1; continue

        if mode == "main":
            bm = re.match(r"^\*\*(.+?)\*\*$", ln)
            if bm and i + 1 < len(body) and body[i + 1].lower().startswith("žánr:"):
                at = split_artist_title(bm.group(1))
                if at:
                    raw = body[i + 1].split(":", 1)[1].strip()
                    add(at[0], at[1], "main", canon_tags(raw), raw)
                i += 2
                continue
        elif mode == "short":
            bm = re.match(r"^-\s*\*\*(.+?)\*\*", ln)
            if bm:
                at = split_artist_title(bm.group(1))
                if at:
                    add(at[0], at[1], "short")
        elif mode == "also":
            at = split_artist_title(ln)
            if at and not ln.startswith(("-", "*")):
                add(at[0], at[1], "also")
        elif mode == "ep":
            at = split_artist_title(ln)
            if at:
                add(at[0], at[1], "ep")
        elif mode == "reissue":
            at = split_artist_title(ln)
            if at:
                add(at[0], at[1], "reissue")
        # mode == "vinyl": duplicates of earlier sections, ignored
        i += 1

    return {
        "week": week,
        "year": year,
        "source_url": url,
        "published": published,
        "release_note": release_note,
        "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "albums": list(albums.values()),
    }


def write_outputs(data: dict) -> Path:
    (DATA / "archive").mkdir(parents=True, exist_ok=True)
    name = f"{data['year']}-w{data['week']:02d}.json"
    path = DATA / "archive" / name
    path.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")

    weeks = sorted(
        (p.name for p in (DATA / "archive").glob("*.json")), reverse=True
    )
    index = {"updated": data["fetched_at"], "weeks": weeks}
    (DATA / "index.json").write_text(json.dumps(index, indent=1), encoding="utf-8")

    # tag catalogue across all weeks, for tag suggestions in the UI
    counts: dict[str, int] = {}
    for w in weeks:
        for a in json.loads((DATA / "archive" / w).read_text(encoding="utf-8"))["albums"]:
            for t in a["tags"]:
                counts[t] = counts.get(t, 0) + 1
    (DATA / "tags.json").write_text(
        json.dumps(dict(sorted(counts.items(), key=lambda kv: -kv[1])), ensure_ascii=False, indent=1),
        encoding="utf-8",
    )
    return path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url")
    ap.add_argument("--html", help="parse this saved HTML file instead of downloading")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--force", action="store_true", help="overwrite an existing week")
    args = ap.parse_args()

    url = args.url or find_latest_article()
    wm = re.search(r"nove-desky-(\d+)-(\d{4})", url)
    if wm and not args.force and not args.dry_run:
        existing = DATA / "archive" / f"{wm.group(2)}-w{int(wm.group(1)):02d}.json"
        if existing.exists():
            print(f"already stored: {existing.name}")
            return

    html = Path(args.html).read_text(encoding="utf-8") if args.html else fetch(url)
    data = parse(html, url)

    kinds: dict[str, int] = {}
    for a in data["albums"]:
        kinds[a["kind"]] = kinds.get(a["kind"], 0) + 1
    print(f"{url}\nweek {data['week']}/{data['year']}  published {data['published']}  albums {len(data['albums'])}  {kinds}")

    # sanity gates: fail loudly if the layout changed
    if kinds.get("main", 0) < 5 or len(data["albums"]) < 30:
        sys.exit("parse sanity check failed: too few albums, site layout probably changed")

    if args.dry_run:
        for a in data["albums"][:8]:
            print(" ", a["kind"], "|", a["artist"], "-", a["title"], "|", a["tags"])
        return
    print("wrote", write_outputs(data))


if __name__ == "__main__":
    main()
