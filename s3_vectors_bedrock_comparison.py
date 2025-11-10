#!/usr/bin/env python3
"""
Amazon S3 Vectors + Bedrock Knowledge Bases Cost Comparison
POC Scenario: 10 Service Manuals (WITHOUT Textract)
Includes new S3 Vectors feature (Preview - July 2025)
"""

from dataclasses import dataclass
from typing import Dict
import json


@dataclass
class POCScenario:
    """POC with 10 service manuals"""
    num_manuals: int = 10
    avg_pages_per_manual: int = 100
    images_per_manual: int = 50
    tables_per_manual: int = 20
    monthly_queries: int = 1000
    avg_docs_per_query: int = 5


class AWSPricing:
    """AWS Pricing (US East - Oregon, January 2025)"""

    # Claude 3.5 Sonnet
    CLAUDE_INPUT_1K = 0.003
    CLAUDE_OUTPUT_1K = 0.015

    # Titan Embeddings V2
    TITAN_EMBED_TEXT_1M = 0.02
    TITAN_EMBED_IMAGE_1K = 0.00006
    VECTOR_DIMENSIONS = 1536  # Titan V2 output dimensions

    # S3 Standard (for documents)
    S3_STORAGE_GB_MONTH = 0.023
    S3_PUT_1K = 0.005
    S3_GET_1K = 0.0004

    # S3 Vectors (NEW - Preview)
    S3_VECTORS_STORAGE_GB_MONTH = 0.06  # Vector storage
    S3_VECTORS_PUT_GB = 0.20  # Upload cost per GB of logical vector data
    S3_VECTORS_QUERY_TB_UNDER_100K = 0.004  # Per TB for first 100K vectors
    S3_VECTORS_QUERY_TB_OVER_100K = 0.002  # Per TB for >100K vectors
    S3_VECTORS_API_1K_REQUESTS = 0.0025  # API call cost

    # OpenSearch Serverless
    OPENSEARCH_OCU_HOUR = 0.24
    OPENSEARCH_STORAGE_GB_MONTH = 0.024

    # DynamoDB On-Demand
    DYNAMODB_WRITE_1M = 1.25
    DYNAMODB_READ_1M = 0.25
    DYNAMODB_STORAGE_GB = 0.25

    # RDS PostgreSQL with pgvector
    RDS_PGVECTOR_HOUR = 0.085
    RDS_STORAGE_GB_MONTH = 0.115

    # Pinecone Serverless
    PINECONE_STORAGE_GB_MONTH = 0.25
    PINECONE_READ_1M = 0.20
    PINECONE_WRITE_1M = 2.00

    # Rerank
    RERANK_1K_QUERIES = 1.00


class S3VectorsCostCalculator:
    """Calculate costs for different vector DB options"""

    def __init__(self, scenario: POCScenario):
        self.scenario = scenario
        self.pricing = AWSPricing()

    def calculate_common_costs(self) -> Dict[str, float]:
        """Costs common to all options (no Textract)"""
        s = self.scenario
        p = self.pricing

        total_pages = s.num_manuals * s.avg_pages_per_manual
        total_images = s.num_manuals * s.images_per_manual
        total_chunks = total_pages * 2

        # One-time ingestion costs (NO TEXTRACT)
        claude_vision_input = (total_images * 300 / 1000) * p.CLAUDE_INPUT_1K
        claude_vision_output = (total_images * 150 / 1000) * p.CLAUDE_OUTPUT_1K
        text_embeddings = (total_pages * 500 / 1_000_000) * p.TITAN_EMBED_TEXT_1M
        image_embeddings = (total_images * 1000 / 1000) * p.TITAN_EMBED_IMAGE_1K

        setup_cost = (claude_vision_input + claude_vision_output +
                     text_embeddings + image_embeddings)

        # S3 Storage for documents (same for all options)
        storage_gb = (
            (s.num_manuals * s.avg_pages_per_manual * 2) +  # PDFs
            (total_images * 0.5) +  # Images
            (total_chunks * 0.01)  # Chunks JSON
        ) / 1024

        s3_storage_monthly = storage_gb * p.S3_STORAGE_GB_MONTH
        s3_put_cost = (s.num_manuals + total_images + total_chunks) / 1000 * p.S3_PUT_1K

        # Monthly query costs (same for all)
        query_embeddings = (s.monthly_queries * 50 / 1_000_000) * p.TITAN_EMBED_TEXT_1M
        rerank_cost = (s.monthly_queries / 1000) * p.RERANK_1K_QUERIES

        avg_input_tokens = 100 + (s.avg_docs_per_query * 400)
        avg_output_tokens = 300
        claude_input_cost = (s.monthly_queries * avg_input_tokens / 1000) * p.CLAUDE_INPUT_1K
        claude_output_cost = (s.monthly_queries * avg_output_tokens / 1000) * p.CLAUDE_OUTPUT_1K

        s3_gets = s.monthly_queries * (s.avg_docs_per_query + 2)
        s3_get_cost = (s3_gets / 1000) * p.S3_GET_1K

        # Vector data size calculation
        # Each vector: dimensions × 4 bytes (float32)
        bytes_per_vector = p.VECTOR_DIMENSIONS * 4
        vector_data_gb = (total_chunks * bytes_per_vector) / (1024 * 1024 * 1024)

        return {
            'setup_one_time': setup_cost,
            's3_storage_monthly': s3_storage_monthly,
            's3_put_cost': s3_put_cost,
            's3_get_cost': s3_get_cost,
            'query_embeddings': query_embeddings,
            'rerank': rerank_cost,
            'claude_input': claude_input_cost,
            'claude_output': claude_output_cost,
            'storage_gb': storage_gb,
            'total_chunks': total_chunks,
            'vector_data_gb': vector_data_gb,
            'vectors_queried_monthly': s.monthly_queries * s.avg_docs_per_query
        }

    def calculate_s3_vectors_native(self, common: Dict) -> Dict:
        """NEW: S3 Vectors (native vector storage in S3)"""
        p = self.pricing

        # Setup: Upload vectors to S3
        vector_upload_cost = common['vector_data_gb'] * p.S3_VECTORS_PUT_GB

        # Monthly: Vector storage
        vector_storage_monthly = common['vector_data_gb'] * p.S3_VECTORS_STORAGE_GB_MONTH

        # Monthly: Vector queries
        # Query cost is per TB of vectors processed
        vectors_queried = common['vectors_queried_monthly']
        vector_data_queried_tb = (vectors_queried * p.VECTOR_DIMENSIONS * 4) / (1024 ** 4)

        # First 100K vectors use $0.004/TB, rest use $0.002/TB
        if vectors_queried <= 100_000:
            vector_query_cost = vector_data_queried_tb * p.S3_VECTORS_QUERY_TB_UNDER_100K
        else:
            first_100k_tb = (100_000 * p.VECTOR_DIMENSIONS * 4) / (1024 ** 4)
            remaining_tb = vector_data_queried_tb - first_100k_tb
            vector_query_cost = (first_100k_tb * p.S3_VECTORS_QUERY_TB_UNDER_100K +
                               remaining_tb * p.S3_VECTORS_QUERY_TB_OVER_100K)

        # API call costs
        api_call_cost = (self.scenario.monthly_queries / 1000) * p.S3_VECTORS_API_1K_REQUESTS

        monthly_infrastructure = (vector_storage_monthly + common['s3_storage_monthly'])
        monthly_queries = (common['query_embeddings'] + common['rerank'] +
                          common['claude_input'] + common['claude_output'] +
                          common['s3_get_cost'] + vector_query_cost + api_call_cost)

        return {
            'name': 'S3 Vectors (Native) + Bedrock KB',
            'vector_db_compute': 0,  # No compute - serverless
            'vector_db_storage': vector_storage_monthly,
            'vector_upload_cost': vector_upload_cost,
            'vector_query_cost': vector_query_cost,
            'api_call_cost': api_call_cost,
            'metadata_storage': 0,
            'monthly_infrastructure': monthly_infrastructure,
            'monthly_queries': monthly_queries,
            'monthly_total': monthly_infrastructure + monthly_queries,
            'setup_total': common['setup_one_time'] + common['s3_put_cost'] + vector_upload_cost,
            'yearly_total': (common['setup_one_time'] + common['s3_put_cost'] +
                           vector_upload_cost + (monthly_infrastructure + monthly_queries) * 12)
        }

    def calculate_opensearch_serverless(self, common: Dict) -> Dict:
        """OpenSearch Serverless costs"""
        p = self.pricing

        ocus_needed = 2
        compute_cost = ocus_needed * p.OPENSEARCH_OCU_HOUR * 730
        storage_cost = common['storage_gb'] * p.OPENSEARCH_STORAGE_GB_MONTH

        dynamodb_storage_gb = (common['total_chunks'] * 5) / (1024 * 1024)
        dynamodb_storage = dynamodb_storage_gb * p.DYNAMODB_STORAGE_GB
        dynamodb_writes = (common['total_chunks'] / 1_000_000) * p.DYNAMODB_WRITE_1M
        dynamodb_reads = (self.scenario.monthly_queries * self.scenario.avg_docs_per_query / 1_000_000) * p.DYNAMODB_READ_1M

        monthly_infrastructure = compute_cost + storage_cost + common['s3_storage_monthly'] + dynamodb_storage
        monthly_queries = (common['query_embeddings'] + common['rerank'] +
                          common['claude_input'] + common['claude_output'] +
                          common['s3_get_cost'] + dynamodb_reads)

        return {
            'name': 'OpenSearch Serverless + S3',
            'vector_db_compute': compute_cost,
            'vector_db_storage': storage_cost,
            'metadata_storage': dynamodb_storage,
            'monthly_infrastructure': monthly_infrastructure,
            'monthly_queries': monthly_queries,
            'monthly_total': monthly_infrastructure + monthly_queries,
            'setup_total': common['setup_one_time'] + common['s3_put_cost'] + dynamodb_writes,
            'yearly_total': (common['setup_one_time'] + common['s3_put_cost'] +
                           dynamodb_writes + (monthly_infrastructure + monthly_queries) * 12)
        }

    def calculate_pgvector_rds(self, common: Dict) -> Dict:
        """RDS PostgreSQL with pgvector"""
        p = self.pricing

        compute_cost = p.RDS_PGVECTOR_HOUR * 730
        total_storage_gb = common['storage_gb'] + common['vector_data_gb'] + 0.5
        storage_cost = total_storage_gb * p.RDS_STORAGE_GB_MONTH

        monthly_infrastructure = compute_cost + storage_cost + common['s3_storage_monthly']
        monthly_queries = (common['query_embeddings'] + common['rerank'] +
                          common['claude_input'] + common['claude_output'] +
                          common['s3_get_cost'])

        return {
            'name': 'RDS pgvector + S3',
            'vector_db_compute': compute_cost,
            'vector_db_storage': storage_cost,
            'metadata_storage': 0,
            'monthly_infrastructure': monthly_infrastructure,
            'monthly_queries': monthly_queries,
            'monthly_total': monthly_infrastructure + monthly_queries,
            'setup_total': common['setup_one_time'] + common['s3_put_cost'],
            'yearly_total': (common['setup_one_time'] + common['s3_put_cost'] +
                           (monthly_infrastructure + monthly_queries) * 12)
        }

    def calculate_pinecone(self, common: Dict) -> Dict:
        """Pinecone Serverless"""
        p = self.pricing

        storage_cost = common['vector_data_gb'] * p.PINECONE_STORAGE_GB_MONTH
        write_cost = (common['total_chunks'] / 1_000_000) * p.PINECONE_WRITE_1M
        read_cost_monthly = (common['vectors_queried_monthly'] / 1_000_000) * p.PINECONE_READ_1M

        monthly_infrastructure = storage_cost + common['s3_storage_monthly']
        monthly_queries = (common['query_embeddings'] + common['rerank'] +
                          common['claude_input'] + common['claude_output'] +
                          common['s3_get_cost'] + read_cost_monthly)

        return {
            'name': 'Pinecone Serverless + S3',
            'vector_db_compute': 0,
            'vector_db_storage': storage_cost,
            'metadata_storage': 0,
            'monthly_infrastructure': monthly_infrastructure,
            'monthly_queries': monthly_queries,
            'monthly_total': monthly_infrastructure + monthly_queries,
            'setup_total': common['setup_one_time'] + common['s3_put_cost'] + write_cost,
            'yearly_total': (common['setup_one_time'] + common['s3_put_cost'] +
                           write_cost + (monthly_infrastructure + monthly_queries) * 12)
        }


def format_currency(value: float) -> str:
    return f"${value:,.2f}" if value >= 0.01 else f"${value:.4f}"


def print_comparison_report(scenario: POCScenario):
    """Generate comparison report including S3 Vectors"""
    print("\n" + "="*85)
    print("COST COMPARISON: S3 VECTORS (NEW) vs OTHER VECTOR STORAGE OPTIONS")
    print("POC Scenario: 10 Service Manuals (WITHOUT Textract)")
    print("="*85 + "\n")

    print(f"📋 SCENARIO DETAILS:")
    print(f"   - Manuals: {scenario.num_manuals}")
    print(f"   - Total Pages: {scenario.num_manuals * scenario.avg_pages_per_manual:,}")
    print(f"   - Total Images: {scenario.num_manuals * scenario.images_per_manual:,}")
    print(f"   - Monthly Queries: {scenario.monthly_queries:,}")
    print(f"   - Docs per Query: {scenario.avg_docs_per_query}\n")

    calculator = S3VectorsCostCalculator(scenario)
    common = calculator.calculate_common_costs()

    print(f"📦 VECTOR DATA SIZE:")
    print(f"   - Total Chunks/Vectors: {common['total_chunks']:,}")
    print(f"   - Vector Dimensions: {calculator.pricing.VECTOR_DIMENSIONS}")
    print(f"   - Logical Vector Data: {common['vector_data_gb']:.4f} GB ({common['vector_data_gb']*1024:.2f} MB)")
    print(f"   - Vectors Queried/Month: {common['vectors_queried_monthly']:,}\n")

    # Calculate all options
    s3_vectors = calculator.calculate_s3_vectors_native(common)
    opensearch = calculator.calculate_opensearch_serverless(common)
    pgvector = calculator.calculate_pgvector_rds(common)
    pinecone = calculator.calculate_pinecone(common)

    options = [s3_vectors, opensearch, pgvector, pinecone]

    # Summary Table
    print("="*85)
    print("💰 COST SUMMARY COMPARISON")
    print("="*85 + "\n")

    print(f"{'Option':<35} {'Setup':<12} {'Monthly':<12} {'Yearly':<12} {'Savings'}")
    print("-"*85)

    baseline = opensearch

    for opt in options:
        savings = baseline['yearly_total'] - opt['yearly_total']
        savings_pct = (savings / baseline['yearly_total'] * 100) if opt != baseline else 0

        if opt == baseline:
            savings_str = "baseline"
        else:
            savings_str = f"-{savings_pct:.0f}% (${savings:,.2f})"

        print(f"{opt['name']:<35} {format_currency(opt['setup_total']):<12} "
              f"{format_currency(opt['monthly_total']):<12} "
              f"{format_currency(opt['yearly_total']):<12} {savings_str}")

    print("\n" + "="*85)
    print("📊 DETAILED BREAKDOWN: S3 VECTORS (NATIVE)")
    print("="*85 + "\n")

    opt = s3_vectors
    print(f"🆕 {opt['name'].upper()}")
    print(f"{'─'*85}")

    print(f"\n💰 Setup Costs (One-time): {format_currency(opt['setup_total'])}")
    print(f"   - Claude Vision (images): {format_currency(common['setup_one_time'])}")
    print(f"   - S3 Document uploads: {format_currency(common['s3_put_cost'])}")
    print(f"   - S3 Vector uploads: {format_currency(opt['vector_upload_cost'])} ({common['vector_data_gb']:.4f} GB × $0.20/GB)")

    print(f"\n💵 Monthly Recurring: {format_currency(opt['monthly_total'])}/month")

    print(f"\n   Infrastructure ({format_currency(opt['monthly_infrastructure'])}):")
    print(f"   - S3 Vector storage: {format_currency(opt['vector_db_storage'])} ({common['vector_data_gb']:.4f} GB × $0.06/GB)")
    print(f"   - S3 Document storage: {format_currency(common['s3_storage_monthly'])} ({common['storage_gb']:.2f} GB)")

    print(f"\n   Queries ({format_currency(opt['monthly_queries'])}):")
    print(f"   - Claude Input: {format_currency(common['claude_input'])}")
    print(f"   - Claude Output: {format_currency(common['claude_output'])}")
    print(f"   - Rerank: {format_currency(common['rerank'])}")
    print(f"   - S3 Vector queries: {format_currency(opt['vector_query_cost'])}")
    print(f"   - S3 Vector API calls: {format_currency(opt['api_call_cost'])}")
    print(f"   - Query embeddings: {format_currency(common['query_embeddings'])}")
    print(f"   - S3 GET requests: {format_currency(common['s3_get_cost'])}")

    print(f"\n📈 Annual Projection:")
    print(f"   Year 1: {format_currency(opt['yearly_total'])}")
    print(f"   Subsequent years: {format_currency(opt['monthly_total'] * 12)}/year")

    print("\n" + "="*85)
    print("🎯 RECOMMENDATIONS FOR POC (10 MANUALS, NO TEXTRACT)")
    print("="*85 + "\n")

    print(f"🏆 BEST OPTION: S3 Vectors (Native) + Bedrock Knowledge Bases")
    print(f"   - Year 1 Cost: {format_currency(s3_vectors['yearly_total'])}")
    print(f"   - Savings vs OpenSearch: {format_currency(opensearch['yearly_total'] - s3_vectors['yearly_total'])} ({(opensearch['yearly_total'] - s3_vectors['yearly_total'])/opensearch['yearly_total']*100:.0f}%)")
    print(f"   - Pros:")
    print(f"     • Fully AWS-native, integrated with Bedrock KB")
    print(f"     • No compute costs - truly serverless")
    print(f"     • Pay only for storage + queries")
    print(f"     • 90% cheaper than traditional vector DBs (AWS claim)")
    print(f"     • Preview feature - cutting edge\n")

    print(f"🥈 ALTERNATIVE: Pinecone Serverless + S3")
    print(f"   - Year 1 Cost: {format_currency(pinecone['yearly_total'])}")
    print(f"   - Savings vs OpenSearch: {format_currency(opensearch['yearly_total'] - pinecone['yearly_total'])} ({(opensearch['yearly_total'] - pinecone['yearly_total'])/opensearch['yearly_total']*100:.0f}%)")
    print(f"   - Pros: Mature product, proven at scale")
    print(f"   - Cons: External vendor, slightly more expensive\n")

    print(f"🔧 AWS-NATIVE ALTERNATIVE: RDS pgvector + S3")
    print(f"   - Year 1 Cost: {format_currency(pgvector['yearly_total'])}")
    print(f"   - Pros: Full control, all AWS")
    print(f"   - Cons: Requires managing RDS instance\n")

    print(f"❌ NOT RECOMMENDED: OpenSearch Serverless")
    print(f"   - Year 1 Cost: {format_currency(opensearch['yearly_total'])}")
    print(f"   - Why: $350/month minimum - 30x more expensive than S3 Vectors\n")

    print("="*85)
    print("💡 KEY INSIGHTS")
    print("="*85 + "\n")

    print(f"1. S3 Vectors is ~97% cheaper than OpenSearch Serverless for POCs")
    print(f"2. Vector storage cost: $0.0007/month (vs $350/month OpenSearch compute)")
    print(f"3. Most cost is in queries (Claude), not vector storage")
    print(f"4. S3 Vectors scales from POC to production seamlessly")
    print(f"5. Preview feature - expect changes before GA\n")

    # Save results
    results = {
        'scenario': vars(scenario),
        'common_costs': common,
        'options': {
            's3_vectors_native': s3_vectors,
            'opensearch_serverless': opensearch,
            'rds_pgvector': pgvector,
            'pinecone_serverless': pinecone
        }
    }

    with open('s3_vectors_bedrock_comparison.json', 'w') as f:
        json.dump(results, f, indent=2)

    print("="*85)
    print("✅ Results saved to: s3_vectors_bedrock_comparison.json")
    print("="*85 + "\n")


def main():
    scenario = POCScenario()
    print_comparison_report(scenario)


if __name__ == "__main__":
    main()
