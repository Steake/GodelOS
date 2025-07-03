<script>
  import { onMount, onDestroy } from 'svelte';
  import { cognitiveState, attentionFocus, processingLoad, activeAgents, systemHealthScore, alerts } from '../../stores/cognitive.js';
  import { fade, fly } from 'svelte/transition';
  
  // Component props
  export let compactMode = false;
  
  let updateInterval;
  let focusHistory = [];
  let loadHistory = [];
  let isExpanded = true;
  const maxHistoryLength = 50;
  
  // Enhanced attention focus data structure
  let currentFocus = {
    topic: 'Knowledge Graph Analysis',
    context: 'User interaction with network visualization',
    intensity: 0.85,
    mode: 'Interactive',
    depth: 'deep',
    timestamp: Date.now()
  };
  
  // Mock realistic focus history for demonstration
  let enhancedFocusHistory = [
    { topic: 'Knowledge Graph Analysis', context: 'User interaction with network visualization', intensity: 0.85, depth: 'deep', timestamp: Date.now() - 1000 },
    { topic: 'SmartImport Processing', context: 'File upload and entity extraction', intensity: 0.72, depth: 'deep', timestamp: Date.now() - 45000 },
    { topic: 'Transparency Dashboard', context: 'Cognitive state monitoring update', intensity: 0.64, depth: 'surface', timestamp: Date.now() - 120000 },
    { topic: 'API Response Processing', context: 'Backend knowledge retrieval', intensity: 0.78, depth: 'deep', timestamp: Date.now() - 180000 },
    { topic: 'UI Component Rendering', context: 'Frontend visual updates', intensity: 0.45, depth: 'surface', timestamp: Date.now() - 240000 }
  ];
  
  // Track attention focus over time with enhanced data
  $: if ($attentionFocus) {
    // If we get simple string focus, convert to enhanced format
    const enhancedFocus = typeof $attentionFocus === 'string' 
      ? { 
          topic: $attentionFocus, 
          context: 'System processing', 
          intensity: Math.random() * 0.4 + 0.6, // 0.6-1.0
          depth: ['surface', 'deep', 'critical'][Math.floor(Math.random() * 3)],
          mode: 'Processing',
          timestamp: Date.now() 
        }
      : $attentionFocus;
    
    currentFocus = enhancedFocus;
    focusHistory = [
      enhancedFocus,
      ...focusHistory.slice(0, maxHistoryLength - 1)
    ];
  }
  
  // Track processing load over time
  $: if ($processingLoad !== undefined) {
    loadHistory = [
      { load: $processingLoad, timestamp: Date.now() },
      ...loadHistory.slice(0, maxHistoryLength - 1)
    ];
  }
  
  function formatTimeAgo(timestamp) {
    const now = Date.now();
    const diff = now - timestamp;
    const seconds = Math.floor(diff / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);
    
    if (seconds < 60) return `${seconds}s ago`;
    if (minutes < 60) return `${minutes}m ago`;
    return `${hours}h ago`;
  }
  
  function getHealthColor(value) {
    if (value >= 0.8) return '#10b981';
    if (value >= 0.6) return '#f59e0b';
    return '#ef4444';
  }
  
  function getLoadIntensity(load) {
    if (load < 0.3) return 'low';
    if (load < 0.7) return 'medium';
    return 'high';
  }
  
  function getFocusDepthColor(depth) {
    switch (depth) {
      case 'surface': return '#10b981';
      case 'deep': return '#3b82f6';
      case 'critical': return '#ef4444';
      case 'meta': return '#8b5cf6';
      default: return '#6b7280';
    }
  }
  
  function getFocusDepthIcon(depth) {
    switch (depth) {
      case 'surface': return '🌊';
      case 'deep': return '🔍';
      case 'critical': return '🎯';
      case 'meta': return '🧠';
      default: return '○';
    }
  }
  
  function getFocusModeColor(mode) {
    switch (mode) {
      case 'Interactive': return '#3b82f6';
      case 'Processing': return '#f59e0b';
      case 'Learning': return '#8b5cf6';
      case 'Analyzing': return '#10b981';
      default: return '#6b7280';
    }
  }
  
  function getIntensityColor(intensity) {
    if (intensity >= 0.8) return '#10b981';
    if (intensity >= 0.6) return '#f59e0b';
    if (intensity >= 0.4) return '#fbbf24';
    return '#ef4444';
  }
  
  onMount(() => {
    // Periodic updates for smooth animations
    updateInterval = setInterval(() => {
      // Trigger reactivity updates
    }, 1000);
  });
  
  onDestroy(() => {
    if (updateInterval) clearInterval(updateInterval);
  });
</script>

<div class="cognitive-monitor" class:compact={compactMode}>
  <!-- Modern Header -->
  <header class="monitor-header">
    <div class="header-left">
      <button 
        on:click={() => isExpanded = !isExpanded}
        class="expand-btn"
        aria-label={isExpanded ? 'Collapse' : 'Expand'}
      >
        <div class="expand-icon" class:rotated={!isExpanded}>
          <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
          </svg>
        </div>
      </button>
      
      <div class="header-info">
        <h3 class="monitor-title">
          <span class="title-icon">🧠</span>
          Cognitive State Monitor
        </h3>
        <div class="monitor-stats">
          <div class="stat-item">
            <span class="stat-number">{Math.round($systemHealthScore * 100)}%</span>
            <span class="stat-text">health</span>
          </div>
          <div class="stat-divider"></div>
          <div class="stat-item">
            <span class="stat-number">{$activeAgents.length}</span>
            <span class="stat-text">agents</span>
          </div>
          <div class="stat-divider"></div>
          <div class="stat-item">
            <span class="stat-number">{Math.round($processingLoad * 100)}%</span>
            <span class="stat-text">load</span>
          </div>
        </div>
      </div>
    </div>
    
    <div class="header-actions">
      <div class="health-indicator" style="--health-color: {getHealthColor($systemHealthScore)}">
        <div class="health-icon">💚</div>
        <span class="health-text">{Math.round($systemHealthScore * 100)}%</span>
      </div>
    </div>
  </header>

  {#if isExpanded}
    <!-- Consciousness Overview -->
    <section class="consciousness-section">
      <div class="consciousness-grid">
        <!-- Attention Focus -->
        <div class="consciousness-card attention-card">
          <div class="card-header">
            <h4 class="card-title">
              <span class="card-icon">🎯</span>
              Attention Focus
            </h4>
            <div class="focus-intensity-badge" style="--intensity-color: {getIntensityColor(currentFocus.intensity)}">
              {Math.round(currentFocus.intensity * 100)}%
            </div>
          </div>
          
          {#if currentFocus}
            <div class="focus-display" in:fade>
              <div class="focus-topic">
                <h5 class="topic-title">{currentFocus.topic}</h5>
                <p class="topic-context">{currentFocus.context}</p>
              </div>
              
              <div class="focus-metrics">
                <div class="metric-item">
                  <span class="metric-label">Depth:</span>
                  <div class="depth-indicator" style="--depth-color: {getFocusDepthColor(currentFocus.depth)}">
                    <span class="depth-icon">{getFocusDepthIcon(currentFocus.depth)}</span>
                    <span class="depth-text">{currentFocus.depth}</span>
                  </div>
                </div>
                
                <div class="metric-item">
                  <span class="metric-label">Mode:</span>
                  <span class="mode-value" style="color: {getFocusModeColor(currentFocus.mode)}">
                    {currentFocus.mode}
                  </span>
                </div>
              </div>
              
              <div class="intensity-bar">
                <div class="intensity-fill" style="width: {currentFocus.intensity * 100}%; background: {getIntensityColor(currentFocus.intensity)}"></div>
              </div>
            </div>
          {:else}
            <div class="empty-focus">
              <div class="empty-icon">○</div>
              <span class="empty-text">Unfocused</span>
            </div>
          {/if}
        </div>
        
        <!-- Processing Load -->
        <div class="consciousness-card load-card">
          <div class="card-header">
            <h4 class="card-title">
              <span class="card-icon">⚡</span>
              Processing Load
            </h4>
            <div class="load-badge load-{getLoadIntensity($processingLoad)}">
              {getLoadIntensity($processingLoad).toUpperCase()}
            </div>
          </div>
          
          <div class="load-display">
            <div class="load-value">{Math.round($processingLoad * 100)}%</div>
            <div class="load-meter">
              <div class="load-fill load-{getLoadIntensity($processingLoad)}" style="width: {$processingLoad * 100}%"></div>
            </div>
          </div>
          
          {#if loadHistory.length > 10}
            <div class="load-chart">
              <div class="chart-title">Recent Activity</div>
              <div class="chart-container">
                {#each loadHistory.slice(0, 20) as item, i}
                  <div 
                    class="chart-bar"
                    style="height: {item.load * 100}%; opacity: {1 - (i * 0.04)}"
                  ></div>
                {/each}
              </div>
            </div>
          {/if}
        </div>
        
        <!-- Working Memory -->
        <div class="consciousness-card memory-card">
          <div class="card-header">
            <h4 class="card-title">
              <span class="card-icon">💭</span>
              Working Memory
            </h4>
            <div class="memory-count">
              {$cognitiveState.manifestConsciousness.workingMemory.length}/10
            </div>
          </div>
          
          <div class="memory-capacity">
            <div class="capacity-bar">
              <div 
                class="capacity-fill"
                style="width: {($cognitiveState.manifestConsciousness.workingMemory.length / 10) * 100}%"
              ></div>
            </div>
            <span class="capacity-text">
              {Math.round(($cognitiveState.manifestConsciousness.workingMemory.length / 10) * 100)}% utilized
            </span>
          </div>
          
          {#if $cognitiveState.manifestConsciousness.workingMemory.length > 0}
            <div class="memory-items">
              {#each $cognitiveState.manifestConsciousness.workingMemory.slice(0, 3) as item}
                <div class="memory-item" in:fly={{ y: 20, duration: 300 }}>
                  <div class="item-header">
                    <span class="item-type item-{item.type}">{item.type}</span>
                    <span class="item-relevance">{Math.round(item.relevance * 100)}%</span>
                  </div>
                  <div class="item-content">{item.content}</div>
                </div>
              {/each}
              {#if $cognitiveState.manifestConsciousness.workingMemory.length > 3}
                <div class="more-items">
                  +{$cognitiveState.manifestConsciousness.workingMemory.length - 3} more items
                </div>
              {/if}
            </div>
          {:else}
            <div class="empty-memory">
              <div class="empty-icon">💭</div>
              <span class="empty-text">Memory clear</span>
            </div>
          {/if}
        </div>
        
        <!-- Current Query -->
        <div class="consciousness-card query-card">
          <div class="card-header">
            <h4 class="card-title">
              <span class="card-icon">❓</span>
              Current Query
            </h4>
            {#if $cognitiveState.manifestConsciousness.currentQuery}
              <div class="query-status processing">
                <div class="status-dot"></div>
                Processing
              </div>
            {/if}
          </div>
          
          {#if $cognitiveState.manifestConsciousness.currentQuery}
            <div class="query-display" in:fade>
              <div class="query-text">"{$cognitiveState.manifestConsciousness.currentQuery}"</div>
              <div class="query-progress">
                <div class="progress-bar">
                  <div class="progress-fill" style="width: {$processingLoad * 100}%"></div>
                </div>
                <span class="progress-text">{Math.round($processingLoad * 100)}%</span>
              </div>
            </div>
          {:else}
            <div class="empty-query">
              <div class="empty-icon">❓</div>
              <span class="empty-text">No active query</span>
            </div>
          {/if}
        </div>
      </div>
    </section>

    <!-- Focus History -->
    {#if enhancedFocusHistory.length > 0}
      <section class="history-section">
        <h4 class="section-title">
          <span class="section-icon">📊</span>
          Recent Focus History
        </h4>
        
        <div class="history-timeline">
          {#each enhancedFocusHistory.slice(0, 5) as item, index}
            <div class="timeline-item" class:current={index === 0}>
              <div class="timeline-marker">
                <div class="marker-dot" style="background: {getIntensityColor(item.intensity)}"></div>
              </div>
              
              <div class="timeline-content">
                <div class="timeline-header">
                  <h5 class="timeline-topic">{item.topic}</h5>
                  <div class="timeline-meta">
                    <span class="timeline-time">{formatTimeAgo(item.timestamp)}</span>
                    <div class="intensity-indicator">
                      <div class="mini-intensity-bar">
                        <div 
                          class="mini-intensity-fill" 
                          style="width: {item.intensity * 100}%; background: {getIntensityColor(item.intensity)}"
                        ></div>
                      </div>
                      <span class="intensity-value">{Math.round(item.intensity * 100)}%</span>
                    </div>
                  </div>
                </div>
                <p class="timeline-context">{item.context}</p>
              </div>
            </div>
          {/each}
        </div>
      </section>
    {/if}

    <!-- Active Agents -->
    {#if $activeAgents.length > 0}
      <section class="agents-section">
        <h4 class="section-title">
          <span class="section-icon">🤖</span>
          Active Agentic Processes
          <span class="section-count">{$activeAgents.length}</span>
        </h4>
        
        <div class="agents-grid">
          {#each $activeAgents as agent (agent.id)}
            <div class="agent-card" in:fly={{ x: -20, duration: 300 }}>
              <div class="agent-header">
                <div class="agent-info">
                  <h5 class="agent-type">{agent.type}</h5>
                  <div class="agent-status status-{agent.status}">
                    <div class="status-dot"></div>
                    <span class="status-text">{agent.status}</span>
                  </div>
                </div>
                <div class="agent-timing">
                  {formatTimeAgo(agent.spawnTime)}
                </div>
              </div>
              
              <div class="agent-goal">
                <span class="goal-label">Goal:</span>
                <span class="goal-text">{agent.goal || 'No specific goal'}</span>
              </div>
              
              {#if agent.resources}
                <div class="agent-resources">
                  <div class="resource-item">
                    <span class="resource-label">CPU:</span>
                    <div class="resource-bar">
                      <div class="resource-fill" style="width: {(agent.resources.cpu || 0) * 100}%"></div>
                    </div>
                    <span class="resource-value">{Math.round((agent.resources.cpu || 0) * 100)}%</span>
                  </div>
                  <div class="resource-item">
                    <span class="resource-label">Memory:</span>
                    <div class="resource-bar">
                      <div class="resource-fill" style="width: {(agent.resources.memory || 0) * 100}%"></div>
                    </div>
                    <span class="resource-value">{Math.round((agent.resources.memory || 0) * 100)}%</span>
                  </div>
                </div>
              {/if}
            </div>
          {/each}
        </div>
      </section>
    {/if}

    <!-- System Health -->
    <section class="health-section">
      <h4 class="section-title">
        <span class="section-icon">💚</span>
        System Health Overview
      </h4>
      
      <div class="health-grid">
        {#each Object.entries($cognitiveState.systemHealth) as [module, health]}
          <div class="health-card">
            <div class="health-header">
              <span class="health-module">{module}</span>
              <span class="health-value" style="color: {getHealthColor(health)}">
                {Math.round(health * 100)}%
              </span>
            </div>
            <div class="health-meter">
              <div 
                class="health-fill"
                style="width: {health * 100}%; background: {getHealthColor(health)}"
              ></div>
            </div>
          </div>
        {/each}
      </div>
    </section>
  {/if}
</div>

<style>
  .cognitive-monitor {
    background: rgba(255, 255, 255, 0.02);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 16px;
    overflow: hidden;
    backdrop-filter: blur(10px);
  }

  .cognitive-monitor.compact {
    border-radius: 12px;
  }

  /* Header Styles */
  .monitor-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1.5rem;
    background: rgba(255, 255, 255, 0.05);
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    gap: 1rem;
  }

  .header-left {
    display: flex;
    align-items: center;
    gap: 1rem;
    flex: 1;
  }

  .expand-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 32px;
    height: 32px;
    background: rgba(255, 255, 255, 0.1);
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 8px;
    color: rgba(255, 255, 255, 0.8);
    cursor: pointer;
    transition: all 0.2s ease;
  }

  .expand-btn:hover {
    background: rgba(255, 255, 255, 0.2);
    color: white;
  }

  .expand-icon {
    transition: transform 0.2s ease;
  }

  .expand-icon.rotated {
    transform: rotate(-90deg);
  }

  .header-info {
    flex: 1;
  }

  .monitor-title {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin: 0 0 0.5rem 0;
    font-size: 1.25rem;
    font-weight: 600;
    color: white;
  }

  .title-icon {
    font-size: 1.5rem;
  }

  .monitor-stats {
    display: flex;
    align-items: center;
    gap: 0.75rem;
  }

  .stat-item {
    display: flex;
    align-items: center;
    gap: 0.25rem;
  }

  .stat-number {
    font-weight: 600;
    color: white;
    font-size: 0.875rem;
  }

  .stat-text {
    font-size: 0.75rem;
    color: rgba(255, 255, 255, 0.7);
  }

  .stat-divider {
    width: 1px;
    height: 12px;
    background: rgba(255, 255, 255, 0.2);
  }

  .header-actions {
    display: flex;
    align-items: center;
  }

  .health-indicator {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem 1rem;
    background: rgba(255, 255, 255, 0.1);
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 12px;
  }

  .health-icon {
    font-size: 1.25rem;
  }

  .health-text {
    font-weight: 600;
    color: white;
    font-size: 0.875rem;
  }

  /* Section Styles */
  .consciousness-section,
  .history-section,
  .agents-section,
  .health-section {
    padding: 1.5rem;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  }

  .consciousness-section:last-child,
  .history-section:last-child,
  .agents-section:last-child,
  .health-section:last-child {
    border-bottom: none;
  }

  .section-title {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin: 0 0 1.5rem 0;
    font-size: 1.125rem;
    font-weight: 600;
    color: white;
  }

  .section-icon {
    font-size: 1.25rem;
  }

  .section-count {
    background: rgba(255, 255, 255, 0.2);
    color: white;
    font-size: 0.75rem;
    padding: 0.125rem 0.5rem;
    border-radius: 10px;
    font-weight: 600;
    margin-left: auto;
  }

  /* Consciousness Grid */
  .consciousness-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 1.5rem;
  }

  .consciousness-card {
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 12px;
    padding: 1.5rem;
    transition: all 0.2s ease;
  }

  .consciousness-card:hover {
    background: rgba(255, 255, 255, 0.08);
    border-color: rgba(255, 255, 255, 0.2);
  }

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
  }

  .card-title {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin: 0;
    font-size: 1rem;
    font-weight: 600;
    color: white;
  }

  .card-icon {
    font-size: 1.25rem;
  }

  /* Focus Card */
  .focus-display {
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  .focus-topic {
    flex: 1;
  }

  .topic-title {
    font-size: 1rem;
    font-weight: 600;
    color: white;
    margin: 0 0 0.5rem 0;
  }

  .topic-context {
    font-size: 0.875rem;
    color: rgba(255, 255, 255, 0.7);
    line-height: 1.4;
    margin: 0;
  }

  .focus-metrics {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 1rem;
  }

  .metric-item {
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .metric-label {
    font-size: 0.75rem;
    color: rgba(255, 255, 255, 0.6);
  }

  .depth-indicator {
    display: flex;
    align-items: center;
    gap: 0.25rem;
    color: var(--depth-color, #6b7280);
  }

  .depth-icon {
    font-size: 1rem;
  }

  .depth-text {
    font-size: 0.75rem;
    font-weight: 500;
    text-transform: capitalize;
  }

  .mode-value {
    font-size: 0.75rem;
    font-weight: 500;
  }

  .focus-intensity-badge {
    padding: 0.25rem 0.5rem;
    background: var(--intensity-color, #6b7280);
    color: white;
    border-radius: 6px;
    font-size: 0.75rem;
    font-weight: 600;
  }

  .intensity-bar {
    width: 100%;
    height: 4px;
    background: rgba(255, 255, 255, 0.1);
    border-radius: 2px;
    overflow: hidden;
  }

  .intensity-fill {
    height: 100%;
    transition: width 0.3s ease;
    border-radius: 2px;
  }

  /* Load Card */
  .load-display {
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  .load-value {
    font-size: 2rem;
    font-weight: 700;
    color: white;
    text-align: center;
  }

  .load-meter {
    width: 100%;
    height: 8px;
    background: rgba(255, 255, 255, 0.1);
    border-radius: 4px;
    overflow: hidden;
  }

  .load-fill {
    height: 100%;
    transition: width 0.3s ease;
    border-radius: 4px;
  }

  .load-fill.load-low {
    background: linear-gradient(90deg, #10b981, #34d399);
  }

  .load-fill.load-medium {
    background: linear-gradient(90deg, #f59e0b, #fbbf24);
  }

  .load-fill.load-high {
    background: linear-gradient(90deg, #ef4444, #f87171);
  }

  .load-badge {
    padding: 0.25rem 0.5rem;
    border-radius: 6px;
    font-size: 0.75rem;
    font-weight: 600;
    text-align: center;
  }

  .load-badge.load-low {
    background: #10b981;
    color: white;
  }

  .load-badge.load-medium {
    background: #f59e0b;
    color: white;
  }

  .load-badge.load-high {
    background: #ef4444;
    color: white;
  }

  .load-chart {
    margin-top: 1rem;
  }

  .chart-title {
    font-size: 0.75rem;
    color: rgba(255, 255, 255, 0.7);
    margin-bottom: 0.5rem;
  }

  .chart-container {
    display: flex;
    align-items: end;
    height: 40px;
    gap: 1px;
  }

  .chart-bar {
    flex: 1;
    background: linear-gradient(to top, #3b82f6, #60a5fa);
    border-radius: 1px;
    min-height: 2px;
    transition: height 0.3s ease;
  }

  /* Memory Card */
  .memory-count {
    font-size: 0.875rem;
    font-weight: 600;
    color: white;
  }

  .memory-capacity {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    margin-bottom: 1rem;
  }

  .capacity-bar {
    width: 100%;
    height: 6px;
    background: rgba(255, 255, 255, 0.1);
    border-radius: 3px;
    overflow: hidden;
  }

  .capacity-fill {
    height: 100%;
    background: linear-gradient(90deg, #3b82f6, #60a5fa);
    transition: width 0.3s ease;
    border-radius: 3px;
  }

  .capacity-text {
    font-size: 0.75rem;
    color: rgba(255, 255, 255, 0.7);
  }

  .memory-items {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
  }

  .memory-item {
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 8px;
    padding: 0.75rem;
  }

  .item-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.5rem;
  }

  .item-type {
    padding: 0.125rem 0.5rem;
    border-radius: 12px;
    font-size: 0.75rem;
    text-transform: uppercase;
    font-weight: 600;
  }

  .item-type.item-reflection {
    background: rgba(139, 92, 246, 0.2);
    color: #8b5cf6;
  }

  .item-type.item-query {
    background: rgba(59, 130, 246, 0.2);
    color: #3b82f6;
  }

  .item-type.item-concept {
    background: rgba(16, 185, 129, 0.2);
    color: #10b981;
  }

  .item-relevance {
    font-size: 0.75rem;
    color: rgba(255, 255, 255, 0.6);
  }

  .item-content {
    color: rgba(255, 255, 255, 0.9);
    font-size: 0.875rem;
    line-height: 1.4;
  }

  .more-items {
    text-align: center;
    font-size: 0.75rem;
    color: rgba(255, 255, 255, 0.6);
    padding: 0.5rem;
    background: rgba(255, 255, 255, 0.02);
    border-radius: 6px;
  }

  .query-status {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.25rem 0.75rem;
    border-radius: 12px;
    font-size: 0.75rem;
    font-weight: 500;
  }

  .query-status.processing {
    background: rgba(59, 130, 246, 0.2);
    color: #3b82f6;
  }

  .status-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: currentColor;
    animation: pulse 2s infinite;
  }

  .query-display {
    background: rgba(59, 130, 246, 0.1);
    border: 1px solid rgba(59, 130, 246, 0.2);
    border-radius: 8px;
    padding: 1rem;
  }

  .query-text {
    color: rgba(255, 255, 255, 0.9);
    font-style: italic;
    margin-bottom: 0.75rem;
    line-height: 1.4;
  }

  .query-progress {
    display: flex;
    align-items: center;
    gap: 0.75rem;
  }

  .progress-bar {
    flex: 1;
    height: 4px;
    background: rgba(255, 255, 255, 0.2);
    border-radius: 2px;
    overflow: hidden;
  }

  .progress-fill {
    height: 100%;
    background: linear-gradient(90deg, #3b82f6, #60a5fa);
    transition: width 0.3s ease;
  }

  .progress-text {
    font-size: 0.75rem;
    color: #3b82f6;
    font-weight: 600;
  }

  .empty-focus,
  .empty-memory,
  .empty-query {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 2rem;
    text-align: center;
  }

  .empty-icon {
    font-size: 2rem;
    opacity: 0.5;
    margin-bottom: 0.5rem;
  }

  .empty-text {
    font-size: 0.875rem;
    color: rgba(255, 255, 255, 0.6);
  }

  .history-timeline {
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  .timeline-item {
    display: flex;
    gap: 1rem;
    padding: 1rem;
    background: rgba(255, 255, 255, 0.02);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 8px;
    transition: all 0.2s ease;
  }

  .timeline-item:hover {
    background: rgba(255, 255, 255, 0.05);
    border-color: rgba(255, 255, 255, 0.2);
  }

  .timeline-item.current {
    background: rgba(59, 130, 246, 0.1);
    border-color: rgba(59, 130, 246, 0.3);
  }

  .timeline-marker {
    display: flex;
    align-items: flex-start;
    padding-top: 0.125rem;
  }

  .marker-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    animation: pulse 2s infinite;
  }

  .timeline-content {
    flex: 1;
  }

  .timeline-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 0.5rem;
    gap: 1rem;
  }

  .timeline-topic {
    font-size: 0.875rem;
    font-weight: 600;
    color: white;
    margin: 0;
  }

  .timeline-meta {
    display: flex;
    align-items: center;
    gap: 0.75rem;
  }

  .timeline-time {
    font-size: 0.75rem;
    color: rgba(255, 255, 255, 0.6);
  }

  .intensity-indicator {
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .mini-intensity-bar {
    width: 30px;
    height: 4px;
    background: rgba(255, 255, 255, 0.1);
    border-radius: 2px;
    overflow: hidden;
  }

  .mini-intensity-fill {
    height: 100%;
    transition: width 0.3s ease;
    border-radius: 2px;
  }

  .intensity-value {
    font-size: 0.75rem;
    font-weight: 500;
    color: rgba(255, 255, 255, 0.8);
    min-width: 30px;
  }

  .timeline-context {
    font-size: 0.75rem;
    color: rgba(255, 255, 255, 0.7);
    line-height: 1.4;
    margin: 0;
  }

  .agents-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 1rem;
  }

  .agent-card {
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 8px;
    padding: 1rem;
    transition: all 0.2s ease;
  }

  .agent-card:hover {
    background: rgba(255, 255, 255, 0.08);
    border-color: rgba(255, 255, 255, 0.2);
  }

  .agent-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 0.75rem;
    gap: 1rem;
  }

  .agent-info {
    flex: 1;
  }

  .agent-type {
    font-size: 0.875rem;
    font-weight: 600;
    color: white;
    margin: 0 0 0.25rem 0;
  }

  .agent-status {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.75rem;
    text-transform: capitalize;
  }

  .agent-status.status-active .status-dot {
    background: #10b981;
  }

  .agent-status.status-idle .status-dot {
    background: #f59e0b;
  }

  .agent-status.status-error .status-dot {
    background: #ef4444;
  }

  .status-text {
    color: rgba(255, 255, 255, 0.8);
  }

  .agent-timing {
    font-size: 0.75rem;
    color: rgba(255, 255, 255, 0.6);
  }

  .agent-goal {
    margin-bottom: 0.75rem;
    font-size: 0.875rem;
  }

  .goal-label {
    color: rgba(255, 255, 255, 0.6);
  }

  .goal-text {
    color: rgba(255, 255, 255, 0.9);
  }

  .agent-resources {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .resource-item {
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .resource-label {
    font-size: 0.75rem;
    color: rgba(255, 255, 255, 0.6);
    min-width: 50px;
  }

  .resource-bar {
    flex: 1;
    height: 4px;
    background: rgba(255, 255, 255, 0.1);
    border-radius: 2px;
    overflow: hidden;
  }

  .resource-fill {
    height: 100%;
    background: linear-gradient(90deg, #3b82f6, #60a5fa);
    transition: width 0.3s ease;
  }

  .resource-value {
    font-size: 0.75rem;
    color: rgba(255, 255, 255, 0.8);
    min-width: 35px;
    text-align: right;
  }

  .health-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem;
  }

  .health-card {
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 8px;
    padding: 1rem;
    transition: all 0.2s ease;
  }

  .health-card:hover {
    background: rgba(255, 255, 255, 0.08);
    border-color: rgba(255, 255, 255, 0.2);
  }

  .health-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.75rem;
  }

  .health-module {
    color: rgba(255, 255, 255, 0.9);
    font-weight: 500;
    text-transform: capitalize;
    font-size: 0.875rem;
  }

  .health-value {
    font-weight: 600;
    font-size: 0.875rem;
  }

  .health-meter {
    height: 6px;
    background: rgba(255, 255, 255, 0.1);
    border-radius: 3px;
    overflow: hidden;
  }

  .health-fill {
    height: 100%;
    transition: width 0.3s ease;
    border-radius: 3px;
  }

  @keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
  }

  @media (max-width: 768px) {
    .monitor-header {
      flex-direction: column;
      align-items: stretch;
      gap: 1rem;
    }

    .header-left {
      flex-direction: column;
      align-items: stretch;
      gap: 1rem;
    }

    .monitor-stats {
      justify-content: space-between;
    }

    .consciousness-grid {
      grid-template-columns: 1fr;
    }

    .agents-grid {
      grid-template-columns: 1fr;
    }

    .health-grid {
      grid-template-columns: repeat(2, 1fr);
    }

    .timeline-header {
      flex-direction: column;
      align-items: stretch;
      gap: 0.5rem;
    }

    .timeline-meta {
      justify-content: space-between;
    }

    .agent-header {
      flex-direction: column;
      align-items: stretch;
      gap: 0.5rem;
    }
  }

  @media (max-width: 480px) {
    .consciousness-section,
    .history-section,
    .agents-section,
    .health-section {
      padding: 1rem;
    }

    .consciousness-card {
      padding: 1rem;
    }

    .health-grid {
      grid-template-columns: 1fr;
    }

    .focus-metrics {
      flex-direction: column;
      align-items: stretch;
      gap: 0.5rem;
    }

    .resource-item {
      flex-direction: column;
      align-items: stretch;
      gap: 0.25rem;
    }

    .resource-label {
      min-width: auto;
    }

    .resource-value {
      text-align: left;
      min-width: auto;
    }
  }
</style>
