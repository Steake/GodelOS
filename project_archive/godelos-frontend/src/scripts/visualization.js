/**
 * Visualization Manager for GödelOS Frontend
 * Handles D3.js-based knowledge graph and network visualizations
 */

class VisualizationManager {
    constructor() {
        this.currentVisualization = 'graph';
        this.svg = null;
        this.simulation = null;
        this.nodes = [];
        this.links = [];
        this.width = 0;
        this.height = 0;
        
        this.initializeVisualization();
        this.setupEventListeners();
    }

    /**
     * Initialize the main visualization container
     */
    initializeVisualization() {
        const container = document.getElementById('knowledgeVisualization');
        if (!container) return;

        const rect = container.getBoundingClientRect();
        this.width = rect.width;
        this.height = Math.max(rect.height, 400);

        // Create SVG element
        this.svg = d3.select('#knowledgeGraph')
            .attr('width', this.width)
            .attr('height', this.height);

        // Add arrow marker for directed edges
        this.svg.append('defs').append('marker')
            .attr('id', 'arrowhead')
            .attr('viewBox', '0 -5 10 10')
            .attr('refX', 15)
            .attr('refY', 0)
            .attr('markerWidth', 6)
            .attr('markerHeight', 6)
            .attr('orient', 'auto')
            .append('path')
            .attr('d', 'M0,-5L10,0L0,5')
            .attr('fill', '#4facfe');

        // Initialize with sample data
        this.loadSampleData();
    }

    /**
     * Setup event listeners for visualization controls
     */
    setupEventListeners() {
        // Visualization type selector
        const typeSelector = document.getElementById('visualizationType');
        if (typeSelector) {
            typeSelector.addEventListener('change', (e) => {
                this.switchVisualization(e.target.value);
            });
        }

        // Listen for knowledge updates from WebSocket
        window.addEventListener('knowledgeUpdate', (e) => {
            this.updateVisualization(e.detail);
        });

        // Window resize handler
        window.addEventListener('resize', () => {
            this.handleResize();
        });
    }

    /**
     * Load sample data for demonstration
     */
    loadSampleData() {
        const sampleData = {
            nodes: [
                { id: 'ai', label: 'Artificial Intelligence', type: 'concept', group: 1 },
                { id: 'ml', label: 'Machine Learning', type: 'concept', group: 1 },
                { id: 'dl', label: 'Deep Learning', type: 'concept', group: 1 },
                { id: 'nn', label: 'Neural Networks', type: 'concept', group: 2 },
                { id: 'nlp', label: 'Natural Language Processing', type: 'concept', group: 2 },
                { id: 'cv', label: 'Computer Vision', type: 'concept', group: 2 },
                { id: 'gpt', label: 'GPT Model', type: 'instance', group: 3 },
                { id: 'bert', label: 'BERT Model', type: 'instance', group: 3 },
                { id: 'cnn', label: 'CNN', type: 'instance', group: 3 },
                { id: 'rnn', label: 'RNN', type: 'instance', group: 3 },
                { id: 'logic', label: 'Logical Reasoning', type: 'concept', group: 4 },
                { id: 'knowledge', label: 'Knowledge Representation', type: 'concept', group: 4 }
            ],
            links: [
                { source: 'ml', target: 'ai', type: 'is-a' },
                { source: 'dl', target: 'ml', type: 'is-a' },
                { source: 'nn', target: 'dl', type: 'implements' },
                { source: 'nlp', target: 'ai', type: 'domain-of' },
                { source: 'cv', target: 'ai', type: 'domain-of' },
                { source: 'gpt', target: 'nlp', type: 'instance-of' },
                { source: 'bert', target: 'nlp', type: 'instance-of' },
                { source: 'cnn', target: 'cv', type: 'instance-of' },
                { source: 'rnn', target: 'nlp', type: 'instance-of' },
                { source: 'logic', target: 'ai', type: 'component-of' },
                { source: 'knowledge', target: 'ai', type: 'component-of' }
            ]
        };

        this.updateVisualization(sampleData);
    }

    /**
     * Switch between different visualization types
     * @param {string} type - Visualization type ('graph', 'hierarchy', 'network')
     */
    switchVisualization(type) {
        this.currentVisualization = type;
        
        // Clear existing visualization
        this.svg.selectAll('*').remove();
        
        // Re-add arrow marker
        this.svg.append('defs').append('marker')
            .attr('id', 'arrowhead')
            .attr('viewBox', '0 -5 10 10')
            .attr('refX', 15)
            .attr('refY', 0)
            .attr('markerWidth', 6)
            .attr('markerHeight', 6)
            .attr('orient', 'auto')
            .append('path')
            .attr('d', 'M0,-5L10,0L0,5')
            .attr('fill', '#4facfe');

        // Render appropriate visualization
        switch (type) {
            case 'graph':
                this.renderKnowledgeGraph();
                break;
            case 'hierarchy':
                this.renderConceptHierarchy();
                break;
            case 'network':
                this.renderSemanticNetwork();
                break;
        }
    }

    /**
     * Update visualization with new data
     * @param {Object} data - New visualization data
     */
    updateVisualization(data) {
        if (data.nodes) {
            this.nodes = data.nodes;
        }
        if (data.links) {
            this.links = data.links;
        }

        // Re-render current visualization
        this.switchVisualization(this.currentVisualization);
    }

    /**
     * Render knowledge graph visualization
     */
    renderKnowledgeGraph() {
        const svg = this.svg;
        const width = this.width;
        const height = this.height;

        // Create force simulation
        this.simulation = d3.forceSimulation(this.nodes)
            .force('link', d3.forceLink(this.links).id(d => d.id).distance(100))
            .force('charge', d3.forceManyBody().strength(-300))
            .force('center', d3.forceCenter(width / 2, height / 2))
            .force('collision', d3.forceCollide().radius(30));

        // Create links
        const link = svg.append('g')
            .attr('class', 'links')
            .selectAll('line')
            .data(this.links)
            .enter().append('line')
            .attr('class', 'link')
            .attr('stroke', '#4facfe')
            .attr('stroke-opacity', 0.6)
            .attr('stroke-width', 2)
            .attr('marker-end', 'url(#arrowhead)');

        // Create link labels
        const linkLabel = svg.append('g')
            .attr('class', 'link-labels')
            .selectAll('text')
            .data(this.links)
            .enter().append('text')
            .attr('class', 'link-label')
            .attr('font-size', '10px')
            .attr('fill', '#e0e6ed')
            .attr('text-anchor', 'middle')
            .text(d => d.type || d.label || '');

        // Create nodes
        const node = svg.append('g')
            .attr('class', 'nodes')
            .selectAll('g')
            .data(this.nodes)
            .enter().append('g')
            .attr('class', 'node')
            .call(d3.drag()
                .on('start', (event, d) => this.dragstarted(event, d))
                .on('drag', (event, d) => this.dragged(event, d))
                .on('end', (event, d) => this.dragended(event, d)));

        // Add circles to nodes
        node.append('circle')
            .attr('r', d => this.getNodeRadius(d))
            .attr('fill', d => this.getNodeColor(d))
            .attr('stroke', '#fff')
            .attr('stroke-width', 2);

        // Add labels to nodes
        node.append('text')
            .attr('dy', 4)
            .attr('text-anchor', 'middle')
            .attr('font-size', '12px')
            .attr('fill', '#e0e6ed')
            .attr('pointer-events', 'none')
            .text(d => d.label);

        // Add hover effects
        node.on('mouseover', (event, d) => this.showNodeInfo(event, d))
            .on('mouseout', () => this.hideNodeInfo())
            .on('click', (event, d) => this.selectNode(d));

        // Update positions on simulation tick
        this.simulation.on('tick', () => {
            link
                .attr('x1', d => d.source.x)
                .attr('y1', d => d.source.y)
                .attr('x2', d => d.target.x)
                .attr('y2', d => d.target.y);

            linkLabel
                .attr('x', d => (d.source.x + d.target.x) / 2)
                .attr('y', d => (d.source.y + d.target.y) / 2);

            node
                .attr('transform', d => `translate(${d.x},${d.y})`);
        });
    }

    /**
     * Render concept hierarchy visualization
     */
    renderConceptHierarchy() {
        // Create hierarchical layout
        const hierarchy = d3.hierarchy(this.convertToHierarchy(this.nodes, this.links));
        const treeLayout = d3.tree().size([this.width - 100, this.height - 100]);
        
        treeLayout(hierarchy);

        const svg = this.svg;

        // Create links
        svg.append('g')
            .attr('class', 'hierarchy-links')
            .selectAll('path')
            .data(hierarchy.links())
            .enter().append('path')
            .attr('class', 'hierarchy-link')
            .attr('fill', 'none')
            .attr('stroke', '#4facfe')
            .attr('stroke-opacity', 0.6)
            .attr('stroke-width', 1.5)
            .attr('d', d3.linkVertical()
                .x(d => d.x + 50)
                .y(d => d.y + 50));

        // Create nodes
        const nodes = svg.append('g')
            .attr('class', 'hierarchy-nodes')
            .selectAll('g')
            .data(hierarchy.descendants())
            .enter().append('g')
            .attr('class', 'hierarchy-node')
            .attr('transform', d => `translate(${d.x + 50},${d.y + 50})`);

        nodes.append('rect')
            .attr('width', 80)
            .attr('height', 30)
            .attr('x', -40)
            .attr('y', -15)
            .attr('fill', 'rgba(79, 172, 254, 0.2)')
            .attr('stroke', '#4facfe')
            .attr('rx', 4);

        nodes.append('text')
            .attr('text-anchor', 'middle')
            .attr('dy', 4)
            .attr('font-size', '11px')
            .attr('fill', '#e0e6ed')
            .text(d => d.data.label);
    }

    /**
     * Render semantic network visualization
     */
    renderSemanticNetwork() {
        // Similar to knowledge graph but with different styling for semantic types
        this.renderKnowledgeGraph();
        
        // Update node styling for semantic types
        this.svg.selectAll('.node circle')
            .attr('fill', d => {
                switch (d.type) {
                    case 'concept': return '#4facfe';
                    case 'relation': return '#ff6b6b';
                    case 'instance': return '#2ed573';
                    default: return '#4facfe';
                }
            });
    }

    /**
     * Get node radius based on type and importance
     * @param {Object} node - Node data
     * @returns {number} Radius value
     */
    getNodeRadius(node) {
        switch (node.type) {
            case 'concept': return 20;
            case 'instance': return 15;
            case 'relation': return 10;
            default: return 18;
        }
    }

    /**
     * Get node color based on type
     * @param {Object} node - Node data
     * @returns {string} Color value
     */
    getNodeColor(node) {
        const colors = {
            concept: '#4facfe',
            instance: '#2ed573',
            relation: '#ff6b6b',
            default: '#4facfe'
        };
        return colors[node.type] || colors.default;
    }

    /**
     * Convert flat node/link structure to hierarchy
     * @param {Array} nodes - Node array
     * @param {Array} links - Link array
     * @returns {Object} Hierarchical data structure
     */
    convertToHierarchy(nodes, links) {
        // Simple hierarchy conversion - in a real app this would be more sophisticated
        const root = { id: 'root', label: 'Knowledge Base', children: [] };
        const nodeMap = new Map();
        
        nodes.forEach(node => {
            nodeMap.set(node.id, { ...node, children: [] });
        });

        // Build hierarchy based on 'is-a' relationships
        links.forEach(link => {
            if (link.type === 'is-a') {
                const child = nodeMap.get(link.source);
                const parent = nodeMap.get(link.target);
                if (child && parent) {
                    parent.children.push(child);
                }
            }
        });

        // Add orphan nodes to root
        nodeMap.forEach(node => {
            if (!this.hasParent(node.id, links)) {
                root.children.push(node);
            }
        });

        return root;
    }

    /**
     * Check if node has a parent in the hierarchy
     * @param {string} nodeId - Node ID
     * @param {Array} links - Link array
     * @returns {boolean} True if node has parent
     */
    hasParent(nodeId, links) {
        return links.some(link => link.source === nodeId && link.type === 'is-a');
    }

    /**
     * Show node information tooltip
     * @param {Event} event - Mouse event
     * @param {Object} node - Node data
     */
    showNodeInfo(event, node) {
        const nodeInfo = document.getElementById('nodeInfo');
        const nodeTitle = document.getElementById('nodeTitle');
        const nodeDescription = document.getElementById('nodeDescription');
        const nodeProperties = document.getElementById('nodeProperties');

        if (nodeInfo && nodeTitle && nodeDescription && nodeProperties) {
            nodeTitle.textContent = node.label;
            nodeDescription.textContent = `Type: ${node.type}`;
            nodeProperties.innerHTML = `
                <div><strong>ID:</strong> ${node.id}</div>
                <div><strong>Group:</strong> ${node.group || 'N/A'}</div>
                <div><strong>Connections:</strong> ${this.getNodeConnections(node.id)}</div>
            `;

            nodeInfo.style.display = 'block';
            nodeInfo.style.left = (event.pageX + 10) + 'px';
            nodeInfo.style.top = (event.pageY + 10) + 'px';
        }
    }

    /**
     * Hide node information tooltip
     */
    hideNodeInfo() {
        const nodeInfo = document.getElementById('nodeInfo');
        if (nodeInfo) {
            nodeInfo.style.display = 'none';
        }
    }

    /**
     * Select a node and highlight its connections
     * @param {Object} node - Selected node
     */
    selectNode(node) {
        // Remove previous selections
        this.svg.selectAll('.node').classed('selected', false);
        this.svg.selectAll('.link').classed('highlighted', false);

        // Highlight selected node
        this.svg.selectAll('.node')
            .filter(d => d.id === node.id)
            .classed('selected', true);

        // Highlight connected links
        this.svg.selectAll('.link')
            .filter(d => d.source.id === node.id || d.target.id === node.id)
            .classed('highlighted', true);

        console.log('Selected node:', node);
    }

    /**
     * Get number of connections for a node
     * @param {string} nodeId - Node ID
     * @returns {number} Number of connections
     */
    getNodeConnections(nodeId) {
        return this.links.filter(link => 
            link.source.id === nodeId || link.target.id === nodeId
        ).length;
    }

    /**
     * Handle window resize
     */
    handleResize() {
        const container = document.getElementById('knowledgeVisualization');
        if (!container) return;

        const rect = container.getBoundingClientRect();
        this.width = rect.width;
        this.height = Math.max(rect.height, 400);

        this.svg
            .attr('width', this.width)
            .attr('height', this.height);

        if (this.simulation) {
            this.simulation
                .force('center', d3.forceCenter(this.width / 2, this.height / 2))
                .alpha(0.3)
                .restart();
        }
    }

    /**
     * Drag event handlers for nodes
     */
    dragstarted(event, d) {
        if (!event.active && this.simulation) {
            this.simulation.alphaTarget(0.3).restart();
        }
        d.fx = d.x;
        d.fy = d.y;
    }

    dragged(event, d) {
        d.fx = event.x;
        d.fy = event.y;
    }

    dragended(event, d) {
        if (!event.active && this.simulation) {
            this.simulation.alphaTarget(0);
        }
        d.fx = null;
        d.fy = null;
    }

    /**
     * Add new node to visualization
     * @param {Object} node - New node data
     */
    addNode(node) {
        this.nodes.push(node);
        this.updateVisualization({ nodes: this.nodes, links: this.links });
    }

    /**
     * Add new link to visualization
     * @param {Object} link - New link data
     */
    addLink(link) {
        this.links.push(link);
        this.updateVisualization({ nodes: this.nodes, links: this.links });
    }

    /**
     * Remove node from visualization
     * @param {string} nodeId - Node ID to remove
     */
    removeNode(nodeId) {
        this.nodes = this.nodes.filter(node => node.id !== nodeId);
        this.links = this.links.filter(link => 
            link.source.id !== nodeId && link.target.id !== nodeId
        );
        this.updateVisualization({ nodes: this.nodes, links: this.links });
    }
}

// Create global visualization manager instance
window.vizManager = new VisualizationManager();