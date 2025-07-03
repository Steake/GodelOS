<script>
  import { onMount } from 'svelte';
  import { cognitiveState, knowledgeState } from './stores/cognitive.js';
  import { GödelOSAPI } from './utils/api.js';
  
  // Core UI Components (imported progressively)
  let CognitiveStateMonitor = null;
  let QueryInterface = null;
  let ResponseDisplay = null;
  let KnowledgeGraph = null;
  let ConceptEvolution = null;
  
  let isLoading = true;
  let loadingStep = 'Initializing...';
  let activeView = 'dashboard';
  let websocketConnected = false;
  let sidebarCollapsed = false;
  let backendConnected = false;
  let componentError = null;
  
  // Enhanced view configuration
  const viewConfig = {
    dashboard: { 
      icon: '🏠', 
      title: 'Dashboard', 
      description: 'System overview and key metrics'
    },
    cognitive: { 
      icon: '🧠', 
      title: 'Cognitive State', 
      description: 'Real-time cognitive processing monitor'
    },
    knowledge: {
      icon: '🕸️', 
      title: 'Knowledge Graph', 
      description: 'Interactive knowledge visualization'
    },
    query: { 
      icon: '💬', 
      title: 'Query Interface', 
      description: 'Natural language interaction'
    }
  };
  
  onMount(async () => {
    try {
      loadingStep = 'Loading core components...';
      console.log('🚀 GödelOS Frontend starting...');
      
      // Test backend connectivity
      loadingStep = 'Checking backend connection...';
      try {
        const healthData = await GödelOSAPI.fetchSystemHealth();
        if (healthData) {
          backendConnected = true;
          console.log('✅ Backend connected');
        }
      } catch (error) {
        console.warn('⚠️ Backend not available:', error);
      }
      
      // Load essential components with error handling
      loadingStep = 'Loading UI components...';
      try {
        const componentModules = await Promise.allSettled([
          import('./components/core/CognitiveStateMonitor.svelte'),
          import('./components/core/QueryInterface.svelte'),
          import('./components/core/ResponseDisplay.svelte'),
          import('./components/knowledge/KnowledgeGraph.svelte'),
          import('./components/knowledge/ConceptEvolution.svelte')
        ]);
        
        componentModules.forEach((result, index) => {
          if (result.status === 'fulfilled') {
            const componentNames = ['CognitiveStateMonitor', 'QueryInterface', 'ResponseDisplay', 'KnowledgeGraph', 'ConceptEvolution'];
            console.log(`✅ Loaded ${componentNames[index]}`);
            
            switch(index) {
              case 0: CognitiveStateMonitor = result.value.default; break;
              case 1: QueryInterface = result.value.default; break;
              case 2: ResponseDisplay = result.value.default; break;
              case 3: KnowledgeGraph = result.value.default; break;
              case 4: ConceptEvolution = result.value.default; break;
            }
          } else {
            console.warn(`⚠️ Failed to load component ${index}:`, result.reason);
          }
        });
        
      } catch (error) {
        console.error('❌ Component loading failed:', error);
        componentError = error.message;
      }
      
      loadingStep = 'Finalizing...';
      setTimeout(() => {
        isLoading = false;
        console.log('✅ GödelOS Frontend loaded successfully');
      }, 500);
      
    } catch (error) {
      console.error('❌ Frontend initialization failed:', error);
      loadingStep = `Error: ${error.message}`;
      isLoading = false;
    }
  });
  
  function toggleSidebar() {
    sidebarCollapsed = !sidebarCollapsed;
  }
</script>

<main class="godelos-interface">
  {#if isLoading}
    <div class="loading-screen">
      <div class="loading-content">
        <div class="logo">🦉</div>
        <h1>GödelOS</h1>
        <div class="loading-spinner"></div>
        <p>{loadingStep}</p>
      </div>
    </div>
  {:else}
    <!-- Modern Header -->
    <header class="interface-header">
      <div class="header-content">
        <div class="header-left">
          <button class="sidebar-toggle" on:click={toggleSidebar}>
            <span class="toggle-icon">{sidebarCollapsed ? '▶️' : '◀️'}</span>
          </button>
          <h1 class="system-title">
            <span class="logo">🦉</span>
            <span class="title-text">GödelOS</span>
            <span class="subtitle">Cognitive Interface</span>
          </h1>
        </div>
        
        <div class="header-center">
          <div class="current-view-indicator">
            <span class="view-icon">{viewConfig[activeView]?.icon}</span>
            <div class="view-info">
              <div class="view-title">{viewConfig[activeView]?.title}</div>
              <div class="view-description">{viewConfig[activeView]?.description}</div>
            </div>
          </div>
        </div>
        
        <div class="header-right">
          <div class="connection-status {backendConnected ? 'connected' : 'disconnected'}">
            <div class="status-indicator"></div>
            <span class="status-text">{backendConnected ? 'Connected' : 'Disconnected'}</span>
          </div>
        </div>
      </div>
    </header>

    <!-- Main application layout -->
    <div class="app-layout">
      <!-- Enhanced Sidebar Navigation -->
      <nav class="sidebar" class:collapsed={sidebarCollapsed}>
        <div class="nav-sections">
          {#each Object.entries(viewConfig) as [key, config]}
            <button 
              class="nav-item {activeView === key ? 'active' : ''}"
              on:click={() => activeView = key}
              title={config.description}
            >
              <span class="nav-icon">{config.icon}</span>
              {#if !sidebarCollapsed}
                <div class="nav-content">
                  <span class="nav-title">{config.title}</span>
                  <span class="nav-description">{config.description}</span>
                </div>
              {/if}
            </button>
          {/each}
        </div>
        
        {#if !sidebarCollapsed}
          <!-- System Status in Sidebar -->
          <div class="sidebar-status">
            <div class="status-section">
              <h4>System Status</h4>
              <div class="status-overview">
                <div class="status-item">
                  <span class="status-label">Frontend</span>
                  <span class="status-value connected">✅ Active</span>
                </div>
                <div class="status-item">
                  <span class="status-label">Backend</span>
                  <span class="status-value {backendConnected ? 'connected' : 'disconnected'}">
                    {backendConnected ? '✅ Connected' : '❌ Disconnected'}
                  </span>
                </div>
                {#if componentError}
                  <div class="status-item">
                    <span class="status-label">Components</span>
                    <span class="status-value error">⚠️ Partial</span>
                  </div>
                {/if}
              </div>
            </div>
          </div>
        {/if}
      </nav>

      <!-- Main Content Area -->
      <section class="main-content">
        {#if activeView === 'dashboard'}
          <!-- Enhanced Dashboard View -->
          <div class="dashboard-layout">
            {#if componentError}
              <div class="error-banner">
                <h3>⚠️ Component Loading Issue</h3>
                <p>Some components failed to load: {componentError}</p>
                <p>Basic functionality is available, but some features may be limited.</p>
              </div>
            {/if}
            
            <div class="dashboard-grid">
              <div class="query-panel">
                <div class="panel-header">
                  <h3>Query Interface</h3>
                </div>
                <div class="panel-content">
                  {#if QueryInterface}
                    <svelte:component this={QueryInterface} />
                  {:else}
                    <div class="placeholder-content">
                      <p>💬 Query interface loading...</p>
                      <p>Natural language interaction will be available here.</p>
                    </div>
                  {/if}
                </div>
              </div>
              
              <div class="response-panel">
                <div class="panel-header">
                  <h3>Response Display</h3>
                </div>
                <div class="panel-content">
                  {#if ResponseDisplay}
                    <svelte:component this={ResponseDisplay} />
                  {:else}
                    <div class="placeholder-content">
                      <p>📝 Response display loading...</p>
                      <p>System responses will appear here.</p>
                    </div>
                  {/if}
                </div>
              </div>
              
              <div class="cognitive-panel">
                <div class="panel-header">
                  <h3>Cognitive State</h3>
                </div>
                <div class="panel-content">
                  {#if CognitiveStateMonitor}
                    <svelte:component this={CognitiveStateMonitor} />
                  {:else}
                    <div class="placeholder-content">
                      <p>🧠 Cognitive monitor loading...</p>
                      <p>Real-time cognitive state will be shown here.</p>
                    </div>
                  {/if}
                </div>
              </div>
              
              <div class="evolution-panel">
                <div class="panel-header">
                  <h3>Concept Evolution</h3>
                </div>
                <div class="panel-content">
                  {#if ConceptEvolution}
                    <svelte:component this={ConceptEvolution} />
                  {:else}
                    <div class="placeholder-content">
                      <p>📈 Evolution tracking loading...</p>
                      <p>Concept development over time will be displayed here.</p>
                    </div>
                  {/if}
                </div>
              </div>
            </div>
          </div>
          
        {:else if activeView === 'knowledge'}
          <!-- Knowledge Graph View -->
          <div class="expanded-view">
            <div class="view-header">
              <h2>Knowledge Graph Visualization</h2>
            </div>
            <div class="graph-container">
              {#if KnowledgeGraph}
                <svelte:component this={KnowledgeGraph} />
              {:else}
                <div class="placeholder-content large">
                  <div class="placeholder-icon">🕸️</div>
                  <h3>Knowledge Graph Loading...</h3>
                  <p>Interactive knowledge visualization will appear here once components are loaded.</p>
                </div>
              {/if}
            </div>
          </div>
          
        {:else if activeView === 'cognitive'}
          <!-- Cognitive State View -->
          <div class="expanded-view">
            <div class="view-header">
              <h2>Cognitive State Monitor</h2>
            </div>
            <div class="component-container">
              {#if CognitiveStateMonitor}
                <svelte:component this={CognitiveStateMonitor} />
              {:else}
                <div class="placeholder-content large">
                  <div class="placeholder-icon">🧠</div>
                  <h3>Cognitive Monitor Loading...</h3>
                  <p>Real-time cognitive processing visualization will appear here.</p>
                </div>
              {/if}
            </div>
          </div>
          
        {:else if activeView === 'query'}
          <!-- Query Interface View -->
          <div class="expanded-view">
            <div class="view-header">
              <h2>Natural Language Query Interface</h2>
            </div>
            <div class="query-layout">
              <div class="query-main">
                {#if QueryInterface}
                  <svelte:component this={QueryInterface} />
                {:else}
                  <div class="placeholder-content large">
                    <div class="placeholder-icon">💬</div>
                    <h3>Query Interface Loading...</h3>
                    <p>Natural language interaction will be available here.</p>
                  </div>
                {/if}
              </div>
              <div class="query-sidebar">
                {#if ResponseDisplay}
                  <svelte:component this={ResponseDisplay} />
                {:else}
                  <div class="placeholder-content">
                    <p>Response display loading...</p>
                  </div>
                {/if}
              </div>
            </div>
          </div>
        {/if}
      </section>
    </div>
  {/if}
</main>

<style>
  /* ... existing code ... */
  .godelos-interface {
    width: 100%;
    height: 100vh;
    background: linear-gradient(135deg, #0f1419 0%, #1a1f29 50%, #0f1629 100%);
    color: #e1e5e9;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    overflow: hidden;
  }

  .loading-screen {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100vh;
    background: radial-gradient(circle at center, rgba(100, 181, 246, 0.1) 0%, transparent 50%);
  }

  .loading-content {
    text-align: center;
    background: rgba(0, 0, 0, 0.3);
    padding: 3rem;
    border-radius: 20px;
    border: 1px solid rgba(100, 181, 246, 0.2);
    backdrop-filter: blur(10px);
  }

  .logo {
    font-size: 4rem;
    margin-bottom: 1rem;
    display: block;
    filter: drop-shadow(0 0 20px rgba(100, 181, 246, 0.5));
  }

  .loading-content h1 {
    font-size: 2.5rem;
    color: #64b5f6;
    margin: 0 0 2rem 0;
    font-weight: 700;
  }

  .loading-spinner {
    width: 40px;
    height: 40px;
    border: 3px solid rgba(100, 181, 246, 0.3);
    border-radius: 50%;
    border-top-color: #64b5f6;
    animation: spin 1s ease-in-out infinite;
    margin: 0 auto 1rem auto;
  }

  @keyframes spin {
    to { transform: rotate(360deg); }
  }

  /* Header Styles */
  .interface-header {
    padding: 1rem 2rem;
    background: rgba(0, 0, 0, 0.3);
    border-bottom: 1px solid rgba(100, 181, 246, 0.2);
    backdrop-filter: blur(10px);
    z-index: 100;
  }

  .header-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .header-left {
    display: flex;
    align-items: center;
    gap: 1rem;
  }

  .sidebar-toggle {
    background: rgba(100, 181, 246, 0.1);
    border: 1px solid rgba(100, 181, 246, 0.3);
    color: #64b5f6;
    padding: 0.5rem;
    border-radius: 6px;
    cursor: pointer;
    transition: all 0.2s ease;
  }

  .sidebar-toggle:hover {
    background: rgba(100, 181, 246, 0.2);
  }

  .system-title {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin: 0;
    font-size: 1.5rem;
    font-weight: 600;
    color: #64b5f6;
  }

  .system-title .logo {
    font-size: 2rem;
    filter: drop-shadow(0 0 8px rgba(100, 181, 246, 0.3));
  }

  .subtitle {
    font-size: 0.9rem;
    opacity: 0.7;
    font-weight: 400;
  }

  .header-center {
    flex: 1;
    display: flex;
    justify-content: center;
  }

  .current-view-indicator {
    display: flex;
    align-items: center;
    gap: 1rem;
    background: rgba(0, 0, 0, 0.3);
    padding: 0.75rem 1.5rem;
    border-radius: 12px;
    border: 1px solid rgba(100, 181, 246, 0.2);
  }

  .view-icon {
    font-size: 1.5rem;
  }

  .view-info {
    display: flex;
    flex-direction: column;
  }

  .view-title {
    font-weight: 600;
    color: #e1e5e9;
  }

  .view-description {
    font-size: 0.8rem;
    opacity: 0.7;
    margin: 0;
  }

  .connection-status {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem 1rem;
    border-radius: 8px;
    background: rgba(0, 0, 0, 0.2);
    border: 1px solid rgba(100, 120, 150, 0.2);
  }

  .connection-status.connected {
    border-color: rgba(129, 199, 132, 0.4);
    background: rgba(129, 199, 132, 0.1);
  }

  .connection-status.disconnected {
    border-color: rgba(229, 115, 115, 0.4);
    background: rgba(229, 115, 115, 0.1);
  }

  .status-indicator {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #f44336;
    animation: pulse 2s infinite;
  }

  .connection-status.connected .status-indicator {
    background: #4CAF50;
  }

  @keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
  }

  /* Layout */
  .app-layout {
    display: flex;
    height: calc(100vh - 80px);
  }

  .sidebar {
    width: 280px;
    background: rgba(15, 20, 35, 0.95);
    display: flex;
    flex-direction: column;
    border-right: 1px solid rgba(100, 181, 246, 0.2);
    transition: width 0.3s ease;
  }

  .sidebar.collapsed {
    width: 70px;
  }

  .nav-sections {
    flex: 1;
    padding: 1rem 0;
  }

  .nav-item {
    width: 100%;
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 1rem;
    background: none;
    border: none;
    color: #e1e5e9;
    cursor: pointer;
    transition: all 0.2s ease;
    border-bottom: 1px solid rgba(100, 181, 246, 0.1);
  }

  .nav-item:hover {
    background: rgba(100, 181, 246, 0.1);
  }

  .nav-item.active {
    background: rgba(100, 181, 246, 0.2);
    border-right: 3px solid #64b5f6;
  }

  .nav-icon {
    font-size: 1.5rem;
    min-width: 24px;
  }

  .nav-content {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
  }

  .nav-title {
    font-weight: 600;
    font-size: 0.95rem;
  }

  .nav-description {
    font-size: 0.8rem;
    opacity: 0.7;
    margin-top: 0.25rem;
  }

  .sidebar-status {
    padding: 1rem;
    border-top: 1px solid rgba(100, 181, 246, 0.2);
  }

  .status-section h4 {
    margin: 0 0 1rem 0;
    color: #64b5f6;
    font-size: 0.9rem;
  }

  .status-overview {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .status-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 0.8rem;
  }

  .status-value.connected {
    color: #4CAF50;
  }

  .status-value.disconnected {
    color: #f44336;
  }

  .status-value.error {
    color: #ff9800;
  }

  /* Main Content */
  .main-content {
    flex: 1;
    display: flex;
    flex-direction: column;
    overflow: hidden;
    padding: 2rem;
    gap: 2rem;
  }

  .error-banner {
    background: rgba(255, 152, 0, 0.1);
    border: 1px solid rgba(255, 152, 0, 0.3);
    border-radius: 12px;
    padding: 1rem;
    margin-bottom: 1rem;
  }

  .error-banner h3 {
    margin: 0 0 0.5rem 0;
    color: #ff9800;
  }

  .error-banner p {
    margin: 0.25rem 0;
    font-size: 0.9rem;
    opacity: 0.9;
  }

  /* Dashboard Layout */
  .dashboard-layout {
    display: flex;
    flex-direction: column;
    height: 100%;
  }

  .dashboard-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    grid-template-rows: 1fr 1fr;
    gap: 2rem;
    flex: 1;
  }

  .query-panel, .response-panel, .cognitive-panel, .evolution-panel {
    background: rgba(0, 0, 0, 0.3);
    border: 1px solid rgba(100, 181, 246, 0.2);
    border-radius: 16px;
    padding: 0;
    display: flex;
    flex-direction: column;
    backdrop-filter: blur(10px);
    overflow: hidden;
  }

  .panel-header {
    padding: 1rem 1.5rem;
    border-bottom: 1px solid rgba(100, 181, 246, 0.2);
    background: rgba(100, 181, 246, 0.05);
  }

  .panel-header h3 {
    margin: 0;
    color: #64b5f6;
    font-size: 1.1rem;
    font-weight: 600;
  }

  .panel-content {
    flex: 1;
    padding: 1.5rem;
    overflow: auto;
  }

  .placeholder-content {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100%;
    text-align: center;
    opacity: 0.7;
  }

  .placeholder-content.large {
    padding: 3rem;
  }

  .placeholder-icon {
    font-size: 4rem;
    margin-bottom: 1rem;
    opacity: 0.5;
  }

  .placeholder-content h3 {
    color: #64b5f6;
    margin: 0 0 1rem 0;
  }

  .placeholder-content p {
    margin: 0.5rem 0;
    opacity: 0.8;
  }

  /* Expanded Views */
  .expanded-view {
    height: 100%;
    display: flex;
    flex-direction: column;
  }

  .view-header {
    margin-bottom: 2rem;
    padding-bottom: 1rem;
    border-bottom: 1px solid rgba(100, 181, 246, 0.2);
  }

  .view-header h2 {
    margin: 0;
    color: #64b5f6;
    font-size: 1.8rem;
    font-weight: 700;
  }

  .component-container, .graph-container {
    flex: 1;
    background: rgba(0, 0, 0, 0.2);
    border: 1px solid rgba(100, 181, 246, 0.2);
    border-radius: 16px;
    padding: 2rem;
    overflow: auto;
  }

  .query-layout {
    display: grid;
    grid-template-columns: 2fr 1fr;
    gap: 2rem;
    height: 100%;
  }

  .query-main, .query-sidebar {
    background: rgba(0, 0, 0, 0.2);
    border: 1px solid rgba(100, 181, 246, 0.2);
    border-radius: 16px;
    padding: 2rem;
    overflow: auto;
  }
</style>
