# RQ1 cross-check — variables.tf diff across version bumps (seed 20260713)

- Population: 1629 adjacent-major pairs, 7472 adjacent-minor pairs across 1399 repos
- Major-bump sample: 40 drawn, 36 comparable (variables.tf at both tags), 4 skipped
- Major bumps with >=1 removed root variable: 12 (33.3%)
- Minor-bump sample: 80 drawn, 75 comparable, 5 skipped
- Minor bumps with >=1 removed root variable (SILENT breaking): 10 (13.3%)

## Major-bump removals detail
- andrewCluey/terraform-azurerm-keyvault 0.6.0 -> 1.0.0: removed allowed_subnet_ids, kv_name, location, private_vault_dns_zone_id, purge_protection_enabled, resource_group_name ...
- amancevice/terraform-aws-slackbot-slash-command 1.1.2 -> 2.0.0: removed role_arn, role_path, slack_signing_version, slackbot_token
- terraform-aws-modules/terraform-aws-autoscaling v6.10.0 -> v7.0.0: removed launch_template
- terraform-aws-modules/terraform-aws-rds v5.9.0 -> v6.0.0: removed create_random_password, random_password_length
- cloudposse/terraform-aws-vpc 1.2.0 -> 2.0.0: removed classiclink_dns_support_enabled, classiclink_enabled
- rhythmictech/terraform-azurerm-postgresql v1.2.0 -> v2.0.0: removed geo_redundant_backup, ssl_enforcement
- Azure/terraform-azurerm-network-security-group 2.0.0 -> 3.0.0: removed location
- claranet/terraform-azurerm-signalr v4.2.0 -> v5.0.0: removed custom_name, name_prefix
- devops-workflow/terraform-aws-autoscaling v2.1.0 -> v3.0.0: removed create_asg, create_lc
- squidfunk/terraform-aws-github-ci 0.5.4 -> 1.0.0: removed codebuild_project, github_reporter
- DanielMabbett/terraform-azurerm-container-registry v0.1.1 -> v1.0.1: removed georeplications
- Azure/terraform-azurerm-vnet v1.2.0 -> 2.0.0: removed location

## Minor-bump removals detail (silent breaks)
- snowplow-devops/terraform-google-enrich-pubsub-ce v0.3.1 -> v0.4.0: removed ubuntu_20_04_source_image
- claranet/terraform-azurerm-front-door v4.3.0 -> v4.4.0: removed enable_default_backend_pools_parameters, enable_default_frontend_endpoint, enable_default_routing_rule, enforce_backend_pools_certificate_name_check
- avinor/terraform-azurerm-virtual-network-hub v1.4.1 -> v1.5.0: removed log_analytics_workspace_id
- cloudposse/terraform-aws-key-pair 0.15.0 -> 0.16.0: removed attributes, delimiter, environment, name, namespace, stage ...
- damacus/terraform-aws-s3-logs-bucket v0.1.0 -> v0.2.0: removed expiration
- claranet/terraform-azurerm-vm-logs v2.0.1 -> v2.1.0: removed location_short, resource_group_name, vm_extension_custom_name, vm_id, vm_name
- cloudposse/terraform-aws-ssm-parameter-store 0.7.1 -> 0.8.0: removed split_delimiter
- andrewCluey/terraform-azurerm-storage-account 1.4.0 -> 1.5.0: removed private_dns_zone_id, private_dns_zone_name, provider_alias
- gruntwork-io/terraform-google-gke v0.4.3 -> v0.5.0: removed client_tls_subject, force_undeploy, private_key_algorithm, private_key_ecdsa_curve, private_key_rsa_bits, tls_subject ...
- viceIII/terraform-aws-static-site v0.0.9 -> v0.1.0: removed enable_cloudfront
