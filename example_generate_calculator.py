#!/usr/bin/env python3
"""
Example: Using Abstract Calculator to Generate Service-Specific Calculators

This script demonstrates how to use the abstract calculator to:
1. Fetch real AWS pricing data
2. Generate calculator code for specific services
3. Create reusable cost calculation tools
"""

from aws_abstract_calculator import (
    AbstractCalculatorGenerator,
    ServicePricing,
    PricingDimension,
    FormulaGenerator
)
import json


def example_1_generate_from_demo_data():
    """
    Example 1: Generate calculator from demo/manual pricing data
    (Works without internet connection)
    """

    print("\n" + "="*80)
    print("EXAMPLE 1: Generate Calculator from Demo Data")
    print("="*80 + "\n")

    # Create sample pricing data manually
    ec2_pricing = ServicePricing(
        service_code="AmazonEC2",
        service_name="Amazon Elastic Compute Cloud",
        region="us-east-1",
        pricing_dimensions={
            "t3.micro": [
                PricingDimension(
                    unit="Hrs",
                    price_per_unit=0.0104,
                    description="$0.0104 per On Demand Linux t3.micro Instance Hour"
                )
            ],
            "t3.small": [
                PricingDimension(
                    unit="Hrs",
                    price_per_unit=0.0208,
                    description="$0.0208 per On Demand Linux t3.small Instance Hour"
                )
            ],
            "m5.large": [
                PricingDimension(
                    unit="Hrs",
                    price_per_unit=0.096,
                    description="$0.096 per On Demand Linux m5.large Instance Hour"
                )
            ],
            "EBS-GP3": [
                PricingDimension(
                    unit="GB-Mo",
                    price_per_unit=0.08,
                    description="$0.08 per GB-month of General Purpose SSD (gp3)"
                )
            ]
        }
    )

    # Generate calculator
    generator = FormulaGenerator(ec2_pricing)
    calculator_code = generator.generate_python_calculator()

    # Save to file
    output_file = "generated_ec2_calculator.py"
    with open(output_file, 'w') as f:
        f.write(calculator_code)
        f.write('\n\n')
        f.write(generator.generate_usage_example())

    print(f"✅ Generated calculator saved to: {output_file}")
    print(f"   Service: {ec2_pricing.service_code}")
    print(f"   Pricing categories: {len(ec2_pricing.pricing_dimensions)}")
    print()


def example_2_live_pricing_fetch():
    """
    Example 2: Fetch live pricing data from AWS (requires internet)
    This example shows how it would work, but will gracefully handle
    offline scenarios
    """

    print("\n" + "="*80)
    print("EXAMPLE 2: Fetch Live Pricing Data (Requires Internet)")
    print("="*80 + "\n")

    generator = AbstractCalculatorGenerator(use_cache=True)

    # Try to fetch real pricing data
    try:
        # This will attempt to fetch from AWS Price List API
        # Falls back to cache if available
        code = generator.generate_calculator(
            service_code='AmazonEC2',
            region='us-east-1',
            output_file='generated_ec2_live.py'
        )

        print("✅ Successfully generated calculator from live pricing data!")
        print(f"   Code length: {len(code)} characters")
        print()

    except Exception as e:
        print(f"⚠️  Could not fetch live data: {e}")
        print("   This is expected if running offline.")
        print("   The abstract calculator can still work with cached or manual data.")
        print()


def example_3_generate_summary_report():
    """
    Example 3: Generate pricing summary report
    """

    print("\n" + "="*80)
    print("EXAMPLE 3: Generate Pricing Summary Report")
    print("="*80 + "\n")

    # Create sample S3 pricing data
    s3_pricing = ServicePricing(
        service_code="AmazonS3",
        service_name="Amazon Simple Storage Service",
        region="us-east-1",
        pricing_dimensions={
            "Standard": [
                PricingDimension(
                    unit="GB-Mo",
                    price_per_unit=0.023,
                    description="First 50 TB / month"
                )
            ],
            "Standard-IA": [
                PricingDimension(
                    unit="GB-Mo",
                    price_per_unit=0.0125,
                    description="Standard - Infrequent Access storage"
                )
            ],
            "Glacier": [
                PricingDimension(
                    unit="GB-Mo",
                    price_per_unit=0.004,
                    description="Glacier Instant Retrieval storage"
                )
            ],
            "PUT-Requests": [
                PricingDimension(
                    unit="Requests",
                    price_per_unit=0.000005,
                    description="PUT, COPY, POST, or LIST requests"
                )
            ],
            "GET-Requests": [
                PricingDimension(
                    unit="Requests",
                    price_per_unit=0.0000004,
                    description="GET and all other requests"
                )
            ]
        }
    )

    summary = {
        'service': s3_pricing.service_code,
        'name': s3_pricing.service_name,
        'region': s3_pricing.region,
        'categories': len(s3_pricing.pricing_dimensions),
        'pricing_overview': {}
    }

    for category, dimensions in s3_pricing.pricing_dimensions.items():
        summary['pricing_overview'][category] = [
            {
                'unit': dim.unit,
                'price': f"${dim.price_per_unit}",
                'description': dim.description
            }
            for dim in dimensions
        ]

    # Print summary
    print("Service Pricing Summary")
    print("-" * 80)
    print(json.dumps(summary, indent=2))
    print()

    # Save summary
    summary_file = "s3_pricing_summary.json"
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)

    print(f"✅ Summary saved to: {summary_file}")
    print()


def example_4_self_updating_calculator():
    """
    Example 4: Demonstrate self-updating capability concept
    """

    print("\n" + "="*80)
    print("EXAMPLE 4: Self-Updating Calculator Concept")
    print("="*80 + "\n")

    print("The abstract calculator can be used to create self-updating calculators:")
    print()
    print("1. Fetch latest pricing from AWS Price List API")
    print("2. Compare with current pricing constants")
    print("3. Auto-generate updated calculator code")
    print("4. Reload or notify about pricing changes")
    print()

    print("Example workflow:")
    print("-" * 80)
    print("""
# In your application
from aws_abstract_calculator import AbstractCalculatorGenerator

def update_pricing():
    generator = AbstractCalculatorGenerator(use_cache=False)

    # Generate fresh calculator
    new_code = generator.generate_calculator('AmazonEC2', 'us-east-1')

    # Save or reload
    with open('calculators/ec2_calculator.py', 'w') as f:
        f.write(new_code)

    print("✓ Pricing updated!")

# Run periodically (e.g., daily cron job)
update_pricing()
    """)
    print("-" * 80)
    print()


def main():
    """Run all examples"""

    print("\n" + "="*80)
    print("AWS ABSTRACT CALCULATOR - USAGE EXAMPLES")
    print("="*80)

    # Run examples
    example_1_generate_from_demo_data()
    example_2_live_pricing_fetch()
    example_3_generate_summary_report()
    example_4_self_updating_calculator()

    print("\n" + "="*80)
    print("✅ ALL EXAMPLES COMPLETED")
    print("="*80)
    print()
    print("Generated files:")
    print("  - generated_ec2_calculator.py")
    print("  - generated_ec2_live.py (if internet available)")
    print("  - s3_pricing_summary.json")
    print()
    print("Next steps:")
    print("  1. Review the generated calculator code")
    print("  2. Customize the calculate() method with your logic")
    print("  3. Use it in your applications")
    print("  4. Set up periodic updates to fetch latest pricing")
    print()


if __name__ == "__main__":
    main()
