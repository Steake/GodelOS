/**
 * Main Application Controller for GödelOS Frontend
 * Coordinates all components and manages application state
 */

class GödelOSApp {
    constructor() {
        this.isInitialized = false;
        this.components = {};
        this.state = {
            connected: false,
            processing: false,
            currentQuery: null,
            systemStatus: 'idle'
        };
        
        this.initializeApp();
    }

    /**
     * Initialize the application
     */
    async initializeApp() {
        try {
            console.log('Initializing GödelOS Frontend...');
            
            // Wait for DOM to be ready
            await this.waitForDOM();
            
            // Initialize components
            this.initializeComponents();
            
            // Setup global event listeners
            this.setupGlobalEventListeners();
            
            // Setup UI interactions
            this.setupUIInteractions();
            
            // Connect to backend
            this.connectToBackend();
            
            // Mark as initialized
            this.isInitialized = true;
            
            console.log('GödelOS Frontend initialized successfully');
            this.showWelcomeMessage();
            
        } catch (error) {
            console.error('Failed to initialize GödelOS Frontend:', error);
            this.showError('Failed to initialize application');
        }
    }

    /**
     * Wait for DOM to be ready
     */
    waitForDOM() {
        return new Promise((resolve) => {
            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', resolve);
            } else {
                resolve();
            }
        });
    }

    /**
     * Initialize all components
     */
    initializeComponents() {
        console.log('Initializing components...');
        
        // Components are already initialized globally
        this.components = {
            websocket: window.wsManager,
            visualization: window.vizManager,
            cognitive: window.cognitiveManager,
            query: window.queryHandler
        };
        
        // Verify all components are available
        Object.entries(this.components).forEach(([name, component]) => {
            if (!component) {
                console.warn(`Component ${name} not available`);
            } else {
                console.log(`✓ ${name} component ready`);
            }
        });
    }

    /**
     * Setup global event listeners
     */
    setupGlobalEventListeners() {
        // Window resize handler
        window.addEventListener('resize', this.debounce(() => {
            this.handleWindowResize();
        }, 250));

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            this.handleKeyboardShortcuts(e);
        });

        // Visibility change (tab switching)
        document.addEventListener('visibilitychange', () => {
            this.handleVisibilityChange();
        });

        // Before unload (cleanup)
        window.addEventListener('beforeunload', () => {
            this.cleanup();
        });

        // Error handling
        window.addEventListener('error', (e) => {
            console.error('Global error:', e.error);
            this.handleGlobalError(e.error);
        });

        // Unhandled promise rejections
        window.addEventListener('unhandledrejection', (e) => {
            console.error('Unhandled promise rejection:', e.reason);
            this.handleGlobalError(e.reason);
        });
    }

    /**
     * Setup UI interactions
     */
    setupUIInteractions() {
        // Panel toggles
        this.setupPanelToggles();
        
        // Theme switching (if implemented)
        this.setupThemeToggle();
        
        // Responsive menu (if needed)
        this.setupResponsiveMenu();
        
        // Tooltip initialization
        this.initializeTooltips();
    }

    /**
     * Setup panel toggle functionality
     */
    setupPanelToggles() {
        const toggleButtons = document.querySelectorAll('.panel-toggle');
        
        toggleButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                const panelName = e.target.getAttribute('data-panel');
                this.togglePanel(panelName);
            });
        });
    }

    /**
     * Toggle panel visibility
     * @param {string} panelName - Name of panel to toggle
     */
    togglePanel(panelName) {
        const panel = document.getElementById(`${panelName}Panel`);
        const button = document.querySelector(`[data-panel="${panelName}"]`);
        
        if (panel && button) {
            const isCollapsed = panel.classList.contains('collapsed');
            
            if (isCollapsed) {
                panel.classList.remove('collapsed');
                button.textContent = '−';
                this.animatePanel(panel, 'expand');
            } else {
                panel.classList.add('collapsed');
                button.textContent = '+';
                this.animatePanel(panel, 'collapse');
            }
        }
    }

    /**
     * Animate panel expand/collapse
     * @param {HTMLElement} panel - Panel element
     * @param {string} action - 'expand' or 'collapse'
     */
    animatePanel(panel, action) {
        const content = panel.querySelector('.panel-content');
        if (!content) return;

        if (action === 'collapse') {
            content.style.maxHeight = content.scrollHeight + 'px';
            requestAnimationFrame(() => {
                content.style.maxHeight = '0';
                content.style.opacity = '0';
            });
        } else {
            content.style.maxHeight = '0';
            content.style.opacity = '0';
            requestAnimationFrame(() => {
                content.style.maxHeight = content.scrollHeight + 'px';
                content.style.opacity = '1';
            });
            
            // Reset max-height after animation
            setTimeout(() => {
                content.style.maxHeight = 'none';
            }, 300);
        }
    }

    /**
     * Setup theme toggle (placeholder for future implementation)
     */
    setupThemeToggle() {
        // Could implement light/dark theme switching here
        const savedTheme = localStorage.getItem('godelOS_theme');
        if (savedTheme) {
            document.body.setAttribute('data-theme', savedTheme);
        }
    }

    /**
     * Setup responsive menu
     */
    setupResponsiveMenu() {
        // Handle mobile menu if needed
        const isMobile = window.innerWidth <= 768;
        if (isMobile) {
            this.enableMobileLayout();
        }
    }

    /**
     * Initialize tooltips
     */
    initializeTooltips() {
        const tooltipElements = document.querySelectorAll('[data-tooltip]');
        
        tooltipElements.forEach(element => {
            element.classList.add('tooltip');
        });
    }

    /**
     * Connect to backend
     */
    connectToBackend() {
        if (this.components.websocket) {
            // Use default WebSocket URL or from environment
            const wsUrl = this.getWebSocketURL();
            this.components.websocket.connect(wsUrl);
            
            // Update connection state
            this.components.websocket.on('connect', () => {
                this.updateConnectionState(true);
            });
            
            this.components.websocket.on('disconnect', () => {
                this.updateConnectionState(false);
            });
        }
    }

    /**
     * Get WebSocket URL from environment or use default
     * @returns {string} WebSocket URL
     */
    getWebSocketURL() {
        // In a real app, this might come from environment variables
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const host = window.location.hostname;
        const port = process?.env?.WS_PORT || '8080';
        
        return `${protocol}//${host}:${port}`;
    }

    /**
     * Update connection state
     * @param {boolean} connected - Connection status
     */
    updateConnectionState(connected) {
        this.state.connected = connected;
        
        if (connected) {
            this.showNotification('Connected to GödelOS backend', 'success');
        } else {
            this.showNotification('Disconnected from backend', 'warning');
        }
    }

    /**
     * Handle keyboard shortcuts
     * @param {KeyboardEvent} e - Keyboard event
     */
    handleKeyboardShortcuts(e) {
        // Ctrl/Cmd + Enter: Submit query
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
            if (this.components.query && !this.state.processing) {
                this.components.query.handleQuerySubmission();
            }
        }
        
        // Escape: Clear current operation
        if (e.key === 'Escape') {
            this.handleEscapeKey();
        }
        
        // Ctrl/Cmd + K: Focus search
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            const queryInput = document.getElementById('naturalLanguageQuery');
            if (queryInput) {
                queryInput.focus();
            }
        }
    }

    /**
     * Handle escape key press
     */
    handleEscapeKey() {
        // Close any open modals or overlays
        const modals = document.querySelectorAll('.modal-overlay.active');
        modals.forEach(modal => {
            modal.classList.remove('active');
        });
        
        // Clear any active selections
        if (this.components.visualization) {
            // Clear node selections in visualization
            const svg = document.querySelector('#knowledgeGraph');
            if (svg) {
                svg.querySelectorAll('.node.selected').forEach(node => {
                    node.classList.remove('selected');
                });
                svg.querySelectorAll('.link.highlighted').forEach(link => {
                    link.classList.remove('highlighted');
                });
            }
        }
    }

    /**
     * Handle window resize
     */
    handleWindowResize() {
        // Update visualization dimensions
        if (this.components.visualization) {
            this.components.visualization.handleResize();
        }
        
        // Update responsive layout
        const isMobile = window.innerWidth <= 768;
        if (isMobile) {
            this.enableMobileLayout();
        } else {
            this.enableDesktopLayout();
        }
    }

    /**
     * Enable mobile layout
     */
    enableMobileLayout() {
        document.body.classList.add('mobile-layout');
        
        // Collapse panels by default on mobile
        const panels = document.querySelectorAll('.panel');
        panels.forEach(panel => {
            if (!panel.classList.contains('response-panel')) {
                panel.classList.add('collapsed');
            }
        });
    }

    /**
     * Enable desktop layout
     */
    enableDesktopLayout() {
        document.body.classList.remove('mobile-layout');
        
        // Expand panels on desktop
        const panels = document.querySelectorAll('.panel.collapsed');
        panels.forEach(panel => {
            panel.classList.remove('collapsed');
        });
    }

    /**
     * Handle visibility change (tab switching)
     */
    handleVisibilityChange() {
        if (document.hidden) {
            // Page is hidden - pause non-essential animations
            this.pauseAnimations();
        } else {
            // Page is visible - resume animations
            this.resumeAnimations();
        }
    }

    /**
     * Pause animations when page is hidden
     */
    pauseAnimations() {
        const animatedElements = document.querySelectorAll('[style*="animation"]');
        animatedElements.forEach(element => {
            element.style.animationPlayState = 'paused';
        });
    }

    /**
     * Resume animations when page is visible
     */
    resumeAnimations() {
        const animatedElements = document.querySelectorAll('[style*="animation"]');
        animatedElements.forEach(element => {
            element.style.animationPlayState = 'running';
        });
    }

    /**
     * Handle global errors
     * @param {Error} error - Error object
     */
    handleGlobalError(error) {
        console.error('Global error handled:', error);
        
        // Show user-friendly error message
        this.showNotification('An unexpected error occurred', 'error');
        
        // Log error for debugging (in production, this might send to error tracking service)
        this.logError(error);
    }

    /**
     * Log error for debugging
     * @param {Error} error - Error to log
     */
    logError(error) {
        const errorData = {
            message: error.message,
            stack: error.stack,
            timestamp: new Date().toISOString(),
            userAgent: navigator.userAgent,
            url: window.location.href,
            state: this.state
        };
        
        // In production, this might send to an error tracking service
        console.log('Error logged:', errorData);
    }

    /**
     * Show notification to user
     * @param {string} message - Notification message
     * @param {string} type - Notification type
     */
    showNotification(message, type = 'info') {
        if (this.components.query) {
            this.components.query.showNotification(message, type);
        } else {
            console.log(`${type.toUpperCase()}: ${message}`);
        }
    }

    /**
     * Show error message
     * @param {string} message - Error message
     */
    showError(message) {
        this.showNotification(message, 'error');
    }

    /**
     * Show welcome message
     */
    showWelcomeMessage() {
        setTimeout(() => {
            this.showNotification('Welcome to GödelOS! Enter a query to begin exploring the knowledge base.', 'info');
        }, 1000);
    }

    /**
     * Debounce function for performance
     * @param {Function} func - Function to debounce
     * @param {number} wait - Wait time in milliseconds
     * @returns {Function} Debounced function
     */
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    /**
     * Cleanup when page unloads
     */
    cleanup() {
        console.log('Cleaning up GödelOS Frontend...');
        
        // Disconnect WebSocket
        if (this.components.websocket) {
            this.components.websocket.disconnect();
        }
        
        // Clean up cognitive animations
        if (this.components.cognitive) {
            this.components.cognitive.destroy();
        }
        
        // Save any pending data
        this.savePendingData();
    }

    /**
     * Save any pending data before unload
     */
    savePendingData() {
        // Save current session state
        try {
            const sessionData = {
                timestamp: Date.now(),
                state: this.state,
                currentQuery: this.state.currentQuery
            };
            sessionStorage.setItem('godelOS_session_state', JSON.stringify(sessionData));
        } catch (error) {
            console.warn('Failed to save session data:', error);
        }
    }

    /**
     * Restore session data
     */
    restoreSessionData() {
        try {
            const sessionData = sessionStorage.getItem('godelOS_session_state');
            if (sessionData) {
                const data = JSON.parse(sessionData);
                // Restore relevant state if session is recent (within 1 hour)
                if (Date.now() - data.timestamp < 3600000) {
                    this.state = { ...this.state, ...data.state };
                }
            }
        } catch (error) {
            console.warn('Failed to restore session data:', error);
        }
    }

    /**
     * Get application state
     * @returns {Object} Current application state
     */
    getState() {
        return { ...this.state };
    }

    /**
     * Update application state
     * @param {Object} newState - State updates
     */
    updateState(newState) {
        this.state = { ...this.state, ...newState };
    }
}

// Initialize the application
const app = new GödelOSApp();

// Make app globally available for debugging
window.godelOSApp = app;

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = GödelOSApp;
}