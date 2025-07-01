/**
 * Provenance Explorer for GödelOS
 * Provides interactive provenance chain navigation, attribution tracking,
 * and temporal versioning with rollback capabilities
 */

class ProvenanceExplorer {
    constructor(containerId = 'provenanceExploration') {
        this.containerId = containerId;
        this.container = null;
        this.svg = null;
        this.width = 800;
        this.height = 600;
        this.margin = { top: 20, right: 20, bottom: 20, left: 20 };
        
        // Provenance data
        this.provenanceData = {
            chains: new Map(),
            versions: new Map(),
            attributions: new Map(),
            dependencies: new Map()
        };
        
        // Visualization state
        this.currentChain = null;
        this.selectedVersion = null;
        this.viewMode = 'timeline';
        this.timeRange = { start: null, end: null };
        
        // D3 elements
        this.simulation = null;
        this.timeline = null;
        this.zoom = null;
        
        // WebSocket connection
        this.wsConnection = null;
        
        this.initialize();
    }

    /**
     * Initialize the provenance explorer
     */
    initialize() {
        this.createContainer();
        this.setupLayout();
        this.setupWebSocketConnection();
        this.setupEventListeners();
        this.loadInitialData();
        
        console.log('Provenance Explorer initialized');
    }

    // Add required refresh method
    refresh(chainId) {
        if (!chainId) {
            console.error('Cannot refresh - chainId is undefined');
            return Promise.reject(new Error('chainId is required'));
        }

        console.log(`Refreshing provenance chain ${chainId}`);
        return fetch(`/api/provenance/${chainId}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`API request failed: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                if (!data) {
                    throw new Error('Empty response from API');
                }
                this.provenanceData.chains.set(chainId, data);
                return true;
            })
            .catch(error => {
                console.error('Failed to refresh provenance:', error);
                this.showErrorState(`Failed to load provenance: ${error.message}`);
                return false;
            });
    }

    showErrorState(message) {
        if (!this.container) return;
        
        this.container.selectAll('.error-state').remove();
        this.container.append('div')
            .attr('class', 'error-state')
            .style('color', 'red')
            .style('padding', '1em')
            .text(message);
    }

    /**
     * Create the visualization container
     */
    createContainer() {
        try {
            this.container = d3.select(`#${this.containerId}`);
            if (this.container.empty()) {
                throw new Error(`Container #${this.containerId} not found`);
            }
            
            this.container.classed('provenance-explorer', true);
            return true;
        } catch (error) {
            console.error('Failed to create container:', error);
            return false;
        }
    }

    /**
     * Setup explorer layout
     */
    setupLayout() {
        // Clear existing content
        this.container.selectAll('*').remove();
        
        // Create header with controls
        const header = this.container.append('div')
            .attr('class', 'provenance-header');
            
        header.append('h3')
            .text('Provenance & Attribution Explorer');
            
        this.createControls(header);
        
        // Create main layout with sidebar and visualization
        const mainLayout = this.container.append('div')
            .attr('class', 'provenance-main-layout');
            
        // Create sidebar for chain list
        this.createSidebar(mainLayout);
        
        // Create main visualization area
        const vizArea = mainLayout.append('div')
            .attr('class', 'provenance-viz-area');
            
        // Create view mode tabs
        this.createViewTabs(vizArea);
        
        // Create main SVG
        this.svg = vizArea.append('svg')
            .attr('width', '100%')
            .attr('height', this.height)
            .attr('viewBox', `0 0 ${this.width} ${this.height}`)
            .attr('preserveAspectRatio', 'xMidYMid meet');
            
        // Setup zoom behavior
        this.zoom = d3.zoom()
            .scaleExtent([0.1, 5])
            .on('zoom', (event) => {
                this.mainGroup.attr('transform', event.transform);
            });
            
        this.svg.call(this.zoom);
        
        // Create main group for zoomable content
        this.mainGroup = this.svg.append('g').attr('class', 'main-group');
        
        // Create details panel
        this.createDetailsPanel(vizArea);
        
        // Initialize default view
        this.switchViewMode('timeline');
    }

    /**
     * Create control panel
     */
    createControls(parent) {
        const controls = parent.append('div')
            .attr('class', 'provenance-controls');
            
        // Search controls
        const searchGroup = controls.append('div')
            .attr('class', 'control-group');
            
        searchGroup.append('input')
            .attr('type', 'text')
            .attr('id', 'provenanceSearch')
            .attr('placeholder', 'Search provenance chains...')
            .on('input', () => this.handleSearch());
            
        searchGroup.append('button')
            .attr('class', 'btn secondary')
            .html('🔍')
            .on('click', () => this.executeSearch());
            
        // Time range controls
        const timeGroup = controls.append('div')
            .attr('class', 'control-group');
            
        timeGroup.append('label').text('Time Range:');
        
        timeGroup.append('button')
            .attr('class', 'btn secondary')
            .text('Last Hour')
            .on('click', () => this.setTimeRange(1));
            
        timeGroup.append('button')
            .attr('class', 'btn secondary')
            .text('Last Day')
            .on('click', () => this.setTimeRange(24));
            
        timeGroup.append('button')
            .attr('class', 'btn secondary')
            .text('All Time')
            .on('click', () => this.setTimeRange(null));
            
        // Export controls
        const exportGroup = controls.append('div')
            .attr('class', 'control-group');
            
        exportGroup.append('button')
            .attr('class', 'btn secondary')
            .html('<span class="btn-icon">📊</span> Export')
            .on('click', () => this.exportProvenance());
            
        exportGroup.append('button')
            .attr('class', 'btn secondary')
            .html('<span class="btn-icon">⏪</span> Rollback')
            .on('click', () => this.showRollbackDialog());
    }

    /**
     * Create sidebar for chain navigation
     */
    createSidebar(parent) {
        const sidebar = parent.append('div')
            .attr('class', 'provenance-sidebar');
            
        sidebar.append('h4').text('Provenance Chains');
        
        // Chain list container
        const chainList = sidebar.append('div')
            .attr('class', 'chain-list')
            .attr('id', 'provenanceChainList');
            
        // Chain filters
        const filtersSection = sidebar.append('div')
            .attr('class', 'chain-filters');
            
        filtersSection.append('h5').text('Filters');
        
        // Source filter
        const sourceFilter = filtersSection.append('div')
            .attr('class', 'filter-group');
            
        sourceFilter.append('label').text('Source:');
        sourceFilter.append('select')
            .attr('id', 'sourceFilter')
            .on('change', () => this.updateFilters());
            
        // Type filter
        const typeFilter = filtersSection.append('div')
            .attr('class', 'filter-group');
            
        typeFilter.append('label').text('Type:');
        typeFilter.append('select')
            .attr('id', 'typeFilter')
            .on('change', () => this.updateFilters());
    }

    /**
     * Create view mode tabs
     */
    createViewTabs(parent) {
        const tabContainer = parent.append('div')
            .attr('class', 'view-tabs');
            
        const tabs = [
            { id: 'timeline', label: 'Timeline', icon: '📅' },
            { id: 'dependency', label: 'Dependencies', icon: '🔗' },
            { id: 'attribution', label: 'Attribution', icon: '📝' },
            { id: 'audit', label: 'Audit Trail', icon: '🔍' }
        ];
        
        tabs.forEach(tab => {
            const tabButton = tabContainer.append('button')
                .attr('class', 'tab-button')
                .attr('data-view', tab.id)
                .html(`<span class="tab-icon">${tab.icon}</span> ${tab.label}`)
                .on('click', () => this.switchViewMode(tab.id));
                
            if (tab.id === this.viewMode) {
                tabButton.classed('active', true);
            }
        });
    }

    /**
     * Create details panel
     */
    createDetailsPanel(parent) {
        const detailsPanel = parent.append('div')
            .attr('class', 'provenance-details-panel')
            .attr('id', 'provenanceDetails');
            
        detailsPanel.append('h4').text('Provenance Details');
        
        const detailsContent = detailsPanel.append('div')
            .attr('class', 'details-content');
            
        // Version info section
        const versionSection = detailsContent.append('div')
            .attr('class', 'version-section')
            .attr('id', 'versionInfo');
            
        // Attribution section
        const attributionSection = detailsContent.append('div')
            .attr('class', 'attribution-section')
            .attr('id', 'attributionInfo');
            
        // Actions section
        const actionsSection = detailsContent.append('div')
            .attr('class', 'actions-section');
            
        actionsSection.append('button')
            .attr('class', 'btn primary')
            .text('View Full History')
            .on('click', () => this.showFullHistory());
            
        actionsSection.append('button')
            .attr('class', 'btn secondary')
            .text('Compare Versions')
            .on('click', () => this.showVersionComparison());
    }

    /**
     * Setup WebSocket connection
     */
    setupWebSocketConnection() {
        if (window.wsManager) {
            this.wsConnection = window.wsManager;
            this.wsConnection.on('provenance-update', (data) => {
                this.handleProvenanceUpdate(data);
            });
            this.wsConnection.on('version-created', (data) => {
                this.handleVersionCreated(data);
            });
        }
    }

    /**
     * Setup event listeners
     */
    setupEventListeners() {
        window.addEventListener('resize', () => {
            this.handleResize();
        });
    }

    /**
     * Load initial provenance data
     */
    async loadInitialData() {
        try {
            // Use the API client with correct backend endpoints
            const data = await window.apiClient.queryProvenance({
                time_range: { hours: 24 }, // Last 24 hours
                depth: 5
            });
            this.updateProvenanceData(data);
        } catch (error) {
            console.warn('Failed to load provenance data:', error);
            this.loadSampleData();
        }
    }

    /**
     * Load sample provenance data
     */
    loadSampleData() {
        const now = Date.now();
        const sampleData = {
            chains: [
                {
                    id: 'chain_1',
                    name: 'Knowledge Base Update',
                    source: 'reasoning_engine',
                    type: 'knowledge_update',
                    created: new Date(now - 3600000), // 1 hour ago
                    versions: ['v1.0', 'v1.1', 'v1.2']
                },
                {
                    id: 'chain_2',
                    name: 'Query Processing',
                    source: 'query_handler',
                    type: 'query_processing',
                    created: new Date(now - 1800000), // 30 minutes ago
                    versions: ['v1.0', 'v1.1']
                },
                {
                    id: 'chain_3',
                    name: 'Learning Adaptation',
                    source: 'learning_system',
                    type: 'learning_update',
                    created: new Date(now - 900000), // 15 minutes ago
                    versions: ['v1.0']
                }
            ],
            versions: [
                {
                    id: 'v1.0',
                    chainId: 'chain_1',
                    timestamp: new Date(now - 3600000),
                    author: 'system',
                    description: 'Initial knowledge base state',
                    changes: ['Added 15 new concepts', 'Updated 3 relationships']
                },
                {
                    id: 'v1.1',
                    chainId: 'chain_1',
                    timestamp: new Date(now - 2700000),
                    author: 'reasoning_engine',
                    description: 'Inference-based updates',
                    changes: ['Inferred 5 new relationships', 'Resolved 2 contradictions']
                }
            ],
            attributions: [
                {
                    id: 'attr_1',
                    versionId: 'v1.1',
                    source: 'reasoning_engine',
                    confidence: 0.85,
                    evidence: ['Logical inference', 'Pattern matching']
                }
            ]
        };
        
        this.updateProvenanceData(sampleData);
    }

    /**
     * Update provenance data
     */
    updateProvenanceData(data) {
        // Process chains
        if (data.chains) {
            data.chains.forEach(chain => {
                this.provenanceData.chains.set(chain.id, chain);
            });
        }
        
        // Process versions
        if (data.versions) {
            data.versions.forEach(version => {
                this.provenanceData.versions.set(version.id, version);
            });
        }
        
        // Process attributions
        if (data.attributions) {
            data.attributions.forEach(attribution => {
                this.provenanceData.attributions.set(attribution.id, attribution);
            });
        }
        
        this.updateChainList();
        this.updateVisualization();
    }

    /**
     * Update chain list in sidebar
     */
    updateChainList() {
        const chainList = d3.select('#provenanceChainList');
        const chains = Array.from(this.provenanceData.chains.values());
        
        const chainItems = chainList.selectAll('.chain-item')
            .data(chains, d => d.id);
            
        chainItems.exit().remove();
        
        const chainEnter = chainItems.enter()
            .append('div')
            .attr('class', 'chain-item')
            .on('click', (event, d) => this.selectChain(d));
            
        chainEnter.append('div')
            .attr('class', 'chain-name');
            
        chainEnter.append('div')
            .attr('class', 'chain-meta');
            
        chainEnter.append('div')
            .attr('class', 'chain-versions');
            
        const chainUpdate = chainEnter.merge(chainItems);
        
        chainUpdate.select('.chain-name')
            .text(d => d.name);
            
        chainUpdate.select('.chain-meta')
            .html(d => `
                <span class="chain-source">${d.source}</span>
                <span class="chain-type">${d.type}</span>
                <span class="chain-time">${d.created.toLocaleTimeString()}</span>
            `);
            
        chainUpdate.select('.chain-versions')
            .text(d => `${d.versions.length} version${d.versions.length !== 1 ? 's' : ''}`);
    }

    /**
     * Switch view mode
     */
    switchViewMode(mode) {
        this.viewMode = mode;
        
        // Update tab appearance
        this.container.selectAll('.tab-button')
            .classed('active', false)
            .filter(`[data-view="${mode}"]`)
            .classed('active', true);
            
        // Clear and redraw visualization
        this.mainGroup.selectAll('*').remove();
        
        switch (mode) {
            case 'timeline':
                this.drawTimelineView();
                break;
            case 'dependency':
                this.drawDependencyView();
                break;
            case 'attribution':
                this.drawAttributionView();
                break;
            case 'audit':
                this.drawAuditView();
                break;
        }
    }

    /**
     * Draw timeline view
     */
    drawTimelineView() {
        if (!this.currentChain) return;
        
        const versions = Array.from(this.provenanceData.versions.values())
            .filter(v => v.chainId === this.currentChain.id)
            .sort((a, b) => a.timestamp - b.timestamp);
            
        if (versions.length === 0) return;
        
        const chartWidth = this.width - this.margin.left - this.margin.right;
        const chartHeight = this.height - this.margin.top - this.margin.bottom;
        
        // Create timeline scale
        const timeExtent = d3.extent(versions, d => d.timestamp);
        const xScale = d3.scaleTime()
            .domain(timeExtent)
            .range([0, chartWidth]);
            
        const yScale = d3.scaleBand()
            .domain(versions.map(d => d.id))
            .range([0, chartHeight])
            .padding(0.1);
            
        // Draw timeline axis
        this.mainGroup.append('g')
            .attr('class', 'timeline-axis')
            .attr('transform', `translate(0, ${chartHeight})`)
            .call(d3.axisBottom(xScale).tickFormat(d3.timeFormat('%H:%M')));
            
        // Draw version nodes
        const versionNodes = this.mainGroup.selectAll('.version-node')
            .data(versions)
            .enter()
            .append('g')
            .attr('class', 'version-node')
            .attr('transform', d => `translate(${xScale(d.timestamp)}, ${yScale(d.id)})`);
            
        versionNodes.append('circle')
            .attr('r', 8)
            .attr('fill', '#2196F3')
            .attr('stroke', '#fff')
            .attr('stroke-width', 2);
            
        versionNodes.append('text')
            .attr('x', 15)
            .attr('y', 5)
            .text(d => d.id)
            .style('font-size', '12px');
            
        // Draw connections between versions
        for (let i = 1; i < versions.length; i++) {
            const prev = versions[i - 1];
            const curr = versions[i];
            
            this.mainGroup.append('line')
                .attr('class', 'version-connection')
                .attr('x1', xScale(prev.timestamp))
                .attr('y1', yScale(prev.id) + yScale.bandwidth() / 2)
                .attr('x2', xScale(curr.timestamp))
                .attr('y2', yScale(curr.id) + yScale.bandwidth() / 2)
                .attr('stroke', '#666')
                .attr('stroke-width', 2);
        }
        
        // Add click handlers
        versionNodes.on('click', (event, d) => this.selectVersion(d));
    }

    /**
     * Draw dependency view
     */
    drawDependencyView() {
        // Create a network visualization of dependencies
        const dependencies = Array.from(this.provenanceData.dependencies.values());
        
        // Placeholder implementation
        this.mainGroup.append('text')
            .attr('x', this.width / 2)
            .attr('y', this.height / 2)
            .attr('text-anchor', 'middle')
            .style('font-size', '16px')
            .text('Dependency visualization will show here');
    }

    /**
     * Draw attribution view
     */
    drawAttributionView() {
        const attributions = Array.from(this.provenanceData.attributions.values());
        
        if (attributions.length === 0) {
            this.mainGroup.append('text')
                .attr('x', this.width / 2)
                .attr('y', this.height / 2)
                .attr('text-anchor', 'middle')
                .style('font-size', '16px')
                .text('No attribution data available');
            return;
        }
        
        // Create attribution visualization
        const chartWidth = this.width - this.margin.left - this.margin.right;
        const chartHeight = this.height - this.margin.top - this.margin.bottom;
        
        const yScale = d3.scaleBand()
            .domain(attributions.map(d => d.id))
            .range([0, chartHeight])
            .padding(0.1);
            
        const confidenceScale = d3.scaleLinear()
            .domain([0, 1])
            .range([0, chartWidth]);
            
        // Draw attribution bars
        const attributionBars = this.mainGroup.selectAll('.attribution-bar')
            .data(attributions)
            .enter()
            .append('g')
            .attr('class', 'attribution-bar')
            .attr('transform', d => `translate(0, ${yScale(d.id)})`);
            
        attributionBars.append('rect')
            .attr('width', d => confidenceScale(d.confidence))
            .attr('height', yScale.bandwidth())
            .attr('fill', '#4CAF50')
            .attr('opacity', 0.7);
            
        attributionBars.append('text')
            .attr('x', 5)
            .attr('y', yScale.bandwidth() / 2)
            .attr('dy', '0.35em')
            .text(d => `${d.source} (${(d.confidence * 100).toFixed(0)}%)`)
            .style('font-size', '12px');
    }

    /**
     * Draw audit view
     */
    drawAuditView() {
        // Show detailed audit trail
        this.mainGroup.append('text')
            .attr('x', this.width / 2)
            .attr('y', this.height / 2)
            .attr('text-anchor', 'middle')
            .style('font-size', '16px')
            .text('Detailed audit trail will show here');
    }

    /**
     * Select a provenance chain
     */
    selectChain(chain) {
        this.currentChain = chain;
        
        // Update visual selection
        this.container.selectAll('.chain-item')
            .classed('selected', false)
            .filter(d => d.id === chain.id)
            .classed('selected', true);
            
        // Update visualization
        this.updateVisualization();
        
        // Update details panel
        this.updateDetailsPanel(chain);
    }

    /**
     * Select a version
     */
    selectVersion(version) {
        this.selectedVersion = version;
        
        // Update visual selection
        this.mainGroup.selectAll('.version-node')
            .classed('selected', false)
            .filter(d => d.id === version.id)
            .classed('selected', true);
            
        // Update details panel
        this.updateVersionDetails(version);
    }

    /**
     * Update visualization
     */
    updateVisualization() {
        this.switchViewMode(this.viewMode);
    }

    /**
     * Update details panel
     */
    updateDetailsPanel(chain) {
        const detailsPanel = d3.select('#provenanceDetails');
        
        detailsPanel.select('h4')
            .text(`Chain: ${chain.name}`);
            
        // Update version info
        const versionInfo = detailsPanel.select('#versionInfo');
        versionInfo.selectAll('*').remove();
        
        versionInfo.append('h5').text('Versions');
        
        const versionList = versionInfo.append('div')
            .attr('class', 'version-list');
            
        const versions = Array.from(this.provenanceData.versions.values())
            .filter(v => v.chainId === chain.id);
            
        versions.forEach(version => {
            const versionItem = versionList.append('div')
                .attr('class', 'version-item');
                
            versionItem.append('strong').text(version.id);
            versionItem.append('span').text(` - ${version.description}`);
            versionItem.append('div')
                .attr('class', 'version-meta')
                .text(`${version.author} at ${version.timestamp.toLocaleString()}`);
        });
    }

    /**
     * Update version details
     */
    updateVersionDetails(version) {
        const attributionInfo = d3.select('#attributionInfo');
        attributionInfo.selectAll('*').remove();
        
        attributionInfo.append('h5').text('Attribution');
        
        const attribution = Array.from(this.provenanceData.attributions.values())
            .find(a => a.versionId === version.id);
            
        if (attribution) {
            const attrDetails = attributionInfo.append('div')
                .attr('class', 'attribution-details');
                
            attrDetails.append('div')
                .html(`<strong>Source:</strong> ${attribution.source}`);
                
            attrDetails.append('div')
                .html(`<strong>Confidence:</strong> ${(attribution.confidence * 100).toFixed(1)}%`);
                
            attrDetails.append('div')
                .html(`<strong>Evidence:</strong> ${attribution.evidence.join(', ')}`);
        } else {
            attributionInfo.append('div').text('No attribution data available');
        }
    }

    /**
     * Event handlers
     */
    handleSearch() {
        const searchTerm = document.getElementById('provenanceSearch').value.toLowerCase();
        
        this.container.selectAll('.chain-item')
            .style('display', function(d) {
                return d.name.toLowerCase().includes(searchTerm) ||
                       d.source.toLowerCase().includes(searchTerm) ? 'block' : 'none';
            });
    }

    executeSearch() {
        this.handleSearch();
    }

    setTimeRange(hours) {
        if (hours === null) {
            this.timeRange = { start: null, end: null };
        } else {
            const now = new Date();
            this.timeRange = {
                start: new Date(now.getTime() - hours * 60 * 60 * 1000),
                end: now
            };
        }
        this.updateVisualization();
    }

    updateFilters() {
        // Apply source and type filters
        const sourceFilter = document.getElementById('sourceFilter').value;
        const typeFilter = document.getElementById('typeFilter').value;
        
        this.container.selectAll('.chain-item')
            .style('display', function(d) {
                const sourceMatch = !sourceFilter || d.source === sourceFilter;
                const typeMatch = !typeFilter || d.type === typeFilter;
                return sourceMatch && typeMatch ? 'block' : 'none';
            });
    }

    showRollbackDialog() {
        if (!this.selectedVersion) {
            alert('Please select a version to rollback to');
            return;
        }
        
        const confirmed = confirm(`Are you sure you want to rollback to version ${this.selectedVersion.id}?`);
        if (confirmed && this.wsConnection) {
            this.wsConnection.send('rollback-version', {
                versionId: this.selectedVersion.id,
                chainId: this.currentChain.id
            });
        }
    }

    showFullHistory() {
        if (!this.currentChain) return;
        
        // Open modal with full history
        console.log('Show full history for chain:', this.currentChain.id);
    }

    showVersionComparison() {
        if (!this.selectedVersion) {
            alert('Please select a version to compare');
            return;
        }
        
        // Open comparison view
        console.log('Compare version:', this.selectedVersion.id);
    }

    exportProvenance() {
        const exportData = {
            chains: Array.from(this.provenanceData.chains.values()),
            versions: Array.from(this.provenanceData.versions.values()),
            attributions: Array.from(this.provenanceData.attributions.values()),
            timestamp: new Date().toISOString()
        };
        
        const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `provenance-export-${Date.now()}.json`;
        a.click();
        URL.revokeObjectURL(url);
    }

    handleProvenanceUpdate(data) {
        this.updateProvenanceData(data);
    }

    handleVersionCreated(data) {
        this.provenanceData.versions.set(data.id, data);
        this.updateChainList();
        this.updateVisualization();
    }

    handleResize() {
        try {
            const rect = this.container.node().getBoundingClientRect();
            this.width = rect.width;
            this.height = Math.max(400, rect.height - 200);
            
            if (this.svg) {
                this.svg.attr('viewBox', `0 0 ${this.width} ${this.height}`);
                this.updateVisualization();
            }
        } catch (error) {
            console.error('Resize handler failed:', error);
        }
    }

    /**
     * Refresh the provenance data
     */
    async refresh(chainId = null) {
        try {
            if (chainId) {
                this.currentChain = chainId;
            }
            await this.loadInitialData();
            this.updateVisualization();
        } catch (error) {
            console.warn('Failed to refresh provenance data:', error);
            this.loadOfflineData(chainId || 'default');
        }
    }

    /**
     * Load offline/static data when live data is unavailable
     */
    loadOfflineData(chainId = 'default') {
        console.log(`Loading offline provenance data for chain: ${chainId}`);
        this.currentChain = chainId;
        
        // Create sample provenance data
        const sampleData = {
            chains: new Map([[chainId, {
                id: chainId,
                name: `Chain ${chainId}`,
                created: new Date(),
                versions: ['v1.0', 'v1.1', 'v1.2']
            }]]),
            versions: new Map([
                ['v1.0', { id: 'v1.0', timestamp: new Date(Date.now() - 3600000), changes: ['Initial creation'] }],
                ['v1.1', { id: 'v1.1', timestamp: new Date(Date.now() - 1800000), changes: ['Added reasoning step'] }],
                ['v1.2', { id: 'v1.2', timestamp: new Date(), changes: ['Updated confidence scores'] }]
            ]),
            attributions: new Map(),
            dependencies: new Map()
        };
        
        this.provenanceData = sampleData;
        this.updateVisualization();
    }

    /**
     * Check if the explorer has valid data
     */
    hasValidData() {
        return this.provenanceData.chains.size > 0 || this.provenanceData.versions.size > 0;
    }
}

// Initialize global instance
window.provenanceExplorer = new ProvenanceExplorer('provenanceExploration');

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ProvenanceExplorer;
}