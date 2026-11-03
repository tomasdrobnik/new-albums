# new-albums architecture and Spotify setup

**ID:** P001
**Last updated:** 2026-11-03
**Status:** Active

---

## Current Understanding

Weekly pipeline: musicserver.cz "Nové desky" article → JSON → static checklist page → private Spotify playlist with whole albums.

- Repo: https://github.com/tomasdrobnik/new-albums (public, so GitHub Pages is free)
- Page: https://tomasdrobnik.github.io/new-albums/ (Pages from `main` /docs)
- Scraper `scraper/scrape.py` (Python + BeautifulSoup) writes `docs/data/archive/YYYY-wWW.json`, `index.json`, `tags.json`
- GitHub Action `weekly.yml`: Wed 15:30 UTC + Thu/Fri 06:30 fallbacks; idempotent ("already stored"), commits only new data
- Client ID built into `docs/index.html` (`DEFAULT_CLIENT_ID`), so each new browser needs only Connect + Agree
- Weekly email = SMTP from Action (`scraper/notify.py`, iCloud smtp.mail.me.com:587, secrets SMTP_USER/SMTP_PASS), button → `?week=YYYY-wWW`; fallback GitHub issue (label `new-week`) if secrets missing
- Article text for genre albums loaded live via `https://r.jina.ai/<article>` (~16 s), cached in localStorage `na.desc.<week>`; NOT stored in repo (site footer forbids reuse)
- Page does Spotify auth with Authorization Code + PKCE in the browser; no client secret; token in localStorage

---

## Key Details

- Spotify app "New albums", Development mode, Web API, Client ID `bb96d763205c40848e69bdb0f4faa2dd` (public identifier, not secret)
- Redirect URI must be exactly `https://tomasdrobnik.github.io/new-albums/` (trailing slash)
- Spotify account linked: antaresin; scope `playlist-modify-private`; refresh token lifetime 180 days
- Feb 2026 Dev Mode rules respected: search limit ≤10, `POST /me/playlists`, `POST /playlists/{id}/items`, `GET /albums/{id}` (no batch)
- Owner needs Premium; max 5 users per app
- Czech genre labels mapped to English in `TAG_MAP`; unknown labels pass through lowercased — extend map when new Czech tags appear in `tags.json`
- Local: `python3 -m venv .venv && .venv/bin/pip install beautifulsoup4`; `.venv/bin/python tests/test_parse.py`; `scraper/scrape.py --dry-run`

---

## Gotchas

- Only ~20-25 albums/week have a genre line; rest are untagged and never preselected
- Week 42/2026 article had no "V krátkosti" section — parser handles missing sections
- Article usually published Wednesday afternoon CET; week number in URL, not ISO week
- GitHub issue emails link to the issue (`#event-…` for assignment), not the page — reason for switching to SMTP
- SMTP 535 auth failures came from bad secret values (one SMTP_PASS saved empty; pasted values with whitespace) — notify.py strips password, tries full address then short username, logs password length; fixed 2026-11-03
- Fallback issue runs when email step outcome == failure (step uses continue-on-error, so its conclusion still shows success)
- Public CORS proxies tested 2026-11-03: corsproxy.io 401 (needs key), allorigins 408, codetabs/cors.lol/whateverorigin fail; only r.jina.ai works

---

## Related Topics

- None yet

---

## History

- 2026-11-03: SMTP email verified working (run 41619889844)
- 2026-11-03: Notification switched from GitHub issue to SMTP email (issue link not direct); issue kept as fallback
- 2026-11-03: Added live article text, collapsible sections, source links, issue-email notification (test issue #1, email confirmed received)
- 2026-11-03: Client ID built into page (was paste-per-browser; user saw "not connected" in own browser)
- 2026-11-03: Repo created, Pages enabled, week 42 stored, Spotify linked, first playlist "New albums 2026-W42" (6 albums, 63 tracks) created; Action verified via manual run
- 2026-11-03: Initial documentation

---

**Lines: ~55 / 100 max**
