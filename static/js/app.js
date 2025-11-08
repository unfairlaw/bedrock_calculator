/**
 * AWS Cost Agent - Frontend Application
 * Handles API communication and UI updates
 */

class CostAgentClient {
    constructor() {
        this.apiBase = '/api';
        this.sessionId = this.generateSessionId();
        this.queryCount = 0;

        // DOM elements
        this.elements = {
            messages: document.getElementById('messages'),
            queryForm: document.getElementById('query-form'),
            queryInput: document.getElementById('query-input'),
            sendBtn: document.getElementById('send-btn'),
            sendBtnText: document.getElementById('send-btn-text'),
            sendBtnLoader: document.getElementById('send-btn-loader'),
            clearBtn: document.getElementById('clear-btn'),
            examplesContainer: document.getElementById('examples-container'),
            toolsContainer: document.getElementById('tools-container'),
            queryCountElement: document.getElementById('query-count'),
            toolsCountElement: document.getElementById('tools-count')
        };

        this.init();
    }

    /**
     * Initialize the application
     */
    init() {
        this.setupEventListeners();
        this.loadTools();
        this.loadExamples();
        this.checkHealth();
    }

    /**
     * Generate a unique session ID
     */
    generateSessionId() {
        return `session-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    }

    /**
     * Setup event listeners
     */
    setupEventListeners() {
        // Form submission
        this.elements.queryForm.addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleSubmit();
        });

        // Clear conversation
        this.elements.clearBtn.addEventListener('click', () => {
            this.clearConversation();
        });

        // Input focus
        this.elements.queryInput.focus();
    }

    /**
     * Check API health
     */
    async checkHealth() {
        try {
            const response = await fetch(`${this.apiBase}/health`);
            const data = await response.json();
            console.log('API Health:', data);
        } catch (error) {
            console.error('Health check failed:', error);
            this.showError('Unable to connect to API server');
        }
    }

    /**
     * Load available tools
     */
    async loadTools() {
        try {
            const response = await fetch(`${this.apiBase}/tools`);
            const data = await response.json();

            this.displayTools(data.tools);
            this.elements.toolsCountElement.textContent = data.tools.length;
        } catch (error) {
            console.error('Failed to load tools:', error);
            this.elements.toolsContainer.innerHTML = '<div class="loading">Failed to load tools</div>';
        }
    }

    /**
     * Load example queries
     */
    async loadExamples() {
        try {
            const response = await fetch(`${this.apiBase}/examples`);
            const data = await response.json();

            this.displayExamples(data.examples);
        } catch (error) {
            console.error('Failed to load examples:', error);
            this.elements.examplesContainer.innerHTML = '<div class="loading">Failed to load examples</div>';
        }
    }

    /**
     * Display tools in sidebar
     */
    displayTools(tools) {
        this.elements.toolsContainer.innerHTML = tools.map(tool => `
            <div class="tool-card">
                <h4>${tool.name}</h4>
                <p>${tool.description}</p>
                <div class="tool-keywords">
                    ${tool.keywords.slice(0, 4).map(kw => `<span class="keyword">${kw}</span>`).join('')}
                </div>
            </div>
        `).join('');
    }

    /**
     * Display examples in sidebar
     */
    displayExamples(examples) {
        this.elements.examplesContainer.innerHTML = examples.map(category => `
            <div class="example-category">
                <div class="category-title">
                    <span>${category.icon}</span>
                    <span>${category.category}</span>
                </div>
                ${category.queries.slice(0, 2).map(query => `
                    <div class="example-query" data-query="${this.escapeHtml(query)}">
                        ${query}
                    </div>
                `).join('')}
            </div>
        `).join('');

        // Add click handlers to example queries
        document.querySelectorAll('.example-query').forEach(el => {
            el.addEventListener('click', () => {
                this.elements.queryInput.value = el.dataset.query;
                this.elements.queryInput.focus();
            });
        });
    }

    /**
     * Handle form submission
     */
    async handleSubmit() {
        const query = this.elements.queryInput.value.trim();

        if (!query) {
            return;
        }

        // Clear input
        this.elements.queryInput.value = '';

        // Add user message
        this.addMessage('user', query);

        // Show loading state
        this.setLoading(true);

        try {
            const response = await fetch(`${this.apiBase}/estimate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    query: query,
                    session_id: this.sessionId
                })
            });

            const data = await response.json();

            if (data.success) {
                this.addMessage('assistant', data.message, data.tool_used);
                this.queryCount++;
                this.elements.queryCountElement.textContent = this.queryCount;
            } else {
                this.addMessage('assistant', `Error: ${data.error}`);
            }
        } catch (error) {
            console.error('Estimation failed:', error);
            this.addMessage('assistant', 'Sorry, I encountered an error processing your request.');
        } finally {
            this.setLoading(false);
            this.elements.queryInput.focus();
        }
    }

    /**
     * Add a message to the chat
     */
    addMessage(role, content, toolUsed = null) {
        // Remove welcome message if present
        const welcomeMsg = this.elements.messages.querySelector('.welcome-message');
        if (welcomeMsg) {
            welcomeMsg.remove();
        }

        const messageDiv = document.createElement('div');
        messageDiv.className = `message message-${role}`;

        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';

        const label = document.createElement('div');
        label.className = 'message-label';
        label.textContent = role === 'user' ? 'You' : 'Agent';

        const text = document.createElement('div');
        text.className = 'message-text';
        text.textContent = content;

        contentDiv.appendChild(label);
        contentDiv.appendChild(text);

        if (role === 'assistant' && toolUsed) {
            const meta = document.createElement('div');
            meta.className = 'message-meta';
            meta.textContent = `Tool: ${toolUsed}`;
            contentDiv.appendChild(meta);
        }

        messageDiv.appendChild(contentDiv);
        this.elements.messages.appendChild(messageDiv);

        // Scroll to bottom
        this.scrollToBottom();
    }

    /**
     * Set loading state
     */
    setLoading(loading) {
        if (loading) {
            this.elements.sendBtn.disabled = true;
            this.elements.sendBtnText.style.display = 'none';
            this.elements.sendBtnLoader.style.display = 'block';
            this.elements.queryInput.disabled = true;
        } else {
            this.elements.sendBtn.disabled = false;
            this.elements.sendBtnText.style.display = 'block';
            this.elements.sendBtnLoader.style.display = 'none';
            this.elements.queryInput.disabled = false;
        }
    }

    /**
     * Clear conversation
     */
    async clearConversation() {
        if (!confirm('Clear conversation history?')) {
            return;
        }

        try {
            await fetch(`${this.apiBase}/session/clear`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    session_id: this.sessionId
                })
            });

            // Clear messages
            this.elements.messages.innerHTML = `
                <div class="welcome-message">
                    <h2>👋 Welcome to AWS Cost Agent</h2>
                    <p>I can help you estimate AWS costs using natural language queries.</p>
                    <p>Try asking:</p>
                    <ul>
                        <li>"How much for 10 t3.medium instances?"</li>
                        <li>"Estimate RAG costs for 100 manuals"</li>
                        <li>"What would 5 million Lambda invocations cost?"</li>
                    </ul>
                </div>
            `;

            // Reset counter
            this.queryCount = 0;
            this.elements.queryCountElement.textContent = '0';

            // Generate new session
            this.sessionId = this.generateSessionId();
        } catch (error) {
            console.error('Failed to clear session:', error);
            alert('Failed to clear conversation');
        }
    }

    /**
     * Show error message
     */
    showError(message) {
        this.addMessage('assistant', `❌ Error: ${message}`);
    }

    /**
     * Scroll to bottom of messages
     */
    scrollToBottom() {
        this.elements.messages.scrollTop = this.elements.messages.scrollHeight;
    }

    /**
     * Escape HTML to prevent XSS
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize the application when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.costAgent = new CostAgentClient();
});
