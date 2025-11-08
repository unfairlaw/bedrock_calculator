# AWS Cost Estimation Agent

An intelligent agent that automatically routes cost estimation queries to the appropriate calculator tool.

## 🤖 Overview

The AWS Cost Agent acts as a unified interface to three powerful calculators:

1. **RAG Calculator** - Bedrock, OpenSearch, document processing
2. **Compute/Storage Calculator** - EC2, Lambda, S3
3. **Abstract Calculator** - Any AWS service via dynamic generation

```
┌─────────────────────────────────────────────────────────┐
│                                                          │
│                    User Query                            │
│                         │                                │
│                         ▼                                │
│              ┌──────────────────────┐                   │
│              │   AWS Cost Agent     │                   │
│              │  (Intent Recognition)│                   │
│              └──────────────────────┘                   │
│                         │                                │
│         ┌───────────────┼───────────────┐               │
│         ▼               ▼               ▼               │
│    ┌────────┐     ┌─────────┐     ┌─────────┐         │
│    │  RAG   │     │ Compute │     │Abstract │         │
│    │  Tool  │     │  Tool   │     │  Tool   │         │
│    └────────┘     └─────────┘     └─────────┘         │
│         │               │               │               │
│         └───────────────┴───────────────┘               │
│                         │                                │
│                         ▼                                │
│                  Formatted Response                      │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Interactive Mode

```bash
python3 aws_cost_agent.py
```

This launches an interactive chat session:

```
🤖 AWS Cost Estimation Agent
============================================================

I can help estimate AWS costs using three calculators:
  1. RAG systems (Bedrock, OpenSearch)
  2. Compute/Storage (EC2, Lambda, S3)
  3. Any AWS service (generates custom calculators)

Type 'help' for examples, 'quit' to exit
============================================================

You: Estimate costs for a RAG system with 50 manuals
```

### Demo Mode

```bash
python3 aws_cost_agent.py demo
```

Runs through pre-built example queries to demonstrate capabilities.

### Programmatic Usage

```python
from aws_cost_agent import AWSCostAgent

agent = AWSCostAgent()

# Ask a question
response = agent.process("How much for 10 t3.large instances?")
print(response)

# Get structured data
# (response includes both message and data)
```

## 📝 Example Queries

### RAG Calculator Queries

```
"Estimate costs for a RAG system with 100 manuals and 10,000 queries per month"
"How much would a Bedrock RAG system with 50 documents cost?"
"What's the cost of processing 200 technical manuals with embeddings?"
"RAG system for 5,000 monthly queries"
```

**Detected keywords:** rag, bedrock, embeddings, opensearch, documents, manuals, claude

### Compute/Storage Queries

```
"How much for 4 t3.medium instances running 24/7?"
"What would 5 million Lambda invocations cost?"
"Cost of 2 m5.large instances and 1000GB S3 storage"
"10 EC2 servers with 2 million Lambda calls per month"
```

**Detected keywords:** ec2, lambda, s3, instances, serverless, storage, function

### Abstract Calculator Queries

```
"Generate a calculator for RDS"
"What's the pricing for DynamoDB in us-west-2?"
"Create calculator for ECS"
"I need pricing info for ElastiCache"
```

**Detected keywords:** rds, dynamodb, ecs, eks, elasticache, redshift, generate

## 🎯 Features

### 1. Intelligent Intent Recognition

The agent automatically determines which calculator to use based on:
- Keywords in the query
- Service names mentioned
- Context from previous conversation

```python
# Automatically routes to RAG calculator
agent.process("RAG system with 100 manuals")

# Automatically routes to Compute calculator
agent.process("10 t3.medium instances")

# Automatically routes to Abstract calculator
agent.process("Generate calculator for RDS")
```

### 2. Parameter Extraction

Extracts numeric values and units automatically:

```python
"100 manuals" → num_manuals=100
"10,000 queries" → monthly_queries=10000
"5 million Lambda invocations" → lambda_invocations=5000000
"t3.medium" → instance_type="t3.medium"
"512MB memory" → memory_mb=512
```

### 3. Formatted Responses

Provides clear, structured output:

```
📊 RAG System Cost Estimate
============================================================

💰 Costs:
   Setup (one-time):  $108.56
   Monthly:           $506.08
   Annual:            $6,181.52

📦 Breakdown:
   Infrastructure:    $352.01/month
   Queries:           $154.07/month
```

### 4. Conversation History

Maintains context across multiple queries:

```python
agent = AWSCostAgent()

# First query
agent.process("How much for 4 t3.medium instances?")

# Follow-up (could use context if enhanced)
agent.process("What about with 1TB of S3 storage?")
```

### 5. Error Handling

Gracefully handles:
- Unknown services
- Ambiguous queries
- Missing parameters
- Invalid inputs

## 🛠️ Architecture

### Tool Interface

Each calculator is wrapped as a tool with:

```python
class ToolWrapper:
    name: str           # Human-readable name
    description: str    # When to use this tool
    execute(**kwargs)   # Execute with parameters
```

### Intent Recognition

Pattern matching on keywords:

```python
def _identify_intent(self, user_input: str) -> Tuple[ToolType, Dict]:
    # Analyze keywords
    # Extract parameters
    # Return (tool_type, parameters)
```

### Parameter Extraction

Regex-based extraction:

```python
# Extracts: "5 million Lambda invocations"
lambda_million = re.search(
    r'(\d+)\s*million\s*(?:invocations?)',
    user_input
)
→ lambda_invocations = 5_000_000
```

## 📊 Tool Selection Logic

```python
if any(keyword in query for keyword in ['rag', 'bedrock', 'opensearch']):
    → Use RAG Calculator

elif any(keyword in query for keyword in ['ec2', 'lambda', 's3']):
    → Use Compute Calculator

elif any(keyword in query for keyword in ['rds', 'dynamodb', 'ecs']):
    → Use Abstract Calculator

else:
    → Provide help message
```

## 🔧 Customization

### Add New Keywords

```python
# In _identify_intent method

rag_keywords = [
    'rag', 'bedrock', 'retrieval',
    'your_custom_keyword'  # Add here
]
```

### Modify Parameter Extraction

```python
# In _extract_compute_params method

# Add custom pattern
custom_match = re.search(r'your_pattern', user_input)
if custom_match:
    params['your_param'] = custom_match.group(1)
```

### Add New Tool

```python
class NewCalculatorTool:
    def __init__(self):
        self.name = "New Calculator"
        self.description = "..."

    def execute(self, **kwargs) -> ToolResponse:
        # Your logic here
        return ToolResponse(...)

# Register in agent
self.tools[ToolType.NEW_TOOL] = NewCalculatorTool()
```

## 💡 Advanced Usage

### Structured Output

```python
agent = AWSCostAgent()
response = agent.process("RAG system with 50 manuals")

# Access structured data
if hasattr(response, 'data') and response.data:
    monthly_cost = response.data['monthly_total']
    yearly_cost = response.data['yearly_total']

    print(f"Monthly: ${monthly_cost:,.2f}")
    print(f"Yearly: ${yearly_cost:,.2f}")
```

### Batch Processing

```python
agent = AWSCostAgent()

queries = [
    "RAG system with 100 manuals",
    "10 t3.medium instances",
    "5 million Lambda invocations"
]

results = []
for query in queries:
    response = agent.process(query)
    results.append(response)

# Process results
for result in results:
    print(result.message)
```

### Export to JSON

```python
import json

agent = AWSCostAgent()
response = agent.process("RAG system with 50 manuals")

# Extract conversation history
history = agent.conversation_history

# Save to file
with open('conversation.json', 'w') as f:
    json.dump(history, f, indent=2)
```

## 🤝 Integration Examples

### Flask API

```python
from flask import Flask, request, jsonify
from aws_cost_agent import AWSCostAgent

app = Flask(__name__)
agent = AWSCostAgent()

@app.route('/estimate', methods=['POST'])
def estimate():
    query = request.json['query']
    response = agent.process(query)
    return jsonify({
        'response': response.message,
        'data': response.data if hasattr(response, 'data') else None
    })

if __name__ == '__main__':
    app.run()
```

### Slack Bot

```python
from slack_bolt import App
from aws_cost_agent import AWSCostAgent

app = App(token="xoxb-your-token")
agent = AWSCostAgent()

@app.message("estimate")
def handle_estimate(message, say):
    query = message['text']
    response = agent.process(query)
    say(response.message)

app.start(port=3000)
```

### Discord Bot

```python
import discord
from aws_cost_agent import AWSCostAgent

client = discord.Client()
agent = AWSCostAgent()

@client.event
async def on_message(message):
    if message.content.startswith('!estimate'):
        query = message.content[10:]  # Remove '!estimate '
        response = agent.process(query)
        await message.channel.send(response.message)

client.run('your-token')
```

## 🧪 Testing

### Run Demo

```bash
python3 aws_cost_agent.py demo
```

### Manual Testing

```python
from aws_cost_agent import AWSCostAgent

agent = AWSCostAgent()

# Test RAG calculator
print(agent.process("RAG system with 50 manuals and 5000 queries"))

# Test Compute calculator
print(agent.process("4 t3.medium instances and 1 million Lambda calls"))

# Test Abstract calculator
print(agent.process("Generate calculator for RDS"))
```

## 📈 Performance

- **Intent Recognition:** ~1ms
- **Parameter Extraction:** ~2ms
- **RAG Calculator:** ~50ms
- **Compute Calculator:** ~100ms
- **Abstract Calculator:** ~150ms (cached) / ~3-5s (live fetch)

## 🔮 Future Enhancements

- [ ] Context-aware follow-up questions
- [ ] Multi-tool queries (combine multiple calculators)
- [ ] Natural language understanding (NLU) instead of regex
- [ ] Learning from user corrections
- [ ] Cost optimization suggestions
- [ ] Comparison across regions
- [ ] Budget alerts and recommendations
- [ ] Voice interface support
- [ ] Multi-language support

## 🐛 Troubleshooting

### Agent Can't Determine Intent

**Problem:** Agent returns "I'm not sure which calculator to use"

**Solution:**
- Be more specific about the AWS service
- Use keywords like "EC2", "Lambda", "RAG", "Bedrock"
- Try: "Estimate EC2 costs for..." instead of "How much for servers?"

### Parameters Not Extracted

**Problem:** Cost shows $0.00 or missing data

**Solution:**
- Include numeric values with units
- Try: "5 million Lambda invocations" instead of "lots of Lambda calls"
- Be explicit: "10 manuals" not "several documents"

### Wrong Calculator Selected

**Problem:** Query goes to wrong tool

**Solution:**
- Check keyword list in agent code
- Add service-specific keywords
- Be more explicit: "EC2 t3.medium" instead of just "t3.medium"

## 📚 API Reference

### AWSCostAgent

```python
class AWSCostAgent:
    def __init__(self):
        """Initialize agent with all three calculator tools"""

    def process(self, user_input: str) -> str:
        """
        Process user query and return formatted response

        Args:
            user_input: Natural language cost question

        Returns:
            Formatted cost estimate
        """

    def get_available_tools(self) -> str:
        """Get list of available tools with descriptions"""
```

### ToolResponse

```python
@dataclass
class ToolResponse:
    tool: ToolType          # Which tool was used
    success: bool           # Whether execution succeeded
    data: Optional[Dict]    # Structured cost data
    error: Optional[str]    # Error message if failed
    message: str            # Formatted response for user
```

## 📄 Files

```
aws_cost_agent.py           # Main agent implementation
AGENT_README.md             # This file
```

## 🎓 Examples Gallery

### Example 1: Startup Infrastructure

```
You: How much would it cost to run a startup with 2 t3.small EC2 instances
     and 500,000 Lambda invocations per month?

Agent: 📊 Compute & Storage Cost Estimate
       ============================================================

       💰 Total Costs:
          Monthly:           $31.21
          Annual:            $374.50

       🖥️  EC2:
          Compute:           $30.37/month
          Storage (EBS):     $0.80/month
          - 2x t3.small: $31.17/month

       ⚡ Lambda:
          Total:             $0.04/month
          Invocations:       500,000/month
```

### Example 2: RAG Production System

```
You: What's the cost for a production RAG system with 200 technical manuals,
     each about 150 pages, handling 50,000 user queries per month?

Agent: 📊 RAG System Cost Estimate
       ============================================================

       💰 Costs:
          Setup (one-time):  $318.06
          Monthly:           $1,245.17
          Annual:            $15,260.10

       📦 Breakdown:
          Infrastructure:    $354.75/month
          Queries:           $890.42/month

       🔍 OpenSearch:
          OCUs needed:       2
          Compute:           $350.40/month
```

### Example 3: Generate Custom Calculator

```
You: I need pricing information for Amazon RDS in us-west-2

Agent: 📊 Abstract Calculator - AmazonRDS
       ============================================================

       ✅ Successfully generated calculator!

       📦 Service Information:
          Service:           AmazonRDS
          Region:            us-west-2
          Pricing Categories: 47

       💰 Sample Pricing Categories:
          - db.t3.micro: $0.017/Hrs
          - db.m5.large: $0.192/Hrs
          - Storage-GP3: $0.115/GB-Mo
```

---

**Built for Intelligent Cost Estimation**

The AWS Cost Agent provides a natural language interface to powerful cost calculators, making AWS pricing accessible through conversation.
