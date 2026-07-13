"""RQ2 aggregation: security-default scan results (checkov) -> results_rq2.md."""

import csv
import re
import statistics
from collections import defaultdict

OFFICIAL_NS = {"azure", "aws-ia", "terraform-aws-modules", "googlecloudplatform",
               "terraform-google-modules", "hashicorp", "oracle", "aws"}
FILES = {"azurerm": "scan_azurerm.csv", "aws": "scan_aws.csv", "google": "scan_google.csv"}


def pct(n, d):
    return f"{100 * n / d:.1f}%" if d else "n/a"


lines = ["# Paper 4 — RQ2 results (checkov 3.3.8, module source excl. examples/tests, snapshot 2026-07-13)", ""]
rule_repos = defaultdict(set)   # check_id -> repos failing it
rule_name = {}
strata = defaultdict(lambda: {"repos": set(), "failing": set()})

for provider, path in FILES.items():
    with open(path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    per_repo = {}
    for r in rows:
        repo = r["repo"]
        if repo not in per_repo:
            per_repo[repo] = {"passed": r["passed"], "failed": r["failed"], "module_id": r["module_id"]}
        if r.get("check_id"):
            rule_repos[r["check_id"]].add(repo)
            rule_name[r["check_id"]] = r.get("check_name", "")
        ns = (r["module_id"].split("/")[0] or "").lower()
        key = "official" if ns in OFFICIAL_NS else "community"
        strata[key]["repos"].add(repo)
        if r.get("check_id"):
            strata[key]["failing"].add(repo)

    n = len(per_repo)
    failed_counts = [int(v["failed"]) for v in per_repo.values() if v["failed"] not in ("", None)]
    passed_counts = [int(v["passed"]) for v in per_repo.values() if v["passed"] not in ("", None)]
    with_fail = sum(1 for c in failed_counts if c > 0)
    no_checks = n - len(failed_counts)
    lines += [f"## {provider}",
              f"- Repos scanned: {n} (no terraform checks applicable: {no_checks})",
              f"- Repos with ≥1 failed check: {with_fail} ({pct(with_fail, len(failed_counts))} of scannable)",
              f"- Median failed checks per repo: {statistics.median(failed_counts) if failed_counts else 'n/a'}",
              f"- Median passed checks per repo: {statistics.median(passed_counts) if passed_counts else 'n/a'}",
              ""]

lines += ["## Top 15 failed rules (by distinct repos, all providers)", "",
          "| Rule | Repos failing | Description |", "|---|---|---|"]
for cid, repos in sorted(rule_repos.items(), key=lambda kv: -len(kv[1]))[:15]:
    lines.append(f"| {cid} | {len(repos)} | {rule_name.get(cid, '')[:80]} |")
lines.append("")

lines += ["## Official vs community (repos with ≥1 failed check)"]
for key, s in sorted(strata.items()):
    lines.append(f"- {key}: {len(s['failing'])}/{len(s['repos'])} ({pct(len(s['failing']), len(s['repos']))})")
lines.append("")

with open("results_rq2.md", "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
print("Wrote results_rq2.md")
