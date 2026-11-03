import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scraper"))
import scrape  # noqa: E402

URL = "https://musicserver.cz/clanek/79858/nove-desky-38-2026-od-lenny-pres-linkin-park-po-tilla-lindemanna/"

# Fixture mirrors the structure observed on the live page (markdown rendering), NOT a raw HTML capture.
HTML = """
<html><body>
<nav>menu junk - not an album</nav>
<h1>Nové desky 38/2026</h1>
<p>Vydáno: 30.09.2026 14:00 v sekci Nové desky</p>
<p><em>V pátek 25. září vyšly tyto nové tituly:</em></p>
<p><strong><a href="/interpret/Lenny/">Lenny</a> - Good Omens</strong><br>žánr: rock / pop-rock</p>
<p>Some long description - with a dash inside.</p><hr>
<p><strong><a href="#">Linkin Park</a> - Unshatter Film Soundtrack (Live In São Paulo)</strong><br>žánr: alternativní rock / nu metal</p><hr>
<h2>Tip týdne</h2>
<p><strong><a href="#">Himari</a> - Debut</strong><br>žánr: klasická hudba</p><hr>
<p><strong><a href="#">Ann Wilson</a> &amp; <a href="#">Tripsitter</a> - Consecrated Ground</strong><br>žánr: hard rock / psychedelie / blues rock</p>
<table><tr><th>V krátkosti</th></tr></table>
<ul>
<li><strong><a href="#">Hol1D4Y</a> - Topology</strong><br>Scott Holiday, founder - of Rival Sons, ... (<a href="#">YouTube</a>)</li>
<li><strong>World Famous Pets - World Famous Pets</strong><br>Projekt, v němž se potkali ...</li>
</ul>
<table><tr><th>Dále vychází</th></tr></table>
<p>7Ebra - How To Land A Plane<br><a href="#">Aurora</a> - All My Demons Greeting Me As A Friend (10th Anniversary)<br>Kirk $Ki - $Ki Day / Baby Boy</p>
<p><em>Vychází na vinylu:</em><br>7Ebra - How To Land A Plane<br><a href="#">Blondshell</a> - Violins</p>
<p><em>EP:</em><br>Mija - Hard Disco</p>
<p><em>Reedice:</em><br><a href="#">Clannad</a> - Legend<br><a href="#">Rolling Stones</a> - Stripped (Shm-Cd)</p>
<p>Tweet</p>
<h3>DOPORUČENÉ ČLÁNKY</h3>
<p><strong>Noise - Not An Album</strong></p>
</body></html>
"""


def test_parse():
    d = scrape.parse(HTML, URL)
    assert d["week"] == 38 and d["year"] == 2026
    assert d["published"] == "2026-09-30"
    by = {(a["artist"], a["title"]): a for a in d["albums"]}

    lenny = by[("Lenny", "Good Omens")]
    assert lenny["kind"] == "main" and lenny["tags"] == ["rock", "pop-rock"]

    assert by[("Linkin Park", "Unshatter Film Soundtrack (Live In São Paulo)")]["tags"] == [
        "alternative rock",
        "nu metal",
    ]
    assert by[("Himari", "Debut")]["tags"] == ["classical"]
    assert by[("Ann Wilson & Tripsitter", "Consecrated Ground")]["tags"] == [
        "hard rock",
        "psychedelic",
        "blues rock",
    ]

    assert by[("Hol1D4Y", "Topology")]["kind"] == "short"
    assert by[("World Famous Pets", "World Famous Pets")]["kind"] == "short"

    assert by[("7Ebra", "How To Land A Plane")]["kind"] == "also"
    assert by[("Kirk $Ki", "$Ki Day / Baby Boy")]["kind"] == "also"
    assert by[("Mija", "Hard Disco")]["kind"] == "ep"
    assert by[("Clannad", "Legend")]["kind"] == "reissue"

    # vinyl list is a duplicate list and must not create entries or duplicates
    assert ("Blondshell", "Violins") not in by
    assert sum(1 for a in d["albums"] if a["title"] == "How To Land A Plane") == 1
    # content outside the article window is ignored
    assert not any("Not An Album" in a["title"] for a in d["albums"])
    assert not any("menu junk" in a["artist"] for a in d["albums"])
    assert all(a["tags"] == [] for a in d["albums"] if a["kind"] != "main")


if __name__ == "__main__":
    test_parse()
    print("ok")
