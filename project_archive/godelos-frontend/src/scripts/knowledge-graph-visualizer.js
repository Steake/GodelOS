/**
 * Dynamic Knowledge Graph Visualizer for GödelOS
 * Provides interactive D3.js-based knowledge graph visualization with real-time updates
 */

class KnowledgeGraphVisualizer {
    constructor(containerId = 'knowledgeGraphVisualization') {
        this.containerId = containerId;
        this.container = null;
        this.svg = null;
        this.width = 800;
        this.height = 600;
        this.margin = { top: 20, right: 20, bottom: 20, left: 20 };
        
        // Graph data
        this.nodes = new Map();
        this.links = new Map();
        this.nodeArray = [];
        this.linkArray = [];
        
        // Visualization state
        this.selectedNode = null;
        this.highlightedNodes = new Set();
        this.filteredTypes = new Set();
        this.zoomLevel = 1;
        this.currentLayout = 'force';
        
        // D3 elements
        this.simulation = null;
        this.zoom = null;
        this.transform = d3.zoomIdentity;
        
        // Provenance tracking
        this.provenanceHistory = [];
        this.currentVersion = 0;
        
        // WebSocket connection
        this.wsConnection = null;
        
        // Single unified initialization
        console.log('🔍 KG: Initializing Knowledge Graph Visualizer');
        this.initialize();
    }
    // Single unified initialization method
    initialize() {
        console.log('🔍 KG: Starting unified initialization');
        
        // Wait for DOM to be ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.initializeComponents());
        } else {
            this.initializeComponents();
        }
    }

    initializeComponents() {
        try {
            console.log('🔍 KG: Initializing components');
            
            // 1. Create/find container
            this.createContainer();
            
            // 2. Setup SVG and visualization elements
            this.setupSVG();
            
            // 3. Setup controls and event listeners
            this.setupControls();
            this.setupEventListeners();
            this.setupWebSocketConnection();
            
            // 4. Load data (sample or real)
            this.loadInitialData();
            
            console.log('✅ KG: Initialization complete');
            
        } catch (error) {
            console.error('❌ KG: Initialization failed:', error);
            this.showErrorVisualization();
        }
    }

    /**
     * Show error visualization when initialization fails
     */
    showErrorVisualization() {
        console.log('🔍 KG: Showing error visualization');
        
        if (!this.container) {
            // Try to create a basic container if none exists
            this.container = d3.select('body')
                .append('div')
                .attr('id', this.containerId)
                .attr('class', 'knowledge-graph-visualizer error')
                .style('width', '100%')
                .style('height', '400px')
                .style('border', '1px solid #dc3545')
                .style('margin', '10px')
                .style('position', 'relative')
                .style('background', '#f8f9fa')
                .style('overflow', 'hidden');
        }
        
        // Clear any existing content
        this.container.html('');
        
        // Add error message
        this.container.append('div')
            .attr('class', 'error-message')
            .style('position', 'absolute')
            .style('top', '50%')
            .style('left', '50%')
            .style('transform', 'translate(-50%, -50%)')
            .style('text-align', 'center')
            .style('font-family', 'sans-serif')
            .style('color', '#dc3545')
            .style('padding', '20px')
            .style('border', '2px solid #dc3545')
            .style('border-radius', '8px')
            .style('background', '#fff')
            .html(`
                <div style="font-size: 24px; margin-bottom: 10px;">⚠️</div>
                <div style="font-size: 16px; font-weight: bold; margin-bottom: 8px;">Knowledge Graph Initialization Failed</div>
                <div style="font-size: 14px; color: #666;">Check the console for detailed error information.</div>
                <button onclick="window.knowledgeGraphVisualizer.initialize()" 
                        style="margin-top: 15px; padding: 8px 16px; background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer;">
                    Retry Initialization
                </button>
            `);
    }

    createContainer() {
        console.log(`🔍 KG: Looking for container #${this.containerId}`);
        
        // Try to find the container
        this.container = d3.select(`#${this.containerId}`);
        
        // If container not found, try alternative containers
        if (this.container.empty()) {
            console.warn(`⚠️ KG: Container #${this.containerId} not found, trying alternatives...`);
            
            // Try common container IDs
            const alternatives = [
                'knowledgeGraphVisualization',
                'knowledgeGraphVisualization2', 
                'knowledgeGraph',
                'knowledgeVisualization'
            ];
            
            for (const altId of alternatives) {
                this.container = d3.select(`#${altId}`);
                if (!this.container.empty()) {
                    console.log(`✅ KG: Found alternative container #${altId}`);
                    this.containerId = altId;
                    break;
                }
            }
            
            // If still not found, create it in the body
            if (this.container.empty()) {
                console.warn(`⚠️ KG: No suitable container found, creating one in body`);
                this.container = d3.select('body')
                    .append('div')
                    .attr('id', this.containerId)
                    .attr('class', 'knowledge-graph-visualizer')
                    .style('width', '100%')
                    .style('height', '600px')
                    .style('border', '1px solid #ccc')
                    .style('margin', '10px')
                    .style('position', 'relative')
                    .style('background', '#f8f9fa')
                    .style('overflow', 'hidden');
            }
        }
        
        // Ensure existing container has proper styling
        this.container
            .style('width', '100%')
            .style('min-height', '400px')
            .style('position', 'relative')
            .style('background', '#f8f9fa')
            .style('overflow', 'hidden');
        
        // Clear existing content
        this.container.html('');
        
        // Add a status message
        const status = this.container.append('div')
            .attr('class', 'status-message')
            .style('position', 'absolute')
            .style('top', '50%')
            .style('left', '50%')
            .style('transform', 'translate(-50%, -50%)')
            .style('font-family', 'sans-serif')
            .style('color', '#666')
            .style('z-index', '10')
            .text('Initializing knowledge graph...');
            
        console.log(`✅ KG: Container ready:`, this.container.node());
        
        // Force layout reflow
        if (this.container.node()) {
            this.container.node().offsetHeight;
        }
    }

    setupSVG() {
        console.log('🔍 KG: Setting up SVG...');
        // Remove previous visualizations but preserve status messages
        this.container.selectAll('.kg-toolbar, svg').remove();
        
        // Get actual container dimensions
        const containerRect = this.container.node().getBoundingClientRect();
        this.width = containerRect.width > 0 ? containerRect.width : 800;
        this.height = containerRect.height > 0 ? containerRect.height : 400;
        
        console.log(`🔍 KG: Container dimensions: ${this.width}x${this.height}`);
        console.log(`🔍 KG: Container rect:`, containerRect);
        
        // Force minimum dimensions if container is hidden
        if (containerRect.width === 0 || containerRect.height === 0) {
            console.warn('🔍 KG: Container has zero dimensions, using defaults');
            this.width = 800;
            this.height = 400;
        }
        
        const toolbar = this.container.append('div')
            .attr('class', 'kg-toolbar');
            
        this.svg = this.container.append('svg')
            .attr('width', '100%')
            .attr('height', this.height)
            .attr('viewBox', `0 0 ${this.width} ${this.height}`)
            .attr('preserveAspectRatio', 'xMidYMid meet')
            .style('background', '#f8f9fa')
            .style('display', 'block')
            .style('margin', '0 auto');
            
        console.log('✅ KG: SVG created:', this.svg.node());
            
        this.zoom = d3.zoom()
            .scaleExtent([0.1, 10])
            .on('zoom', (event) => {
                this.transform = event.transform;
                this.zoomLevel = event.transform.k;
                this.mainGroup.attr('transform', event.transform);
            });
            
        this.svg.call(this.zoom);
        this.mainGroup = this.svg.append('g').attr('class', 'main-group');
        
        const defs = this.svg.append('defs');
        const markerTypes = [
            { id: 'arrow-default', color: '#666' },
            { id: 'arrow-causal', color: '#e74c3c' },
            { id: 'arrow-temporal', color: '#3498db' },
            { id: 'arrow-hierarchical', color: '#2ecc71' },
            { id: 'arrow-similarity', color: '#f39c12' }
        ];
        
        markerTypes.forEach(marker => {
            defs.append('marker')
                .attr('id', marker.id)
                .attr('viewBox', '0 -5 10 10')
                .attr('refX', 15)
                .attr('refY', 0)
                .attr('markerWidth', 6)
                .attr('markerHeight', 6)
                .attr('orient', 'auto')
                .append('path')
                .attr('d', 'M0,-5L10,0L0,5')
                .attr('fill', marker.color);
        });
        
        this.linksGroup = this.mainGroup.append('g').attr('class', 'links');
        this.nodesGroup = this.mainGroup.append('g').attr('class', 'nodes');
        this.labelsGroup = this.mainGroup.append('g').attr('class', 'labels');
    }

    setupControls() {
        const toolbar = this.container.select('.kg-toolbar');
        
        const layoutGroup = toolbar.append('div').attr('class', 'control-group');
        layoutGroup.append('label').text('Layout:');
        const layoutSelect = layoutGroup.append('select')
            .attr('id', 'layoutSelect')
            .on('change', () => this.changeLayout());
            
        layoutSelect.selectAll('option')
            .data([
                { value: 'force', text: 'Force-Directed' },
                { value: 'hierarchical', text: 'Hierarchical' },
                { value: 'circular', text: 'Circular' }
            ])
            .enter()
            .append('option')
            .attr('value', d => d.value)
            .text(d => d.text);
            
        const viewGroup = toolbar.append('div').attr('class', 'control-group');
        viewGroup.append('button')
            .attr('class', 'btn secondary')
            .text('Zoom In')
            .on('click', () => this.zoomIn());
            
        viewGroup.append('button')
            .attr('class', 'btn secondary')
            .text('Zoom Out')
            .on('click', () => this.zoomOut());
            
        viewGroup.append('button')
            .attr('class', 'btn secondary')
            .text('Reset')
            .on('click', () => this.resetView());
    }

    setupWebSocketConnection() {
        if (window.wsManager) {
            this.wsConnection = window.wsManager;
            
            // Listen for knowledge graph updates from transparency WebSocket
            this.wsConnection.on('knowledge-graph-update', (data) => {
                this.handleGraphUpdate(data);
            });
            
            // Listen for reasoning chain updates to highlight paths
            this.wsConnection.on('reasoning-update', (data) => {
                if (data.knowledge_path) {
                    this.highlightReasoningPath(data.knowledge_path);
                }
            });
            
            // Listen for transparency level changes
            this.wsConnection.on('transparency-level-change', (data) => {
                this.updateTransparencyLevel(data.level);
            });
        }
    }

    setupEventListeners() {
        window.addEventListener('resize', () => this.handleResize());
        
        // Listen for real-time knowledge updates from WebSocket
        window.addEventListener('knowledgeUpdate', (event) => {
            console.log('Knowledge Graph: Received knowledge update', event.detail);
            this.handleKnowledgeUpdate(event.detail);
        });
        
        // Listen for knowledge graph bulk updates from WebSocket
        window.addEventListener('knowledgeGraphUpdate', (event) => {
            console.log('Knowledge Graph: Received knowledge graph update', event.detail);
            this.handleGraphUpdate(event.detail);
        });
    }
    
    /**
     * Handle real-time knowledge updates from WebSocket
     * @param {Object} data - Knowledge update data
     */
    handleKnowledgeUpdate(data) {
        console.log('Knowledge Graph: Processing knowledge update', data);
        
        if (data.event === 'item_added' && data.data) {
            const { item_id, title, source, categories } = data.data;
            
            // Add new node to the graph
            this.addNode({
                id: item_id,
                label: title,
                type: source || 'knowledge',
                categories: categories || [],
                size: 10,
                color: this.getNodeColor(source || 'knowledge')
            });
            
            // Refresh the visualization
            this.refresh();
            
            console.log(`Knowledge Graph: Added new node ${item_id} (${title})`);
        }
    }

    /**
     * Add a node to the graph data
     * @param {Object} nodeData - The node data to add
     */
    addNode(nodeData) {
        if (!nodeData || !nodeData.id) {
            console.error('Knowledge Graph: Invalid node data provided to addNode', nodeData);
            return;
        }

        if (this.nodes.has(nodeData.id)) {
            console.warn(`Knowledge Graph: Node ${nodeData.id} already exists. Updating.`);
            // Optionally, update existing node properties here
            const existingNode = this.nodes.get(nodeData.id);
            Object.assign(existingNode, nodeData);
        } else {
            const newNode = {
                ...nodeData,
                x: Math.random() * (this.width - 100) + 50, // Initial position
                y: Math.random() * (this.height - 100) + 50,
            };
            this.nodes.set(nodeData.id, newNode);
        }
        this.updateNodeArray(); // Rebuild the nodeArray
        console.log(`Knowledge Graph: Node ${nodeData.id} added/updated. Total nodes: ${this.nodes.size}`);
    }

    /**
     * Update the nodeArray from the nodes Map.
     * This is necessary for D3 force simulation.
     */
    updateNodeArray() {
        this.nodeArray = Array.from(this.nodes.values());
    }

    async loadInitialData() {
        console.log('🔍 KG DEBUG: loadInitialData called');
        try {
            console.log('Knowledge Graph: Fetching initial data...');
            
            // Use the API client with correct backend endpoints
            const data = await window.apiClient.getKnowledgeGraph({
                format: 'visualization',
                include_statistics: true,
                node_limit: 100
            });

            // Validate response data structure
            if (!data) {
                throw new Error('No data received from API');
            }

            // Extract graph data, checking both possible locations
            const graphData = data.graph_data || data;
            
            if (!graphData || typeof graphData !== 'object') {
                throw new Error('Invalid graph data structure');
            }

            // Validate nodes and edges existence
            if (!Array.isArray(graphData.nodes)) {
                throw new Error('Graph data missing nodes array');
            }

            if (!Array.isArray(graphData.edges) && !Array.isArray(graphData.links)) {
                throw new Error('Graph data missing edges/links array');
            }

            // Convert data to visualization format
            const visualizationData = {
                nodes: graphData.nodes,
                links: (graphData.edges || graphData.links).map(edge => ({
                    source: edge.source_node_id || edge.source,
                    target: edge.target_node_id || edge.target,
                    type: edge.type || 'default',
                    strength: edge.strength || 0.5,
                    ...edge
                }))
            };

            console.log(`Knowledge Graph: Processing ${visualizationData.nodes.length} nodes and ${visualizationData.links.length} links`);
            
            // Update the graph with validated data
            this.updateGraph(visualizationData);

        } catch (error) {
            console.warn('Failed to load knowledge graph data:', error);
            console.log('Knowledge Graph: Falling back to sample data');
            this.loadSampleData();
        }
    }

    loadSampleData() {
        console.log('🔍 KG DEBUG: Loading sample data...');
        
        // Always create a fresh SVG - this helps ensure we have a clean slate
        if (this.svg) {
            this.svg.remove();
        }
        this.setupSVG();
        
        const sampleData = {
            nodes: [
                { id: 'concept1', type: 'concept', label: 'Concept 1', confidence: 0.95 },
                { id: 'concept2', type: 'concept', label: 'Concept 2', confidence: 0.90 },
                { id: 'concept3', type: 'concept', label: 'Concept 3', confidence: 0.85 },
                { id: 'concept4', type: 'concept', label: 'Concept 4', confidence: 0.88 }
            ],
            links: [
                { source: 'concept1', target: 'concept2', type: 'hierarchical', strength: 0.8 },
                { source: 'concept2', target: 'concept3', type: 'causal', strength: 0.7 },
                { source: 'concept2', target: 'concept4', type: 'causal', strength: 0.75 }
            ]
        };
        
        // Clear any existing data
        this.nodes.clear();
        this.links.clear();
        this.nodeArray = [];
        this.linkArray = [];
        
        console.log('🔍 KG DEBUG: Sample data:', sampleData);
        
        // Update with sample data
        this.updateGraph(sampleData);
        
        // Center and scale the view
        const transform = d3.zoomIdentity.translate(this.width/2, this.height/2).scale(0.8);
        this.svg.call(this.zoom.transform, transform);
        
        console.log('✅ KG DEBUG: Sample data loaded and graph updated');
    }

    /**
     * Create a simple test visualization for debugging
     */
    createSimpleTestVisualization() {
        console.log('🔍 KG DEBUG: Creating simple test visualization...');
        
        if (!this.container) {
            console.error('❌ KG DEBUG: No container for simple test');
            return;
        }
        
        // Remove any existing content except status messages
        this.container.selectAll('svg, .kg-toolbar').remove();
        
        // Create a simple SVG with test circles
        const svg = this.container.append('svg')
            .attr('width', '100%')
            .attr('height', '400px')
            .style('background', '#f8f9fa')
            .style('border', '1px solid #dee2e6');
        
        // Add title
        svg.append('text')
            .attr('x', 400)
            .attr('y', 30)
            .attr('text-anchor', 'middle')
            .style('font-size', '18px')
            .style('font-weight', 'bold')
            .text('Knowledge Graph Visualization (Test Mode)');
        
        // Add test nodes
        const testNodes = [
            { id: 'consciousness', x: 200, y: 150, label: 'Consciousness' },
            { id: 'cognition', x: 400, y: 150, label: 'Cognition' },
            { id: 'attention', x: 300, y: 250, label: 'Attention' },
            { id: 'memory', x: 500, y: 250, label: 'Memory' }
        ];
        
        // Draw connections
        svg.selectAll('line')
            .data([
                { x1: 200, y1: 150, x2: 400, y2: 150 },
                { x1: 400, y1: 150, x2: 300, y2: 250 },
                { x1: 400, y1: 150, x2: 500, y2: 250 }
            ])
            .enter()
            .append('line')
            .attr('x1', d => d.x1)
            .attr('y1', d => d.y1)
            .attr('x2', d => d.x2)
            .attr('y2', d => d.y2)
            .attr('stroke', '#6c757d')
            .attr('stroke-width', 2);
        
        // Draw nodes
        const nodeGroups = svg.selectAll('.node')
            .data(testNodes)
            .enter()
            .append('g')
            .attr('class', 'node')
            .attr('transform', d => `translate(${d.x}, ${d.y})`);
        
        nodeGroups.append('circle')
            .attr('r', 20)
            .attr('fill', '#2196F3')
            .attr('stroke', '#fff')
            .attr('stroke-width', 2);
        
        nodeGroups.append('text')
            .attr('text-anchor', 'middle')
            .attr('dy', 35)
            .style('font-size', '12px')
            .text(d => d.label);
        
        console.log('✅ KG DEBUG: Simple test visualization created');
        this.notifyVisualizationReady();
    }

    /**
     * Refresh the visualization
     */
    refresh() {
        console.log('🔧 KG DEBUG: refresh() called');
        if (this.svg) {
            console.log('🔧 KG DEBUG: SVG exists, calling refreshVisualization()');
            this.refreshVisualization();
        } else {
            console.log('🔧 KG DEBUG: No SVG found, initializing DOM parts');
            this.initializeDOMDependentParts();
        }
        console.log('🔧 KG DEBUG: refresh() completed synchronously');
        return Promise.resolve(); // Return resolved promise for compatibility with await
    }

    /**
     * Get current graph data
     * @returns {Object} Current graph data with nodes and links
     */
    getData() {
        return {
            nodes: this.nodeArray,
            links: this.linkArray
        };
    }

    /**
     * Check if the visualizer has valid data
     * @returns {boolean} True if there's valid graph data
     */
    hasData() {
        return this.nodeArray && this.nodeArray.length > 0;
    }

    updateGraph(data) {
        // Clear existing data if nodes array is present
        if (data.nodes && Array.isArray(data.nodes)) {
            this.nodes.clear();
            this.links.clear();
            console.log('Knowledge Graph: Cleared existing data');
        }

        // Add/update nodes first
        if (data.nodes) {
            data.nodes.forEach(nodeData => this.addOrUpdateNode(nodeData));
            console.log(`Knowledge Graph: Processed ${data.nodes.length} nodes`);
        }

        // Then process links to ensure all nodes exist
        if (data.links) {
            data.links.forEach(linkData => this.addOrUpdateLink(linkData));
            console.log(`Knowledge Graph: Processed ${data.links.length} links`);
        }

        this.refreshVisualization();
    }

    addOrUpdateNode(nodeData) {
        // Map API field names to visualization field names
        const nodeId = nodeData.node_id || nodeData.id;
        if (!nodeId) {
            console.error('Knowledge Graph: Node missing ID:', nodeData);
            return;
        }

        const existingNode = this.nodes.get(nodeId);
        
        const node = {
            id: nodeId,
            type: nodeData.node_type || nodeData.type || 'concept',
            label: nodeData.concept || nodeData.label || nodeId,
            confidence: nodeData.confidence || 0.5,
            size: this.calculateNodeSize(nodeData),
            color: this.getNodeColor(nodeData.node_type || nodeData.type),
            properties: nodeData.properties || {},
            x: existingNode ? existingNode.x : (Math.random() * (this.width - 100)) + 50,
            y: existingNode ? existingNode.y : (Math.random() * (this.height - 100)) + 50
        };
        
        this.nodes.set(nodeId, node);
        this.updateNodeArray();
        console.log(`Knowledge Graph: Added/updated node ${nodeId}`);
    }

    addOrUpdateLink(linkData) {
        // Map API field names to visualization field names
        const sourceId = linkData.source_node_id || linkData.source;
        const targetId = linkData.target_node_id || linkData.target;
        
        if (!sourceId || !targetId) {
            console.error('Knowledge Graph: Link missing source or target:', linkData);
            return;
        }
        
        // Validate that both source and target nodes exist
        const sourceNode = this.nodes.get(sourceId);
        const targetNode = this.nodes.get(targetId);
        
        if (!sourceNode || !targetNode) {
            console.warn(`Knowledge Graph: Cannot create link - missing ${!sourceNode ? 'source' : 'target'} node`, {
                sourceId,
                targetId,
                linkData
            });
            return;
        }
        
        const linkId = linkData.edge_id || `${sourceId}-${targetId}`;
        
        const link = {
            id: linkId,
            source: sourceNode,
            target: targetNode,
            type: linkData.relation_type || linkData.type || 'default',
            strength: linkData.weight || linkData.strength || 0.5,
            properties: linkData.properties || {}
        };
        
        this.links.set(linkId, link);
        this.updateLinkArray();
        console.log(`Knowledge Graph: Added/updated link ${linkId}`);
    }

    updateNodeArray() {
        this.nodeArray = Array.from(this.nodes.values());
    }

    updateLinkArray() {
        this.linkArray = Array.from(this.links.values());
    }

    refreshVisualization() {
        this.updateNodeArray();
        this.updateLinkArray();
        this.updateNodes();
        this.updateLinks();
        this.updateSimulation();
        
        // Signal that visualization is ready
        this.notifyVisualizationReady();
    }

    /**
     * Notify that the visualization has been rendered and is ready
     */
    notifyVisualizationReady() {
        // Dispatch a custom event to signal completion
        const event = new CustomEvent('knowledgeGraphReady', {
            detail: { 
                visualizer: this, 
                nodeCount: this.nodeArray.length,
                linkCount: this.linkArray.length 
            }
        });
        document.dispatchEvent(event);
        
        // Hide any status messages in the container
        if (this.container) {
            const statusMessage = this.container.select('.status-message');
            if (!statusMessage.empty()) {
                statusMessage.style('display', 'none');
            }
        }
    }

    updateNodes() {
        const nodeSelection = this.nodesGroup.selectAll('.kg-node')
            .data(this.nodeArray, d => d.id);
            
        nodeSelection.exit().remove();
        
        const nodeEnter = nodeSelection.enter()
            .append('g')
            .attr('class', 'kg-node')
            .call(d3.drag()
                .on('start', (event, d) => this.dragStarted(event, d))
                .on('drag', (event, d) => this.dragged(event, d))
                .on('end', (event, d) => this.dragEnded(event, d)));
                
        nodeEnter.append('circle')
            .attr('class', 'node-circle')
            .attr('r', d => d.size || 15)
            .attr('fill', d => d.color || '#2196F3')
            .attr('stroke', '#fff')
            .attr('stroke-width', 2)
            .style('cursor', 'pointer')
            .style('opacity', 0.9);
            
        nodeEnter.append('text')
            .attr('class', 'node-label')
            .attr('text-anchor', 'middle')
            .attr('dy', d => d.size + 15)
            .text(d => d.label)
            .style('font-size', '12px');
            
        const nodeUpdate = nodeEnter.merge(nodeSelection);
        
        nodeUpdate
            .on('click', (event, d) => this.selectNode(d))
            .on('mouseover', (event, d) => this.highlightNode(d))
            .on('mouseout', (event, d) => this.unhighlightNode(d));
    }

    updateLinks() {
        const linkSelection = this.linksGroup.selectAll('.kg-link')
            .data(this.linkArray, d => d.id);
            
        linkSelection.exit().remove();
        
        const linkEnter = linkSelection.enter()
            .append('line')
            .attr('class', 'kg-link')
            .attr('stroke', d => this.getLinkColor(d.type))
            .attr('stroke-width', 2)
            .attr('marker-end', d => `url(#arrow-${d.type})`)
            .style('opacity', 0.6);
    }

    updateSimulation() {
        console.log('🔍 KG DEBUG: Updating simulation');
        
        if (this.simulation) {
            this.simulation.stop();
        }

        // Position nodes in a circle if they don't have positions
        const radius = Math.min(this.width, this.height) / 4;
        const centerX = this.width / 2;
        const centerY = this.height / 2;
        
        this.nodeArray.forEach((node, i) => {
            if (isNaN(node.x) || isNaN(node.y)) {
                const angle = (i / this.nodeArray.length) * 2 * Math.PI;
                node.x = centerX + radius * Math.cos(angle);
                node.y = centerY + radius * Math.sin(angle);
            }
        });

        // Filter out invalid nodes and links
        const validNodes = this.nodeArray.filter(node =>
            node && node.id && typeof node.x === 'number' && typeof node.y === 'number'
        );

        const validLinks = this.linkArray.filter(link =>
            link && link.id && link.source && link.target &&
            validNodes.some(n => n.id === (typeof link.source === 'object' ? link.source.id : link.source)) &&
            validNodes.some(n => n.id === (typeof link.target === 'object' ? link.target.id : link.target))
        );

        if (validNodes.length === 0) {
            console.warn('⚠️ KG DEBUG: No valid nodes to simulate');
            return;
        }

        console.log(`🔍 KG DEBUG: Starting simulation with ${validNodes.length} nodes and ${validLinks.length} links`);
        
        try {
            // Initialize simulation with custom forces
            this.simulation = d3.forceSimulation(validNodes)
                .force('link', d3.forceLink(validLinks)
                    .id(d => d.id)
                    .distance(d => 100 + (d.strength || 0.5) * 50))
                .force('charge', d3.forceManyBody()
                    .strength(d => -200 - (d.size || 10) * 10)
                    .distanceMax(300)
                    .theta(0.8))
                .force('collide', d3.forceCollide()
                    .radius(d => (d.size || 10) * 1.5)
                    .strength(0.8)
                    .iterations(2))
                .force('center', d3.forceCenter(this.width / 2, this.height / 2))
                .force('x', d3.forceX(this.width / 2).strength(0.05))
                .force('y', d3.forceY(this.height / 2).strength(0.05))
                .velocityDecay(0.3)
                .alpha(1)
                .alphaDecay(0.01)
                .alphaMin(0.001)
                .alphaTarget(0);
            
            // Add tick handler for updating positions
            this.simulation.on('tick', () => {
                // Update link positions with safety checks
                this.linksGroup.selectAll('.kg-link')
                    .attr('x1', d => {
                        const source = d.source || {};
                        return typeof source.x === 'number' ? source.x : this.width / 2;
                    })
                    .attr('y1', d => {
                        const source = d.source || {};
                        return typeof source.y === 'number' ? source.y : this.height / 2;
                    })
                    .attr('x2', d => {
                        const target = d.target || {};
                        return typeof target.x === 'number' ? target.x : this.width / 2;
                    })
                    .attr('y2', d => {
                        const target = d.target || {};
                        return typeof target.y === 'number' ? target.y : this.height / 2;
                    });
                
                // Update node positions with safety checks and boundary constraints
                this.nodesGroup.selectAll('.kg-node')
                    .attr('transform', d => {
                        if (!d) return `translate(${this.width / 2},${this.height / 2})`;
                        
                        // Keep nodes within bounds with padding
                        const padding = (d.size || 10) + 10;
                        const x = Math.max(padding, Math.min(this.width - padding, d.x));
                        const y = Math.max(padding, Math.min(this.height - padding, d.y));
                        
                        // Update the node's position for the next tick
                        d.x = x;
                        d.y = y;
                        
                        return `translate(${x},${y})`;
                    });
            });

            // Add simulation event handlers
            this.simulation
                .on('end', () => {
                    console.log('✅ KG DEBUG: Simulation stabilized');
                    this.container.select('.status-message').style('display', 'none');
                });

        } catch (error) {
            console.error('❌ KG DEBUG: Error in force simulation:', error);
            this.simulation = null;
            
            // Show error in container
            this.container.select('.status-message')
                .style('display', 'block')
                .style('color', '#dc3545')
                .text('Error in visualization. Check console for details.');
        }
    }

    calculateNodeSize(nodeData) {
        return 10 + (nodeData.confidence || 0.5) * 10;
    }

    getNodeColor(type) {
        const colors = {
            concept: '#2196F3',
            entity: '#4CAF50',
            relation: '#FF9800'
        };
        return colors[type] || '#9E9E9E';
    }

    getLinkColor(type) {
        const colors = {
            hierarchical: '#2ecc71',
            causal: '#e74c3c',
            temporal: '#3498db',
            default: '#666'
        };
        return colors[type] || colors.default;
    }

    selectNode(node) {
        this.selectedNode = node;
        this.nodesGroup.selectAll('.kg-node').classed('selected', false);
        this.nodesGroup.selectAll('.kg-node')
            .filter(d => d.id === node.id)
            .classed('selected', true);
    }

    highlightNode(node) {
        this.highlightedNodes.add(node.id);
    }

    unhighlightNode(node) {
        this.highlightedNodes.delete(node.id);
    }

    changeLayout() {
        const layout = document.getElementById('layoutSelect').value;
        this.currentLayout = layout;
        
        switch (layout) {
            case 'hierarchical':
                this.applyHierarchicalLayout();
                break;
            case 'circular':
                this.applyCircularLayout();
                break;
            default:
                this.applyForceLayout();
        }
    }

    applyForceLayout() {
        this.nodeArray.forEach(node => {
            node.fx = null;
            node.fy = null;
        });
        
        if (this.simulation) {
            this.simulation.alpha(1).restart();
        }
    }

    applyHierarchicalLayout() {
        this.nodeArray.forEach((node, index) => {
            node.fx = (index + 1) * (this.width / (this.nodeArray.length + 1));
            node.fy = this.height / 2;
        });
        
        if (this.simulation) {
            this.simulation.alpha(1).restart();
        }
    }

    applyCircularLayout() {
        const radius = Math.min(this.width, this.height) / 3;
        const centerX = this.width / 2;
        const centerY = this.height / 2;
        
        this.nodeArray.forEach((node, index) => {
            const angle = (index / this.nodeArray.length) * 2 * Math.PI;
            node.fx = centerX + radius * Math.cos(angle);
            node.fy = centerY + radius * Math.sin(angle);
        });
        
        if (this.simulation) {
            this.simulation.alpha(1).restart();
        }
    }

    handleGraphUpdate(data) {
        try {
            console.log('🔍 KG DEBUG: handleGraphUpdate called with data:', data);
            
            // Clear status message if present
            if (this.container) {
                const statusMessage = this.container.select('.status-message');
                if (!statusMessage.empty()) {
                    statusMessage.style('display', 'none');
                }
            }
            
            // Handle nested data structure from WebSocket
            const graphData = data.data || data;
            
            if (!graphData || typeof graphData !== 'object') {
                throw new Error('Invalid graph data received');
            }
            
            console.log('🔍 KG DEBUG: Graph data structure:', graphData);
            
            // Create nodes count indicator if it doesn't exist
            if (this.container && this.container.select('.nodes-count').empty()) {
                this.container.append('div')
                    .attr('class', 'nodes-count')
                    .style('position', 'absolute')
                    .style('top', '10px')
                    .style('right', '10px')
                    .style('font-family', 'sans-serif')
                    .style('padding', '5px')
                    .style('background', 'rgba(255,255,255,0.8)')
                    .style('border', '1px solid #ccc')
                    .style('border-radius', '3px')
                    .style('color', '#666');
            }
            
            let nodesProcessed = 0;
            let linksProcessed = 0;
            
            // Process nodes first
            if (graphData.nodes && Array.isArray(graphData.nodes)) {
                console.log(`🔍 KG DEBUG: Processing ${graphData.nodes.length} nodes`);
                graphData.nodes.forEach(node => {
                    try {
                        console.log('🔍 KG DEBUG: Processing node:', node);
                        this.addOrUpdateNode(node);
                        nodesProcessed++;
                    } catch (nodeError) {
                        console.error('Error processing node:', node, nodeError);
                    }
                });
            }
            
            // Then process links
            if (graphData.links && Array.isArray(graphData.links)) {
                console.log(`🔍 KG DEBUG: Processing ${graphData.links.length} links`);
                graphData.links.forEach(link => {
                    try {
                        console.log('🔍 KG DEBUG: Processing link:', link);
                        this.addOrUpdateLink(link);
                        linksProcessed++;
                    } catch (linkError) {
                        console.error('Error processing link:', link, linkError);
                    }
                });
            }
            
            // Update stats display
            if (this.container) {
                this.container.select('.nodes-count')
                    .text(`Nodes: ${this.nodes.size} (${nodesProcessed} updated) | Links: ${this.links.size} (${linksProcessed} updated)`);
            }
            
            if (nodesProcessed > 0 || linksProcessed > 0) {
                console.log('🔍 KG DEBUG: Refreshing visualization after graph update');
                this.refreshVisualization();
            } else {
                console.warn('⚠️ KG DEBUG: No valid nodes or links processed');
                if (this.container) {
                    this.container.select('.status-message')
                        .style('display', 'block')
                        .style('color', '#856404')
                        .style('background-color', '#fff3cd')
                        .style('padding', '10px')
                        .style('border-radius', '4px')
                        .text('No valid data to visualize. Waiting for updates...');
                }
            }
            
        } catch (error) {
            console.error('❌ KG DEBUG: Error in handleGraphUpdate:', error);
            if (this.container) {
                this.container.select('.status-message')
                    .style('display', 'block')
                    .style('color', '#dc3545')
                    .text('Error updating visualization. Check console for details.');
            }
        }
    }

    handleResize() {
        const rect = this.container.node().getBoundingClientRect();
        this.width = rect.width;
        this.height = Math.max(400, rect.height - 100);
        
        this.svg.attr('viewBox', `0 0 ${this.width} ${this.height}`);
        
        if (this.simulation) {
            this.simulation.force('center', d3.forceCenter(this.width / 2, this.height / 2));
            this.simulation.alpha(0.3).restart();
        }
    }

    zoomIn() {
        this.svg.transition()
            .duration(300)
            .call(this.zoom.scaleBy, 1.5);
    }

    zoomOut() {
        this.svg.transition()
            .duration(300)
            .call(this.zoom.scaleBy, 0.67);
    }

    resetView() {
        this.svg.transition()
            .duration(750)
            .call(this.zoom.transform, d3.zoomIdentity);
    }

    dragStarted(event, d) {
        if (!event.active) this.simulation.alphaTarget(0.3).restart();
        d.fx = d.x;
        d.fy = d.y;
    }

    dragged(event, d) {
        d.fx = event.x;
        d.fy = event.y;
    }

    dragEnded(event, d) {
        if (!event.active) this.simulation.alphaTarget(0);
        d.fx = null;
        d.fy = null;
    }

    /**
     * Highlight reasoning path in the knowledge graph
     * @param {Array} knowledgePath - Array of node IDs in the reasoning path
     */
    highlightReasoningPath(knowledgePath) {
        if (!knowledgePath || knowledgePath.length === 0) return;
        
        // Clear previous highlights
        this.nodesGroup.selectAll('.kg-node').classed('reasoning-path', false);
        this.linksGroup.selectAll('.kg-link').classed('reasoning-path', false);
        
        // Highlight nodes in the reasoning path
        this.nodesGroup.selectAll('.kg-node')
            .filter(d => knowledgePath.includes(d.id))
            .classed('reasoning-path', true);
            
        // Highlight links between consecutive nodes in the path
        for (let i = 0; i < knowledgePath.length - 1; i++) {
            const sourceId = knowledgePath[i];
            const targetId = knowledgePath[i + 1];
            
            this.linksGroup.selectAll('.kg-link')
                .filter(d =>
                    (d.source.id === sourceId && d.target.id === targetId) ||
                    (d.source.id === targetId && d.target.id === sourceId)
                )
                .classed('reasoning-path', true);
        }
    }

    /**
     * Update transparency level for the visualization
     * @param {string} level - Transparency level (minimal, standard, detailed, maximum)
     */
    updateTransparencyLevel(level) {
        const transparencyConfig = {
            minimal: { showLabels: false, showConfidence: false, maxNodes: 20 },
            standard: { showLabels: true, showConfidence: true, maxNodes: 50 },
            detailed: { showLabels: true, showConfidence: true, maxNodes: 100 },
            maximum: { showLabels: true, showConfidence: true, maxNodes: -1 }
        };
        
        const config = transparencyConfig[level] || transparencyConfig.standard;
        
        // Update label visibility
        this.labelsGroup.selectAll('.node-label')
            .style('display', config.showLabels ? 'block' : 'none');
            
        // Update confidence indicators
        this.nodesGroup.selectAll('.confidence-indicator')
            .style('display', config.showConfidence ? 'block' : 'none');
            
        // Filter nodes if there's a limit
        if (config.maxNodes > 0 && this.nodeArray.length > config.maxNodes) {
            // Sort by importance/confidence and keep top nodes
            const sortedNodes = [...this.nodeArray]
                .sort((a, b) => (b.confidence || 0) - (a.confidence || 0))
                .slice(0, config.maxNodes);
                
            this.nodeArray = sortedNodes;
            this.refreshVisualization();
        }
    }
}

// Make class available globally
window.KnowledgeGraphVisualizer = KnowledgeGraphVisualizer;

// Initialize global instance
window.knowledgeGraphVisualizer = new KnowledgeGraphVisualizer('knowledgeGraphVisualization');

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = KnowledgeGraphVisualizer;
}