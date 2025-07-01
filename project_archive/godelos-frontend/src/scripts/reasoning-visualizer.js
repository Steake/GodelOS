/**
 * Reasoning Chain Visualizer for GödelOS
 * Provides interactive visualization of reasoning steps, decision pathways, and uncertainty
 */

class ReasoningVisualizer {
    constructor(containerId = 'reasoningVisualization') {
        this.containerId = containerId;
        this.container = null;
        this.svg = null;
        this.width = 800;
        this.height = 600;
        this.margin = { top: 20, right: 20, bottom: 20, left: 20 };
        
        // Reasoning chain data
        this.reasoningChain = [];
        this.currentStep = -1;
        this.expandedBranches = new Set();
        
        // D3 elements
        this.simulation = null;
        this.nodes = [];
        this.links = [];
        
        // WebSocket connection for real-time updates
        this.wsConnection = null;
        
        this.initialize();
    }

    /**
     * Initialize the reasoning visualizer
     */
    initialize() {
        this.createContainer();
        this.setupSVG();
        this.setupControls();
        this.setupWebSocketConnection();
        this.setupEventListeners();
        
        console.log('Reasoning Visualizer initialized');
    }

    /**
     * Refresh the visualization
     */
    refresh() {
        if (this.svg) {
            this.updateVisualization();
        }
    }

    /**
     * Update the visualization with current data
     */
    updateVisualization() {
        // Redraw the current reasoning chain
        this.renderReasoningChain();
    }

    /**
     * Create the visualization container
     */
    createContainer() {
        this.container = d3.select(`#${this.containerId}`);
        if (this.container.empty()) {
            console.error(`Container #${this.containerId} not found`);
            return;
        }
        
        this.container.classed('reasoning-visualizer', true);
    }

    /**
     * Setup SVG canvas
     */
    setupSVG() {
        // Clear existing content
        this.container.selectAll('*').remove();
        
        // Create control panel
        const controlPanel = this.container.append('div')
            .attr('class', 'reasoning-controls');
            
        // Create SVG
        this.svg = this.container.append('svg')
            .attr('width', '100%')
            .attr('height', this.height)
            .attr('viewBox', `0 0 ${this.width} ${this.height}`)
            .attr('preserveAspectRatio', 'xMidYMid meet');
            
        // Create groups for different elements
        this.svg.append('defs').append('marker')
            .attr('id', 'arrowhead')
            .attr('viewBox', '0 -5 10 10')
            .attr('refX', 8)
            .attr('refY', 0)
            .attr('markerWidth', 6)
            .attr('markerHeight', 6)
            .attr('orient', 'auto')
            .append('path')
            .attr('d', 'M0,-5L10,0L0,5')
            .attr('class', 'arrowhead');
            
        this.linksGroup = this.svg.append('g').attr('class', 'links');
        this.nodesGroup = this.svg.append('g').attr('class', 'nodes');
        this.labelsGroup = this.svg.append('g').attr('class', 'labels');
    }

    /**
     * Setup control panel
     */
    setupControls() {
        const controls = this.container.select('.reasoning-controls');
        
        // Timeline controls
        const timelineControls = controls.append('div')
            .attr('class', 'timeline-controls');
            
        timelineControls.append('button')
            .attr('class', 'btn secondary')
            .attr('id', 'playPauseBtn')
            .html('<span class="btn-icon">▶️</span> Play')
            .on('click', () => this.togglePlayback());
            
        timelineControls.append('button')
            .attr('class', 'btn secondary')
            .attr('id', 'resetBtn')
            .html('<span class="btn-icon">⏮️</span> Reset')
            .on('click', () => this.resetVisualization());
            
        // Step controls
        const stepControls = controls.append('div')
            .attr('class', 'step-controls');
            
        stepControls.append('button')
            .attr('class', 'btn secondary')
            .attr('id', 'prevStepBtn')
            .html('<span class="btn-icon">⬅️</span> Previous')
            .on('click', () => this.previousStep());
            
        stepControls.append('span')
            .attr('class', 'step-indicator')
            .attr('id', 'stepIndicator')
            .text('Step 0 of 0');
            
        stepControls.append('button')
            .attr('class', 'btn secondary')
            .attr('id', 'nextStepBtn')
            .html('<span class="btn-icon">➡️</span> Next')
            .on('click', () => this.nextStep());
            
        // View controls
        const viewControls = controls.append('div')
            .attr('class', 'view-controls');
            
        viewControls.append('label')
            .text('Detail Level:');
            
        const detailSelect = viewControls.append('select')
            .attr('id', 'detailLevel')
            .on('change', () => this.updateDetailLevel());
            
        detailSelect.selectAll('option')
            .data([
                { value: 'minimal', text: 'Minimal' },
                { value: 'standard', text: 'Standard' },
                { value: 'detailed', text: 'Detailed' },
                { value: 'maximum', text: 'Maximum' }
            ])
            .enter()
            .append('option')
            .attr('value', d => d.value)
            .text(d => d.text);
            
        detailSelect.property('value', 'standard');
        
        // Uncertainty toggle
        viewControls.append('label')
            .attr('class', 'checkbox-label')
            .html(`
                <input type="checkbox" id="showUncertainty" checked>
                <span>Show Uncertainty</span>
            `)
            .select('input')
            .on('change', () => this.toggleUncertaintyDisplay());
    }

    /**
     * Setup WebSocket connection for real-time updates
     */
    setupWebSocketConnection() {
        if (window.wsManager) {
            this.wsConnection = window.wsManager;
            this.wsConnection.on('reasoning-step', (data) => {
                this.addReasoningStep(data);
            });
            this.wsConnection.on('reasoning-complete', (data) => {
                this.completeReasoning(data);
            });
        }
    }

    /**
     * Setup event listeners
     */
    setupEventListeners() {
        // Window resize
        window.addEventListener('resize', () => {
            this.handleResize();
        });
        
        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.target.closest('.reasoning-visualizer')) {
                this.handleKeyboard(e);
            }
        });
    }

    /**
     * Add a new reasoning step
     * @param {Object} stepData - Step data from backend
     */
    addReasoningStep(stepData) {
        const step = {
            id: stepData.id || `step_${this.reasoningChain.length}`,
            type: stepData.type || 'inference',
            description: stepData.description || '',
            confidence: stepData.confidence || 0.5,
            uncertainty: stepData.uncertainty || {},
            premises: stepData.premises || [],
            conclusions: stepData.conclusions || [],
            alternatives: stepData.alternatives || [],
            timestamp: stepData.timestamp || Date.now(),
            duration: stepData.duration || 0,
            metadata: stepData.metadata || {}
        };
        
        this.reasoningChain.push(step);
        this.updateVisualization();
        this.updateStepIndicator();
        
        // Auto-advance if playing
        if (this.isPlaying) {
            this.currentStep = this.reasoningChain.length - 1;
        }
    }

    /**
     * Update the visualization
     */
    updateVisualization() {
        this.prepareData();
        this.updateNodes();
        this.updateLinks();
        this.updateSimulation();
    }

    /**
     * Prepare data for visualization
     */
    prepareData() {
        this.nodes = [];
        this.links = [];
        
        const detailLevel = document.getElementById('detailLevel')?.value || 'standard';
        const showUncertainty = document.getElementById('showUncertainty')?.checked !== false;
        
        // Create nodes for each reasoning step
        this.reasoningChain.forEach((step, index) => {
            if (index <= this.currentStep || this.currentStep === -1) {
                const node = {
                    id: step.id,
                    index: index,
                    type: step.type,
                    description: step.description,
                    confidence: step.confidence,
                    uncertainty: step.uncertainty,
                    active: index === this.currentStep,
                    completed: index < this.currentStep,
                    x: 100 + (index % 5) * 150,
                    y: 100 + Math.floor(index / 5) * 120,
                    fx: null,
                    fy: null
                };
                
                this.nodes.push(node);
                
                // Add alternative branches if expanded
                if (this.expandedBranches.has(step.id) && step.alternatives.length > 0) {
                    step.alternatives.forEach((alt, altIndex) => {
                        const altNode = {
                            id: `${step.id}_alt_${altIndex}`,
                            index: -1,
                            type: 'alternative',
                            description: alt.description,
                            confidence: alt.confidence,
                            uncertainty: alt.uncertainty || {},
                            active: false,
                            completed: false,
                            parent: step.id,
                            x: node.x + 100 + altIndex * 80,
                            y: node.y + 60,
                            fx: null,
                            fy: null
                        };
                        this.nodes.push(altNode);
                    });
                }
            }
        });
        
        // Create links between consecutive steps
        for (let i = 0; i < this.nodes.length - 1; i++) {
            const source = this.nodes[i];
            const target = this.nodes[i + 1];
            
            if (source.type !== 'alternative' && target.type !== 'alternative') {
                this.links.push({
                    source: source.id,
                    target: target.id,
                    type: 'reasoning'
                });
            }
        }
        
        // Create links to alternatives
        this.nodes.forEach(node => {
            if (node.parent) {
                this.links.push({
                    source: node.parent,
                    target: node.id,
                    type: 'alternative'
                });
            }
        });
    }

    /**
     * Update node visualization
     */
    updateNodes() {
        const nodeSelection = this.nodesGroup.selectAll('.reasoning-node')
            .data(this.nodes, d => d.id);
            
        // Remove old nodes
        nodeSelection.exit().remove();
        
        // Add new nodes
        const nodeEnter = nodeSelection.enter()
            .append('g')
            .attr('class', 'reasoning-node')
            .call(d3.drag()
                .on('start', (event, d) => this.dragStarted(event, d))
                .on('drag', (event, d) => this.dragged(event, d))
                .on('end', (event, d) => this.dragEnded(event, d)));
                
        // Add circles
        nodeEnter.append('circle')
            .attr('r', 20)
            .attr('class', d => `node-circle ${d.type}`)
            .style('fill', d => this.getNodeColor(d))
            .style('stroke', d => this.getNodeStroke(d))
            .style('stroke-width', d => d.active ? 3 : 1);
            
        // Add confidence indicators
        nodeEnter.append('circle')
            .attr('r', d => 15 * d.confidence)
            .attr('class', 'confidence-indicator')
            .style('fill', 'none')
            .style('stroke', '#4CAF50')
            .style('stroke-width', 2)
            .style('opacity', 0.7);
            
        // Add uncertainty visualization
        nodeEnter.append('circle')
            .attr('r', d => 10 + (d.uncertainty.epistemic || 0) * 10)
            .attr('class', 'uncertainty-indicator')
            .style('fill', 'none')
            .style('stroke', '#FF9800')
            .style('stroke-width', 1)
            .style('stroke-dasharray', '2,2')
            .style('opacity', d => document.getElementById('showUncertainty')?.checked ? 0.5 : 0);
            
        // Add labels
        nodeEnter.append('text')
            .attr('class', 'node-label')
            .attr('text-anchor', 'middle')
            .attr('dy', 35)
            .text(d => `Step ${d.index + 1}`)
            .style('font-size', '12px')
            .style('fill', '#333');
            
        // Add expand/collapse buttons for nodes with alternatives
        nodeEnter.filter(d => this.hasAlternatives(d))
            .append('circle')
            .attr('r', 8)
            .attr('cx', 15)
            .attr('cy', -15)
            .attr('class', 'expand-button')
            .style('fill', '#2196F3')
            .style('cursor', 'pointer')
            .on('click', (event, d) => this.toggleBranch(d));
            
        nodeEnter.filter(d => this.hasAlternatives(d))
            .append('text')
            .attr('x', 15)
            .attr('y', -10)
            .attr('text-anchor', 'middle')
            .attr('class', 'expand-icon')
            .text(d => this.expandedBranches.has(d.id) ? '−' : '+')
            .style('font-size', '12px')
            .style('fill', 'white')
            .style('cursor', 'pointer')
            .on('click', (event, d) => this.toggleBranch(d));
            
        // Update existing nodes
        const nodeUpdate = nodeEnter.merge(nodeSelection);
        
        nodeUpdate.select('.node-circle')
            .style('fill', d => this.getNodeColor(d))
            .style('stroke', d => this.getNodeStroke(d))
            .style('stroke-width', d => d.active ? 3 : 1);
            
        nodeUpdate.select('.confidence-indicator')
            .attr('r', d => 15 * d.confidence);
            
        nodeUpdate.select('.uncertainty-indicator')
            .attr('r', d => 10 + (d.uncertainty.epistemic || 0) * 10)
            .style('opacity', d => document.getElementById('showUncertainty')?.checked ? 0.5 : 0);
            
        nodeUpdate.select('.expand-icon')
            .text(d => this.expandedBranches.has(d.id) ? '−' : '+');
            
        // Add click handlers for node details
        nodeUpdate.on('click', (event, d) => {
            if (!event.defaultPrevented) {
                this.showNodeDetails(d);
            }
        });
        
        // Add hover effects
        nodeUpdate.on('mouseover', (event, d) => {
            this.showTooltip(event, d);
        }).on('mouseout', () => {
            this.hideTooltip();
        });
    }

    /**
     * Update link visualization
     */
    updateLinks() {
        const linkSelection = this.linksGroup.selectAll('.reasoning-link')
            .data(this.links, d => `${d.source}-${d.target}`);
            
        // Remove old links
        linkSelection.exit().remove();
        
        // Add new links
        const linkEnter = linkSelection.enter()
            .append('line')
            .attr('class', d => `reasoning-link ${d.type}`)
            .attr('marker-end', 'url(#arrowhead)')
            .style('stroke', d => d.type === 'alternative' ? '#FF9800' : '#666')
            .style('stroke-width', d => d.type === 'alternative' ? 1 : 2)
            .style('stroke-dasharray', d => d.type === 'alternative' ? '5,5' : 'none');
            
        // Update all links
        linkEnter.merge(linkSelection);
    }

    /**
     * Update force simulation
     */
    updateSimulation() {
        if (this.simulation) {
            this.simulation.stop();
        }
        
        this.simulation = d3.forceSimulation(this.nodes)
            .force('link', d3.forceLink(this.links).id(d => d.id).distance(100))
            .force('charge', d3.forceManyBody().strength(-300))
            .force('center', d3.forceCenter(this.width / 2, this.height / 2))
            .force('collision', d3.forceCollide().radius(30));
            
        this.simulation.on('tick', () => {
            this.linksGroup.selectAll('.reasoning-link')
                .attr('x1', d => d.source.x)
                .attr('y1', d => d.source.y)
                .attr('x2', d => d.target.x)
                .attr('y2', d => d.target.y);
                
            this.nodesGroup.selectAll('.reasoning-node')
                .attr('transform', d => `translate(${d.x},${d.y})`);
        });
    }

    /**
     * Get node color based on type and state
     */
    getNodeColor(node) {
        if (node.active) return '#4CAF50';
        if (node.completed) return '#2196F3';
        if (node.type === 'alternative') return '#FF9800';
        return '#9E9E9E';
    }

    /**
     * Get node stroke color
     */
    getNodeStroke(node) {
        if (node.active) return '#388E3C';
        if (node.completed) return '#1976D2';
        return '#757575';
    }

    /**
     * Check if node has alternatives
     */
    hasAlternatives(node) {
        if (node.index === -1) return false;
        const step = this.reasoningChain[node.index];
        return step && step.alternatives && step.alternatives.length > 0;
    }

    /**
     * Toggle branch expansion
     */
    toggleBranch(node) {
        if (this.expandedBranches.has(node.id)) {
            this.expandedBranches.delete(node.id);
        } else {
            this.expandedBranches.add(node.id);
        }
        this.updateVisualization();
    }

    /**
     * Show node details in a popup
     */
    showNodeDetails(node) {
        const step = this.reasoningChain[node.index];
        if (!step) return;
        
        const popup = d3.select('body').append('div')
            .attr('class', 'reasoning-popup')
            .style('position', 'absolute')
            .style('background', 'white')
            .style('border', '1px solid #ccc')
            .style('border-radius', '4px')
            .style('padding', '10px')
            .style('box-shadow', '0 2px 10px rgba(0,0,0,0.1)')
            .style('max-width', '300px')
            .style('z-index', 1000);
            
        popup.append('h4')
            .text(`Step ${node.index + 1}: ${step.type}`);
            
        popup.append('p')
            .text(step.description);
            
        popup.append('div')
            .html(`
                <strong>Confidence:</strong> ${(step.confidence * 100).toFixed(1)}%<br>
                <strong>Duration:</strong> ${step.duration}ms<br>
                <strong>Premises:</strong> ${step.premises.length}<br>
                <strong>Conclusions:</strong> ${step.conclusions.length}
            `);
            
        if (step.alternatives.length > 0) {
            popup.append('div')
                .html(`<strong>Alternatives:</strong> ${step.alternatives.length}`);
        }
        
        popup.append('button')
            .text('Close')
            .style('margin-top', '10px')
            .on('click', () => popup.remove());
            
        // Position popup
        const rect = this.container.node().getBoundingClientRect();
        popup.style('left', (rect.left + node.x + 30) + 'px')
             .style('top', (rect.top + node.y - 50) + 'px');
    }

    /**
     * Show tooltip on hover
     */
    showTooltip(event, node) {
        const tooltip = d3.select('body').select('.reasoning-tooltip');
        if (tooltip.empty()) {
            d3.select('body').append('div')
                .attr('class', 'reasoning-tooltip')
                .style('position', 'absolute')
                .style('background', 'rgba(0,0,0,0.8)')
                .style('color', 'white')
                .style('padding', '5px 10px')
                .style('border-radius', '3px')
                .style('font-size', '12px')
                .style('pointer-events', 'none')
                .style('z-index', 1001);
        }
        
        const step = this.reasoningChain[node.index];
        const text = step ? 
            `${step.type}: ${step.description.substring(0, 50)}...` : 
            `${node.type}: ${node.description}`;
            
        d3.select('.reasoning-tooltip')
            .style('opacity', 1)
            .style('left', (event.pageX + 10) + 'px')
            .style('top', (event.pageY - 10) + 'px')
            .text(text);
    }

    /**
     * Hide tooltip
     */
    hideTooltip() {
        d3.select('.reasoning-tooltip').style('opacity', 0);
    }

    /**
     * Navigation methods
     */
    nextStep() {
        if (this.currentStep < this.reasoningChain.length - 1) {
            this.currentStep++;
            this.updateVisualization();
            this.updateStepIndicator();
        }
    }

    previousStep() {
        if (this.currentStep > 0) {
            this.currentStep--;
            this.updateVisualization();
            this.updateStepIndicator();
        }
    }

    resetVisualization() {
        this.currentStep = -1;
        this.updateVisualization();
        this.updateStepIndicator();
    }

    togglePlayback() {
        this.isPlaying = !this.isPlaying;
        const btn = document.getElementById('playPauseBtn');
        
        if (this.isPlaying) {
            btn.innerHTML = '<span class="btn-icon">⏸️</span> Pause';
            this.startPlayback();
        } else {
            btn.innerHTML = '<span class="btn-icon">▶️</span> Play';
            this.stopPlayback();
        }
    }

    startPlayback() {
        this.playbackInterval = setInterval(() => {
            if (this.currentStep < this.reasoningChain.length - 1) {
                this.nextStep();
            } else {
                this.stopPlayback();
            }
        }, 2000);
    }

    stopPlayback() {
        if (this.playbackInterval) {
            clearInterval(this.playbackInterval);
            this.playbackInterval = null;
        }
        this.isPlaying = false;
        const btn = document.getElementById('playPauseBtn');
        btn.innerHTML = '<span class="btn-icon">▶️</span> Play';
    }

    updateStepIndicator() {
        const indicator = document.getElementById('stepIndicator');
        if (indicator) {
            indicator.textContent = `Step ${this.currentStep + 1} of ${this.reasoningChain.length}`;
        }
    }

    updateDetailLevel() {
        this.updateVisualization();
    }

    toggleUncertaintyDisplay() {
        this.updateVisualization();
    }

    /**
     * Drag handlers
     */
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
     * Handle resize
     */
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

    /**
     * Handle keyboard shortcuts
     */
    handleKeyboard(event) {
        switch (event.key) {
            case 'ArrowRight':
                event.preventDefault();
                this.nextStep();
                break;
            case 'ArrowLeft':
                event.preventDefault();
                this.previousStep();
                break;
            case ' ':
                event.preventDefault();
                this.togglePlayback();
                break;
            case 'r':
                event.preventDefault();
                this.resetVisualization();
                break;
        }
    }

    /**
     * Complete reasoning process
     */
    completeReasoning(data) {
        this.currentStep = this.reasoningChain.length - 1;
        this.updateVisualization();
        this.updateStepIndicator();
        
        if (this.isPlaying) {
            this.stopPlayback();
        }
    }

    /**
     * Clear visualization
     */
    clear() {
        this.reasoningChain = [];
        this.currentStep = -1;
        this.expandedBranches.clear();
        this.updateVisualization();
        this.updateStepIndicator();
    }

    /**
     * Export reasoning chain data
     */
    exportData() {
        return {
            reasoningChain: this.reasoningChain,
            currentStep: this.currentStep,
            expandedBranches: Array.from(this.expandedBranches),
            timestamp: Date.now()
        };
    }

    /**
     * Import reasoning chain data
     */
    importData(data) {
        this.reasoningChain = data.reasoningChain || [];
        this.currentStep = data.currentStep || -1;
        this.expandedBranches = new Set(data.expandedBranches || []);
        this.updateVisualization();
        this.updateStepIndicator();
    }
}

// Initialize global instance
window.reasoningVisualizer = new ReasoningVisualizer('reasoningVisualization');

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ReasoningVisualizer;
}