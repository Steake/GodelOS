/**
 * Uncertainty Visualization Engine for GödelOS
 * Provides multi-dimensional uncertainty display and interactive exploration tools
 */

class UncertaintyVisualizer {
    constructor(containerId = 'uncertaintyVisualization') {
        this.containerId = containerId;
        this.container = null;
        this.svg = null;
        this.width = 800;
        this.height = 600;
        this.margin = { top: 20, right: 20, bottom: 40, left: 60 };
        
        // Uncertainty data
        this.uncertaintyData = {
            epistemic: [], // Knowledge uncertainty
            aleatoric: [], // Data uncertainty
            model: [],     // Model uncertainty
            temporal: []   // Time-based uncertainty
        };
        
        // Visualization state
        this.currentView = 'overview';
        this.selectedDimension = 'epistemic';
        this.confidenceThreshold = 0.5;
        
        // WebSocket connection
        this.wsConnection = null;
        
        this.initialize();
    }

    initialize() {
        this.createContainer();
        this.setupLayout();
        this.setupWebSocketConnection();
        this.setupEventListeners();
        this.loadInitialData();
        
        console.log('Uncertainty Visualizer initialized');
    }

    createContainer() {
        this.container = d3.select(`#${this.containerId}`);
        if (this.container.empty()) {
            console.error(`Container #${this.containerId} not found`);
            return;
        }
        
        this.container.classed('uncertainty-visualizer', true);
    }

    setupLayout() {
        this.container.selectAll('*').remove();
        
        const header = this.container.append('div')
            .attr('class', 'uncertainty-header');
            
        header.append('h3').text('Uncertainty Analysis');
        this.createControls(header);
        
        const vizArea = this.container.append('div')
            .attr('class', 'uncertainty-viz-area');
            
        this.createViewTabs(vizArea);
        
        this.svg = vizArea.append('svg')
            .attr('width', '100%')
            .attr('height', this.height)
            .attr('viewBox', `0 0 ${this.width} ${this.height}`)
            .attr('preserveAspectRatio', 'xMidYMid meet');
            
        this.chartGroup = this.svg.append('g')
            .attr('transform', `translate(${this.margin.left},${this.margin.top})`);
            
        this.createInfoPanel(vizArea);
        this.switchView('overview');
    }

    createControls(parent) {
        const controls = parent.append('div')
            .attr('class', 'uncertainty-controls');
            
        const dimensionGroup = controls.append('div')
            .attr('class', 'control-group');
            
        dimensionGroup.append('label').text('Uncertainty Type:');
        
        const dimensionSelect = dimensionGroup.append('select')
            .attr('id', 'uncertaintyDimension')
            .on('change', () => this.changeDimension());
            
        dimensionSelect.selectAll('option')
            .data([
                { value: 'epistemic', text: 'Epistemic (Knowledge)' },
                { value: 'aleatoric', text: 'Aleatoric (Data)' },
                { value: 'model', text: 'Model Uncertainty' },
                { value: 'temporal', text: 'Temporal Uncertainty' }
            ])
            .enter()
            .append('option')
            .attr('value', d => d.value)
            .text(d => d.text);
            
        const thresholdGroup = controls.append('div')
            .attr('class', 'control-group');
            
        thresholdGroup.append('label').text('Confidence Threshold:');
        
        thresholdGroup.append('input')
            .attr('type', 'range')
            .attr('id', 'confidenceThreshold')
            .attr('min', 0)
            .attr('max', 1)
            .attr('step', 0.01)
            .attr('value', this.confidenceThreshold)
            .on('input', () => this.updateConfidenceThreshold());
            
        thresholdGroup.append('span')
            .attr('id', 'thresholdValue')
            .text((this.confidenceThreshold * 100).toFixed(0) + '%');
    }

    createViewTabs(parent) {
        const tabContainer = parent.append('div')
            .attr('class', 'view-tabs');
            
        const tabs = [
            { id: 'overview', label: 'Overview', icon: '📊' },
            { id: 'distribution', label: 'Distribution', icon: '📈' },
            { id: 'correlation', label: 'Correlation', icon: '🔗' }
        ];
        
        tabs.forEach(tab => {
            const tabButton = tabContainer.append('button')
                .attr('class', 'tab-button')
                .attr('data-view', tab.id)
                .html(`<span class="tab-icon">${tab.icon}</span> ${tab.label}`)
                .on('click', () => this.switchView(tab.id));
                
            if (tab.id === this.currentView) {
                tabButton.classed('active', true);
            }
        });
    }

    createInfoPanel(parent) {
        const infoPanel = parent.append('div')
            .attr('class', 'uncertainty-info-panel')
            .attr('id', 'uncertaintyInfo');
            
        infoPanel.append('h4').text('Uncertainty Details');
        
        const infoContent = infoPanel.append('div')
            .attr('class', 'info-content');
            
        const statsSection = infoContent.append('div')
            .attr('class', 'stats-section');
            
        statsSection.append('h5').text('Statistics');
        statsSection.append('div')
            .attr('class', 'stats-list')
            .attr('id', 'uncertaintyStats');
            
        const explanationSection = infoContent.append('div')
            .attr('class', 'explanation-section');
            
        explanationSection.append('h5').text('Interpretation');
        explanationSection.append('div')
            .attr('class', 'explanation-text')
            .attr('id', 'uncertaintyExplanation');
    }

    setupWebSocketConnection() {
        if (window.wsManager) {
            this.wsConnection = window.wsManager;
            this.wsConnection.on('uncertainty-update', (data) => {
                this.handleUncertaintyUpdate(data);
            });
        }
    }

    setupEventListeners() {
        window.addEventListener('resize', () => this.handleResize());
    }

    async loadInitialData() {
        try {
            // Use the API client with correct backend endpoints
            const targetIds = ['default']; // Default target for initial load
            const data = await window.apiClient.analyzeUncertainty(targetIds, {
                analysis_type: 'comprehensive',
                include_temporal: true
            });
            this.updateUncertaintyData(data);
        } catch (error) {
            console.warn('Failed to load uncertainty data:', error);
            this.loadSampleData();
        }
    }

    loadSampleData() {
        const now = Date.now();
        const sampleData = {
            epistemic: this.generateSampleData(now, 'epistemic'),
            aleatoric: this.generateSampleData(now, 'aleatoric'),
            model: this.generateSampleData(now, 'model'),
            temporal: this.generateSampleData(now, 'temporal')
        };
        
        this.updateUncertaintyData(sampleData);
    }

    generateSampleData(baseTime, type) {
        const data = [];
        const count = 30;
        
        for (let i = 0; i < count; i++) {
            const timestamp = new Date(baseTime - (count - i) * 60000);
            let value, confidence;
            
            switch (type) {
                case 'epistemic':
                    value = 0.3 + Math.random() * 0.4;
                    confidence = 0.6 + Math.random() * 0.3;
                    break;
                case 'aleatoric':
                    value = 0.2 + Math.random() * 0.3;
                    confidence = 0.7 + Math.random() * 0.2;
                    break;
                case 'model':
                    value = 0.1 + Math.random() * 0.5;
                    confidence = 0.5 + Math.random() * 0.4;
                    break;
                case 'temporal':
                    value = 0.15 + Math.random() * 0.35;
                    confidence = 0.65 + Math.random() * 0.25;
                    break;
                default:
                    value = Math.random();
                    confidence = Math.random();
            }
            
            data.push({
                timestamp,
                value: Math.max(0, Math.min(1, value)),
                confidence: Math.max(0, Math.min(1, confidence)),
                metadata: {
                    source: `${type}_source_${i}`,
                    context: `Context for ${type} uncertainty`
                }
            });
        }
        
        return data;
    }

    updateUncertaintyData(data) {
        Object.assign(this.uncertaintyData, data);
        this.updateVisualization();
        this.updateStatistics();
        this.updateExplanation();
    }

    switchView(viewId) {
        this.currentView = viewId;
        
        this.container.selectAll('.tab-button')
            .classed('active', false)
            .filter(`[data-view="${viewId}"]`)
            .classed('active', true);
            
        this.chartGroup.selectAll('*').remove();
        
        switch (viewId) {
            case 'overview':
                this.drawOverviewChart();
                break;
            case 'distribution':
                this.drawDistributionChart();
                break;
            case 'correlation':
                this.drawCorrelationChart();
                break;
        }
    }

    drawOverviewChart() {
        const chartWidth = this.width - this.margin.left - this.margin.right;
        const chartHeight = this.height - this.margin.top - this.margin.bottom;
        
        const allData = Object.values(this.uncertaintyData).flat();
        const timeExtent = d3.extent(allData, d => d.timestamp);
        
        const xScale = d3.scaleTime()
            .domain(timeExtent)
            .range([0, chartWidth]);
            
        const yScale = d3.scaleLinear()
            .domain([0, 1])
            .range([chartHeight, 0]);
            
        const line = d3.line()
            .x(d => xScale(d.timestamp))
            .y(d => yScale(d.value))
            .curve(d3.curveMonotoneX);
            
        const colorScale = d3.scaleOrdinal()
            .domain(['epistemic', 'aleatoric', 'model', 'temporal'])
            .range(['#e74c3c', '#3498db', '#2ecc71', '#f39c12']);
            
        // Draw axes
        this.chartGroup.append('g')
            .attr('class', 'x-axis')
            .attr('transform', `translate(0,${chartHeight})`)
            .call(d3.axisBottom(xScale).tickFormat(d3.timeFormat('%H:%M')));
            
        this.chartGroup.append('g')
            .attr('class', 'y-axis')
            .call(d3.axisLeft(yScale).tickFormat(d3.format('.0%')));
            
        // Draw uncertainty lines
        Object.entries(this.uncertaintyData).forEach(([type, data]) => {
            if (data.length === 0) return;
            
            this.chartGroup.append('path')
                .datum(data)
                .attr('class', `uncertainty-line uncertainty-${type}`)
                .attr('fill', 'none')
                .attr('stroke', colorScale(type))
                .attr('stroke-width', 2)
                .attr('d', line);
                
            // Data points
            this.chartGroup.selectAll(`.point-${type}`)
                .data(data)
                .enter()
                .append('circle')
                .attr('class', `uncertainty-point point-${type}`)
                .attr('cx', d => xScale(d.timestamp))
                .attr('cy', d => yScale(d.value))
                .attr('r', 3)
                .attr('fill', colorScale(type))
                .attr('opacity', 0.7)
                .on('mouseover', (event, d) => this.showTooltip(event, d, type))
                .on('mouseout', () => this.hideTooltip());
        });
        
        this.drawLegend(colorScale);
    }

    drawDistributionChart() {
        const data = this.uncertaintyData[this.selectedDimension] || [];
        if (data.length === 0) return;
        
        const chartWidth = this.width - this.margin.left - this.margin.right;
        const chartHeight = this.height - this.margin.top - this.margin.bottom;
        
        const values = data.map(d => d.value);
        const bins = d3.histogram()
            .domain([0, 1])
            .thresholds(15)(values);
            
        const xScale = d3.scaleLinear()
            .domain([0, 1])
            .range([0, chartWidth]);
            
        const yScale = d3.scaleLinear()
            .domain([0, d3.max(bins, d => d.length)])
            .range([chartHeight, 0]);
            
        // Draw axes
        this.chartGroup.append('g')
            .attr('class', 'x-axis')
            .attr('transform', `translate(0,${chartHeight})`)
            .call(d3.axisBottom(xScale).tickFormat(d3.format('.0%')));
            
        this.chartGroup.append('g')
            .attr('class', 'y-axis')
            .call(d3.axisLeft(yScale));
            
        // Draw bars
        this.chartGroup.selectAll('.histogram-bar')
            .data(bins)
            .enter()
            .append('rect')
            .attr('class', 'histogram-bar')
            .attr('x', d => xScale(d.x0))
            .attr('y', d => yScale(d.length))
            .attr('width', d => Math.max(0, xScale(d.x1) - xScale(d.x0) - 1))
            .attr('height', d => chartHeight - yScale(d.length))
            .attr('fill', '#3498db')
            .attr('opacity', 0.7);
    }

    drawCorrelationChart() {
        const types = Object.keys(this.uncertaintyData);
        const correlationMatrix = this.calculateCorrelationMatrix();
        
        const chartWidth = this.width - this.margin.left - this.margin.right;
        const cellSize = Math.min(chartWidth, 300) / types.length;
        
        const colorScale = d3.scaleSequential(d3.interpolateRdBu)
            .domain([-1, 1]);
            
        types.forEach((typeA, i) => {
            types.forEach((typeB, j) => {
                const correlation = correlationMatrix[typeA][typeB];
                
                this.chartGroup.append('rect')
                    .attr('x', i * cellSize)
                    .attr('y', j * cellSize)
                    .attr('width', cellSize)
                    .attr('height', cellSize)
                    .attr('fill', colorScale(correlation))
                    .attr('stroke', '#fff')
                    .attr('stroke-width', 1);
                    
                this.chartGroup.append('text')
                    .attr('x', i * cellSize + cellSize / 2)
                    .attr('y', j * cellSize + cellSize / 2)
                    .attr('text-anchor', 'middle')
                    .attr('dy', '0.35em')
                    .style('font-size', '12px')
                    .style('fill', Math.abs(correlation) > 0.5 ? 'white' : 'black')
                    .text(correlation.toFixed(2));
            });
        });
        
        // Add labels
        types.forEach((type, i) => {
            this.chartGroup.append('text')
                .attr('x', i * cellSize + cellSize / 2)
                .attr('y', -5)
                .attr('text-anchor', 'middle')
                .style('font-size', '12px')
                .text(type);
        });
    }

    drawLegend(colorScale) {
        const legend = this.chartGroup.append('g')
            .attr('class', 'legend')
            .attr('transform', `translate(${this.width - this.margin.left - this.margin.right - 150}, 20)`);
            
        const legendItems = legend.selectAll('.legend-item')
            .data(colorScale.domain())
            .enter()
            .append('g')
            .attr('class', 'legend-item')
            .attr('transform', (d, i) => `translate(0, ${i * 20})`);
            
        legendItems.append('line')
            .attr('x1', 0)
            .attr('x2', 15)
            .attr('y1', 0)
            .attr('y2', 0)
            .attr('stroke', colorScale)
            .attr('stroke-width', 2);
            
        legendItems.append('text')
            .attr('x', 20)
            .attr('y', 0)
            .attr('dy', '0.35em')
            .style('font-size', '12px')
            .text(d => d.charAt(0).toUpperCase() + d.slice(1));
    }

    calculateCorrelationMatrix() {
        const types = Object.keys(this.uncertaintyData);
        const matrix = {};
        
        types.forEach(typeA => {
            matrix[typeA] = {};
            types.forEach(typeB => {
                matrix[typeA][typeB] = this.calculateCorrelation(
                    this.uncertaintyData[typeA],
                    this.uncertaintyData[typeB]
                );
            });
        });
        
        return matrix;
    }

    calculateCorrelation(dataA, dataB) {
        if (dataA.length !== dataB.length || dataA.length === 0) return 0;
        
        const valuesA = dataA.map(d => d.value);
        const valuesB = dataB.map(d => d.value);
        
        const meanA = d3.mean(valuesA);
        const meanB = d3.mean(valuesB);
        
        const numerator = d3.sum(valuesA.map((a, i) => (a - meanA) * (valuesB[i] - meanB)));
        const denomA = Math.sqrt(d3.sum(valuesA.map(a => (a - meanA) ** 2)));
        const denomB = Math.sqrt(d3.sum(valuesB.map(b => (b - meanB) ** 2)));
        
        return denomA * denomB === 0 ? 0 : numerator / (denomA * denomB);
    }

    updateVisualization() {
        this.switchView(this.currentView);
    }

    updateStatistics() {
        const data = this.uncertaintyData[this.selectedDimension] || [];
        if (data.length === 0) return;
        
        const values = data.map(d => d.value);
        const confidences = data.map(d => d.confidence);
        
        const stats = {
            mean: d3.mean(values),
            median: d3.median(values),
            std: d3.deviation(values),
            avgConfidence: d3.mean(confidences)
        };
        
        const statsContainer = d3.select('#uncertaintyStats');
        statsContainer.selectAll('*').remove();
        
        Object.entries(stats).forEach(([key, value]) => {
            const statItem = statsContainer.append('div')
                .attr('class', 'stat-item');
                
            statItem.append('span')
                .attr('class', 'stat-label')
                .text(key.charAt(0).toUpperCase() + key.slice(1) + ':');
                
            statItem.append('span')
                .attr('class', 'stat-value')
                .text(typeof value === 'number' ? value.toFixed(3) : 'N/A');
        });
    }

    updateExplanation() {
        const explanations = {
            epistemic: 'Epistemic uncertainty reflects our lack of knowledge about the true model.',
            aleatoric: 'Aleatoric uncertainty represents inherent randomness in the data.',
            model: 'Model uncertainty arises from the choice of model architecture.',
            temporal: 'Temporal uncertainty captures how uncertainty changes over time.'
        };
        
        d3.select('#uncertaintyExplanation')
            .text(explanations[this.selectedDimension] || '');
    }

    changeDimension() {
        this.selectedDimension = document.getElementById('uncertaintyDimension').value;
        this.updateVisualization();
        this.updateStatistics();
        this.updateExplanation();
    }

    updateConfidenceThreshold() {
        this.confidenceThreshold = parseFloat(document.getElementById('confidenceThreshold').value);
        document.getElementById('thresholdValue').textContent = 
            (this.confidenceThreshold * 100).toFixed(0) + '%';
        this.updateVisualization();
    }

    showTooltip(event, data, type) {
        const tooltip = d3.select('body').selectAll('.uncertainty-tooltip')
            .data([data]);
            
        const tooltipEnter = tooltip.enter()
            .append('div')
            .attr('class', 'uncertainty-tooltip')
            .style('position', 'absolute')
            .style('background', 'rgba(0,0,0,0.8)')
            .style('color', 'white')
            .style('padding', '8px')
            .style('border-radius', '4px')
            .style('font-size', '12px')
            .style('pointer-events', 'none')
            .style('z-index', 1000);
            
        const tooltipUpdate = tooltipEnter.merge(tooltip);
        
        tooltipUpdate
            .html(`
                <strong>${type.charAt(0).toUpperCase() + type.slice(1)}</strong><br>
                Value: ${(data.value * 100).toFixed(1)}%<br>
                Confidence: ${(data.confidence * 100).toFixed(1)}%<br>
                Time: ${data.timestamp.toLocaleTimeString()}
            `)
            .style('left', (event.pageX + 10) + 'px')
            .style('top', (event.pageY - 10) + 'px')
            .style('opacity', 1);
    }

    hideTooltip() {
        d3.select('.uncertainty-tooltip').style('opacity', 0);
    }

    handleUncertaintyUpdate(data) {
        Object.assign(this.uncertaintyData, data);
        this.updateVisualization();
        this.updateStatistics();
    }

    handleResize() {
        const rect = this.container.node().getBoundingClientRect();
        this.width = rect.width;
        this.height = Math.max(400, rect.height - 100);
        
        this.svg.attr('viewBox', `0 0 ${this.width} ${this.height}`);
        this.updateVisualization();
    }

    /**
     * Refresh the uncertainty visualization
     */
    async refresh() {
        try {
            await this.loadInitialData();
            this.updateVisualization();
        } catch (error) {
            console.warn('Failed to refresh uncertainty data:', error);
            this.useStaticData();
        }
    }

    /**
     * Check if the visualizer has valid data
     * @returns {boolean} True if there's valid uncertainty data
     */
    hasData() {
        return Object.values(this.uncertaintyData).some(data => data && data.length > 0);
    }

    /**
     * Use static/sample data when live data is unavailable
     */
    useStaticData() {
        this.uncertaintyData = {
            epistemic: [
                { category: 'Knowledge Gap', value: 0.3, timestamp: Date.now() },
                { category: 'Inference Confidence', value: 0.7, timestamp: Date.now() }
            ],
            aleatoric: [
                { category: 'Data Quality', value: 0.8, timestamp: Date.now() },
                { category: 'Measurement Error', value: 0.2, timestamp: Date.now() }
            ],
            model: [
                { category: 'Model Uncertainty', value: 0.4, timestamp: Date.now() },
                { category: 'Parameter Uncertainty', value: 0.6, timestamp: Date.now() }
            ],
            temporal: [
                { category: 'Prediction Decay', value: 0.5, timestamp: Date.now() }
            ]
        };
        this.updateVisualization();
    }
}

// Initialize global instance
window.uncertaintyVisualizer = new UncertaintyVisualizer('uncertaintyVisualization');

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = UncertaintyVisualizer;
}