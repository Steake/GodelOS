<script>
  import { onMount, onDestroy } from 'svelte';
  import { cognitiveState, attentionFocus, processingLoad, activeAgents, systemHealthScore, alerts } from '../../stores/cognitive.js';
  import { fade, fly } from 'svelte/transition';
  
  let updateInterval;
  let focusHistory = [];
  let loadHistory = [];
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
    if (value >= 0.8) return '#66bb6a';
    if (value >= 0.6) return '#ffa726';
    return '#ef5350';
  }
  
  function getLoadIntensity(load) {
    if (load < 0.3) return 'low';
    if (load < 0.7) return 'medium';
    return 'high';
  }
  
  function getFocusDepthColor(depth) {
    switch (depth) {
      case 'surface': return '#81c784';
      case 'deep': return '#64b5f6';
      case 'critical': return '#ef5350';
      case 'meta': return '#ba68c8';
      default: return '#90a4ae';
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
      case 'Interactive': return '#2196f3';
      case 'Processing': return '#ff9800';
      case 'Learning': return '#9c27b0';
      case 'Analyzing': return '#4caf50';
      default: return '#607d8b';
    }
  }
  
  function getIntensityColor(intensity) {
    if (intensity >= 0.8) return '#4caf50';
    if (intensity >= 0.6) return '#ff9800';
    if (intensity >= 0.4) return '#ffc107';
    return '#f44336';
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

<div class="cognitive-monitor">
  <!-- Manifest Consciousness Section -->
  <section class="consciousness-section">
    <div class="section-header">
      <h2>
        <span class="section-icon">🧠</span>
        Manifest Consciousness
      </h2>
      <div class="health-indicator">
        Health: <span style="color: {getHealthColor($systemHealthScore)}">{Math.round($systemHealthScore * 100)}%</span>
      </div>
    </div>
    
    <div class="consciousness-grid">
      <!-- Attention Focus -->
      <div class="consciousness-card attention-card">
        <h3>🧠 Attention Focus</h3>
        {#if currentFocus}
          <div class="focus-display" in:fade>
            <div class="current-focus">
              <div class="focus-topic">
                <span class="focus-label">Topic:</span>
                <span class="focus-value">{currentFocus.topic}</span>
              </div>
              
              <div class="focus-context">
                <span class="focus-label">Context:</span>
                <span class="focus-value context-text">{currentFocus.context}</span>
              </div>
              
              <div class="focus-intensity">
                <span class="focus-label">Intensity:</span>
                <div class="intensity-display">
                  <span class="intensity-value" style="color: {getIntensityColor(currentFocus.intensity)}">
                    {Math.round(currentFocus.intensity * 100)}%
                  </span>
                  <div class="intensity-bar">
                    <div 
                      class="intensity-fill" 
                      style="width: {currentFocus.intensity * 100}%; background: {getIntensityColor(currentFocus.intensity)}"
                    ></div>
                  </div>
                </div>
              </div>
              
              <div class="focus-metadata">
                <div class="focus-depth">
                  <span class="depth-icon">{getFocusDepthIcon(currentFocus.depth)}</span>
                  <span 
                    class="depth-value"
                    style="color: {getFocusDepthColor(currentFocus.depth)}"
                  >
                    {currentFocus.depth}
                  </span>
                </div>
                
                <div class="focus-mode">
                  <span class="mode-label">Mode:</span>
                  <span 
                    class="mode-value"
                    style="color: {getFocusModeColor(currentFocus.mode)}"
                  >
                    {currentFocus.mode}
                  </span>
                </div>
              </div>
            </div>
          </div>
        {:else}
          <div class="focus-empty">
            <span class="empty-icon">○</span>
            <span class="empty-text">Unfocused</span>
          </div>
        {/if}
        
        {#if enhancedFocusHistory.length > 0}
          <div class="focus-history">
            <h4>Recent Focus History</h4>
            <div class="history-list">
              {#each enhancedFocusHistory.slice(0, 5) as item, index}
                <div class="history-item" class:current={index === 0}>
                  <div class="history-main">
                    <span class="history-topic">{item.topic}</span>
                    <div class="history-meta">
                      <span class="history-time">{formatTimeAgo(item.timestamp)}</span>
                      <div class="history-intensity">
                        <div class="mini-intensity-bar">
                          <div 
                            class="mini-intensity-fill" 
                            style="width: {item.intensity * 100}%; background: {getIntensityColor(item.intensity)}"
                          ></div>
                        </div>
                        <span class="mini-intensity-value">{Math.round(item.intensity * 100)}%</span>
                      </div>
                    </div>
                  </div>
                  <div class="history-context">{item.context}</div>
                </div>
              {/each}
            </div>
          </div>
        {/if}
      </div>
      
      <!-- Processing Load -->
      <div class="consciousness-card load-card">
        <h3>Processing Load</h3>
        <div class="load-display">
          <div class="load-meter">
            <div 
              class="load-fill {getLoadIntensity($processingLoad)}"
              style="width: {$processingLoad * 100}%"
            ></div>
          </div>
          <div class="load-value">
            {Math.round($processingLoad * 100)}%
          </div>
        </div>
        
        <div class="load-classification">
          <span class="load-label">Intensity:</span>
          <span class="load-class {getLoadIntensity($processingLoad)}">
            {getLoadIntensity($processingLoad).toUpperCase()}
          </span>
        </div>
        
        {#if loadHistory.length > 10}
          <div class="load-chart">
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
        <h3>Working Memory</h3>
        <div class="memory-stats">
          <div class="memory-count">
            {$cognitiveState.manifestConsciousness.workingMemory.length} items
          </div>
          <div class="memory-capacity">
            <div class="capacity-bar">
              <div 
                class="capacity-fill"
                style="width: {($cognitiveState.manifestConsciousness.workingMemory.length / 10) * 100}%"
              ></div>
            </div>
          </div>
        </div>
        
        {#if $cognitiveState.manifestConsciousness.workingMemory.length > 0}
          <div class="memory-items">
            {#each $cognitiveState.manifestConsciousness.workingMemory.slice(0, 5) as item}
              <div class="memory-item" in:fly={{ y: 20, duration: 300 }}>
                <div class="item-type {item.type}">{item.type}</div>
                <div class="item-content">{item.content}</div>
                <div class="item-relevance">
                  Relevance: {Math.round(item.relevance * 100)}%
                </div>
              </div>
            {/each}
          </div>
        {:else}
          <div class="memory-empty">
            <span class="empty-icon">💭</span>
            <span class="empty-text">Working memory clear</span>
          </div>
        {/if}
      </div>
      
      <!-- Current Query -->
      <div class="consciousness-card query-card">
        <h3>Current Query</h3>
        {#if $cognitiveState.manifestConsciousness.currentQuery}
          <div class="query-display" in:fade>
            <div class="query-text">
              "{$cognitiveState.manifestConsciousness.currentQuery}"
            </div>
            <div class="query-progress">
              <div class="progress-bar">
                <div 
                  class="progress-fill"
                  style="width: {$processingLoad * 100}%"
                ></div>
              </div>
              <span class="progress-text">Processing...</span>
            </div>
          </div>
        {:else}
          <div class="query-empty">
            <span class="empty-icon">❓</span>
            <span class="empty-text">No active query</span>
          </div>
        {/if}
      </div>
    </div>
  </section>
  
  <!-- Agentic Processes Section -->
  <section class="agents-section">
    <div class="section-header">
      <h2>
        <span class="section-icon">🤖</span>
        Agentic Processes
      </h2>
      <div class="agent-count">
        {$activeAgents.length} active
      </div>
    </div>
    
    {#if $activeAgents.length > 0}
      <div class="agents-grid">
        {#each $activeAgents as agent (agent.id)}
          <div class="agent-card" in:fly={{ x: -20, duration: 300 }}>
            <div class="agent-header">
              <div class="agent-type">{agent.type}</div>
              <div class="agent-status {agent.status}">
                <div class="status-dot"></div>
                {agent.status}
              </div>
            </div>
            
            <div class="agent-goal">
              <strong>Goal:</strong> {agent.goal || 'No specific goal'}
            </div>
            
            {#if agent.resources}
              <div class="agent-resources">
                <div class="resource-usage">
                  CPU: {Math.round((agent.resources.cpu || 0) * 100)}%
                </div>
                <div class="resource-usage">
                  Memory: {Math.round((agent.resources.memory || 0) * 100)}%
                </div>
              </div>
            {/if}
            
            <div class="agent-timing">
              Running for: {formatTimeAgo(agent.spawnTime)}
            </div>
          </div>
        {/each}
      </div>
    {:else}
      <div class="agents-empty">
        <span class="empty-icon">🤖</span>
        <span class="empty-text">No active agentic processes</span>
        <span class="empty-subtext">Agents will spawn when needed for complex tasks</span>
      </div>
    {/if}
  </section>
  
  <!-- Daemon Threads Section -->
  <section class="daemons-section">
    <div class="section-header">
      <h2>
        <span class="section-icon">⚙️</span>
        Daemon Threads
      </h2>
      <div class="daemon-count">
        {$cognitiveState.daemonThreads.length} running
      </div>
    </div>
    
    {#if $cognitiveState.daemonThreads.length > 0}
      <div class="daemons-grid">
        {#each $cognitiveState.daemonThreads as daemon (daemon.id)}
          <div class="daemon-card">
            <div class="daemon-header">
              <div class="daemon-name">{daemon.name}</div>
              <div class="daemon-load">
                <div class="load-bar">
                  <div 
                    class="load-fill"
                    style="width: {(daemon.load || 0) * 100}%"
                  ></div>
                </div>
              </div>
            </div>
            
            <div class="daemon-activity">
              <span class="activity-label">Activity:</span>
              <span class="activity-value">{daemon.activity || 'idle'}</span>
            </div>
            
            <div class="daemon-timing">
              Last active: {formatTimeAgo(daemon.lastActivity)}
            </div>
          </div>
        {/each}
      </div>
    {:else}
      <div class="daemons-empty">
        <span class="empty-icon">⚙️</span>
        <span class="empty-text">No daemon threads active</span>
      </div>
    {/if}
  </section>
  
  <!-- System Health Overview -->
  <section class="health-section">
    <div class="section-header">
      <h2>
        <span class="section-icon">💚</span>
        System Health
      </h2>
    </div>
    
    <div class="health-grid">
      {#each Object.entries($cognitiveState.systemHealth) as [module, health]}
        <div class="health-card">
          <div class="health-module">{module}</div>
          <div class="health-meter">
            <div 
              class="health-fill"
              style="width: {health * 100}%; background: {getHealthColor(health)}"
            ></div>
          </div>
          <div class="health-value" style="color: {getHealthColor(health)}">
            {Math.round(health * 100)}%
          </div>
        </div>
      {/each}
    </div>
  </section>
</div>

<style>
  .cognitive-monitor {
    padding: 2rem;
    max-width: 1200px;
    margin: 0 auto;
  }
  
  .section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1.5rem;
    padding-bottom: 0.75rem;
    border-bottom: 1px solid rgba(100, 120, 150, 0.2);
  }
  
  .section-header h2 {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin: 0;
    font-size: 1.4rem;
    color: #e1e5e9;
  }
  
  .section-icon {
    font-size: 1.6rem;
  }
  
  .health-indicator,
  .agent-count,
  .daemon-count {
    font-size: 0.9rem;
    color: #a0a9b8;
    background: rgba(255, 255, 255, 0.05);
    padding: 0.5rem 1rem;
    border-radius: 20px;
    border: 1px solid rgba(255, 255, 255, 0.1);
  }
  
  /* Consciousness Section */
  .consciousness-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 1.5rem;
    margin-bottom: 3rem;
  }
  
  .consciousness-card {
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(100, 120, 150, 0.15);
    border-radius: 12px;
    padding: 1.5rem;
    backdrop-filter: blur(10px);
  }
  
  .consciousness-card h3 {
    margin: 0 0 1rem 0;
    color: #64b5f6;
    font-size: 1.1rem;
  }
  
  /* Enhanced Attention Focus Styles */
  .focus-display {
    margin-bottom: 1.5rem;
  }
  
  .current-focus {
    background: rgba(255, 255, 255, 0.05);
    border-radius: 12px;
    padding: 1rem;
    margin-bottom: 1rem;
    border: 1px solid rgba(255, 255, 255, 0.1);
  }
  
  .focus-topic,
  .focus-context,
  .focus-intensity {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.75rem;
  }
  
  .focus-topic:last-child,
  .focus-context:last-child,
  .focus-intensity:last-child {
    margin-bottom: 0;
  }
  
  .focus-label {
    color: #a0a9b8;
    font-size: 0.9rem;
    min-width: 70px;
  }
  
  .focus-value {
    color: #e1e5e9;
    font-weight: 500;
    flex: 1;
    text-align: right;
  }
  
  .context-text {
    font-size: 0.85rem;
    opacity: 0.9;
    font-style: italic;
  }
  
  .intensity-display {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    flex: 1;
    justify-content: flex-end;
  }
  
  .intensity-value {
    font-weight: 600;
    font-size: 0.9rem;
    min-width: 40px;
  }
  
  .intensity-bar {
    width: 60px;
    height: 6px;
    background: rgba(255, 255, 255, 0.1);
    border-radius: 3px;
    overflow: hidden;
  }
  
  .intensity-fill {
    height: 100%;
    transition: width 0.3s ease, background 0.3s ease;
    border-radius: 3px;
  }
  
  .focus-metadata {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 0.75rem;
    padding-top: 0.75rem;
    border-top: 1px solid rgba(255, 255, 255, 0.1);
  }
  
  .focus-depth,
  .focus-mode {
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }
  
  .depth-icon {
    font-size: 1.1rem;
  }
  
  .depth-value,
  .mode-value {
    font-weight: 500;
    text-transform: capitalize;
    font-size: 0.85rem;
  }
  
  .mode-label {
    color: #a0a9b8;
    font-size: 0.85rem;
  }
  
  .focus-empty,
  .query-empty,
  .memory-empty,
  .agents-empty,
  .daemons-empty {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.5rem;
    padding: 2rem;
    color: #64748b;
    text-align: center;
  }
  
  .empty-icon {
    font-size: 2rem;
    opacity: 0.6;
  }
  
  .empty-text {
    font-weight: 500;
  }
  
  .empty-subtext {
    font-size: 0.85rem;
    opacity: 0.7;
  }
  
  /* Processing Load Styles */
  .load-display {
    display: flex;
    align-items: center;
    gap: 1rem;
    margin-bottom: 1rem;
  }
  
  .load-meter {
    flex: 1;
    height: 8px;
    background: rgba(255, 255, 255, 0.1);
    border-radius: 4px;
    overflow: hidden;
  }
  
  .load-fill {
    height: 100%;
    transition: width 0.3s ease;
  }
  
  .load-fill.low {
    background: linear-gradient(90deg, #66bb6a, #81c784);
  }
  
  .load-fill.medium {
    background: linear-gradient(90deg, #ffa726, #ffcc02);
  }
  
  .load-fill.high {
    background: linear-gradient(90deg, #ef5350, #f44336);
  }
  
  .load-value {
    font-weight: 600;
    color: #e1e5e9;
  }
  
  .load-classification {
    display: flex;
    justify-content: space-between;
    margin-bottom: 1rem;
  }
  
  .load-class {
    font-weight: 600;
    font-size: 0.8rem;
  }
  
  .load-class.low {
    color: #66bb6a;
  }
  
  .load-class.medium {
    color: #ffa726;
  }
  
  .load-class.high {
    color: #ef5350;
  }
  
  /* Chart Styles */
  .load-chart {
    margin-top: 1rem;
  }
  
  .chart-container {
    display: flex;
    align-items: end;
    height: 40px;
    gap: 1px;
  }
  
  .chart-bar {
    flex: 1;
    background: linear-gradient(to top, #64b5f6, #42a5f5);
    border-radius: 1px;
    min-height: 2px;
    transition: height 0.3s ease;
  }
  
  /* Working Memory Styles */
  .memory-stats {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
  }
  
  .memory-count {
    font-weight: 600;
    color: #e1e5e9;
  }
  
  .capacity-bar {
    width: 100px;
    height: 6px;
    background: rgba(255, 255, 255, 0.1);
    border-radius: 3px;
    overflow: hidden;
  }
  
  .capacity-fill {
    height: 100%;
    background: linear-gradient(90deg, #64b5f6, #42a5f5);
    transition: width 0.3s ease;
  }
  
  .memory-items {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
  }
  
  .memory-item {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(100, 120, 150, 0.1);
    border-radius: 8px;
    padding: 0.75rem;
  }
  
  .item-type {
    display: inline-block;
    padding: 0.25rem 0.5rem;
    border-radius: 12px;
    font-size: 0.7rem;
    text-transform: uppercase;
    font-weight: 600;
    margin-bottom: 0.5rem;
  }
  
  .item-type.reflection {
    background: rgba(186, 104, 200, 0.2);
    color: #ba68c8;
  }
  
  .item-type.query {
    background: rgba(100, 181, 246, 0.2);
    color: #64b5f6;
  }
  
  .item-type.concept {
    background: rgba(129, 199, 132, 0.2);
    color: #81c784;
  }
  
  .item-content {
    color: #e1e5e9;
    font-size: 0.9rem;
    margin-bottom: 0.5rem;
  }
  
  .item-relevance {
    font-size: 0.8rem;
    color: #a0a9b8;
  }
  
  /* Current Query Styles */
  .query-display {
    background: rgba(100, 181, 246, 0.1);
    border: 1px solid rgba(100, 181, 246, 0.2);
    border-radius: 8px;
    padding: 1rem;
  }
  
  .query-text {
    color: #e1e5e9;
    font-style: italic;
    margin-bottom: 0.75rem;
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
    background: linear-gradient(90deg, #64b5f6, #42a5f5);
    animation: pulse 2s infinite;
  }
  
  .progress-text {
    font-size: 0.8rem;
    color: #64b5f6;
  }
  
  /* Agent and Daemon Styles */
  .agents-grid,
  .daemons-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 1rem;
    margin-bottom: 3rem;
  }
  
  .agent-card,
  .daemon-card {
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(100, 120, 150, 0.15);
    border-radius: 8px;
    padding: 1rem;
  }
  
  .agent-header,
  .daemon-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.75rem;
  }
  
  .agent-type,
  .daemon-name {
    font-weight: 600;
    color: #e1e5e9;
  }
  
  .agent-status {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.8rem;
    text-transform: capitalize;
  }
  
  .status-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #66bb6a;
  }
  
  .agent-goal {
    color: #a0a9b8;
    font-size: 0.9rem;
    margin-bottom: 0.75rem;
  }
  
  .agent-resources {
    display: flex;
    gap: 1rem;
    margin-bottom: 0.5rem;
  }
  
  .resource-usage {
    font-size: 0.8rem;
    color: #a0a9b8;
  }
  
  .agent-timing,
  .daemon-timing {
    font-size: 0.8rem;
    color: #64748b;
  }
  
  .daemon-load {
    width: 80px;
  }
  
  .daemon-activity {
    margin-bottom: 0.5rem;
    font-size: 0.9rem;
  }
  
  .activity-label {
    color: #a0a9b8;
  }
  
  .activity-value {
    color: #e1e5e9;
    text-transform: capitalize;
  }
  
  /* Health Section */
  .health-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem;
  }
  
  .health-card {
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(100, 120, 150, 0.15);
    border-radius: 8px;
    padding: 1rem;
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
  }
  
  .health-module {
    color: #e1e5e9;
    font-weight: 500;
    text-transform: capitalize;
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
  }
  
  .health-value {
    font-weight: 600;
    text-align: right;
  }
  
  /* Enhanced Focus History */
  .focus-history {
    margin-top: 1.5rem;
    padding-top: 1rem;
    border-top: 1px solid rgba(100, 120, 150, 0.1);
  }
  
  .focus-history h4 {
    margin: 0 0 1rem 0;
    font-size: 0.95rem;
    color: #a0a9b8;
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }
  
  .focus-history h4::before {
    content: "📊";
    font-size: 1rem;
  }
  
  .history-list {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
  }
  
  .history-item {
    padding: 0.75rem;
    background: rgba(255, 255, 255, 0.04);
    border-radius: 8px;
    border: 1px solid rgba(255, 255, 255, 0.05);
    transition: all 0.2s ease;
  }
  
  .history-item:hover {
    background: rgba(255, 255, 255, 0.06);
    border-color: rgba(255, 255, 255, 0.1);
  }
  
  .history-item.current {
    background: rgba(33, 150, 243, 0.15);
    border-color: rgba(33, 150, 243, 0.3);
  }
  
  .history-main {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.5rem;
  }
  
  .history-topic {
    color: #e1e5e9;
    font-size: 0.9rem;
    font-weight: 500;
  }
  
  .history-meta {
    display: flex;
    align-items: center;
    gap: 0.75rem;
  }
  
  .history-time {
    color: #64748b;
    font-size: 0.75rem;
  }
  
  .history-intensity {
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
  
  .mini-intensity-value {
    font-size: 0.7rem;
    font-weight: 500;
    min-width: 30px;
    color: #a0a9b8;
  }
  
  .history-context {
    color: #8892a0;
    font-size: 0.8rem;
    font-style: italic;
    line-height: 1.3;
  }
  
  @keyframes pulse {
    0%, 100% {
      opacity: 1;
    }
    50% {
      opacity: 0.7;
    }
  }
</style>
