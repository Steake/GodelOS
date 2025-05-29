/**
 * Knowledge Search Interface
 * 
 * Provides advanced search functionality for the knowledge base with
 * real-time search, filters, and result visualization.
 */

class KnowledgeSearchInterface {
    constructor() {
        this.apiClient = window.apiClient;
        this.searchHistory = [];
        this.savedSearches = [];
        this.currentQuery = '';
        this.searchTimeout = null;
        
        this.initializeInterface();
        this.setupEventListeners();
        this.loadSearchHistory();
        
        console.log('✅ Knowledge Search Interface initialized');
    }

    /**
     * Refresh the interface
     */
    refresh() {
        this.loadSearchHistory();
        if (this.currentQuery) {
            this.performQuickSearch();
        }
    }

    initializeInterface() {
        // Get the main container (could be standalone or within transparency panel)
        const mainContainer = document.getElementById('knowledge-search-container');
        
        if (!mainContainer) {
            console.error('❌ KNOWLEDGE SEARCH DIAGNOSTIC: knowledge-search-container not found');
            return;
        }
        
        console.log('✅ KNOWLEDGE SEARCH DIAGNOSTIC: Container found, populating content...');
        console.log('🔍 KNOWLEDGE SEARCH DIAGNOSTIC: Container parent:', mainContainer.parentElement?.id || 'no parent id');
        
        // Generate the interface HTML
        const interfaceHTML = `
            <div class="knowledge-search-interface">
                <!-- Quick Search Bar -->
                <div class="quick-search-section">
                    <div class="search-bar">
                        <div class="search-input-wrapper">
                            <input type="text" id="quick-search-input" 
                                   placeholder="Search knowledge base..." 
                                   autocomplete="off">
                            <button class="search-button" onclick="knowledgeSearch.performQuickSearch()">
                                <i class="icon-search"></i>
                            </button>
                            <button class="voice-search-button" onclick="knowledgeSearch.startVoiceSearch()">
                                <i class="icon-mic"></i>
                            </button>
                        </div>
                        
                        <div class="search-suggestions-dropdown" id="search-suggestions-dropdown">
                            <!-- Real-time suggestions will appear here -->
                        </div>
                    </div>
                    
                    <div class="quick-filters">
                        <button class="filter-chip" data-filter="recent" onclick="knowledgeSearch.applyQuickFilter('recent')">
                            Recent
                        </button>
                        <button class="filter-chip" data-filter="high-confidence" onclick="knowledgeSearch.applyQuickFilter('high-confidence')">
                            High Confidence
                        </button>
                        <button class="filter-chip" data-filter="frequently-accessed" onclick="knowledgeSearch.applyQuickFilter('frequently-accessed')">
                            Popular
                        </button>
                        <button class="filter-chip" data-filter="wikipedia" onclick="knowledgeSearch.applyQuickFilter('wikipedia')">
                            Wikipedia
                        </button>
                        <button class="filter-chip" data-filter="files" onclick="knowledgeSearch.applyQuickFilter('files')">
                            Files
                        </button>
                    </div>
                </div>

                <!-- Advanced Search Panel -->
                <div class="advanced-search-panel" id="advanced-search-panel" style="display: none;">
                    <h4>Advanced Search</h4>
                    
                    <div class="search-fields">
                        <div class="field-group">
                            <label>Search in Content</label>
                            <input type="text" id="content-search" placeholder="Search in content...">
                        </div>
                        
                        <div class="field-group">
                            <label>Search in Title</label>
                            <input type="text" id="title-search" placeholder="Search in titles...">
                        </div>
                        
                        <div class="field-group">
                            <label>Exact Phrase</label>
                            <input type="text" id="exact-phrase" placeholder="Exact phrase match...">
                        </div>
                        
                        <div class="field-group">
                            <label>Exclude Words</label>
                            <input type="text" id="exclude-words" placeholder="Words to exclude...">
                        </div>
                    </div>
                    
                    <div class="search-options">
                        <div class="option-group">
                            <label>Search Type</label>
                            <div class="radio-group">
                                <label><input type="radio" name="search-type" value="hybrid" checked> Hybrid</label>
                                <label><input type="radio" name="search-type" value="full_text"> Full Text</label>
                                <label><input type="radio" name="search-type" value="semantic"> Semantic</label>
                            </div>
                        </div>
                        
                        <div class="option-group">
                            <label>Date Range</label>
                            <div class="date-range">
                                <input type="date" id="date-from" placeholder="From">
                                <input type="date" id="date-to" placeholder="To">
                            </div>
                        </div>
                        
                        <div class="option-group">
                            <label>Confidence Range</label>
                            <div class="range-slider">
                                <input type="range" id="confidence-min" min="0" max="100" value="0">
                                <input type="range" id="confidence-max" min="0" max="100" value="100">
                                <div class="range-values">
                                    <span id="confidence-min-value">0%</span> - 
                                    <span id="confidence-max-value">100%</span>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="search-actions">
                        <button onclick="knowledgeSearch.performAdvancedSearch()" class="primary-button">
                            Search
                        </button>
                        <button onclick="knowledgeSearch.clearAdvancedSearch()">
                            Clear
                        </button>
                        <button onclick="knowledgeSearch.saveCurrentSearch()">
                            Save Search
                        </button>
                    </div>
                </div>

                <!-- Search Results -->
                <div class="search-results-container">
                    <div class="results-header">
                        <div class="results-summary">
                            <span id="results-summary">Ready to search</span>
                        </div>
                        
                        <div class="results-actions">
                            <button onclick="knowledgeSearch.toggleAdvancedSearch()" id="advanced-toggle">
                                <i class="icon-sliders"></i> Advanced
                            </button>
                            <button onclick="knowledgeSearch.exportResults()" id="export-button" disabled>
                                <i class="icon-download"></i> Export
                            </button>
                            <button onclick="knowledgeSearch.shareSearch()" id="share-button" disabled>
                                <i class="icon-share"></i> Share
                            </button>
                        </div>
                    </div>
                    
                    <div class="search-results-list" id="search-results-list">
                        <!-- Search results will be displayed here -->
                    </div>
                    
                    <div class="load-more-container" id="load-more-container" style="display: none;">
                        <button onclick="knowledgeSearch.loadMoreResults()" id="load-more-button">
                            Load More Results
                        </button>
                    </div>
                </div>

                <!-- Search History Sidebar -->
                <div class="search-history-sidebar" id="search-history-sidebar">
                    <div class="sidebar-header">
                        <h4>Search History</h4>
                        <button onclick="knowledgeSearch.clearSearchHistory()" class="clear-history-button">
                            <i class="icon-trash"></i>
                        </button>
                    </div>
                    
                    <div class="history-list" id="history-list">
                        <!-- Search history items will be displayed here -->
                    </div>
                    
                    <div class="sidebar-section">
                        <h5>Saved Searches</h5>
                        <div class="saved-searches-list" id="saved-searches-list">
                            <!-- Saved searches will be displayed here -->
                        </div>
                    </div>
                </div>

                <!-- Search Analytics -->
                <div class="search-analytics" id="search-analytics" style="display: none;">
                    <h4>Search Analytics</h4>
                    <div class="analytics-grid">
                        <div class="metric-card">
                            <span class="metric-value" id="total-searches">0</span>
                            <span class="metric-label">Total Searches</span>
                        </div>
                        <div class="metric-card">
                            <span class="metric-value" id="avg-results">0</span>
                            <span class="metric-label">Avg Results</span>
                        </div>
                        <div class="metric-card">
                            <span class="metric-value" id="most-searched">-</span>
                            <span class="metric-label">Most Searched</span>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Populate the container (works for both standalone and transparency panel contexts)
        console.log('✅ KNOWLEDGE SEARCH DIAGNOSTIC: Populating container with interface HTML');
        mainContainer.innerHTML = interfaceHTML;
        
        // Set up event listeners after DOM is updated
        setTimeout(() => {
            this.setupEventListeners();
        }, 100);
    }

    setupEventListeners() {
        // Quick search input
        const quickSearchInput = document.getElementById('quick-search-input');
        if (quickSearchInput) {
            quickSearchInput.addEventListener('input', this.debounce(this.handleSearchInput.bind(this), 300));
            quickSearchInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    this.performQuickSearch();
                }
            });
            quickSearchInput.addEventListener('focus', this.showSearchSuggestions.bind(this));
            quickSearchInput.addEventListener('blur', this.hideSearchSuggestions.bind(this));
        }

        // Confidence range sliders
        const confidenceMin = document.getElementById('confidence-min');
        const confidenceMax = document.getElementById('confidence-max');
        
        if (confidenceMin && confidenceMax) {
            confidenceMin.addEventListener('input', this.updateConfidenceRange.bind(this));
            confidenceMax.addEventListener('input', this.updateConfidenceRange.bind(this));
        }

        // Advanced search inputs
        document.querySelectorAll('#advanced-search-panel input').forEach(input => {
            input.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    this.performAdvancedSearch();
                }
            });
        });

        // Click outside to close suggestions
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.search-input-wrapper')) {
                this.hideSearchSuggestions();
            }
        });
    }

    async handleSearchInput(e) {
        const query = e.target.value.trim();
        this.currentQuery = query;
        
        if (query.length > 2) {
            await this.showSearchSuggestions();
        } else {
            this.hideSearchSuggestions();
        }
    }

    async showSearchSuggestions() {
        if (!this.currentQuery || this.currentQuery.length < 3) return;

        const dropdown = document.getElementById('search-suggestions-dropdown');
        dropdown.innerHTML = '<div class="loading-suggestions">Loading suggestions...</div>';
        dropdown.style.display = 'block';

        try {
            // Simulate getting suggestions - in real implementation, this would call an API
            const suggestions = await this.generateSearchSuggestions(this.currentQuery);
            
            if (suggestions.length > 0) {
                dropdown.innerHTML = suggestions.map(suggestion => `
                    <div class="suggestion-item" onclick="knowledgeSearch.selectSuggestion('${suggestion}')">
                        <i class="icon-search"></i>
                        <span class="suggestion-text">${suggestion}</span>
                        <span class="suggestion-type">Search</span>
                    </div>
                `).join('');
            } else {
                dropdown.innerHTML = '<div class="no-suggestions">No suggestions found</div>';
            }
            
        } catch (error) {
            dropdown.innerHTML = '<div class="suggestion-error">Error loading suggestions</div>';
        }
    }

    hideSearchSuggestions() {
        setTimeout(() => {
            const dropdown = document.getElementById('search-suggestions-dropdown');
            dropdown.style.display = 'none';
        }, 200);
    }

    selectSuggestion(suggestion) {
        document.getElementById('quick-search-input').value = suggestion;
        this.hideSearchSuggestions();
        this.performQuickSearch();
    }

    async generateSearchSuggestions(query) {
        // Simulate search suggestions based on query
        const baseSuggestions = [
            `${query} concepts`,
            `${query} examples`,
            `${query} procedures`,
            `${query} facts`,
            `${query} in wikipedia`,
            `${query} recent`
        ];
        
        return baseSuggestions.slice(0, 5);
    }

    async performQuickSearch() {
        const query = document.getElementById('quick-search-input').value.trim();
        if (!query) {
            this.showError('Please enter a search query');
            return;
        }

        this.addToSearchHistory(query);
        await this.executeSearch({
            query: query,
            search_type: 'hybrid',
            max_results: 50
        });
    }

    async performAdvancedSearch() {
        const searchParams = this.buildAdvancedSearchParams();
        if (!searchParams.query) {
            this.showError('Please enter at least one search term');
            return;
        }

        this.addToSearchHistory(searchParams.query);
        await this.executeSearch(searchParams);
    }

    buildAdvancedSearchParams() {
        const contentSearch = document.getElementById('content-search').value.trim();
        const titleSearch = document.getElementById('title-search').value.trim();
        const exactPhrase = document.getElementById('exact-phrase').value.trim();
        const excludeWords = document.getElementById('exclude-words').value.trim();
        
        // Build query string
        let queryParts = [];
        if (contentSearch) queryParts.push(contentSearch);
        if (titleSearch) queryParts.push(`title:${titleSearch}`);
        if (exactPhrase) queryParts.push(`"${exactPhrase}"`);
        if (excludeWords) queryParts.push(`-${excludeWords.split(' ').join(' -')}`);
        
        const query = queryParts.join(' ');
        
        const searchType = document.querySelector('input[name="search-type"]:checked').value;
        const dateFrom = document.getElementById('date-from').value;
        const dateTo = document.getElementById('date-to').value;
        const confidenceMin = document.getElementById('confidence-min').value / 100;
        const confidenceMax = document.getElementById('confidence-max').value / 100;
        
        const params = {
            query: query,
            search_type: searchType,
            confidence_threshold: confidenceMin,
            max_results: 100
        };
        
        if (dateFrom || dateTo) {
            params.date_range = {};
            if (dateFrom) params.date_range.start = new Date(dateFrom).getTime() / 1000;
            if (dateTo) params.date_range.end = new Date(dateTo).getTime() / 1000;
        }
        
        return params;
    }

    async executeSearch(params) {
        this.showSearchLoading();
        
        try {
            const urlParams = new URLSearchParams();
            Object.entries(params).forEach(([key, value]) => {
                if (typeof value === 'object') {
                    urlParams.append(key, JSON.stringify(value));
                } else {
                    urlParams.append(key, value);
                }
            });
            
            const response = await this.apiClient.get('/api/knowledge/search', urlParams);
            this.displaySearchResults(response);
            this.updateSearchSummary(response);
            
        } catch (error) {
            this.showError(`Search failed: ${error.message}`);
        } finally {
            this.hideSearchLoading();
        }
    }

    displaySearchResults(response) {
        const container = document.getElementById('search-results-list');
        
        if (!response.results || response.results.length === 0) {
            container.innerHTML = `
                <div class="no-results">
                    <i class="icon-search"></i>
                    <h3>No results found</h3>
                    <p>Try adjusting your search terms or using different filters.</p>
                </div>
            `;
            return;
        }
        
        const resultsHTML = response.results.map(result => this.createSearchResultElement(result)).join('');
        container.innerHTML = resultsHTML;
        
        // Enable action buttons
        document.getElementById('export-button').disabled = false;
        document.getElementById('share-button').disabled = false;
    }

    createSearchResultElement(result) {
        const item = result.knowledge_item;
        const snippet = result.snippet || item.content.substring(0, 200) + '...';
        
        return `
            <div class="search-result-card" onclick="knowledgeSearch.viewResult('${item.id}')">
                <div class="result-header">
                    <h3 class="result-title">${item.title || 'Untitled'}</h3>
                    <div class="result-score">
                        <span class="score-value">${result.relevance_score.toFixed(2)}</span>
                        <span class="score-label">Relevance</span>
                    </div>
                </div>
                
                <div class="result-snippet">${snippet}</div>
                
                <div class="result-metadata">
                    <span class="metadata-item">
                        <i class="icon-type"></i> ${item.knowledge_type}
                    </span>
                    <span class="metadata-item">
                        <i class="icon-source"></i> ${item.source.source_type}
                    </span>
                    <span class="metadata-item">
                        <i class="icon-confidence"></i> ${Math.round(item.confidence * 100)}%
                    </span>
                    <span class="metadata-item">
                        <i class="icon-calendar"></i> ${new Date(item.extracted_at * 1000).toLocaleDateString()}
                    </span>
                </div>
                
                <div class="result-categories">
                    ${(item.categories || []).map(cat => `<span class="category-tag">${cat}</span>`).join('')}
                </div>
            </div>
        `;
    }

    updateSearchSummary(response) {
        const summary = document.getElementById('results-summary');
        const count = response.total_matches;
        const time = response.search_time_ms;
        
        summary.textContent = `Found ${count} result${count !== 1 ? 's' : ''} in ${time.toFixed(0)}ms`;
    }

    applyQuickFilter(filterType) {
        // Remove active state from all filter chips
        document.querySelectorAll('.filter-chip').forEach(chip => {
            chip.classList.remove('active');
        });
        
        // Add active state to clicked filter
        document.querySelector(`[data-filter="${filterType}"]`).classList.add('active');
        
        let searchParams = {};
        
        switch (filterType) {
            case 'recent':
                const oneWeekAgo = new Date();
                oneWeekAgo.setDate(oneWeekAgo.getDate() - 7);
                searchParams = {
                    query: '*',
                    date_range: { start: oneWeekAgo.getTime() / 1000 }
                };
                break;
                
            case 'high-confidence':
                searchParams = {
                    query: '*',
                    confidence_threshold: 0.8
                };
                break;
                
            case 'frequently-accessed':
                searchParams = {
                    query: '*',
                    sort_by: 'access_count'
                };
                break;
                
            case 'wikipedia':
                searchParams = {
                    query: '*',
                    source_types: ['wikipedia']
                };
                break;
                
            case 'files':
                searchParams = {
                    query: '*',
                    source_types: ['file']
                };
                break;
        }
        
        this.executeSearch(searchParams);
    }

    toggleAdvancedSearch() {
        const panel = document.getElementById('advanced-search-panel');
        const button = document.getElementById('advanced-toggle');
        
        if (panel.style.display === 'none') {
            panel.style.display = 'block';
            button.innerHTML = '<i class="icon-x"></i> Close';
        } else {
            panel.style.display = 'none';
            button.innerHTML = '<i class="icon-sliders"></i> Advanced';
        }
    }

    clearAdvancedSearch() {
        document.getElementById('content-search').value = '';
        document.getElementById('title-search').value = '';
        document.getElementById('exact-phrase').value = '';
        document.getElementById('exclude-words').value = '';
        document.getElementById('date-from').value = '';
        document.getElementById('date-to').value = '';
        document.getElementById('confidence-min').value = 0;
        document.getElementById('confidence-max').value = 100;
        document.querySelector('input[value="hybrid"]').checked = true;
        this.updateConfidenceRange();
    }

    updateConfidenceRange() {
        const min = document.getElementById('confidence-min').value;
        const max = document.getElementById('confidence-max').value;
        document.getElementById('confidence-min-value').textContent = `${min}%`;
        document.getElementById('confidence-max-value').textContent = `${max}%`;
    }

    addToSearchHistory(query) {
        const historyItem = {
            query: query,
            timestamp: Date.now(),
            id: Date.now().toString()
        };
        
        this.searchHistory.unshift(historyItem);
        this.searchHistory = this.searchHistory.slice(0, 20); // Keep only last 20 searches
        
        this.saveSearchHistory();
        this.updateHistoryDisplay();
    }

    updateHistoryDisplay() {
        const container = document.getElementById('history-list');
        
        if (this.searchHistory.length === 0) {
            container.innerHTML = '<div class="empty-history">No search history</div>';
            return;
        }
        
        container.innerHTML = this.searchHistory.map(item => `
            <div class="history-item" onclick="knowledgeSearch.repeatSearch('${item.query}')">
                <span class="history-query">${item.query}</span>
                <span class="history-time">${new Date(item.timestamp).toLocaleDateString()}</span>
            </div>
        `).join('');
    }

    repeatSearch(query) {
        document.getElementById('quick-search-input').value = query;
        this.performQuickSearch();
    }

    clearSearchHistory() {
        if (confirm('Clear all search history?')) {
            this.searchHistory = [];
            this.saveSearchHistory();
            this.updateHistoryDisplay();
        }
    }

    saveSearchHistory() {
        localStorage.setItem('knowledgeSearchHistory', JSON.stringify(this.searchHistory));
    }

    loadSearchHistory() {
        const saved = localStorage.getItem('knowledgeSearchHistory');
        if (saved) {
            this.searchHistory = JSON.parse(saved);
            this.updateHistoryDisplay();
        }
    }

    async viewResult(itemId) {
        try {
            const item = await this.apiClient.get(`/api/knowledge/${itemId}`);
            // For now, just show an alert - in full implementation, this would open a detailed view
            alert(`Knowledge Item: ${item.title}\n\nContent: ${item.content.substring(0, 500)}...`);
        } catch (error) {
            this.showError(`Failed to load knowledge item: ${error.message}`);
        }
    }

    showSearchLoading() {
        const container = document.getElementById('search-results-list');
        container.innerHTML = `
            <div class="search-loading">
                <div class="loading-spinner"></div>
                <p>Searching knowledge base...</p>
            </div>
        `;
    }

    hideSearchLoading() {
        // Loading will be replaced by results
    }

    showError(message) {
        const notification = document.createElement('div');
        notification.className = 'notification error';
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
window.KnowledgeSearchInterface = KnowledgeSearchInterface;

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.knowledgeSearch = new KnowledgeSearchInterface();
    window.knowledgeSearchInterface = window.knowledgeSearch; // Also make it available as knowledgeSearchInterface
    console.log('✅ Knowledge Search Interface initialized and class available globally');
});