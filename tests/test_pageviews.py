"""Sidevisninger fra norsk Wikipedia som ekstra kjenthetsmål (uten nettverk)."""
from dypdykk_data.sources import wikidata as wd


def test_nowiki_views(monkeypatch):
    items = {"Q1": {"sitelinks": 90}, "Q2": {"sitelinks": 40}, "Q3": {"sitelinks": 1}}
    monkeypatch.setattr(wd, "_run", lambda q, log, refresh: [
        {"item": {"value": "http://www.wikidata.org/entity/Q1"}, "t": {"value": "A-ha"}},
        {"item": {"value": "http://www.wikidata.org/entity/Q2"}, "t": {"value": "Mayhem (band)"}}])
    def fake_fetch(url, params=None, refresh=False, log=None):
        assert "A-ha" in params["titles"]
        return {"query": {"normalized": [{"from": "Mayhem (band)", "to": "Mayhem (band)"}],
                          "pages": [{"title": "A-ha", "pageviews": {"2026-11-01": 300, "2026-11-02": None}},
                                    {"title": "Mayhem (band)", "pageviews": {"2026-11-01": 20}}]}}
    monkeypatch.setattr(wd, "fetch_json", fake_fetch)
    wd.collect_nowiki_views(items, {"top": 2}, lambda m: None, False)
    assert items["Q1"]["nowiki_views"] == 300
    assert items["Q2"]["nowiki_views"] == 20
    assert items["Q3"]["nowiki_views"] is None   # utenfor «top»
