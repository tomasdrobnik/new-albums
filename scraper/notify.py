#!/usr/bin/env python3
"""Weekly 'new albums are ready' notification.

  python scraper/notify.py email docs/data/archive/2026-w43.json <page_url>
      Sends an HTML email via SMTP. Env: SMTP_USER, SMTP_PASS,
      optional SMTP_HOST (default smtp.mail.me.com = iCloud), SMTP_PORT (587),
      NOTIFY_TO (default SMTP_USER).
  python scraper/notify.py issue docs/data/archive/2026-w43.json <page_url>
      Prints the GitHub issue title (line 1) and Markdown body (fallback).
  python scraper/notify.py preview ... -> writes email.html for a local look.
"""
import json
import os
import smtplib
import sys
from email.message import EmailMessage
from html import escape
from pathlib import Path


def load(path: Path, page: str):
    d = json.loads(path.read_text(encoding="utf-8"))
    link = f"{page.rstrip('/')}/?week={path.stem}"
    kinds: dict[str, int] = {}
    for a in d["albums"]:
        kinds[a["kind"]] = kinds.get(a["kind"], 0) + 1
    main = [a for a in d["albums"] if a["kind"] == "main"]
    return d, link, kinds, main


def subject(d) -> str:
    return f"New albums week {d['week']}/{d['year']} are ready ({len(d['albums'])} albums)"


def html_body(d, link, kinds, main) -> str:
    rows = "".join(
        f"<li><b>{escape(a['artist'])}</b> – {escape(a['title'])}"
        + (f" <span style='color:#6b6b66'>({escape(', '.join(a['tags']))})</span>" if a["tags"] else "")
        + "</li>"
        for a in main
    )
    counts = ", ".join(f"{n} {k}" for k, n in kinds.items())
    return f"""<!doctype html><html><body style="font:15px/1.45 -apple-system,Segoe UI,Roboto,sans-serif;color:#1c1c1a">
<h2 style="margin:0 0 12px">New albums week {d['week']}/{d['year']}</h2>
<p><a href="{escape(link)}" style="display:inline-block;background:#1a7f4b;color:#fff;text-decoration:none;
padding:10px 18px;border-radius:6px;font-weight:600">Open the checklist →</a></p>
<p style="color:#6b6b66;font-size:13px">Published {escape(d.get('published') or '?')} · {counts}<br>
<a href="{escape(d['source_url'])}">Source article on musicserver.cz</a></p>
<h3 style="font-size:14px;margin:16px 0 4px">Highlights with genre</h3><ul style="padding-left:18px">{rows}</ul>
<p style="font-size:12px;color:#6b6b66">Link: {escape(link)}</p>
</body></html>"""


def text_body(d, link, kinds, main) -> str:
    lines = [f"Open the checklist: {link}", "", f"Source article: {d['source_url']}", "", "Highlights with genre:"]
    lines += [f"- {a['artist']} – {a['title']}" + (f" ({', '.join(a['tags'])})" if a["tags"] else "") for a in main]
    return "\n".join(lines)


def issue_md(d, link, kinds, main) -> str:
    lines = [subject(d), f"**[Open the checklist for week {d['week']}/{d['year']} →]({link})**", "",
             f"Source article: {d['source_url']}", "", "### Highlights with genre"]
    lines += [f"- **{a['artist']}** – {a['title']}" + (f" _({', '.join(a['tags'])})_" if a["tags"] else "") for a in main]
    return "\n".join(lines)


def main():
    mode, path, page = sys.argv[1], Path(sys.argv[2]), sys.argv[3]
    d, link, kinds, main_ = load(path, page)
    if mode == "issue":
        print(issue_md(d, link, kinds, main_))
        return
    if mode == "preview":
        Path("email.html").write_text(html_body(d, link, kinds, main_), encoding="utf-8")
        print(subject(d), "->", link)
        return
    user, pw = os.environ["SMTP_USER"], os.environ["SMTP_PASS"]
    msg = EmailMessage()
    msg["Subject"] = subject(d)
    msg["From"] = f"New albums <{user}>"
    msg["To"] = os.environ.get("NOTIFY_TO") or user
    msg.set_content(text_body(d, link, kinds, main_))
    msg.add_alternative(html_body(d, link, kinds, main_), subtype="html")
    host, port = os.environ.get("SMTP_HOST") or "smtp.mail.me.com", int(os.environ.get("SMTP_PORT") or 587)
    with smtplib.SMTP(host, port, timeout=30) as s:
        s.starttls()
        s.login(user, pw)
        s.send_message(msg)
    print("sent:", msg["Subject"], "->", msg["To"])


if __name__ == "__main__":
    main()
