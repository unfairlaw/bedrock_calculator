# AWS Abstract Cost Calculator

A meta-calculator that can dynamically fetch AWS pricing data and generate cost calculation code for any AWS service.

## 🎯 Overview

Unlike traditional cost calculators that hardcode pricing for specific services, the **Abstract Calculator** can:

1. **Fetch live pricing** from AWS Price List API
2. **Parse pricing structures** for any AWS service
3. **Generate calculator code** automatically
4. **Self-update** when prices change

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  Abstract Calculator                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌────────────────┐      ┌──────────────────┐              │
│  │ Pricing Fetcher│─────▶│ Pricing Parser   │              │
│  └────────────────┘      └──────────────────┘              │
│         │                         │                          │
│         │                         ▼                          │
│         │                ┌──────────────────┐              │
│         │                │ Formula Generator │              │
│         │                └──────────────────┘              │
│         │                         │                          │
│         ▼                         ▼                          │
│  ┌────────────────┐      ┌──────────────────┐              │
│  │  Local Cache   │      │ Generated Code   │              │
│  └────────────────┘      └──────────────────┘              │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## 📦 Components

### 1. `AWSPricingFetcher`

Fetches pricing data from AWS Price List API with caching support.

```python
from aws_abstract_calculator import AWSPricingFetcher

fetcher = AWSPricingFetcher(use_cache=True)

# List available services
services = fetcher.get_service_list()

# Fetch pricing for specific service
pricing = fetcher.fetch_service_pricing('AmazonEC2', 'us-east-1')
```

**Features:**
- Automatic caching (24-hour TTL)
- Graceful offline fallback
- Region-specific pricing
- Error handling

### 2. `FormulaGenerator`

Generates Python calculator code from pricing data.

```python
from aws_abstract_calculator import FormulaGenerator

generator = FormulaGenerator(pricing)

# Generate calculator class
code = generator.generate_python_calculator()

# Generate usage examples
example = generator.generate_usage_example()
```

**Generated code includes:**
- Pricing constants as class attributes
- Calculator class with `calculate()` method
- Type hints and documentation
- Usage examples

### 3. `AbstractCalculatorGenerator`

High-level interface for end-to-end calculator generation.

```python
from aws_abstract_calculator import AbstractCalculatorGenerator

generator = AbstractCalculatorGenerator(use_cache=True)

# Generate calculator for any AWS service
code = generator.generate_calculator(
    service_code='AmazonEC2',
    region='us-east-1',
    output_file='ec2_calculator.py'
)
```

## 🚀 Quick Start

### Basic Usage

```python
#!/usr/bin/env python3
from aws_abstract_calculator import AbstractCalculatorGenerator

# Create generator
generator = AbstractCalculatorGenerator()

# Generate EC2 calculator
ec2_code = generator.generate_calculator(
    service_code='AmazonEC2',
    region='us-east-1',
    output_file='my_ec2_calculator.py'
)

print("✓ Calculator generated!")
```

### With Manual Pricing Data

```python
from aws_abstract_calculator import (
    ServicePricing,
    PricingDimension,
    FormulaGenerator
)

# Define pricing manually
pricing = ServicePricing(
    service_code="AmazonEC2",
    service_name="Amazon EC2",
    region="us-east-1",
    pricing_dimensions={
        "t3.micro": [
            PricingDimension(
                unit="Hrs",
                price_per_unit=0.0104,
                description="t3.micro instance hour"
            )
        ]
    }
)

# Generate calculator
generator = FormulaGenerator(pricing)
code = generator.generate_python_calculator()

# Save to file
with open('custom_calculator.py', 'w') as f:
    f.write(code)
```

## 📊 Examples

Run the included examples:

```bash
# Demo of abstract calculator
python3 aws_abstract_calculator.py

# Full examples with multiple scenarios
python3 example_generate_calculator.py
```

### Generated Calculator Example

Input:
```python
generator.generate_calculator('AmazonEC2', 'us-east-1')
```

Output (`generated_ec2_calculator.py`):
```python
class Pricing:
    """Pricing for AmazonEC2"""

    T3_MICRO_HRS = 0.0104
    T3_SMALL_HRS = 0.0208
    M5_LARGE_HRS = 0.096
    EBS_GP3_GB_MO = 0.08

class CostCalculator:
    """Cost calculator for AmazonEC2"""

    def __init__(self):
        self.pricing = Pricing()

    def calculate(self, **kwargs) -> Dict[str, float]:
        total_cost = 0.0
        breakdown = {}

        # Add your calculation logic here

        return {
            "total": total_cost,
            "breakdown": breakdown
        }
```

## 🔄 Self-Updating Calculators

Create calculators that update themselves automatically:

```python
from aws_abstract_calculator import AbstractCalculatorGenerator
import schedule
import importlib

def update_pricing():
    """Update calculator with latest pricing"""
    generator = AbstractCalculatorGenerator(use_cache=False)

    # Generate fresh calculator
    code = generator.generate_calculator(
        'AmazonEC2',
        'us-east-1',
        output_file='calculators/ec2.py'
    )

    # Reload module
    import calculators.ec2
    importlib.reload(calculators.ec2)

    print("✓ Pricing updated!")

# Schedule daily updates
schedule.every().day.at("00:00").do(update_pricing)

# Or trigger manually
update_pricing()
```

## 🌐 AWS Price List API

The calculator uses the official AWS Price List API:

**Service List:**
```
https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/index.json
```

**Service Pricing:**
```
https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/{ServiceCode}/current/index.json
```

**Supported Services:**
- AmazonEC2
- AWSLambda
- AmazonS3
- AmazonDynamoDB
- AmazonRDS
- AmazonECS
- AmazonEKS
- And 200+ more...

## 💾 Caching

Pricing data is cached locally to reduce API calls:

```
.aws_pricing_cache/
├── AmazonEC2_pricing.json
├── AWSLambda_pricing.json
└── AmazonS3_pricing.json
```

**Cache behavior:**
- TTL: 24 hours
- Automatic refresh when expired
- Manual refresh: `use_cache=False`

## 🎨 Customization

### Add Custom Calculation Logic

Edit generated calculators to add your business logic:

```python
# generated_ec2_calculator.py

class CostCalculator:
    def calculate(self, **kwargs) -> Dict[str, float]:
        # Custom logic
        hours = kwargs.get('hours', 0)
        instance_type = kwargs.get('instance_type', 't3.micro')

        # Get rate dynamically
        rate = getattr(self.pricing, f"{instance_type.upper()}_HRS", 0)

        compute_cost = hours * rate

        return {
            "total": compute_cost,
            "breakdown": {
                "compute": compute_cost,
                "instance_type": instance_type,
                "hours": hours
            }
        }
```

### Extend the Generator

Subclass `FormulaGenerator` to customize code generation:

```python
from aws_abstract_calculator import FormulaGenerator

class CustomFormulaGenerator(FormulaGenerator):
    def generate_python_calculator(self) -> str:
        # Add custom code generation logic
        code = super().generate_python_calculator()

        # Add custom methods
        code += """
    def calculate_with_discount(self, discount_pct: float, **kwargs):
        result = self.calculate(**kwargs)
        result['total'] *= (1 - discount_pct / 100)
        return result
"""
        return code
```

## 🔧 Advanced Usage

### Multi-Region Pricing

```python
generator = AbstractCalculatorGenerator()

regions = ['us-east-1', 'us-west-2', 'eu-west-1']

for region in regions:
    code = generator.generate_calculator(
        'AmazonEC2',
        region,
        output_file=f'calculators/ec2_{region}.py'
    )
```

### Pricing Comparison

```python
# Compare pricing across regions
def compare_regions(service: str, regions: List[str]):
    generator = AbstractCalculatorGenerator()
    comparison = {}

    for region in regions:
        pricing = generator.fetcher.fetch_service_pricing(service, region)
        comparison[region] = pricing.pricing_dimensions

    return comparison

regions = ['us-east-1', 'eu-west-1', 'ap-southeast-1']
comparison = compare_regions('AmazonEC2', regions)
```

## 🤖 AI Agent Integration

Perfect for use as an AI agent tool:

```python
def cost_calculator_tool(service: str, region: str = 'us-east-1'):
    """
    AI Tool: Generate cost calculator for AWS service

    Args:
        service: AWS service code (e.g., 'AmazonEC2')
        region: AWS region (default: us-east-1)

    Returns:
        Generated calculator code
    """
    generator = AbstractCalculatorGenerator()
    return generator.generate_calculator(service, region)

# Use in AI agent
from typing import Callable

tools: List[Callable] = [
    cost_calculator_tool,
    # ... other tools
]
```

## 📝 Use Cases

### 1. Cost Estimation Platform
Build a web app that generates custom calculators for users' specific AWS services.

### 2. Multi-Cloud Cost Analysis
Extend to support Azure, GCP pricing APIs for comparison.

### 3. Budget Alerting
Generate calculators with built-in budget thresholds.

### 4. Cost Optimization
Identify pricing changes and recommend optimizations.

### 5. Documentation
Auto-generate pricing documentation for internal wikis.

## ⚠️ Limitations

1. **API Rate Limits**: AWS Price List API has rate limits
2. **Pricing Complexity**: Some services have complex tiered pricing
3. **Reserved/Spot Pricing**: Currently focuses on on-demand pricing
4. **Generated Code**: Requires manual logic implementation

## 🛣️ Roadmap

- [ ] Support for Reserved Instances pricing
- [ ] Spot Instance pricing integration
- [ ] Tiered pricing calculations
- [ ] Cost optimization recommendations
- [ ] Web UI for calculator generation
- [ ] Multi-cloud support (Azure, GCP)
- [ ] Real-time pricing alerts
- [ ] Historical pricing trends

## 📄 Files

```
.
├── aws_abstract_calculator.py           # Main calculator framework
├── example_generate_calculator.py       # Usage examples
├── generated_ec2_calculator.py          # Example generated calculator
├── s3_pricing_summary.json              # Example pricing summary
└── .aws_pricing_cache/                  # Pricing data cache
```

## 🔗 Related Calculators

- `aws_rag_cost_calculator.py` - RAG system costs (Bedrock, OpenSearch)
- `aws_compute_storage_calculator.py` - EC2, Lambda, S3 costs

## 🎓 Learning Resources

- [AWS Price List API Documentation](https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/price-changes.html)
- [AWS Pricing Overview](https://aws.amazon.com/pricing/)
- [Python Code Generation Patterns](https://docs.python.org/3/library/ast.html)

## 🤝 Contributing

Ideas for contributions:
1. Add support for more complex pricing models
2. Improve code generation templates
3. Add pricing trend analysis
4. Create visualization tools
5. Build web interface

## 📊 Performance

- **Fetching**: ~2-5 seconds per service (first time)
- **Caching**: ~50ms (cached reads)
- **Generation**: ~100ms per calculator
- **Cache size**: ~1-10MB per service

## ✅ Best Practices

1. **Use caching** in production to reduce API calls
2. **Update periodically** (daily/weekly) not real-time
3. **Version control** generated calculators
4. **Test generated code** before deployment
5. **Monitor API limits** if generating many calculators

---

**Created for AI Agent Integration**

This abstract calculator is designed to be used as a tool by AI agents, enabling them to dynamically generate cost calculators for any AWS service on demand.
