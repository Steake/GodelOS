/**
 * Query Handler for GödelOS Frontend
 * Manages query form submission, validation, and response handling
 */

class QueryHandler {
    constructor() {
        this.currentQuery = null;
        this.queryHistory = [];
        this.isProcessing = false;
        
        this.initializeForm();
        this.setupEventListeners();
        this.setupResponseTabs();
    }

    /**
     * Initialize the query form
     */
    initializeForm() {
        // Set up confidence threshold display
        const confidenceSlider = document.getElementById('confidenceThreshold');
        const confidenceValue = document.getElementById('confidenceValue');
        
        if (confidenceSlider && confidenceValue) {
            confidenceSlider.addEventListener('input', (e) => {
                confidenceValue.textContent = e.target.value;
            });
        }

        // Initialize form with default values
        this.resetForm();
    }

    /**
     * Setup event listeners for form interactions
     */
    setupEventListeners() {
        // Submit query button
        const submitButton = document.getElementById('submitQuery');
        if (submitButton) {
            submitButton.addEventListener('click', (e) => {
                e.preventDefault();
                this.handleQuerySubmission();
            });
        }

        // Clear query button
        const clearButton = document.getElementById('clearQuery');
        if (clearButton) {
            clearButton.addEventListener('click', (e) => {
                e.preventDefault();
                this.clearForm();
            });
        }

        // Enter key submission
        const queryTextarea = document.getElementById('naturalLanguageQuery');
        if (queryTextarea) {
            queryTextarea.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' && e.ctrlKey) {
                    e.preventDefault();
                    this.handleQuerySubmission();
                }
            });
        }

        // Listen for query responses
        window.addEventListener('queryResponse', (e) => {
            this.handleQueryResponse(e.detail);
        });

        // Export results button
        const exportButton = document.getElementById('exportResults');
        if (exportButton) {
            exportButton.addEventListener('click', () => {
                this.exportResults();
            });
        }
    }

    /**
     * Setup response tabs functionality
     */
    setupResponseTabs() {
        const tabButtons = document.querySelectorAll('.tab-button');
        const tabPanes = document.querySelectorAll('.tab-pane');

        tabButtons.forEach(button => {
            button.addEventListener('click', () => {
                const targetTab = button.getAttribute('data-tab');
                
                // Remove active class from all tabs and panes
                tabButtons.forEach(btn => btn.classList.remove('active'));
                tabPanes.forEach(pane => pane.classList.remove('active'));
                
                // Add active class to clicked tab and corresponding pane
                button.classList.add('active');
                const targetPane = document.getElementById(`${targetTab}Tab`);
                if (targetPane) {
                    targetPane.classList.add('active');
                }
            });
        });
    }

    /**
     * Handle query form submission
     */
    async handleQuerySubmission() {
        if (this.isProcessing) {
            console.log('Query already being processed');
            return;
        }

        const queryData = this.collectFormData();
        
        // Validate form data
        if (!this.validateQuery(queryData)) {
            return;
        }

        // Set processing state
        this.setProcessingState(true);
        
        try {
            // Send query to backend via WebSocket
            this.sendQuery(queryData);
            
            // Add to history
            this.addToHistory(queryData);
            
            // Show processing indicators
            this.showProcessingIndicators();
            
        } catch (error) {
            console.error('Error submitting query:', error);
            this.showError('Failed to submit query. Please try again.');
            this.setProcessingState(false);
        }
    }

    /**
     * Collect form data
     * @returns {Object} Form data object
     */
    collectFormData() {
        const queryText = document.getElementById('naturalLanguageQuery')?.value || '';
        const queryType = document.getElementById('queryType')?.value || 'knowledge';
        const confidenceThreshold = parseFloat(document.getElementById('confidenceThreshold')?.value || '0.7');

        return {
            query: queryText.trim(),
            type: queryType,
            confidence_threshold: confidenceThreshold,
            timestamp: Date.now(),
            session_id: this.getSessionId()
        };
    }

    /**
     * Validate query data
     * @param {Object} queryData - Query data to validate
     * @returns {boolean} True if valid
     */
    validateQuery(queryData) {
        if (!queryData.query) {
            this.showError('Please enter a query');
            return false;
        }

        if (queryData.query.length < 3) {
            this.showError('Query must be at least 3 characters long');
            return false;
        }

        if (queryData.query.length > 1000) {
            this.showError('Query must be less than 1000 characters');
            return false;
        }

        return true;
    }

    /**
     * Send query to backend
     * @param {Object} queryData - Query data to send
     */
    async sendQuery(queryData) {
        this.currentQuery = queryData;
        
        try {
            // Send query via API client
            if (window.apiClient) {
                const response = await window.apiClient.processQuery(queryData.query, {
                    context: {
                        type: queryData.type,
                        confidence_threshold: queryData.confidence_threshold,
                        session_id: queryData.session_id
                    },
                    include_reasoning: true
                });
                
                // Handle the response directly
                this.handleQueryResponse({
                    query_id: Date.now(),
                    original_query: queryData.query,
                    natural_response: response.response,
                    formal_logic: `Confidence: ${(response.confidence * 100).toFixed(1)}% | Steps: ${response.reasoning_steps.length}`,
                    metadata: {
                        confidence: response.confidence,
                        processing_time: response.inference_time_ms,
                        sources_used: response.knowledge_used.length,
                        reasoning_steps: response.reasoning_steps.length
                    },
                    reasoning_trace: response.reasoning_steps.map((step, index) => ({
                        step: step.step_number || index + 1,
                        description: step.description,
                        confidence: step.confidence
                    }))
                });
                
            } else {
                console.error('API client not available');
                throw new Error('API client not available');
            }
        } catch (error) {
            console.error('Error sending query:', error);
            this.showError(`Query failed: ${error.message}`);
            this.setProcessingState(false);
            throw error;
        }
    }

    /**
     * Handle query response from backend
     * @param {Object} responseData - Response data
     */
    handleQueryResponse(responseData) {
        console.log('Received query response:', responseData);
        
        // Update response panels
        this.updateNaturalLanguageResponse(responseData.natural_response);
        this.updateFormalLogicResponse(responseData.formal_logic);
        this.updateMetadataResponse(responseData.metadata);
        this.updateReasoningTrace(responseData.reasoning_trace);
        
        // Clear processing state
        this.setProcessingState(false);
        
        // Show success indicator
        this.showSuccess('Query processed successfully');
        
        // Store response
        if (this.currentQuery) {
            this.currentQuery.response = responseData;
        }
    }

    /**
     * Update natural language response panel
     * @param {string} response - Natural language response
     */
    updateNaturalLanguageResponse(response) {
        const responseElement = document.getElementById('naturalResponse');
        if (responseElement) {
            responseElement.innerHTML = `<p>${response}</p>`;
            responseElement.classList.add('fade-in');
        }
    }

    /**
     * Update formal logic response panel
     * @param {string} formalLogic - Formal logic representation
     */
    updateFormalLogicResponse(formalLogic) {
        const formalElement = document.getElementById('formalResponse');
        if (formalElement) {
            formalElement.innerHTML = `<pre>${formalLogic}</pre>`;
            formalElement.classList.add('fade-in');
        }
    }

    /**
     * Update metadata response panel
     * @param {Object} metadata - Response metadata
     */
    updateMetadataResponse(metadata) {
        if (!metadata) return;

        // Update individual metadata fields
        this.updateMetadataField('responseConfidence', 
            metadata.confidence ? `${(metadata.confidence * 100).toFixed(1)}%` : '-');
        this.updateMetadataField('processingTime', 
            metadata.processing_time ? `${metadata.processing_time.toFixed(0)}ms` : '-');
        this.updateMetadataField('sourcesUsed', 
            metadata.sources_used ? metadata.sources_used.toString() : '-');
        this.updateMetadataField('reasoningSteps', 
            metadata.reasoning_steps ? metadata.reasoning_steps.toString() : '-');
    }

    /**
     * Update individual metadata field
     * @param {string} fieldId - Field element ID
     * @param {string} value - Field value
     */
    updateMetadataField(fieldId, value) {
        const fieldElement = document.getElementById(fieldId);
        if (fieldElement) {
            fieldElement.textContent = value;
            fieldElement.classList.add('fade-in');
        }
    }

    /**
     * Update reasoning trace panel
     * @param {Array} trace - Reasoning trace steps
     */
    updateReasoningTrace(trace) {
        const traceElement = document.getElementById('reasoningTrace');
        if (!traceElement || !trace) return;

        traceElement.innerHTML = '';
        
        const traceContainer = document.createElement('div');
        traceContainer.className = 'reasoning-chain';

        trace.forEach((step, index) => {
            const stepElement = document.createElement('div');
            stepElement.className = 'reasoning-step';
            stepElement.style.animationDelay = `${index * 0.2}s`;
            
            stepElement.innerHTML = `
                <div class="step-number">${step.step}</div>
                <div class="step-content">${step.description}</div>
                <div class="step-confidence">${(step.confidence * 100).toFixed(0)}%</div>
            `;
            
            traceContainer.appendChild(stepElement);
            
            // Animate step activation
            setTimeout(() => {
                stepElement.classList.add('active');
            }, index * 200);
        });

        traceElement.appendChild(traceContainer);
        traceElement.classList.add('fade-in');
    }

    /**
     * Show processing indicators
     */
    showProcessingIndicators() {
        // Update natural language panel with loading message
        const naturalResponse = document.getElementById('naturalResponse');
        if (naturalResponse) {
            naturalResponse.innerHTML = `
                <div class="loading-indicator">
                    <div class="loading-spinner"></div>
                    <p>Processing your query...</p>
                </div>
            `;
        }

        // Clear other panels
        const formalResponse = document.getElementById('formalResponse');
        if (formalResponse) {
            formalResponse.innerHTML = '<pre class="placeholder">Processing...</pre>';
        }

        // Reset metadata
        this.updateMetadataField('responseConfidence', 'Processing...');
        this.updateMetadataField('processingTime', 'Processing...');
        this.updateMetadataField('sourcesUsed', 'Processing...');
        this.updateMetadataField('reasoningSteps', 'Processing...');

        // Clear reasoning trace
        const reasoningTrace = document.getElementById('reasoningTrace');
        if (reasoningTrace) {
            reasoningTrace.innerHTML = '<div class="trace-placeholder">Building reasoning chain...</div>';
        }
    }

    /**
     * Set processing state
     * @param {boolean} processing - Whether currently processing
     */
    setProcessingState(processing) {
        this.isProcessing = processing;
        
        const submitButton = document.getElementById('submitQuery');
        const queryTextarea = document.getElementById('naturalLanguageQuery');
        
        if (submitButton) {
            submitButton.disabled = processing;
            submitButton.textContent = processing ? 'Processing...' : 'Submit Query';
            
            if (processing) {
                submitButton.classList.add('loading');
            } else {
                submitButton.classList.remove('loading');
            }
        }
        
        if (queryTextarea) {
            queryTextarea.disabled = processing;
        }
    }

    /**
     * Add query to history
     * @param {Object} queryData - Query data to add
     */
    addToHistory(queryData) {
        this.queryHistory.unshift(queryData);
        
        // Limit history size
        if (this.queryHistory.length > 50) {
            this.queryHistory = this.queryHistory.slice(0, 50);
        }
        
        // Store in localStorage
        try {
            localStorage.setItem('godelOS_query_history', JSON.stringify(this.queryHistory));
        } catch (error) {
            console.warn('Failed to save query history:', error);
        }
    }

    /**
     * Load query history from localStorage
     */
    loadHistory() {
        try {
            const stored = localStorage.getItem('godelOS_query_history');
            if (stored) {
                this.queryHistory = JSON.parse(stored);
            }
        } catch (error) {
            console.warn('Failed to load query history:', error);
            this.queryHistory = [];
        }
    }

    /**
     * Clear the query form
     */
    clearForm() {
        const queryTextarea = document.getElementById('naturalLanguageQuery');
        const queryType = document.getElementById('queryType');
        const confidenceSlider = document.getElementById('confidenceThreshold');
        const confidenceValue = document.getElementById('confidenceValue');
        
        if (queryTextarea) queryTextarea.value = '';
        if (queryType) queryType.value = 'knowledge';
        if (confidenceSlider) confidenceSlider.value = '0.7';
        if (confidenceValue) confidenceValue.textContent = '0.7';
        
        // Clear response panels
        this.clearResponsePanels();
    }

    /**
     * Reset form to initial state
     */
    resetForm() {
        this.clearForm();
        this.setProcessingState(false);
    }

    /**
     * Clear all response panels
     */
    clearResponsePanels() {
        const naturalResponse = document.getElementById('naturalResponse');
        const formalResponse = document.getElementById('formalResponse');
        const reasoningTrace = document.getElementById('reasoningTrace');
        
        if (naturalResponse) {
            naturalResponse.innerHTML = '<p class="placeholder">Submit a query to see the natural language response...</p>';
        }
        
        if (formalResponse) {
            formalResponse.innerHTML = '<pre class="placeholder">Formal logic representation will appear here...</pre>';
        }
        
        if (reasoningTrace) {
            reasoningTrace.innerHTML = '<div class="trace-placeholder">Reasoning trace will be displayed here...</div>';
        }
        
        // Reset metadata fields
        this.updateMetadataField('responseConfidence', '-');
        this.updateMetadataField('processingTime', '-');
        this.updateMetadataField('sourcesUsed', '-');
        this.updateMetadataField('reasoningSteps', '-');
    }

    /**
     * Export query results
     */
    exportResults() {
        if (!this.currentQuery || !this.currentQuery.response) {
            this.showError('No results to export');
            return;
        }

        const exportData = {
            query: this.currentQuery,
            response: this.currentQuery.response,
            timestamp: new Date().toISOString(),
            version: '1.0'
        };

        // Create downloadable JSON file
        const blob = new Blob([JSON.stringify(exportData, null, 2)], {
            type: 'application/json'
        });
        
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `godelos_query_${Date.now()}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        this.showSuccess('Results exported successfully');
    }

    /**
     * Show error message
     * @param {string} message - Error message
     */
    showError(message) {
        this.showNotification(message, 'error');
    }

    /**
     * Show success message
     * @param {string} message - Success message
     */
    showSuccess(message) {
        this.showNotification(message, 'success');
    }

    /**
     * Show notification
     * @param {string} message - Notification message
     * @param {string} type - Notification type ('error', 'success', 'info')
     */
    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification ${type} fade-in`;
        notification.textContent = message;
        
        // Style notification
        Object.assign(notification.style, {
            position: 'fixed',
            top: '20px',
            right: '20px',
            padding: '1rem 1.5rem',
            borderRadius: '8px',
            color: 'white',
            fontWeight: '500',
            zIndex: '1000',
            maxWidth: '300px',
            wordWrap: 'break-word'
        });
        
        // Set background color based on type
        const colors = {
            error: '#ff4757',
            success: '#2ed573',
            info: '#4facfe'
        };
        notification.style.background = colors[type] || colors.info;
        
        // Add to DOM
        document.body.appendChild(notification);
        
        // Remove after delay
        setTimeout(() => {
            notification.classList.add('fade-out');
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }, 3000);
    }

    /**
     * Get or create session ID
     * @returns {string} Session ID
     */
    getSessionId() {
        let sessionId = sessionStorage.getItem('godelOS_session_id');
        if (!sessionId) {
            sessionId = 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
            sessionStorage.setItem('godelOS_session_id', sessionId);
        }
        return sessionId;
    }

    /**
     * Initialize the query handler
     */
    initialize() {
        this.loadHistory();
        console.log('Query handler initialized');
    }
}

// Create global query handler instance
window.queryHandler = new QueryHandler();

// Initialize when DOM is loaded
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.queryHandler.initialize();
    });
} else {
    window.queryHandler.initialize();
}