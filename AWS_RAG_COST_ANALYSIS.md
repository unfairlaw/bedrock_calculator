# Análise de Custos AWS - Sistema RAG Multimodal para Manuais Técnicos

**Data:** Janeiro 2025
**Região:** US East (Oregon)
**Moeda:** USD

---

## 📋 Sumário Executivo

Este documento apresenta uma análise detalhada dos custos para implementar a arquitetura RAG multimodal proposta na AWS usando Amazon Bedrock e serviços complementares.

### Resumo dos Cenários

| Cenário | Manuais | Páginas | Setup (One-time) | Mensal | Anual (Ano 1) |
|---------|---------|---------|------------------|--------|---------------|
| **Piloto** | 10 | 1.000 | $6,13 | $362,31 | $4.353,87 |
| **Produção** | 50 | 7.500 | $54,28 | $505,28 | $6.117,58 |
| **Enterprise** | 200 | 40.000 | $318,06 | $1.245,17 | $15.260,10 |
| **Industrial** | 500 | 90.000 | $672,78 | $3.732,15 | $45.458,59 |

### Principais Descobertas

1. **OpenSearch Serverless domina os custos mensais** (60-95% do total mensal)
2. **Setup inicial é relativamente baixo** (< 2% do custo anual)
3. **Custos escalam primariamente com queries**, não com volume de dados
4. **Arquitetura é viável financeiramente** mesmo para grandes volumes

---

## 🏗️ Arquitetura Analisada

```
┌─────────────────────────────────────────────────────────────┐
│                    FASE 1: INGESTÃO                         │
├─────────────────────────────────────────────────────────────┤
│ PDFs → Textract → Claude Vision → Embeddings → OpenSearch  │
│   ↓       ↓           ↓              ↓            ↓         │
│  S3    OCR+Tables  Descrições    Titan V2      Índices     │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                    FASE 2: RETRIEVAL                        │
├─────────────────────────────────────────────────────────────┤
│ Query → Embedding → OpenSearch → Rerank → Context → Claude │
│   ↓        ↓           ↓           ↓         ↓        ↓     │
│ User   Titan V2    Hybrid      Cohere    Enrich   Answer   │
└─────────────────────────────────────────────────────────────┘
```

---

## 💰 Detalhamento de Custos por Componente

### 1. Amazon Textract (Ingestão - One-time)

**Função:** Extração de texto, layout, tabelas e estrutura dos PDFs

| Operação | Preço | Uso no Cenário Enterprise |
|----------|-------|---------------------------|
| Detect Text (OCR) | $0,0015/página | $60,00 (40.000 páginas) |
| Analyze Document (Tables) | $0,015/página | $180,00 (12.000 tabelas) |

**Observações:**
- Custo proporcional ao número de páginas/tabelas
- Executado apenas uma vez por documento
- 3 meses de Free Tier (1.000 páginas/mês)

---

### 2. Amazon Bedrock - Claude 3.5 Sonnet

**Funções:**
- Descrição de imagens técnicas (visão multimodal)
- Geração de respostas RAG

| Operação | Preço | Uso Enterprise (mensal) |
|----------|-------|-------------------------|
| **Ingestão (Vision):** | | |
| Input (imagens) | $0,003/1K tokens | $21,60 (24.000 imagens × 300 tokens) |
| Output (descrições) | $0,015/1K tokens | $54,00 (24.000 × 150 tokens) |
| **Queries (RAG):** | | |
| Input (contexto) | $0,003/1K tokens | $615/mês (50K queries × ~4.100 tokens) |
| Output (respostas) | $0,015/1K tokens | $225/mês (50K queries × 300 tokens) |

**Otimizações Disponíveis:**
- **Batch Mode:** 50% desconto (não aplicável para queries em tempo real)
- **Prompt Caching:** $0,0006/1K tokens para cache hits (90% desconto)
  - Ideal para contextos repetidos (seções de manuais)
  - Pode reduzir custos de input em 40-60%

---

### 3. Amazon Bedrock - Titan Embeddings V2

**Função:** Converter texto e queries em vetores para busca semântica

| Operação | Preço | Uso Enterprise (mensal) |
|----------|-------|-------------------------|
| **Ingestão:** | | |
| Text Embeddings | $0,02/1M tokens | $0,40 (20M tokens) |
| Image Embeddings | $0,00006/1K tokens | $1,44 (24.000 imagens) |
| **Queries:** | | |
| Query Embeddings | $0,02/1M tokens | $0,05 (50K queries × 50 tokens) |

**Observações:**
- Embeddings são extremamente baratos
- Não há custo para armazenar embeddings (apenas vetores em OpenSearch)
- Batch mode disponível para 50% desconto

---

### 4. Amazon OpenSearch Serverless ⚠️ MAIOR CUSTO

**Função:** Armazenamento de vetores, busca híbrida (semântica + keywords), filtros

| Componente | Preço | Uso Enterprise |
|------------|-------|----------------|
| **Compute (OCU)** | $0,24/OCU/hora | $350,40/mês (2 OCUs × 730h) |
| **Storage** | $0,024/GB/mês | $2,18/mês (~91 GB) |

**Dimensionamento de OCUs:**

| Volume | Chunks | OCUs | Custo Mensal |
|--------|--------|------|--------------|
| Pequeno | < 100K | 2 | $350 |
| Médio | 100K-500K | 6 | $1.051 |
| Grande | 500K-1M | 10 | $1.752 |
| Muito Grande | > 1M | 15+ | $2.628+ |

**Por que OpenSearch Serverless é caro?**
- Mínimo de 4 half-OCUs (~$350/mês) para vector search
- Compute é sempre-on (não escala a zero)
- Separação de OCUs para vector search vs time-series/search

**Alternativas Mais Econômicas:**
1. **OpenSearch Managed (provisionado):** ~$150-250/mês para clusters pequenos
2. **Pinecone:** $70-100/mês para ~100K vetores
3. **Amazon Neptune ML:** Preços competitivos para grafos + vetores
4. **pgvector (RDS/Aurora):** $50-150/mês para workloads menores

---

### 5. Amazon S3

**Função:** Armazenamento de PDFs originais, chunks processados, imagens extraídas

| Operação | Preço | Uso Enterprise |
|----------|-------|----------------|
| Storage (Standard) | $0,023/GB/mês | $2,08/mês (~91 GB) |
| PUT Requests | $0,005/1K | $0,52 (ingestão) |
| GET Requests | $0,0004/1K | $0,24/mês (50K queries × 12 objetos) |

**Otimizações:**
- S3 Intelligent-Tiering: economia automática de 40-70% para dados raramente acessados
- Compressão de chunks JSON: redução de 60-80% do tamanho

---

### 6. Amazon DynamoDB

**Função:** Metadados, índices reversos, mapeamento chunk-documento

| Operação | Preço | Uso Enterprise |
|----------|-------|----------------|
| Storage | $0,25/GB/mês | $0,10/mês (~400 MB) |
| Write Units | $1,25/1M | $0,10 (ingestão) |
| Read Units | $0,25/1M | $0,12/mês (50K queries) |

**Alternativa:** DynamoDB On-Demand é ideal para padrões imprevisíveis

---

### 7. Amazon Rerank (Bedrock)

**Função:** Reordenação de resultados para melhorar relevância

| Modelo | Preço | Uso Enterprise |
|--------|-------|----------------|
| Amazon Rerank 1.0 | $1,00/1K queries | $50/mês (50K queries) |

**Observações:**
- Cada query pode reranquear até 100 documentos
- Se exceder 100 docs, conta como múltiplas queries
- Cohere Rerank 3.5 também disponível (preço a confirmar)

---

## 📊 Cenários Detalhados

### Cenário 1: Piloto - Pequeno Porte

**Perfil:**
- 10 manuais técnicos
- ~100 páginas/manual (1.000 páginas totais)
- 50 imagens/manual (500 imagens)
- 20 tabelas/manual (200 tabelas)
- 1.000 queries/mês (~33/dia)

**Custos:**
- **Setup:** $6,13
- **Mensal:** $362,31
  - OpenSearch: $350,40 (97%)
  - Queries: $11,81 (3%)
- **Anual (Ano 1):** $4.353,87

**Caso de Uso:** POC, validação de tecnologia, área específica

---

### Cenário 2: Produção - Médio Porte

**Perfil:**
- 50 manuais
- ~150 páginas/manual (7.500 páginas)
- 80 imagens/manual (4.000 imagens)
- 40 tabelas/manual (2.000 tabelas)
- 10.000 queries/mês (~330/dia)

**Custos:**
- **Setup:** $54,28
- **Mensal:** $505,28
  - OpenSearch: $351,21 (69%)
  - Queries: $154,07 (31%)
- **Anual (Ano 1):** $6.117,58

**Caso de Uso:** Departamento, planta industrial, múltiplas equipes

---

### Cenário 3: Enterprise - Grande Porte

**Perfil:**
- 200 manuais
- ~200 páginas/manual (40.000 páginas)
- 120 imagens/manual (24.000 imagens)
- 60 tabelas/manual (12.000 tabelas)
- 50.000 queries/mês (~1.667/dia)

**Custos:**
- **Setup:** $318,06
- **Mensal:** $1.245,17
  - OpenSearch: $354,75 (28%)
  - Queries: $890,41 (72%)
- **Anual (Ano 1):** $15.260,10

**Caso de Uso:** Empresa média-grande, múltiplas plantas, suporte 24/7

---

### Cenário 4: Escala Industrial

**Perfil:**
- 500 manuais
- ~180 páginas/manual (90.000 páginas)
- 100 imagens/manual (50.000 imagens)
- 50 tabelas/manual (25.000 tabelas)
- 150.000 queries/mês (~5.000/dia)

**Custos:**
- **Setup:** $672,78
- **Mensal:** $3.732,15
  - OpenSearch: $1.060,91 (28%)
  - Queries: $2.671,24 (72%)
- **Anual (Ano 1):** $45.458,59

**Caso de Uso:** Multinacional, dezenas de plantas, milhares de usuários

---

## 🎯 Estratégias de Otimização de Custos

### 1. **OpenSearch Serverless → Alternativas** 💰 ALTO IMPACTO

**Problema:** OpenSearch Serverless tem custo fixo alto ($350-1.000/mês)

**Soluções:**

#### a) OpenSearch Managed (Provisionado)
```yaml
Configuração:
  - Instâncias: 2x t3.small.search ($0.036/hora)
  - Storage: 100 GB GP3

Custo: ~$52/mês (compute) + $10/mês (storage) = $62/mês
Economia: 82% vs Serverless
```

**Trade-offs:**
- Precisa gerenciar capacity planning
- Menos elástico
- Ideal para workloads previsíveis

#### b) Pinecone (SaaS)
```yaml
Plano Standard:
  - 100K vetores 1024-dim
  - Custo: $70/mês

Plano Enterprise:
  - 500K vetores
  - Custo: ~$200-300/mês
```

**Vantagens:**
- Mais barato que OpenSearch Serverless
- Gerenciamento simplificado
- Boa performance

#### c) pgvector no RDS/Aurora
```yaml
Aurora Serverless v2:
  - Min: 0.5 ACU, Max: 8 ACU
  - Custo: $43-350/mês (baseado em uso)

RDS PostgreSQL:
  - db.t3.medium
  - Custo: ~$62/mês
```

**Vantagens:**
- Mais barato para workloads menores
- Integração fácil com aplicações
- Escala a zero (Aurora Serverless)

**Quando usar cada opção:**
- **< 100K vetores:** pgvector (RDS) ou Pinecone
- **100K-500K vetores:** Pinecone ou OpenSearch Managed
- **> 500K vetores:** OpenSearch Serverless ou Pinecone Enterprise

---

### 2. **Claude 3.5 Sonnet com Prompt Caching** 💰 MÉDIO IMPACTO

**Problema:** Queries repetem contexto de seções de manuais frequentes

**Solução:** Habilitar Prompt Caching
```python
# Exemplo de uso
response = bedrock_client.invoke_model(
    modelId='anthropic.claude-3-5-sonnet-v2',
    body={
        'messages': [...],
        'system': [{
            'text': '... contexto do manual ...',
            'cache_control': {'type': 'ephemeral'}  # Cache habilitado
        }]
    }
)
```

**Economia Potencial:**
- Cache write: $0,0075/1K tokens (primeira vez)
- Cache read: $0,0006/1K tokens (80% desconto vs $0,003)
- **Economia típica: 40-60% nos custos de input do Claude**

**Cenário Enterprise:**
- Sem cache: $615/mês (input)
- Com cache (50% hit rate): $308 input + $77 cache = $385/mês
- **Economia: $230/mês (37%)**

---

### 3. **Batch Processing para Ingestão** 💰 BAIXO IMPACTO

**Problema:** Ingestão é processada em tempo real

**Solução:** Usar batch mode do Bedrock
- Claude batch: 50% desconto
- Titan batch: 50% desconto

**Economia Potencial:**
```
Setup Enterprise (sem batch): $318
Setup Enterprise (com batch): $238 (-25%)

Economia: $80 one-time
```

**Trade-off:** Ingestão leva mais tempo (horas vs minutos)

---

### 4. **Chunking e Retrieval Otimizado** 💰 MÉDIO IMPACTO

**Problema:** Recuperar muitos documentos aumenta custos de input do Claude

**Soluções:**

#### a) Reduzir avg_docs_per_query
```
Enterprise atual: 10 docs/query
Enterprise otimizado: 6 docs/query

Economia Claude input:
  - Antes: $615/mês
  - Depois: $390/mês
  - Economia: $225/mês (37%)
```

**Como:**
- Melhorar qualidade dos embeddings
- Usar rerank mais agressivamente
- Filtros de metadados mais precisos

#### b) Hierarchical Retrieval
```python
# Primeiro: busca rápida com resumos (poucos tokens)
summaries = search_summaries(query, top_k=20)

# Depois: retrieval detalhado apenas do melhor candidato
detailed_chunks = get_detailed_chunks(summaries[0])
```

**Economia:** 50-70% de tokens no Claude

---

### 5. **Compressão e S3 Tiering** 💰 BAIXO IMPACTO

**Problema:** Chunks JSON ocupam muito espaço

**Soluções:**

#### a) Compressão GZIP
```python
import gzip

chunk_json = json.dumps(chunk)
compressed = gzip.compress(chunk_json.encode())

# Redução típica: 60-80%
```

#### b) S3 Intelligent-Tiering
```bash
aws s3api put-bucket-intelligent-tiering-configuration \
  --bucket my-rag-bucket \
  --id auto-tier
```

**Economia:**
- PDFs raramente acessados: 40-70% desconto
- Chunks antigos: movidos para Glacier

**Economia típica:** $1-5/mês (baixo impacto)

---

### 6. **Rerank Seletivo** 💰 MÉDIO IMPACTO

**Problema:** Rerank todas queries custa $1/1K

**Solução:** Reranking condicional
```python
def should_rerank(query_complexity, results_confidence):
    # Apenas rerank queries complexas ou resultados ambíguos
    if query_complexity > threshold or results_confidence < 0.8:
        return True
    return False

# Rerank apenas 30% das queries
if should_rerank(query, initial_results):
    results = rerank(query, initial_results)
```

**Economia:**
- Enterprise: $50/mês → $15/mês (70% economia)
- Trade-off: Qualidade ligeiramente menor em queries simples

---

### 7. **Reserved Capacity (Longo Prazo)** 💰 ALTO IMPACTO

**Problema:** On-demand tem preços premium

**Solução:** Provisioned Throughput do Bedrock
- Commits de 1 mês ou 6 meses
- Descontos de 30-50% para throughput garantido
- Ideal para workloads previsíveis

**Quando usar:**
- Queries > 10K/mês consistentes
- Budget aprovado para 6+ meses
- ROI claro

**Economia potencial:** $200-500/mês em cenários grandes

---

## 💡 Recomendações por Cenário

### Piloto (< $500/mês)

**Otimizações prioritárias:**
1. ✅ Usar RDS pgvector ao invés de OpenSearch ($300/mês economia)
2. ✅ Desabilitar rerank (economia $1/mês)
3. ✅ Batch processing na ingestão

**Custo otimizado:** ~$60/mês (83% economia)

---

### Produção ($500-1.500/mês)

**Otimizações prioritárias:**
1. ✅ Pinecone ao invés de OpenSearch Serverless ($250/mês economia)
2. ✅ Prompt caching no Claude ($100/mês economia)
3. ✅ Reduzir docs/query para 6 ($50/mês economia)

**Custo otimizado:** ~$300/mês (40% economia)

---

### Enterprise ($1.500-5.000/mês)

**Otimizações prioritárias:**
1. ✅ OpenSearch Managed ao invés de Serverless ($300/mês economia)
2. ✅ Prompt caching + hierarchical retrieval ($400/mês economia)
3. ✅ Rerank seletivo ($35/mês economia)
4. ✅ S3 Intelligent-Tiering + compressão ($20/mês economia)

**Custo otimizado:** ~$490/mês (61% economia)

---

### Industrial (> $5.000/mês)

**Otimizações prioritárias:**
1. ✅ OpenSearch Serverless otimizado (disk-based vectors)
2. ✅ Provisioned Throughput Bedrock ($500/mês economia)
3. ✅ Todas otimizações anteriores ($1.000/mês economia total)
4. ✅ Considerar infra híbrida (self-hosted vector DB)

**Custo otimizado:** ~$2.200/mês (41% economia)

---

## 📈 Comparação: AWS vs Self-Hosted

### AWS Bedrock (Managed)

**Vantagens:**
- Zero setup de infraestrutura
- Escalabilidade automática
- Modelos state-of-the-art (Claude, Titan)
- Segurança e compliance built-in
- Time-to-market rápido

**Desvantagens:**
- Custos recorrentes
- Vendor lock-in parcial
- Menos controle sobre modelos

---

### Self-Hosted (EC2 + Open Source)

**Stack exemplo:**
```yaml
Compute:
  - EC2 g4dn.xlarge (GPU): $0.526/hora = $383/mês
  - EC2 t3.large (API): $0.0832/hora = $61/mês

Storage:
  - EBS gp3 500GB: $40/mês

Vector DB:
  - Milvus/Qdrant (self-hosted no EC2)

Models:
  - Llama 3 70B ou Mixtral 8x7B
  - BGE embeddings (gratuito)

Total: ~$484/mês
```

**Vantagens:**
- Custos fixos (não escalam com queries)
- Controle total sobre modelos
- Customização ilimitada
- Sem custos de API calls

**Desvantagens:**
- Complexidade operacional alta
- Qualidade inferior (Llama vs Claude)
- Custos de DevOps/MLOps
- Responsabilidade por segurança

---

### Recomendação por Porte

| Porte | Recomendação | Razão |
|-------|--------------|-------|
| Piloto | AWS Bedrock | TTM rápido, baixo risco |
| Produção | AWS Bedrock | Melhor ROI, qualidade garantida |
| Enterprise | AWS Bedrock | Compliance, escalabilidade |
| Industrial | Híbrido | AWS + alguns modelos self-hosted |

---

## 🔍 Fatores de Custo Não Incluídos

Esta análise foca nos custos diretos de serviços AWS. **Não estão incluídos:**

### 1. Custos de Desenvolvimento
- Engenharia de software: $80K-150K/ano (1-2 devs)
- Data Science/ML: $100K-180K/ano (opcional)
- DevOps: $90K-140K/ano (0.5 FTE)

**Total:** $170K-470K/ano dependendo da equipe

---

### 2. Custos de Manutenção
- Atualização de documentos: 2-4 horas/mês
- Monitoring e alertas: Cloudwatch (~$50/mês)
- Retraining/fine-tuning (se aplicável)
- Suporte operacional

**Total:** $5K-20K/ano

---

### 3. Custos de Rede
- Data Transfer Out: $0.09/GB (após 100GB/mês)
- CloudFront (se aplicável): $0.085/GB
- VPC endpoints: $0.01/GB

**Estimativa:** $20-200/mês dependendo do tráfego

---

### 4. Compliance e Segurança
- AWS WAF: $5/mês + $1/milhão requests
- AWS Shield: $3.000/mês (Advanced)
- KMS: $1/key/mês + $0.03/10K requests
- Logs e auditoria: CloudTrail, Config

**Estimativa:** $50-500/mês

---

## ✅ Checklist de Implementação

### Fase 1: Setup Inicial (Semanas 1-2)

- [ ] Provisionar conta AWS e IAM roles
- [ ] Habilitar Bedrock models (Claude, Titan)
- [ ] Escolher vector database (OpenSearch vs alternativas)
- [ ] Configurar S3 buckets com lifecycle policies
- [ ] Setup DynamoDB tables
- [ ] Implementar pipeline de ingestão básico
- [ ] Processar 1-2 manuais de teste

**Custo estimado:** $100-500 (setup + testes)

---

### Fase 2: POC (Semanas 3-4)

- [ ] Processar 10 manuais completos
- [ ] Implementar retrieval híbrido
- [ ] Adicionar rerank
- [ ] Criar interface de teste
- [ ] Validar qualidade das respostas
- [ ] Medir latências

**Custo estimado:** $500-1.000

---

### Fase 3: Otimização (Semanas 5-6)

- [ ] Implementar prompt caching
- [ ] Otimizar chunking strategy
- [ ] Adicionar filtros de metadados
- [ ] Testar diferentes valores de top-K
- [ ] Benchmark vector databases
- [ ] Configurar monitoring

**Custo estimado:** $500-1.000

---

### Fase 4: Produção (Semanas 7-8)

- [ ] Processar biblioteca completa de manuais
- [ ] Configurar auto-scaling
- [ ] Implementar backup/disaster recovery
- [ ] Documentação técnica
- [ ] Treinamento de usuários
- [ ] Go-live

**Custo estimado:** Varia por cenário

---

## 🎓 Lições Aprendidas (Boas Práticas)

### 1. Start Small, Scale Smart
- Comece com 5-10 manuais
- Valide qualidade antes de processar tudo
- Invista em boas métricas desde o início

### 2. Embeddings são Baratos, OpenSearch é Caro
- Não economize em qualidade de embeddings
- Invista tempo escolhendo o vector DB certo
- Considere alternativas ao OpenSearch Serverless para < 500K vetores

### 3. Prompt Engineering > Mais Contexto
- 6 chunks bem selecionados > 10 chunks medianos
- Use rerank, não aumente cegamente top-K
- Metadados bem estruturados reduzem custos

### 4. Monitore Token Usage Religiosamente
- Configure alertas no CloudWatch
- Track custos por query type
- Identifique outliers (queries caras)

### 5. Cache é Seu Amigo
- Prompt caching do Claude: 80% desconto
- Embeddings caching: evite reprocessar queries comuns
- CDN para imagens estáticas

---

## 📞 Próximos Passos

### Imediato
1. **Validar premissas** com seus dados reais
2. **Rodar calculadora** com números específicos
3. **POC com 5 manuais** para validar arquitetura

### Curto Prazo (1-3 meses)
1. Implementar pipeline completo
2. Benchmark diferentes vector databases
3. Otimizar custos com técnicas descritas

### Médio Prazo (3-6 meses)
1. Expandir para biblioteca completa
2. Implementar features avançadas (multi-hop, citations)
3. Considerar fine-tuning de embeddings

---

## 🔗 Recursos Úteis

### Documentação Oficial
- [AWS Bedrock Pricing](https://aws.amazon.com/bedrock/pricing/)
- [OpenSearch Serverless Pricing](https://aws.amazon.com/opensearch-service/pricing/)
- [Textract Pricing](https://aws.amazon.com/textract/pricing/)
- [Claude Prompt Caching](https://docs.anthropic.com/claude/docs/prompt-caching)

### Ferramentas
- [AWS Pricing Calculator](https://calculator.aws/)
- [Bedrock Pricing Calculator](https://calculator.aws/#/addService/Bedrock)
- Script Python incluído: `aws_rag_cost_calculator.py`

### Benchmarks
- [OpenSearch vs Pinecone vs pgvector](https://benchmarks.vectorview.ai/)
- [RAG Cost Optimization Guide](https://www.anthropic.com/research/rag-optimization)

---

## 📊 Anexo: Fórmulas de Cálculo

### Tokens Estimados
```python
# Texto
tokens_per_page = 500  # ~2000 caracteres/página ÷ 4

# Imagens (Claude vision)
tokens_per_image_input = 300
tokens_per_image_output = 150

# Query context
tokens_per_chunk = 400
query_tokens = 100
response_tokens = 300
```

### Storage Estimado
```python
# S3
pdf_size_mb = 2  # por página
image_size_mb = 0.5
chunk_size_kb = 10

# DynamoDB
metadata_per_chunk_kb = 5
```

### OCUs OpenSearch
```python
def estimate_ocus(num_chunks, qps):
    """
    num_chunks: número de chunks indexados
    qps: queries per second
    """
    if num_chunks < 100_000 and qps < 5:
        return 2  # mínimo
    elif num_chunks < 500_000 and qps < 10:
        return 6
    elif num_chunks < 1_000_000 and qps < 20:
        return 10
    else:
        return 15 + (qps // 10)
```

---

## 📝 Notas Finais

**Importante:**
- Preços são de Janeiro 2025 e podem variar
- Sempre consulte a [calculadora oficial AWS](https://calculator.aws/)
- Considere custos de rede, compliance e operação
- ROI depende fortemente da qualidade das respostas

**Contato para dúvidas:**
- Abra uma issue no repositório
- Consulte a documentação AWS Bedrock
- Entre em contato com AWS Solutions Architects

---

**Última atualização:** 2025-01-07
**Versão do documento:** 1.0
