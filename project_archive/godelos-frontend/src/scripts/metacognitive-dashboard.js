/**
 * Metacognitive Dashboard for GödelOS
 * Provides real-time monitoring of metacognitive processes, self-evaluation metrics,
 * and autonomous learning objectives
 */

class MetacognitiveDashboard {
    constructor(containerId = 'metacognitiveDashboard') {
        this.containerId = containerId;
        this.container = null;
        this.width = 800;
        this.height = 600;
        
        // Dashboard data
        this.metacognitiveData = {
            selfEvaluation: {
                confidence: 0.75,
                competence: 0.68,
                consistency: 0.82,
                accuracy: 0.71
            },
            learningObjectives: [],
            performanceMetrics: {
                queryResponseTime: [],
                accuracyTrend: [],
                learningRate: [],
                adaptationSpeed: []
            },
            strategyAdaptation: {
                currentStrategy: 'balanced',
                adaptationHistory: [],
                effectiveness: 0.73
            },
            knowledgeGaps: [],
            recommendations: []
        };
        
        // Update intervals
        this.updateInterval = null;
        this.refreshRate = 5000; // 5 seconds
        
        // WebSocket connection
        this.wsConnection = null;
        
        // Chart instances
        this.charts = {};
        
        this.initialize();
    }

    /**
     * Initialize the metacognitive dashboard
     */
    initialize() {
        this.createContainer();
        this.setupLayout();
        this.setupWebSocketConnection();
        this.setupEventListeners();
        this.startPeriodicUpdates();
        
        console.log('Metacognitive Dashboard initialized');
    }

    /**
     * Create the dashboard container
     */
    createContainer() {
        this.container = d3.select(`#${this.containerId}`);
        if (this.container.empty()) {
            console.error(`Container #${this.containerId} not found`);
            return;
        }
        
        this.container.classed('metacognitive-dashboard', true);
    }

    /**
     * Setup dashboard layout
     */
    setupLayout() {
        // Clear existing content
        this.container.selectAll('*').remove();
        
        // Create header
        const header = this.container.append('div')
            .attr('class', 'dashboard-header');
            
        header.append('h3')
            .text('Metacognitive Monitoring');
            
        header.append('div')
            .attr('class', 'dashboard-controls')
            .call(this.createControls.bind(this));
        
        // Create main dashboard grid
        const dashboardGrid = this.container.append('div')
            .attr('class', 'dashboard-grid');
            
        // Self-evaluation panel
        this.createSelfEvaluationPanel(dashboardGrid);
        
        // Performance metrics panel
        this.createPerformancePanel(dashboardGrid);
        
        // Learning objectives panel
        this.createLearningObjectivesPanel(dashboardGrid);
        
        // Strategy adaptation panel
        this.createStrategyPanel(dashboardGrid);
        
        // Knowledge gaps panel
        this.createKnowledgeGapsPanel(dashboardGrid);
        
        // Recommendations panel
        this.createRecommendationsPanel(dashboardGrid);
    }

    /**
     * Create dashboard controls
     */
    createControls(selection) {
        // Refresh rate control
        const refreshGroup = selection.append('div')
            .attr('class', 'control-group');
            
        refreshGroup.append('label').text('Refresh Rate:');
        
        const refreshSelect = refreshGroup.append('select')
            .attr('id', 'refreshRate')
            .on('change', () => this.updateRefreshRate());
            
        refreshSelect.selectAll('option')
            .data([
                { value: 1000, text: '1 second' },
                { value: 5000, text: '5 seconds' },
                { value: 10000, text: '10 seconds' },
                { value: 30000, text: '30 seconds' }
            ])
            .enter()
            .append('option')
            .attr('value', d => d.value)
            .text(d => d.text)
            .property('selected', d => d.value === this.refreshRate);
            
        // Manual refresh button
        selection.append('button')
            .attr('class', 'btn secondary')
            .html('<span class="btn-icon">🔄</span> Refresh')
            .on('click', () => this.manualRefresh());
            
        // Export button
        selection.append('button')
            .attr('class', 'btn secondary')
            .html('<span class="btn-icon">📊</span> Export')
            .on('click', () => this.exportData());
    }

    /**
     * Create self-evaluation panel
     */
    createSelfEvaluationPanel(parent) {
        const panel = parent.append('div')
            .attr('class', 'dashboard-panel self-evaluation-panel');
            
        panel.append('h4')
            .html('<span class="panel-icon">🎯</span> Self-Evaluation Metrics');
            
        const metricsGrid = panel.append('div')
            .attr('class', 'metrics-grid');
            
        // Create metric cards
        const metrics = [
            { key: 'confidence', label: 'Confidence', icon: '💪', color: '#4CAF50' },
            { key: 'competence', label: 'Competence', icon: '🧠', color: '#2196F3' },
            { key: 'consistency', label: 'Consistency', icon: '⚖️', color: '#FF9800' },
            { key: 'accuracy', label: 'Accuracy', icon: '🎯', color: '#9C27B0' }
        ];
        
        metrics.forEach(metric => {
            const card = metricsGrid.append('div')
                .attr('class', 'metric-card')
                .attr('data-metric', metric.key);
                
            card.append('div')
                .attr('class', 'metric-icon')
                .text(metric.icon);
                
            card.append('div')
                .attr('class', 'metric-label')
                .text(metric.label);
                
            const valueContainer = card.append('div')
                .attr('class', 'metric-value-container');
                
            valueContainer.append('div')
                .attr('class', 'metric-value')
                .attr('id', `metric-${metric.key}`)
                .text('0.00');
                
            // Add progress bar
            const progressBar = valueContainer.append('div')
                .attr('class', 'metric-progress');
                
            progressBar.append('div')
                .attr('class', 'metric-progress-fill')
                .attr('id', `progress-${metric.key}`)
                .style('background-color', metric.color)
                .style('width', '0%');
        });
    }

    /**
     * Create performance metrics panel
     */
    createPerformancePanel(parent) {
        const panel = parent.append('div')
            .attr('class', 'dashboard-panel performance-panel');
            
        panel.append('h4')
            .html('<span class="panel-icon">📈</span> Performance Trends');
            
        // Create chart container
        const chartContainer = panel.append('div')
            .attr('class', 'chart-container')
            .attr('id', 'performanceChart');
            
        // Initialize performance chart
        this.initializePerformanceChart();
    }

    /**
     * Create learning objectives panel
     */
    createLearningObjectivesPanel(parent) {
        const panel = parent.append('div')
            .attr('class', 'dashboard-panel learning-objectives-panel');
            
        panel.append('h4')
            .html('<span class="panel-icon">🎓</span> Learning Objectives');
            
        const objectivesList = panel.append('div')
            .attr('class', 'objectives-list')
            .attr('id', 'objectivesList');
            
        // Add new objective button
        panel.append('button')
            .attr('class', 'btn primary add-objective-btn')
            .html('<span class="btn-icon">➕</span> Add Objective')
            .on('click', () => this.addLearningObjective());
    }

    /**
     * Create strategy adaptation panel
     */
    createStrategyPanel(parent) {
        const panel = parent.append('div')
            .attr('class', 'dashboard-panel strategy-panel');
            
        panel.append('h4')
            .html('<span class="panel-icon">🧭</span> Strategy Adaptation');
            
        const strategyInfo = panel.append('div')
            .attr('class', 'strategy-info');
            
        strategyInfo.append('div')
            .attr('class', 'current-strategy')
            .html('<strong>Current Strategy:</strong> <span id="currentStrategy">Loading...</span>');
            
        strategyInfo.append('div')
            .attr('class', 'strategy-effectiveness')
            .html('<strong>Effectiveness:</strong> <span id="strategyEffectiveness">0%</span>');
            
        // Strategy history chart
        const historyContainer = panel.append('div')
            .attr('class', 'strategy-history')
            .attr('id', 'strategyHistory');
            
        this.initializeStrategyChart();
    }

    /**
     * Create knowledge gaps panel
     */
    createKnowledgeGapsPanel(parent) {
        const panel = parent.append('div')
            .attr('class', 'dashboard-panel knowledge-gaps-panel');
            
        panel.append('h4')
            .html('<span class="panel-icon">🕳️</span> Knowledge Gaps');
            
        const gapsList = panel.append('div')
            .attr('class', 'gaps-list')
            .attr('id', 'knowledgeGapsList');
    }

    /**
     * Create recommendations panel
     */
    createRecommendationsPanel(parent) {
        const panel = parent.append('div')
            .attr('class', 'dashboard-panel recommendations-panel');
            
        panel.append('h4')
            .html('<span class="panel-icon">💡</span> Learning Recommendations');
            
        const recommendationsList = panel.append('div')
            .attr('class', 'recommendations-list')
            .attr('id', 'recommendationsList');
    }

    /**
     * Initialize performance chart
     */
    initializePerformanceChart() {
        const container = d3.select('#performanceChart');
        const width = 400;
        const height = 200;
        const margin = { top: 20, right: 20, bottom: 30, left: 40 };
        
        const svg = container.append('svg')
            .attr('width', width)
            .attr('height', height)
            .attr('viewBox', `0 0 ${width} ${height}`)
            .attr('preserveAspectRatio', 'xMidYMid meet');
            
        const chartGroup = svg.append('g')
            .attr('transform', `translate(${margin.left},${margin.top})`);
            
        // Create scales
        const xScale = d3.scaleTime()
            .range([0, width - margin.left - margin.right]);
            
        const yScale = d3.scaleLinear()
            .range([height - margin.top - margin.bottom, 0]);
            
        // Create line generator
        const line = d3.line()
            .x(d => xScale(d.timestamp))
            .y(d => yScale(d.value))
            .curve(d3.curveMonotoneX);
            
        // Add axes
        chartGroup.append('g')
            .attr('class', 'x-axis')
            .attr('transform', `translate(0,${height - margin.top - margin.bottom})`);
            
        chartGroup.append('g')
            .attr('class', 'y-axis');
            
        // Store chart elements for updates
        this.charts.performance = {
            svg,
            chartGroup,
            xScale,
            yScale,
            line,
            width: width - margin.left - margin.right,
            height: height - margin.top - margin.bottom
        };
    }

    /**
     * Initialize strategy adaptation chart
     */
    initializeStrategyChart() {
        const container = d3.select('#strategyHistory');
        const width = 300;
        const height = 150;
        
        const svg = container.append('svg')
            .attr('width', width)
            .attr('height', height)
            .attr('viewBox', `0 0 ${width} ${height}`)
            .attr('preserveAspectRatio', 'xMidYMid meet');
            
        this.charts.strategy = { svg, width, height };
    }

    /**
     * Setup WebSocket connection
     */
    setupWebSocketConnection() {
        if (window.wsManager) {
            this.wsConnection = window.wsManager;
            this.wsConnection.on('metacognitive-update', (data) => {
                this.handleMetacognitiveUpdate(data);
            });
            this.wsConnection.on('learning-progress', (data) => {
                this.handleLearningProgress(data);
            });
            this.wsConnection.on('strategy-adaptation', (data) => {
                this.handleStrategyAdaptation(data);
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
     * Start periodic updates
     */
    startPeriodicUpdates() {
        this.updateInterval = setInterval(() => {
            this.updateDashboard();
        }, this.refreshRate);
    }

    /**
     * Update dashboard with latest data
     */
    updateDashboard() {
        this.updateSelfEvaluationMetrics();
        this.updatePerformanceChart();
        this.updateLearningObjectives();
        this.updateStrategyInfo();
        this.updateKnowledgeGaps();
        this.updateRecommendations();
    }

    /**
     * Update self-evaluation metrics
     */
    updateSelfEvaluationMetrics() {
        const metrics = this.metacognitiveData.selfEvaluation;
        
        Object.entries(metrics).forEach(([key, value]) => {
            // Update value display
            d3.select(`#metric-${key}`)
                .transition()
                .duration(500)
                .tween('text', function() {
                    const i = d3.interpolate(+this.textContent, value);
                    return function(t) {
                        this.textContent = i(t).toFixed(2);
                    };
                });
                
            // Update progress bar
            d3.select(`#progress-${key}`)
                .transition()
                .duration(500)
                .style('width', (value * 100) + '%');
        });
    }

    /**
     * Update performance chart
     */
    updatePerformanceChart() {
        if (!this.charts.performance) return;
        
        const chart = this.charts.performance;
        const data = this.metacognitiveData.performanceMetrics.accuracyTrend;
        
        if (data.length === 0) return;
        
        // Update scales
        chart.xScale.domain(d3.extent(data, d => d.timestamp));
        chart.yScale.domain([0, 1]);
        
        // Update axes
        chart.chartGroup.select('.x-axis')
            .transition()
            .duration(500)
            .call(d3.axisBottom(chart.xScale).tickFormat(d3.timeFormat('%H:%M')));
            
        chart.chartGroup.select('.y-axis')
            .transition()
            .duration(500)
            .call(d3.axisLeft(chart.yScale).tickFormat(d3.format('.0%')));
            
        // Update line
        const path = chart.chartGroup.selectAll('.performance-line')
            .data([data]);
            
        path.enter()
            .append('path')
            .attr('class', 'performance-line')
            .attr('fill', 'none')
            .attr('stroke', '#4CAF50')
            .attr('stroke-width', 2)
            .merge(path)
            .transition()
            .duration(500)
            .attr('d', chart.line);
    }

    /**
     * Update learning objectives
     */
    updateLearningObjectives() {
        const objectives = this.metacognitiveData.learningObjectives;
        const container = d3.select('#objectivesList');
        
        const objectiveItems = container.selectAll('.objective-item')
            .data(objectives, d => d.id);
            
        objectiveItems.exit().remove();
        
        const objectiveEnter = objectiveItems.enter()
            .append('div')
            .attr('class', 'objective-item');
            
        objectiveEnter.append('div')
            .attr('class', 'objective-title');
            
        objectiveEnter.append('div')
            .attr('class', 'objective-progress');
            
        objectiveEnter.append('div')
            .attr('class', 'objective-status');
            
        const objectiveUpdate = objectiveEnter.merge(objectiveItems);
        
        objectiveUpdate.select('.objective-title')
            .text(d => d.title);
            
        objectiveUpdate.select('.objective-progress')
            .html(d => `
                <div class="progress-bar">
                    <div class="progress-fill" style="width: ${d.progress * 100}%"></div>
                </div>
                <span class="progress-text">${(d.progress * 100).toFixed(0)}%</span>
            `);
            
        objectiveUpdate.select('.objective-status')
            .attr('class', d => `objective-status ${d.status}`)
            .text(d => d.status);
    }

    /**
     * Update strategy information
     */
    updateStrategyInfo() {
        const strategy = this.metacognitiveData.strategyAdaptation;
        
        d3.select('#currentStrategy')
            .text(strategy.currentStrategy);
            
        d3.select('#strategyEffectiveness')
            .text((strategy.effectiveness * 100).toFixed(1) + '%');
    }

    /**
     * Update knowledge gaps
     */
    updateKnowledgeGaps() {
        const gaps = this.metacognitiveData.knowledgeGaps;
        const container = d3.select('#knowledgeGapsList');
        
        const gapItems = container.selectAll('.gap-item')
            .data(gaps, d => d.id);
            
        gapItems.exit().remove();
        
        const gapEnter = gapItems.enter()
            .append('div')
            .attr('class', 'gap-item');
            
        gapEnter.append('div')
            .attr('class', 'gap-topic');
            
        gapEnter.append('div')
            .attr('class', 'gap-severity');
            
        gapEnter.append('div')
            .attr('class', 'gap-impact');
            
        const gapUpdate = gapEnter.merge(gapItems);
        
        gapUpdate.select('.gap-topic')
            .text(d => d.topic);
            
        gapUpdate.select('.gap-severity')
            .attr('class', d => `gap-severity ${d.severity}`)
            .text(d => d.severity);
            
        gapUpdate.select('.gap-impact')
            .text(d => `Impact: ${d.impact}`);
    }

    /**
     * Update recommendations
     */
    updateRecommendations() {
        const recommendations = this.metacognitiveData.recommendations;
        const container = d3.select('#recommendationsList');
        
        const recItems = container.selectAll('.recommendation-item')
            .data(recommendations, d => d.id);
            
        recItems.exit().remove();
        
        const recEnter = recItems.enter()
            .append('div')
            .attr('class', 'recommendation-item');
            
        recEnter.append('div')
            .attr('class', 'recommendation-text');
            
        recEnter.append('div')
            .attr('class', 'recommendation-priority');
            
        recEnter.append('button')
            .attr('class', 'btn secondary recommendation-action')
            .text('Apply')
            .on('click', (event, d) => this.applyRecommendation(d));
            
        const recUpdate = recEnter.merge(recItems);
        
        recUpdate.select('.recommendation-text')
            .text(d => d.text);
            
        recUpdate.select('.recommendation-priority')
            .attr('class', d => `recommendation-priority ${d.priority}`)
            .text(d => d.priority);
    }

    /**
     * Handle metacognitive updates from WebSocket
     */
    handleMetacognitiveUpdate(data) {
        if (data.selfEvaluation) {
            Object.assign(this.metacognitiveData.selfEvaluation, data.selfEvaluation);
        }
        
        if (data.performanceMetrics) {
            Object.assign(this.metacognitiveData.performanceMetrics, data.performanceMetrics);
        }
        
        this.updateDashboard();
    }

    /**
     * Handle learning progress updates
     */
    handleLearningProgress(data) {
        if (data.objectives) {
            this.metacognitiveData.learningObjectives = data.objectives;
        }
        
        if (data.knowledgeGaps) {
            this.metacognitiveData.knowledgeGaps = data.knowledgeGaps;
        }
        
        this.updateLearningObjectives();
        this.updateKnowledgeGaps();
    }

    /**
     * Handle strategy adaptation updates
     */
    handleStrategyAdaptation(data) {
        Object.assign(this.metacognitiveData.strategyAdaptation, data);
        this.updateStrategyInfo();
    }

    /**
     * Add new learning objective
     */
    addLearningObjective() {
        const title = prompt('Enter learning objective:');
        if (title) {
            const objective = {
                id: Date.now().toString(),
                title: title,
                progress: 0,
                status: 'active',
                created: new Date()
            };
            
            this.metacognitiveData.learningObjectives.push(objective);
            this.updateLearningObjectives();
            
            // Send to backend
            if (this.wsConnection) {
                this.wsConnection.send('add-learning-objective', objective);
            }
        }
    }

    /**
     * Apply recommendation
     */
    applyRecommendation(recommendation) {
        if (this.wsConnection) {
            this.wsConnection.send('apply-recommendation', { id: recommendation.id });
        }
        
        // Remove from list
        this.metacognitiveData.recommendations = 
            this.metacognitiveData.recommendations.filter(r => r.id !== recommendation.id);
        this.updateRecommendations();
    }

    /**
     * Update refresh rate
     */
    updateRefreshRate() {
        const newRate = parseInt(document.getElementById('refreshRate').value);
        this.refreshRate = newRate;
        
        // Restart periodic updates
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
        }
        this.startPeriodicUpdates();
    }

    /**
     * Manual refresh
     */
    manualRefresh() {
        this.updateDashboard();
        
        // Visual feedback
        const button = d3.select('.btn:contains("Refresh")');
        button.classed('refreshing', true);
        setTimeout(() => {
            button.classed('refreshing', false);
        }, 1000);
    }

    /**
     * Export dashboard data
     */
    exportData() {
        const exportData = {
            timestamp: new Date().toISOString(),
            metacognitiveData: this.metacognitiveData
        };
        
        const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `metacognitive-data-${Date.now()}.json`;
        a.click();
        URL.revokeObjectURL(url);
    }

    /**
     * Handle resize
     */
    handleResize() {
        // Redraw charts if needed
        if (this.charts.performance) {
            this.updatePerformanceChart();
        }
    }

    /**
     * Refresh the metacognitive dashboard
     */
    async refresh() {
        try {
            await this.loadMetacognitiveData();
            this.updateDashboard();
        } catch (error) {
            console.warn('Failed to refresh metacognitive data:', error);
            this.useOfflineMode();
        }
    }

    /**
     * Use offline/static data when live data is unavailable
     */
    useOfflineMode() {
        console.log('Metacognitive dashboard using offline mode');
        // Use current sample data structure
        this.updateDashboard();
    }

    /**
     * Cleanup
     */
    destroy() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
        }
    }
}

// Initialize global instance
window.metacognitiveDashboard = new MetacognitiveDashboard('metacognitiveDashboard');

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = MetacognitiveDashboard;
}