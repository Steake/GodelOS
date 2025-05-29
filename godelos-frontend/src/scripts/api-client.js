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
            
            // Add diagnostic logging for empty data responses
            this.validateAPIResponse(url, data, config.method || 'GET');
            
            return data;
            
        } catch (error) {
            console.error(`API Request failed: ${config.method || 'GET'} ${url}`, error);
            throw error;
        }
    }

    /**
     * Make a GET request
     * @param {string} endpoint - API endpoint
     * @param {Object} options - Request options
     * @returns {Promise<Object>} Response data
     */
    async get(endpoint, options = {}) {
        return await this.request(endpoint, {
            method: 'GET',
            ...options
        });
    }

    /**
     * Make a POST request
     * @param {string} endpoint - API endpoint
     * @param {Object} data - Request body data
     * @param {Object} options - Request options
     * @returns {Promise<Object>} Response data
     */
    async post(endpoint, data = {}, options = {}) {
        return await this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(data),
            ...options
        });
    }

    /**
     * Make a PUT request
     * @param {string} endpoint - API endpoint
     * @param {Object} data - Request body data
     * @param {Object} options - Request options
     * @returns {Promise<Object>} Response data
     */
    async put(endpoint, data = {}, options = {}) {
        return await this.request(endpoint, {
            method: 'PUT',
            body: JSON.stringify(data),
            ...options
        });
    }

    /**
     * Make a DELETE request
     * @param {string} endpoint - API endpoint
     * @param {Object} options - Request options
     * @returns {Promise<Object>} Response data
     */
    async delete(endpoint, options = {}) {
        return await this.request(endpoint, {
            method: 'DELETE',
            ...options
        });
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

    // ===== COGNITIVE TRANSPARENCY API METHODS =====

    /**
     * Get knowledge graph data
     * @param {Object} options - Graph options
     * @returns {Promise<Object>} Knowledge graph response
     */
    async getKnowledgeGraph(options = {}) {
        // Use the transparency knowledge graph export endpoint
        try {
            const data = await this.request('/api/transparency/knowledge-graph/export');
            
            // The transparency endpoint returns data in the correct format already
            if (data && data.graph_data && data.graph_data.nodes && data.graph_data.edges) {
                return {
                    graph_data: {
                        nodes: data.graph_data.nodes,
                        links: data.graph_data.edges  // Convert edges to links for consistency
                    },
                    statistics: data.statistics || {
                        node_count: data.graph_data.nodes.length,
                        link_count: data.graph_data.edges.length,
                        total_count: data.graph_data.nodes.length + data.graph_data.edges.length
                    },
                    metadata: data.metadata || {}
                };
            }
            
            // Fallback to empty graph if no data
            return {
                graph_data: {
                    nodes: [],
                    links: []
                },
                statistics: {
                    node_count: 0,
                    link_count: 0,
                    total_count: 0
                }
            };
        } catch (error) {
            console.warn('Failed to fetch knowledge graph data, using fallback:', error);
            return {
                graph_data: {
                    nodes: [],
                    links: []
                },
                statistics: {
                    node_count: 0,
                    link_count: 0,
                    total_count: 0
                }
            };
        }
    }

    /**
     * Get knowledge graph statistics
     * @returns {Promise<Object>} Knowledge graph statistics
     */
    async getKnowledgeGraphStatistics() {
        return await this.request('/api/transparency/knowledge-graph/statistics');
    }

    /**
     * Analyze uncertainty for given targets
     * @param {Array} targetIds - Array of target IDs to analyze
     * @param {Object} options - Analysis options
     * @returns {Promise<Object>} Uncertainty analysis response
     */
    async analyzeUncertainty(targetIds, options = {}) {
        // Use the first target ID and match backend expected format
        const targetId = Array.isArray(targetIds) ? targetIds[0] : targetIds;
        const requestData = {
            target_id: targetId || 'default',
            target_type: options.target_type || 'step',
            context: options.context || {}
        };

        return await this.request('/api/transparency/uncertainty/analyze', {
            method: 'POST',
            body: JSON.stringify(requestData)
        });
    }

    /**
     * Get uncertainty visualization data
     * @param {Array} targetIds - Array of target IDs
     * @returns {Promise<Object>} Uncertainty visualization data
     */
    async getUncertaintyVisualization(targetIds) {
        const targetIdsStr = targetIds.join(',');
        return await this.request(`/api/transparency/uncertainty/visualization/${targetIdsStr}`);
    }

    /**
     * Query provenance information
     * @param {Object} queryParams - Provenance query parameters
     * @returns {Promise<Object>} Provenance query response
     */
    async queryProvenance(queryParams) {
        const requestData = {
            target_id: queryParams.entity_id || queryParams.target_id || 'default',
            query_type: queryParams.query_type || 'backward_trace',
            max_depth: queryParams.depth || queryParams.max_depth || 5,
            time_window_start: queryParams.time_range?.start || null,
            time_window_end: queryParams.time_range?.end || null
        };

        return await this.request('/api/transparency/provenance/query', {
            method: 'POST',
            body: JSON.stringify(requestData)
        });
    }

    /**
     * Get attribution information for a target
     * @param {string} targetId - Target ID for attribution
     * @returns {Promise<Object>} Attribution response
     */
    async getAttribution(targetId) {
        return await this.request(`/api/transparency/provenance/attribution/${targetId}`);
    }

    /**
     * Get learning system status
     * @returns {Promise<Object>} Learning status response
     */
    async getLearningStatus() {
        return await this.request('/api/transparency/learning/status');
    }

    /**
     * Get learning recommendations
     * @param {Object} context - Context for recommendations
     * @returns {Promise<Object>} Learning recommendations response
     */
    async getLearningRecommendations(context = {}) {
        return await this.request('/api/transparency/learning/recommendations', {
            method: 'POST',
            body: JSON.stringify(context)
        });
    }

    /**
     * Create a new transparency session
     * @param {Object} sessionConfig - Session configuration
     * @returns {Promise<Object>} Session creation response
     */
    async createSession(sessionConfig) {
        const requestData = {
            name: sessionConfig.name || 'Unnamed Session',
            transparency_level: sessionConfig.transparency_level || 'standard',
            components: sessionConfig.components || ['reasoning', 'knowledge', 'uncertainty'],
            metadata: sessionConfig.metadata || {}
        };

        return await this.request('/api/transparency/session/create', {
            method: 'POST',
            body: JSON.stringify(requestData)
        });
    }

    /**
     * Get session information
     * @param {string} sessionId - Session ID
     * @returns {Promise<Object>} Session information
     */
    async getSession(sessionId) {
        return await this.request(`/api/transparency/session/${sessionId}`);
    }

    /**
     * Update session configuration
     * @param {string} sessionId - Session ID
     * @param {Object} updates - Configuration updates
     * @returns {Promise<Object>} Update response
     */
    async updateSession(sessionId, updates) {
        return await this.request(`/api/transparency/session/${sessionId}`, {
            method: 'PUT',
            body: JSON.stringify(updates)
        });
    }

    /**
     * End a transparency session
     * @param {string} sessionId - Session ID
     * @returns {Promise<Object>} End session response
     */
    async endSession(sessionId) {
        return await this.request(`/api/transparency/session/${sessionId}/end`, {
            method: 'POST'
        });
    }

    /**
     * Validate API response for empty or problematic data
     * @param {string} url - Request URL
     * @param {Object} data - Response data
     * @param {string} method - HTTP method
     */
    validateAPIResponse(url, data, method) {
        // Check for common empty data patterns
        if (url.includes('/knowledge-graph/export')) {
            if (data.node_count === 0 && data.edge_count === 0) {
                console.warn('⚠️ DIAGNOSTIC: Knowledge graph export returned empty data:', {
                    url, node_count: data.node_count, edge_count: data.edge_count
                });
            }
        }
        
        if (url.includes('/uncertainty/analyze')) {
            if (Object.keys(data.uncertainty_metrics || {}).length === 0) {
                console.warn('⚠️ DIAGNOSTIC: Uncertainty analysis returned empty metrics:', {
                    url, uncertainty_metrics: data.uncertainty_metrics
                });
            }
        }
        
        if (url.includes('/provenance/query')) {
            if (!data.results || Object.keys(data.results).length === 0) {
                console.warn('⚠️ DIAGNOSTIC: Provenance query returned empty results:', {
                    url, results: data.results
                });
            }
        }
        
        if (url.includes('/knowledge/categories')) {
            if (!data.categories || data.categories.length === 0) {
                console.warn('⚠️ DIAGNOSTIC: Knowledge categories returned empty array:', {
                    url, categories: data.categories
                });
            }
        }
        
        if (url.includes('/knowledge/statistics')) {
            const stats = data.statistics || {};
            if (Object.keys(stats).length === 0) {
                console.warn('⚠️ DIAGNOSTIC: Knowledge statistics returned empty object:', {
                    url, statistics: stats
                });
            }
        }
    }
}

// Make the class available globally
window.APIClient = APIClient;

// Create global API client instance
window.apiClient = new APIClient();

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = APIClient;
}

console.log('✅ APIClient module loaded and available as window.APIClient');