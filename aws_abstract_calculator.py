#!/usr/bin/env python3
"""
AWS Abstract Cost Calculator
Dynamically fetches AWS pricing data and generates cost calculation formulas
"""

import json
import urllib.request
import urllib.error
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
import re


@dataclass
class PricingDimension:
    """Represents a pricing dimension from AWS"""
    unit: str
    price_per_unit: float
    description: str
    begin_range: Optional[str] = None
    end_range: Optional[str] = None


@dataclass
class ServicePricing:
    """Represents pricing for an AWS service"""
    service_code: str
    service_name: str
    region: str
    pricing_dimensions: Dict[str, List[PricingDimension]] = field(default_factory=dict)
    attributes: Dict[str, Any] = field(default_factory=dict)
    last_updated: str = field(default_factory=lambda: datetime.now().isoformat())


class AWSPricingFetcher:
    """Fetches pricing data from AWS Price List API"""

    BASE_URL = "https://pricing.us-east-1.amazonaws.com"
    CACHE_DIR = Path(".aws_pricing_cache")

    def __init__(self, use_cache: bool = True):
        self.use_cache = use_cache
        if use_cache:
            self.CACHE_DIR.mkdir(exist_ok=True)

    def _fetch_json(self, url: str) -> Dict:
        """Fetch JSON from URL with error handling"""
        try:
            with urllib.request.urlopen(url, timeout=30) as response:
                return json.loads(response.read().decode('utf-8'))
        except urllib.error.URLError as e:
            raise Exception(f"Failed to fetch from {url}: {e}")
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse JSON from {url}: {e}")

    def _get_cache_path(self, service_code: str) -> Path:
        """Get cache file path for a service"""
        return self.CACHE_DIR / f"{service_code}_pricing.json"

    def _load_from_cache(self, service_code: str) -> Optional[Dict]:
        """Load pricing data from cache"""
        cache_path = self._get_cache_path(service_code)
        if cache_path.exists():
            try:
                with open(cache_path, 'r') as f:
                    data = json.load(f)
                    # Check if cache is less than 24 hours old
                    cached_time = datetime.fromisoformat(data.get('cached_at', ''))
                    age_hours = (datetime.now() - cached_time).total_seconds() / 3600
                    if age_hours < 24:
                        return data
            except Exception:
                pass
        return None

    def _save_to_cache(self, service_code: str, data: Dict):
        """Save pricing data to cache"""
        cache_path = self._get_cache_path(service_code)
        data['cached_at'] = datetime.now().isoformat()
        with open(cache_path, 'w') as f:
            json.dump(data, f, indent=2)

    def get_service_list(self) -> Dict[str, str]:
        """Get list of available AWS services"""
        url = f"{self.BASE_URL}/offers/v1.0/aws/index.json"
        try:
            data = self._fetch_json(url)
            return {
                code: details['offerCode']
                for code, details in data.get('offers', {}).items()
            }
        except Exception as e:
            print(f"Warning: Could not fetch service list: {e}")
            # Return common services as fallback
            return {
                'AmazonEC2': 'AmazonEC2',
                'AWSLambda': 'AWSLambda',
                'AmazonS3': 'AmazonS3',
                'AmazonDynamoDB': 'AmazonDynamoDB',
                'AmazonRDS': 'AmazonRDS'
            }

    def fetch_service_pricing(self, service_code: str, region: str = "us-east-1") -> ServicePricing:
        """Fetch pricing data for a specific service"""

        # Try cache first
        if self.use_cache:
            cached_data = self._load_from_cache(service_code)
            if cached_data:
                return self._parse_cached_pricing(cached_data, region)

        # Fetch from API
        url = f"{self.BASE_URL}/offers/v1.0/aws/{service_code}/current/index.json"

        try:
            print(f"Fetching pricing data for {service_code}...")
            data = self._fetch_json(url)

            # Save to cache
            if self.use_cache:
                self._save_to_cache(service_code, data)

            return self._parse_pricing_data(data, service_code, region)

        except Exception as e:
            raise Exception(f"Failed to fetch pricing for {service_code}: {e}")

    def _parse_pricing_data(self, data: Dict, service_code: str, region: str) -> ServicePricing:
        """Parse AWS pricing JSON into ServicePricing object"""

        products = data.get('products', {})
        terms = data.get('terms', {})

        service_pricing = ServicePricing(
            service_code=service_code,
            service_name=data.get('formatVersion', service_code),
            region=region
        )

        # Parse on-demand pricing
        on_demand = terms.get('OnDemand', {})

        for product_sku, product_data in products.items():
            attributes = product_data.get('attributes', {})
            product_region = attributes.get('location', '').lower()

            # Filter by region (AWS uses location names, not codes)
            region_mapping = {
                'us-east-1': 'us east (n. virginia)',
                'us-west-2': 'us west (oregon)',
                'eu-west-1': 'eu (ireland)',
            }

            target_location = region_mapping.get(region, region)
            if target_location not in product_region.lower():
                continue

            # Get pricing dimensions for this product
            if product_sku in on_demand:
                offer_terms = on_demand[product_sku]

                for offer_term_code, offer_term in offer_terms.items():
                    price_dimensions = offer_term.get('priceDimensions', {})

                    for dim_key, dimension in price_dimensions.items():
                        unit = dimension.get('unit', 'Unknown')
                        price_usd = float(dimension.get('pricePerUnit', {}).get('USD', 0))
                        description = dimension.get('description', '')

                        pricing_dim = PricingDimension(
                            unit=unit,
                            price_per_unit=price_usd,
                            description=description,
                            begin_range=dimension.get('beginRange'),
                            end_range=dimension.get('endRange')
                        )

                        # Categorize by instance type or service feature
                        category = self._categorize_product(attributes)

                        if category not in service_pricing.pricing_dimensions:
                            service_pricing.pricing_dimensions[category] = []

                        service_pricing.pricing_dimensions[category].append(pricing_dim)
                        service_pricing.attributes[category] = attributes

        return service_pricing

    def _parse_cached_pricing(self, data: Dict, region: str) -> ServicePricing:
        """Parse cached pricing data"""
        return self._parse_pricing_data(data, data.get('service_code', 'Unknown'), region)

    def _categorize_product(self, attributes: Dict[str, Any]) -> str:
        """Categorize a product based on its attributes"""

        # EC2: use instance type
        if 'instanceType' in attributes:
            return attributes['instanceType']

        # Lambda: categorize by architecture or feature
        if 'group' in attributes and 'lambda' in attributes['group'].lower():
            return attributes.get('groupDescription', 'Lambda-Request')

        # S3: use storage class
        if 'storageClass' in attributes:
            return attributes['storageClass']

        # DynamoDB: use operation type
        if 'group' in attributes and 'dynamodb' in attributes['group'].lower():
            return attributes.get('groupDescription', 'DynamoDB-Operation')

        # Generic: use usagetype or operation
        usage_type = attributes.get('usagetype', '')
        if usage_type:
            return usage_type

        return 'General'


class FormulaGenerator:
    """Generates calculation formulas from pricing data"""

    def __init__(self, service_pricing: ServicePricing):
        self.pricing = service_pricing

    def generate_python_calculator(self) -> str:
        """Generate Python code for a calculator based on pricing data"""

        code_parts = [
            '"""',
            f'Auto-generated calculator for {self.pricing.service_name}',
            f'Generated at: {datetime.now().isoformat()}',
            f'Region: {self.pricing.region}',
            '"""',
            '',
            'from dataclasses import dataclass',
            'from typing import Dict, Optional',
            '',
        ]

        # Generate pricing constants
        code_parts.append('class Pricing:')
        code_parts.append(f'    """Pricing for {self.pricing.service_code}"""')
        code_parts.append('')

        for category, dimensions in self.pricing.pricing_dimensions.items():
            safe_name = self._sanitize_name(category)
            for dim in dimensions[:3]:  # Limit to first 3 dimensions per category
                const_name = f"{safe_name}_{self._sanitize_name(dim.unit)}".upper()
                code_parts.append(f'    {const_name} = {dim.price_per_unit}  # {dim.description[:60]}')

        code_parts.append('')
        code_parts.append('')

        # Generate calculator class
        code_parts.extend(self._generate_calculator_class())

        return '\n'.join(code_parts)

    def _generate_calculator_class(self) -> List[str]:
        """Generate calculator class code"""

        lines = [
            'class CostCalculator:',
            f'    """Cost calculator for {self.pricing.service_code}"""',
            '',
            '    def __init__(self):',
            '        self.pricing = Pricing()',
            '',
            '    def calculate(self, **kwargs) -> Dict[str, float]:',
            '        """',
            '        Calculate costs based on usage parameters',
            '        ',
            '        Parameters depend on service type:',
        ]

        # Add parameter hints based on pricing dimensions
        for category in list(self.pricing.pricing_dimensions.keys())[:5]:
            lines.append(f'        - {category}: usage amount')

        lines.extend([
            '        """',
            '        total_cost = 0.0',
            '        breakdown = {}',
            '',
            '        # Add your calculation logic here',
            '        # Example: total_cost += kwargs.get("hours", 0) * self.pricing.SOME_RATE',
            '',
            '        return {',
            '            "total": total_cost,',
            '            "breakdown": breakdown',
            '        }',
            ''
        ])

        return lines

    def _sanitize_name(self, name: str) -> str:
        """Sanitize a name for use as Python identifier"""
        # Replace invalid characters with underscore
        name = re.sub(r'[^a-zA-Z0-9_]', '_', name)
        # Remove leading/trailing underscores
        name = name.strip('_')
        # Ensure it doesn't start with a number
        if name and name[0].isdigit():
            name = 'n' + name
        return name or 'unknown'

    def generate_usage_example(self) -> str:
        """Generate example usage code"""

        example = [
            '"""',
            'Example usage:',
            '',
            'calculator = CostCalculator()',
            'result = calculator.calculate(',
        ]

        # Add example parameters
        for i, category in enumerate(list(self.pricing.pricing_dimensions.keys())[:3]):
            safe_name = self._sanitize_name(category).lower()
            example.append(f'    {safe_name}=100,  # Example value')

        example.extend([
            ')',
            'print(f"Total cost: ${result[\'total\']:.2f}")',
            '"""',
        ])

        return '\n'.join(example)


class AbstractCalculatorGenerator:
    """Main class for abstract calculator generation"""

    def __init__(self, use_cache: bool = True):
        self.fetcher = AWSPricingFetcher(use_cache=use_cache)

    def list_available_services(self) -> Dict[str, str]:
        """List all available AWS services"""
        return self.fetcher.get_service_list()

    def generate_calculator(
        self,
        service_code: str,
        region: str = "us-east-1",
        output_file: Optional[str] = None
    ) -> str:
        """
        Generate a calculator for a specific AWS service

        Args:
            service_code: AWS service code (e.g., 'AmazonEC2', 'AWSLambda')
            region: AWS region code
            output_file: Optional file path to save generated code

        Returns:
            Generated Python code as string
        """

        print(f"\n{'='*80}")
        print(f"Generating calculator for {service_code} in {region}")
        print(f"{'='*80}\n")

        # Fetch pricing data
        pricing = self.fetcher.fetch_service_pricing(service_code, region)

        print(f"✓ Fetched pricing data")
        print(f"  - Found {len(pricing.pricing_dimensions)} pricing categories")
        print(f"  - Region: {pricing.region}")

        # Generate calculator code
        generator = FormulaGenerator(pricing)
        calculator_code = generator.generate_python_calculator()
        usage_example = generator.generate_usage_example()

        full_code = calculator_code + '\n\n' + usage_example

        print(f"✓ Generated calculator code ({len(full_code)} chars)")

        # Save to file if specified
        if output_file:
            with open(output_file, 'w') as f:
                f.write(full_code)
            print(f"✓ Saved to {output_file}")

        print(f"\n{'='*80}\n")

        return full_code

    def generate_summary_report(self, service_code: str, region: str = "us-east-1") -> Dict:
        """Generate a summary report of pricing information"""

        pricing = self.fetcher.fetch_service_pricing(service_code, region)

        summary = {
            'service': service_code,
            'region': region,
            'categories': len(pricing.pricing_dimensions),
            'pricing_overview': {}
        }

        for category, dimensions in list(pricing.pricing_dimensions.items())[:10]:
            summary['pricing_overview'][category] = [
                {
                    'unit': dim.unit,
                    'price': dim.price_per_unit,
                    'description': dim.description[:80]
                }
                for dim in dimensions[:3]
            ]

        return summary


def main():
    """Demo of abstract calculator generation"""

    print("AWS Abstract Cost Calculator")
    print("=" * 80)
    print()

    generator = AbstractCalculatorGenerator(use_cache=True)

    # Example: Generate calculator for a service
    print("Example: Generating calculator framework...")
    print()
    print("Note: Full pricing data fetch requires internet connection.")
    print("      The system will use cached data when available.")
    print()

    # Demo with manual pricing data (works offline)
    demo_pricing = ServicePricing(
        service_code="DemoService",
        service_name="Demo AWS Service",
        region="us-east-1",
        pricing_dimensions={
            "ComputeHours": [
                PricingDimension(
                    unit="Hrs",
                    price_per_unit=0.096,
                    description="Compute instance per hour"
                )
            ],
            "Storage": [
                PricingDimension(
                    unit="GB-Mo",
                    price_per_unit=0.023,
                    description="Storage per GB per month"
                )
            ],
            "Requests": [
                PricingDimension(
                    unit="Requests",
                    price_per_unit=0.0000002,
                    description="API requests"
                )
            ]
        }
    )

    formula_gen = FormulaGenerator(demo_pricing)
    code = formula_gen.generate_python_calculator()
    example = formula_gen.generate_usage_example()

    print("Generated Calculator Code:")
    print("-" * 80)
    print(code)
    print()
    print("Usage Example:")
    print("-" * 80)
    print(example)
    print()

    print("=" * 80)
    print("✅ Abstract calculator framework ready!")
    print()
    print("To generate a calculator for a real AWS service:")
    print("  generator = AbstractCalculatorGenerator()")
    print("  code = generator.generate_calculator('AmazonEC2', 'us-east-1')")
    print()
    print("Available services: AmazonEC2, AWSLambda, AmazonS3, AmazonDynamoDB, etc.")
    print("=" * 80)


if __name__ == "__main__":
    main()
