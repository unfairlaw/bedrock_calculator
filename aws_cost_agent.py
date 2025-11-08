#!/usr/bin/env python3
"""
AWS Cost Estimation Agent

An AI agent that uses three calculators as tools:
1. RAG Cost Calculator - for Bedrock/OpenSearch RAG systems
2. Compute/Storage Calculator - for EC2/Lambda/S3
3. Abstract Calculator - for any AWS service dynamically

Usage:
    python3 aws_cost_agent.py
    Or import and use programmatically:
        agent = AWSCostAgent()
        response = agent.process("Estimate costs for a RAG system with 100 manuals")
"""

import json
import re
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum

# Import calculator modules
from aws_rag_cost_calculator import (
    UsageScenario as RAGScenario,
    CostCalculator as RAGCalculator
)

from aws_compute_storage_calculator import (
    UsageScenario as ComputeScenario,
    EC2Usage,
    LambdaUsage,
    S3Usage,
    EC2InstanceType,
    S3StorageClass,
    CostCalculator as ComputeCalculator
)

from aws_abstract_calculator import AbstractCalculatorGenerator


class ToolType(Enum):
    """Available tools"""
    RAG_CALCULATOR = "rag_calculator"
    COMPUTE_CALCULATOR = "compute_calculator"
    ABSTRACT_CALCULATOR = "abstract_calculator"
    UNKNOWN = "unknown"


@dataclass
class ToolResponse:
    """Response from a tool execution"""
    tool: ToolType
    success: bool
    data: Optional[Dict] = None
    error: Optional[str] = None
    message: str = ""


class RAGCalculatorTool:
    """Tool wrapper for RAG Cost Calculator"""

    def __init__(self):
        self.name = "RAG Cost Calculator"
        self.description = """
        Estimates costs for RAG (Retrieval-Augmented Generation) systems using AWS Bedrock.

        Use this tool when the user asks about:
        - RAG system costs
        - Bedrock pricing
        - Document processing with AI
        - Technical manual Q&A systems
        - OpenSearch with embeddings
        - Multimodal document analysis

        Parameters:
        - num_manuals: Number of technical manuals/documents
        - avg_pages_per_manual: Average pages per manual (default: 150)
        - images_per_manual: Images per manual (default: 80)
        - tables_per_manual: Tables per manual (default: 40)
        - monthly_queries: User queries per month
        - avg_docs_per_query: Documents retrieved per query (default: 8)
        """

    def execute(
        self,
        num_manuals: int = 50,
        avg_pages_per_manual: int = 150,
        images_per_manual: int = 80,
        tables_per_manual: int = 40,
        monthly_queries: int = 10000,
        avg_docs_per_query: int = 8,
        **kwargs
    ) -> ToolResponse:
        """Execute RAG cost calculation"""

        try:
            scenario = RAGScenario(
                name="Custom RAG System",
                num_manuals=num_manuals,
                avg_pages_per_manual=avg_pages_per_manual,
                images_per_manual=images_per_manual,
                tables_per_manual=tables_per_manual,
                monthly_queries=monthly_queries,
                avg_docs_per_query=avg_docs_per_query
            )

            calculator = RAGCalculator(scenario)
            results = calculator.calculate_total_costs()

            message = self._format_results(results)

            return ToolResponse(
                tool=ToolType.RAG_CALCULATOR,
                success=True,
                data=results,
                message=message
            )

        except Exception as e:
            return ToolResponse(
                tool=ToolType.RAG_CALCULATOR,
                success=False,
                error=str(e),
                message=f"Error calculating RAG costs: {e}"
            )

    def _format_results(self, results: Dict) -> str:
        """Format results for display"""
        lines = [
            f"\n📊 RAG System Cost Estimate",
            f"{'='*60}",
            f"",
            f"💰 Costs:",
            f"   Setup (one-time):  ${results['setup_one_time']:,.2f}",
            f"   Monthly:           ${results['monthly_total']:,.2f}",
            f"   Annual:            ${results['yearly_total']:,.2f}",
            f"",
            f"📦 Breakdown:",
            f"   Infrastructure:    ${results['monthly_infrastructure']:,.2f}/month",
            f"   Queries:           ${results['monthly_queries']:,.2f}/month",
            f"",
        ]

        # OpenSearch details
        ops = results['breakdown']['opensearch']
        lines.extend([
            f"🔍 OpenSearch:",
            f"   OCUs needed:       {ops['ocus']}",
            f"   Compute:           ${ops['compute_monthly']:,.2f}/month",
            f"   Storage:           ${ops['storage_monthly']:,.2f}/month",
            f"",
        ])

        return "\n".join(lines)


class ComputeCalculatorTool:
    """Tool wrapper for Compute/Storage Calculator"""

    def __init__(self):
        self.name = "Compute & Storage Calculator"
        self.description = """
        Estimates costs for EC2, Lambda, and S3 usage.

        Use this tool when the user asks about:
        - EC2 instance costs
        - Lambda function costs
        - S3 storage costs
        - Web application infrastructure
        - API backend costs
        - Serverless architecture costs

        Parameters:
        - EC2: instance_type, num_instances, hours_per_month, ebs_gb
        - Lambda: monthly_invocations, avg_duration_ms, memory_mb
        - S3: storage_gb, storage_class, requests
        """

    def execute(
        self,
        # EC2 params
        ec2_instance_type: Optional[str] = None,
        ec2_num_instances: int = 0,
        ec2_hours_per_month: float = 730,
        ec2_ebs_gb: float = 50,
        # Lambda params
        lambda_invocations: int = 0,
        lambda_duration_ms: int = 200,
        lambda_memory_mb: int = 512,
        # S3 params
        s3_storage_gb: float = 0,
        s3_storage_class: str = "Standard",
        s3_get_requests: int = 0,
        s3_put_requests: int = 0,
        **kwargs
    ) -> ToolResponse:
        """Execute compute/storage cost calculation"""

        try:
            # Build EC2 usage
            ec2_usage = None
            if ec2_instance_type and ec2_num_instances > 0:
                instance_enum = self._parse_instance_type(ec2_instance_type)
                ec2_usage = [EC2Usage(
                    instance_type=instance_enum,
                    num_instances=ec2_num_instances,
                    hours_per_month=ec2_hours_per_month,
                    ebs_storage_gb=ec2_ebs_gb,
                    ebs_type="gp3"
                )]

            # Build Lambda usage
            lambda_usage = None
            if lambda_invocations > 0:
                lambda_usage = LambdaUsage(
                    monthly_invocations=lambda_invocations,
                    avg_duration_ms=lambda_duration_ms,
                    memory_mb=lambda_memory_mb
                )

            # Build S3 usage
            s3_usage = None
            if s3_storage_gb > 0:
                storage_class_enum = self._parse_storage_class(s3_storage_class)
                s3_usage = [S3Usage(
                    storage_gb=s3_storage_gb,
                    storage_class=storage_class_enum,
                    get_requests_monthly=s3_get_requests,
                    put_requests_monthly=s3_put_requests
                )]

            scenario = ComputeScenario(
                name="Custom Infrastructure",
                ec2_usage=ec2_usage,
                lambda_usage=lambda_usage,
                s3_usage=s3_usage
            )

            calculator = ComputeCalculator(scenario)
            results = calculator.calculate_total_costs()

            message = self._format_results(results)

            return ToolResponse(
                tool=ToolType.COMPUTE_CALCULATOR,
                success=True,
                data=results,
                message=message
            )

        except Exception as e:
            return ToolResponse(
                tool=ToolType.COMPUTE_CALCULATOR,
                success=False,
                error=str(e),
                message=f"Error calculating compute costs: {e}"
            )

    def _parse_instance_type(self, instance_type: str) -> EC2InstanceType:
        """Parse instance type string to enum"""
        # Normalize: t3.medium -> T3_MEDIUM
        normalized = instance_type.upper().replace('.', '_')
        try:
            return EC2InstanceType[normalized]
        except KeyError:
            # Default to t3.medium
            return EC2InstanceType.T3_MEDIUM

    def _parse_storage_class(self, storage_class: str) -> S3StorageClass:
        """Parse storage class string to enum"""
        mapping = {
            'standard': S3StorageClass.STANDARD,
            'standard-ia': S3StorageClass.STANDARD_IA,
            'intelligent': S3StorageClass.INTELLIGENT_TIERING,
            'glacier': S3StorageClass.GLACIER_INSTANT,
        }

        normalized = storage_class.lower()
        for key, value in mapping.items():
            if key in normalized:
                return value

        return S3StorageClass.STANDARD

    def _format_results(self, results: Dict) -> str:
        """Format results for display"""
        lines = [
            f"\n📊 Compute & Storage Cost Estimate",
            f"{'='*60}",
            f"",
            f"💰 Total Costs:",
            f"   Monthly:           ${results['monthly_total']:,.2f}",
            f"   Annual:            ${results['yearly_total']:,.2f}",
            f"",
        ]

        # EC2
        ec2 = results['breakdown']['ec2']
        if ec2['total_monthly'] > 0:
            lines.extend([
                f"🖥️  EC2:",
                f"   Compute:           ${ec2['compute_cost']:,.2f}/month",
                f"   Storage (EBS):     ${ec2['storage_cost']:,.2f}/month",
            ])
            if ec2['instances']:
                for inst in ec2['instances']:
                    lines.append(
                        f"   - {inst['num_instances']}x {inst['instance_type']}: "
                        f"${inst['total']:,.2f}/month"
                    )
            lines.append("")

        # Lambda
        lmb = results['breakdown']['lambda']
        if lmb['total_monthly'] > 0:
            lines.extend([
                f"⚡ Lambda:",
                f"   Total:             ${lmb['total_monthly']:,.2f}/month",
                f"   Invocations:       {lmb['monthly_invocations']:,}/month",
                f"   Memory:            {lmb['memory_mb']}MB",
                f"   Avg Duration:      {lmb['avg_duration_ms']}ms",
                f"",
            ])

        # S3
        s3 = results['breakdown']['s3']
        if s3['total_monthly'] > 0:
            lines.extend([
                f"🗄️  S3:",
                f"   Storage:           ${s3['storage_cost']:,.2f}/month",
                f"   Requests:          ${s3['request_cost']:,.2f}/month",
            ])
            if s3['buckets']:
                for bucket in s3['buckets']:
                    lines.append(
                        f"   - {bucket['storage_class']}: {bucket['storage_gb']:.1f}GB"
                    )
            lines.append("")

        return "\n".join(lines)


class AbstractCalculatorTool:
    """Tool wrapper for Abstract Calculator"""

    def __init__(self):
        self.name = "Abstract Calculator Generator"
        self.description = """
        Generates cost calculators for any AWS service dynamically.

        Use this tool when the user asks about:
        - A service not covered by other calculators
        - RDS, DynamoDB, ECS, EKS, etc.
        - Custom or uncommon AWS services
        - Latest pricing for any service
        - Generating a reusable calculator

        Parameters:
        - service_code: AWS service code (e.g., 'AmazonRDS', 'AmazonDynamoDB')
        - region: AWS region (default: 'us-east-1')
        - generate_file: Whether to save generated calculator
        """

    def execute(
        self,
        service_code: str,
        region: str = "us-east-1",
        generate_file: bool = False,
        **kwargs
    ) -> ToolResponse:
        """Execute abstract calculator generation"""

        try:
            generator = AbstractCalculatorGenerator(use_cache=True)

            # Generate pricing summary
            pricing = generator.fetcher.fetch_service_pricing(service_code, region)

            # Generate calculator code
            output_file = None
            if generate_file:
                output_file = f"generated_{service_code.lower()}_calculator.py"

            code = generator.generate_calculator(
                service_code=service_code,
                region=region,
                output_file=output_file
            )

            message = self._format_results(service_code, pricing, output_file, code)

            return ToolResponse(
                tool=ToolType.ABSTRACT_CALCULATOR,
                success=True,
                data={
                    'service': service_code,
                    'region': region,
                    'code_length': len(code),
                    'output_file': output_file,
                    'categories': len(pricing.pricing_dimensions)
                },
                message=message
            )

        except Exception as e:
            return ToolResponse(
                tool=ToolType.ABSTRACT_CALCULATOR,
                success=False,
                error=str(e),
                message=f"Error generating calculator for {service_code}: {e}"
            )

    def _format_results(
        self,
        service_code: str,
        pricing: Any,
        output_file: Optional[str],
        code: str
    ) -> str:
        """Format results for display"""
        lines = [
            f"\n📊 Abstract Calculator - {service_code}",
            f"{'='*60}",
            f"",
            f"✅ Successfully generated calculator!",
            f"",
            f"📦 Service Information:",
            f"   Service:           {service_code}",
            f"   Region:            {pricing.region}",
            f"   Pricing Categories: {len(pricing.pricing_dimensions)}",
            f"",
        ]

        # Show sample pricing categories
        if pricing.pricing_dimensions:
            lines.append(f"💰 Sample Pricing Categories:")
            for i, category in enumerate(list(pricing.pricing_dimensions.keys())[:5]):
                dimensions = pricing.pricing_dimensions[category]
                if dimensions:
                    dim = dimensions[0]
                    lines.append(
                        f"   - {category}: ${dim.price_per_unit}/{dim.unit}"
                    )
                if i >= 4:
                    break
            lines.append("")

        if output_file:
            lines.extend([
                f"💾 Generated File:",
                f"   {output_file}",
                f"   Size: {len(code)} characters",
                f"",
                f"You can now import and use:",
                f"   from {output_file[:-3]} import CostCalculator",
                f"",
            ])

        return "\n".join(lines)


class AWSCostAgent:
    """
    AI Agent for AWS Cost Estimation

    Uses three calculators as tools to answer cost questions.
    """

    def __init__(self):
        self.tools = {
            ToolType.RAG_CALCULATOR: RAGCalculatorTool(),
            ToolType.COMPUTE_CALCULATOR: ComputeCalculatorTool(),
            ToolType.ABSTRACT_CALCULATOR: AbstractCalculatorTool(),
        }

        self.conversation_history: List[Dict[str, str]] = []

    def process(self, user_input: str) -> str:
        """
        Process user input and route to appropriate tool

        Args:
            user_input: Natural language query from user

        Returns:
            Formatted response
        """

        # Add to conversation history
        self.conversation_history.append({
            "role": "user",
            "content": user_input
        })

        # Identify intent and extract parameters
        intent, params = self._identify_intent(user_input)

        # Route to appropriate tool
        if intent == ToolType.RAG_CALCULATOR:
            response = self.tools[ToolType.RAG_CALCULATOR].execute(**params)
        elif intent == ToolType.COMPUTE_CALCULATOR:
            response = self.tools[ToolType.COMPUTE_CALCULATOR].execute(**params)
        elif intent == ToolType.ABSTRACT_CALCULATOR:
            response = self.tools[ToolType.ABSTRACT_CALCULATOR].execute(**params)
        else:
            response = self._handle_unknown_intent(user_input)

        # Add to conversation history
        self.conversation_history.append({
            "role": "assistant",
            "content": response.message
        })

        return response.message

    def _identify_intent(self, user_input: str) -> Tuple[ToolType, Dict]:
        """
        Identify user intent and extract parameters

        Returns:
            (intent_type, parameters)
        """

        user_lower = user_input.lower()

        # RAG Calculator keywords
        rag_keywords = [
            'rag', 'bedrock', 'retrieval', 'embeddings', 'opensearch',
            'document processing', 'manual', 'technical docs', 'claude',
            'multimodal', 'textract'
        ]

        # Compute Calculator keywords
        compute_keywords = [
            'ec2', 'lambda', 's3', 'instance', 'serverless',
            'web app', 'api', 'storage', 'bucket', 'function'
        ]

        # Abstract Calculator keywords
        abstract_keywords = [
            'rds', 'dynamodb', 'ecs', 'eks', 'fargate', 'elasticache',
            'redshift', 'generate calculator', 'any service', 'pricing for'
        ]

        # Check for RAG calculator
        if any(keyword in user_lower for keyword in rag_keywords):
            params = self._extract_rag_params(user_input)
            return ToolType.RAG_CALCULATOR, params

        # Check for compute calculator
        if any(keyword in user_lower for keyword in compute_keywords):
            params = self._extract_compute_params(user_input)
            return ToolType.COMPUTE_CALCULATOR, params

        # Check for abstract calculator
        if any(keyword in user_lower for keyword in abstract_keywords):
            params = self._extract_abstract_params(user_input)
            return ToolType.ABSTRACT_CALCULATOR, params

        return ToolType.UNKNOWN, {}

    def _extract_rag_params(self, user_input: str) -> Dict:
        """Extract RAG calculator parameters from user input"""
        params = {}

        # Extract numbers followed by keywords
        patterns = {
            'num_manuals': r'(\d+)\s*(?:manuals?|documents?|docs?)',
            'monthly_queries': r'(\d+[,\d]*)\s*(?:queries|query|requests?)',
            'avg_pages_per_manual': r'(\d+)\s*(?:pages?)',
        }

        for param, pattern in patterns.items():
            match = re.search(pattern, user_input.lower())
            if match:
                value = match.group(1).replace(',', '')
                params[param] = int(value)

        return params

    def _extract_compute_params(self, user_input: str) -> Dict:
        """Extract compute calculator parameters from user input"""
        params = {}

        # EC2 instance type
        instance_match = re.search(r'(t3|m5|c5|r5)\.(\w+)', user_input.lower())
        if instance_match:
            params['ec2_instance_type'] = f"{instance_match.group(1)}.{instance_match.group(2)}"

            # Try to find number before instance type
            number_before = re.search(r'(\d+)\s+' + re.escape(params['ec2_instance_type']), user_input.lower())
            if number_before:
                params['ec2_num_instances'] = int(number_before.group(1))

        # Number of instances (general pattern)
        instance_count = re.search(r'(\d+)\s*(?:instances?|servers?)', user_input.lower())
        if instance_count and 'ec2_num_instances' not in params:
            params['ec2_num_instances'] = int(instance_count.group(1))

        # Lambda invocations (look for million)
        lambda_million = re.search(r'(\d+)\s*million\s*(?:lambda\s*)?(?:invocations?|calls?|executions?)', user_input.lower())
        if lambda_million:
            params['lambda_invocations'] = int(lambda_million.group(1)) * 1_000_000
        else:
            # Regular lambda invocations
            lambda_match = re.search(r'(\d+[,\d]*)\s*(?:lambda\s*)?(?:invocations?|calls?|executions?)', user_input.lower())
            if lambda_match:
                value = lambda_match.group(1).replace(',', '')
                params['lambda_invocations'] = int(value)

        # Lambda memory
        memory_match = re.search(r'(\d+)\s*(?:mb|megabytes?)', user_input.lower())
        if memory_match and ('lambda' in user_input.lower() or 'lambda_invocations' in params):
            params['lambda_memory_mb'] = int(memory_match.group(1))

        # S3 storage
        s3_match = re.search(r'(\d+[,\d]*)\s*(?:gb|gigabytes?)', user_input.lower())
        if s3_match and ('s3' in user_input.lower() or 'storage' in user_input.lower()):
            value = s3_match.group(1).replace(',', '')
            params['s3_storage_gb'] = float(value)

        return params

    def _extract_abstract_params(self, user_input: str) -> Dict:
        """Extract abstract calculator parameters from user input"""
        params = {}

        # Service code patterns
        service_patterns = {
            'rds': 'AmazonRDS',
            'dynamodb': 'AmazonDynamoDB',
            'ecs': 'AmazonECS',
            'eks': 'AmazonEKS',
            'elasticache': 'AmazonElastiCache',
            'redshift': 'AmazonRedshift',
            'sqs': 'AmazonSQS',
            'sns': 'AmazonSNS',
        }

        user_lower = user_input.lower()
        for keyword, service_code in service_patterns.items():
            if keyword in user_lower:
                params['service_code'] = service_code
                break

        # Region
        region_match = re.search(r'(?:in|region)\s+(us-\w+-\d+|eu-\w+-\d+)', user_input.lower())
        if region_match:
            params['region'] = region_match.group(1)

        # Generate file flag
        if 'generate' in user_lower or 'save' in user_lower or 'create file' in user_lower:
            params['generate_file'] = True

        return params

    def _handle_unknown_intent(self, user_input: str) -> ToolResponse:
        """Handle unknown or ambiguous intents"""

        message = f"""
❓ I'm not sure which calculator to use for your question.

I have three tools available:

1️⃣  **RAG Cost Calculator**
   For: Bedrock, OpenSearch, document processing, RAG systems
   Example: "Estimate costs for a RAG system with 100 manuals and 10,000 queries/month"

2️⃣  **Compute/Storage Calculator**
   For: EC2, Lambda, S3 costs
   Example: "How much for 4 t3.medium instances and 2 million Lambda invocations?"

3️⃣  **Abstract Calculator**
   For: Any other AWS service (RDS, DynamoDB, ECS, etc.)
   Example: "Generate a calculator for RDS in us-west-2"

Could you rephrase your question to be more specific about which AWS services you're interested in?
"""

        return ToolResponse(
            tool=ToolType.UNKNOWN,
            success=False,
            message=message
        )

    def get_available_tools(self) -> str:
        """Get formatted list of available tools"""
        lines = [
            "\n🛠️  Available Tools:",
            "=" * 60,
            "",
        ]

        for tool_type, tool in self.tools.items():
            lines.extend([
                f"📌 {tool.name}",
                f"   {tool.description.strip()}",
                "",
            ])

        return "\n".join(lines)


def interactive_mode():
    """Run agent in interactive mode"""

    print("\n" + "="*60)
    print("🤖 AWS Cost Estimation Agent")
    print("="*60)
    print("\nI can help estimate AWS costs using three calculators:")
    print("  1. RAG systems (Bedrock, OpenSearch)")
    print("  2. Compute/Storage (EC2, Lambda, S3)")
    print("  3. Any AWS service (generates custom calculators)")
    print("\nType 'help' for examples, 'quit' to exit")
    print("="*60 + "\n")

    agent = AWSCostAgent()

    while True:
        try:
            user_input = input("You: ").strip()

            if not user_input:
                continue

            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Goodbye!")
                break

            if user_input.lower() == 'help':
                print(agent.get_available_tools())
                print("\n💡 Example questions:")
                print("  - 'Estimate RAG costs for 50 manuals with 5000 queries per month'")
                print("  - 'How much for 2 t3.medium instances and 1000GB of S3 storage?'")
                print("  - 'Generate a calculator for RDS'")
                print("  - 'What would 5 million Lambda invocations cost?'")
                print()
                continue

            # Process input
            response = agent.process(user_input)
            print(f"\n{response}\n")

        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}\n")


def demo_mode():
    """Run agent with demo queries"""

    print("\n" + "="*60)
    print("🤖 AWS Cost Agent - Demo Mode")
    print("="*60 + "\n")

    agent = AWSCostAgent()

    demo_queries = [
        "Estimate costs for a RAG system with 100 manuals and 10,000 queries per month",
        "How much for 4 t3.medium instances running 24/7?",
        "What would 5 million Lambda invocations cost with 512MB memory?",
    ]

    for i, query in enumerate(demo_queries, 1):
        print(f"\n{'='*60}")
        print(f"Demo Query {i}/{len(demo_queries)}")
        print(f"{'='*60}")
        print(f"\nUser: {query}")

        response = agent.process(query)
        print(response)

    print(f"\n{'='*60}")
    print("✅ Demo Complete!")
    print(f"{'='*60}\n")


def main():
    """Main entry point"""
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == 'demo':
        demo_mode()
    else:
        interactive_mode()


if __name__ == "__main__":
    main()
