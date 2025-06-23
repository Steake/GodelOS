<script>
  import { onMount, onDestroy } from 'svelte';
  import { cognitiveState, knowledgeState, evolutionState, uiState } from './stores/cognitive.js';
  import { enhancedCognitiveState, autonomousLearningState, streamState } from './stores/enhanced-cognitive.js';
  import { setupWebSocket, connectToCognitiveStream } from './utils/websocket.js';
  import { GödelOSAPI } from './utils/api.js';
  
  // Core UI Components
  import CognitiveStateMonitor from './components/core/CognitiveStateMonitor.svelte';
  import QueryInterface from './components/core/QueryInterface.svelte';
  import ResponseDisplay from './components/core/ResponseDisplay.svelte';
  
  // Enhanced Metacognition Components
  import StreamOfConsciousnessMonitor from './components/core/StreamOfConsciousnessMonitor.svelte';
  import AutonomousLearningMonitor from './components/core/AutonomousLearningMonitor.svelte';
  import EnhancedCognitiveDashboard from './components/dashboard/EnhancedCognitiveDashboard.svelte';
  
  // Transparency Components
  import ReflectionVisualization from './components/transparency/ReflectionVisualization.svelte';
  import ResourceAllocation from './components/transparency/ResourceAllocation.svelte';
  import ProcessInsight from './components/transparency/ProcessInsight.svelte';
  import TransparencyDashboard from './components/transparency/TransparencyDashboard.svelte';
  import ReasoningSessionViewer from './components/transparency/ReasoningSessionViewer.svelte';
  import ProvenanceTracker from './components/transparency/ProvenanceTracker.svelte';
  
  // Knowledge Management
  import KnowledgeGraph from './components/knowledge/KnowledgeGraph.svelte';
  import ConceptEvolution from './components/knowledge/ConceptEvolution.svelte';
  import SmartImport from './components/knowledge/SmartImport.svelte';
  
  // Evolution Tracking
  import CapabilityDashboard from './components/evolution/CapabilityDashboard.svelte';
  import ArchitectureTimeline from './components/evolution/ArchitectureTimeline.svelte';
  
  // UI Components
  import Modal from './components/ui/Modal.svelte';
  
  let activeView = 'dashboard';
  let websocketConnected = false;
  let sidebarCollapsed = false;
  let fullscreenMode = false;
  let pollInterval;
  
  // Check URL parameters for direct view access
  onMount(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const viewParam = urlParams.get('view');
    if (viewParam && viewConfig[viewParam]) {
      activeView = viewParam;
      console.log(`🎯 Direct navigation to view: ${viewParam}`);
    }
    
    // Debug navigation sections
    console.log('🧭 Available view sections:', Object.keys(viewSections));
    console.log('🧭 Enhanced section views:', Object.keys(viewSections.enhanced?.views || {}));
    console.log('🧭 Total views available:', Object.keys(viewConfig).length);
  });
  
  // Modal state management
  let showProcessInsightModal = false;
  let showKnowledgeGraphModal = false;
  let showSmartImportModal = false;
  let showCapabilityDashboardModal = false;
  let showArchitectureTimelineModal = false;
  
  onMount(async () => {
    try {
      console.log('🚀 Initializing GödelOS cognitive interface...');
      
      // Setup WebSocket connection
      await setupWebSocket();
      websocketConnected = true;
      
      // Initialize enhanced cognitive features
      await initializeEnhancedCognitive();
      
      // Start real-time data polling
      pollInterval = await GödelOSAPI.pollForUpdates(handleDataUpdate, 3000);
      
      console.log('✅ GödelOS cognitive interface connected with enhanced features');
    } catch (error) {
      // Silently handle WebSocket connection errors when backend is unavailable
      websocketConnected = false;
    }
  });

  onDestroy(() => {
    if (pollInterval) {
      clearInterval(pollInterval);
    }
  });

  function handleDataUpdate(data) {
    if (data.health) {
      cognitiveState.update(state => ({
        ...state,
        systemHealth: data.health
      }));
    }
    if (data.cognitive) {
      cognitiveState.update(state => ({
        ...state,
        ...data.cognitive
      }));
    }
    if (data.concepts) {
      knowledgeState.update(state => ({
        ...state,
        concepts: data.concepts
      }));
    }
  }
  
  // Query event handlers
  function handleQuerySubmitted(event) {
    console.log('Query submitted:', event.detail);
    // Could add loading states or other UI updates here
  }
  
  function handleQueryResponse(event) {
    console.log('Query response received:', event.detail);
    // The ResponseDisplay component will handle displaying the response
    // We could add additional processing here if needed
  }
  
  // Enhanced view configuration with better UX organization
  const viewSections = {
    core: {
      title: 'Core Features',
      icon: '⭐',
      views: {
        dashboard: {
          icon: '🏠',
          title: 'Dashboard',
          description: 'System overview and key metrics',
          component: 'dashboard'
        },
        cognitive: {
          icon: '🧠',
          title: 'Cognitive State',
          description: 'Real-time cognitive processing monitor',
          component: CognitiveStateMonitor
        },
        knowledge: {
          icon: '🕸️',
          title: 'Knowledge Graph',
          description: 'Interactive knowledge visualization',
          component: KnowledgeGraph
        },
        query: {
          icon: '💬',
          title: 'Query Interface',
          description: 'Natural language interaction',
          component: QueryInterface
        }
      }
    },
    enhanced: {
      title: 'Enhanced Cognition',
      icon: '🚀',
      badge: 'NEW',
      views: {
        enhanced: {
          icon: '🚀',
          title: 'Enhanced Dashboard',
          description: 'Unified cognitive enhancement overview',
          component: EnhancedCognitiveDashboard,
          featured: true
        },
        stream: {
          icon: '🌊',
          title: 'Stream of Consciousness',
          description: 'Real-time cognitive event streaming',
          component: StreamOfConsciousnessMonitor,
          featured: true
        },
        autonomous: {
          icon: '🤖',
          title: 'Autonomous Learning',
          description: 'Self-directed knowledge acquisition',
          component: AutonomousLearningMonitor,
          featured: true
        }
      }
    },
    analysis: {
      title: 'Analysis & Tools',
      icon: '🔬',
      views: {
        transparency: {
          icon: '🔍',
          title: 'Transparency',
          description: 'Cognitive transparency and reasoning insights',
          component: TransparencyDashboard
        },
        reasoning: {
          icon: '🎯',
          title: 'Reasoning Sessions',
          description: 'Live reasoning session monitoring',
          component: ReasoningSessionViewer
        },
        reflection: {
          icon: '🪞',
          title: 'Reflection',
          description: 'System introspection and analysis',
          component: ReflectionVisualization
        },
        provenance: {
          icon: '🔗',
          title: 'Provenance',
          description: 'Data lineage and attribution tracking',
          component: ProvenanceTracker
        }
      }
    },
    system: {
      title: 'System Management',
      icon: '⚙️',
      views: {
        import: {
          icon: '📥',
          title: 'Knowledge Import',
          description: 'Import and process documents',
          component: SmartImport
        },
        capabilities: {
          icon: '📈',
          title: 'Capabilities',
          description: 'System capabilities and evolution',
          component: CapabilityDashboard
        },
        resources: {
          icon: '⚡',
          title: 'Resources',
          description: 'Resource allocation and performance',
          component: ResourceAllocation
        }
      }
    }
  };

  // Flatten views for backward compatibility
  const viewConfig = {};
  Object.values(viewSections).forEach(section => {
    Object.assign(viewConfig, section.views);
  });

  function toggleSidebar() {
    sidebarCollapsed = !sidebarCollapsed;
  }

  function toggleFullscreen() {
    fullscreenMode = !fullscreenMode;
    if (fullscreenMode) {
      document.documentElement.requestFullscreen?.();
    } else {
      document.exitFullscreen?.();
    }
  }

  function getHealthColor(value) {
    if (value >= 0.8) return '#66bb6a';
    if (value >= 0.6) return '#ffa726';
    if (value >= 0.4) return '#ff7043';
    return '#ef5350';
  }
  
  async function initializeEnhancedCognitive() {
    try {
      console.log('🧠 Initializing enhanced cognitive features...');
      
      // Check if enhanced cognitive API is available
      const response = await fetch('http://localhost:8000/api/enhanced-cognitive/health');
      if (response.ok) {
        const cognitiveState = await response.json();
        console.log('✅ Enhanced cognitive API connected');
        
        // Initialize enhanced cognitive store
        enhancedCognitiveState.update(state => ({
          ...state,
          apiConnected: true,
          lastUpdate: new Date().toISOString()
        }));
        
        // Start cognitive streaming if enabled
        await setupCognitiveStreaming();
        
        // Initialize autonomous learning monitoring
        await initializeAutonomousLearning();
        
      } else {
        console.log('⚠️ Enhanced cognitive API not available, using fallback mode');
      }
    } catch (error) {
      // Silently handle initialization errors when backend is unavailable
      enhancedCognitiveState.update(state => ({
        ...state,
        apiConnected: false,
        lastUpdate: new Date().toISOString()
      }));
    }
  }
  
  async function setupCognitiveStreaming() {
    try {
      // Connect to cognitive event stream
      const streamResponse = await fetch('http://localhost:8000/api/enhanced-cognitive/stream/status');
      if (streamResponse.ok) {
        console.log('🌊 Cognitive streaming available');
        
        // Update stream state
        streamState.update(state => ({
          ...state,
          available: true,
          connected: false
        }));
      }
    } catch (error) {
      // Silently handle streaming setup errors when backend is unavailable
      streamState.update(state => ({
        ...state,
        available: false,
        connected: false
      }));
    }
  }
  
  async function initializeAutonomousLearning() {
    try {
      // Check autonomous learning status
      const learningResponse = await fetch('http://localhost:8000/api/enhanced-cognitive/autonomous/status');
      if (learningResponse.ok) {
        const learningData = await learningResponse.json();
        console.log('🤖 Autonomous learning status:', learningData);
        
        // Update autonomous learning state
        autonomousLearningState.update(state => ({
          ...state,
          enabled: learningData.enabled || false,
          available: true
        }));
      }
    } catch (error) {
      // Silently handle autonomous learning initialization errors when backend is unavailable
      autonomousLearningState.update(state => ({
        ...state,
        enabled: false,
        available: false
      }));
    }
  }
</script>

<main class="godelos-interface" class:fullscreen={fullscreenMode} data-testid="app-container">
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
        <div class="connection-status {websocketConnected ? 'connected' : 'disconnected'}">
          <div class="status-indicator"></div>
          <span class="status-text">{websocketConnected ? 'Connected' : 'Disconnected'}</span>
        </div>
        <button class="fullscreen-toggle" on:click={toggleFullscreen}>
          <span>{fullscreenMode ? '🗗' : '⛶'}</span>
        </button>
      </div>
    </div>
  </header>

  <!-- Main application layout -->
  <div class="app-layout">
    <!-- Enhanced Sidebar Navigation -->
    <nav class="sidebar" class:collapsed={sidebarCollapsed} data-testid="sidebar-nav">
      {#if !sidebarCollapsed}
        <div class="sidebar-header">
          <h3>🧭 Navigation</h3>
          <span class="nav-count">{Object.keys(viewConfig).length} views available</span>
        </div>
      {/if}
      
      <div class="nav-sections">
        {#each Object.entries(viewSections) as [sectionKey, section]}
          <div class="nav-section" data-testid="nav-section-{sectionKey}">
            {#if !sidebarCollapsed}
              <div class="section-header">
                <span class="section-icon">{section.icon}</span>
                <span class="section-title">{section.title}</span>
                {#if section.badge}
                  <span class="section-badge">{section.badge}</span>
                {/if}
              </div>
            {/if}
            
            <div class="section-items">
              {#each Object.entries(section.views) as [key, config]}
                <button
                  class="nav-item {activeView === key ? 'active' : ''} {config.featured ? 'featured' : ''}"
                  data-testid="nav-item-{key}"
                  on:click={() => {
                    activeView = key;
                  }}
                  title={config.description}
                >
                  <span class="nav-icon">{config.icon}</span>
                  {#if !sidebarCollapsed}
                    <div class="nav-content">
                      <span class="nav-title">{config.title}</span>
                      {#if config.featured}
                        <span class="featured-indicator">✨</span>
                      {/if}
                    </div>
                  {/if}
                </button>
              {/each}
            </div>
          </div>
        {/each}
      </div>
      
      {#if !sidebarCollapsed}
        <!-- System Status in Sidebar -->
        <div class="sidebar-status">
          <div class="status-section">
            <h4>System Health</h4>
            <div class="health-overview">
              {#each Object.entries($cognitiveState.systemHealth) as [module, health]}
                {#if typeof health === 'number' && !isNaN(health) && health >= 0 && health <= 1}
                  <div class="health-item">
                    <span class="module-name">{module}</span>
                    <div class="health-bar">
                      <div class="health-fill" style="width: {health * 100}%; background: {getHealthColor(health)}"></div>
                    </div>
                    <span class="health-value" style="color: {getHealthColor(health)}">{Math.round(health * 100)}%</span>
                  </div>
                {/if}
              {/each}
            </div>
          </div>
          
          <div class="status-section">
            <h4>Knowledge Stats</h4>
            <div class="knowledge-stats">
              <div class="stat">
                <span class="stat-value">{$knowledgeState.totalConcepts}</span>
                <span class="stat-label">Concepts</span>
              </div>
              <div class="stat">
                <span class="stat-value">{$knowledgeState.totalConnections}</span>
                <span class="stat-label">Connections</span>
              </div>
              <div class="stat">
                <span class="stat-value">{$knowledgeState.totalDocuments}</span>
                <span class="stat-label">Documents</span>
              </div>
            </div>
          </div>
        </div>
      {/if}
    </nav>

    <!-- Main Content Area -->
    <section class="main-content">
      {#if activeView === 'dashboard'}
        <!-- Enhanced Dashboard View -->
        <div class="dashboard-layout" data-testid="dashboard-view">
          <div class="dashboard-top">
            <div class="query-panel">
              <QueryInterface 
                on:query-submitted={handleQuerySubmitted}
                on:query-response={handleQueryResponse}
              />
            </div>
            <div class="response-panel">
              <ResponseDisplay />
            </div>
          </div>
          
          <div class="dashboard-middle">
            <div class="cognitive-panel">
              <CognitiveStateMonitor />
            </div>
            <div class="evolution-panel">
              <ConceptEvolution />
            </div>
          </div>
          
          <div class="dashboard-bottom">
            <div class="insights-panel">
              <div class="panel-header">
                <h3>Process Insights</h3>
                <button class="expand-btn" on:click={() => showProcessInsightModal = true}>
                  Expand 🗗
                </button>
              </div>
              <div class="insights-preview">
                <ProcessInsight />
              </div>
            </div>
            
            <div class="knowledge-preview-panel">
              <div class="panel-header">
                <h3>Knowledge Graph</h3>
                <button class="expand-btn" on:click={() => activeView = 'knowledge'}>
                  Open Graph 🕸️
                </button>
              </div>
              <div class="knowledge-preview">
                <div class="graph-stats">
                  <div class="stat-item">
                    <span class="value">{$knowledgeState.totalConcepts}</span>
                    <span class="label">Concepts</span>
                  </div>
                  <div class="stat-item">
                    <span class="value">{$knowledgeState.totalConnections}</span>
                    <span class="label">Connections</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        
      {:else if activeView === 'query'}
        <!-- Enhanced Query Interface -->
        <div class="expanded-view">
          <div class="query-layout">
            <div class="query-main">
              <QueryInterface 
                on:query-submitted={handleQuerySubmitted}
                on:query-response={handleQueryResponse}
              />
            </div>
            <div class="query-sidebar">
              <ResponseDisplay />
            </div>
          </div>
        </div>
        
      {:else if viewConfig[activeView]?.component && typeof viewConfig[activeView].component !== 'string'}
        <!-- Standard Component Views -->
        <div class="expanded-view" data-testid="{activeView}-view">
          <div class="view-header">
            <h2>{viewConfig[activeView].title}</h2>
            <p class="view-description">{viewConfig[activeView].description}</p>
          </div>
          <div class="component-container">
            <svelte:component this={viewConfig[activeView].component} />
          </div>
        </div>
      {:else}
        <!-- Fallback for unmatched views -->
        <div class="expanded-view" data-testid="fallback-view">
          <div class="view-header">
            <h2>View Not Found</h2>
            <div class="debug-info" style="background: rgba(255,0,0,0.1); padding: 1rem; border-radius: 8px;">
              <p>⚠️ Debug: Could not render view "{activeView}"</p>
              <p>Component: {JSON.stringify(viewConfig[activeView]?.component)}</p>
              <p>Available views: {Object.keys(viewConfig).join(', ')}</p>
            </div>
          </div>
        </div>
      {/if}
    </section>
  </div>

  <!-- Alert notifications -->
  {#if $cognitiveState.alerts.length > 0}
    <div class="alert-overlay">
      {#each $cognitiveState.alerts as alert}
        <div class="alert alert-{alert.severity}">
          <span class="alert-icon">⚠️</span>
          <div class="alert-content">
            <div class="alert-title">{alert.title}</div>
            <div class="alert-message">{alert.message}</div>
          </div>
        </div>
      {/each}
    </div>
  {/if}

  <!-- Modal Components -->
  <Modal 
    bind:show={showProcessInsightModal} 
    title="Process Insights & Analysis"
    size="large"
    on:close={() => showProcessInsightModal = false}
  >
    <ProcessInsight />
  </Modal>

  <Modal 
    bind:show={showKnowledgeGraphModal} 
    title="Knowledge Graph Visualization"
    size="fullscreen"
    on:close={() => showKnowledgeGraphModal = false}
  >
    <KnowledgeGraph />
  </Modal>

  <Modal 
    bind:show={showSmartImportModal} 
    title="Smart Knowledge Import"
    size="large"
    on:close={() => showSmartImportModal = false}
  >
    <SmartImport />
  </Modal>

  <Modal 
    bind:show={showCapabilityDashboardModal} 
    title="Capability Dashboard"
    size="large"
    on:close={() => showCapabilityDashboardModal = false}
  >
    <CapabilityDashboard />
  </Modal>

  <Modal 
    bind:show={showArchitectureTimelineModal} 
    title="Architecture Timeline"
    size="large"
    on:close={() => showArchitectureTimelineModal = false}
  >
    <ArchitectureTimeline />
  </Modal>
</main>

<style>
  :global(body) {
    margin: 0;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
    background: linear-gradient(135deg, #0a0a0f 0%, #1a1a2e 50%, #16213e 100%);
    color: #e1e5e9;
    overflow: hidden;
  }

  .godelos-interface {
    height: 100vh;
    display: flex;
    flex-direction: column;
    background: transparent;
  }

  .godelos-interface.fullscreen {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    z-index: 9999;
  }

  /* Enhanced Header */
  .interface-header {
    background: rgba(20, 25, 40, 0.95);
    border-bottom: 1px solid rgba(100, 120, 150, 0.2);
    backdrop-filter: blur(20px);
    z-index: 100;
    padding: 0.5rem 0;
    min-height: 60px;
    flex-shrink: 0;
  }

  .header-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0 2rem;
    max-width: none;
    margin: 0;
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
    border-color: rgba(100, 181, 246, 0.5);
  }

  .system-title {
    display: flex;
    align-items: center;
    gap: 1rem;
    margin: 0;
    font-size: 1.5rem;
    font-weight: 700;
    color: #64b5f6;
  }

  .logo {
    font-size: 2rem;
  }

  .title-text {
    font-size: 1.5rem;
    font-weight: 700;
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

  .header-right {
    display: flex;
    align-items: center;
    gap: 1rem;
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

  .status-text {
    font-size: 0.9rem;
    font-weight: 500;
  }

  .fullscreen-toggle {
    background: rgba(100, 181, 246, 0.1);
    border: 1px solid rgba(100, 181, 246, 0.3);
    color: #64b5f6;
    padding: 0.5rem;
    border-radius: 6px;
    cursor: pointer;
    transition: all 0.2s ease;
  }

  .fullscreen-toggle:hover {
    background: rgba(100, 181, 246, 0.2);
    border-color: rgba(100, 181, 246, 0.5);
  }

  /* Main Layout */
  .app-layout {
    display: flex;
    flex: 1;
    overflow: hidden;
  }

  /* Sidebar */
  .sidebar {
    width: 280px;
    background: rgba(15, 20, 35, 0.95);
    border-right: 1px solid rgba(100, 120, 150, 0.2);
    display: flex;
    flex-direction: column;
    transition: width 0.3s ease;
    backdrop-filter: blur(10px);
    height: 100%;
    overflow: hidden;
  }

  .sidebar.collapsed {
    width: 70px;
  }

  .sidebar-header {
    padding: 1rem;
    border-bottom: 1px solid rgba(100, 120, 150, 0.2);
    text-align: center;
  }

  .sidebar-header h3 {
    margin: 0 0 0.5rem 0;
    color: #64b5f6;
    font-size: 1.1rem;
  }

  .nav-count {
    font-size: 0.8rem;
    color: rgba(225, 229, 233, 0.7);
    background: rgba(100, 181, 246, 0.1);
    padding: 0.25rem 0.5rem;
    border-radius: 12px;
  }

  .nav-sections {
    flex: 1;
    padding: 1rem 0.5rem;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    overflow-y: auto;
    scrollbar-width: thin;
    scrollbar-color: rgba(100, 181, 246, 0.3) transparent;
  }

  .nav-sections::-webkit-scrollbar {
    width: 6px;
  }

  .nav-sections::-webkit-scrollbar-track {
    background: transparent;
  }

  .nav-sections::-webkit-scrollbar-thumb {
    background: rgba(100, 181, 246, 0.3);
    border-radius: 3px;
  }

  .nav-sections::-webkit-scrollbar-thumb:hover {
    background: rgba(100, 181, 246, 0.5);
  }

  .nav-item {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 1rem;
    background: transparent;
    border: 1px solid transparent;
    border-radius: 12px;
    color: #e1e5f9;
    cursor: pointer;
    transition: all 0.2s ease;
    text-align: left;
    min-height: 60px;
  }

  .nav-item:hover {
    background: rgba(100, 181, 246, 0.1);
    border-color: rgba(100, 181, 246, 0.3);
  }

  .nav-item.active {
    background: rgba(100, 181, 246, 0.2);
    border-color: rgba(100, 181, 246, 0.5);
    color: #64b5f6;
  }

  /* Navigation Sections */
  .nav-section {
    margin-bottom: 1rem;
  }

  .section-header {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.75rem 1rem;
    margin-bottom: 0.5rem;
    background: rgba(100, 181, 246, 0.05);
    border: 1px solid rgba(100, 181, 246, 0.2);
    border-radius: 8px;
    font-size: 0.9rem;
    font-weight: 600;
    color: #64b5f6;
  }

  .section-icon {
    font-size: 1.1rem;
  }

  .section-title {
    flex: 1;
  }

  .section-badge {
    background: linear-gradient(135deg, #ff6b35, #f7931e);
    color: white;
    padding: 0.2rem 0.5rem;
    border-radius: 12px;
    font-size: 0.7rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    animation: pulse 2s infinite;
  }

  @keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.7; }
  }

  .section-items {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
    padding-left: 0.5rem;
  }

  .nav-item.featured {
    background: linear-gradient(135deg, rgba(100, 181, 246, 0.1), rgba(156, 39, 176, 0.1));
    border: 1px solid rgba(100, 181, 246, 0.4);
    position: relative;
    overflow: hidden;
  }

  .nav-item.featured::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.1), transparent);
    transition: left 0.5s ease;
  }

  .nav-item.featured:hover::before {
    left: 100%;
  }

  .nav-item.featured:hover {
    background: linear-gradient(135deg, rgba(100, 181, 246, 0.2), rgba(156, 39, 176, 0.2));
    border-color: rgba(100, 181, 246, 0.6);
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(100, 181, 246, 0.3);
  }

  .featured-indicator {
    font-size: 0.8rem;
    animation: sparkle 1.5s infinite;
  }

  @keyframes sparkle {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.7; transform: scale(1.2); }
  }

  .nav-icon {
    font-size: 1.5rem;
    min-width: 1.5rem;
  }

  .nav-content {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
  }

  .nav-title {
    font-weight: 600;
    font-size: 1rem;
  }

  .sidebar-status {
    padding: 1rem;
    border-top: 1px solid rgba(100, 120, 150, 0.2);
  }

  .status-section {
    margin-bottom: 1.5rem;
  }

  .status-section h4 {
    margin: 0 0 0.75rem 0;
    font-size: 0.9rem;
    color: #64b5f6;
    font-weight: 600;
  }

  .health-overview {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .health-item {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.8rem;
  }

  .module-name {
    flex: 1;
    min-width: 60px;
  }

  .health-bar {
    flex: 2;
    height: 4px;
    background: rgba(100, 181, 246, 0.2);
    border-radius: 2px;
    overflow: hidden;
  }

  .health-fill {
    height: 100%;
    background: linear-gradient(90deg, #f44336 0%, #ff9800 50%, #4CAF50 100%);
    transition: width 0.3s ease;
  }

  .health-value {
    min-width: 35px;
    text-align: right;
    font-weight: 500;
  }

  .knowledge-stats {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 0.5rem;
  }

  .stat {
    text-align: center;
    background: rgba(0, 0, 0, 0.3);
    padding: 0.5rem;
    border-radius: 6px;
  }

  .stat-value {
    display: block;
    font-size: 1.1rem;
    font-weight: 600;
    color: #64b5f6;
  }

  .stat-label {
    display: block;
    font-size: 0.7rem;
    opacity: 0.7;
    margin-top: 0.25rem;
  }

  /* Main Content */
  .main-content {
    flex: 1;
    padding: 0.75rem;
    overflow: hidden;
    background: rgba(10, 15, 25, 0.8);
    border-radius: 8px;
    margin: 0.25rem 0.5rem 0.5rem 0;
    box-shadow: 0 4px 20px rgba(0,0,0,0.2);
    display: flex;
    flex-direction: column;
    min-height: 0;
  }

  /* Dashboard Layout */
  .dashboard-layout {
    display: grid;
    grid-template-rows: minmax(180px, auto) 1fr minmax(200px, auto);
    gap: 1.5rem;
    height: 100%;
    overflow: hidden;
  }

  .dashboard-top {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1.5rem;
    min-height: 180px;
  }

  .dashboard-middle {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1.5rem;
    min-height: 200px;
  }

  .dashboard-bottom {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1.5rem;
    min-height: 200px;
  }

  .query-panel, .response-panel, .cognitive-panel, .evolution-panel,
  .insights-panel, .knowledge-preview-panel {
    background: rgba(0, 0, 0, 0.3);
    border: 1px solid rgba(100, 181, 246, 0.2);
    border-radius: 16px;
    padding: 1.25rem;
    display: flex;
    flex-direction: column;
    backdrop-filter: blur(10px);
    min-height: 0;
    overflow: hidden;
  }

  .panel-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
    padding-bottom: 0.75rem;
    border-bottom: 1px solid rgba(100, 181, 246, 0.2);
  }

  .panel-header h3 {
    margin: 0;
    color: #64b5f6;
    font-size: 1.1rem;
    font-weight: 600;
  }

  .expand-btn {
    background: rgba(100, 181, 246, 0.1);
    border: 1px solid rgba(100, 181, 246, 0.3);
    color: #64b5f6;
    padding: 0.5rem 1rem;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.2s ease;
    font-size: 0.9rem;
  }

  .expand-btn:hover {
    background: rgba(100, 181, 246, 0.2);
    border-color: rgba(100, 181, 246, 0.5);
  }

  /* Expanded Views */
  .expanded-view {
    height: 100%;
    width: 100%;
    display: flex;
    flex-direction: column;
  }

  .view-header {
    margin-bottom: 2rem;
    padding-bottom: 1rem;
    border-bottom: 1px solid rgba(100, 181, 246, 0.2);
  }

  .view-header h2 {
    margin: 0 0 0.5rem 0;
    color: #64b5f6;
    font-size: 1.8rem;
    font-weight: 700;
  }

  .component-container {
    flex: 1;
    background: rgba(0, 0, 0, 0.2);
    border: 1px solid rgba(100, 181, 246, 0.2);
    border-radius: 16px;
    padding: 1.5rem;
    overflow: auto;
    min-height: 0;
    max-height: 100%;
  }

  .query-layout {
    display: grid;
    grid-template-columns: 2fr 1fr;
    gap: 1.5rem;
    height: 100%;
    min-height: 0;
  }

  .query-main, .query-sidebar {
    background: rgba(0, 0, 0, 0.2);
    border: 1px solid rgba(100, 181, 246, 0.2);
    border-radius: 16px;
    padding: 1.5rem;
    overflow: auto;
    min-height: 0;
    max-height: 100%;
  }

  /* Knowledge Preview */
  .graph-stats {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 1rem;
    margin-top: 1rem;
  }

  .stat-item {
    text-align: center;
    background: rgba(0, 0, 0, 0.3);
    padding: 1rem;
    border-radius: 10px;
  }

  .stat-item .value {
    display: block;
    font-size: 1.5rem;
    font-weight: 700;
    color: #64b5f6;
    margin-bottom: 0.25rem;
  }

  .stat-item .label {
    font-size: 0.9rem;
    opacity: 0.7;
  }

  /* Alert overlay */
  .alert-overlay {
    position: fixed;
    top: 100px;
    right: 2rem;
    z-index: 1000;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .alert {
    display: flex;
    align-items: flex-start;
    gap: 0.75rem;
    padding: 1rem;
    background: rgba(20, 25, 40, 0.95);
    border-radius: 8px;
    border-left: 4px solid;
    backdrop-filter: blur(20px);
    max-width: 400px;
    animation: slideIn 0.3s ease;
  }

  .alert-warning {
    border-left-color: #ffa726;
  }

  .alert-error {
    border-left-color: #ef5350;
  }

  .alert-info {
    border-left-color: #64b5f6;
  }

  .alert-icon {
    font-size: 1.2rem;
    flex-shrink: 0;
  }

  .alert-title {
    font-weight: 600;
    color: #e1e5e9;
    margin-bottom: 0.25rem;
  }

  .alert-message {
    font-size: 0.9rem;
    color: #a0a9b8;
  }

  /* Insights and Knowledge Preview Content */
  .insights-preview, .knowledge-preview {
    flex: 1;
    display: flex;
    flex-direction: column;
    min-height: 0;
    overflow: hidden;
  }

  .insights-preview {
    background: rgba(100, 181, 246, 0.05);
    border-radius: 12px;
    padding: 1rem;
    border: 1px dashed rgba(100, 181, 246, 0.2);
  }

  /* Empty state styling */
  .insights-preview:empty::before {
    content: "💭 Process insights will appear here when system is processing...";
    color: rgba(225, 229, 233, 0.6);
    font-style: italic;
    text-align: center;
    display: block;
    padding: 2rem;
  }

  /* Animations */
  @keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
  }

  @keyframes slideIn {
    from {
      opacity: 0;
      transform: translateY(10px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }

  @keyframes fadeInContent {
    from {
      opacity: 0;
      transform: translateY(10px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }

  /* Loading and transition effects */
  .nav-item, .expand-btn, .sidebar-toggle, .fullscreen-toggle {
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  }

  .dashboard-layout, .expanded-view, .query-layout {
    opacity: 0;
    animation: fadeInContent 0.3s ease forwards;
  }

  /* Responsive Design */
  @media (max-width: 1200px) {
    .dashboard-top, .dashboard-middle, .dashboard-bottom {
      grid-template-columns: 1fr;
      gap: 1rem;
    }
    
    .dashboard-layout {
      gap: 1rem;
    }
    
    .query-layout {
      grid-template-columns: 1fr;
      grid-template-rows: 1fr 1fr;
      gap: 1rem;
    }

    .main-content {
      padding: 0.5rem;
    }
  }

  @media (max-width: 768px) {
    .sidebar:not(.collapsed) {
      width: 100%;
      position: absolute;
      z-index: 200;
      height: 100%;
    }
    
    .header-content {
      padding: 0 1rem;
    }
    
    .main-content {
      padding: 0.5rem;
      margin: 0.25rem;
    }

    .dashboard-layout {
      gap: 0.75rem;
    }
    
    .query-panel, .response-panel, .cognitive-panel, .evolution-panel,
    .insights-panel, .knowledge-preview-panel {
      padding: 1rem;
    }

    .header-center {
      display: none; /* Hide view indicator on mobile to save space */
    }
  }
</style>
