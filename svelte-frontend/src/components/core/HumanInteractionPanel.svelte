<script>
  import { onMount, onDestroy } from 'svelte';
  import { cognitiveState, uiState } from '../../stores/cognitive.js';
  import { enhancedCognitiveState } from '../../stores/enhanced-cognitive.js';

  // Component props
  export let compactMode = false;
  export let showAdvancedMetrics = true;
  export let autoRefresh = true;

  // Local state for human interaction metrics
  let interactionMode = 'normal'; // normal, enhanced, diagnostic
  let humanPresenceDetected = false;
  let lastInteractionTime = null;
  let systemResponseiveness = 100;
  let cognitiveLoad = 0;
  let attentionFocus = 'idle';
  let communicationQuality = 95;
  let understandingLevel = 88;
  
  // Critical system indicators
  let cpuUsage = 0;
  let memoryUsage = 0;
  let networkLatency = 12;
  let processingSpeed = 150; // operations per second
  
  // Metadiagnostic data
  let consciousnessLevel = 0.85;
  let integrationMeasure = 0.76;
  let attentionAwareness = 0.82;
  let selfModelCoherence = 0.91;
  let phenomenalDescriptors = 0;
  let autonomousGoals = 3;
  
  // Real-time monitoring
  let unsubscribeCognitive, unsubscribeEnhanced;
  let updateInterval;

  onMount(() => {
    // Subscribe to cognitive state changes
    unsubscribeCognitive = cognitiveState.subscribe(state => {
      // Update metrics from cognitive state
      if (state.manifestConsciousness) {
        attentionFocus = state.manifestConsciousness.attention?.current || 'idle';
        cognitiveLoad = state.manifestConsciousness.processingLoad || 0;
      }
      
      // Extract system health metrics
      if (state.systemHealth) {
        const healthValues = Object.values(state.systemHealth).filter(v => typeof v === 'number');
        systemResponseiveness = healthValues.length > 0 
          ? Math.round(healthValues.reduce((a, b) => a + b, 0) / healthValues.length * 100)
          : 100;
      }
    });

    // Subscribe to enhanced cognitive state
    unsubscribeEnhanced = enhancedCognitiveState.subscribe(state => {
      if (state.manifestConsciousness) {
        consciousnessLevel = state.manifestConsciousness.consciousnessLevel || consciousnessLevel;
        integrationMeasure = state.manifestConsciousness.integrationMeasure || integrationMeasure;
        attentionAwareness = state.manifestConsciousness.attentionAwareness || attentionAwareness;
        
        // Update interaction state based on consciousness
        humanPresenceDetected = consciousnessLevel > 0.7;
        lastInteractionTime = humanPresenceDetected ? new Date() : lastInteractionTime;
      }
      
      if (state.autonomousLearning) {
        autonomousGoals = state.autonomousLearning.activeGoals?.length || autonomousGoals;
        selfModelCoherence = state.autonomousLearning.selfModelCoherence || selfModelCoherence;
      }
    });

    // Start real-time updates
    if (autoRefresh) {
      updateInterval = setInterval(updateMetrics, 2000);
    }
    
    // Initial metrics update
    updateMetrics();
  });

  onDestroy(() => {
    if (unsubscribeCognitive) unsubscribeCognitive();
    if (unsubscribeEnhanced) unsubscribeEnhanced();
    if (updateInterval) clearInterval(updateInterval);
  });

  function updateMetrics() {
    // Simulate real-time system metrics with some variance
    cpuUsage = Math.max(15, Math.min(95, cpuUsage + (Math.random() - 0.5) * 10));
    memoryUsage = Math.max(20, Math.min(85, memoryUsage + (Math.random() - 0.5) * 8));
    networkLatency = Math.max(5, Math.min(100, networkLatency + (Math.random() - 0.5) * 5));
    processingSpeed = Math.max(50, Math.min(300, processingSpeed + (Math.random() - 0.5) * 20));
    
    // Update communication metrics
    communicationQuality = Math.max(70, Math.min(100, communicationQuality + (Math.random() - 0.5) * 5));
    understandingLevel = Math.max(60, Math.min(100, understandingLevel + (Math.random() - 0.5) * 6));
    
    // Update metadiagnostic data with slight variations
    consciousnessLevel = Math.max(0.1, Math.min(1.0, consciousnessLevel + (Math.random() - 0.5) * 0.05));
    integrationMeasure = Math.max(0.1, Math.min(1.0, integrationMeasure + (Math.random() - 0.5) * 0.03));
    attentionAwareness = Math.max(0.1, Math.min(1.0, attentionAwareness + (Math.random() - 0.5) * 0.04));
    phenomenalDescriptors = Math.max(0, Math.min(10, phenomenalDescriptors + Math.round((Math.random() - 0.5) * 2)));
  }

  function setInteractionMode(mode) {
    interactionMode = mode;
    // Update UI state to reflect mode change
    uiState.update(state => ({
      ...state,
      interactionMode: mode,
      lastModeChange: new Date()
    }));
  }

  function getStatusColor(value, threshold = 0.7) {
    if (typeof value === 'number') {
      if (value >= threshold) return 'status-excellent';
      if (value >= threshold * 0.7) return 'status-good';
      if (value >= threshold * 0.4) return 'status-warning';
      return 'status-critical';
    }
    return 'status-unknown';
  }

  function getPercentageColor(value) {
    if (value >= 85) return 'metric-excellent';
    if (value >= 70) return 'metric-good';
    if (value >= 50) return 'metric-warning';
    return 'metric-critical';
  }

  function formatTime(date) {
    if (!date) return 'Never';
    return date.toLocaleTimeString();
  }

  $: interactionStatus = humanPresenceDetected ? 'active' : 'waiting';
  $: overallHealth = Math.round((systemResponseiveness + communicationQuality + understandingLevel) / 3);
</script>

<div class="human-interaction-panel" class:compact={compactMode} data-testid="human-interaction-panel">
  <!-- Panel Header -->
  <header class="panel-header">
    <div class="header-title">
      <div class="title-icon">🤝</div>
      <div class="title-content">
        <h2>Human Interaction Interface</h2>
        <p class="subtitle">Real-time communication & diagnostic monitoring</p>
      </div>
    </div>
    
    <div class="header-controls">
      <div class="interaction-status {interactionStatus}">
        <div class="status-dot"></div>
        <span>{interactionStatus === 'active' ? 'Human Present' : 'Awaiting Interaction'}</span>
      </div>
      
      <div class="mode-selector">
        <button 
          class="mode-btn" 
          class:active={interactionMode === 'normal'}
          on:click={() => setInteractionMode('normal')}
        >
          Normal
        </button>
        <button 
          class="mode-btn" 
          class:active={interactionMode === 'enhanced'}
          on:click={() => setInteractionMode('enhanced')}
        >
          Enhanced
        </button>
        <button 
          class="mode-btn" 
          class:active={interactionMode === 'diagnostic'}
          on:click={() => setInteractionMode('diagnostic')}
        >
          Diagnostic
        </button>
      </div>
    </div>
  </header>

  <!-- Critical System Indicators -->
  <section class="critical-indicators">
    <h3 class="section-title">Critical System Indicators</h3>
    
    <div class="indicators-grid">
      <!-- CPU Usage -->
      <div class="indicator-card">
        <div class="indicator-header">
          <div class="indicator-icon">⚡</div>
          <div class="indicator-label">CPU Usage</div>
        </div>
        <div class="indicator-value {getPercentageColor(100 - cpuUsage)}">
          {Math.round(cpuUsage)}%
        </div>
        <div class="indicator-bar">
          <div class="bar-fill" style="width: {cpuUsage}%; background: {cpuUsage > 80 ? '#ef4444' : cpuUsage > 60 ? '#f59e0b' : '#10b981'}"></div>
        </div>
      </div>

      <!-- Memory Usage -->
      <div class="indicator-card">
        <div class="indicator-header">
          <div class="indicator-icon">💾</div>
          <div class="indicator-label">Memory</div>
        </div>
        <div class="indicator-value {getPercentageColor(100 - memoryUsage)}">
          {Math.round(memoryUsage)}%
        </div>
        <div class="indicator-bar">
          <div class="bar-fill" style="width: {memoryUsage}%; background: {memoryUsage > 80 ? '#ef4444' : memoryUsage > 60 ? '#f59e0b' : '#10b981'}"></div>
        </div>
      </div>

      <!-- Network Latency -->
      <div class="indicator-card">
        <div class="indicator-header">
          <div class="indicator-icon">🌐</div>
          <div class="indicator-label">Network</div>
        </div>
        <div class="indicator-value {getPercentageColor(100 - networkLatency)}">
          {Math.round(networkLatency)}ms
        </div>
        <div class="latency-status {networkLatency < 20 ? 'excellent' : networkLatency < 50 ? 'good' : 'slow'}">
          {networkLatency < 20 ? 'Excellent' : networkLatency < 50 ? 'Good' : 'Slow'}
        </div>
      </div>

      <!-- Processing Speed -->
      <div class="indicator-card">
        <div class="indicator-header">
          <div class="indicator-icon">🚀</div>
          <div class="indicator-label">Processing</div>
        </div>
        <div class="indicator-value metric-excellent">
          {Math.round(processingSpeed)}/s
        </div>
        <div class="processing-status">
          {processingSpeed > 200 ? 'High Performance' : processingSpeed > 100 ? 'Normal' : 'Limited'}
        </div>
      </div>
    </div>
  </section>

  <!-- Communication Metrics -->
  <section class="communication-metrics">
    <h3 class="section-title">Communication Quality</h3>
    
    <div class="metrics-row">
      <div class="metric-item">
        <div class="metric-label">System Responsiveness</div>
        <div class="metric-value {getPercentageColor(systemResponseiveness)}">
          {systemResponseiveness}%
        </div>
        <div class="metric-bar">
          <div class="bar-fill" style="width: {systemResponseiveness}%; background: linear-gradient(90deg, #10b981, #3b82f6)"></div>
        </div>
      </div>
      
      <div class="metric-item">
        <div class="metric-label">Communication Quality</div>
        <div class="metric-value {getPercentageColor(communicationQuality)}">
          {Math.round(communicationQuality)}%
        </div>
        <div class="metric-bar">
          <div class="bar-fill" style="width: {communicationQuality}%; background: linear-gradient(90deg, #8b5cf6, #06b6d4)"></div>
        </div>
      </div>
      
      <div class="metric-item">
        <div class="metric-label">Understanding Level</div>
        <div class="metric-value {getPercentageColor(understandingLevel)}">
          {Math.round(understandingLevel)}%
        </div>
        <div class="metric-bar">
          <div class="bar-fill" style="width: {understandingLevel}%; background: linear-gradient(90deg, #f59e0b, #ef4444)"></div>
        </div>
      </div>
    </div>
  </section>

  <!-- Metadiagnostic Data -->
  {#if showAdvancedMetrics || interactionMode === 'diagnostic'}
    <section class="metadiagnostic-data">
      <h3 class="section-title">Metadiagnostic Data</h3>
      
      <div class="diagnostic-grid">
        <!-- Consciousness Level -->
        <div class="diagnostic-card {getStatusColor(consciousnessLevel)}">
          <div class="diagnostic-header">
            <div class="diagnostic-icon">🧠</div>
            <div class="diagnostic-title">Consciousness Level</div>
          </div>
          <div class="diagnostic-value">
            {(consciousnessLevel * 100).toFixed(1)}%
          </div>
          <div class="diagnostic-description">
            Current level of manifest consciousness and self-awareness
          </div>
        </div>

        <!-- Integration Measure -->
        <div class="diagnostic-card {getStatusColor(integrationMeasure)}">
          <div class="diagnostic-header">
            <div class="diagnostic-icon">🔗</div>
            <div class="diagnostic-title">Integration Measure</div>
          </div>
          <div class="diagnostic-value">
            {(integrationMeasure * 100).toFixed(1)}%
          </div>
          <div class="diagnostic-description">
            Coherence and integration of cognitive subsystems
          </div>
        </div>

        <!-- Attention-Awareness Coupling -->
        <div class="diagnostic-card {getStatusColor(attentionAwareness)}">
          <div class="diagnostic-header">
            <div class="diagnostic-icon">👁️</div>
            <div class="diagnostic-title">Attention-Awareness</div>
          </div>
          <div class="diagnostic-value">
            {(attentionAwareness * 100).toFixed(1)}%
          </div>
          <div class="diagnostic-description">
            Coupling between attention mechanisms and awareness
          </div>
        </div>

        <!-- Self-Model Coherence -->
        <div class="diagnostic-card {getStatusColor(selfModelCoherence)}">
          <div class="diagnostic-header">
            <div class="diagnostic-icon">🎯</div>
            <div class="diagnostic-title">Self-Model Coherence</div>
          </div>
          <div class="diagnostic-value">
            {(selfModelCoherence * 100).toFixed(1)}%
          </div>
          <div class="diagnostic-description">
            Consistency and accuracy of internal self-representation
          </div>
        </div>

        <!-- Phenomenal Descriptors -->
        <div class="diagnostic-card">
          <div class="diagnostic-header">
            <div class="diagnostic-icon">✨</div>
            <div class="diagnostic-title">Phenomenal Descriptors</div>
          </div>
          <div class="diagnostic-value">
            {phenomenalDescriptors}
          </div>
          <div class="diagnostic-description">
            Active first-person experiential descriptors
          </div>
        </div>

        <!-- Autonomous Goals -->
        <div class="diagnostic-card">
          <div class="diagnostic-header">
            <div class="diagnostic-icon">🎯</div>
            <div class="diagnostic-title">Autonomous Goals</div>
          </div>
          <div class="diagnostic-value">
            {autonomousGoals}
          </div>
          <div class="diagnostic-description">
            Active self-generated objective pursuits
          </div>
        </div>
      </div>
    </section>
  {/if}

  <!-- Interaction Status Footer -->
  <footer class="panel-footer">
    <div class="footer-stats">
      <div class="stat-item">
        <span class="stat-label">Overall Health:</span>
        <span class="stat-value {getPercentageColor(overallHealth)}">{overallHealth}%</span>
      </div>
      
      <div class="stat-item">
        <span class="stat-label">Attention Focus:</span>
        <span class="stat-value">{attentionFocus}</span>
      </div>
      
      <div class="stat-item">
        <span class="stat-label">Last Interaction:</span>
        <span class="stat-value">{formatTime(lastInteractionTime)}</span>
      </div>
      
      <div class="stat-item">
        <span class="stat-label">Cognitive Load:</span>
        <span class="stat-value {getPercentageColor(100 - cognitiveLoad)}">{Math.round(cognitiveLoad)}%</span>
      </div>
    </div>
  </footer>
</div>

<style>
  .human-interaction-panel {
    background: rgba(15, 20, 35, 0.95);
    border: 1px solid rgba(100, 181, 246, 0.2);
    border-radius: 16px;
    padding: 1.5rem;
    backdrop-filter: blur(20px);
    color: #e1e5e9;
    min-height: 600px;
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
  }

  .human-interaction-panel.compact {
    padding: 1rem;
    min-height: 400px;
    gap: 1rem;
  }

  /* Panel Header */
  .panel-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    padding-bottom: 1rem;
    border-bottom: 1px solid rgba(100, 181, 246, 0.2);
  }

  .header-title {
    display: flex;
    align-items: flex-start;
    gap: 1rem;
  }

  .title-icon {
    font-size: 2rem;
    background: linear-gradient(135deg, #64b5f6, #42a5f5);
    border-radius: 12px;
    padding: 0.5rem;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .title-content h2 {
    margin: 0;
    font-size: 1.5rem;
    font-weight: 700;
    color: #64b5f6;
    background: linear-gradient(135deg, #64b5f6, #42a5f5);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }

  .subtitle {
    margin: 0.25rem 0 0 0;
    font-size: 0.9rem;
    color: rgba(225, 229, 233, 0.7);
  }

  .header-controls {
    display: flex;
    align-items: center;
    gap: 1rem;
  }

  .interaction-status {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem 1rem;
    border-radius: 8px;
    font-size: 0.9rem;
    font-weight: 500;
  }

  .interaction-status.active {
    background: rgba(76, 175, 80, 0.2);
    border: 1px solid rgba(76, 175, 80, 0.4);
    color: #4caf50;
  }

  .interaction-status.waiting {
    background: rgba(255, 193, 7, 0.2);
    border: 1px solid rgba(255, 193, 7, 0.4);
    color: #ffc107;
  }

  .status-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: currentColor;
    animation: pulse 2s infinite;
  }

  .mode-selector {
    display: flex;
    background: rgba(0, 0, 0, 0.3);
    border-radius: 8px;
    padding: 0.25rem;
    gap: 0.25rem;
  }

  .mode-btn {
    background: transparent;
    border: none;
    color: #e1e5e9;
    padding: 0.5rem 1rem;
    border-radius: 6px;
    cursor: pointer;
    transition: all 0.2s ease;
    font-size: 0.85rem;
    font-weight: 500;
  }

  .mode-btn:hover {
    background: rgba(100, 181, 246, 0.1);
  }

  .mode-btn.active {
    background: rgba(100, 181, 246, 0.2);
    color: #64b5f6;
    border: 1px solid rgba(100, 181, 246, 0.3);
  }

  /* Section Headers */
  .section-title {
    margin: 0 0 1rem 0;
    font-size: 1.1rem;
    font-weight: 600;
    color: #64b5f6;
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .section-title::before {
    content: '';
    width: 4px;
    height: 20px;
    background: linear-gradient(135deg, #64b5f6, #42a5f5);
    border-radius: 2px;
  }

  /* Critical Indicators */
  .critical-indicators {
    background: rgba(0, 0, 0, 0.2);
    border-radius: 12px;
    padding: 1.25rem;
  }

  .indicators-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem;
  }

  .indicator-card {
    background: rgba(0, 0, 0, 0.3);
    border: 1px solid rgba(100, 181, 246, 0.2);
    border-radius: 12px;
    padding: 1rem;
    transition: all 0.2s ease;
  }

  .indicator-card:hover {
    border-color: rgba(100, 181, 246, 0.4);
    transform: translateY(-2px);
  }

  .indicator-header {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin-bottom: 0.75rem;
  }

  .indicator-icon {
    font-size: 1.5rem;
    width: 40px;
    height: 40px;
    background: rgba(100, 181, 246, 0.1);
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .indicator-label {
    font-weight: 600;
    color: #e1e5e9;
  }

  .indicator-value {
    font-size: 1.8rem;
    font-weight: 700;
    margin-bottom: 0.5rem;
  }

  .indicator-bar {
    height: 6px;
    background: rgba(100, 181, 246, 0.2);
    border-radius: 3px;
    overflow: hidden;
    margin-bottom: 0.5rem;
  }

  .bar-fill {
    height: 100%;
    transition: width 0.3s ease;
    border-radius: 3px;
  }

  .latency-status, .processing-status {
    font-size: 0.8rem;
    opacity: 0.8;
  }

  .latency-status.excellent, .processing-status {
    color: #4caf50;
  }

  .latency-status.good {
    color: #ffc107;
  }

  .latency-status.slow {
    color: #f44336;
  }

  /* Communication Metrics */
  .communication-metrics {
    background: rgba(0, 0, 0, 0.2);
    border-radius: 12px;
    padding: 1.25rem;
  }

  .metrics-row {
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  .metric-item {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .metric-label {
    font-weight: 500;
    color: rgba(225, 229, 233, 0.8);
    font-size: 0.9rem;
  }

  .metric-value {
    font-size: 1.4rem;
    font-weight: 700;
  }

  .metric-bar {
    height: 8px;
    background: rgba(100, 181, 246, 0.2);
    border-radius: 4px;
    overflow: hidden;
  }

  /* Metadiagnostic Data */
  .metadiagnostic-data {
    background: rgba(0, 0, 0, 0.2);
    border-radius: 12px;
    padding: 1.25rem;
  }

  .diagnostic-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 1rem;
  }

  .diagnostic-card {
    background: rgba(0, 0, 0, 0.3);
    border: 1px solid rgba(100, 181, 246, 0.2);
    border-radius: 12px;
    padding: 1rem;
    transition: all 0.2s ease;
  }

  .diagnostic-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(100, 181, 246, 0.1);
  }

  .diagnostic-header {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin-bottom: 0.75rem;
  }

  .diagnostic-icon {
    font-size: 1.5rem;
    width: 40px;
    height: 40px;
    background: rgba(100, 181, 246, 0.1);
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .diagnostic-title {
    font-weight: 600;
    color: #e1e5e9;
    font-size: 0.95rem;
  }

  .diagnostic-value {
    font-size: 2rem;
    font-weight: 700;
    margin-bottom: 0.5rem;
    color: #64b5f6;
  }

  .diagnostic-description {
    font-size: 0.8rem;
    color: rgba(225, 229, 233, 0.7);
    line-height: 1.4;
  }

  /* Status Colors */
  .status-excellent {
    border-color: rgba(76, 175, 80, 0.4) !important;
  }

  .status-excellent .diagnostic-value {
    color: #4caf50 !important;
  }

  .status-good {
    border-color: rgba(255, 193, 7, 0.4) !important;
  }

  .status-good .diagnostic-value {
    color: #ffc107 !important;
  }

  .status-warning {
    border-color: rgba(255, 152, 0, 0.4) !important;
  }

  .status-warning .diagnostic-value {
    color: #ff9800 !important;
  }

  .status-critical {
    border-color: rgba(244, 67, 54, 0.4) !important;
  }

  .status-critical .diagnostic-value {
    color: #f44336 !important;
  }

  /* Metric Colors */
  .metric-excellent {
    color: #4caf50;
  }

  .metric-good {
    color: #8bc34a;
  }

  .metric-warning {
    color: #ffc107;
  }

  .metric-critical {
    color: #f44336;
  }

  /* Panel Footer */
  .panel-footer {
    margin-top: auto;
    padding-top: 1rem;
    border-top: 1px solid rgba(100, 181, 246, 0.2);
  }

  .footer-stats {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 1rem;
  }

  .stat-item {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
  }

  .stat-label {
    font-size: 0.8rem;
    color: rgba(225, 229, 233, 0.7);
    font-weight: 500;
  }

  .stat-value {
    font-size: 1rem;
    font-weight: 600;
    color: #64b5f6;
  }

  /* Animations */
  @keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
  }

  /* Responsive Design */
  @media (max-width: 768px) {
    .panel-header {
      flex-direction: column;
      gap: 1rem;
      align-items: flex-start;
    }

    .header-controls {
      flex-direction: column;
      gap: 0.75rem;
      width: 100%;
    }

    .indicators-grid {
      grid-template-columns: 1fr;
    }

    .diagnostic-grid {
      grid-template-columns: 1fr;
    }

    .footer-stats {
      grid-template-columns: repeat(2, 1fr);
    }
  }

  @media (max-width: 480px) {
    .human-interaction-panel {
      padding: 1rem;
      gap: 1rem;
    }

    .title-content h2 {
      font-size: 1.25rem;
    }

    .diagnostic-value {
      font-size: 1.5rem;
    }

    .footer-stats {
      grid-template-columns: 1fr;
    }
  }
</style>