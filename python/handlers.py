from __future__ import print_function
import boto3
from botocore.exceptions import ClientError
import logging
import os
import ipaddress

root = logging.getLogger()
if root.handlers:
    for handler in root.handlers:
        root.removeHandler(handler)
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO
)


def publish_subnet_metrics(subnets, vpc, region):
    for subnet in subnets:
        available_ips = subnet.available_ip_address_count
        total_ips = ipaddress.ip_network(subnet.cidr_block).num_addresses - 5
        percent_remaining = round(available_ips / total_ips, 2) * 100
        logging.info(
            "%s in %s (%s): %s%% remaining (%s/%s IPs)",
            subnet.id, vpc, region, percent_remaining, available_ips, total_ips,
        )
        put_cw_metrics(subnet.id, vpc, available_ips, total_ips, percent_remaining)


def count_available_enis(region):
    ec2 = boto3.client("ec2", region_name=region)
    response = ec2.describe_network_interfaces(
        Filters=[{"Name": "status", "Values": ["available"]}]
    )
    return len(response["NetworkInterfaces"])


def put_cw_metrics(subnet, vpc, available_ips, total_ips, percent_remaining):
    cloudwatch = boto3.client("cloudwatch")
    metrics = [
        ("AvailableIpAddressCount", available_ips),
        ("TotalIpAddressCount", total_ips),
        ("AvailableIpAddressPercent", percent_remaining),
    ]
    for metric_name, value in metrics:
        try:
            cloudwatch.put_metric_data(
                Namespace="VPCSubnetMetrics",
                MetricData=[
                    {
                        "MetricName": metric_name,
                        "Dimensions": [
                            {"Name": "VPCId", "Value": vpc},
                            {"Name": "SubnetId", "Value": subnet},
                        ],
                        "Value": value,
                        "Unit": "Count",
                    }
                ],
            )
        except ClientError as err:
            logging.error("[%s] CloudWatch PutMetricData failed: %s", metric_name, err)


def put_eni_metric(vpc, eni_count):
    cloudwatch = boto3.client("cloudwatch")
    try:
        cloudwatch.put_metric_data(
            Namespace="VPCSubnetMetrics",
            MetricData=[
                {
                    "MetricName": "AvailableNetworkInterface",
                    "Dimensions": [{"Name": "VPCId", "Value": vpc}],
                    "Value": eni_count,
                    "Unit": "Count",
                }
            ],
        )
    except ClientError as err:
        logging.error("[AvailableNetworkInterface] CloudWatch PutMetricData failed: %s", err)


def process_vpc(vpc_id, vpc_resource, region):
    vpc_object = vpc_resource.Vpc(vpc_id)
    publish_subnet_metrics(list(vpc_object.subnets.all()), vpc_id, region)
    put_eni_metric(vpc_id, count_available_enis(region))


def main(event, context):
    if ("REGION_ID" not in os.environ or os.environ["REGION_ID"] == "") and (
        "VPC_ID" not in os.environ or os.environ["VPC_ID"] == ""
    ):
        regions = boto3.client("ec2").describe_regions()["Regions"]
        for region in regions:
            region_name = region["RegionName"]
            vpc_client = boto3.client("ec2", region_name=region_name)
            vpc_resource = boto3.resource("ec2", region_name=region_name)
            for vpc in vpc_client.describe_vpcs()["Vpcs"]:
                process_vpc(vpc["VpcId"], vpc_resource, region_name)
    else:
        if "REGION_ID" not in os.environ or os.environ["REGION_ID"] == "":
            region_id = boto3.session.Session().region_name
            logging.info("REGION_ID not set, defaulting to %s", region_id)
        else:
            region_id = os.environ["REGION_ID"]

        vpc_resource = boto3.resource("ec2", region_name=region_id)

        if "VPC_ID" not in os.environ or os.environ["VPC_ID"] == "":
            vpc_client = boto3.client("ec2", region_name=region_id)
            for vpc in vpc_client.describe_vpcs()["Vpcs"]:
                process_vpc(vpc["VpcId"], vpc_resource, region_id)
        else:
            process_vpc(os.environ["VPC_ID"], vpc_resource, region_id)


if __name__ == "__main__":
    main(0, 0)
