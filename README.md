# Terraform Registry Module Study — Dataset & Pipeline

Companion repository for the paper *"Terraform Module Ecosystems at Enterprise Scale: An Empirical Study of Public Registry Modules"* (Venkata Sandeep Chowdary Kaza, 2026 — under submission).

Empirical study of the top 500 Terraform Registry modules by downloads for each of the `aws`, `azurerm`, and `google` providers. **Snapshot date: 2026-07-13** (recorded in every artifact).

## Dataset

| File | Contents |
|---|---|
| `data/modules_{aws,azurerm,google}.csv` | Top-500 module listings per provider (registry API) |
| `data/repos_meta.csv` | GitHub metadata for 1,493 unique source repos (stars, archived, pushed_at, contributor count, ...) |
| `data/repo_tags.csv` | 21,732 release tags across all repos (RQ1 raw material) |
| `data/scan_{aws,azurerm,google}.csv` | checkov 3.3.8 scan results, top-100 modules per provider, default branch, excluding `examples/`/`tests/` |
| `results.md`, `results_rq2.md` | Aggregated findings |

## Pipeline (reproduce from scratch)

```bash
pip install requests checkov==3.3.8

# 1. Registry crawl (no auth)
python collect.py --provider azurerm --top 500 --out data/modules_azurerm.csv
python collect.py --provider aws     --top 500 --out data/modules_aws.csv
python collect.py --provider google  --top 500 --out data/modules_google.csv

# 2. GitHub metadata (needs GITHUB_TOKEN or `gh auth login`; rate-limit aware, resumable)
python github_meta.py --in data/modules_*.csv --out data/repos_meta.csv --tags-out data/repo_tags.csv

# 3. Security-default scans (clones repos; resumable)
python clone_and_scan.py --modules data/modules_azurerm.csv --top 100 --out data/scan_azurerm.csv

# 4. Analysis
python analyze.py --modules data/modules_*.csv --meta data/repos_meta.csv --tags data/repo_tags.csv
python rq2_analyze.py
```

Note: re-running steps 1–3 today produces a *new* snapshot; numbers in the paper correspond to the committed 2026-07-13 CSVs. Step 4 on the committed CSVs reproduces the paper's numbers exactly.

## Headline findings (2026-07-13 snapshot)

- 251 vendor-governed ("official") modules = 16.7% of listings but **87.0% of downloads**
- **67.8%** of top-500 repos had no push in >18 months; **12.1%** archived; **28.4%** single-contributor; **2.9%** of source repos no longer exist
- **88.3%** semver-adherent; only 4.0% average ≥1 major (breaking) release/year
- **87.4%** of scannable top-100 modules fail ≥1 checkov rule on defaults (official namespaces: 58.0%)

## License

Code: MIT. Data: derived from public Terraform Registry and GitHub APIs; provided for research reproducibility.
