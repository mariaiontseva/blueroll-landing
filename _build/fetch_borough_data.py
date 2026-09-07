#!/usr/bin/env python3
"""Pull FSA data for the 33 London boroughs.

Writes _build/data/borough_data.json with everything the page builder needs,
and rotates a slim snapshot (id -> rating) so next week's run can compute
risers and fallers. One API request per borough (pageSize=5000 covers the
largest, Westminster at ~5.7k -- paged just in case). Run from repo root:

    python3 _build/fetch_borough_data.py
"""
import gzip
import json
import sys
import time
import urllib.request
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from borough_config import BOROUGHS  # noqa: E402

DATA = Path(__file__).parent / "data"
DATA.mkdir(exist_ok=True)
RATED = {"0", "1", "2", "3", "4", "5"}
RECENT_DAYS = 31


def fetch(authority_id: int) -> list[dict]:
    out, page = [], 1
    while True:
        url = (f"https://api.ratings.food.gov.uk/Establishments"
               f"?localAuthorityId={authority_id}&pageSize=5000&pageNumber={page}")
        req = urllib.request.Request(url, headers={"x-api-version": "2"})
        d = json.load(urllib.request.urlopen(req, timeout=120))
        out += d["establishments"]
        if len(out) >= d["meta"]["totalCount"] or not d["establishments"]:
            return out
        page += 1


def slim(e: dict) -> dict:
    g = e.get("geocode") or {}
    return {
        "id": e["FHRSID"],
        "name": (e["BusinessName"] or "").strip(),
        "type": (e["BusinessType"] or "").replace("/sandwich shop", "").strip(),
        "addr": ", ".join(x.strip() for x in [e.get("AddressLine1"), e.get("AddressLine2")] if x and x.strip())[:60],
        "pc": e.get("PostCode") or "",
        "r": e["RatingValue"],
        "d": (e["RatingDate"] or "")[:10],
        "lat": g.get("latitude"), "lng": g.get("longitude"),
    }


def main() -> None:
    today = date.today().isoformat()
    cutoff = (date.today() - timedelta(days=RECENT_DAYS)).isoformat()
    prev_path = DATA / "borough_snapshot.json.gz"
    prev = {}
    if prev_path.exists():
        with gzip.open(prev_path, "rt") as f:
            old = json.load(f)
        if old.get("date") != today:  # re-runs on the same day must not eat the diff
            prev = old.get("ratings", {})
            prev_meta = old.get("date")
        else:
            prev = old.get("prev_ratings", {})
            prev_meta = old.get("prev_date")
    else:
        prev_meta = None

    data, snapshot = {"fetched": today, "prev_date": prev_meta, "boroughs": {}}, {}
    for slug, cfg in BOROUGHS.items():
        es = [slim(e) for e in fetch(cfg["id"])]
        rated = [e for e in es if e["r"] in RATED]
        counts = {r: sum(1 for e in rated if e["r"] == r) for r in RATED}
        worst = sorted([e for e in rated if e["r"] in ("0", "1")], key=lambda e: (e["r"], e["d"]))
        recent = [e for e in rated if e["d"] >= cutoff]
        movers = {"up": [], "down": []}
        for e in rated:
            old_r = prev.get(str(e["id"]))
            if old_r and old_r in RATED and old_r != e["r"]:
                (movers["up"] if int(e["r"]) > int(old_r) else movers["down"]).append({**e, "was": old_r})
        movers["up"].sort(key=lambda e: e["d"], reverse=True)
        movers["down"].sort(key=lambda e: e["d"], reverse=True)
        data["boroughs"][slug] = {
            "total": len(es), "rated": len(rated), "counts": counts,
            "pct5": round(100 * counts["5"] / len(rated), 1) if rated else 0,
            "low": counts["0"] + counts["1"] + counts["2"],
            "worst": worst[:15],
            "recent_count": len(recent),
            "recent_new5": sum(1 for e in recent if e["r"] == "5"),
            "recent_low": sorted([e for e in recent if e["r"] in ("0", "1", "2")], key=lambda e: e["d"], reverse=True)[:6],
            "movers_up": movers["up"][:8], "movers_down": movers["down"][:8],
        }
        snapshot.update({str(e["id"]): e["r"] for e in rated})
        print(f"{slug}: {len(es)} est, {counts['5']} fives, {counts['0']+counts['1']} at 0-1, {len(recent)} rated recently")
        time.sleep(1)

    (DATA / "borough_data.json").write_text(json.dumps(data, ensure_ascii=False))
    with gzip.open(prev_path, "wt") as f:
        json.dump({"date": today, "ratings": snapshot,
                   "prev_date": prev_meta, "prev_ratings": prev}, f)
    print("written borough_data.json +", prev_path.name,
          f"(diff base: {prev_meta or 'none yet, movers appear next run'})")


if __name__ == "__main__":
    main()
