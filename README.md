# AWS Cost Calculator Suite

A comprehensive collection of AWS cost calculators designed for AI agent integration. This suite provides three powerful calculators, each serving different use cases.

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

## 📊 Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                 AWS Cost Calculator Suite                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1️⃣  RAG Cost Calculator          (Specialized)                 │
│      └─ Bedrock, OpenSearch, Textract                           │
│                                                                  │
│  2️⃣  Compute/Storage Calculator    (Common Services)            │
│      └─ EC2, Lambda, S3                                          │
│                                                                  │
│  3️⃣  Abstract Calculator           (Meta/Self-Generating)       │
│      └─ Any AWS Service (200+)                                   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## 🎯 Calculators

### 1. RAG Cost Calculator

**Purpose:** Estimate costs for RAG (Retrieval-Augmented Generation) systems using AWS Bedrock.

**File:** `aws_rag_cost_calculator.py`

**Services:**
- AWS Bedrock (Claude 3.5 Sonnet)
- OpenSearch Serverless
- Amazon Textract
- S3 Storage
- DynamoDB

**Use Cases:**
- Multimodal document processing
- Technical manual Q&A systems
- AI-powered knowledge bases

**Example:**
```python
from aws_rag_cost_calculator import UsageScenario, CostCalculator

scenario = UsageScenario(
    name="Enterprise RAG",
    num_manuals=200,
    avg_pages_per_manual=200,
    monthly_queries=50000
)

calculator = CostCalculator(scenario)
results = calculator.calculate_total_costs()

print(f"Monthly: ${results['monthly_total']:,.2f}")
print(f"Yearly: ${results['yearly_total']:,.2f}")
```

**Cost Estimates:**
- Pilot (10 manuals): $4.4K/year
- Production (50 manuals): $6.1K/year
- Enterprise (200 manuals): $15.3K/year

📄 **Detailed Analysis:** [AWS_RAG_COST_ANALYSIS.md](AWS_RAG_COST_ANALYSIS.md)
📊 **Executive Summary:** [EXECUTIVE_SUMMARY.md](EXECUTIVE_SUMMARY.md)

---

### 2. Compute/Storage Calculator

**Purpose:** Calculate costs for common AWS compute and storage services.

**File:** `aws_compute_storage_calculator.py`

**Services:**
- Amazon EC2 (11 instance types)
- AWS Lambda (with free tier)
- Amazon S3 (7 storage classes)
- EBS Storage
- Data Transfer

**Use Cases:**
- Web applications
- API backends
- Serverless architectures
- High-performance computing

**Example:**
```python
from aws_compute_storage_calculator import (
    UsageScenario, EC2Usage, LambdaUsage, S3Usage,
    EC2InstanceType, S3StorageClass, CostCalculator
)

scenario = UsageScenario(
    name="Web Application",
    ec2_usage=[
        EC2Usage(
            instance_type=EC2InstanceType.T3_MEDIUM,
            num_instances=2,
            hours_per_month=730,
            ebs_storage_gb=50
        )
    ],
    lambda_usage=LambdaUsage(
        monthly_invocations=2_000_000,
        avg_duration_ms=200,
        memory_mb=512
    ),
    s3_usage=[
        S3Usage(
            storage_gb=1000,
            storage_class=S3StorageClass.STANDARD,
            get_requests_monthly=5_000_000
        )
    ]
)

calculator = CostCalculator(scenario)
results = calculator.calculate_total_costs()
```

**Pre-built Scenarios:**
- Small Startup: $193/month ($2.3K/year)
- Medium Business: $1,634/month ($19.6K/year)
- Serverless-First: $1,023/month ($12.3K/year)
- Enterprise HPC: $22,324/month ($267.9K/year)

---

### 3. Abstract Calculator ⭐

**Purpose:** Meta-calculator that generates cost calculators for ANY AWS service dynamically.

**File:** `aws_abstract_calculator.py`

**Key Features:**
- ✨ **Self-Generating:** Fetches pricing and writes calculator code
- 🌐 **AWS Price List API:** Direct integration with official AWS pricing
- 💾 **Caching:** 24-hour cache for offline operation
- 🔄 **Auto-Update:** Can refresh pricing automatically
- 🤖 **AI-Ready:** Perfect for AI agent tool integration

**Services:** 200+ AWS services supported via Price List API

**Use Cases:**
- Dynamic cost estimation platforms
- Self-updating pricing systems
- Multi-service cost analysis
- AI agent tools

**Example:**
```python
from aws_abstract_calculator import AbstractCalculatorGenerator

# Generate calculator for any AWS service
generator = AbstractCalculatorGenerator(use_cache=True)

# Example: Generate RDS calculator
code = generator.generate_calculator(
    service_code='AmazonRDS',
    region='us-east-1',
    output_file='rds_calculator.py'
)

# The generated file contains:
# - Pricing constants from AWS API
# - Calculator class with calculate() method
# - Documentation and usage examples
```

**Generated Output Example:**
```python
class Pricing:
    """Pricing for AmazonRDS"""

    DB_T3_MICRO_HRS = 0.017
    DB_M5_LARGE_HRS = 0.192
    STORAGE_GP3_GB_MO = 0.115
    # ... more pricing constants

class CostCalculator:
    def calculate(self, **kwargs) -> Dict[str, float]:
        # Your custom logic here
        return {"total": cost, "breakdown": {...}}
```

📄 **Full Documentation:** [ABSTRACT_CALCULATOR_README.md](ABSTRACT_CALCULATOR_README.md)

---

## 🚀 Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/unfairlaw/bedrock_calculator.git
cd bedrock_calculator

# No dependencies required! Pure Python 3.8+
```

### Run Calculators

```bash
# RAG Calculator
python3 aws_rag_cost_calculator.py

# Compute/Storage Calculator
python3 aws_compute_storage_calculator.py

# Abstract Calculator Demo
python3 aws_abstract_calculator.py

# Abstract Calculator Examples
python3 example_generate_calculator.py
```

## 🤖 AI Agent Integration

All three calculators are designed to be used as tools by AI agents.

### Example Tool Definitions

```python
def estimate_rag_costs(num_manuals: int, monthly_queries: int) -> Dict:
    """Estimate costs for RAG system"""
    from aws_rag_cost_calculator import UsageScenario, CostCalculator

    scenario = UsageScenario(
        name="Custom",
        num_manuals=num_manuals,
        monthly_queries=monthly_queries,
        # ... other params
    )

    calculator = CostCalculator(scenario)
    return calculator.calculate_total_costs()


def estimate_compute_costs(instance_type: str, num_instances: int) -> Dict:
    """Estimate EC2/Lambda/S3 costs"""
    from aws_compute_storage_calculator import CostCalculator, UsageScenario
    # ... implementation


def generate_cost_calculator(service: str, region: str = 'us-east-1') -> str:
    """Generate calculator for any AWS service"""
    from aws_abstract_calculator import AbstractCalculatorGenerator

    generator = AbstractCalculatorGenerator()
    return generator.generate_calculator(service, region)
```

### LangChain Tool Example

```python
from langchain.tools import Tool

tools = [
    Tool(
        name="RAGCostEstimator",
        func=estimate_rag_costs,
        description="Estimate costs for AWS Bedrock RAG systems. Input: number of manuals and monthly queries."
    ),
    Tool(
        name="ComputeCostEstimator",
        func=estimate_compute_costs,
        description="Estimate costs for EC2, Lambda, and S3 usage."
    ),
    Tool(
        name="GenerateCalculator",
        func=generate_cost_calculator,
        description="Generate a cost calculator for any AWS service dynamically."
    )
]
```

## 📁 Repository Structure

```
bedrock_calculator/
├── README.md                               # This file
│
├── aws_rag_cost_calculator.py              # RAG calculator
├── aws_rag_costs_detailed.json             # RAG sample results
├── AWS_RAG_COST_ANALYSIS.md                # RAG detailed analysis
├── EXECUTIVE_SUMMARY.md                    # RAG executive summary
│
├── aws_compute_storage_calculator.py       # Compute/storage calculator
├── aws_compute_storage_costs.json          # Compute sample results
│
├── aws_abstract_calculator.py              # Abstract calculator core
├── example_generate_calculator.py          # Abstract calculator examples
├── ABSTRACT_CALCULATOR_README.md           # Abstract calculator docs
├── generated_ec2_calculator.py             # Example generated code
└── s3_pricing_summary.json                 # Example pricing summary
```

## 🎓 Use Cases

### 1. Cost Planning
Use pre-built calculators to estimate costs before deploying AWS infrastructure.

### 2. Budget Optimization
Analyze different scenarios to find cost-optimal configurations.

### 3. Proposal Generation
Generate cost estimates for client proposals quickly.

### 4. Multi-Region Comparison
Compare costs across AWS regions using the abstract calculator.

### 5. AI Cost Assistant
Integrate with AI agents to provide real-time cost estimates in conversations.

### 6. FinOps Automation
Automate cost tracking and reporting for finance teams.

## 🔧 Customization

### Modify Scenarios

```python
# Customize RAG calculator
scenario = UsageScenario(
    name="My Custom RAG",
    num_manuals=100,
    avg_pages_per_manual=150,
    monthly_queries=25000,
    # Adjust all parameters to your needs
)

# Customize Compute calculator
ec2 = EC2Usage(
    instance_type=EC2InstanceType.M5_XLARGE,
    num_instances=4,
    hours_per_month=730
)
```

### Extend Calculators

```python
# Extend with custom pricing
class CustomCostCalculator(CostCalculator):
    def calculate_with_discount(self, discount_pct: float):
        results = self.calculate_total_costs()
        results['monthly_total'] *= (1 - discount_pct / 100)
        return results
```

## 📊 Output Formats

All calculators support JSON export:

```python
import json

results = calculator.calculate_total_costs()

# Save to JSON
with open('cost_estimate.json', 'w') as f:
    json.dump(results, f, indent=2)

# Results structure
{
  "scenario": "Production",
  "monthly_total": 1245.17,
  "yearly_total": 14942.04,
  "breakdown": {
    "ec2": {...},
    "lambda": {...},
    "s3": {...}
  }
}
```

## 🌟 Features

| Feature | RAG Calculator | Compute Calculator | Abstract Calculator |
|---------|----------------|-------------------|---------------------|
| **Pre-built Scenarios** | ✅ 4 scenarios | ✅ 4 scenarios | ➖ User-defined |
| **Service Coverage** | 5 services | 3 services | 200+ services |
| **Code Generation** | ➖ N/A | ➖ N/A | ✅ Yes |
| **Auto-Update** | ➖ Manual | ➖ Manual | ✅ Automatic |
| **Offline Mode** | ✅ Yes | ✅ Yes | ✅ Cached |
| **AI Agent Ready** | ✅ Yes | ✅ Yes | ✅ Yes |
| **JSON Export** | ✅ Yes | ✅ Yes | ✅ Yes |

## 🎯 Choosing the Right Calculator

```
┌─────────────────────────────────────────────────────────┐
│ Need to estimate RAG/Bedrock costs?                     │
│ → Use: aws_rag_cost_calculator.py                       │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ Need EC2/Lambda/S3 costs for web apps?                  │
│ → Use: aws_compute_storage_calculator.py                │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ Need a calculator for a service not covered?            │
│ → Use: aws_abstract_calculator.py                       │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ Building an AI agent that needs cost estimation?        │
│ → Use: All three as complementary tools!                │
└─────────────────────────────────────────────────────────┘
```

## 💡 Examples

### Complete Cost Analysis

```python
#!/usr/bin/env python3
"""Complete AWS cost analysis for a web application"""

from aws_compute_storage_calculator import *
from aws_rag_cost_calculator import *

# Infrastructure costs
infra_scenario = UsageScenario(
    name="Production Infrastructure",
    ec2_usage=[...],
    lambda_usage=...,
    s3_usage=[...]
)

infra_calculator = CostCalculator(infra_scenario)
infra_costs = infra_calculator.calculate_total_costs()

# RAG system costs (if using AI features)
rag_scenario = UsageScenario(
    name="AI Features",
    num_manuals=50,
    monthly_queries=10000
)

rag_calculator = CostCalculator(rag_scenario)
rag_costs = rag_calculator.calculate_total_costs()

# Total costs
total_monthly = (
    infra_costs['monthly_total'] +
    rag_costs['monthly_total']
)

print(f"Total Monthly Cost: ${total_monthly:,.2f}")
print(f"Infrastructure: ${infra_costs['monthly_total']:,.2f}")
print(f"AI/RAG: ${rag_costs['monthly_total']:,.2f}")
```

## 🔮 Future Enhancements

- [ ] Web UI for interactive cost estimation
- [ ] Reserved Instance pricing support
- [ ] Spot Instance calculations
- [ ] Savings Plans recommendations
- [ ] Cost anomaly detection
- [ ] Multi-cloud support (Azure, GCP)
- [ ] Historical cost tracking
- [ ] Budget alerting
- [ ] Cost optimization suggestions
- [ ] GraphQL API

## 📈 Performance

| Operation | Time | Notes |
|-----------|------|-------|
| RAG Calculator | ~50ms | Pre-built scenarios |
| Compute Calculator | ~100ms | Pre-built scenarios |
| Abstract Calculator (cached) | ~150ms | Using cached pricing |
| Abstract Calculator (live) | ~3-5s | First fetch from AWS API |
| Code Generation | ~100ms | Per service |

## 🤝 Contributing

Contributions welcome! Areas of interest:

1. Additional calculator types
2. More pre-built scenarios
3. Enhanced code generation templates
4. Web interface
5. Additional cloud providers
6. Cost optimization algorithms

## 📝 License

MIT License - See LICENSE file for details

## 🙏 Acknowledgments

- AWS Price List API for pricing data
- Python community for excellent tooling
- AI community for agent integration patterns

## 📞 Support

For questions or issues:
- Open an issue on GitHub
- Check individual README files for detailed docs
- Review example scripts for usage patterns

---

**Built for the AI Agent Era**

These calculators are specifically designed to be used as tools by AI agents, enabling intelligent cost estimation and optimization in conversational interfaces.

**Version:** 1.0.0
**Last Updated:** 2025-11-08
**Python:** 3.8+
