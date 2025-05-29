/**
 * Tab Management System
 */

class TabManager {
    constructor() {
        this.init();
    }

    init() {
        this.setupEventListeners();
        console.log('✅ Tab Manager initialized');
    }

    setupEventListeners() {
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('tab-button')) {
                const tabId = e.target.getAttribute('data-tab');
                this.switchTab(tabId);
            }
        });
    }

    switchTab(tabId) {
        // Hide all tab panes
        document.querySelectorAll('.tab-pane').forEach(pane => {
            pane.classList.remove('active');
        });
        
        // Remove active state from all tab buttons
        document.querySelectorAll('.tab-button').forEach(button => {
            button.classList.remove('active');
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
        }
        
        // Handle lazy initialization of interfaces
        this.initializeTabInterface(tabId);
        
        console.log(`📋 Switched to tab: ${tabId}`);
    }
    
    initializeTabInterface(tabId) {
        switch (tabId) {
            case 'knowledgeIngestion':
                this.initializeKnowledgeIngestionInterface();
                break;
            case 'knowledgeManagement':
                this.initializeKnowledgeManagementInterface();
                break;
            case 'knowledgeSearch':
                this.initializeKnowledgeSearchInterface();
                break;
            default:
                // No special initialization needed
                break;
        }
    }
    
    initializeKnowledgeIngestionInterface() {
        // Check if interface needs initialization
        if (window.knowledgeIngestionInterface && !window.knowledgeIngestionInterface.initialized) {
            const container = document.getElementById('knowledgeIngestionPane');
            if (container) {
                try {
                    window.knowledgeIngestionInterface.initializeInterface();
                    console.log('✅ Knowledge Ingestion Interface lazy-initialized');
                } catch (error) {
                    console.error('❌ Failed to initialize Knowledge Ingestion Interface:', error);
                }
            } else {
                console.warn('⚠️ Knowledge Ingestion container not found');
            }
        }
    }
    
    initializeKnowledgeManagementInterface() {
        // Placeholder for knowledge management interface initialization
        console.log('🔍 Knowledge Management Interface check (placeholder)');
    }
    
    initializeKnowledgeSearchInterface() {
        // Placeholder for knowledge search interface initialization
        console.log('🔍 Knowledge Search Interface check (placeholder)');
    }
}

// Initialize tab manager
const tabManager = new TabManager();

// Make available globally
window.tabManager = tabManager;

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = TabManager;
}