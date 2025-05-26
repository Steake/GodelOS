/**
 * API Client for GödelOS Frontend
 * Handles HTTP requests to the backend API endpoints
 */

class APIClient {
    constructor(baseUrl = 'http://localhost:8000') {
        this.baseUrl = baseUrl;
        this.defaultHeaders = {
            'Content-Type': 'application/json',
        };
    }

    /**
     * Make a generic API request
     * @param {string} endpoint - API endpoint
     * @param {Object} options - Request options
     * @returns {Promise<Object>} Response data
     */
    async request(endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;
        const config = {
            headers: { ...this.defaultHeaders, ...options.headers },
            ...options
        };

        try {
            console.log(`API Request: ${config.method || 'GET'} ${url}`);
            const response = await fetch(url, config);
            
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(`API Error ${response.status}: ${errorData.detail || response.statusText}`);
            }

            const data = await response.json();
            console.log(`API Response: ${config.method || 'GET'} ${url}`, data);
            return data;
            
        } catch (error) {
            console.error(`API Request failed: ${config.method || 'GET'} ${url}`, error);
            throw error;
        }
    }

    /**
     * Process a natural language query
     * @param {string} query - Natural language query
     * @param {Object} options - Query options
     * @returns {Promise<Object>} Query response
     */
    async processQuery(query, options = {}) {
        const requestData = {
            query: query,
            context: options.context || null,
            include_reasoning: options.include_reasoning !== false
        };

        return await this.request('/api/query', {
            method: 'POST',
            body: JSON.stringify(requestData)
        });
    }

    /**
     * Get knowledge base information
     * @param {Object} filters - Knowledge filters
     * @returns {Promise<Object>} Knowledge response
     */
    async getKnowledge(filters = {}) {
        const params = new URLSearchParams();
        
        if (filters.context_id) params.append('context_id', filters.context_id);
        if (filters.knowledge_type) params.append('knowledge_type', filters.knowledge_type);
        if (filters.limit) params.append('limit', filters.limit.toString());

        const endpoint = `/api/knowledge${params.toString() ? '?' + params.toString() : ''}`;
        return await this.request(endpoint);
    }

    /**
     * Add knowledge to the system
     * @param {Object} knowledgeData - Knowledge to add
     * @returns {Promise<Object>} Add knowledge response
     */
    async addKnowledge(knowledgeData) {
        const requestData = {
            content: knowledgeData.content,
            knowledge_type: knowledgeData.knowledge_type || 'fact',
            context_id: knowledgeData.context_id || null,
            metadata: knowledgeData.metadata || null
        };

        return await this.request('/api/knowledge', {
            method: 'POST',
            body: JSON.stringify(requestData)
        });
    }

    /**
     * Get current cognitive state
     * @returns {Promise<Object>} Cognitive state response
     */
    async getCognitiveState() {
        return await this.request('/api/cognitive-state');
    }

    /**
     * Check system health
     * @returns {Promise<Object>} Health status
     */
    async getHealthStatus() {
        return await this.request('/health');
    }

    /**
     * Get system information
     * @returns {Promise<Object>} System info
     */
    async getSystemInfo() {
        return await this.request('/');
    }
}

// Create global API client instance
window.apiClient = new APIClient();

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = APIClient;
}