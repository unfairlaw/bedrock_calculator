# Guia Completo: PC para Executar e Fine-Tunar LLMs com Ollama no Brasil (2025)

## Índice
1. [Requisitos de Hardware](#requisitos-de-hardware)
2. [Configurações Recomendadas](#configurações-recomendadas)
3. [Componentes Detalhados](#componentes-detalhados)
4. [Onde Comprar no Brasil](#onde-comprar-no-brasil)
5. [Custos Estimados](#custos-estimados)
6. [Considerações de Performance](#considerações-de-performance)

---

## Requisitos de Hardware

### Para Executar LLMs com Ollama

#### VRAM/GPU Mínima por Tamanho de Modelo:
- **Modelos 3B-7B**: 8GB VRAM (ex: RTX 4060)
- **Modelos 13B**: 16GB VRAM (ex: RTX 4060 Ti 16GB, RTX 4070 Ti Super)
- **Modelos 70B**: 24GB+ VRAM (ex: RTX 4090, RTX A6000)

#### RAM do Sistema:
- **Modelos 7B**: Mínimo 16GB RAM (recomendado 32GB)
- **Modelos 13B**: Mínimo 32GB RAM
- **Modelos 70B**: Mínimo 64GB RAM

#### Regra Geral:
O modelo deve ser pelo menos **2x menor** que a RAM disponível e ocupar **⅔ da VRAM** disponível.

**Exemplo**: Modelo 8GB requer 16GB RAM e 12GB VRAM

#### Quantização (Redução de Memória):
- **4-bit (Q4_K_M)**: Reduz requisitos em ~4x
  - Llama 3.1 8B → ~5GB
  - Llama 3 70B → ~35GB (viável em RTX 4090 24GB)
- **8-bit**: Reduz requisitos em ~2x

### Para Fine-Tuning de LLMs

#### Full Fine-Tuning:
- **Modelo 7B**: 100-120GB VRAM (múltiplas GPUs A100/H100)
- **Inviável para hardware consumer**

#### LoRA (Low-Rank Adaptation):
- **Modelo 7B**: 12-24GB VRAM
  - Viável: RTX 4090, RTX 4080 Super, L40S
- **Modelo 13B**: 24GB+ VRAM
  - Requer: RTX 4090 ou superior

#### QLoRA (Quantized LoRA):
- **Modelo 7B**: 8GB VRAM (RTX 4060 Ti, RTX 4070)
- **Modelo 13B**: 12-16GB VRAM (RTX 4060 Ti 16GB, RTX 4070 Ti)
- **95-99% da performance** do full fine-tune

---

## Configurações Recomendadas

### 🟢 CONFIGURAÇÃO ENTRY-LEVEL (R$ 12.000 - R$ 15.000)
**Ideal para**: Modelos até 7B-13B, fine-tuning com QLoRA

| Componente | Especificação | Preço Estimado |
|------------|---------------|----------------|
| **GPU** | NVIDIA RTX 4060 Ti 16GB | R$ 3.000 - R$ 3.500 |
| **CPU** | AMD Ryzen 7 7700X (8-core) | R$ 1.800 - R$ 2.200 |
| **Motherboard** | ASRock B650M PG Riptide | R$ 1.400 - R$ 1.600 |
| **RAM** | 32GB DDR5 (2x16GB) 6000MHz | R$ 1.800 - R$ 2.000 |
| **Storage** | 1TB NVMe Gen4 SSD | R$ 500 - R$ 700 |
| **PSU** | 750W 80+ Gold Full Modular | R$ 600 - R$ 800 |
| **Case** | Mid Tower com boa ventilação | R$ 300 - R$ 500 |
| **Cooler CPU** | Torre média/AIO 240mm | R$ 300 - R$ 500 |

**Capacidades**:
- ✅ Executar modelos até 13B com quantização
- ✅ Fine-tuning de modelos 7B com QLoRA
- ✅ Desenvolvimento e testes de IA
- ⚠️ Limitado para modelos 70B (quantização agressiva necessária)

---

### 🟡 CONFIGURAÇÃO INTERMEDIÁRIA (R$ 18.000 - R$ 22.000)
**Ideal para**: Modelos até 13B, fine-tuning com LoRA/QLoRA

| Componente | Especificação | Preço Estimado |
|------------|---------------|----------------|
| **GPU** | NVIDIA RTX 4070 Ti Super 16GB | R$ 5.500 - R$ 6.500 |
| **CPU** | AMD Ryzen 9 7900X (12-core) | R$ 2.500 - R$ 3.000 |
| **Motherboard** | ASUS B650E-F Gaming | R$ 2.000 - R$ 2.400 |
| **RAM** | 64GB DDR5 (2x32GB) 6000MHz | R$ 4.000 - R$ 4.500 |
| **Storage** | 2TB NVMe Gen4 SSD | R$ 900 - R$ 1.200 |
| **PSU** | 850W 80+ Gold Full Modular PCIe 5.0 | R$ 800 - R$ 1.000 |
| **Case** | Mid/Full Tower premium | R$ 500 - R$ 800 |
| **Cooler CPU** | AIO 280mm/360mm | R$ 600 - R$ 900 |

**Capacidades**:
- ✅ Executar modelos até 13B confortavelmente
- ✅ Fine-tuning de modelos 7B-13B com LoRA
- ✅ Modelos 70B com quantização 4-bit
- ✅ Desenvolvimento profissional de IA
- ⚠️ Limitado para fine-tuning de modelos 70B

---

### 🔴 CONFIGURAÇÃO PROFISSIONAL (R$ 30.000 - R$ 38.000)
**Ideal para**: Todos os modelos, incluindo 70B, fine-tuning avançado

| Componente | Especificação | Preço Estimado |
|------------|---------------|----------------|
| **GPU** | NVIDIA RTX 4090 24GB | R$ 12.000 - R$ 14.000 |
| **CPU** | AMD Ryzen 9 7950X (16-core) | R$ 3.500 - R$ 4.000 |
| **Motherboard** | ASUS X670E ROG Strix | R$ 3.000 - R$ 3.500 |
| **RAM** | 128GB DDR5 (4x32GB) 6000MHz | R$ 8.000 - R$ 9.000 |
| **Storage** | 2TB NVMe Gen4 (sistema) + 2TB Gen4 (dados) | R$ 1.800 - R$ 2.400 |
| **PSU** | 1000W 80+ Platinum Full Modular PCIe 5.0 | R$ 1.200 - R$ 1.500 |
| **Case** | Full Tower com excelente airflow | R$ 800 - R$ 1.200 |
| **Cooler CPU** | AIO 360mm premium | R$ 900 - R$ 1.300 |

**Capacidades**:
- ✅ Executar modelos até 70B (com quantização leve)
- ✅ Fine-tuning de modelos até 13B com LoRA
- ✅ Fine-tuning de modelos 7B-13B full precision
- ✅ Múltiplos modelos simultâneos
- ✅ Produção profissional de IA
- ⚠️ Modelos 70B+ full precision requerem GPUs enterprise

---

### 🟣 CONFIGURAÇÃO ENTERPRISE (R$ 45.000+)
**Ideal para**: Produção empresarial, múltiplas GPUs, modelos gigantes

| Componente | Especificação | Preço Estimado |
|------------|---------------|----------------|
| **GPU** | 2x NVIDIA RTX 4090 24GB | R$ 24.000 - R$ 28.000 |
| **CPU** | AMD Ryzen Threadripper 7960X (24-core) | R$ 8.000 - R$ 10.000 |
| **Motherboard** | TRX50 com suporte multi-GPU | R$ 4.000 - R$ 5.000 |
| **RAM** | 256GB DDR5 (8x32GB) ECC | R$ 16.000 - R$ 18.000 |
| **Storage** | 4TB NVMe Gen4 (sistema) + 8TB NVMe (dados) | R$ 4.000 - R$ 5.000 |
| **PSU** | 1600W 80+ Titanium Full Modular | R$ 2.500 - R$ 3.000 |
| **Case** | Workstation chassis com suporte multi-GPU | R$ 1.500 - R$ 2.000 |
| **Cooler CPU** | AIO 420mm ou custom loop | R$ 1.500 - R$ 3.000 |

**Capacidades**:
- ✅ 48GB VRAM total (combinado)
- ✅ Executar modelos 70B+ sem quantização
- ✅ Fine-tuning de modelos até 30B com full precision
- ✅ Múltiplos usuários/experimentos simultâneos
- ✅ Ambiente de produção empresarial

---

## Componentes Detalhados

### GPUs NVIDIA (Disponíveis no Brasil - 2025)

#### Série RTX 40 (Ada Lovelace):

| Modelo | VRAM | CUDA Cores | Bandwidth | Preço (R$) | Uso Recomendado |
|--------|------|------------|-----------|------------|-----------------|
| RTX 4060 | 8GB | 3072 | 272 GB/s | 1.800-2.200 | Modelos 7B apenas |
| RTX 4060 Ti 8GB | 8GB | 4352 | 288 GB/s | 2.400-2.800 | Modelos 7B |
| RTX 4060 Ti 16GB | 16GB | 4352 | 288 GB/s | 3.000-3.500 | **Melhor custo-benefício 13B** |
| RTX 4070 | 12GB | 5888 | 504 GB/s | 3.800-4.400 | **Ótimo custo-benefício geral** |
| RTX 4070 Ti Super | 16GB | 8448 | 672 GB/s | 5.500-6.500 | Modelos 13B + fine-tuning |
| RTX 4080 Super | 16GB | 10240 | 736 GB/s | 7.300-9.600 | Alto desempenho 13B |
| RTX 4090 | 24GB | 16384 | 1008 GB/s | 12.000-14.000 | **Melhor consumer 70B** |

#### Série RTX 50 (Blackwell) - Lançamento 2025:

| Modelo | VRAM | MSRP USD | Preço Estimado BR | Disponibilidade |
|--------|------|----------|-------------------|-----------------|
| RTX 5070 | 12GB | $549 | R$ 4.000-5.000 | Q2 2025 |
| RTX 5070 Ti | 16GB | $749 | R$ 5.500-6.500 | Q2 2025 |
| RTX 5080 | 16GB | $999 | R$ 7.500-9.000 | Q1 2025 |
| RTX 5090 | 32GB | $1,999 | R$ 15.000-18.000 | Q1 2025 |

⚠️ **Nota**: Escassez de estoque e scalping podem elevar preços significativamente no lançamento.

### CPUs Recomendadas

#### AMD Ryzen (Socket AM5):

| Modelo | Cores/Threads | Base/Boost | Preço (R$) | Uso Recomendado |
|--------|---------------|------------|------------|-----------------|
| Ryzen 7 7700X | 8C/16T | 4.5/5.4 GHz | 1.800-2.200 | Entry-level |
| Ryzen 7 7800X3D | 8C/16T | 4.2/5.0 GHz | 2.500-3.000 | Gaming + IA |
| Ryzen 9 7900X | 12C/24T | 4.7/5.4 GHz | 2.500-3.000 | **Melhor custo-benefício** |
| Ryzen 9 7950X | 16C/32T | 4.5/5.7 GHz | 3.500-4.000 | Alto desempenho |
| Threadripper 7960X | 24C/48T | 4.2/5.3 GHz | 8.000-10.000 | Workstation/Enterprise |

#### Intel Core (Socket LGA1700/1851):

| Modelo | Cores (P+E) | Base/Boost | Preço (R$) | Uso Recomendado |
|--------|-------------|------------|------------|-----------------|
| i7-14700K | 20C (8P+12E) | 3.4/5.6 GHz | 2.500-3.000 | Intermediário |
| i9-14900K | 24C (8P+16E) | 3.2/6.0 GHz | 4.000-4.500 | Alto desempenho |

**Recomendação**: AMD Ryzen oferece melhor custo-benefício para cargas de trabalho de IA em 2025.

### Placas-Mãe

#### Socket AM5 (AMD):

| Chipset | PCIe | Overclocking | Preço (R$) | Uso |
|---------|------|--------------|------------|-----|
| A620 | PCIe 4.0 | ❌ | 800-1.200 | Budget |
| B650 | PCIe 4.0 | ✅ | 1.200-1.800 | **Melhor custo-benefício** |
| B650E | PCIe 5.0 | ✅ | 1.800-2.500 | Enthusiast |
| X670E | PCIe 5.0 + Multi-GPU | ✅ | 2.500-4.000 | Profissional |

**Modelos Recomendados**:
- **Budget**: ASRock B650M PG Riptide (R$ 1.400-1.600)
- **Mid-range**: ASUS B650E-F Gaming (R$ 2.000-2.400)
- **High-end**: ASUS X670E ROG Strix (R$ 3.000-3.500)

#### Socket LGA1700 (Intel):

| Chipset | PCIe | Overclocking | Preço (R$) | Uso |
|---------|------|--------------|------------|-----|
| B760 | PCIe 4.0/5.0 | ❌ | 1.200-1.800 | Mid-range |
| Z790 | PCIe 5.0 | ✅ | 2.000-3.500 | Enthusiast |

### Memória RAM DDR5

⚠️ **Alerta de Preços**: Preços de DDR5 dobraram em 2024-2025 devido à demanda de IA.

| Capacidade | Velocidade | Preço (R$) | Uso Recomendado |
|------------|------------|------------|-----------------|
| 32GB (2x16GB) | 6000MHz CL30 | 1.800-2.000 | **Mínimo recomendado** |
| 64GB (2x32GB) | 6000MHz CL30 | 4.000-4.500 | Profissional |
| 128GB (4x32GB) | 6000MHz CL30 | 8.000-9.000 | High-end |

**Marcas Recomendadas**: Kingston Fury Renegade, G.SKILL Trident Z5, Corsair Dominator

### Armazenamento (NVMe SSD)

| Capacidade | Interface | Preço (R$) | Uso |
|------------|-----------|------------|-----|
| 1TB | PCIe Gen4 | 500-700 | Sistema + Modelos básicos |
| 2TB | PCIe Gen4 | 900-1.200 | **Recomendado para IA** |
| 4TB | PCIe Gen4 | 2.000-2.500 | Datasets grandes |

**Modelos Recomendados**: Samsung 990 Pro, WD Black SN850X, Crucial T700

### Fontes de Alimentação (PSU)

⚠️ **Importante**: RTX 4090 e 5090 requerem conectores PCIe 5.0 (12VHPWR)

| Potência | Certificação | Preço (R$) | Uso Recomendado |
|----------|--------------|------------|-----------------|
| 750W | 80+ Gold | 600-800 | RTX 4060/4070 |
| 850W | 80+ Gold | 800-1.000 | **RTX 4070 Ti/4080** |
| 1000W | 80+ Gold/Platinum | 1.200-1.500 | **RTX 4090** |
| 1200W+ | 80+ Platinum/Titanium | 1.500-2.000 | RTX 5090 |
| 1600W | 80+ Titanium | 2.500-3.000 | Multi-GPU |

**Marcas Confiáveis**: Corsair, EVGA, Seasonic, XPG, MSI

---

## Onde Comprar no Brasil

### Principais Varejistas (2025):

#### 🏆 **Pichau** (pichau.com.br)
- ✅ Amplo catálogo de componentes
- ✅ PCs montados especializados (linha Highflyer)
- ✅ Bons preços em GPUs
- ✅ Parcelamento em até 12x

#### 🏆 **KaBuM!** (kabum.com.br)
- ✅ Maior variedade de marcas
- ✅ Promoções frequentes (Black Friday, Esquenta Black)
- ✅ Cashback e clube de descontos
- ✅ Entrega rápida

#### 🏆 **Terabyte Shop** (terabyteshop.com.br)
- ✅ Preços competitivos
- ✅ Bom atendimento técnico
- ✅ Componentes high-end

#### 🏆 **Amazon.com.br**
- ✅ Amazon Prime (frete grátis)
- ✅ Garantia facilitada
- ⚠️ Preços podem ser mais altos

#### Lojas Especializadas em Workstations IA:
- **Elite Computadores** (elitecomputadores.com.br)
- **Donatec Informática** (blog.donatec.com.br)
- **Netshop Informática Brasília** (netshopinformatica.com.br)

### Dicas de Compra:

1. **Compare Preços**: Use Zoom, Buscapé, e Hardware Barato
2. **Períodos de Promoção**:
   - Black Friday (Novembro)
   - Esquenta Black (Outubro)
   - Aniversário das lojas
   - Lançamento de novas GPUs (preços das anteriores caem)
3. **Parcelamento**: A maioria aceita até 12x sem juros
4. **Garantia**: Verifique se é nacional ou internacional
5. **Frete**: Compare custos e prazos

---

## Custos Estimados

### Investimento Inicial por Configuração:

| Configuração | Hardware | Energia/Mês* | Total Ano 1 |
|--------------|----------|--------------|-------------|
| Entry-Level | R$ 12-15k | R$ 150-250 | R$ 13.8-18k |
| Intermediária | R$ 18-22k | R$ 200-350 | R$ 20.4-26.2k |
| Profissional | R$ 30-38k | R$ 300-500 | R$ 33.6-44k |
| Enterprise | R$ 45k+ | R$ 500-800 | R$ 51-54.6k |

**Consumo de energia estimado para uso contínuo (24/7)*

### Custo Operacional Mensal (Energia):

**Tarifa média Brasil: R$ 0,70/kWh (2025)**

| GPU | TDP | Consumo Sistema** | Custo 24/7 | Custo 8h/dia |
|-----|-----|-------------------|------------|--------------|
| RTX 4060 Ti | 160W | ~300W | R$ 151 | R$ 50 |
| RTX 4070 | 200W | ~350W | R$ 176 | R$ 59 |
| RTX 4070 Ti Super | 285W | ~450W | R$ 227 | R$ 76 |
| RTX 4080 Super | 320W | ~500W | R$ 252 | R$ 84 |
| RTX 4090 | 450W | ~650W | R$ 328 | R$ 109 |
| 2x RTX 4090 | 900W | ~1200W | R$ 605 | R$ 202 |

**Sistema completo (CPU, RAM, storage, periféricos)*

---

## Considerações de Performance

### Modelos Populares e Requisitos (Ollama):

#### Small Models (7B-8B):
| Modelo | Quantização | VRAM Mín. | RAM Mín. | GPU Recomendada |
|--------|-------------|-----------|----------|-----------------|
| Llama 3.1 8B | Q4_K_M | 5GB | 16GB | RTX 4060 Ti |
| Llama 3.1 8B | Q8_0 | 8GB | 16GB | RTX 4060 Ti 16GB |
| Mistral 7B | Q4_K_M | 4GB | 16GB | RTX 4060 |
| Gemma 2 9B | Q4_K_M | 6GB | 16GB | RTX 4060 Ti |

#### Medium Models (13B-30B):
| Modelo | Quantização | VRAM Mín. | RAM Mín. | GPU Recomendada |
|--------|-------------|-----------|----------|-----------------|
| Llama 3.1 13B | Q4_K_M | 8GB | 32GB | RTX 4070 |
| Mixtral 8x7B | Q4_K_M | 24GB | 32GB | RTX 4090 |
| Qwen 2.5 14B | Q4_K_M | 9GB | 32GB | RTX 4070 Ti Super |

#### Large Models (70B+):
| Modelo | Quantização | VRAM Mín. | RAM Mín. | GPU Recomendada |
|--------|-------------|-----------|----------|-----------------|
| Llama 3.1 70B | Q4_K_M | 35GB | 64GB | 2x RTX 4090 |
| Llama 3.1 70B | Q8_0 | 70GB | 128GB | 3x RTX 4090 / A100 |
| Llama 3.1 405B | Q4_K_M | 200GB+ | 256GB+ | Cluster GPU |

### Fine-Tuning Performance:

| Método | Modelo | GPU Mínima | Tempo Treino* | Dataset Exemplo |
|--------|--------|------------|---------------|-----------------|
| QLoRA | Llama 3.1 8B | RTX 4060 Ti 16GB | 2-6h | 10k exemplos |
| QLoRA | Llama 3.1 13B | RTX 4070 Ti Super | 4-12h | 10k exemplos |
| LoRA | Llama 3.1 8B | RTX 4080 Super | 1-4h | 10k exemplos |
| LoRA | Llama 3.1 13B | RTX 4090 | 3-8h | 10k exemplos |
| Full | Llama 3.1 7B | 8x A100 | 12-48h | 100k exemplos |

**Tempo aproximado para 3 epochs em dataset de instrução*

### Otimizações Recomendadas:

#### Para Inferência (Ollama):
1. **Quantização Agressiva**: Use Q4_K_M para máxima eficiência
2. **Context Length**: Reduza se não precisar de contexto longo
3. **Batch Size**: Ajuste conforme VRAM disponível
4. **CPU Offloading**: Use para modelos que excedem VRAM

#### Para Fine-Tuning:
1. **QLoRA**: Melhor relação custo-benefício
2. **Gradient Checkpointing**: Reduz uso de VRAM
3. **Mixed Precision (FP16/BF16)**: Acelera treino
4. **LoRA Rank**: r=8 ou r=16 para maioria dos casos
5. **Batch Size**: Menor = mais RAM, maior = mais rápido

### Benchmark de Tokens/Segundo (Ollama):

| GPU | Llama 3.1 8B (Q4) | Llama 3.1 70B (Q4) |
|-----|-------------------|---------------------|
| RTX 4060 Ti | ~40-50 t/s | N/A |
| RTX 4070 | ~60-70 t/s | N/A |
| RTX 4080 Super | ~100-120 t/s | ~15-20 t/s |
| RTX 4090 | ~140-160 t/s | ~25-35 t/s |

---

## Recomendações Finais

### 🎯 **Melhor Custo-Benefício Geral**: Configuração Intermediária
- **RTX 4070 Ti Super 16GB** (R$ 5.500-6.500)
- **AMD Ryzen 9 7900X** (R$ 2.500-3.000)
- **64GB DDR5** (R$ 4.000-4.500)
- **Total**: ~R$ 18.000-22.000

**Justificativa**:
- ✅ Executa modelos até 13B confortavelmente
- ✅ Fine-tuning eficiente com QLoRA/LoRA
- ✅ Modelos 70B viáveis com quantização
- ✅ Espaço para upgrade futuro

### 🚀 **Melhor para Fine-Tuning Sério**: Configuração Profissional
- **RTX 4090 24GB**
- **AMD Ryzen 9 7950X**
- **128GB DDR5**

### 💰 **Melhor para Começar**: Configuração Entry-Level
- **RTX 4060 Ti 16GB**
- **AMD Ryzen 7 7700X**
- **32GB DDR5**

### 🏢 **Para Produção Empresarial**: Configuração Enterprise
- **2x RTX 4090** ou aguardar **RTX 5090**
- **AMD Threadripper**
- **256GB DDR5 ECC**

---

## Próximos Passos

### Antes de Comprar:
1. ✅ Defina seus modelos-alvo (7B, 13B, 70B?)
2. ✅ Determine se fará fine-tuning ou apenas inferência
3. ✅ Calcule custos de energia mensal
4. ✅ Verifique disponibilidade de componentes
5. ✅ Compare preços em múltiplos varejistas

### Após Montar:
1. 📦 Instalar Ubuntu 22.04/24.04 LTS ou Windows 11
2. 🔧 Instalar NVIDIA Drivers (versão 535+)
3. 🐳 Instalar Docker + NVIDIA Container Toolkit
4. 🦙 Instalar Ollama: `curl -fsSL https://ollama.ai/install.sh | sh`
5. 🧪 Testar: `ollama run llama3.1:8b`
6. 🔬 Para fine-tuning: Instalar Python, PyTorch, transformers, PEFT

### Recursos Úteis:
- **Ollama**: https://ollama.ai
- **Hugging Face**: https://huggingface.co
- **Unsloth (QLoRA otimizado)**: https://github.com/unslothai/unsloth
- **Axolotl (Fine-tuning framework)**: https://github.com/OpenAccess-AI-Collective/axolotl

---

## Glossário

- **VRAM**: Memória da GPU (Video RAM)
- **LoRA**: Low-Rank Adaptation - método eficiente de fine-tuning
- **QLoRA**: LoRA com quantização 4-bit
- **Quantização**: Redução de precisão numérica para economizar memória
- **Q4_K_M**: Formato de quantização 4-bit (GGUF)
- **Tokens/s**: Velocidade de geração de texto
- **Context Length**: Tamanho máximo de contexto (em tokens)
- **PCIe 5.0**: Interface mais rápida para GPUs modernas
- **DDR5**: Memória RAM de última geração

---

**Última atualização**: Novembro 2025
**Mercado**: Brasil
**Moeda**: Real (R$)

---

### Notas Importantes:

⚠️ **Volatilidade de Preços**: O mercado de GPUs é altamente volátil. Preços podem variar 20-30% em semanas.

⚠️ **Escassez de GPUs**: RTX 5090 e modelos high-end frequentemente enfrentam escassez no lançamento.

⚠️ **Taxas de Importação**: Componentes importados sofrem com impostos pesados no Brasil (~60-80% sobre o valor).

⚠️ **Energia**: Brasil tem tarifas de energia relativamente altas. Considere o custo operacional.

⚠️ **Garantia**: Prefira vendedores com garantia nacional para facilitar RMA.

---

**Compilado por**: Claude (Anthropic AI)
**Fontes**: Pesquisa de mercado brasileiro, especificações técnicas NVIDIA/AMD, benchmarks comunidade Ollama/Hugging Face
