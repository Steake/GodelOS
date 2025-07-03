/**
 * Knowledge Management Interface
 * 
 * Provides comprehensive knowledge base management including search,
 * categorization, bulk operations, and analytics visualization.
 */

class KnowledgeManagementInterface {
    constructor() {
        this.apiClient = window.apiClient;
        this.searchResults = [];
        this.selectedItems = new Set();
        this.categories = [];
        this.currentView = 'grid';
        this.currentFilters = {};
        
        this.initializeInterface();
        this.setupEventListeners();
        this.loadCategories();
        this.loadStatistics();
        
        console.log('✅ Knowledge Management Interface initialized');
    }

    /**
     * Refresh the interface
     */
    refresh() {
        this.loadCategories();
        this.loadStatistics();
        if (this.searchResults.length > 0) {
            this.performSearch();
        }
    }

    initializeInterface() {
        // Get the main container (could be standalone or within transparency panel)
        const mainContainer = document.getElementById('knowledge-management-container');
        
        if (!mainContainer) {
            console.error('❌ KNOWLEDGE MANAGEMENT DIAGNOSTIC: knowledge-management-container not found');
            return;
        }
        
        console.log('✅ KNOWLEDGE MANAGEMENT DIAGNOSTIC: Container found, populating content...');
        console.log('🔍 KNOWLEDGE MANAGEMENT DIAGNOSTIC: Container parent:', mainContainer.parentElement?.id || 'no parent id');
        
        // Generate the interface HTML
        const interfaceHTML = `
            <div class="knowledge-management-interface">
                <!-- Search Section -->
                <div class="search-section">
                    <div class="search-header">
                        <h3>Knowledge Base Search</h3>
                        <div class="search-controls">
                            <button class="view-toggle" onclick="knowledgeManagement.toggleView()">
                                <i class="icon-grid"></i> <span id="view-toggle-text">List View</span>
                            </button>
                            <button class="bulk-actions-toggle" onclick="knowledgeManagement.toggleBulkActions()">
                                <i class="icon-check-square"></i> Bulk Actions
                            </button>
                        </div>
                    </div>
                    
                    <div class="search-form">
                        <div class="search-input-container">
                            <input type="text" id="search-query" placeholder="Search knowledge base..." autocomplete="off">
                            <button class="search-btn" onclick="knowledgeManagement.performSearch()">
                                <i class="icon-search"></i>
                            </button>
                            <button class="advanced-search-toggle" onclick="knowledgeManagement.toggleAdvancedSearch()">
                                <i class="icon-filter"></i> Advanced
                            </button>
                        </div>
                        
                        <div class="search-suggestions" id="search-suggestions"></div>
                    </div>
                    
                    <!-- Advanced Search Filters -->
                    <div class="advanced-search" id="advanced-search" style="display: none;">
                        <div class="filter-row">
                            <div class="filter-group">
                                <label>Search Type</label>
                                <select id="search-type">
                                    <option value="hybrid">Hybrid (Recommended)</option>
                                    <option value="full_text">Full Text</option>
                                    <option value="semantic">Semantic</option>
                                </select>
                            </div>
                            
                            <div class="filter-group">
                                <label>Knowledge Types</label>
                                <select id="knowledge-types" multiple>
                                    <option value="fact">Facts</option>
                                    <option value="rule">Rules</option>
                                    <option value="concept">Concepts</option>
                                    <option value="procedure">Procedures</option>
                                    <option value="example">Examples</option>
                                </select>
                            </div>
                            
                            <div class="filter-group">
                                <label>Categories</label>
                                <select id="search-categories" multiple>
                                    <!-- Categories will be populated dynamically -->
                                </select>
                            </div>
                        </div>
                        
                        <div class="filter-row">
                            <div class="filter-group">
                                <label>Source Types</label>
                                <select id="source-types" multiple>
                                    <option value="url">Web Pages</option>
                                    <option value="file">Files</option>
                                    <option value="wikipedia">Wikipedia</option>
                                    <option value="text">Manual Text</option>
                                </select>
                            </div>
                            
                            <div class="filter-group">
                                <label>Confidence Threshold</label>
                                <input type="range" id="confidence-threshold" min="0" max="1" step="0.1" value="0">
                                <span id="confidence-value">0%</span>
                            </div>
                            
                            <div class="filter-group">
                                <label>Max Results</label>
                                <select id="max-results">
                                    <option value="25">25</option>
                                    <option value="50" selected>50</option>
                                    <option value="100">100</option>
                                    <option value="200">200</option>
                                </select>
                            </div>
                        </div>
                        
                        <div class="filter-actions">
                            <button onclick="knowledgeManagement.applyFilters()">Apply Filters</button>
                            <button onclick="knowledgeManagement.clearFilters()">Clear All</button>
                            <button onclick="knowledgeManagement.saveSearchPreset()">Save Preset</button>
                        </div>
                    </div>
                </div>

                <!-- Search Results -->
                <div class="search-results-section">
                    <div class="results-header">
                        <div class="results-info">
                            <span id="results-count">0 results</span>
                            <span id="search-time"></span>
                        </div>
                        
                        <div class="results-controls">
                            <div class="sort-controls">
                                <label>Sort by:</label>
                                <select id="sort-by" onchange="knowledgeManagement.sortResults()">
                                    <option value="relevance">Relevance</option>
                                    <option value="date">Date Added</option>
                                    <option value="title">Title</option>
                                    <option value="confidence">Confidence</option>
                                    <option value="access_count">Access Count</option>
                                </select>
                            </div>
                        </div>
                    </div>
                    
                    <div class="search-results" id="search-results">
                        <!-- Results will be populated here -->
                    </div>
                </div>

                <!-- Statistics Dashboard -->
                <div class="statistics-section">
                    <h3>Knowledge Base Statistics</h3>
                    <div class="stats-grid">
                        <div class="stat-card">
                            <div class="stat-value" id="total-knowledge-items">0</div>
                            <div class="stat-label">Total Items</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value" id="avg-confidence">0%</div>
                            <div class="stat-label">Avg Confidence</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value" id="recent-imports">0</div>
                            <div class="stat-label">Recent Imports</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value" id="storage-size">0 MB</div>
                            <div class="stat-label">Storage Used</div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Populate the container (works for both standalone and transparency panel contexts)
        console.log('✅ KNOWLEDGE MANAGEMENT DIAGNOSTIC: Populating container with interface HTML');
        mainContainer.innerHTML = interfaceHTML;
        
        // Set up event listeners after DOM is updated
        setTimeout(() => {
            this.setupEventListeners();
        }, 100);
    }

    setupEventListeners() {
        // Search input
        const searchInput = document.getElementById('search-query');
        if (searchInput) {
            searchInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    this.performSearch();
                }
            });
        }

        // Confidence threshold slider
        const confidenceSlider = document.getElementById('confidence-threshold');
        if (confidenceSlider) {
            confidenceSlider.addEventListener('input', (e) => {
                document.getElementById('confidence-value').textContent = `${Math.round(e.target.value * 100)}%`;
            });
        }
    }

    async performSearch() {
        const query = document.getElementById('search-query').value.trim();
        if (!query) {
            this.showError('Please enter a search query');
            return;
        }

        try {
            const searchParams = this.buildSearchParams(query);
            const response = await this.apiClient.get('/api/knowledge/search', searchParams);
            
            this.searchResults = response.results;
            this.displaySearchResults(response);
            this.updateResultsInfo(response);
            
        } catch (error) {
            this.showError(`Search failed: ${error.message}`);
        }
    }

    buildSearchParams(query) {
        const params = new URLSearchParams();
        params.append('query', query);
        params.append('search_type', 'hybrid');
        params.append('include_snippets', 'true');
        params.append('highlight_terms', 'true');
        return params;
    }

    displaySearchResults(response) {
        const container = document.getElementById('search-results');
        if (!response.results.length) {
            container.innerHTML = '<div class="no-results">No results found. Try adjusting your search terms.</div>';
            return;
        }

        const resultsHTML = response.results.map(result => this.createResultElement(result)).join('');
        container.innerHTML = resultsHTML;
    }

    createResultElement(result) {
        const item = result.knowledge_item;
        
        return `
            <div class="search-result-item" data-item-id="${item.id}">
                <div class="result-header">
                    <div class="result-info">
                        <h4 class="result-title" onclick="knowledgeManagement.viewKnowledgeItem('${item.id}')">
                            ${item.title || 'Untitled'}
                        </h4>
                        <div class="result-meta">
                            <span class="knowledge-type">${item.knowledge_type}</span>
                            <span class="source-type">${item.source.source_type}</span>
                            <span class="confidence">Confidence: ${Math.round(item.confidence * 100)}%</span>
                            <span class="date">Added: ${new Date(item.extracted_at * 1000).toLocaleDateString()}</span>
                        </div>
                    </div>
                    <div class="result-actions">
                        <div class="relevance-score">
                            Score: ${result.relevance_score.toFixed(2)}
                        </div>
                        <button onclick="knowledgeManagement.viewKnowledgeItem('${item.id}')" class="view-btn">
                            <i class="icon-eye"></i>
                        </button>
                    </div>
                </div>
                
                <div class="result-content">
                    <div class="result-snippet">
                        ${result.snippet || item.content.substring(0, 200) + '...'}
                    </div>
                    
                    <div class="result-categories">
                        ${(item.categories || []).map(cat => `<span class="category-tag">${cat}</span>`).join('')}
                        ${(item.auto_categories || []).map(cat => `<span class="category-tag auto">${cat}</span>`).join('')}
                    </div>
                </div>
            </div>
        `;
    }

    updateResultsInfo(response) {
        document.getElementById('results-count').textContent = 
            `${response.total_matches} result${response.total_matches !== 1 ? 's' : ''}`;
        
        document.getElementById('search-time').textContent = 
            `(${response.search_time_ms.toFixed(0)}ms)`;
    }

    async viewKnowledgeItem(itemId) {
        try {
            const item = await this.apiClient.get(`/api/knowledge/${itemId}`);
            alert(`Knowledge Item: ${item.title}\n\nContent: ${item.content.substring(0, 500)}...`);
        } catch (error) {
            this.showError(`Failed to load knowledge item: ${error.message}`);
        }
    }

    async loadCategories() {
        try {
            this.categories = await this.apiClient.get('/api/transparency/knowledge/categories');
        } catch (error) {
            console.error('Failed to load categories:', error);
        }
    }

    async loadStatistics() {
        try {
            const stats = await this.apiClient.get('/api/transparency/knowledge/statistics');
            this.displayStatistics(stats);
        } catch (error) {
            console.error('Failed to load statistics:', error);
        }
    }

    displayStatistics(response) {
        // Extract statistics from the response structure
        const stats = response.statistics || response;
        
        // Use safe access with fallback values
        const totalItems = stats.total_knowledge_items || stats.total_items || 0;
        const avgConfidence = stats.avg_confidence || stats.average_confidence || 0;
        const recentAdditions = stats.recent_additions || stats.recent_imports || 0;
        const storageSize = stats.total_storage_mb || 0;
        
        // Update DOM elements with safe checks
        const totalEl = document.getElementById('total-knowledge-items');
        if (totalEl) totalEl.textContent = totalItems;
        
        const avgEl = document.getElementById('avg-confidence');
        if (avgEl) avgEl.textContent = `${Math.round(avgConfidence * 100)}%`;
        
        const recentEl = document.getElementById('recent-imports');
        if (recentEl) recentEl.textContent = recentAdditions;
        
        const storageEl = document.getElementById('storage-size');
        if (storageEl) storageEl.textContent = `${storageSize.toFixed ? storageSize.toFixed(1) : storageSize} MB`;
    }

    toggleAdvancedSearch() {
        const advancedSearch = document.getElementById('advanced-search');
        advancedSearch.style.display = advancedSearch.style.display === 'none' ? 'block' : 'none';
    }

    showSuccess(message) {
        this.showNotification(message, 'success');
    }

    showError(message) {
        this.showNotification(message, 'error');
    }

    showNotification(message, type) {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.innerHTML = `
            <span>${message}</span>
            <button onclick="this.parentElement.remove()">×</button>
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 5000);
    }

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
}

// Make the class available globally
window.KnowledgeManagementInterface = KnowledgeManagementInterface;

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.knowledgeManagement = new KnowledgeManagementInterface();
    window.knowledgeManagementInterface = window.knowledgeManagement; // Also make it available as knowledgeManagementInterface
    console.log('✅ Knowledge Management Interface initialized and class available globally');
});