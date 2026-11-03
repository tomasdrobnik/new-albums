#!/usr/bin/env python3
"""Print the title (line 1) and Markdown body of the weekly 'new albums' issue.

Usage: python scraper/notify_body.py docs/data/archive/2026-w43.json <page_url> [@owner]
"""
import json
import sys
from pathlib import Path

path, page = Path(sys.argv[1]), sys.argv[2].rstrip("/") + "/"
mention = sys.argv[3] if len(sys.argv) > 3 else ""
d = json.loads(path.read_text(encoding="utf-8"))
week = path.stem  # e.g. 2026-w43

kinds: dict[str, int] = {}
for a in d["albums"]:
    kinds[a["kind"]] = kinds.get(a["kind"], 0) + 1

lines = [
    f"New albums week {d['week']}/{d['year']} are ready ({len(d['albums'])} albums)",
    f"**[Open the checklist for week {d['week']}/{d['year']} →]({page}?week={week})**",
    "",
    f"Source article: {d['source_url']}  ",
    f"Published {d.get('published') or '?'} · "
    + ", ".join(f"{n} {k}" for k, n in kinds.items()),
    "",
    "### Highlights with genre",
]
for a in d["albums"]:
    if a["kind"] == "main":
        tags = ", ".join(a["tags"])
        lines.append(f"- **{a['artist']}** – {a['title']}" + (f" _({tags})_" if tags else ""))
if mention:
    lines += ["", f"cc {mention}"]
print("\n".join(lines))
