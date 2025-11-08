# AWS Bedrock AI Agent - Real AI Integration

Complete guide for using AWS Bedrock with Claude 3.5 Sonnet for true AI-powered cost estimation.

## 🤖 What Changed?

The agent now has **TWO modes**:

### 1. Regex Mode (Default - No Credentials Needed)
- ✅ Works offline
- ✅ No AWS account required
- ✅ Fast and free
- ❌ Limited to pattern matching
- ❌ Can't understand complex queries

### 2. Bedrock Mode (Real AI - Requires AWS)
- ✅ **True AI understanding** with Claude 3.5 Sonnet
- ✅ Natural language comprehension
- ✅ Tool calling (function calling)
- ✅ Multi-turn conversations
- ✅ Context awareness
- ❌ Requires AWS credentials
- ❌ Small cost per query (~$0.01)

## 🚀 Quick Start with Bedrock

### Step 1: Prerequisites

1. **AWS Account** with Bedrock access
2. **Claude 3.5 Sonnet** model enabled in your region
3. **IAM Permissions**: `bedrock:InvokeModel`

### Step 2: Enable Bedrock Model Access

```bash
# Go to AWS Console
# Navigate to: Amazon Bedrock → Model access
# Request access to: Anthropic Claude 3.5 Sonnet
# Region: us-east-1 (recommended)
```

### Step 3: Get AWS Credentials

```bash
# Go to AWS Console → IAM → Users → Your User → Security credentials
# Create Access Key
# Save AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY
```

### Step 4: Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env and add your credentials:
USE_BEDROCK=true
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here
AWS_REGION=us-east-1
```

### Step 5: Run

```bash
# Option 1: Flask (Development)
pip install boto3
export USE_BEDROCK=true
python3 app.py

# Option 2: Docker
docker-compose up -d

# Access at http://localhost:5000
```

## 🎯 Comparison

| Feature | Regex Mode | Bedrock Mode |
|---------|-----------|--------------|
| **Understanding** | Pattern matching | True AI comprehension |
| **Query Flexibility** | Limited patterns | Any natural language |
| **Tool Selection** | Keywords | AI reasoning |
| **Parameter Extraction** | Regex | AI extraction |
| **Conversation** | Stateless | Multi-turn aware |
| **Cost** | Free | ~$0.01/query |
| **Speed** | ~50ms | ~2-3 seconds |
| **Setup** | None | AWS account + credentials |
| **Accuracy** | Good for simple queries | Excellent for all queries |

## 💡 Example Queries

### Regex Mode Works Well For:

```
"How much for 10 t3.medium instances?"
"RAG system with 100 manuals and 5000 queries"
"5 million Lambda invocations with 512MB"
```

### Bedrock Mode Excels At:

```
"I need to process technical documents for my engineering team.
 We have about 200 manuals, each around 150 pages with lots of
 diagrams. We expect maybe 50,000 queries per month. What would
 this cost me using AWS?"

"My startup needs compute resources. We're running a web app
 that needs to handle moderate traffic - maybe 4 medium-sized
 instances should do it. What's the monthly cost if they run 24/7?"

"We're going serverless! I'm thinking of using Lambda with around
 5 to 10 million function calls per month. Each function takes
 about half a second and needs 512MB of memory. Can you estimate?"
```

The Bedrock mode understands context, infers details, and asks clarifying questions!

## 🛠️ Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `USE_BEDROCK` | No | `false` | Enable Bedrock AI mode |
| `AWS_ACCESS_KEY_ID` | Yes* | - | AWS access key |
| `AWS_SECRET_ACCESS_KEY` | Yes* | - | AWS secret key |
| `AWS_REGION` | No | `us-east-1` | AWS region with Bedrock |

*Required only if `USE_BEDROCK=true`

### IAM Policy

Minimum required IAM policy:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel"
      ],
      "Resource": [
        "arn:aws:bedrock:*::foundation-model/anthropic.claude-3-5-sonnet-20241022-v2:0"
      ]
    }
  ]
}
```

## 🐳 Docker with Bedrock

### Using .env File

```bash
# 1. Create .env file
cat > .env <<EOF
USE_BEDROCK=true
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=abc123...
AWS_REGION=us-east-1
EOF

# 2. Start Docker
docker-compose up -d

# Docker Compose will automatically load .env
```

### Using Environment Variables

```bash
docker run -d \
  -p 5000:5000 \
  -e USE_BEDROCK=true \
  -e AWS_ACCESS_KEY_ID=AKIA... \
  -e AWS_SECRET_ACCESS_KEY=abc123... \
  -e AWS_REGION=us-east-1 \
  aws-cost-agent
```

### Using AWS Credentials File

```bash
docker run -d \
  -p 5000:5000 \
  -e USE_BEDROCK=true \
  -v ~/.aws:/root/.aws:ro \
  aws-cost-agent
```

## 📊 Cost Estimation

### Bedrock Pricing (as of 2025)

**Claude 3.5 Sonnet v2:**
- Input: $0.003 per 1K tokens
- Output: $0.015 per 1K tokens

**Typical Query:**
- Input: ~500 tokens (your question + tools + conversation)
- Output: ~200 tokens (response)
- **Cost per query: ~$0.005 to $0.01**

**Monthly Estimates:**

| Queries/Month | Estimated Cost |
|---------------|----------------|
| 100 | $1 |
| 1,000 | $10 |
| 10,000 | $100 |
| 100,000 | $1,000 |

## 🔧 Architecture

### Tool Calling (Function Calling)

The Bedrock agent uses Claude's tool calling feature:

```
User: "How much for 100 manuals with 10K queries?"
  ↓
Claude AI analyzes query
  ↓
Claude decides to call: estimate_rag_costs
  ↓
Claude extracts parameters:
  - num_manuals: 100
  - monthly_queries: 10000
  ↓
Agent executes RAG calculator
  ↓
Results sent back to Claude
  ↓
Claude formats friendly response
  ↓
User sees: "For a RAG system with 100 manuals..."
```

### Defined Tools

The agent exposes 3 tools to Claude:

1. **estimate_rag_costs**
   - For Bedrock RAG systems
   - Parameters: num_manuals, monthly_queries, etc.

2. **estimate_compute_costs**
   - For EC2, Lambda, S3
   - Parameters: instance types, storage, invocations, etc.

3. **generate_calculator**
   - For any AWS service
   - Parameters: service_code, region

Claude intelligently selects and calls the right tools!

## 🧪 Testing

### Test Bedrock Connectivity

```bash
python3 aws_bedrock_agent.py
```

Expected output:
```
AWS Bedrock AI Cost Agent
Using Claude 3.5 Sonnet with Tool Calling
============================================================

Query 1/3
User: How much would it cost for a RAG system with...

Agent: For a RAG system with 100 manuals and 10,000 queries
       per month, here's the cost breakdown...
```

### Test via API

```bash
curl -X POST http://localhost:5000/api/estimate \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What would 100 manuals with 10K monthly queries cost?"
  }'
```

### Check Agent Mode

```bash
curl http://localhost:5000/api/health
```

Response should show:
```json
{
  "status": "healthy",
  "agent_mode": "bedrock",
  "bedrock_available": true
}
```

## 🐛 Troubleshooting

### Error: "Module 'boto3' not found"

```bash
pip install boto3 botocore
```

### Error: "credentials not found"

```bash
# Set environment variables
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
export AWS_REGION=us-east-1
export USE_BEDROCK=true
```

### Error: "Access denied" or "ValidationException"

**Cause:** Model access not enabled

**Solution:**
1. Go to AWS Console → Bedrock → Model access
2. Enable "Anthropic Claude 3.5 Sonnet"
3. Wait 2-5 minutes for activation

### Error: "Model not found in region"

**Cause:** Claude not available in your region

**Solution:**
```bash
# Use us-east-1 (recommended)
export AWS_REGION=us-east-1
```

Bedrock availability by region:
- ✅ us-east-1 (N. Virginia)
- ✅ us-west-2 (Oregon)
- ✅ eu-west-1 (Ireland)
- ✅ ap-southeast-1 (Singapore)

### Agent Stuck in Regex Mode

```bash
# Check environment variable
echo $USE_BEDROCK  # Should be 'true'

# Check logs
docker logs aws-cost-agent | grep "Agent Mode"
# Should show: Agent Mode: BEDROCK
```

## 🔐 Security Best Practices

### 1. Never Commit Credentials

```bash
# .env is in .gitignore
# Always use .env.example for templates
```

### 2. Use IAM Roles (Recommended for Production)

Instead of access keys, use IAM roles:

**For EC2:**
```bash
# Attach IAM role to EC2 instance
# No credentials needed in .env
```

**For ECS/Fargate:**
```bash
# Task role with bedrock:InvokeModel permission
```

### 3. Rotate Keys Regularly

```bash
# AWS Console → IAM → Users → Security credentials
# Deactivate old key → Create new key → Update .env
```

### 4. Limit Permissions

Only grant `bedrock:InvokeModel` - nothing more!

### 5. Use AWS Secrets Manager (Production)

```python
import boto3
import json

def get_secret():
    client = boto3.client('secretsmanager')
    secret = client.get_secret_value(SecretId='prod/bedrock/creds')
    return json.loads(secret['SecretString'])
```

## 📈 Monitoring

### Track Bedrock Usage

```bash
# AWS Console → CloudWatch → Bedrock metrics
# Monitor:
# - Invocations
# - Latency
# - Errors
# - Token usage
```

### Application Logs

```bash
# Docker logs
docker logs -f aws-cost-agent

# Local logs
tail -f app.log

# Look for:
# - Agent Mode: BEDROCK
# - Tool calls
# - Errors
```

## 🎓 Advanced Usage

### Custom Model Configuration

Edit `aws_bedrock_agent.py`:

```python
config = BedrockConfig(
    region='us-west-2',
    model_id='anthropic.claude-3-5-sonnet-20241022-v2:0',
    max_tokens=8192,  # Increase for longer responses
    temperature=0.3   # Higher for more creative responses
)

agent = AWSBedrockCostAgent(config=config)
```

### Add Custom Tools

```python
# Add to _define_tools() in aws_bedrock_agent.py
{
    "toolSpec": {
        "name": "your_custom_tool",
        "description": "What this tool does",
        "inputSchema": {
            "json": {
                "type": "object",
                "properties": {...}
            }
        }
    }
}
```

### Multi-Region Support

```python
# Create agents for different regions
agent_us = AWSBedrockCostAgent(BedrockConfig(region='us-east-1'))
agent_eu = AWSBedrockCostAgent(BedrockConfig(region='eu-west-1'))
agent_ap = AWSBedrockCostAgent(BedrockConfig(region='ap-southeast-1'))
```

## 🔄 Switching Between Modes

### At Runtime

```bash
# Start in regex mode
docker-compose up -d

# Switch to Bedrock mode
docker-compose down
USE_BEDROCK=true docker-compose up -d
```

### Both Modes Available

You can run both simultaneously on different ports:

```bash
# Regex mode on 5000
docker run -d -p 5000:5000 -e USE_BEDROCK=false aws-cost-agent

# Bedrock mode on 5001
docker run -d -p 5001:5000 -e USE_BEDROCK=true \
  -e AWS_ACCESS_KEY_ID=... aws-cost-agent
```

## 📚 Additional Resources

- [AWS Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
- [Claude Model Documentation](https://docs.anthropic.com/claude/)
- [Tool Calling Guide](https://docs.anthropic.com/claude/docs/tool-use)
- [AWS IAM Best Practices](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html)

## ✅ Checklist for Production

- [ ] AWS account created
- [ ] Bedrock enabled in region
- [ ] Claude 3.5 Sonnet access granted
- [ ] IAM user created with minimal permissions
- [ ] Access keys generated
- [ ] .env file created (not committed!)
- [ ] Environment variables set in production
- [ ] Credentials rotated regularly
- [ ] CloudWatch monitoring enabled
- [ ] Cost alerts configured
- [ ] Backup agent mode (regex) available

---

**You're now running a TRUE AI agent with AWS Bedrock!** 🚀

For questions or issues, check the main [README.md](README.md)
