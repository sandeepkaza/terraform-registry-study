"""RQ1 cross-check: does a major version bump coincide with removed input variables,
and do minor bumps silently remove variables? (variables.tf via GitHub contents API —
no cloning; 2 calls per version pair.)

Usage:
    python variables_diff.py --tags repo_tags.csv --meta repos_meta.csv --out results_vardiff.md

Method (stated in paper):
- For each repo, parse semver tags. Adjacent-major pair = (highest tag of major N,
  lowest tag of major N+1). Adjacent-minor pair = (highest tag of (major,minor),
  lowest tag of (major,minor+1)) within the same major.
- Sample up to 40 major pairs and 80 minor pairs (seeded RNG, reproducible).
- 'Variable removed' = a `variable "name"` block present in the older tag's root
  variables.tf but absent in the newer tag's. Removal of a root input is a breaking
  change for any consumer that sets it.
- Limitation: variables declared outside variables.tf are missed; repos without a
  root variables.tf at either tag are skipped (counted).
"""

import argparse
import csv
import os
import random
import re
import subprocess
import sys
from collections import defaultdict

import requests

API = "https://api.github.com"
SEMVER = re.compile(r"^v?(\d+)\.(\d+)\.(\d+)$")
VAR_RE = re.compile(r'^\s*variable\s+"([^"]+)"', re.MULTILINE)


def get_token():
    return os.environ.get("GITHUB_TOKEN") or subprocess.check_output(
        ["gh", "auth", "token"], text=True).strip()


SESSION = requests.Session()


def variables_at(repo: str, tag: str) -> set[str] | None:
    r = SESSION.get(f"{API}/repos/{repo}/contents/variables.tf",
                    params={"ref": tag},
                    headers={"Accept": "application/vnd.github.raw+json"},
                    timeout=30)
    if r.status_code == 404:
        return None
    r.raise_for_status()
    return set(VAR_RE.findall(r.text))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tags", default="repo_tags.csv")
    ap.add_argument("--meta", default="repos_meta.csv")
    ap.add_argument("--out", default="results_vardiff.md")
    ap.add_argument("--major-sample", type=int, default=40)
    ap.add_argument("--minor-sample", type=int, default=80)
    args = ap.parse_args()

    SESSION.headers.update({"Authorization": f"Bearer {get_token()}",
                            "X-GitHub-Api-Version": "2022-11-28"})

    by_repo = defaultdict(list)
    with open(args.tags, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            m = SEMVER.match(row["tag"].strip())
            if m:
                by_repo[row["repo"]].append((tuple(map(int, m.groups())), row["tag"]))

    major_pairs, minor_pairs = [], []
    for repo, tags in by_repo.items():
        tags.sort()
        majors = defaultdict(list)
        for ver, name in tags:
            majors[ver[0]].append((ver, name))
        ms = sorted(majors)
        for a, b in zip(ms, ms[1:]):
            if b == a + 1:
                major_pairs.append((repo, majors[a][-1][1], majors[b][0][1]))
        # minor pairs within a major
        for mj in ms:
            minors = defaultdict(list)
            for ver, name in majors[mj]:
                minors[ver[1]].append((ver, name))
            mns = sorted(minors)
            for a, b in zip(mns, mns[1:]):
                if b == a + 1:
                    minor_pairs.append((repo, minors[a][-1][1], minors[b][0][1]))

    rng = random.Random(20260713)  # snapshot date as seed — reproducible
    major_sample = rng.sample(major_pairs, min(args.major_sample, len(major_pairs)))
    minor_sample = rng.sample(minor_pairs, min(args.minor_sample, len(minor_pairs)))

    def assess(pairs, label):
        removed, comparable, skipped = [], 0, 0
        for repo, old, new in pairs:
            try:
                v_old = variables_at(repo, old)
                v_new = variables_at(repo, new)
            except requests.RequestException as e:
                print(f"  skip {repo} {old}->{new}: {e}", file=sys.stderr)
                skipped += 1
                continue
            if v_old is None or v_new is None:
                skipped += 1
                continue
            comparable += 1
            gone = v_old - v_new
            if gone:
                removed.append((repo, old, new, sorted(gone)))
        print(f"{label}: {comparable} comparable, {len(removed)} with removals, "
              f"{skipped} skipped", file=sys.stderr)
        return removed, comparable, skipped

    maj_removed, maj_n, maj_skip = assess(major_sample, "major pairs")
    min_removed, min_n, min_skip = assess(minor_sample, "minor pairs")

    def pct(n, d):
        return f"{100 * n / d:.1f}%" if d else "n/a"

    lines = [
        "# RQ1 cross-check — variables.tf diff across version bumps (seed 20260713)",
        "",
        f"- Population: {len(major_pairs)} adjacent-major pairs, {len(minor_pairs)} adjacent-minor pairs across {len(by_repo)} repos",
        f"- Major-bump sample: {len(major_sample)} drawn, {maj_n} comparable (variables.tf at both tags), {maj_skip} skipped",
        f"- Major bumps with >=1 removed root variable: {len(maj_removed)} ({pct(len(maj_removed), maj_n)})",
        f"- Minor-bump sample: {len(minor_sample)} drawn, {min_n} comparable, {min_skip} skipped",
        f"- Minor bumps with >=1 removed root variable (SILENT breaking): {len(min_removed)} ({pct(len(min_removed), min_n)})",
        "",
        "## Major-bump removals detail",
    ]
    for repo, old, new, gone in maj_removed:
        lines.append(f"- {repo} {old} -> {new}: removed {', '.join(gone[:6])}{' ...' if len(gone) > 6 else ''}")
    lines.append("")
    lines.append("## Minor-bump removals detail (silent breaks)")
    for repo, old, new, gone in min_removed:
        lines.append(f"- {repo} {old} -> {new}: removed {', '.join(gone[:6])}{' ...' if len(gone) > 6 else ''}")

    with open(args.out, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(f"Wrote {args.out}")


if __name__ == "__main__":
    main()
