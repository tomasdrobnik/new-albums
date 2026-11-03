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

---

## Related Topics

- None yet

---

## History

- 2026-11-03: Repo created, Pages enabled, week 42 stored, Spotify linked, first playlist "New albums 2026-W42" (6 albums, 63 tracks) created; Action verified via manual run
- 2026-11-03: Initial documentation

---

**Lines: ~55 / 100 max**
