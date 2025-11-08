#!/usr/bin/env python3
"""
AWS Compute & Storage Cost Calculator
Estimates costs for EC2, Lambda, and S3 usage scenarios
"""

from dataclasses import dataclass
from typing import Dict, List, Optional
from enum import Enum
import json


class EC2InstanceType(Enum):
    """Common EC2 instance types"""
    T3_MICRO = "t3.micro"
    T3_SMALL = "t3.small"
    T3_MEDIUM = "t3.medium"
    T3_LARGE = "t3.large"
    M5_LARGE = "m5.large"
    M5_XLARGE = "m5.xlarge"
    M5_2XLARGE = "m5.2xlarge"
    C5_LARGE = "c5.large"
    C5_XLARGE = "c5.xlarge"
    R5_LARGE = "r5.large"
    R5_XLARGE = "r5.xlarge"


class S3StorageClass(Enum):
    """S3 storage classes"""
    STANDARD = "Standard"
    INTELLIGENT_TIERING = "Intelligent-Tiering"
    STANDARD_IA = "Standard-IA"
    ONE_ZONE_IA = "One Zone-IA"
    GLACIER_INSTANT = "Glacier Instant Retrieval"
    GLACIER_FLEXIBLE = "Glacier Flexible Retrieval"
    GLACIER_DEEP = "Glacier Deep Archive"


@dataclass
class EC2Usage:
    """Defines EC2 usage scenario"""
    instance_type: EC2InstanceType
    num_instances: int
    hours_per_month: float  # Average hours per month (max 730)
    ebs_storage_gb: float  # EBS storage in GB
    ebs_type: str = "gp3"  # gp3, gp2, io2, etc.
    data_transfer_out_gb: float = 0  # Data transfer out per month


@dataclass
class LambdaUsage:
    """Defines Lambda usage scenario"""
    monthly_invocations: int
    avg_duration_ms: int  # Average execution time in milliseconds
    memory_mb: int  # Allocated memory (128-10240 MB)
    data_transfer_out_gb: float = 0


@dataclass
class S3Usage:
    """Defines S3 usage scenario"""
    storage_gb: float
    storage_class: S3StorageClass
    put_requests_monthly: int = 0
    get_requests_monthly: int = 0
    data_transfer_out_gb: float = 0


@dataclass
class UsageScenario:
    """Complete usage scenario"""
    name: str
    ec2_usage: Optional[List[EC2Usage]] = None
    lambda_usage: Optional[LambdaUsage] = None
    s3_usage: Optional[List[S3Usage]] = None


class AWSPricing:
    """AWS Pricing (US East - N. Virginia, January 2025)"""

    # EC2 On-Demand Pricing (per hour)
    EC2_HOURLY = {
        EC2InstanceType.T3_MICRO: 0.0104,
        EC2InstanceType.T3_SMALL: 0.0208,
        EC2InstanceType.T3_MEDIUM: 0.0416,
        EC2InstanceType.T3_LARGE: 0.0832,
        EC2InstanceType.M5_LARGE: 0.096,
        EC2InstanceType.M5_XLARGE: 0.192,
        EC2InstanceType.M5_2XLARGE: 0.384,
        EC2InstanceType.C5_LARGE: 0.085,
        EC2InstanceType.C5_XLARGE: 0.17,
        EC2InstanceType.R5_LARGE: 0.126,
        EC2InstanceType.R5_XLARGE: 0.252,
    }

    # EBS Pricing (per GB-month)
    EBS_PRICING = {
        "gp3": 0.08,  # General Purpose SSD
        "gp2": 0.10,  # General Purpose SSD (older)
        "io2": 0.125,  # Provisioned IOPS SSD
        "st1": 0.045,  # Throughput Optimized HDD
        "sc1": 0.015,  # Cold HDD
    }

    # Lambda Pricing
    LAMBDA_REQUEST_1M = 0.20  # Per 1M requests
    LAMBDA_GB_SECOND = 0.0000166667  # Per GB-second
    LAMBDA_FREE_REQUESTS = 1_000_000  # Free tier per month
    LAMBDA_FREE_GB_SECONDS = 400_000  # Free tier per month

    # S3 Storage Pricing (per GB-month)
    S3_STORAGE_PRICING = {
        S3StorageClass.STANDARD: 0.023,
        S3StorageClass.INTELLIGENT_TIERING: 0.023,  # + monitoring fee
        S3StorageClass.STANDARD_IA: 0.0125,
        S3StorageClass.ONE_ZONE_IA: 0.01,
        S3StorageClass.GLACIER_INSTANT: 0.004,
        S3StorageClass.GLACIER_FLEXIBLE: 0.0036,
        S3StorageClass.GLACIER_DEEP: 0.00099,
    }

    # S3 Request Pricing
    S3_PUT_1K = 0.005  # Per 1000 PUT requests (Standard)
    S3_GET_1K = 0.0004  # Per 1000 GET requests (Standard)

    # Data Transfer Out (per GB)
    DATA_TRANSFER_OUT_GB = 0.09  # First 10TB/month
    DATA_TRANSFER_FREE_GB = 100  # Free tier per month


class CostCalculator:
    """AWS Cost Calculator"""

    def __init__(self, scenario: UsageScenario):
        self.scenario = scenario
        self.pricing = AWSPricing()

    def calculate_ec2_costs(self, ec2_list: List[EC2Usage]) -> Dict:
        """Calculate EC2 costs"""
        if not ec2_list:
            return {"total_monthly": 0, "instances": []}

        instance_costs = []
        total_compute = 0
        total_storage = 0
        total_transfer = 0

        for ec2 in ec2_list:
            # Compute cost
            hourly_rate = self.pricing.EC2_HOURLY[ec2.instance_type]
            compute_cost = hourly_rate * ec2.hours_per_month * ec2.num_instances

            # EBS storage cost
            storage_rate = self.pricing.EBS_PRICING.get(ec2.ebs_type, 0.08)
            storage_cost = storage_rate * ec2.ebs_storage_gb * ec2.num_instances

            # Data transfer cost
            transfer_gb = max(0, ec2.data_transfer_out_gb - self.pricing.DATA_TRANSFER_FREE_GB)
            transfer_cost = transfer_gb * self.pricing.DATA_TRANSFER_OUT_GB

            instance_total = compute_cost + storage_cost + transfer_cost

            instance_costs.append({
                "instance_type": ec2.instance_type.value,
                "num_instances": ec2.num_instances,
                "hours_per_month": ec2.hours_per_month,
                "compute_cost": compute_cost,
                "storage_cost": storage_cost,
                "transfer_cost": transfer_cost,
                "total": instance_total
            })

            total_compute += compute_cost
            total_storage += storage_cost
            total_transfer += transfer_cost

        return {
            "total_monthly": total_compute + total_storage + total_transfer,
            "compute_cost": total_compute,
            "storage_cost": total_storage,
            "transfer_cost": total_transfer,
            "instances": instance_costs
        }

    def calculate_lambda_costs(self, lambda_usage: Optional[LambdaUsage]) -> Dict:
        """Calculate Lambda costs"""
        if not lambda_usage:
            return {"total_monthly": 0}

        # Request costs
        billable_requests = max(0, lambda_usage.monthly_invocations - self.pricing.LAMBDA_FREE_REQUESTS)
        request_cost = (billable_requests / 1_000_000) * self.pricing.LAMBDA_REQUEST_1M

        # Compute costs (GB-seconds)
        memory_gb = lambda_usage.memory_mb / 1024
        duration_seconds = lambda_usage.avg_duration_ms / 1000
        total_gb_seconds = lambda_usage.monthly_invocations * memory_gb * duration_seconds

        billable_gb_seconds = max(0, total_gb_seconds - self.pricing.LAMBDA_FREE_GB_SECONDS)
        compute_cost = billable_gb_seconds * self.pricing.LAMBDA_GB_SECOND

        # Data transfer
        transfer_gb = max(0, lambda_usage.data_transfer_out_gb - self.pricing.DATA_TRANSFER_FREE_GB)
        transfer_cost = transfer_gb * self.pricing.DATA_TRANSFER_OUT_GB

        return {
            "total_monthly": request_cost + compute_cost + transfer_cost,
            "request_cost": request_cost,
            "compute_cost": compute_cost,
            "transfer_cost": transfer_cost,
            "monthly_invocations": lambda_usage.monthly_invocations,
            "total_gb_seconds": total_gb_seconds,
            "memory_mb": lambda_usage.memory_mb,
            "avg_duration_ms": lambda_usage.avg_duration_ms
        }

    def calculate_s3_costs(self, s3_list: Optional[List[S3Usage]]) -> Dict:
        """Calculate S3 costs"""
        if not s3_list:
            return {"total_monthly": 0, "buckets": []}

        bucket_costs = []
        total_storage = 0
        total_requests = 0
        total_transfer = 0

        for s3 in s3_list:
            # Storage cost
            storage_rate = self.pricing.S3_STORAGE_PRICING[s3.storage_class]
            storage_cost = s3.storage_gb * storage_rate

            # Request costs
            put_cost = (s3.put_requests_monthly / 1000) * self.pricing.S3_PUT_1K
            get_cost = (s3.get_requests_monthly / 1000) * self.pricing.S3_GET_1K
            request_cost = put_cost + get_cost

            # Data transfer cost
            transfer_gb = max(0, s3.data_transfer_out_gb - self.pricing.DATA_TRANSFER_FREE_GB)
            transfer_cost = transfer_gb * self.pricing.DATA_TRANSFER_OUT_GB

            bucket_total = storage_cost + request_cost + transfer_cost

            bucket_costs.append({
                "storage_class": s3.storage_class.value,
                "storage_gb": s3.storage_gb,
                "storage_cost": storage_cost,
                "request_cost": request_cost,
                "transfer_cost": transfer_cost,
                "total": bucket_total
            })

            total_storage += storage_cost
            total_requests += request_cost
            total_transfer += transfer_cost

        return {
            "total_monthly": total_storage + total_requests + total_transfer,
            "storage_cost": total_storage,
            "request_cost": total_requests,
            "transfer_cost": total_transfer,
            "buckets": bucket_costs
        }

    def calculate_total_costs(self) -> Dict:
        """Calculate total costs across all services"""
        ec2_costs = self.calculate_ec2_costs(self.scenario.ec2_usage or [])
        lambda_costs = self.calculate_lambda_costs(self.scenario.lambda_usage)
        s3_costs = self.calculate_s3_costs(self.scenario.s3_usage or [])

        monthly_total = (
            ec2_costs["total_monthly"] +
            lambda_costs["total_monthly"] +
            s3_costs["total_monthly"]
        )

        return {
            "scenario": self.scenario.name,
            "monthly_total": monthly_total,
            "yearly_total": monthly_total * 12,
            "breakdown": {
                "ec2": ec2_costs,
                "lambda": lambda_costs,
                "s3": s3_costs
            }
        }


def format_currency(value: float) -> str:
    """Format value as USD"""
    return f"${value:,.2f}"


def print_cost_report(results: Dict):
    """Print formatted cost report"""
    print(f"\n{'='*80}")
    print(f"AWS COST ESTIMATE - {results['scenario']}")
    print(f"{'='*80}\n")

    print("💰 MONTHLY COSTS")
    print(f"   Total: {format_currency(results['monthly_total'])}/month")
    print(f"   Annual: {format_currency(results['yearly_total'])}/year\n")

    # EC2 Breakdown
    ec2 = results['breakdown']['ec2']
    if ec2['total_monthly'] > 0:
        print(f"   EC2: {format_currency(ec2['total_monthly'])}/month")
        print(f"   - Compute:          {format_currency(ec2['compute_cost'])}")
        print(f"   - EBS Storage:      {format_currency(ec2['storage_cost'])}")
        print(f"   - Data Transfer:    {format_currency(ec2['transfer_cost'])}")

        if ec2['instances']:
            print(f"\n   EC2 Instances:")
            for inst in ec2['instances']:
                print(f"   - {inst['num_instances']}x {inst['instance_type']}: "
                      f"{format_currency(inst['total'])}/month "
                      f"({inst['hours_per_month']:.0f}h)")

    # Lambda Breakdown
    lmb = results['breakdown']['lambda']
    if lmb['total_monthly'] > 0:
        print(f"\n   Lambda: {format_currency(lmb['total_monthly'])}/month")
        print(f"   - Requests:         {format_currency(lmb['request_cost'])}")
        print(f"   - Compute:          {format_currency(lmb['compute_cost'])}")
        print(f"   - Data Transfer:    {format_currency(lmb['transfer_cost'])}")
        print(f"   - Invocations:      {lmb['monthly_invocations']:,}/month")
        print(f"   - Memory:           {lmb['memory_mb']}MB")
        print(f"   - Avg Duration:     {lmb['avg_duration_ms']}ms")

    # S3 Breakdown
    s3 = results['breakdown']['s3']
    if s3['total_monthly'] > 0:
        print(f"\n   S3: {format_currency(s3['total_monthly'])}/month")
        print(f"   - Storage:          {format_currency(s3['storage_cost'])}")
        print(f"   - Requests:         {format_currency(s3['request_cost'])}")
        print(f"   - Data Transfer:    {format_currency(s3['transfer_cost'])}")

        if s3['buckets']:
            print(f"\n   S3 Buckets:")
            for bucket in s3['buckets']:
                print(f"   - {bucket['storage_class']}: "
                      f"{bucket['storage_gb']:.1f}GB = {format_currency(bucket['total'])}/month")

    print(f"\n{'='*80}\n")


def main():
    """Run calculations for different scenarios"""

    scenarios = [
        UsageScenario(
            name="SCENARIO 1: Small Startup - Web Application",
            ec2_usage=[
                EC2Usage(
                    instance_type=EC2InstanceType.T3_MEDIUM,
                    num_instances=2,
                    hours_per_month=730,  # 24/7
                    ebs_storage_gb=50,
                    ebs_type="gp3",
                    data_transfer_out_gb=500
                )
            ],
            lambda_usage=LambdaUsage(
                monthly_invocations=2_000_000,
                avg_duration_ms=200,
                memory_mb=512,
                data_transfer_out_gb=50
            ),
            s3_usage=[
                S3Usage(
                    storage_gb=1000,
                    storage_class=S3StorageClass.STANDARD,
                    put_requests_monthly=100_000,
                    get_requests_monthly=5_000_000,
                    data_transfer_out_gb=800
                )
            ]
        ),

        UsageScenario(
            name="SCENARIO 2: Medium Business - API Backend",
            ec2_usage=[
                EC2Usage(
                    instance_type=EC2InstanceType.M5_XLARGE,
                    num_instances=4,
                    hours_per_month=730,
                    ebs_storage_gb=200,
                    ebs_type="gp3",
                    data_transfer_out_gb=2000
                ),
                EC2Usage(
                    instance_type=EC2InstanceType.R5_LARGE,
                    num_instances=2,
                    hours_per_month=730,
                    ebs_storage_gb=100,
                    ebs_type="gp3",
                    data_transfer_out_gb=500
                )
            ],
            lambda_usage=LambdaUsage(
                monthly_invocations=10_000_000,
                avg_duration_ms=300,
                memory_mb=1024,
                data_transfer_out_gb=200
            ),
            s3_usage=[
                S3Usage(
                    storage_gb=5000,
                    storage_class=S3StorageClass.STANDARD,
                    put_requests_monthly=500_000,
                    get_requests_monthly=20_000_000,
                    data_transfer_out_gb=3000
                ),
                S3Usage(
                    storage_gb=10000,
                    storage_class=S3StorageClass.STANDARD_IA,
                    put_requests_monthly=50_000,
                    get_requests_monthly=1_000_000,
                    data_transfer_out_gb=500
                )
            ]
        ),

        UsageScenario(
            name="SCENARIO 3: Serverless-First Architecture",
            lambda_usage=LambdaUsage(
                monthly_invocations=50_000_000,
                avg_duration_ms=150,
                memory_mb=512,
                data_transfer_out_gb=1000
            ),
            s3_usage=[
                S3Usage(
                    storage_gb=10000,
                    storage_class=S3StorageClass.STANDARD,
                    put_requests_monthly=1_000_000,
                    get_requests_monthly=50_000_000,
                    data_transfer_out_gb=5000
                ),
                S3Usage(
                    storage_gb=50000,
                    storage_class=S3StorageClass.GLACIER_FLEXIBLE,
                    put_requests_monthly=10_000,
                    get_requests_monthly=50_000,
                    data_transfer_out_gb=100
                )
            ]
        ),

        UsageScenario(
            name="SCENARIO 4: Enterprise - High Performance Computing",
            ec2_usage=[
                EC2Usage(
                    instance_type=EC2InstanceType.C5_XLARGE,
                    num_instances=10,
                    hours_per_month=730,
                    ebs_storage_gb=500,
                    ebs_type="io2",
                    data_transfer_out_gb=5000
                ),
                EC2Usage(
                    instance_type=EC2InstanceType.M5_2XLARGE,
                    num_instances=5,
                    hours_per_month=730,
                    ebs_storage_gb=1000,
                    ebs_type="gp3",
                    data_transfer_out_gb=2000
                )
            ],
            lambda_usage=LambdaUsage(
                monthly_invocations=100_000_000,
                avg_duration_ms=500,
                memory_mb=2048,
                data_transfer_out_gb=3000
            ),
            s3_usage=[
                S3Usage(
                    storage_gb=100000,
                    storage_class=S3StorageClass.STANDARD,
                    put_requests_monthly=5_000_000,
                    get_requests_monthly=100_000_000,
                    data_transfer_out_gb=20000
                ),
                S3Usage(
                    storage_gb=500000,
                    storage_class=S3StorageClass.INTELLIGENT_TIERING,
                    put_requests_monthly=500_000,
                    get_requests_monthly=10_000_000,
                    data_transfer_out_gb=5000
                )
            ]
        )
    ]

    all_results = []

    for scenario in scenarios:
        calculator = CostCalculator(scenario)
        results = calculator.calculate_total_costs()
        all_results.append(results)
        print_cost_report(results)

    # Quick Comparison
    print(f"\n{'='*80}")
    print("📊 QUICK COMPARISON")
    print(f"{'='*80}\n")
    print(f"{'Scenario':<50} {'Monthly':<15} {'Annual'}")
    print(f"{'-'*80}")

    for r in all_results:
        name = r['scenario'].split(':')[1].strip()[:45]
        print(f"{name:<50} {format_currency(r['monthly_total']):<15} {format_currency(r['yearly_total'])}")

    print(f"\n{'='*80}\n")

    # Save JSON
    with open('aws_compute_storage_costs.json', 'w') as f:
        json.dump(all_results, f, indent=2, default=str)

    print("✅ Detailed results saved to: aws_compute_storage_costs.json\n")


if __name__ == "__main__":
    main()
