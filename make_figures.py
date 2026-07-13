"""Paper figures (vector PDF, IEEE single-column width 3.5in).

Fig 1: months-since-last-push distribution, official vs community strata.
Fig 2: top-10 failed checkov rules by distinct repos, classed hygiene vs defaults.
"""

import csv
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

SNAPSHOT = datetime(2026, 7, 13, tzinfo=timezone.utc)
OFFICIAL = {"azure", "aws-ia", "terraform-aws-modules", "googlecloudplatform",
            "terraform-google-modules", "hashicorp", "oracle", "aws"}
BLUE, AQUA = "#2a78d6", "#1baf7a"
INK, MUTED = "#0b0b0b", "#52514e"

plt.rcParams.update({
    "font.size": 7.5, "axes.labelsize": 7.5, "axes.titlesize": 8,
    "xtick.labelsize": 7, "ytick.labelsize": 7, "legend.fontsize": 7,
    "font.family": "serif", "axes.edgecolor": MUTED, "axes.linewidth": 0.6,
    "xtick.color": MUTED, "ytick.color": MUTED, "text.color": INK,
    "axes.labelcolor": INK, "pdf.fonttype": 42,
})


def load(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


# ---------- Fig 1: dormancy ----------
buckets = ["0-6", "6-18", "18-36", "36-60", ">60"]
edges = [0, 6, 18, 36, 60, 10**6]
counts = {"official": Counter(), "community": Counter()}
for r in load("repos_meta.csv"):
    if r.get("not_found") == "True" or not r.get("pushed_at"):
        continue
    months = (SNAPSHOT - datetime.fromisoformat(r["pushed_at"].replace("Z", "+00:00"))).days / 30.44
    stratum = "official" if r["repo"].split("/")[0].lower() in OFFICIAL else "community"
    for i in range(len(buckets)):
        if edges[i] <= months < edges[i + 1]:
            counts[stratum][buckets[i]] += 1
            break

fig, ax = plt.subplots(figsize=(3.5, 2.1))
x = range(len(buckets))
w = 0.38
tot_off = sum(counts["official"].values())
tot_com = sum(counts["community"].values())
off = [100 * counts["official"][b] / tot_off for b in buckets]
com = [100 * counts["community"][b] / tot_com for b in buckets]
b1 = ax.bar([i - w / 2 for i in x], off, w, color=BLUE, label=f"official (n={tot_off})")
b2 = ax.bar([i + w / 2 for i in x], com, w, color=AQUA, hatch="///",
            edgecolor="white", linewidth=0.3, label=f"community (n={tot_com})")
for bars in (b1, b2):
    for rect in bars:
        ax.annotate(f"{rect.get_height():.0f}", (rect.get_x() + rect.get_width() / 2,
                    rect.get_height()), ha="center", va="bottom", fontsize=6.5, color=MUTED)
ax.set_xticks(list(x), buckets)
ax.set_xlabel("Months since last push (snapshot 2026-07-13)")
ax.set_ylabel("Share of repositories (%)")
ax.spines[["top", "right"]].set_visible(False)
ax.yaxis.grid(True, linewidth=0.3, color="#d9d8d3")
ax.set_axisbelow(True)
ax.legend(frameon=False, loc="upper center")
fig.tight_layout()
fig.savefig("fig_dormancy.pdf")
print("fig_dormancy.pdf")

# ---------- Fig 2: top failed rules ----------
rule_repos = defaultdict(set)
rule_name = {}
for f in ("scan_azurerm.csv", "scan_aws.csv", "scan_google.csv"):
    for r in load(f):
        if r.get("check_id"):
            rule_repos[r["check_id"]].add(r["repo"])
            rule_name[r["check_id"]] = r.get("check_name", "")

SHORT = {
    "CKV_TF_1": "Module refs not commit-pinned",
    "CKV_GCP_114": "GCS public-access prevention off",
    "CKV_GCP_62": "Bucket access logging off",
    "CKV_GCP_78": "Storage versioning off",
    "CKV_AWS_356": "IAM policy wildcard resource",
    "CKV_GCP_32": "Project-wide SSH keys allowed",
    "CKV_AWS_111": "IAM write access unconstrained",
    "CKV2_AWS_5": "Security group unattached",
    "CKV_AWS_382": "SG egress open to 0.0.0.0/0",
    "CKV2_AWS_62": "S3 event notifications off",
}
top = sorted(rule_repos.items(), key=lambda kv: -len(kv[1]))[:10]
labels = [f"{SHORT.get(cid, rule_name[cid][:30])}  ({cid})" for cid, _ in top][::-1]
vals = [len(repos) for _, repos in top][::-1]
cols = [MUTED if cid == "CKV_TF_1" else BLUE for cid, _ in top][::-1]

fig, ax = plt.subplots(figsize=(3.5, 2.4))
bars = ax.barh(range(len(vals)), vals, color=cols, height=0.62)
for i, (v, rect) in enumerate(zip(vals, bars)):
    ax.annotate(str(v), (v + 1, rect.get_y() + rect.get_height() / 2),
                va="center", fontsize=6.5, color=MUTED)
ax.set_yticks(range(len(labels)), labels, fontsize=6.5)
ax.set_xlabel("Failing repos (n=300)")
ax.spines[["top", "right"]].set_visible(False)
ax.xaxis.grid(True, linewidth=0.3, color="#d9d8d3")
ax.set_axisbelow(True)
ax.set_xlim(0, max(vals) * 1.15)
fig.tight_layout()
fig.savefig("fig_toprules.pdf")
print("fig_toprules.pdf")
