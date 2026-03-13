# agents/pia_pulse/monitors.py

import feedparser
from datetime import datetime

# EUR-Lex RSS-Feed für den AI Act
EURLEX_FEED = "https://eur-lex.europa.eu/rss/search-result.xml?qid=..."

def check_eurlex_updates() -> list:
    """
    Prüft den EUR-Lex RSS-Feed auf neue Veröffentlichungen.

    Warum RSS?
    EUR-Lex bietet RSS-Feeds an, die automatisch aktualisiert
    werden, wenn neue Dokumente veröffentlicht werden.
    So muss Pia nicht die ganze Website durchsuchen.
    """
    feed = feedparser.parse(EURLEX_FEED)

    updates = []
    for entry in feed.entries:
        published = datetime(*entry.published_parsed[:6])
        updates.append({
            "title": entry.title,
            "url": entry.link,
            "published": published.isoformat(),
            "summary": entry.summary
        })

    return updates


def check_freshness(claim_date: str, source_date: str) -> dict:
    """
    Vergleicht das Datum einer Behauptung mit dem Datum der Quelle.

    Einfache Logik:
    - Quelle jünger als 30 Tage → fresh
    - Quelle 30 bis 90 Tage alt → stale
    - Quelle älter als 90 Tage → outdated
    """
    source_dt = datetime.fromisoformat(source_date)
    days_old = (datetime.now() - source_dt).days

    if days_old <= 30:
        return {"freshness": "fresh", "days_old": days_old}
    elif days_old <= 90:
        return {"freshness": "stale", "days_old": days_old}
    else:
        return {"freshness": "outdated", "days_old": days_old}
