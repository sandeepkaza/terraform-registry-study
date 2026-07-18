# Terraform Registry Module Study — Dataset & Pipeline

Companion repository for the paper *"Terraform Module Ecosystems at
Enterprise Scale: An Empirical Study of Public Registry Modules"*
(Venkata Sandeep Chowdary Kaza, 2026).
Preprint: [doi:10.5281/zenodo.21347268](https://doi.org/10.5281/zenodo.21347268).

Empirical study of the top 500 Terraform Registry modules by downloads for
each of the `aws`, `azurerm`, and `google` providers — 1,500 listings,
1,493 unique repositories, 21,732 release tags, 300 security-scanned module
sources. **Snapshot date: 2026-07-13** (recorded in every artifact).

## Headline findings (2026-07-13 snapshot)

- 251 vendor-governed ("official") modules = 16.7% of listings but
  **87.0% of downloads**
- **67.8%** of top-500 repos had no push in >18 months; **12.1%** archived;
  **28.4%** single-contributor; **2.9%** of source repos no longer exist
- **88.3%** semver-adherent in *form* — but **13.3% of sampled minor bumps
  silently removed root input variables** (breaking changes under a
  compatibility-signaling version)
- **87.4%** of scannable top-100 modules fail ≥1 checkov rule on their
  defaults (official namespaces: 58.0%)

## Dataset

| File | Contents |
|---|---|
| `data/modules_{aws,azurerm,google}.csv` | Top-500 module listings per provider (registry API): namespace, name, downloads, verified flag, source URL, latest version |
| `data/repos_meta.csv` | GitHub metadata for the unique source repos: stars, forks, archived, created/pushed timestamps, contributor count, license |
| `data/repo_tags.csv` | 21,732 release tags across all repos (RQ1 raw material) |
| `data/scan_{aws,azurerm,google}.csv` | checkov v3.3.8 scan results, top-100 modules per provider, default branch, excluding `examples/`/`tests/` |
| `results.md`, `results_rq2.md`, `results_vardiff.md` | Aggregated findings behind every table in the paper |

## Reproducing — two paths

### Path A: verify the paper's numbers from the committed snapshot (~5 min)

No API access or tokens needed — the analysis stages read only the committed
CSVs:

```bash
pip install requests

# RQ1 (versioning) + RQ3 (maintenance health) aggregates:
python analyze.py --modules data/modules_*.csv --meta data/repos_meta.csv --tags data/repo_tags.csv

# RQ2 (security defaults) aggregates + top-rules table:
python rq2_analyze.py
```

Checkpoint: the printed aggregates match `results.md` / `results_rq2.md`
line for line (semver 88.3%, archived 12.1%, dormant 67.8%, official
download share 87.0%, scan-failure 87.4%, ...).

The versioning cross-check (variables.tf diff across sampled version bumps)
is seeded by the snapshot date, so it reproduces the exact sample:

```bash
python variables_diff.py --tags data/repo_tags.csv --meta data/repos_meta.csv \
  --major-sample 40 --minor-sample 80 --out results_vardiff.md
```

Note: this step fetches the sampled tag pairs from GitHub (shallow), so it
needs network + a token (step B2 below) and ~15 min; its per-pair outcomes
should match the committed `results_vardiff.md` (12/36 major and 10/75 minor
pairs with removed root variables).

### Path B: fresh end-to-end snapshot (~3–6 h, mostly unattended)

Re-running collection produces a **new** snapshot — expect numbers to drift
from the paper's; that drift is the longitudinal follow-up the paper invites.

**B0. Prerequisites**

```bash
pip install requests checkov==3.3.8
```

git on PATH; ~5 GB free disk for shallow clones.

**B1. Registry crawl (no auth, ~10 min)**

```bash
python collect.py --provider azurerm --top 500 --out data/modules_azurerm.csv
python collect.py --provider aws     --top 500 --out data/modules_aws.csv
python collect.py --provider google  --top 500 --out data/modules_google.csv
```

Checkpoint: each CSV has 500 rows + header; downloads column strictly
decreasing after the client-side sort.

**B2. GitHub metadata + tags (~30–60 min, rate-limit aware, resumable)**

Needs an authenticated token — either `export GITHUB_TOKEN=...` (classic,
`public_repo` scope is enough) or an active `gh auth login` session:

```bash
python github_meta.py --in data/modules_*.csv --out data/repos_meta.csv --tags-out data/repo_tags.csv
```

Checkpoint: `repos_meta.csv` row count ≈ unique source repos; a small
percentage of 404s is *expected* (vanished sources are a paper finding, not
an error). Re-running resumes rather than restarting.

**B3. Security-default scans (~1–3 h; clones top-100 per provider; resumable)**

```bash
python clone_and_scan.py --modules data/modules_azurerm.csv --top 100 --out data/scan_azurerm.csv
python clone_and_scan.py --modules data/modules_aws.csv     --top 100 --out data/scan_aws.csv
python clone_and_scan.py --modules data/modules_google.csv  --top 100 --out data/scan_google.csv
```

Keep checkov pinned at 3.3.8 for comparability — its rule set grows over
time, and a newer scanner conflates rule-set growth with ecosystem change
(discussed in the paper's threats section).

**B4. Analysis** — same commands as Path A, now against your fresh CSVs.

## Interpreting / extending

- Every number in the paper maps to one analyzer output; grep `results*.md`.
- The seeded sampling in `variables_diff.py` means anyone can audit the
  exact version pairs behind the silent-break rate — or raise
  `--minor-sample` toward the full 7,472-pair population.
- Cross-registry replication (e.g., OpenTofu registry) needs only a new
  `collect.py` endpoint; everything downstream is registry-agnostic.

## Citing

Use GitHub's **"Cite this repository"** button (backed by
[`CITATION.cff`](CITATION.cff)) or cite the preprint DOI above.
License: code MIT; data derived from public Terraform Registry and GitHub
APIs, provided for research reproducibility.
