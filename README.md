# Subnet Watcher

Publishes AWS VPC subnet IP metrics to CloudWatch every 5 minutes for visualization in Grafana.

## What it does

Pushes 4 custom metrics to CloudWatch under the `VPCSubnetMetrics` namespace:

| Metric | Description |
|---|---|
| `AvailableIpAddressCount` | Free IPs in the subnet |
| `TotalIpAddressCount` | Total IPs (CIDR size minus 5 AWS-reserved) |
| `AvailableIpAddressPercent` | % of IPs remaining |
| `AvailableNetworkInterface` | Detached (unused) ENIs in the VPC |

## Configuration

Set these in the `Makefile` before deploying:

| Parameter | Description | Default |
|---|---|---|
| `Product` | Product name | `subnet-watcher` |
| `Project` | Your project name | |
| `Environment` | Environment name | |
| `AWSRegion` | Target AWS region | `eu-west-1` |

**Optional:** Set `VPC_ID` in the CloudFormation template to scope to a single VPC. Set `REGION_ID` to scope to a single region. If neither is set, all regions and VPCs are scanned.

## Deploy

```bash
make deploy
```

## Grafana

Import `grafana/dashboard.json` into Grafana (Dashboards → Import) and select your CloudWatch datasource and region.
