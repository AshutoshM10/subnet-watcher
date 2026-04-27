# Subnet Watcher

Monitors free IP addresses in AWS VPC subnets and alerts when they're running low.

## What it does

- Pushes 4 custom metrics to CloudWatch under the `VPCSubnetMetrics` namespace:
  - `AvailableIpAddressCount` — free IPs in the subnet
  - `TotalIpAddressCount` — total IPs (CIDR size minus 5 AWS-reserved)
  - `AvailableIpAddressPercent` — % of IPs remaining
  - `AvailableNetworkInterface` — detached ENIs in the VPC
- Sends an SNS alert when any subnet drops below your warning threshold

## Configuration

Set these in the `Makefile` before deploying:

| Parameter | Description | Default |
|---|---|---|
| `Product` | Name of the product | `subnet-watcher` |
| `Project` | Your project name | |
| `Environment` | Environment name | |
| `AWSRegion` | Target AWS region | `eu-west-1` |
| `AlertsRecipient` | SNS alert recipient email | |
| `PercentageRemainingWarning` | Alert threshold (% IPs left) | `20` |

**Optional:** Set `VPC_ID` as an env var in the CloudFormation template to scope checks to a single VPC. Set `REGION_ID` to scope to a single region. If neither is set, all regions and VPCs are scanned.

## Deploy

```bash
make deploy
```
