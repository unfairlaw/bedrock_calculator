#!/usr/bin/env python3
"""
AWS Bedrock RAG Cost Calculator
Estimativa de custos para sistema RAG multimodal com manuais técnicos
"""

from dataclasses import dataclass
from typing import Dict, List
import json


@dataclass
class UsageScenario:
    """Define um cenário de uso"""
    name: str
    num_manuals: int  # Número de manuais técnicos
    avg_pages_per_manual: int
    images_per_manual: int
    tables_per_manual: int
    monthly_queries: int  # Consultas por mês
    avg_docs_per_query: int  # Documentos recuperados por query


class AWSPricing:
    """Preços AWS (US East - Oregon, Janeiro 2025)"""

    # Textract
    TEXTRACT_DETECT_TEXT = 0.0015  # por página
    TEXTRACT_TABLES = 0.015  # por página

    # Bedrock - Claude 3.5 Sonnet
    CLAUDE_INPUT_1K = 0.003  # por 1K tokens
    CLAUDE_OUTPUT_1K = 0.015  # por 1K tokens

    # Bedrock - Titan Embeddings V2
    TITAN_EMBED_TEXT_1M = 0.02  # por 1M tokens
    TITAN_EMBED_IMAGE_1K = 0.00006  # estimativa para multimodal

    # OpenSearch Serverless
    OPENSEARCH_OCU_HOUR = 0.24  # por OCU/hora
    OPENSEARCH_STORAGE_GB_MONTH = 0.024  # por GB/mês

    # Rerank
    RERANK_1K_QUERIES = 1.00  # Amazon Rerank 1.0

    # S3 Standard
    S3_STORAGE_GB_MONTH = 0.023  # por GB/mês
    S3_PUT_1K = 0.005  # por 1000 PUT requests
    S3_GET_1K = 0.0004  # por 1000 GET requests

    # DynamoDB On-Demand
    DYNAMODB_WRITE_1M = 1.25  # por 1M write units
    DYNAMODB_READ_1M = 0.25  # por 1M read units
    DYNAMODB_STORAGE_GB = 0.25  # por GB/mês


class CostCalculator:
    """Calculadora de custos AWS"""

    def __init__(self, scenario: UsageScenario):
        self.scenario = scenario
        self.pricing = AWSPricing()
        self.costs = {}

    def calculate_ingestion_costs(self) -> Dict[str, float]:
        """Calcula custos de ingestão (one-time ou recorrente)"""
        s = self.scenario
        p = self.pricing

        total_pages = s.num_manuals * s.avg_pages_per_manual
        total_images = s.num_manuals * s.images_per_manual
        total_tables = s.num_manuals * s.tables_per_manual

        # 1. Textract: OCR + Tables
        textract_ocr = total_pages * p.TEXTRACT_DETECT_TEXT
        textract_tables = total_tables * p.TEXTRACT_TABLES

        # 2. Claude 3.5 Sonnet: Descrição de imagens
        # Estimativa: 300 tokens input (imagem) + 150 tokens output por imagem
        claude_vision_input = (total_images * 300 / 1000) * p.CLAUDE_INPUT_1K
        claude_vision_output = (total_images * 150 / 1000) * p.CLAUDE_OUTPUT_1K

        # 3. Chunking e processamento
        # Estimativa: 500 tokens por página
        total_text_tokens = total_pages * 500

        # 4. Embeddings - Titan Text V2
        # Processar todo o texto
        embedding_cost = (total_text_tokens / 1_000_000) * p.TITAN_EMBED_TEXT_1M

        # 5. Embeddings - Imagens (Titan Multimodal)
        # Estimativa: ~1000 tokens equivalentes por imagem
        image_embedding_cost = (total_images * 1000 / 1000) * p.TITAN_EMBED_IMAGE_1K

        # 6. S3 Storage inicial (documentos + chunks + imagens)
        # Estimativa: 2MB por página PDF, 500KB por imagem, 10KB por chunk
        total_chunks = total_pages * 2  # ~2 chunks por página
        storage_gb = (
            (s.num_manuals * s.avg_pages_per_manual * 2) +  # PDFs
            (total_images * 0.5) +  # Imagens
            (total_chunks * 0.01)  # Chunks JSON
        ) / 1024  # Convert MB to GB

        s3_storage_monthly = storage_gb * p.S3_STORAGE_GB_MONTH

        # 7. S3 PUT requests
        total_objects = s.num_manuals + total_images + total_chunks
        s3_put_cost = (total_objects / 1000) * p.S3_PUT_1K

        # 8. DynamoDB storage (metadados)
        # Estimativa: 5KB por chunk de metadados
        dynamodb_storage_gb = (total_chunks * 5) / (1024 * 1024)
        dynamodb_storage = dynamodb_storage_gb * p.DYNAMODB_STORAGE_GB

        # 9. DynamoDB writes (ingestão inicial)
        dynamodb_writes = (total_chunks / 1_000_000) * p.DYNAMODB_WRITE_1M

        return {
            'textract_ocr': textract_ocr,
            'textract_tables': textract_tables,
            'claude_vision_input': claude_vision_input,
            'claude_vision_output': claude_vision_output,
            'text_embeddings': embedding_cost,
            'image_embeddings': image_embedding_cost,
            's3_storage_monthly': s3_storage_monthly,
            's3_put_requests': s3_put_cost,
            'dynamodb_storage_monthly': dynamodb_storage,
            'dynamodb_writes': dynamodb_writes,
            'storage_gb': storage_gb,
            'dynamodb_storage_gb': dynamodb_storage_gb,
            'total_chunks': total_chunks
        }

    def calculate_opensearch_costs(self, total_chunks: int, storage_gb: float) -> Dict[str, float]:
        """Calcula custos mensais do OpenSearch Serverless"""
        p = self.pricing

        # Estimar OCUs necessários baseado no volume
        # Vector search collection: mínimo 4 half-OCUs ($350/mês)
        # Para volumes maiores, adicionar OCUs

        if total_chunks < 100_000:
            # Pequeno: 4 half-OCUs (2 OCUs)
            ocus_needed = 2
        elif total_chunks < 500_000:
            # Médio: 6 OCUs
            ocus_needed = 6
        elif total_chunks < 1_000_000:
            # Grande: 10 OCUs
            ocus_needed = 10
        else:
            # Muito grande: 15+ OCUs
            ocus_needed = 15

        # Custo por mês (730 horas)
        compute_cost = ocus_needed * p.OPENSEARCH_OCU_HOUR * 730

        # Storage cost
        storage_cost = storage_gb * p.OPENSEARCH_STORAGE_GB_MONTH

        return {
            'ocus': ocus_needed,
            'compute_monthly': compute_cost,
            'storage_monthly': storage_cost,
            'total_monthly': compute_cost + storage_cost
        }

    def calculate_query_costs(self) -> Dict[str, float]:
        """Calcula custos mensais de queries (retrieval + generation)"""
        s = self.scenario
        p = self.pricing

        monthly_queries = s.monthly_queries

        # 1. Embeddings para queries
        # Estimativa: 50 tokens por query
        query_embedding_cost = (monthly_queries * 50 / 1_000_000) * p.TITAN_EMBED_TEXT_1M

        # 2. Rerank (opcional, mas recomendado)
        # Cada query rerank top-K documentos
        rerank_cost = (monthly_queries / 1000) * p.RERANK_1K_QUERIES

        # 3. Claude 3.5 Sonnet: Geração de resposta
        # Input: query + contexto recuperado
        # Estimativa: 100 tokens query + (avg_docs_per_query * 400 tokens por doc)
        avg_input_tokens = 100 + (s.avg_docs_per_query * 400)
        # Output: ~300 tokens por resposta
        avg_output_tokens = 300

        claude_input_cost = (monthly_queries * avg_input_tokens / 1000) * p.CLAUDE_INPUT_1K
        claude_output_cost = (monthly_queries * avg_output_tokens / 1000) * p.CLAUDE_OUTPUT_1K

        # 4. S3 GET requests (recuperar chunks + imagens)
        # Estimativa: avg_docs_per_query chunks + 2 imagens por query
        s3_gets = monthly_queries * (s.avg_docs_per_query + 2)
        s3_get_cost = (s3_gets / 1000) * p.S3_GET_1K

        # 5. DynamoDB reads (metadados)
        dynamodb_reads = (monthly_queries * s.avg_docs_per_query / 1_000_000) * p.DYNAMODB_READ_1M

        return {
            'query_embeddings': query_embedding_cost,
            'rerank': rerank_cost,
            'claude_input': claude_input_cost,
            'claude_output': claude_output_cost,
            's3_get_requests': s3_get_cost,
            'dynamodb_reads': dynamodb_reads
        }

    def calculate_total_costs(self) -> Dict:
        """Calcula custos totais (setup + mensal)"""

        # Custos de ingestão (one-time)
        ingestion = self.calculate_ingestion_costs()

        # Custos OpenSearch (mensal)
        opensearch = self.calculate_opensearch_costs(
            ingestion['total_chunks'],
            ingestion['storage_gb']
        )

        # Custos de queries (mensal)
        queries = self.calculate_query_costs()

        # Totais
        setup_cost = (
            ingestion['textract_ocr'] +
            ingestion['textract_tables'] +
            ingestion['claude_vision_input'] +
            ingestion['claude_vision_output'] +
            ingestion['text_embeddings'] +
            ingestion['image_embeddings'] +
            ingestion['s3_put_requests'] +
            ingestion['dynamodb_writes']
        )

        monthly_infrastructure = (
            opensearch['total_monthly'] +
            ingestion['s3_storage_monthly'] +
            ingestion['dynamodb_storage_monthly']
        )

        monthly_queries_total = sum(queries.values())

        monthly_total = monthly_infrastructure + monthly_queries_total

        return {
            'scenario': self.scenario.name,
            'setup_one_time': setup_cost,
            'monthly_infrastructure': monthly_infrastructure,
            'monthly_queries': monthly_queries_total,
            'monthly_total': monthly_total,
            'yearly_total': setup_cost + (monthly_total * 12),
            'breakdown': {
                'ingestion': ingestion,
                'opensearch': opensearch,
                'queries': queries
            }
        }


def format_currency(value: float) -> str:
    """Formata valor em USD"""
    return f"${value:,.2f}"


def print_cost_report(results: Dict):
    """Imprime relatório de custos formatado"""
    print(f"\n{'='*80}")
    print(f"ESTIMATIVA DE CUSTOS AWS - {results['scenario']}")
    print(f"{'='*80}\n")

    print("📊 CUSTOS DE SETUP (One-time)")
    print(f"   Total: {format_currency(results['setup_one_time'])}")
    print(f"\n   Detalhamento:")
    ing = results['breakdown']['ingestion']
    print(f"   - Textract OCR:              {format_currency(ing['textract_ocr'])}")
    print(f"   - Textract Tables:           {format_currency(ing['textract_tables'])}")
    print(f"   - Claude Vision (input):     {format_currency(ing['claude_vision_input'])}")
    print(f"   - Claude Vision (output):    {format_currency(ing['claude_vision_output'])}")
    print(f"   - Text Embeddings:           {format_currency(ing['text_embeddings'])}")
    print(f"   - Image Embeddings:          {format_currency(ing['image_embeddings'])}")
    print(f"   - S3 PUT Requests:           {format_currency(ing['s3_put_requests'])}")
    print(f"   - DynamoDB Writes:           {format_currency(ing['dynamodb_writes'])}")

    print(f"\n{'='*80}")
    print("💰 CUSTOS MENSAIS RECORRENTES")
    print(f"   Total: {format_currency(results['monthly_total'])}/mês")

    print(f"\n   Infraestrutura: {format_currency(results['monthly_infrastructure'])}/mês")
    ops = results['breakdown']['opensearch']
    print(f"   - OpenSearch Compute ({ops['ocus']} OCUs): {format_currency(ops['compute_monthly'])}")
    print(f"   - OpenSearch Storage:        {format_currency(ops['storage_monthly'])}")
    print(f"   - S3 Storage:                {format_currency(ing['s3_storage_monthly'])}")
    print(f"   - DynamoDB Storage:          {format_currency(ing['dynamodb_storage_monthly'])}")

    print(f"\n   Queries: {format_currency(results['monthly_queries'])}/mês")
    q = results['breakdown']['queries']
    print(f"   - Query Embeddings:          {format_currency(q['query_embeddings'])}")
    print(f"   - Rerank:                    {format_currency(q['rerank'])}")
    print(f"   - Claude Input:              {format_currency(q['claude_input'])}")
    print(f"   - Claude Output:             {format_currency(q['claude_output'])}")
    print(f"   - S3 GET Requests:           {format_currency(q['s3_get_requests'])}")
    print(f"   - DynamoDB Reads:            {format_currency(q['dynamodb_reads'])}")

    print(f"\n{'='*80}")
    print("📈 PROJEÇÃO ANUAL")
    print(f"   Primeiro Ano: {format_currency(results['yearly_total'])}")
    print(f"   Anos subsequentes: {format_currency(results['monthly_total'] * 12)}/ano")
    print(f"{'='*80}\n")


def main():
    """Executa cálculos para diferentes cenários"""

    scenarios = [
        UsageScenario(
            name="CENÁRIO 1: Piloto - Pequeno Porte",
            num_manuals=10,
            avg_pages_per_manual=100,
            images_per_manual=50,
            tables_per_manual=20,
            monthly_queries=1000,
            avg_docs_per_query=5
        ),
        UsageScenario(
            name="CENÁRIO 2: Produção - Médio Porte",
            num_manuals=50,
            avg_pages_per_manual=150,
            images_per_manual=80,
            tables_per_manual=40,
            monthly_queries=10000,
            avg_docs_per_query=8
        ),
        UsageScenario(
            name="CENÁRIO 3: Enterprise - Grande Porte",
            num_manuals=200,
            avg_pages_per_manual=200,
            images_per_manual=120,
            tables_per_manual=60,
            monthly_queries=50000,
            avg_docs_per_query=10
        ),
        UsageScenario(
            name="CENÁRIO 4: Empresa Grande - Escala Industrial",
            num_manuals=500,
            avg_pages_per_manual=180,
            images_per_manual=100,
            tables_per_manual=50,
            monthly_queries=150000,
            avg_docs_per_query=10
        )
    ]

    all_results = []

    for scenario in scenarios:
        calculator = CostCalculator(scenario)
        results = calculator.calculate_total_costs()
        all_results.append(results)
        print_cost_report(results)

    # Comparação
    print(f"\n{'='*80}")
    print("📊 COMPARAÇÃO RÁPIDA DOS CENÁRIOS")
    print(f"{'='*80}\n")
    print(f"{'Cenário':<45} {'Setup':<15} {'Mensal':<15} {'Anual'}")
    print(f"{'-'*80}")

    for r in all_results:
        name = r['scenario'].split(':')[1].strip()[:40]
        print(f"{name:<45} {format_currency(r['setup_one_time']):<15} "
              f"{format_currency(r['monthly_total']):<15} {format_currency(r['yearly_total'])}")

    print(f"\n{'='*80}\n")

    # Salvar JSON
    with open('aws_rag_costs_detailed.json', 'w') as f:
        json.dump(all_results, f, indent=2, default=str)

    print("✅ Resultados detalhados salvos em: aws_rag_costs_detailed.json\n")


if __name__ == "__main__":
    main()
