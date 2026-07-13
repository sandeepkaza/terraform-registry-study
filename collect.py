"""Collect top Terraform Registry modules for the MSR study (Paper 4, RQ1-RQ4 dataset).

Usage:
    python collect.py --provider azurerm --top 500 --out modules_azurerm.csv
    python collect.py --provider aws --top 500 --out modules_aws.csv

No auth required (public registry API). Be polite: built-in delay between pages.
Record the snapshot date — it goes in the paper's Method section.
"""

import argparse
import csv
import sys
import time
from datetime import date, timezone, datetime

import requests

REGISTRY = "https://registry.terraform.io/v1/modules"
PAGE_SIZE = 100  # registry max is 100 per page


def fetch_modules(provider: str, top: int) -> list[dict]:
    modules = []
    offset = 0
    while len(modules) < top:
        resp = requests.get(
            REGISTRY,
            params={"provider": provider, "limit": PAGE_SIZE, "offset": offset},
            timeout=30,
        )
        resp.raise_for_status()
        batch = resp.json().get("modules", [])
        if not batch:
            break
        modules.extend(batch)
        offset += PAGE_SIZE
        time.sleep(1.0)
        print(f"  fetched {len(modules)} modules...", file=sys.stderr)
    # Registry sort by download count is not guaranteed by the list endpoint;
    # sort explicitly so "top N" is well-defined and stated in the paper.
    modules.sort(key=lambda m: m.get("downloads", 0), reverse=True)
    return modules[:top]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--provider", required=True, choices=["aws", "azurerm", "google"])
    ap.add_argument("--top", type=int, default=500)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    out_path = args.out or f"modules_{args.provider}.csv"
    snapshot = date.today().isoformat()
    print(f"Snapshot date {snapshot} — record this in the Method section.", file=sys.stderr)

    modules = fetch_modules(args.provider, args.top)

    fields = [
        "snapshot_date", "id", "namespace", "name", "provider", "downloads",
        "verified", "source", "published_at", "latest_version", "description",
    ]
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for m in modules:
            w.writerow({
                "snapshot_date": snapshot,
                "id": m.get("id"),
                "namespace": m.get("namespace"),
                "name": m.get("name"),
                "provider": m.get("provider"),
                "downloads": m.get("downloads"),
                "verified": m.get("verified"),
                "source": m.get("source"),  # GitHub URL — input to github_meta.py
                "published_at": m.get("published_at"),
                "latest_version": m.get("version"),
                "description": (m.get("description") or "").replace("\n", " "),
            })
    print(f"Wrote {len(modules)} rows -> {out_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
