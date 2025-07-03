/**
 * WebSocket Connection Manager for GödelOS Frontend
 * Handles real-time communication with the backend system
 */

class WebSocketManager {
    constructor() {
        this.socket = null;
        this.connectionStatus = 'disconnected';
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 1000;
        this.eventHandlers = new Map();
        this.messageQueue = [];
        
        this.initializeEventHandlers();
    }

    /**
     * Initialize default event handlers
     */
    initializeEventHandlers() {
        this.on('connect', () => {
            console.log('WebSocket connected to GödelOS backend');
            this.updateConnectionStatus('connected');
            this.reconnectAttempts = 0;
            this.flushMessageQueue();
        });

        this.on('disconnect', () => {
            console.log('WebSocket disconnected from GödelOS backend');
            this.updateConnectionStatus('disconnected');
            this.attemptReconnect();
        });

        this.on('error', (error) => {
            console.error('WebSocket error:', error);
            this.updateConnectionStatus('error');
        });

        this.on('query_response', (data) => {
            this.handleQueryResponse(data);
        });

        this.on('cognitive_update', (data) => {
            this.handleCognitiveUpdate(data);
        });

        this.on('knowledge_update', (data) => {
            this.handleKnowledgeUpdate(data);
        });

        this.on('system_status', (data) => {
            this.handleSystemStatus(data);
        });

        // Cognitive Transparency Event Handlers
        this.on('reasoning-update', (data) => {
            this.handleReasoningUpdate(data);
        });

        this.on('knowledge-graph-update', (data) => {
            this.handleKnowledgeGraphUpdate(data);
        });

        this.on('uncertainty-update', (data) => {
            this.handleUncertaintyUpdate(data);
        });

        this.on('provenance-update', (data) => {
            this.handleProvenanceUpdate(data);
        });

        this.on('metacognition-update', (data) => {
            this.handleMetacognitionUpdate(data);
        });

        this.on('transparency-level-change', (data) => {
            this.handleTransparencyLevelChange(data);
        });

        // Add handler for cognitive_state_update messages
        this.on('cognitive_state_update', (data) => {
            this.handleCognitiveStateUpdate(data);
        });

        // Add handlers for knowledge ingestion events
        this.on('import_started', (data) => {
            this.handleImportStarted(data);
        });

        this.on('import_progress', (data) => {
            this.handleImportProgress(data);
        });

        this.on('import_completed', (data) => {
            this.handleImportCompleted(data);
        });

        this.on('import_failed', (data) => {
            this.handleImportFailed(data);
        });
    }

    /**
     * Connect to the WebSocket server
     * @param {string} url - WebSocket server URL
     */
    connect(url) { // Default URL removed to be set by caller
        if (!url) {
            console.error('WebSocket URL must be provided.');
            this.updateConnectionStatus('error');
            this.emit('error', { message: 'WebSocket URL not provided' });
            return;
        }
        try {
            console.log(`Attempting to connect to ${url}...`);
            
            // Create WebSocket connection to backend
            this.socket = new WebSocket(url);
            
            this.socket.onopen = () => {
                console.log('WebSocket connected to GödelOS backend');
                this.updateConnectionStatus('connected');
                this.reconnectAttempts = 0;
                this.flushMessageQueue();
                this.emit('connect');
            };
            
            this.socket.onclose = () => {
                console.log('WebSocket disconnected from GödelOS backend');
                this.updateConnectionStatus('disconnected');
                this.emit('disconnect');
            };
            
            this.socket.onerror = (error) => {
                console.error('WebSocket error:', error);
                this.updateConnectionStatus('error');
                this.emit('error', error);
            };
            
            this.socket.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    // Emit the raw event type from the server directly
                    if (data.type && this.eventHandlers.has(data.type)) {
                        this.emit(data.type, data.data || data); // Pass data.data if present, else the whole object
                    } else if (data.type) {
                        console.warn(`No explicit handler for WebSocket message type: ${data.type}. Emitting raw event.`);
                        this.emit(data.type, data.data || data); // Emit anyway for generic listeners
                    } else {
                        console.error('Received WebSocket message without a type:', data);
                    }
                } catch (error) {
                    console.error('Error parsing WebSocket message:', error);
                }
            };
            
        } catch (error) {
            console.error('Failed to connect to WebSocket:', error);
            this.updateConnectionStatus('error');
        }
    }

    /**
     * Handle incoming WebSocket messages from backend
     */
    handleWebSocketMessage(data) {
        console.log('Received WebSocket message:', data);
        // This method might become redundant or simplified if events are emitted directly in onmessage
        // For now, keep it for logging or specific pre-processing if needed.
        // However, the primary dispatch logic is now in this.socket.onmessage
        if (data.type && this.eventHandlers.has(data.type)) {
            // this.emit(data.type, data.data || data); // This line is now handled in onmessage
        } else {
            // console.warn('⚠️ Unknown WebSocket message type in handleWebSocketMessage (should be handled by onmessage):', data.type);
        }
    }

    /**
     * Start simulated real-time updates for demo
     */
    startSimulatedUpdates() {
        // Simulate cognitive layer updates every 3 seconds
        setInterval(() => {
            if (this.connectionStatus === 'connected') {
                this.emit('cognitive_update', this.generateMockCognitiveData());
            }
        }, 3000);

        // Simulate system status updates every 5 seconds
        setInterval(() => {
            if (this.connectionStatus === 'connected') {
                this.emit('system_status', this.generateMockSystemStatus());
            }
        }, 5000);
    }

    /**
     * Generate mock cognitive data for demo
     */
    generateMockCognitiveData() {
        const processes = [
            'Query Parser', 'Knowledge Retriever', 'Inference Engine', 
            'Response Generator', 'Meta-Reasoner'
        ];
        
        const daemons = [
            'Memory Consolidation', 'Background Learning', 'System Monitoring',
            'Knowledge Indexing', 'Pattern Recognition'
        ];

        return {
            timestamp: Date.now(),
            manifest_consciousness: {
                attention_focus: Math.random() * 100,
                working_memory: [
                    'Current Query Processing',
                    'Active Knowledge Retrieval',
                    'Reasoning Chain Construction'
                ].slice(0, Math.floor(Math.random() * 3) + 1)
            },
            agentic_processes: processes.map(name => ({
                name,
                status: Math.random() > 0.7 ? 'active' : 'idle',
                cpu_usage: Math.random() * 100,
                memory_usage: Math.random() * 100
            })),
            daemon_threads: daemons.map(name => ({
                name,
                active: Math.random() > 0.5,
                activity_level: Math.random() * 100
            }))
        };
    }

    /**
     * Generate mock system status for demo
     */
    generateMockSystemStatus() {
        return {
            timestamp: Date.now(),
            system_load: Math.random() * 100,
            memory_usage: Math.random() * 100,
            knowledge_base_size: Math.floor(Math.random() * 10000) + 50000,
            active_queries: Math.floor(Math.random() * 10),
            inference_speed: Math.random() * 1000 + 100
        };
    }

    /**
     * Disconnect from the WebSocket server
     */
    disconnect() {
        if (this.socket) {
            this.socket.close();
            this.socket = null;
        }
        this.updateConnectionStatus('disconnected');
    }

    /**
     * Send a message to the server
     * @param {string} event - Event name
     * @param {Object} data - Data to send
     */
    send(event, data) {
        if (this.connectionStatus === 'connected' && this.socket) {
            const message = {
                type: event,
                timestamp: Date.now(),
                data: data
            };
            
            console.log(`Sending ${event}:`, data);
            this.socket.send(JSON.stringify(message));
        } else {
            // Queue message for when connection is restored
            this.messageQueue.push({ event, data });
            console.log(`Queued message ${event} (not connected)`);
        }
    }

    /**
     * Simulate server responses for demo
     */
    simulateResponse(event, data) {
        switch (event) {
            case 'submit_query':
                setTimeout(() => {
                    this.emit('query_response', this.generateMockQueryResponse(data));
                }, 2000);
                break;
            
            case 'request_knowledge_graph':
                setTimeout(() => {
                    this.emit('knowledge_update', this.generateMockKnowledgeGraph());
                }, 1000);
                break;
        }
    }

    /**
     * Generate mock query response
     */
    generateMockQueryResponse(queryData) {
        const responses = [
            "Based on the knowledge graph analysis, I found several relevant concepts related to your query.",
            "The inference engine has processed your request and identified key relationships in the knowledge base.",
            "After analyzing the semantic network, I can provide the following insights about your question.",
            "The reasoning system has evaluated multiple pathways to arrive at this conclusion."
        ];

        return {
            query_id: Date.now(),
            original_query: queryData.query,
            natural_response: responses[Math.floor(Math.random() * responses.length)],
            formal_logic: `∀x (Query(x) → Response(x)) ∧ Confidence(${(Math.random() * 0.3 + 0.7).toFixed(2)})`,
            metadata: {
                confidence: Math.random() * 0.3 + 0.7,
                processing_time: Math.random() * 2000 + 500,
                sources_used: Math.floor(Math.random() * 10) + 5,
                reasoning_steps: Math.floor(Math.random() * 8) + 3
            },
            reasoning_trace: [
                { step: 1, description: "Parse natural language query", confidence: 0.95 },
                { step: 2, description: "Identify key concepts and entities", confidence: 0.88 },
                { step: 3, description: "Search knowledge base for relevant information", confidence: 0.92 },
                { step: 4, description: "Apply inference rules and reasoning", confidence: 0.85 },
                { step: 5, description: "Generate natural language response", confidence: 0.91 }
            ]
        };
    }

    /**
     * Generate mock knowledge graph data
     */
    generateMockKnowledgeGraph() {
        const nodes = [
            { id: 'concept1', label: 'Artificial Intelligence', type: 'concept', x: 100, y: 100 },
            { id: 'concept2', label: 'Machine Learning', type: 'concept', x: 200, y: 150 },
            { id: 'concept3', label: 'Neural Networks', type: 'concept', x: 300, y: 100 },
            { id: 'concept4', label: 'Deep Learning', type: 'concept', x: 250, y: 200 },
            { id: 'instance1', label: 'GPT Model', type: 'instance', x: 400, y: 150 },
            { id: 'relation1', label: 'is-a', type: 'relation', x: 150, y: 125 }
        ];

        const links = [
            { source: 'concept2', target: 'concept1', label: 'is-a' },
            { source: 'concept3', target: 'concept2', label: 'implements' },
            { source: 'concept4', target: 'concept3', label: 'uses' },
            { source: 'instance1', target: 'concept4', label: 'instance-of' }
        ];

        return { nodes, links };
    }

    /**
     * Register an event handler
     * @param {string} event - Event name
     * @param {Function} handler - Event handler function
     */
    on(event, handler) {
        if (!this.eventHandlers.has(event)) {
            this.eventHandlers.set(event, []);
        }
        this.eventHandlers.get(event).push(handler);
    }

    /**
     * Remove an event handler
     * @param {string} event - Event name
     * @param {Function} handler - Event handler function
     */
    off(event, handler) {
        if (this.eventHandlers.has(event)) {
            const handlers = this.eventHandlers.get(event);
            const index = handlers.indexOf(handler);
            if (index > -1) {
                handlers.splice(index, 1);
            }
        }
    }

    /**
     * Emit an event
     * @param {string} event - Event name
     * @param {*} data - Event data
     */
    emit(event, data) {
        if (this.eventHandlers.has(event)) {
            this.eventHandlers.get(event).forEach(handler => {
                try {
                    handler(data);
                } catch (error) {
                    console.error(`Error in event handler for ${event}:`, error);
                }
            });
        }
    }

    /**
     * Update connection status in UI
     * @param {string} status - Connection status
     */
    updateConnectionStatus(status) {
        this.connectionStatus = status;
        
        const statusElement = document.getElementById('connectionStatus');
        const statusDot = statusElement?.querySelector('.status-dot');
        const statusText = statusElement?.querySelector('.status-text');
        
        if (statusDot && statusText) {
            statusDot.className = `status-dot ${status}`;
            statusText.textContent = status.charAt(0).toUpperCase() + status.slice(1);
        }
    }

    /**
     * Attempt to reconnect to the server
     */
    attemptReconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`);
            
            setTimeout(() => {
                this.connect();
            }, this.reconnectDelay * this.reconnectAttempts);
        } else {
            console.log('Max reconnection attempts reached');
            this.updateConnectionStatus('failed');
        }
    }

    /**
     * Flush queued messages when connection is restored
     */
    flushMessageQueue() {
        while (this.messageQueue.length > 0) {
            const { event, data } = this.messageQueue.shift();
            this.send(event, data);
        }
    }

    /**
     * Handle query response from server
     * @param {Object} data - Query response data
     */
    handleQueryResponse(data) {
        // Emit custom event for query handler
        window.dispatchEvent(new CustomEvent('queryResponse', { detail: data }));
    }

    /**
     * Handle cognitive layer updates
     * @param {Object} data - Cognitive update data
     */
    handleCognitiveUpdate(data) {
        // Emit custom event for cognitive layers handler
        window.dispatchEvent(new CustomEvent('cognitiveUpdate', { detail: data }));
    }

    /**
     * Handle knowledge graph updates
     * @param {Object} data - Knowledge update data
     */
    handleKnowledgeUpdate(data) {
        // Emit custom event for visualization handler
        window.dispatchEvent(new CustomEvent('knowledgeUpdate', { detail: data }));
    }

    /**
     * Handle system status updates
     * @param {Object} data - System status data
     */
    handleSystemStatus(data) {
        const systemStatusElement = document.getElementById('systemStatus');
        const statusText = systemStatusElement?.querySelector('.status-text');
        
        if (statusText) {
            const load = Math.round(data.system_load);
            statusText.textContent = `System: ${load}% load, ${data.active_queries} active queries`;
        }
    }

    // ===== COGNITIVE TRANSPARENCY EVENT HANDLERS =====

    /**
     * Handle reasoning updates from transparency WebSocket
     * @param {Object} data - Reasoning update data
     */
    handleReasoningUpdate(data) {
        // Emit custom event for reasoning visualizer
        window.dispatchEvent(new CustomEvent('reasoningUpdate', { detail: data }));
    }

    /**
     * Handle knowledge graph updates from transparency WebSocket
     * @param {Object} data - Knowledge graph update data
     */
    handleKnowledgeGraphUpdate(data) {
        // Emit custom event for knowledge graph visualizer
        window.dispatchEvent(new CustomEvent('knowledgeGraphUpdate', { detail: data }));
    }

    /**
     * Handle uncertainty updates from transparency WebSocket
     * @param {Object} data - Uncertainty update data
     */
    handleUncertaintyUpdate(data) {
        // Emit custom event for uncertainty visualizer
        window.dispatchEvent(new CustomEvent('uncertaintyUpdate', { detail: data }));
    }

    /**
     * Handle provenance updates from transparency WebSocket
     * @param {Object} data - Provenance update data
     */
    handleProvenanceUpdate(data) {
        // Emit custom event for provenance explorer
        window.dispatchEvent(new CustomEvent('provenanceUpdate', { detail: data }));
    }

    /**
     * Handle metacognition updates from transparency WebSocket
     * @param {Object} data - Metacognition update data
     */
    handleMetacognitionUpdate(data) {
        // Emit custom event for metacognitive dashboard
        window.dispatchEvent(new CustomEvent('metacognitionUpdate', { detail: data }));
    }

    /**
     * Handle transparency level changes
     * @param {Object} data - Transparency level change data
     */
    handleTransparencyLevelChange(data) {
        // Emit custom event for all transparency components
        window.dispatchEvent(new CustomEvent('transparencyLevelChange', { detail: data }));
    }

    /**
     * Handle cognitive state updates from transparency WebSocket
     * @param {Object} data - Cognitive state update data
     */
    handleCognitiveStateUpdate(data) {
        // Emit custom event for cognitive layer updates
        window.dispatchEvent(new CustomEvent('cognitiveStateUpdate', { detail: data }));
        
        // Also trigger the general cognitive update handler for backward compatibility
        this.handleCognitiveUpdate(data);
    }

    /**
     * Handle import started events
     * @param {Object} data - Import started data
     */
    handleImportStarted(data) {
        console.log('🔍 IMPORT: Import started:', data);
        window.dispatchEvent(new CustomEvent('importStarted', { detail: data }));
    }

    /**
     * Handle import progress events
     * @param {Object} data - Import progress data
     */
    handleImportProgress(data) {
        console.log('🔍 IMPORT: Import progress:', data);
        window.dispatchEvent(new CustomEvent('importProgress', { detail: data }));
    }

    /**
     * Handle import completed events
     * @param {Object} data - Import completed data
     */
    handleImportCompleted(data) {
        console.log('🔍 IMPORT: Import completed:', data);
        window.dispatchEvent(new CustomEvent('importCompleted', { detail: data }));
    }

    /**
     * Handle import failed events
     * @param {Object} data - Import failed data
     */
    handleImportFailed(data) {
        console.log('🔍 IMPORT: Import failed:', data);
        window.dispatchEvent(new CustomEvent('importFailed', { detail: data }));
    }

    /**
     * Check if WebSocket is connected
     * @returns {boolean} Connection status
     */
    isConnected() {
        return this.connectionStatus === 'connected' && this.socket && this.socket.readyState === WebSocket.OPEN;
    }

    /**
     * Send ping to check connection latency
     * @returns {Promise<number>} Latency in milliseconds
     */
    ping() {
        return new Promise((resolve, reject) => {
            if (!this.isConnected()) {
                reject(new Error('WebSocket not connected'));
                return;
            }

            const startTime = Date.now();
            const pingId = Math.random().toString(36).substr(2, 9);

            const handlePong = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    if (data.type === 'pong' && data.pingId === pingId) {
                        this.socket.removeEventListener('message', handlePong);
                        resolve(Date.now() - startTime);
                    }
                } catch (error) {
                    // Ignore parsing errors for other messages
                }
            };

            this.socket.addEventListener('message', handlePong);

            // Send ping
            this.send('ping', { pingId, timestamp: startTime });

            // Timeout after 5 seconds
            setTimeout(() => {
                this.socket.removeEventListener('message', handlePong);
                reject(new Error('Ping timeout'));
            }, 5000);
        });
    }

    /**
     * Send heartbeat to keep connection alive
     * This method is called by main.js heartbeat system
     */
    sendHeartbeat() {
        if (this.isConnected()) {
            this.send('heartbeat', {
                timestamp: Date.now(),
                client_id: 'godelos-frontend'
            });
            console.log('🔍 HEARTBEAT: Sent heartbeat to server');
        } else {
            console.log('🔍 HEARTBEAT: Connection not available, skipping heartbeat');
        }
    }
}

// Make the class available globally
window.WebSocketManager = WebSocketManager;

console.log('✅ WebSocketManager module loaded and available as window.WebSocketManager');

// Create global WebSocket manager instance
window.wsManager = new WebSocketManager();
// Use the working cognitive-stream endpoint directly
const wsUrl = 'ws://localhost:8000/ws/cognitive-stream';
window.wsManager.connect(wsUrl);
console.log('Global WebSocketManager initialized and connected to cognitive-stream.');