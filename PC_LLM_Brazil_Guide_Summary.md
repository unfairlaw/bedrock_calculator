# PC Build Guide for Running and Fine-Tuning LLMs in Brazil - Executive Summary

## Quick Reference: Recommended Configurations

### Entry-Level (R$ 12,000 - R$ 15,000)
**Best for**: 7B-13B models, QLoRA fine-tuning
- **GPU**: RTX 4060 Ti 16GB (R$ 3,000-3,500)
- **CPU**: AMD Ryzen 7 7700X (R$ 1,800-2,200)
- **RAM**: 32GB DDR5 (R$ 1,800-2,000)
- **Use cases**: Development, testing, small model fine-tuning

### Intermediate (R$ 18,000 - R$ 22,000) ⭐ **BEST VALUE**
**Best for**: Up to 13B models, LoRA/QLoRA fine-tuning
- **GPU**: RTX 4070 Ti Super 16GB (R$ 5,500-6,500)
- **CPU**: AMD Ryzen 9 7900X (R$ 2,500-3,000)
- **RAM**: 64GB DDR5 (R$ 4,000-4,500)
- **Use cases**: Professional AI development, 70B models with quantization

### Professional (R$ 30,000 - R$ 38,000)
**Best for**: All models including 70B, advanced fine-tuning
- **GPU**: RTX 4090 24GB (R$ 12,000-14,000)
- **CPU**: AMD Ryzen 9 7950X (R$ 3,500-4,000)
- **RAM**: 128GB DDR5 (R$ 8,000-9,000)
- **Use cases**: Production AI, serious fine-tuning, large models

### Enterprise (R$ 45,000+)
**Best for**: Enterprise production, multiple GPUs
- **GPU**: 2x RTX 4090 24GB (48GB total)
- **CPU**: AMD Threadripper 7960X
- **RAM**: 256GB DDR5 ECC
- **Use cases**: 70B+ models without quantization, multi-user environments

## Key Hardware Requirements

### VRAM by Model Size (Ollama Inference)
- **7B models**: 8GB VRAM (with 4-bit quantization: ~5GB)
- **13B models**: 16GB VRAM (with 4-bit quantization: ~8GB)
- **70B models**: 48GB+ VRAM (with 4-bit quantization: ~35GB)

### Fine-Tuning Methods
- **QLoRA (Recommended)**: 7B model = 8GB VRAM, 13B model = 12-16GB VRAM
- **LoRA**: 7B model = 12-24GB VRAM, 13B model = 24GB+ VRAM
- **Full Fine-Tuning**: 7B model = 100-120GB VRAM (not viable on consumer hardware)

## Top GPU Recommendations for Brazil (2025)

| GPU | VRAM | Price Range (R$) | Best For |
|-----|------|------------------|----------|
| RTX 4060 Ti 16GB | 16GB | 3,000-3,500 | **Best budget option** for 13B models |
| RTX 4070 | 12GB | 3,800-4,400 | **Best overall value** for 7B-13B |
| RTX 4070 Ti Super | 16GB | 5,500-6,500 | **Sweet spot** for serious work |
| RTX 4090 | 24GB | 12,000-14,000 | **Best consumer GPU** for 70B models |
| RTX 5090 (2025) | 32GB | 15,000-18,000 | Future-proof option (limited availability) |

## Where to Buy in Brazil

### Recommended Retailers:
1. **Pichau** (pichau.com.br) - Great GPU prices, pre-built options
2. **KaBuM!** (kabum.com.br) - Largest selection, frequent promotions
3. **Terabyte Shop** (terabyteshop.com.br) - Competitive pricing
4. **Amazon.com.br** - Prime shipping, easy returns

### Best Times to Buy:
- Black Friday (November)
- Pre-Black Friday sales (October)
- When new GPU generations launch (previous gen prices drop)

## Model Performance Examples (Ollama with 4-bit Quantization)

| Model | Quantized Size | Min VRAM | Recommended GPU | Tokens/sec* |
|-------|----------------|----------|-----------------|-------------|
| Llama 3.1 8B | ~5GB | 8GB | RTX 4060 Ti | 40-50 |
| Llama 3.1 8B | ~5GB | 12GB | RTX 4070 | 60-70 |
| Llama 3.1 8B | ~5GB | 24GB | RTX 4090 | 140-160 |
| Llama 3.1 70B | ~35GB | 48GB | 2x RTX 4090 | 25-35 |
| Mistral 7B | ~4GB | 8GB | RTX 4060 | 45-55 |

*Approximate generation speed

## Important Considerations

### Cost of Ownership:
- **Hardware**: R$ 12,000 - R$ 45,000+ (depending on configuration)
- **Monthly Electricity** (24/7 operation):
  - RTX 4060 Ti: ~R$ 150
  - RTX 4070 Ti Super: ~R$ 227
  - RTX 4090: ~R$ 328
  - 2x RTX 4090: ~R$ 605

### Market Challenges in Brazil:
- ⚠️ Import taxes add 60-80% to component costs
- ⚠️ DDR5 RAM prices doubled in 2024-2025 (AI demand)
- ⚠️ GPU shortages common at launch
- ⚠️ High electricity costs (avg R$ 0.70/kWh)

## Getting Started After Building

1. Install Ubuntu 22.04/24.04 LTS or Windows 11
2. Install NVIDIA Drivers (version 535+)
3. Install Docker + NVIDIA Container Toolkit
4. Install Ollama: `curl -fsSL https://ollama.ai/install.sh | sh`
5. Test: `ollama run llama3.1:8b`

For fine-tuning, additionally install:
- Python 3.10+
- PyTorch with CUDA support
- Hugging Face transformers
- PEFT (Parameter-Efficient Fine-Tuning)
- Unsloth or Axolotl frameworks

## Final Recommendations

### For Most Users:
**Intermediate Configuration (RTX 4070 Ti Super + Ryzen 9 7900X + 64GB DDR5)**
- Total cost: R$ 18,000-22,000
- Handles 7B-13B models excellently
- 70B models viable with quantization
- QLoRA/LoRA fine-tuning capable
- Good upgrade path

### For Serious Fine-Tuning:
**Professional Configuration (RTX 4090 + Ryzen 9 7950X + 128GB DDR5)**
- Total cost: R$ 30,000-38,000
- Maximum consumer-grade VRAM (24GB)
- Full LoRA fine-tuning of 13B models
- 70B inference with light quantization

### Budget-Conscious:
**Entry-Level Configuration (RTX 4060 Ti 16GB + Ryzen 7 7700X + 32GB DDR5)**
- Total cost: R$ 12,000-15,000
- Perfect for learning and development
- QLoRA fine-tuning of 7B models
- Can run 13B models with quantization

---

**Full detailed guide available in**: `PC_LLM_Brazil_Guide.md`

**Last updated**: November 2025
**Market**: Brazil
**Currency**: Brazilian Real (R$)
