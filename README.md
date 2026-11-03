# New albums → Spotify playlist

Weekly flow: musicserver.cz "Nové desky" article → JSON (artist, title, genre tags) → checklist page → Spotify playlist with whole albums.

- `scraper/scrape.py` – finds the newest "Nové desky" article, extracts artist / title / genre tags only (no descriptions), writes `docs/data/archive/YYYY-wWW.json`, `index.json`, `tags.json`.
- `.github/workflows/weekly.yml` – runs Wed 15:30 UTC (+ Thu/Fri fallbacks), commits new data. Idempotent.
- Notification: when a new week is stored, the Action opens a GitHub issue (label `new-week`) assigned to the repo owner, with a link to the page for that week. GitHub emails it to you (Settings → Notifications → Email must be on for "Participating"/"Watching"). The previous week's issue is closed. Re-send: Run workflow with `notify_week` = e.g. `2026-w42`.
- `docs/index.html` – static page (GitHub Pages). Sections are collapsible (genre highlights open, the rest collapsed). Highlights show the article text, loaded live from musicserver.cz through the r.jina.ai reader in your browser and cached locally; it is not stored in the repo. Favourite tags preselect albums; you tick/untick; "Find on Spotify" matches albums; you review; "Create playlist" builds a private playlist with all tracks of the confirmed albums.

## One-time setup

1. Create a GitHub repo, push this folder, enable Pages: Settings → Pages → Branch `main`, folder `/docs`.
2. Spotify Developer Dashboard → Create app → Web API. Redirect URI = the exact page URL shown at the top of the page (e.g. `https://<user>.github.io/<repo>/`). The app owner needs Spotify Premium.
3. Set `DEFAULT_CLIENT_ID` in `docs/index.html` to your Client ID (or paste it on the page and Save), then Connect Spotify.
4. Actions → weekly-new-albums → Run workflow (first run fills week data; paste an article URL to backfill).

No client secret is used (PKCE). Token and favourite tags live in your browser's localStorage only.

## Local checks

```bash
pip install beautifulsoup4
python tests/test_parse.py
python scraper/scrape.py --dry-run --url "https://musicserver.cz/clanek/79858/nove-desky-38-2026-od-lenny-pres-linkin-park-po-tilla-lindemanna/"
```

## Known limits

- Only ~25 albums per week carry a genre line in the article; the rest are listed untagged and never preselected.
- Spotify Development Mode (since Feb 2026): Premium owner, max 5 users, search max 10 results, playlist items endpoints are `/items`. See https://developer.spotify.com/documentation/web-api/tutorials/february-2026-migration-guide
- Personal use only; the site's footer restricts reuse of its content, so only factual metadata is stored.
