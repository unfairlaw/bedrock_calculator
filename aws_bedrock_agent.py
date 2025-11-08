#!/usr/bin/env python3
"""
AWS Bedrock AI Cost Agent

Real AI agent using AWS Bedrock with Claude 3.5 Sonnet
Uses tool calling (function calling) to interact with cost calculators
"""

import os
import json
import boto3
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

# Import calculators
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


@dataclass
class BedrockConfig:
    """AWS Bedrock configuration"""
    region: str = os.getenv('AWS_REGION', 'us-east-1')
    model_id: str = 'anthropic.claude-3-5-sonnet-20241022-v2:0'
    max_tokens: int = 4096
    temperature: float = 0.1


class AWSBedrockCostAgent:
    """
    AI Cost Agent using AWS Bedrock with Claude 3.5 Sonnet

    Uses tool calling to execute cost calculations
    """

    def __init__(self, config: Optional[BedrockConfig] = None):
        self.config = config or BedrockConfig()

        # Initialize Bedrock client
        self.bedrock = boto3.client(
            service_name='bedrock-runtime',
            region_name=self.config.region
        )

        # Conversation history
        self.conversation_history: List[Dict] = []

        # Tool definitions
        self.tools = self._define_tools()

    def _define_tools(self) -> List[Dict]:
        """
        Define tools (functions) that Claude can call

        Uses Bedrock's tool specification format
        """
        return [
            {
                "toolSpec": {
                    "name": "estimate_rag_costs",
                    "description": "Estimates costs for AWS Bedrock RAG (Retrieval-Augmented Generation) systems. Use this when the user asks about RAG, Bedrock, OpenSearch, document processing, embeddings, or technical manual Q&A systems.",
                    "inputSchema": {
                        "json": {
                            "type": "object",
                            "properties": {
                                "num_manuals": {
                                    "type": "integer",
                                    "description": "Number of technical manuals or documents to process"
                                },
                                "avg_pages_per_manual": {
                                    "type": "integer",
                                    "description": "Average number of pages per manual (default: 150)"
                                },
                                "images_per_manual": {
                                    "type": "integer",
                                    "description": "Average number of images per manual (default: 80)"
                                },
                                "tables_per_manual": {
                                    "type": "integer",
                                    "description": "Average number of tables per manual (default: 40)"
                                },
                                "monthly_queries": {
                                    "type": "integer",
                                    "description": "Number of user queries per month"
                                },
                                "avg_docs_per_query": {
                                    "type": "integer",
                                    "description": "Average number of documents retrieved per query (default: 8)"
                                }
                            },
                            "required": ["num_manuals", "monthly_queries"]
                        }
                    }
                }
            },
            {
                "toolSpec": {
                    "name": "estimate_compute_costs",
                    "description": "Estimates costs for AWS compute and storage services including EC2 instances, Lambda functions, and S3 storage. Use this for general infrastructure, web applications, serverless, or API backends.",
                    "inputSchema": {
                        "json": {
                            "type": "object",
                            "properties": {
                                "ec2_instance_type": {
                                    "type": "string",
                                    "description": "EC2 instance type (e.g., 't3.medium', 'm5.large', 'c5.xlarge')",
                                    "enum": ["t3.micro", "t3.small", "t3.medium", "t3.large",
                                            "m5.large", "m5.xlarge", "m5.2xlarge",
                                            "c5.large", "c5.xlarge", "r5.large", "r5.xlarge"]
                                },
                                "ec2_num_instances": {
                                    "type": "integer",
                                    "description": "Number of EC2 instances"
                                },
                                "ec2_hours_per_month": {
                                    "type": "number",
                                    "description": "Hours running per month (max 730 for 24/7)"
                                },
                                "ec2_ebs_gb": {
                                    "type": "number",
                                    "description": "EBS storage in GB per instance (default: 50)"
                                },
                                "lambda_invocations": {
                                    "type": "integer",
                                    "description": "Monthly Lambda function invocations"
                                },
                                "lambda_duration_ms": {
                                    "type": "integer",
                                    "description": "Average Lambda execution duration in milliseconds (default: 200)"
                                },
                                "lambda_memory_mb": {
                                    "type": "integer",
                                    "description": "Lambda memory allocation in MB (default: 512)"
                                },
                                "s3_storage_gb": {
                                    "type": "number",
                                    "description": "S3 storage in GB"
                                },
                                "s3_storage_class": {
                                    "type": "string",
                                    "description": "S3 storage class",
                                    "enum": ["Standard", "Standard-IA", "Intelligent-Tiering",
                                            "Glacier", "One Zone-IA"]
                                },
                                "s3_get_requests": {
                                    "type": "integer",
                                    "description": "Monthly S3 GET requests"
                                },
                                "s3_put_requests": {
                                    "type": "integer",
                                    "description": "Monthly S3 PUT requests"
                                }
                            },
                            "required": []
                        }
                    }
                }
            },
            {
                "toolSpec": {
                    "name": "generate_calculator",
                    "description": "Generates a cost calculator for any AWS service dynamically. Use this when asked about services not covered by other tools like RDS, DynamoDB, ECS, EKS, ElastiCache, or when asked to generate/create a calculator.",
                    "inputSchema": {
                        "json": {
                            "type": "object",
                            "properties": {
                                "service_code": {
                                    "type": "string",
                                    "description": "AWS service code (e.g., 'AmazonRDS', 'AmazonDynamoDB', 'AmazonECS')"
                                },
                                "region": {
                                    "type": "string",
                                    "description": "AWS region (default: 'us-east-1')"
                                }
                            },
                            "required": ["service_code"]
                        }
                    }
                }
            }
        ]

    def _execute_tool(self, tool_name: str, tool_input: Dict) -> Dict:
        """Execute a tool (calculator) and return results"""

        try:
            if tool_name == "estimate_rag_costs":
                return self._execute_rag_calculator(tool_input)

            elif tool_name == "estimate_compute_costs":
                return self._execute_compute_calculator(tool_input)

            elif tool_name == "generate_calculator":
                return self._execute_abstract_calculator(tool_input)

            else:
                return {"error": f"Unknown tool: {tool_name}"}

        except Exception as e:
            return {"error": str(e)}

    def _execute_rag_calculator(self, params: Dict) -> Dict:
        """Execute RAG cost calculator"""
        scenario = RAGScenario(
            name="Custom RAG System",
            num_manuals=params.get('num_manuals', 50),
            avg_pages_per_manual=params.get('avg_pages_per_manual', 150),
            images_per_manual=params.get('images_per_manual', 80),
            tables_per_manual=params.get('tables_per_manual', 40),
            monthly_queries=params.get('monthly_queries', 10000),
            avg_docs_per_query=params.get('avg_docs_per_query', 8)
        )

        calculator = RAGCalculator(scenario)
        results = calculator.calculate_total_costs()

        return {
            "setup_cost": results['setup_one_time'],
            "monthly_cost": results['monthly_total'],
            "annual_cost": results['yearly_total'],
            "breakdown": {
                "infrastructure": results['monthly_infrastructure'],
                "queries": results['monthly_queries'],
                "opensearch_ocus": results['breakdown']['opensearch']['ocus']
            }
        }

    def _execute_compute_calculator(self, params: Dict) -> Dict:
        """Execute compute/storage calculator"""

        # Build EC2 usage
        ec2_usage = None
        if params.get('ec2_instance_type') and params.get('ec2_num_instances'):
            instance_type = params['ec2_instance_type'].upper().replace('.', '_')
            try:
                instance_enum = EC2InstanceType[instance_type]
            except KeyError:
                instance_enum = EC2InstanceType.T3_MEDIUM

            ec2_usage = [EC2Usage(
                instance_type=instance_enum,
                num_instances=params['ec2_num_instances'],
                hours_per_month=params.get('ec2_hours_per_month', 730),
                ebs_storage_gb=params.get('ec2_ebs_gb', 50),
                ebs_type="gp3"
            )]

        # Build Lambda usage
        lambda_usage = None
        if params.get('lambda_invocations'):
            lambda_usage = LambdaUsage(
                monthly_invocations=params['lambda_invocations'],
                avg_duration_ms=params.get('lambda_duration_ms', 200),
                memory_mb=params.get('lambda_memory_mb', 512)
            )

        # Build S3 usage
        s3_usage = None
        if params.get('s3_storage_gb'):
            storage_class_map = {
                'Standard': S3StorageClass.STANDARD,
                'Standard-IA': S3StorageClass.STANDARD_IA,
                'Intelligent-Tiering': S3StorageClass.INTELLIGENT_TIERING,
                'Glacier': S3StorageClass.GLACIER_INSTANT,
                'One Zone-IA': S3StorageClass.ONE_ZONE_IA
            }
            storage_class = storage_class_map.get(
                params.get('s3_storage_class', 'Standard'),
                S3StorageClass.STANDARD
            )

            s3_usage = [S3Usage(
                storage_gb=params['s3_storage_gb'],
                storage_class=storage_class,
                get_requests_monthly=params.get('s3_get_requests', 0),
                put_requests_monthly=params.get('s3_put_requests', 0)
            )]

        scenario = ComputeScenario(
            name="Custom Infrastructure",
            ec2_usage=ec2_usage,
            lambda_usage=lambda_usage,
            s3_usage=s3_usage
        )

        calculator = ComputeCalculator(scenario)
        results = calculator.calculate_total_costs()

        return {
            "monthly_cost": results['monthly_total'],
            "annual_cost": results['yearly_total'],
            "breakdown": {
                "ec2": results['breakdown']['ec2']['total_monthly'],
                "lambda": results['breakdown']['lambda']['total_monthly'],
                "s3": results['breakdown']['s3']['total_monthly']
            }
        }

    def _execute_abstract_calculator(self, params: Dict) -> Dict:
        """Execute abstract calculator generator"""
        service_code = params['service_code']
        region = params.get('region', 'us-east-1')

        generator = AbstractCalculatorGenerator(use_cache=True)

        try:
            pricing = generator.fetcher.fetch_service_pricing(service_code, region)

            # Get sample pricing
            sample_categories = list(pricing.pricing_dimensions.keys())[:5]
            sample_pricing = {}

            for category in sample_categories:
                dimensions = pricing.pricing_dimensions[category]
                if dimensions:
                    dim = dimensions[0]
                    sample_pricing[category] = {
                        'price': dim.price_per_unit,
                        'unit': dim.unit,
                        'description': dim.description[:100]
                    }

            return {
                "service": service_code,
                "region": region,
                "categories_found": len(pricing.pricing_dimensions),
                "sample_pricing": sample_pricing,
                "message": f"Found pricing for {len(pricing.pricing_dimensions)} categories"
            }
        except Exception as e:
            return {
                "error": f"Failed to fetch pricing: {str(e)}",
                "service": service_code
            }

    def process(self, user_message: str) -> str:
        """
        Process user message using Claude 3.5 Sonnet with tool calling

        Args:
            user_message: User's question about AWS costs

        Returns:
            AI-generated response with cost estimates
        """

        # Add user message to history
        self.conversation_history.append({
            "role": "user",
            "content": [{"text": user_message}]
        })

        # Call Bedrock Converse API
        try:
            response = self.bedrock.converse(
                modelId=self.config.model_id,
                messages=self.conversation_history,
                toolConfig={"tools": self.tools},
                inferenceConfig={
                    "maxTokens": self.config.max_tokens,
                    "temperature": self.config.temperature
                }
            )

            # Process response
            output_message = response['output']['message']
            stop_reason = response['stopReason']

            # Add assistant response to history
            self.conversation_history.append(output_message)

            # Check if Claude wants to use tools
            if stop_reason == 'tool_use':
                return self._handle_tool_use(output_message)

            # Otherwise return text response
            for content in output_message['content']:
                if 'text' in content:
                    return content['text']

            return "I apologize, but I couldn't generate a response."

        except Exception as e:
            return f"Error communicating with Bedrock: {str(e)}"

    def _handle_tool_use(self, message: Dict) -> str:
        """Handle tool use (function calling) from Claude"""

        tool_results = []

        # Execute all requested tools
        for content in message['content']:
            if 'toolUse' in content:
                tool_use = content['toolUse']
                tool_name = tool_use['name']
                tool_input = tool_use['input']
                tool_use_id = tool_use['toolUseId']

                # Execute the tool
                result = self._execute_tool(tool_name, tool_input)

                # Add result to tool results
                tool_results.append({
                    "toolResult": {
                        "toolUseId": tool_use_id,
                        "content": [{"json": result}]
                    }
                })

        # Send tool results back to Claude
        self.conversation_history.append({
            "role": "user",
            "content": tool_results
        })

        # Get final response from Claude
        try:
            response = self.bedrock.converse(
                modelId=self.config.model_id,
                messages=self.conversation_history,
                toolConfig={"tools": self.tools},
                inferenceConfig={
                    "maxTokens": self.config.max_tokens,
                    "temperature": self.config.temperature
                }
            )

            output_message = response['output']['message']
            self.conversation_history.append(output_message)

            # Extract text response
            for content in output_message['content']:
                if 'text' in content:
                    return content['text']

            return "I apologize, but I couldn't generate a response."

        except Exception as e:
            return f"Error getting final response: {str(e)}"

    def clear_conversation(self):
        """Clear conversation history"""
        self.conversation_history = []


def main():
    """Demo of Bedrock AI agent"""

    print("\n" + "="*60)
    print("AWS Bedrock AI Cost Agent")
    print("Using Claude 3.5 Sonnet with Tool Calling")
    print("="*60 + "\n")

    # Check for AWS credentials
    if not os.getenv('AWS_ACCESS_KEY_ID'):
        print("⚠️  AWS credentials not found!")
        print("\nPlease set the following environment variables:")
        print("  export AWS_ACCESS_KEY_ID=your_access_key")
        print("  export AWS_SECRET_ACCESS_KEY=your_secret_key")
        print("  export AWS_REGION=us-east-1")
        print("\nAnd ensure Bedrock access is enabled in your AWS account.")
        return

    try:
        agent = AWSBedrockCostAgent()

        # Demo queries
        queries = [
            "How much would it cost for a RAG system with 100 manuals and 10,000 queries per month?",
            "What's the cost for 4 t3.medium EC2 instances running 24/7?",
            "Estimate costs for 5 million Lambda invocations with 512MB memory"
        ]

        for i, query in enumerate(queries, 1):
            print(f"\n{'='*60}")
            print(f"Query {i}/{len(queries)}")
            print(f"{'='*60}\n")
            print(f"User: {query}\n")

            response = agent.process(query)
            print(f"Agent: {response}\n")

            # Clear conversation for next query
            agent.clear_conversation()

        print(f"{'='*60}")
        print("✅ Demo Complete!")
        print(f"{'='*60}\n")

    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        print("\nMake sure:")
        print("  1. AWS credentials are configured")
        print("  2. Bedrock is enabled in your region")
        print("  3. Claude 3.5 Sonnet model access is granted")
        print()


if __name__ == "__main__":
    main()
