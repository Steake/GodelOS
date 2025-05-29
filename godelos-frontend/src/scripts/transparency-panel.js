/**
 * Cognitive Transparency Panel Controller
 * Handles the visibility and interaction of the transparency panel
 */

// @ts-nocheck

class TransparencyPanelController {
    constructor() {
        this.panel = null;
        this.toggleBtn = null;
        this.isVisible = false;
        this.currentTab = 'reasoning';
        this.currentChainId = 'default';
        this.backendStatus = {
            isConnected: false,
            lastConnected: null,
            reconnectAttempts: 0
        };
        
        // Bind context for public methods
        this.showErrorState = this.showErrorState.bind(this);
        this.getCurrentChainId = this.getCurrentChainId.bind(this);
        
        this.initialize();
    }

    /**
     * Gets the current provenance chain ID
     * @returns {string} Current chain ID
     */
    getCurrentChainId() {
        return this.currentChainId;
    }

    // Unified error handling implementation
    showErrorState(component, message) {
        console.error(`🚨 ${component.toUpperCase()} ERROR:`, message);
        const errorDiv = document.getElementById('transparency-errors');
        if (errorDiv) {
            errorDiv.innerHTML = `
                <div class="transparency-error">
                    <h4>${component} Error</h4>
                    <pre>${message}</pre>
                </div>
            `;
            errorDiv.style.display = 'block';
        }
    }

    async verifyBackendReadiness(retries = 2) {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 3000);
        const baseDelay = 2000; // Start with 2s delay

        for (let attempt = 0; attempt <= retries; attempt++) {
            try {
                if (attempt > 0) {
                    const delay = baseDelay * Math.pow(2, attempt - 1); // Exponential backoff
                    console.log(`🔄 Retrying backend health check (attempt ${attempt}/${retries}), waiting ${delay}ms`);
                    await new Promise(resolve => setTimeout(resolve, delay));
                }

                const response = await fetch('http://localhost:8000/health', {
                    signal: controller.signal,
                    headers: {
                        'Accept': 'application/json'
                    }
                });
                
                if (!response.ok) {
                    throw new Error(`Backend unhealthy (${response.status}): ${response.statusText}`);
                }
                
                const data = await response.json();
                if (data.status !== 'healthy') {
                    throw new Error(`Backend status: ${data.status}`);
                }
                
                clearTimeout(timeoutId);
                this.backendStatus.isConnected = true;
                this.backendStatus.lastConnected = new Date();
                this.backendStatus.reconnectAttempts = 0;
                return true;
            } catch (error) {
                if (attempt === retries) {
                    clearTimeout(timeoutId);
                    const errorMsg = error.name === 'AbortError'
                        ? 'Backend health check timed out'
                        : `Backend unavailable: ${error.message}`;
                    
                    console.warn(`⚠️ ${errorMsg} - Running in fallback mode`);
                    return false;
                }
            }
        }
        return false;
    }

    
    initialize() {
        console.log('🔍 TRANSPARENCY PANEL DIAGNOSTIC: Starting initialization...');
        
        this.panel = document.getElementById('cognitiveTransparencyPanel');
        this.toggleBtn = document.getElementById('transparencyToggleBtn');
        
        console.log('🔍 TRANSPARENCY PANEL DIAGNOSTIC: Panel found:', !!this.panel);
        console.log('🔍 TRANSPARENCY PANEL DIAGNOSTIC: Toggle button found:', !!this.toggleBtn);
        
        if (this.toggleBtn) {
            // Detailed button diagnostics
            const rect = this.toggleBtn.getBoundingClientRect();
            const computedStyle = window.getComputedStyle(this.toggleBtn);
            
            console.log('🔍 BUTTON DIAGNOSTIC: Position:', {
                top: rect.top,
                left: rect.left,
                bottom: rect.bottom,
                right: rect.right,
                width: rect.width,
                height: rect.height
            });
            
            console.log('🔍 BUTTON DIAGNOSTIC: Computed styles:', {
                display: computedStyle.display,
                visibility: computedStyle.visibility,
                opacity: computedStyle.opacity,
                zIndex: computedStyle.zIndex,
                position: computedStyle.position,
                background: computedStyle.backgroundColor
            });
            
            console.log('🔍 BUTTON DIAGNOSTIC: Button element:', this.toggleBtn);
        }
        
        if (!this.panel) {
            console.error('❌ TRANSPARENCY PANEL DIAGNOSTIC: cognitiveTransparencyPanel not found');
        }
        
        if (!this.toggleBtn) {
            console.error('❌ TRANSPARENCY PANEL DIAGNOSTIC: transparencyToggleBtn not found');
        }
        
        if (!this.panel || !this.toggleBtn) {
            console.warn('⚠️ TRANSPARENCY PANEL DIAGNOSTIC: Required elements not found, skipping initialization');
            return;
        }
        
        this.setupEventListeners();
        this.setupTabs();
        this.setupCloseButton();
        
        // Show panel by default in expert mode OR for debugging
        const complexityLevel = document.body.dataset.complexity;
        if (complexityLevel === 'expert' || true) { // Force show for debugging
            setTimeout(() => this.showPanel(), 100); // Small delay to ensure DOM is ready
        }
// Initialize all tab panes with default content
        this.initializeDefaultContent();
        
        console.log('✅ Transparency Panel Controller initialized');
    }
    
    setupEventListeners() {
        // Toggle button
        this.toggleBtn.addEventListener('click', () => {
            this.togglePanel();
        });
        
        // Tab switching
        const tabs = this.panel.querySelectorAll('.transparency-tab');
        tabs.forEach(tab => {
            tab.addEventListener('click', () => {
                this.switchTab(tab.dataset.tab);
            });
        });
        
        // Transparency level selector
        const levelSelect = this.panel.querySelector('#transparencyLevel');
        if (levelSelect) {
            levelSelect.addEventListener('change', (e) => {
                this.setTransparencyLevel(e.target.value);
            });
        }
        
        // Listen for complexity changes
        document.addEventListener('complexityChanged', (e) => {
            this.handleComplexityChange(e.detail.level);
        });
    }
    
    setupCloseButton() {
        // Add close button functionality
        const closeBtn = this.panel.querySelector('.transparency-close-btn');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => {
                this.hidePanel();
            });
            console.log('✅ TRANSPARENCY PANEL: Close button event listener added');
        } else {
            console.warn('⚠️ TRANSPARENCY PANEL: Close button not found');
        }
        
        // Add ESC key handler
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.isVisible) {
                this.hidePanel();
            }
        });
    }
    
    setupTabs() {
        const tabs = this.panel.querySelectorAll('.transparency-tab');
        const panes = this.panel.querySelectorAll('.transparency-pane');
        
        // Set initial active tab
        this.switchTab(this.currentTab);
    }
    
    togglePanel() {
        if (this.isVisible) {
            this.hidePanel();
        } else {
            this.showPanel();
        }
    }
    
    showPanel() {
        console.log('🔍 TRANSPARENCY PANEL: Attempting to show panel...');
        
        if (!this.panel) {
            console.error('❌ TRANSPARENCY PANEL: Panel element not found');
            return;
        }
        
        // Create backdrop if it doesn't exist
        let backdrop = document.getElementById('transparencyBackdrop');
        if (!backdrop) {
            backdrop = document.createElement('div');
            backdrop.id = 'transparencyBackdrop';
            backdrop.className = 'transparency-backdrop';
            backdrop.style.cssText = `
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: rgba(0, 0, 0, 0.7);
                z-index: 9999;
                display: block;
            `;
            
            // Add click handler to close panel when clicking backdrop
            backdrop.addEventListener('click', (e) => {
                if (e.target === backdrop) {
                    this.hidePanel();
                }
            });
            
            document.body.appendChild(backdrop);
            console.log('✅ TRANSPARENCY PANEL: Created backdrop');
        } else {
            backdrop.style.display = 'block';
        }
        
        // Show the panel using class instead of inline style
        this.panel.classList.add('show');
        this.panel.style.display = 'block';
        
        if (this.toggleBtn) {
            this.toggleBtn.classList.add('active');
        }
        
        this.isVisible = true;
        
        // Trigger resize event for visualizations
        setTimeout(() => {
            window.dispatchEvent(new Event('resize'));
        }, 100);
        
        console.log('✅ TRANSPARENCY PANEL: Panel shown successfully');
        
        // Update the active visualization
        this.updateActiveVisualization(this.currentTab);
        
        // Set focus to the first focusable element for accessibility
        const firstFocusable = this.panel.querySelector('button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])');
        if (firstFocusable) {
            firstFocusable.focus();
        }
    }
    
    hidePanel() {
        console.log('🔍 TRANSPARENCY PANEL: Attempting to hide panel...');
        
        if (!this.panel) {
            console.error('❌ TRANSPARENCY PANEL: Panel element not found');
            return;
        }
        
        const backdrop = document.getElementById('transparencyBackdrop');
        if (backdrop) {
            backdrop.style.display = 'none';
        }
        
        // Hide the panel
        this.panel.classList.remove('show');
        this.panel.style.display = 'none';
        
        if (this.toggleBtn) {
            this.toggleBtn.classList.remove('active');
        }
        
        this.isVisible = false;
        
        console.log('✅ TRANSPARENCY PANEL: Panel hidden successfully');
    }
    
    switchTab(tabName) {
        // Update tab buttons
        const tabs = this.panel.querySelectorAll('.transparency-tab');
        tabs.forEach(tab => {
            if (tab.dataset.tab === tabName) {
                tab.classList.add('active');
            } else {
                tab.classList.remove('active');
            }
        });
        
        // Update tab panes
        const panes = this.panel.querySelectorAll('.transparency-pane');
        panes.forEach(pane => {
            if (pane.id === `${tabName}Pane`) {
                pane.classList.add('active');
            } else {
                pane.classList.remove('active');
            }
        });
        
        this.currentTab = tabName;
        
        // Trigger visualization updates for the active tab
        this.updateActiveVisualization(tabName);
    }
    
    async updateActiveVisualization(tabName) {
        console.log(`🔍 TRANSPARENCY DIAGNOSTIC: Updating visualization for tab: ${tabName}`);
        
        try {
            // First check backend readiness with retries
            // Store previous connection state for change detection
            const wasConnected = this.backendStatus.isConnected;
            const isBackendReady = await this.verifyBackendReadiness(2);
            let usingFallback = false;
            
            if (!isBackendReady) {
                // Update reconnect attempts only if we were previously connected
                if (wasConnected) {
                    this.backendStatus.reconnectAttempts++;
                }
                console.log('⚠️ Running in fallback mode without backend');
                this.showErrorState('system',
                    'Running in limited mode - some features unavailable\n' +
                    'Backend services may be starting up or experiencing issues');
                usingFallback = true;
            }

            // Show loading state before attempting any data fetches
            this.showLoadingState(tabName);

            // Handle visualization updates with fallback modes
            switch (tabName) {
                case 'reasoning':
                    // Backend is already verified above
                    this.hideLoadingState(tabName);
                    break;
                
                case 'knowledge':
                    console.log('🔧 TRANSPARENCY DEBUG: Starting knowledge case');
                    console.log('🔧 TRANSPARENCY DEBUG: knowledgeGraphVisualizer exists:', !!window.knowledgeGraphVisualizer);
                    
                    if (window.knowledgeGraphVisualizer) {
                        console.log('✅ TRANSPARENCY DIAGNOSTIC: Refreshing knowledge graph visualizer');
                        try {
                            // Force reinitialize if the container was hidden when first created
                            if (!window.knowledgeGraphVisualizer.svg || window.knowledgeGraphVisualizer.width === 0) {
                                console.log('🔧 TRANSPARENCY DIAGNOSTIC: Reinitializing knowledge graph visualizer');
                                window.knowledgeGraphVisualizer.initializeDOMDependentParts();
                            }
                            
                            console.log('🔧 TRANSPARENCY DEBUG: About to load knowledge graph data');
                            
                            // Load fresh knowledge graph data from the main app controller
                            if (window.app && typeof window.app.loadKnowledgeGraphData === 'function') {
                                console.log('📊 Loading knowledge graph data via main app...');
                                await window.app.loadKnowledgeGraphData();
                            } else {
                                // Fallback to refresh method
                                console.log('🔧 TRANSPARENCY DEBUG: refresh method exists:', typeof window.knowledgeGraphVisualizer.refresh);
                                
                                // Add timeout to catch hanging refresh
                                const refreshPromise = window.knowledgeGraphVisualizer.refresh();
                                const timeoutPromise = new Promise((_, reject) => 
                                    setTimeout(() => reject(new Error('Refresh timeout')), 5000)
                                );
                                
                                await Promise.race([refreshPromise, timeoutPromise]);
                            }
                            console.log('🔧 TRANSPARENCY DEBUG: Knowledge graph update completed');
                            
                            const graphData = window.knowledgeGraphVisualizer.getData();
                            console.log('🔧 TRANSPARENCY DEBUG: Got graph data:', graphData);
                            
                            if (!graphData || (graphData.nodes && graphData.nodes.length === 0)) {
                                console.warn('⚠️ Knowledge graph returned empty data, loading sample data');
                                window.knowledgeGraphVisualizer.loadSampleData();
                            }
                            console.log('🔧 TRANSPARENCY DEBUG: About to hide loading state');
                            this.hideLoadingState(tabName);
                            console.log('🔧 TRANSPARENCY DEBUG: Loading state hidden');
                        } catch (error) {
                            console.error('❌ TRANSPARENCY DEBUG: Error in knowledge case:', error);
                            console.warn('⚠️ Knowledge graph refresh failed, loading sample data:', error);
                            try {
                                window.knowledgeGraphVisualizer.loadSampleData();
                            } catch (sampleError) {
                                console.error('❌ TRANSPARENCY DEBUG: Sample data loading also failed:', sampleError);
                            }
                            this.hideLoadingState(tabName);
                        }
                    } else {
                        console.error('❌ TRANSPARENCY DEBUG: knowledgeGraphVisualizer not available');
                        this.showErrorState('knowledge', 'Knowledge visualization component not initialized');
                    }
                    break;
                
                case 'metacognition':
                    if (window.metacognitiveDashboard) {
                        console.log('✅ TRANSPARENCY DIAGNOSTIC: Refreshing metacognitive dashboard');
                        try {
                            if (usingFallback) {
                                window.metacognitiveDashboard.useOfflineMode();
                            }
                            await window.metacognitiveDashboard.refresh();
                            this.hideLoadingState(tabName);
                        } catch (error) {
                            console.warn('⚠️ Metacognitive dashboard refresh failed:', error);
                            this.showErrorState('metacognition', 'Unable to update metacognitive data');
                        }
                    } else {
                        console.warn('⚠️ TRANSPARENCY DIAGNOSTIC: metacognitiveDashboard not available');
                        this.showErrorState('metacognition', 'Metacognitive dashboard not initialized');
                    }
                    break;
                
                case 'uncertainty':
                    if (window.uncertaintyVisualizer) {
                        console.log('✅ TRANSPARENCY DIAGNOSTIC: Refreshing uncertainty visualizer');
                        try {
                            if (usingFallback) {
                                window.uncertaintyVisualizer.useStaticData();
                            } else {
                                await window.uncertaintyVisualizer.refresh();
                                if (!window.uncertaintyVisualizer.hasData()) {
                                    window.uncertaintyVisualizer.useStaticData();
                                }
                            }
                            this.hideLoadingState(tabName);
                        } catch (error) {
                            console.warn('⚠️ Uncertainty visualizer refresh failed:', error);
                            window.uncertaintyVisualizer.useStaticData();
                            this.hideLoadingState(tabName);
                        }
                    } else {
                        console.warn('⚠️ TRANSPARENCY DIAGNOSTIC: uncertaintyVisualizer not available');
                        this.showErrorState('uncertainty', 'Uncertainty visualization not initialized');
                    }
                    break;
                
                case 'provenance':
                    if (window.provenanceExplorer) {
                        console.log('✅ TRANSPARENCY DIAGNOSTIC: Refreshing provenance explorer');
                        try {
                            const chainId = this.getCurrentChainId() || 'default';
                            if (usingFallback) {
                                window.provenanceExplorer.loadOfflineData(chainId);
                            } else {
                                await window.provenanceExplorer.refresh(chainId);
                                if (!window.provenanceExplorer.hasValidData()) {
                                    window.provenanceExplorer.loadOfflineData(chainId);
                                }
                            }
                            this.hideLoadingState(tabName);
                        } catch (error) {
                            console.warn('⚠️ Provenance explorer refresh failed:', error);
                            this.showErrorState('provenance', 'Unable to load live provenance data, using cached data');
                            window.provenanceExplorer.loadOfflineData(this.getCurrentChainId() || 'default');
                            this.hideLoadingState(tabName);
                        }
                    } else {
                        console.warn('⚠️ TRANSPARENCY DIAGNOSTIC: provenanceExplorer not available');
                        this.showErrorState('provenance', 'Provenance explorer not initialized');
                    }
                    break;
                
                case 'knowledgeIngestion':
                    console.log('🔍 TRANSPARENCY DIAGNOSTIC: Initializing knowledge ingestion integration...');
                    try {
                        if (usingFallback) {
                            this.showErrorState('knowledgeIngestion',
                                'Knowledge ingestion is temporarily unavailable (offline mode)\n\n' +
                                'To restore functionality:\n' +
                                '• Check your network connection\n' +
                                '• Verify the backend service is running at http://localhost:8000\n' +
                                '• Try refreshing the page\n\n' +
                                'Your existing knowledge base remains accessible in read-only mode.\n' +
                                'Tip: Run `npm start` in the backend directory if the service is not running.');
                            return;
                        }

                        // Check class registration
                        if (typeof window.KnowledgeIngestionInterface === 'undefined') {
                            throw new Error('KnowledgeIngestionInterface class not registered - check script loading order');
                        }

                        // Initialize or reuse instance
                        window.knowledgeIngestionInterface = window.knowledgeIngestionInterface ||
                            new window.KnowledgeIngestionInterface();

                        // Direct initialization with async/await
                        console.log('✅ TRANSPARENCY DIAGNOSTIC: Starting async interface initialization');
                        await window.knowledgeIngestionInterface.initializeInterface();
                        console.log('✅ TRANSPARENCY DIAGNOSTIC: Interface initialization completed');
                        this.hideLoadingState(tabName);
                    } catch (error) {
                        console.error('❌ INITIALIZATION FAILURE:', error);
                        this.showErrorState('knowledgeIngestion',
                            `Initialization failed: ${error.message}. Check console for details.`);
                    }
                    break;
                
                case 'knowledgeManagement':
                    console.log('🔍 TRANSPARENCY DIAGNOSTIC: Checking knowledgeManagementInterface...');
                    if (window.knowledgeManagementInterface) {
                        console.log('✅ TRANSPARENCY DIAGNOSTIC: Force re-initializing knowledge management interface');
                        window.knowledgeManagementInterface.initializeInterface();
                        this.hideLoadingState(tabName);
                    } else {
                        console.warn('⚠️ TRANSPARENCY DIAGNOSTIC: knowledgeManagementInterface not available');
                        this.initializeMissingInterface('knowledgeManagement');
                    }
                    break;
                
                case 'knowledgeSearch':
                    console.log('🔍 TRANSPARENCY DIAGNOSTIC: Checking knowledgeSearchInterface...');
                    if (window.knowledgeSearchInterface) {
                        console.log('✅ TRANSPARENCY DIAGNOSTIC: Force re-initializing knowledge search interface');
                        window.knowledgeSearchInterface.initializeInterface();
                        this.hideLoadingState(tabName);
                    } else {
                        console.warn('⚠️ TRANSPARENCY DIAGNOSTIC: knowledgeSearchInterface not available');
                        this.initializeMissingInterface('knowledgeSearch');
                    }
                    break;
            }
        } catch (error) {
            console.error('❌ TRANSPARENCY INTEGRATION ERROR:', error);
            this.showErrorState('system',
                `Failed to update visualization: ${error.message}\n` +
                'Try refreshing the page or check system status');
            
            // Enhanced error recovery
            if (!this.backendStatus.isConnected) {
                console.log('🔄 Starting background recovery process...');
                this.startBackgroundRecovery();
            }
            
            // Handle WebSocket reconnection with exponential backoff
            if (window.webSocketManager && !window.webSocketManager.isConnected()) {
                console.log('🔄 Attempting to reconnect WebSocket...');
                this.handleWebSocketReconnection();
            }
        }
    }

    // Clean up resources before component is destroyed
    cleanup() {
        if (this._recoveryTimeout) {
            clearTimeout(this._recoveryTimeout);
        }
        if (window.webSocketManager) {
            window.webSocketManager.disconnect();
        }
    }

    startBackgroundRecovery() {
        // Prevent multiple recovery processes
        if (this._recoveryTimeout) {
            clearTimeout(this._recoveryTimeout);
        }

        // Attempt recovery every 30 seconds, backing off to 2 minutes after 5 failures
        const interval = this.backendStatus.reconnectAttempts > 5 ? 120000 : 30000;
        
        this._recoveryTimeout = setTimeout(async () => {
            console.log('🔄 Attempting background recovery...');
            const isRecovered = await this.verifyBackendReadiness(1);
            
            if (isRecovered) {
                console.log('✅ Backend connection restored');
                this.updateActiveVisualization(this.currentTab);
            } else {
                this.startBackgroundRecovery();
            }
        }, interval);
    }

    async handleWebSocketReconnection(attempt = 1, maxAttempts = 3) {
        const backoffDelay = Math.min(2000 * Math.pow(2, attempt - 1), 8000); // Max 8s delay

        if (attempt <= maxAttempts) {
            console.log(`🔄 WebSocket reconnection attempt ${attempt}/${maxAttempts} (delay: ${backoffDelay}ms)`);
            
            try {
                await new Promise(resolve => setTimeout(resolve, backoffDelay));
                await window.webSocketManager.reconnect();
                
                if (window.webSocketManager.isConnected()) {
                    console.log('✅ WebSocket reconnection successful');
                    return true;
                }
                
                // Try again with exponential backoff
                return this.handleWebSocketReconnection(attempt + 1, maxAttempts);
            } catch (error) {
                console.warn(`⚠️ WebSocket reconnection attempt ${attempt} failed:`, error);
                if (attempt === maxAttempts) {
                    this.showErrorState('system',
                        'Unable to establish real-time connection\n' +
                        'Some features may be delayed or require manual refresh\n' +
                        'Real-time updates will resume automatically when connection is restored');
                    return false;
                }
                return this.handleWebSocketReconnection(attempt + 1, maxAttempts);
            }
        }
        return false;
    }
    
    /**
     * Ensure interface content is properly initialized
     */
    ensureInterfaceContent(interfaceType) {
        // Convert camelCase to kebab-case for container IDs
        const containerName = interfaceType.replace(/([A-Z])/g, '-$1').toLowerCase();
        const containerId = `${containerName}-container`;
        const container = document.getElementById(containerId);
        
        console.log(`🔍 TRANSPARENCY DIAGNOSTIC: Looking for container: ${containerId}`);
        
        if (!container) {
            console.error(`❌ TRANSPARENCY DIAGNOSTIC: Container ${containerId} not found`);
            return;
        }
        
        // Check if container only has the default status message
        const statusMessage = container.querySelector('.status-message');
        if (statusMessage && container.children.length === 1) {
            console.warn(`⚠️ TRANSPARENCY DIAGNOSTIC: ${interfaceType} container only has status message, content not initialized`);
            
            // Try to initialize the interface content
            this.forceInterfaceInitialization(interfaceType, container);
        } else {
            console.log(`✅ TRANSPARENCY DIAGNOSTIC: ${interfaceType} container has content`);
        }
    }
    
    /**
     * Force initialization of interface content
     */
    forceInterfaceInitialization(interfaceType, container) {
        console.log(`🔧 TRANSPARENCY DIAGNOSTIC: Force initializing ${interfaceType} content...`);
        
        switch (interfaceType) {
            case 'knowledgeIngestion':
                if (window.knowledgeIngestionInterface && window.knowledgeIngestionInterface.initializeInterface) {
                    window.knowledgeIngestionInterface.initializeInterface();
                    console.log('✅ TRANSPARENCY DIAGNOSTIC: Knowledge ingestion interface content initialized');
                }
                break;
            case 'knowledgeManagement':
                if (window.knowledgeManagementInterface && window.knowledgeManagementInterface.initializeInterface) {
                    window.knowledgeManagementInterface.initializeInterface();
                    console.log('✅ TRANSPARENCY DIAGNOSTIC: Knowledge management interface content initialized');
                }
                break;
            case 'knowledgeSearch':
                if (window.knowledgeSearchInterface && window.knowledgeSearchInterface.initializeInterface) {
                    window.knowledgeSearchInterface.initializeInterface();
                    console.log('✅ TRANSPARENCY DIAGNOSTIC: Knowledge search interface content initialized');
                }
                break;
        }
    }
    
    /**
     * Initialize missing interface
     */
    initializeMissingInterface(interfaceType) {
        console.log(`🔧 TRANSPARENCY DIAGNOSTIC: Attempting to initialize missing ${interfaceType} interface...`);
        
        switch (interfaceType) {
            case 'knowledgeIngestion':
                if (window.KnowledgeIngestionInterface) {
                    window.knowledgeIngestionInterface = new window.KnowledgeIngestionInterface();
                    console.log('✅ TRANSPARENCY DIAGNOSTIC: Knowledge ingestion interface created');
                } else {
                    console.error('❌ TRANSPARENCY DIAGNOSTIC: KnowledgeIngestionInterface class not available');
                }
                break;
            case 'knowledgeManagement':
                if (window.KnowledgeManagementInterface) {
                    window.knowledgeManagementInterface = new window.KnowledgeManagementInterface();
                    console.log('✅ TRANSPARENCY DIAGNOSTIC: Knowledge management interface created');
                } else {
                    console.error('❌ TRANSPARENCY DIAGNOSTIC: KnowledgeManagementInterface class not available');
                }
                break;
            case 'knowledgeSearch':
                if (window.KnowledgeSearchInterface) {
                    window.knowledgeSearchInterface = new window.KnowledgeSearchInterface();
                    console.log('✅ TRANSPARENCY DIAGNOSTIC: Knowledge search interface created');
                } else {
                    console.error('❌ TRANSPARENCY DIAGNOSTIC: KnowledgeSearchInterface class not available');
                }
                break;
        }
    }
    
    setTransparencyLevel(level) {
        // Update visualization detail levels
        const event = new CustomEvent('transparencyLevelChanged', {
            detail: { level: level }
        });
        document.dispatchEvent(event);
        
        console.log(`🔍 Transparency level set to: ${level}`);
    }
    
    handleComplexityChange(complexityLevel) {
        // Auto-show panel in expert mode
        if (complexityLevel === 'expert' && !this.isVisible) {
            this.showPanel();
        } else if (complexityLevel === 'novice' && this.isVisible) {
            this.hidePanel();
        }
    }
    
    // Public methods for external access
    updateVisualization(tabName, data) {
        const pane = this.panel.querySelector(`#${tabName}Pane`);
        if (pane) {
            const container = pane.querySelector('.visualization-container');
            if (container) {
                // Update the visualization with new data
                const statusMessage = container.querySelector('.status-message');
                if (statusMessage && data) {
                    statusMessage.style.display = 'none';
                }
            }
        }
    }
    
    showLoadingState(tabName) {
        // Show global loading indicator
        const globalLoading = document.getElementById('transparency-loading');
        if (globalLoading) {
            globalLoading.innerHTML = `
                <div class="loading-spinner"></div>
                <div class="status-message">
                    <span class="status-text">Loading ${tabName} visualization...</span>
                </div>
            `;
            globalLoading.style.display = 'block';
        }
        
        // Also update the tab-specific loading state
        const pane = this.panel.querySelector(`#${tabName}Pane`);
        if (pane) {
            const container = pane.querySelector('.visualization-container');
            if (container) {
                const statusMessage = container.querySelector('.status-message');
                if (statusMessage) {
                    statusMessage.innerHTML = `
                        <div class="loading-spinner"></div>
                        <p>Loading ${tabName} visualization...</p>
                    `;
                    statusMessage.style.display = 'block';
                }
            }
        }
    }

    hideLoadingState(tabName) {
        // Hide global loading indicator
        const globalLoading = document.getElementById('transparency-loading');
        if (globalLoading) {
            globalLoading.style.display = 'none';
        }
        
        const pane = this.panel.querySelector(`#${tabName}Pane`);
        if (pane) {
            const container = pane.querySelector('.visualization-container');
            if (container) {
                const statusMessage = container.querySelector('.status-message');
                if (statusMessage) {
                    // Check if we have actual visualization content
                    const hasContent = container.querySelector('svg, canvas, .chart-container, .interface-content');
                    
                    if (hasContent) {
                        // Hide the loading message to reveal the visualization
                        statusMessage.style.display = 'none';
                    } else {
                        // Show fallback content if no visualization is present
                        statusMessage.innerHTML = `
                            <span class="status-icon">📊</span>
                            <span class="status-text">Ready for ${tabName} visualization. Submit a query to see content.</span>
                        `;
                        statusMessage.style.display = 'flex';
                    }
                    
                    // Ensure the container is visible and can hold visualizations
                    container.style.display = 'block';
                    container.style.minHeight = '400px';
                    
                    // If there's an SVG or canvas element, make sure it's visible
                    const vizElements = container.querySelectorAll('svg, canvas, .chart-container');
                    vizElements.forEach(el => {
                        el.style.display = 'block';
                        el.style.visibility = 'visible';
                    });
                }
            }
        }
    }
    
    /**
     * Initialize default content for all tab panes to ensure visibility
     */
    initializeDefaultContent() {
        console.log('🔧 TRANSPARENCY: Initializing default content for all panes');
        
        const tabPanes = [
            { id: 'reasoningPane', icon: '🧠', title: 'Reasoning Chains', desc: 'Submit a query to see step-by-step reasoning processes.' },
            { id: 'knowledgePane', icon: '🕸️', title: 'Knowledge Graph', desc: 'Submit a query to explore concept relationships and knowledge structure.' },
            { id: 'metacognitionPane', icon: '🎯', title: 'Metacognitive Dashboard', desc: 'System will display self-evaluation metrics and cognitive monitoring.' },
            { id: 'uncertaintyPane', icon: '📊', title: 'Uncertainty Analysis', desc: 'System will show confidence levels and uncertainty metrics.' },
            { id: 'provenancePane', icon: '📝', title: 'Provenance Explorer', desc: 'System will track knowledge sources and attribution chains.' },
            { id: 'knowledgeIngestionPane', icon: '📚', title: 'Knowledge Ingestion', desc: 'Upload and process new knowledge into the system.' },
            { id: 'knowledgeManagementPane', icon: '🔍', title: 'Knowledge Management', desc: 'Search, categorize, and manage your knowledge base.' },
            { id: 'knowledgeSearchPane', icon: '🔎', title: 'Knowledge Search', desc: 'Perform detailed searches with filters and analytics.' }
        ];
        
        tabPanes.forEach(pane => {
            const paneElement = this.panel?.querySelector(`#${pane.id}`);
            if (paneElement) {
                const container = paneElement.querySelector('.visualization-container');
                if (container) {
                    // Ensure the container has default content
                    let statusMessage = container.querySelector('.status-message');
                    if (!statusMessage) {
                        statusMessage = document.createElement('div');
                        statusMessage.className = 'status-message';
                        container.appendChild(statusMessage);
                    }
                    
                    statusMessage.innerHTML = `
                        <span class="status-icon">${pane.icon}</span>
                        <span class="status-text">${pane.desc}</span>
                    `;
                    statusMessage.style.display = 'flex';
                    
                    // Ensure container has minimum height
                    container.style.minHeight = '400px';
                    
                    console.log(`✅ TRANSPARENCY: Initialized default content for ${pane.id}`);
                }
            }
        });
    }
}

// Initialize when DOM is ready and handle cleanup
document.addEventListener('DOMContentLoaded', () => {
    window.transparencyPanelController = new TransparencyPanelController();
    
    // Clean up resources when page is unloaded
    window.addEventListener('unload', () => {
        if (window.transparencyPanelController) {
            window.transparencyPanelController.cleanup();
        }
    });
});

// Global function for HTML onclick handlers
window.toggleTransparencyPanel = function() {
    if (window.transparencyPanelController) {
        window.transparencyPanelController.togglePanel();
    } else {
        console.warn('Transparency panel controller not available');
    }
};

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = TransparencyPanelController;
}

console.log('✅ TransparencyPanelController module loaded with global toggleTransparencyPanel function');