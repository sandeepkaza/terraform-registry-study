# Paper 4 — RQ2 results (checkov 3.3.8, module source excl. examples/tests, snapshot 2026-07-13)

## azurerm
- Repos scanned: 100 (no terraform checks applicable: 40)
- Repos with ≥1 failed check: 49 (81.7% of scannable)
- Median failed checks per repo: 1.0
- Median passed checks per repo: 2.5

## aws
- Repos scanned: 100 (no terraform checks applicable: 7)
- Repos with ≥1 failed check: 87 (93.5% of scannable)
- Median failed checks per repo: 3
- Median passed checks per repo: 15

## google
- Repos scanned: 100 (no terraform checks applicable: 22)
- Repos with ≥1 failed check: 66 (84.6% of scannable)
- Median failed checks per repo: 3.0
- Median passed checks per repo: 11.5

## Top 15 failed rules (by distinct repos, all providers)

| Rule | Repos failing | Description |
|---|---|---|
| CKV_TF_1 | 114 | Ensure Terraform module sources use a commit hash |
| CKV_GCP_114 | 16 | Ensure public access prevention is enforced on Cloud Storage bucket |
| CKV_GCP_62 | 15 | Bucket should log access |
| CKV_GCP_78 | 15 | Ensure Cloud storage has versioning enabled |
| CKV_AWS_356 | 14 | Ensure no IAM policies documents allow "*" as a statement's resource for restric |
| CKV_GCP_32 | 12 | Ensure 'Block Project-wide SSH keys' is enabled for VM instances |
| CKV_AWS_111 | 11 | Ensure IAM policies does not allow write access without constraints |
| CKV2_AWS_5 | 11 | Ensure that Security Groups are attached to another resource |
| CKV_AWS_382 | 11 | Ensure no security groups allow egress from 0.0.0.0:0 to port -1 |
| CKV2_AWS_62 | 11 | Ensure S3 buckets should have event notifications enabled |
| CKV_AWS_144 | 10 | Ensure that S3 bucket has cross-region replication enabled |
| CKV_GCP_49 | 10 | Ensure roles do not impersonate or manage Service Accounts used at project level |
| CKV_GCP_40 | 10 | Ensure that Compute instances do not have public IP addresses |
| CKV_GCP_39 | 10 | Ensure Compute instances are launched with Shielded VM enabled |
| CKV_AWS_21 | 9 | Ensure all data stored in the S3 bucket have versioning enabled |

## Official vs community (repos with ≥1 failed check)
- community: 115/150 (76.7%)
- official: 87/150 (58.0%)
