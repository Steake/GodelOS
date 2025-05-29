/**
 * GödelOS Main Application Controller
 *
 * Enhanced main application controller that integrates the new adaptive interface
 * system with all existing functionality
 */

// Debug: Track script loading
console.log('🔍 DEBUG: Main.js loading...');
console.log('🔍 DEBUG: Available window objects at main.js load:', Object.keys(window).filter(k =>
    k.includes('API') || k.includes('Client') || k.includes('WebSocket') || k.includes('Query') ||
    k.includes('Handler') || k.includes('Cognitive') || k.includes('Educational') || k.includes('Manager')
));

class GödelOSApp {
    constructor() {
        this.isInitialized = false;
        this.modules = new Map();
        this.eventListeners = new Map();
        this.config = {
            apiBaseUrl: 'http://localhost:8000',
            wsBaseUrl: 'ws://localhost:8000',
            retryAttempts: 3,
            retryDelay: 1000,
            heartbeatInterval: 30000
        };
        
        this.state = {
            isConnected: false,
            currentQuery: null,
            lastResponse: null,
            cognitiveState: null,
            complexityLevel: 'intermediate'
        };
        
        console.log('🚀 GödelOS Application Controller initialized');
    }

    /**
     * Initialize the application
     */
    async init() {
        if (this.isInitialized) {
            console.warn('Application already initialized');
            return;
        }

        try {
            console.log('🔄 Initializing GödelOS Application...');
            
            // Wait for DOM to be ready
            if (document.readyState === 'loading') {
                await new Promise(resolve => {
                    document.addEventListener('DOMContentLoaded', resolve);
                });
            }

            // Initialize core modules in order
            await this.initializeAdaptiveInterface();
            await this.initializeAPIClient();
            await this.initializeWebSocket();
            await this.initializeQueryHandler();
            await this.initializeVisualization();
            await this.initializeCognitiveLayers();
            await this.initializeKnowledgeManagement();
            await this.initializeEducationalFeatures();
            
            // Setup event handlers
            this.setupEventHandlers();
            this.setupKeyboardShortcuts();
            this.setupErrorHandling();
            
            // Initialize UI components
            this.initializeUIComponents();
            
            // Run backend diagnostics
            await this.runBackendDiagnostics();
            
            // Start application services
            this.startServices();
            
            this.isInitialized = true;
            console.log('✅ GödelOS Application successfully initialized');
            
            // Dispatch initialization complete event
            this.dispatchEvent('appInitialized', {
                timestamp: Date.now(),
                modules: Array.from(this.modules.keys())
            });
            
        } catch (error) {
            console.error('❌ Failed to initialize GödelOS Application:', error);
            this.handleInitializationError(error);
        }
    }

    /**
     * Initialize adaptive interface system
     */
    async initializeAdaptiveInterface() {
        try {
            // AdaptiveInterface is already initialized globally
            if (window.adaptiveInterface) {
                this.modules.set('adaptiveInterface', window.adaptiveInterface);
                
                // Listen for complexity changes
                document.addEventListener('complexityChanged', (event) => {
                    this.handleComplexityChange(event.detail);
                });
                
                console.log('✅ Adaptive Interface integrated');
            } else {
                throw new Error('Adaptive Interface not found');
            }
        } catch (error) {
            console.error('❌ Failed to initialize Adaptive Interface:', error);
            throw error;
        }
    }

    /**
     * Initialize API client
     */
    async initializeAPIClient() {
        try {
            console.log('🔍 DEBUG: Checking for window.APIClient...', typeof window.APIClient);
            if (window.APIClient) {
                this.modules.set('apiClient', new window.APIClient(this.config.apiBaseUrl));
                console.log('✅ API Client initialized');
            } else {
                console.warn('⚠️ API Client not available, using fallback');
                console.log('🔍 DEBUG: Available window objects:', Object.keys(window).filter(k => k.includes('API') || k.includes('Client')));
                this.modules.set('apiClient', this.createFallbackAPIClient());
            }
        } catch (error) {
            console.error('❌ Failed to initialize API Client:', error);
            this.modules.set('apiClient', this.createFallbackAPIClient());
        }
    }

    /**
     * Initialize WebSocket connection
     */
    async initializeWebSocket() {
        try {
            // Use the existing global WebSocket manager instead of creating a new one
            if (window.wsManager) {
                this.modules.set('websocket', window.wsManager);
                
                // Setup WebSocket event handlers
                window.wsManager.on('connected', () => {
                    this.updateConnectionStatus('connected');
                });
                
                window.wsManager.on('disconnected', () => {
                    this.updateConnectionStatus('disconnected');
                });
                
                window.wsManager.on('cognitiveUpdate', (data) => {
                    this.handleCognitiveUpdate(data);
                });
                
                console.log('✅ Using existing global WebSocket Manager');
            } else {
                console.warn('⚠️ Global WebSocket Manager not available');
                console.log('🔍 DEBUG: Checking for WebSocket classes...', {
                    'window.WebSocketManager': typeof window.WebSocketManager,
                    'window.wsManager': typeof window.wsManager,
                    'window.io': typeof window.io,
                    'WebSocket': typeof WebSocket
                });
            }
        } catch (error) {
            console.error('❌ Failed to initialize WebSocket:', error);
            this.updateConnectionStatus('disconnected');
        }
    }

    /**
     * Initialize query handler
     */
    async initializeQueryHandler() {
        try {
            console.log('🔍 DEBUG: Checking for window.QueryHandler...', typeof window.QueryHandler);
            if (window.QueryHandler) {
                const queryHandler = new window.QueryHandler({
                    apiClient: this.modules.get('apiClient'),
                    websocket: this.modules.get('websocket')
                });
                this.modules.set('queryHandler', queryHandler);
                
                // Setup query event handlers
                queryHandler.on('querySubmitted', (data) => {
                    this.handleQuerySubmitted(data);
                });
                
                queryHandler.on('responseReceived', (data) => {
                    this.handleResponseReceived(data);
                });
                
                console.log('✅ Query Handler initialized');
            } else {
                console.warn('⚠️ Query Handler not available');
                console.log('🔍 DEBUG: Available window objects:', Object.keys(window).filter(k => k.includes('Query') || k.includes('Handler')));
            }
        } catch (error) {
            console.error('❌ Failed to initialize Query Handler:', error);
        }
    }

    /**
     * Initialize visualization systems
     */
    async initializeVisualization() {
        try {
            // Initialize knowledge graph visualizer
            if (window.KnowledgeGraphVisualizer) {
                const kgVisualizer = new window.KnowledgeGraphVisualizer('knowledgeGraphVisualization');
                this.modules.set('knowledgeGraphVisualizer', kgVisualizer);
                // Also set as global for transparency panel access
                window.knowledgeGraphVisualizer = kgVisualizer;
            }
            
            // Initialize reasoning visualizer
            if (window.ReasoningVisualizer) {
                const reasoningVisualizer = new window.ReasoningVisualizer('#reasoningVisualization');
                this.modules.set('reasoningVisualizer', reasoningVisualizer);
                // Also set as global for transparency panel access
                window.reasoningVisualizer = reasoningVisualizer;
            }
            
            // Initialize uncertainty visualizer
            if (window.UncertaintyVisualizer) {
                const uncertaintyVisualizer = new window.UncertaintyVisualizer('#uncertaintyVisualization');
                this.modules.set('uncertaintyVisualizer', uncertaintyVisualizer);
                // Also set as global for transparency panel access
                window.uncertaintyVisualizer = uncertaintyVisualizer;
            }
            
            // Initialize metacognitive dashboard
            if (window.MetacognitiveDashboard) {
                const metacognitiveDashboard = new window.MetacognitiveDashboard('metacognitiveDashboard');
                this.modules.set('metacognitiveDashboard', metacognitiveDashboard);
                // Also set as global for transparency panel access
                window.metacognitiveDashboard = metacognitiveDashboard;
            }
            
            // Initialize provenance explorer
            if (window.ProvenanceExplorer) {
                const provenanceExplorer = new window.ProvenanceExplorer('provenanceExploration');
                this.modules.set('provenanceExplorer', provenanceExplorer);
                // Also set as global for transparency panel access
                window.provenanceExplorer = provenanceExplorer;
            }
            
            console.log('✅ Visualization systems initialized');
            console.log('🔍 DEBUG: Available visualizers:', {
                knowledgeGraphVisualizer: !!window.knowledgeGraphVisualizer,
                reasoningVisualizer: !!window.reasoningVisualizer,
                uncertaintyVisualizer: !!window.uncertaintyVisualizer,
                metacognitiveDashboard: !!window.metacognitiveDashboard,
                provenanceExplorer: !!window.provenanceExplorer
            });
        } catch (error) {
            console.error('❌ Failed to initialize visualization systems:', error);
        }
    }

    /**
     * Initialize cognitive layers
     */
    async initializeCognitiveLayers() {
        try {
            console.log('🔍 DEBUG: Checking for window.CognitiveLayers...', typeof window.CognitiveLayers);
            if (window.CognitiveLayers) {
                const cognitiveLayers = new window.CognitiveLayers('#cognitiveLayers');
                this.modules.set('cognitiveLayers', cognitiveLayers);
                console.log('✅ Cognitive Layers initialized');
            } else {
                console.warn('⚠️ Cognitive Layers not available');
                console.log('🔍 DEBUG: Available window objects:', Object.keys(window).filter(k => k.includes('Cognitive') || k.includes('Layer')));
            }
        } catch (error) {
            console.error('❌ Failed to initialize Cognitive Layers:', error);
        }
    }

    /**
     * Initialize knowledge management
     */
    async initializeKnowledgeManagement() {
        try {
            console.log('🔍 Initializing Knowledge Management interfaces...');
            
            // Initialize knowledge ingestion
            if (window.KnowledgeIngestionInterface) {
                const knowledgeIngestionInterface = new window.KnowledgeIngestionInterface('knowledgeIngestion');
                
                // Initialize the interface if the container exists
                if (document.getElementById('knowledgeIngestion')) {
                    knowledgeIngestionInterface.initializeInterface();
                    console.log('✅ Knowledge Ingestion Interface initialized');
                } else {
                    console.warn('⚠️ Knowledge Ingestion container not found, will initialize later');
                }
                
                this.modules.set('knowledgeIngestion', knowledgeIngestionInterface);
                window.knowledgeIngestionInterface = knowledgeIngestionInterface;
            } else {
                console.warn('⚠️ KnowledgeIngestionInterface not available');
            }
            
            // Initialize knowledge management
            if (window.KnowledgeManagementInterface) {
                const knowledgeManagementInterface = new window.KnowledgeManagementInterface();
                this.modules.set('knowledgeManagement', knowledgeManagementInterface);
                window.knowledgeManagementInterface = knowledgeManagementInterface;
                console.log('✅ Knowledge Management Interface initialized');
            } else {
                console.warn('⚠️ KnowledgeManagementInterface not available');
            }
            
            // Initialize knowledge search
            if (window.KnowledgeSearchInterface) {
                const knowledgeSearchInterface = new window.KnowledgeSearchInterface();
                this.modules.set('knowledgeSearch', knowledgeSearchInterface);
                window.knowledgeSearchInterface = knowledgeSearchInterface;
                console.log('✅ Knowledge Search Interface initialized');
            } else {
                console.warn('⚠️ KnowledgeSearchInterface not available');
            }
            
            console.log('✅ Knowledge Management systems initialized');
        } catch (error) {
            console.error('❌ Failed to initialize Knowledge Management:', error);
        }
    }

    /**
     * Initialize educational features
     */
    async initializeEducationalFeatures() {
        try {
            console.log('🔍 DEBUG: Checking for window.EducationalFeatures...', typeof window.EducationalFeatures);
            if (window.EducationalFeatures) {
                const educational = new window.EducationalFeatures();
                this.modules.set('educational', educational);
                console.log('✅ Educational Features initialized');
            } else {
                console.warn('⚠️ Educational Features not available');
                console.log('🔍 DEBUG: Available window objects:', Object.keys(window).filter(k => k.includes('Educational') || k.includes('Feature')));
            }
        } catch (error) {
            console.error('❌ Failed to initialize Educational Features:', error);
        }
    }

    /**
     * Setup global event handlers
     */
    setupEventHandlers() {
        // Tutorial button
        const tutorialButton = document.getElementById('tutorialButton');
        if (tutorialButton) {
            tutorialButton.addEventListener('click', () => {
                const adaptiveInterface = this.modules.get('adaptiveInterface');
                if (adaptiveInterface) {
                    adaptiveInterface.restartOnboarding();
                }
            });
        }

        // Help button
        const helpButton = document.getElementById('helpButton');
        if (helpButton) {
            helpButton.addEventListener('click', () => {
                this.showHelpModal();
            });
        }

        // Settings button
        const settingsButton = document.getElementById('settingsButton');
        if (settingsButton) {
            settingsButton.addEventListener('click', () => {
                this.showSettingsModal();
            });
        }

        // Query form
        const queryForm = document.getElementById('queryForm');
        if (queryForm) {
            queryForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.handleQuerySubmit();
            });
        }

        // Character count for query textarea
        const queryTextarea = document.getElementById('naturalLanguageQuery');
        if (queryTextarea) {
            queryTextarea.addEventListener('input', (e) => {
                this.updateCharacterCount(e.target.value.length);
            });
        }

        // Confidence slider
        const confidenceSlider = document.getElementById('confidenceThreshold');
        if (confidenceSlider) {
            confidenceSlider.addEventListener('input', (e) => {
                this.updateConfidenceDisplay(e.target.value);
            });
        }

        // Query type selector
        const queryTypeSelect = document.getElementById('queryType');
        if (queryTypeSelect) {
            queryTypeSelect.addEventListener('change', (e) => {
                this.updateQueryTypeDescription(e.target.value);
            });
        }
    }

    /**
     * Setup keyboard shortcuts
     */
    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Ctrl+Enter to submit query
            if (e.ctrlKey && e.key === 'Enter') {
                e.preventDefault();
                this.handleQuerySubmit();
            }
            
            // Escape to close modals
            if (e.key === 'Escape') {
                this.closeAllModals();
            }
            
            // Alt+H for help
            if (e.altKey && e.key === 'h') {
                e.preventDefault();
                this.showHelpModal();
            }
            
            // Alt+T for tutorial
            if (e.altKey && e.key === 't') {
                e.preventDefault();
                const adaptiveInterface = this.modules.get('adaptiveInterface');
                if (adaptiveInterface) {
                    adaptiveInterface.restartOnboarding();
                }
            }
        });
    }

    /**
     * Setup error handling
     */
    setupErrorHandling() {
        // Global error handler
        window.addEventListener('error', (event) => {
            console.error('Global error:', event.error);
            this.handleGlobalError(event.error);
        });

        // Unhandled promise rejection handler
        window.addEventListener('unhandledrejection', (event) => {
            console.error('Unhandled promise rejection:', event.reason);
            this.handleGlobalError(event.reason);
        });
    }

    /**
     * Initialize UI components
     */
    initializeUIComponents() {
        // Initialize tooltips
        this.initializeTooltips();
        
        // Initialize tabs
        this.initializeTabs();
        
        // Initialize modals
        this.initializeModals();
        
        // Initialize visualization controls
        this.initializeVisualizationControls();
    }

    /**
     * Initialize tooltips
     */
    initializeTooltips() {
        // Enhanced tooltips are handled by the adaptive interface
        console.log('✅ Tooltips initialized');
    }

    /**
     * Initialize tabs
     */
    initializeTabs() {
        const tabButtons = document.querySelectorAll('.tab-button');
        tabButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                const tabId = e.target.getAttribute('data-tab');
                this.switchTab(tabId);
            });
        });
    }

    /**
     * Initialize modals
     */
    initializeModals() {
        // Modal close buttons
        document.querySelectorAll('.modal-close').forEach(button => {
            button.addEventListener('click', (e) => {
                const modal = e.target.closest('.modal-overlay');
                if (modal) {
                    this.closeModal(modal);
                }
            });
        });

        // Modal backdrop clicks
        document.querySelectorAll('.modal-overlay').forEach(modal => {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    this.closeModal(modal);
                }
            });
        });
    }

    /**
     * Initialize visualization controls
     */
    initializeVisualizationControls() {
        // Zoom controls
        const zoomIn = document.getElementById('zoomIn');
        const zoomOut = document.getElementById('zoomOut');
        const resetZoom = document.getElementById('resetZoom');
        const centerGraph = document.getElementById('centerGraph');

        if (zoomIn) {
            zoomIn.addEventListener('click', () => {
                const visualizer = this.modules.get('knowledgeGraphVisualizer');
                if (visualizer && visualizer.zoomIn) {
                    visualizer.zoomIn();
                }
            });
        }

        if (zoomOut) {
            zoomOut.addEventListener('click', () => {
                const visualizer = this.modules.get('knowledgeGraphVisualizer');
                if (visualizer && visualizer.zoomOut) {
                    visualizer.zoomOut();
                }
            });
        }

        if (resetZoom) {
            resetZoom.addEventListener('click', () => {
                const visualizer = this.modules.get('knowledgeGraphVisualizer');
                if (visualizer && visualizer.resetZoom) {
                    visualizer.resetZoom();
                }
            });
        }

        if (centerGraph) {
            centerGraph.addEventListener('click', () => {
                const visualizer = this.modules.get('knowledgeGraphVisualizer');
                if (visualizer && visualizer.centerGraph) {
                    visualizer.centerGraph();
                }
            });
        }
    }

    /**
     * Load and display knowledge graph data
     */
    async loadKnowledgeGraphData() {
        const kgVisualizer = this.modules.get('knowledgeGraphVisualizer');
        if (!kgVisualizer) {
            console.warn('Knowledge graph visualizer not available');
            return;
        }

        try {
            console.log('🔄 Loading knowledge graph data...');
            const data = await window.apiClient.getKnowledgeGraph();
            
            if (data && data.graph_data) {
                console.log('✅ Knowledge graph data loaded:', {
                    nodes: data.graph_data.nodes?.length || 0,
                    edges: data.graph_data.edges?.length || 0
                });
                
                kgVisualizer.updateVisualization(data);
                
                // Update the knowledge pane status
                const knowledgePane = document.getElementById('knowledgePane');
                if (knowledgePane) {
                    const statusMessage = knowledgePane.querySelector('.status-message');
                    if (statusMessage) {
                        statusMessage.innerHTML = `
                            <span class="status-icon">✅</span>
                            <span class="status-text">Knowledge graph loaded with ${data.graph_data.nodes?.length || 0} concepts and ${data.graph_data.edges?.length || 0} relationships.</span>
                        `;
                    }
                }
                
                return data;
            } else {
                console.warn('No knowledge graph data available');
                return null;
            }
        } catch (error) {
            console.error('Failed to load knowledge graph data:', error);
            
            // Update the knowledge pane with error status
            const knowledgePane = document.getElementById('knowledgePane');
            if (knowledgePane) {
                const statusMessage = knowledgePane.querySelector('.status-message');
                if (statusMessage) {
                    statusMessage.innerHTML = `
                        <span class="status-icon">❌</span>
                        <span class="status-text">Failed to load knowledge graph data. Please check system status.</span>
                    `;
                }
            }
            
            return null;
        }
    }

    /**
     * Start application services
     */
    startServices() {
        // Start heartbeat
        this.startHeartbeat();
        
        // Start performance monitoring
        this.startPerformanceMonitoring();
        
        console.log('✅ Application services started');
    }

    /**
     * Start heartbeat service
     */
    startHeartbeat() {
        setInterval(() => {
            const websocket = this.modules.get('websocket');
            if (websocket && websocket.isConnected()) {
                // Check if sendHeartbeat method exists before calling it
                if (typeof websocket.sendHeartbeat === 'function') {
                    websocket.sendHeartbeat();
                } else {
                    console.log('🔍 HEARTBEAT: sendHeartbeat method not available on websocket');
                }
            }
        }, this.config.heartbeatInterval);
    }

    /**
     * Start performance monitoring
     */
    startPerformanceMonitoring() {
        // Monitor performance metrics
        if ('performance' in window) {
            setInterval(() => {
                const navigation = performance.getEntriesByType('navigation')[0];
                if (navigation) {
                    this.updatePerformanceMetrics(navigation);
                }
            }, 10000); // Every 10 seconds
        }
    }

    /**
     * Handle complexity level change
     */
    handleComplexityChange(detail) {
        // Prevent recursion by checking if this is already the current level
        if (this.state.complexityLevel === detail.currentLevel) {
            return;
        }
        
        this.state.complexityLevel = detail.currentLevel;
        
        // Update all modules that support complexity changes (except the one that triggered this)
        this.modules.forEach((module, name) => {
            if (module.setComplexityLevel && name !== 'adaptiveInterface') {
                module.setComplexityLevel(detail.currentLevel);
            }
        });
        
        console.log(`🎯 Complexity level changed to: ${detail.currentLevel}`);
    }

    /**
     * Handle query submission
     */
    async handleQuerySubmit() {
        const queryTextarea = document.getElementById('naturalLanguageQuery');
        const queryType = document.getElementById('queryType');
        const confidence = document.getElementById('confidenceThreshold');
        
        if (!queryTextarea || !queryTextarea.value.trim()) {
            this.showError('Please enter a query');
            return;
        }

        const queryData = {
            query: queryTextarea.value.trim(),
            type: queryType ? queryType.value : 'knowledge',
            confidence: confidence ? parseFloat(confidence.value) : 0.7,
            complexity: this.state.complexityLevel
        };

        const queryHandler = this.modules.get('queryHandler');
        if (queryHandler) {
            try {
                await queryHandler.submitQuery(queryData);
            } catch (error) {
                this.handleError('Failed to submit query', error);
            }
        } else {
            this.handleError('Query handler not available');
        }
    }

    /**
     * Handle query submitted event
     */
    handleQuerySubmitted(data) {
        this.state.currentQuery = data;
        this.showLoadingState();
        console.log('📤 Query submitted:', data);
    }

    /**
     * Handle response received event
     */
    handleResponseReceived(data) {
        this.state.lastResponse = data;
        this.hideLoadingState();
        this.displayResponse(data);
        console.log('📥 Response received:', data);
    }

    /**
     * Handle cognitive update
     */
    handleCognitiveUpdate(data) {
        this.state.cognitiveState = data;
        
        // Update cognitive layers display
        const cognitiveLayers = this.modules.get('cognitiveLayers');
        if (cognitiveLayers) {
            cognitiveLayers.updateState(data);
        }
        
        // Update visualizations if needed
        this.updateVisualizationsWithCognitiveData(data);
    }

    /**
     * Update connection status
     */
    updateConnectionStatus(status) {
        this.state.isConnected = status === 'connected';
        
        const statusElement = document.getElementById('connectionStatus');
        if (statusElement) {
            statusElement.setAttribute('data-status', status);
            const statusText = statusElement.querySelector('.status-text');
            if (statusText) {
                statusText.textContent = status === 'connected' ? 'Connected' : 'Disconnected';
            }
        }
        
        // Update connection quality if connected
        if (status === 'connected') {
            this.updateConnectionQuality('excellent');
        } else {
            this.updateConnectionQuality('poor');
        }
    }

    /**
     * Update connection quality
     */
    updateConnectionQuality(quality) {
        const qualityElement = document.getElementById('connectionQuality');
        if (qualityElement) {
            qualityElement.setAttribute('data-quality', quality);
        }
    }

    /**
     * Update character count
     */
    updateCharacterCount(count) {
        const charCountElement = document.getElementById('charCount');
        if (charCountElement) {
            charCountElement.textContent = `${count} characters`;
        }
    }

    /**
     * Update confidence display
     */
    updateConfidenceDisplay(value) {
        const confidenceValue = document.getElementById('confidenceValue');
        const confidenceLabel = document.getElementById('confidenceLabel');
        
        if (confidenceValue) {
            confidenceValue.textContent = value;
        }
        
        if (confidenceLabel) {
            let label = 'Low';
            if (value >= 0.7) label = 'High';
            else if (value >= 0.4) label = 'Medium';
            confidenceLabel.textContent = `(${label})`;
        }
    }

    /**
     * Update query type description
     */
    updateQueryTypeDescription(type) {
        const descriptions = {
            'knowledge': 'Retrieve and synthesize information from the knowledge base',
            'reasoning': 'Apply logical reasoning and inference to solve problems',
            'learning': 'Learn new concepts and update the knowledge base',
            'metacognition': 'Analyze and reflect on the reasoning process'
        };
        
        const descElement = document.getElementById('query-type-desc');
        if (descElement) {
            descElement.textContent = descriptions[type] || descriptions['knowledge'];
        }
    }

    /**
     * Show loading state
     */
    showLoadingState() {
        const loadingOverlay = document.getElementById('loadingOverlay');
        if (loadingOverlay) {
            loadingOverlay.style.display = 'flex';
        }
        
        // Show loading in visualizations
        const visualizationLoading = document.getElementById('visualizationLoading');
        if (visualizationLoading) {
            visualizationLoading.style.display = 'flex';
        }
    }

    /**
     * Hide loading state
     */
    hideLoadingState() {
        const loadingOverlay = document.getElementById('loadingOverlay');
        if (loadingOverlay) {
            loadingOverlay.style.display = 'none';
        }
        
        const visualizationLoading = document.getElementById('visualizationLoading');
        if (visualizationLoading) {
            visualizationLoading.style.display = 'none';
        }
    }

    /**
     * Display response
     */
    displayResponse(response) {
        // Update natural language response
        const naturalResponse = document.getElementById('naturalResponse');
        if (naturalResponse && response.natural_language) {
            naturalResponse.innerHTML = `
                <div class="response-content">
                    <p>${response.natural_language}</p>
                </div>
            `;
        }
        
        // Update metadata if available
        if (response.metadata) {
            this.updateResponseMetadata(response.metadata);
        }
        
        // Update visualizations
        this.updateVisualizationsWithResponse(response);
    }

    /**
     * Update response metadata
     */
    updateResponseMetadata(metadata) {
        const confidenceElement = document.getElementById('responseConfidence');
        const processingTimeElement = document.getElementById('processingTime');
        
        if (confidenceElement && metadata.confidence) {
            confidenceElement.textContent = `${(metadata.confidence * 100).toFixed(1)}%`;
        }
        
        if (processingTimeElement && metadata.processing_time) {
            processingTimeElement.textContent = `${metadata.processing_time.toFixed(2)}ms`;
        }
    }

    /**
     * Update visualizations with response data
     */
    updateVisualizationsWithResponse(response) {
        // Update knowledge graph
        const kgVisualizer = this.modules.get('knowledgeGraphVisualizer');
        if (kgVisualizer && (response.knowledge_graph || response.graph_data)) {
            // Handle both response formats for compatibility
            const graphData = response.knowledge_graph || response.graph_data;
            kgVisualizer.updateVisualization({ graph_data: graphData });
        }
        
        // Update reasoning visualizer
        const reasoningVisualizer = this.modules.get('reasoningVisualizer');
        if (reasoningVisualizer && response.reasoning_trace) {
            reasoningVisualizer.displayTrace(response.reasoning_trace);
        }
    }

    /**
     * Update visualizations with cognitive data
     */
    updateVisualizationsWithCognitiveData(data) {
        // This method updates visualizations based on cognitive state changes
        // Implementation depends on the specific cognitive data structure
    }

    /**
     * Switch tab
     */
    switchTab(tabId) {
        // Hide all tab panes
        document.querySelectorAll('.tab-pane').forEach(pane => {
            pane.classList.remove('active');
        });
        
        // Remove active state from all tab buttons
        document.querySelectorAll('.tab-button').forEach(button => {
            button.classList.remove('active');
            button.setAttribute('aria-selected', 'false');
        });
        
        // Show selected tab pane
        const targetPane = document.getElementById(`${tabId}Tab`);
        if (targetPane) {
            targetPane.classList.add('active');
        }
        
        // Activate selected tab button
        const targetButton = document.querySelector(`[data-tab="${tabId}"]`);
        if (targetButton) {
            targetButton.classList.add('active');
            targetButton.setAttribute('aria-selected', 'true');
        }
    }

    /**
     * Show help modal
     */
    showHelpModal() {
        const helpModal = document.getElementById('helpModal');
        if (helpModal) {
            helpModal.style.display = 'flex';
            helpModal.setAttribute('aria-hidden', 'false');
            
            // Focus management
            const firstFocusable = helpModal.querySelector('button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])');
            if (firstFocusable) {
                firstFocusable.focus();
            }
        }
    }

    /**
     * Show settings modal
     */
    showSettingsModal() {
        // Implementation for settings modal
        console.log('Settings modal would be shown here');
    }

    /**
     * Close modal
     */
    closeModal(modal) {
        modal.style.display = 'none';
        modal.setAttribute('aria-hidden', 'true');
    }

    /**
     * Close all modals
     */
    closeAllModals() {
        document.querySelectorAll('.modal-overlay').forEach(modal => {
            this.closeModal(modal);
        });
        
        // Also close onboarding if active
        const adaptiveInterface = this.modules.get('adaptiveInterface');
        if (adaptiveInterface && adaptiveInterface.onboarding && adaptiveInterface.onboarding.isActive) {
            adaptiveInterface.skipOnboarding();
        }
    }

    /**
     * Show error message
     */
    showError(message) {
        const adaptiveInterface = this.modules.get('adaptiveInterface');
        if (adaptiveInterface) {
            adaptiveInterface.announceToScreenReader(`Error: ${message}`);
        }
        
        // Could also show a toast notification or modal
        console.error('User Error:', message);
    }

    /**
     * Handle error
     */
    handleError(message, error = null) {
        console.error(message, error);
        this.showError(message);
        this.hideLoadingState();
    }

    /**
     * Handle global error
     */
    handleGlobalError(error) {
        console.error('Global application error:', error);
        
        // Could implement error reporting here
        // For now, just log and continue
    }

    /**
     * Handle initialization error
     */
    handleInitializationError(error) {
        console.error('Initialization error:', error);
        
        // Show error message to user
        document.body.innerHTML = `
            <div style="padding: 2rem; text-align: center; font-family: Arial, sans-serif;">
                <h1 style="color: #e74c3c;">GödelOS Initialization Error</h1>
                <p>Failed to initialize the application. Please refresh the page and try again.</p>
                <p style="color: #7f8c8d; font-size: 0.9em;">Error: ${error.message}</p>
                <button onclick="location.reload()" style="padding: 0.5rem 1rem; background: #3498db; color: white; border: none; border-radius: 4px; cursor: pointer;">
                    Refresh Page
                </button>
            </div>
        `;
    }

    /**
     * Update performance metrics
     */
    updatePerformanceMetrics(navigation) {
        // Log performance metrics for monitoring
        const metrics = {
            loadTime: navigation.loadEventEnd - navigation.loadEventStart,
            domContentLoaded: navigation.domContentLoadedEventEnd - navigation.domContentLoadedEventStart,
            firstPaint: performance.getEntriesByName('first-paint')[0]?.startTime || 0,
            firstContentfulPaint: performance.getEntriesByName('first-contentful-paint')[0]?.startTime || 0
        };
        
        console.log('📊 Performance metrics:', metrics);
    }

    /**
     * Create fallback API client
     */
    createFallbackAPIClient() {
        return {
            async submitQuery(query) {
                console.warn('Using fallback API client - no real backend connection');
                return {
                    natural_language: 'This is a fallback response. The backend is not connected.',
                    metadata: {
                        confidence: 0.5,
                        processing_time: 100
                    }
                };
            }
        };
    }

    /**
     * Dispatch custom event
     */
    dispatchEvent(eventName, detail = {}) {
        const event = new CustomEvent(eventName, {
            detail: {
                ...detail,
                timestamp: Date.now(),
                source: 'GödelOSApp'
            }
        });
        document.dispatchEvent(event);
    }

    /**
     * Get application state
     */
    getState() {
        return { ...this.state };
    }

    /**
     * Get module by name
     */
    getModule(name) {
        return this.modules.get(name);
    }

    /**
     * Check if application is initialized
     */
    isReady() {
        return this.isInitialized;
    }

    /**
     * Run comprehensive backend diagnostics
     */
    async runBackendDiagnostics() {
        console.log('🔍 DIAGNOSTIC: Running backend health checks...');
        
        try {
            // Check basic health endpoint
            const healthStatus = await window.apiClient.getHealthStatus();
            if (healthStatus.status === 'unhealthy') {
                console.warn('⚠️ DIAGNOSTIC: Backend reports unhealthy status:', healthStatus);
                console.log('🔍 DIAGNOSTIC: Backend health details:', healthStatus.details);
            } else {
                console.log('✅ DIAGNOSTIC: Backend health check passed:', healthStatus);
            }
        } catch (error) {
            console.error('❌ DIAGNOSTIC: Backend health check failed:', error);
        }

        try {
            // Check knowledge graph data availability
            const kgData = await window.apiClient.getKnowledgeGraph({
                format: 'visualization',
                include_statistics: true,
                node_limit: 10
            });
            console.log('🔍 DIAGNOSTIC: Knowledge graph data check:', {
                node_count: kgData.node_count,
                edge_count: kgData.edge_count,
                has_graph_data: !!kgData.graph_data
            });
        } catch (error) {
            console.error('❌ DIAGNOSTIC: Knowledge graph check failed:', error);
        }

        try {
            // Check knowledge categories
            const categories = await window.apiClient.get('/api/transparency/knowledge/categories');
            console.log('🔍 DIAGNOSTIC: Knowledge categories check:', {
                success: categories.success,
                category_count: categories.categories ? categories.categories.length : 0,
                categories: categories.categories
            });
        } catch (error) {
            console.error('❌ DIAGNOSTIC: Knowledge categories check failed:', error);
        }

        try {
            // Check knowledge statistics
            const stats = await window.apiClient.get('/api/transparency/knowledge/statistics');
            console.log('🔍 DIAGNOSTIC: Knowledge statistics check:', {
                success: stats.success,
                has_statistics: !!stats.statistics,
                statistics_keys: stats.statistics ? Object.keys(stats.statistics) : []
            });
        } catch (error) {
            console.error('❌ DIAGNOSTIC: Knowledge statistics check failed:', error);
        }

        console.log('🔍 DIAGNOSTIC: Backend diagnostics completed');
    }

    /**
     * Load and display knowledge graph data
     */
    async loadKnowledgeGraphData() {
        const kgVisualizer = this.modules.get('knowledgeGraphVisualizer');
        if (!kgVisualizer) {
            console.warn('Knowledge graph visualizer not available');
            return;
        }

        try {
            console.log('🔄 Loading knowledge graph data...');
            const data = await window.apiClient.getKnowledgeGraph();
            
            if (data && data.graph_data) {
                console.log('✅ Knowledge graph data loaded:', {
                    nodes: data.graph_data.nodes?.length || 0,
                    edges: data.graph_data.edges?.length || 0
                });
                
                kgVisualizer.updateVisualization(data);
                
                // Update the knowledge pane status
                const knowledgePane = document.getElementById('knowledgePane');
                if