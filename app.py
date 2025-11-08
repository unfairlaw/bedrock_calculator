#!/usr/bin/env python3
"""
Flask API for AWS Cost Agent
Provides REST API endpoints for cost estimation
"""

from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import os
import json
from datetime import datetime

# Import both agent types
from aws_cost_agent import AWSCostAgent, ToolType

# Try to import Bedrock agent (optional)
try:
    from aws_bedrock_agent import AWSBedrockCostAgent, BedrockConfig
    BEDROCK_AVAILABLE = True
except ImportError:
    BEDROCK_AVAILABLE = False
    print("⚠️  Bedrock agent not available (boto3 not installed)")

app = Flask(__name__,
            static_folder='static',
            template_folder='templates')
CORS(app)  # Enable CORS for all routes

# Determine which agent to use based on environment variable
USE_BEDROCK = os.getenv('USE_BEDROCK', 'false').lower() == 'true'
AGENT_MODE = 'bedrock' if (USE_BEDROCK and BEDROCK_AVAILABLE) else 'regex'

print(f"\n🤖 Agent Mode: {AGENT_MODE.upper()}")
if AGENT_MODE == 'bedrock':
    print("   Using AWS Bedrock with Claude 3.5 Sonnet")
    print(f"   Region: {os.getenv('AWS_REGION', 'us-east-1')}")
else:
    print("   Using regex-based routing")
print()

# Store conversation sessions (in production, use Redis or database)
sessions = {}


@app.route('/')
def index():
    """Serve the main page"""
    return render_template('index.html')


@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0',
        'agent_mode': AGENT_MODE,
        'bedrock_available': BEDROCK_AVAILABLE
    })


@app.route('/api/estimate', methods=['POST'])
def estimate():
    """
    Main cost estimation endpoint

    Request body:
    {
        "query": "How much for 10 t3.medium instances?",
        "session_id": "optional-session-id"
    }

    Response:
    {
        "success": true,
        "message": "formatted response",
        "data": {...},
        "tool_used": "compute_calculator",
        "timestamp": "2025-11-08T..."
    }
    """
    try:
        data = request.get_json()

        if not data or 'query' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing query parameter'
            }), 400

        query = data['query']
        session_id = data.get('session_id', 'default')

        # Get or create session with appropriate agent type
        if session_id not in sessions:
            if AGENT_MODE == 'bedrock':
                sessions[session_id] = AWSBedrockCostAgent()
            else:
                sessions[session_id] = AWSCostAgent()

        session_agent = sessions[session_id]

        # Process query
        response = session_agent.process(query)

        # Extract tool type and data
        tool_used = 'unknown'
        response_data = None

        # Parse the conversation history to get the last tool response
        if session_agent.conversation_history:
            # Look for tool response in the agent's processing
            # Since the agent doesn't expose tool responses directly,
            # we'll infer from the response message
            if 'RAG System' in response:
                tool_used = 'rag_calculator'
            elif 'Compute & Storage' in response:
                tool_used = 'compute_calculator'
            elif 'Abstract Calculator' in response:
                tool_used = 'abstract_calculator'

        return jsonify({
            'success': True,
            'message': response,
            'data': response_data,
            'tool_used': tool_used,
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


@app.route('/api/tools', methods=['GET'])
def get_tools():
    """
    Get available calculator tools

    Response:
    {
        "tools": [
            {
                "name": "RAG Calculator",
                "description": "...",
                "keywords": ["rag", "bedrock", ...]
            },
            ...
        ]
    }
    """
    tools = [
        {
            'id': 'rag_calculator',
            'name': 'RAG Cost Calculator',
            'description': 'Estimates costs for RAG systems using AWS Bedrock, OpenSearch, and Textract',
            'keywords': ['rag', 'bedrock', 'opensearch', 'embeddings', 'documents', 'manuals', 'retrieval'],
            'example': 'Estimate costs for a RAG system with 100 manuals and 10,000 queries per month'
        },
        {
            'id': 'compute_calculator',
            'name': 'Compute & Storage Calculator',
            'description': 'Calculates costs for EC2, Lambda, and S3',
            'keywords': ['ec2', 'lambda', 's3', 'instances', 'serverless', 'storage', 'compute'],
            'example': 'How much for 4 t3.medium instances and 1 million Lambda invocations?'
        },
        {
            'id': 'abstract_calculator',
            'name': 'Abstract Calculator',
            'description': 'Generates calculators for any AWS service dynamically',
            'keywords': ['rds', 'dynamodb', 'ecs', 'eks', 'generate', 'pricing'],
            'example': 'Generate a calculator for Amazon RDS'
        }
    ]

    return jsonify({'tools': tools})


@app.route('/api/examples', methods=['GET'])
def get_examples():
    """
    Get example queries

    Response:
    {
        "examples": [
            {
                "category": "RAG Systems",
                "queries": [...]
            },
            ...
        ]
    }
    """
    examples = [
        {
            'category': 'RAG Systems',
            'icon': '🤖',
            'queries': [
                'Estimate costs for a RAG system with 50 manuals and 5,000 queries per month',
                'How much for processing 200 technical documents with Bedrock?',
                'RAG system with 100 manuals, 150 pages each, 10,000 monthly queries'
            ]
        },
        {
            'category': 'EC2 Instances',
            'icon': '🖥️',
            'queries': [
                'How much for 4 t3.medium instances running 24/7?',
                'Cost of 10 m5.large instances with 100GB EBS storage',
                '2 c5.xlarge instances for 12 hours per day'
            ]
        },
        {
            'category': 'Lambda & Serverless',
            'icon': '⚡',
            'queries': [
                'What would 5 million Lambda invocations cost?',
                '10 million Lambda calls with 1GB memory and 500ms duration',
                'Serverless architecture with 2 million invocations per month'
            ]
        },
        {
            'category': 'S3 Storage',
            'icon': '🗄️',
            'queries': [
                'How much for 1TB of S3 storage?',
                '5000GB S3 Standard with 10 million GET requests',
                'S3 storage costs for 500GB with frequent access'
            ]
        },
        {
            'category': 'Other Services',
            'icon': '🔧',
            'queries': [
                'Generate a calculator for Amazon RDS',
                'What\'s the pricing for DynamoDB?',
                'Create calculator for Amazon ECS'
            ]
        }
    ]

    return jsonify({'examples': examples})


@app.route('/api/session/clear', methods=['POST'])
def clear_session():
    """
    Clear a conversation session

    Request body:
    {
        "session_id": "session-id"
    }
    """
    data = request.get_json()
    session_id = data.get('session_id', 'default')

    if session_id in sessions:
        del sessions[session_id]

    return jsonify({
        'success': True,
        'message': 'Session cleared'
    })


@app.route('/api/session/history', methods=['GET'])
def get_history():
    """
    Get conversation history for a session

    Query params:
    - session_id: Session ID (default: 'default')
    """
    session_id = request.args.get('session_id', 'default')

    if session_id in sessions:
        history = sessions[session_id].conversation_history
        return jsonify({
            'success': True,
            'history': history
        })

    return jsonify({
        'success': True,
        'history': []
    })


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'success': False,
        'error': 'Endpoint not found'
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500


if __name__ == '__main__':
    # Create necessary directories
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)
    os.makedirs('templates', exist_ok=True)

    # Run the app
    print("\n" + "="*60)
    print("🚀 AWS Cost Agent API Server")
    print("="*60)
    print("\nServer starting on http://localhost:5000")
    print("\nAPI Endpoints:")
    print("  GET  /                    - Web interface")
    print("  GET  /api/health          - Health check")
    print("  POST /api/estimate        - Cost estimation")
    print("  GET  /api/tools           - Available tools")
    print("  GET  /api/examples        - Example queries")
    print("  GET  /api/session/history - Conversation history")
    print("  POST /api/session/clear   - Clear session")
    print("\n" + "="*60 + "\n")

    app.run(debug=True, host='0.0.0.0', port=5000)
