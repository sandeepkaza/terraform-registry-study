"""Paper 4 analysis: RQ1 (versioning discipline) + RQ3 (maintenance health).

Usage:
    python analyze.py --modules modules_azurerm.csv modules_aws.csv modules_google.csv \
                      --meta repos_meta.csv --tags repo_tags.csv --out results.md

Pure offline analysis over the collected CSVs. Every number in the paper's
Results section must be reproducible by re-running this script on the
published snapshot.
"""

import argparse
import csv
import re
import statistics
from collections import defaultdict
from datetime import datetime, timezone

SEMVER = re.compile(r"^v?(\d+)\.(\d+)\.(\d+)$")
SNAPSHOT = datetime(2026, 7, 13, tzinfo=timezone.utc)  # collection snapshot date
ABANDON_MONTHS = 18


def load_csv(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def parse_dt(s):
    if not s:
        return None
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def pct(n, d):
    return f"{100 * n / d:.1f}%" if d else "n/a"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--modules", nargs="+", required=True)
    ap.add_argument("--meta", required=True)
    ap.add_argument("--tags", required=True)
    ap.add_argument("--out", default="results.md")
    args = ap.parse_args()

    modules = [r for p in args.modules for r in load_csv(p)]
    meta = {r["repo"]: r for r in load_csv(args.meta) if r.get("not_found") != "True"}
    tags_by_repo = defaultdict(list)
    for r in load_csv(args.tags):
        tags_by_repo[r["repo"]].append(r["tag"])

    # map module -> repo (same regex as github_meta.py)
    def repo_of(row):
        m = re.search(r"github\.com/([^/]+/[^/\s]+)", row.get("source") or "")
        return m.group(1).removesuffix(".git") if m else None

    # official = hyperscaler/vendor namespaces (stratification per mining plan)
    OFFICIAL_NS = {"azure", "aws-ia", "terraform-aws-modules", "googlecloudplatform",
                   "terraform-google-modules", "hashicorp", "oracle", "aws"}

    lines = [f"# Paper 4 — Results snapshot {SNAPSHOT.date()}", ""]

    # ---------- RQ1: versioning discipline ----------
    semver_ok, semver_bad = 0, 0
    major_bumps_per_repo = {}
    for repo, tags in tags_by_repo.items():
        parsed = []
        for t in tags:
            m = SEMVER.match(t.strip())
            if m:
                parsed.append(tuple(map(int, m.groups())))
        if not tags:
            continue
        if len(parsed) / len(tags) >= 0.9:
            semver_ok += 1
        else:
            semver_bad += 1
        majors = {p[0] for p in parsed}
        if parsed:
            created = parse_dt(meta.get(repo, {}).get("created_at"))
            if created:
                years = max((SNAPSHOT - created).days / 365.25, 0.5)
                major_bumps_per_repo[repo] = (len(majors) - 1) / years

    lines += ["## RQ1 Versioning discipline",
              f"- Repos with tags analyzed: {semver_ok + semver_bad}",
              f"- Semver-adherent (≥90% of tags parse as x.y.z): {semver_ok} ({pct(semver_ok, semver_ok + semver_bad)})",
              ""]
    if major_bumps_per_repo:
        rates = sorted(major_bumps_per_repo.values())
        ge1 = sum(1 for r in rates if r >= 1.0)
        lines += [f"- Median major-version bumps/year: {statistics.median(rates):.2f}",
                  f"- Repos averaging ≥1 major (breaking) bump per year: {ge1} ({pct(ge1, len(rates))})",
                  ""]

    # ---------- RQ3: maintenance health ----------
    n = len(meta)
    archived = sum(1 for r in meta.values() if r.get("archived") == "True")
    solo = sum(1 for r in meta.values() if r.get("contributor_count") == "1")
    abandoned = 0
    for r in meta.values():
        pushed = parse_dt(r.get("pushed_at"))
        if pushed and (SNAPSHOT - pushed).days > ABANDON_MONTHS * 30:
            abandoned += 1
    stars = sorted(int(r["stars"]) for r in meta.values() if r.get("stars"))
    lines += ["## RQ3 Maintenance health",
              f"- Repos resolved on GitHub: {n}",
              f"- Archived: {archived} ({pct(archived, n)})",
              f"- Single-contributor (bus factor 1): {solo} ({pct(solo, n)})",
              f"- No push in >{ABANDON_MONTHS} months (abandonment proxy): {abandoned} ({pct(abandoned, n)})",
              f"- Median stars: {statistics.median(stars) if stars else 'n/a'}",
              ""]

    # ---------- stratification: official vs community ----------
    strata = defaultdict(lambda: {"n": 0, "downloads": 0})
    for m in modules:
        ns = (m.get("namespace") or "").lower()
        key = "official" if ns in OFFICIAL_NS else "community"
        strata[key]["n"] += 1
        strata[key]["downloads"] += int(m.get("downloads") or 0)
    lines += ["## Stratification (official vs community namespaces)"]
    total_dl = sum(s["downloads"] for s in strata.values())
    for key, s in sorted(strata.items()):
        lines.append(f"- {key}: {s['n']} modules, {pct(s['downloads'], total_dl)} of downloads")
    lines.append("")

    with open(args.out, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"Wrote {args.out}")


if __name__ == "__main__":
    main()
