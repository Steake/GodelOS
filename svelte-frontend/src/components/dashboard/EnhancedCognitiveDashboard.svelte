<script>
    import { onMount, onDestroy } from 'svelte';
    import { enhancedCognitive } from '../../stores/enhanced-cognitive.js';
    import StreamOfConsciousnessMonitor from '../core/StreamOfConsciousnessMonitor.svelte';
    import AutonomousLearningMonitor from '../core/AutonomousLearningMonitor.svelte';
    import CognitiveStateMonitor from '../core/CognitiveStateMonitor.svelte';

    // Component props
    export let layout = 'grid'; // 'grid', 'tabs', 'accordion'
    export let compactMode = false;
    export let showHealth = true;
    export let autoRefresh = true;

    // Local state
    let cognitiveState = null;
    let systemHealth = null;
    let activeTab = 'overview';
    let isConnected = false;
    let lastUpdate = null;
    let isLoading = true;

    // Subscriptions
    let unsubscribe;

    onMount(() => {
        // Subscribe to cognitive state
        unsubscribe = enhancedCognitive.subscribe(state => {
            cognitiveState = state;
            systemHealth = state.systemHealth;
            isConnected = state.cognitiveStreaming?.connected || false;
            lastUpdate = new Date();
            isLoading = false;
        });

        // Initialize enhanced cognitive systems
        enhancedCognitive.initializeEnhancedSystems();
    });

    onDestroy(() => {
        if (unsubscribe) unsubscribe();
    });

    function getHealthStatus() {
        if (!systemHealth) return { status: 'unknown', color: 'gray', score: 0 };
        
        const components = [
            systemHealth?.inferenceEngine,
            systemHealth?.knowledgeStore,
            systemHealth?.autonomousLearning,
            systemHealth?.cognitiveStreaming
        ];
        
        const healthy = components.filter(c => c === 'healthy').length;
        const total = components.length;
        const score = total > 0 ? (healthy / total) * 100 : 0;
        
        if (healthy === total) return { status: 'excellent', color: 'emerald', score };
        if (healthy >= total * 0.75) return { status: 'good', color: 'amber', score };
        if (healthy >= total * 0.5) return { status: 'degraded', color: 'orange', score };
        return { status: 'critical', color: 'red', score };
    }

    function formatUptime(seconds) {
        if (!seconds) return 'Unknown';
        const hours = Math.floor(seconds / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        return `${hours}h ${minutes}m`;
    }

    function refreshAllSystems() {
        isLoading = true;
        enhancedCognitive.refreshSystemHealth();
        enhancedCognitive.refreshAutonomousState();
        enhancedCognitive.refreshStreamingState();
        setTimeout(() => isLoading = false, 1000);
    }

    $: healthStatus = getHealthStatus();
</script>

<div class="enhanced-dashboard" data-testid="enhanced-cognitive-dashboard">
    <!-- Modern Header with Glassmorphism -->
    <header class="dashboard-header">
        <div class="header-content">
            <div class="header-info">
                <div class="header-title">
                    <div class="title-icon">🧠</div>
                    <div>
                        <h1 class="title">Enhanced Cognitive Dashboard</h1>
                        <p class="subtitle">Real-time monitoring of autonomous cognitive processes</p>
                    </div>
                </div>
                
                <div class="header-stats">
                    <div class="stat-item">
                        <div class="stat-indicator {isConnected ? 'connected' : 'disconnected'}">
                            <div class="indicator-dot"></div>
                        </div>
                        <span class="stat-label">{isConnected ? 'Connected' : 'Disconnected'}</span>
                    </div>
                    
                    <div class="stat-item">
                        <div class="health-badge health-{healthStatus.color}">
                            <div class="health-icon">💚</div>
                            <span class="health-text">{Math.round(healthStatus.score)}%</span>
                        </div>
                        <span class="stat-label">{healthStatus.status}</span>
                    </div>
                    
                    {#if lastUpdate}
                        <div class="stat-item">
                            <div class="update-time">
                                {lastUpdate.toLocaleTimeString()}
                            </div>
                            <span class="stat-label">Last update</span>
                        </div>
                    {/if}
                </div>
            </div>
            
            <div class="header-actions">
                <button
                    on:click={refreshAllSystems}
                    class="action-btn refresh-btn"
                    class:loading={isLoading}
                    disabled={isLoading}
                >
                    <div class="btn-icon" class:spinning={isLoading}>🔄</div>
                    <span>Refresh</span>
                </button>
            </div>
        </div>
    </header>

    <!-- System Health Overview -->
    {#if showHealth && systemHealth}
        <section class="health-overview">
            <h2 class="section-title">System Health</h2>
            
            <div class="health-grid">
                <!-- Inference Engine -->
                <div class="health-card">
                    <div class="card-header">
                        <div class="card-icon">⚡</div>
                        <div class="card-info">
                            <h3 class="card-title">Inference Engine</h3>
                            <p class="card-metric">~0ms avg response</p>
                        </div>
                    </div>
                    <div class="status-indicator status-{systemHealth?.inferenceEngine === 'healthy' ? 'healthy' : 'unhealthy'}">
                        <div class="status-dot"></div>
                        <span class="status-text">{systemHealth?.inferenceEngine || 'unknown'}</span>
                    </div>
                </div>

                <!-- Knowledge Store -->
                <div class="health-card">
                    <div class="card-header">
                        <div class="card-icon">📚</div>
                        <div class="card-info">
                            <h3 class="card-title">Knowledge Store</h3>
                            <p class="card-metric">0 entities indexed</p>
                        </div>
                    </div>
                    <div class="status-indicator status-{systemHealth?.knowledgeStore === 'healthy' ? 'healthy' : 'unhealthy'}">
                        <div class="status-dot"></div>
                        <span class="status-text">{systemHealth?.knowledgeStore || 'unknown'}</span>
                    </div>
                </div>

                <!-- Autonomous Learning -->
                <div class="health-card">
                    <div class="card-header">
                        <div class="card-icon">🤖</div>
                        <div class="card-info">
                            <h3 class="card-title">Autonomous Learning</h3>
                            <p class="card-metric">0 active plans</p>
                        </div>
                    </div>
                    <div class="status-indicator status-{systemHealth?.autonomousLearning === 'healthy' ? 'healthy' : 'unhealthy'}">
                        <div class="status-dot"></div>
                        <span class="status-text">{systemHealth?.autonomousLearning || 'unknown'}</span>
                    </div>
                </div>

                <!-- Cognitive Streaming -->
                <div class="health-card">
                    <div class="card-header">
                        <div class="card-icon">🌊</div>
                        <div class="card-info">
                            <h3 class="card-title">Cognitive Streaming</h3>
                            <p class="card-metric">0 active clients</p>
                        </div>
                    </div>
                    <div class="status-indicator status-{systemHealth?.cognitiveStreaming === 'healthy' ? 'healthy' : 'unhealthy'}">
                        <div class="status-dot"></div>
                        <span class="status-text">{systemHealth?.cognitiveStreaming || 'unknown'}</span>
                    </div>
                </div>
            </div>
            
            <div class="health-footer">
                <div class="uptime-info">
                    <span class="uptime-label">System Uptime:</span>
                    <span class="uptime-value">{formatUptime(systemHealth?.uptime)}</span>
                </div>
            </div>
        </section>
    {/if}

    <!-- Main Content Area -->
    <main class="dashboard-content">
        {#if layout === 'tabs'}
            <!-- Modern Tab Navigation -->
            <nav class="tab-navigation">
                <div class="tab-list">
                    <button
                        on:click={() => activeTab = 'overview'}
                        class="tab-button"
                        class:active={activeTab === 'overview'}
                    >
                        <div class="tab-icon">📊</div>
                        <span>Overview</span>
                    </button>
                    <button
                        on:click={() => activeTab = 'consciousness'}
                        class="tab-button"
                        class:active={activeTab === 'consciousness'}
                    >
                        <div class="tab-icon">🧠</div>
                        <span>Stream of Consciousness</span>
                    </button>
                    <button
                        on:click={() => activeTab = 'learning'}
                        class="tab-button"
                        class:active={activeTab === 'learning'}
                    >
                        <div class="tab-icon">🤖</div>
                        <span>Autonomous Learning</span>
                    </button>
                    <button
                        on:click={() => activeTab = 'cognitive'}
                        class="tab-button"
                        class:active={activeTab === 'cognitive'}
                    >
                        <div class="tab-icon">🎯</div>
                        <span>Cognitive State</span>
                    </button>
                </div>
            </nav>

            <!-- Tab Content -->
            <div class="tab-content">
                {#if activeTab === 'overview'}
                    <div class="overview-panel">
                        <div class="overview-hero">
                            <h2 class="hero-title">Enhanced Cognitive Capabilities</h2>
                            <p class="hero-description">
                                Monitor and interact with advanced AI cognitive processes in real-time
                            </p>
                        </div>
                        
                        <div class="feature-grid">
                            <div class="feature-card">
                                <div class="feature-icon">🧠</div>
                                <h3 class="feature-title">Stream of Consciousness</h3>
                                <p class="feature-description">
                                    Real-time visibility into cognitive processes, reasoning patterns, and decision-making flows
                                </p>
                            </div>
                            
                            <div class="feature-card">
                                <div class="feature-icon">📚</div>
                                <h3 class="feature-title">Autonomous Learning</h3>
                                <p class="feature-description">
                                    Intelligent knowledge gap detection and autonomous acquisition strategies
                                </p>
                            </div>
                            
                            <div class="feature-card">
                                <div class="feature-icon">👁️</div>
                                <h3 class="feature-title">Cognitive Transparency</h3>
                                <p class="feature-description">
                                    Complete transparency into attention focus, processing load, and system state
                                </p>
                            </div>
                        </div>
                    </div>
                {:else if activeTab === 'consciousness'}
                    <div class="component-panel">
                        <StreamOfConsciousnessMonitor {compactMode} />
                    </div>
                {:else if activeTab === 'learning'}
                    <div class="component-panel">
                        <AutonomousLearningMonitor {compactMode} />
                    </div>
                {:else if activeTab === 'cognitive'}
                    <div class="component-panel">
                        <CognitiveStateMonitor {compactMode} />
                    </div>
                {/if}
            </div>
        {:else if layout === 'grid'}
            <!-- Modern Grid Layout -->
            <div class="grid-layout">
                <div class="grid-column">
                    <div class="component-wrapper">
                        <StreamOfConsciousnessMonitor {compactMode} />
                    </div>
                    <div class="component-wrapper">
                        <CognitiveStateMonitor {compactMode} />
                    </div>
                </div>
                <div class="grid-column">
                    <div class="component-wrapper">
                        <AutonomousLearningMonitor {compactMode} />
                    </div>
                </div>
            </div>
        {:else if layout === 'accordion'}
            <!-- Accordion Layout -->
            <div class="accordion-layout">
                <div class="accordion-item">
                    <StreamOfConsciousnessMonitor {compactMode} showFilters={false} />
                </div>
                <div class="accordion-item">
                    <AutonomousLearningMonitor {compactMode} showDetails={false} />
                </div>
                <div class="accordion-item">
                    <CognitiveStateMonitor {compactMode} />
                </div>
            </div>
        {/if}
    </main>
</div>

<style>
    .enhanced-dashboard {
        min-height: 100vh;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }

    /* Header Styles */
    .dashboard-header {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 24px;
        padding: 2rem;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    }

    .header-content {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 2rem;
    }

    .header-info {
        flex: 1;
    }

    .header-title {
        display: flex;
        align-items: center;
        gap: 1rem;
        margin-bottom: 1.5rem;
    }

    .title-icon {
        font-size: 3rem;
        filter: drop-shadow(0 4px 8px rgba(0, 0, 0, 0.2));
    }

    .title {
        font-size: 2.5rem;
        font-weight: 700;
        color: white;
        margin: 0;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
    }

    .subtitle {
        font-size: 1.125rem;
        color: rgba(255, 255, 255, 0.8);
        margin: 0.5rem 0 0 0;
        font-weight: 400;
    }

    .header-stats {
        display: flex;
        gap: 2rem;
        align-items: center;
    }

    .stat-item {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 0.5rem;
    }

    .stat-indicator {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.5rem 1rem;
        border-radius: 12px;
        background: rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }

    .indicator-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        animation: pulse 2s infinite;
    }

    .stat-indicator.connected .indicator-dot {
        background: #10b981;
    }

    .stat-indicator.disconnected .indicator-dot {
        background: #ef4444;
    }

    .health-badge {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.5rem 1rem;
        border-radius: 12px;
        background: rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }

    .health-badge.health-emerald {
        background: rgba(16, 185, 129, 0.2);
        border-color: rgba(16, 185, 129, 0.3);
    }

    .health-badge.health-amber {
        background: rgba(245, 158, 11, 0.2);
        border-color: rgba(245, 158, 11, 0.3);
    }

    .health-badge.health-red {
        background: rgba(239, 68, 68, 0.2);
        border-color: rgba(239, 68, 68, 0.3);
    }

    .health-icon {
        font-size: 1.25rem;
    }

    .health-text {
        font-weight: 600;
        color: white;
    }

    .stat-label {
        font-size: 0.875rem;
        color: rgba(255, 255, 255, 0.7);
        font-weight: 500;
    }

    .update-time {
        padding: 0.5rem 1rem;
        border-radius: 12px;
        background: rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        color: white;
        font-weight: 500;
    }

    .header-actions {
        display: flex;
        gap: 1rem;
    }

    .action-btn {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.75rem 1.5rem;
        background: rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 12px;
        color: white;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.2s ease;
        backdrop-filter: blur(10px);
    }

    .action-btn:hover:not(:disabled) {
        background: rgba(255, 255, 255, 0.2);
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
    }

    .action-btn:disabled {
        opacity: 0.6;
        cursor: not-allowed;
    }

    .btn-icon {
        font-size: 1.25rem;
        transition: transform 0.2s ease;
    }

    .btn-icon.spinning {
        animation: spin 1s linear infinite;
    }

    /* Health Overview */
    .health-overview {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 2rem;
        margin-bottom: 2rem;
    }

    .section-title {
        font-size: 1.5rem;
        font-weight: 700;
        color: white;
        margin: 0 0 1.5rem 0;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
    }

    .health-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
        gap: 1.5rem;
        margin-bottom: 2rem;
    }

    .health-card {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 16px;
        padding: 1.5rem;
        transition: all 0.2s ease;
    }

    .health-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
        background: rgba(255, 255, 255, 0.15);
    }

    .card-header {
        display: flex;
        align-items: center;
        gap: 1rem;
        margin-bottom: 1rem;
    }

    .card-icon {
        font-size: 2rem;
        filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.2));
    }

    .card-info {
        flex: 1;
    }

    .card-title {
        font-size: 1.125rem;
        font-weight: 600;
        color: white;
        margin: 0 0 0.25rem 0;
    }

    .card-metric {
        font-size: 0.875rem;
        color: rgba(255, 255, 255, 0.7);
        margin: 0;
    }

    .status-indicator {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        background: rgba(255, 255, 255, 0.05);
    }

    .status-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
    }

    .status-indicator.status-healthy .status-dot {
        background: #10b981;
        animation: pulse 2s infinite;
    }

    .status-indicator.status-unhealthy .status-dot {
        background: #ef4444;
    }

    .status-text {
        font-size: 0.875rem;
        font-weight: 500;
        color: white;
        text-transform: capitalize;
    }

    .health-footer {
        display: flex;
        justify-content: center;
        padding-top: 1rem;
        border-top: 1px solid rgba(255, 255, 255, 0.1);
    }

    .uptime-info {
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    .uptime-label {
        color: rgba(255, 255, 255, 0.7);
        font-size: 0.875rem;
    }

    .uptime-value {
        color: white;
        font-weight: 600;
        font-size: 0.875rem;
    }

    /* Main Content */
    .dashboard-content {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        overflow: hidden;
    }

    /* Tab Navigation */
    .tab-navigation {
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        padding: 0 2rem;
    }

    .tab-list {
        display: flex;
        gap: 0.5rem;
    }

    .tab-button {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        padding: 1rem 1.5rem;
        background: none;
        border: none;
        color: rgba(255, 255, 255, 0.7);
        font-weight: 500;
        cursor: pointer;
        border-radius: 12px 12px 0 0;
        transition: all 0.2s ease;
        position: relative;
    }

    .tab-button:hover {
        color: white;
        background: rgba(255, 255, 255, 0.05);
    }

    .tab-button.active {
        color: white;
        background: rgba(255, 255, 255, 0.1);
    }

    .tab-button.active::after {
        content: '';
        position: absolute;
        bottom: 0;
        left: 0;
        right: 0;
        height: 2px;
        background: linear-gradient(90deg, #10b981, #3b82f6);
    }

    .tab-icon {
        font-size: 1.25rem;
    }

    .tab-content {
        padding: 2rem;
    }

    /* Overview Panel */
    .overview-panel {
        text-align: center;
    }

    .overview-hero {
        margin-bottom: 3rem;
    }

    .hero-title {
        font-size: 2rem;
        font-weight: 700;
        color: white;
        margin: 0 0 1rem 0;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
    }

    .hero-description {
        font-size: 1.125rem;
        color: rgba(255, 255, 255, 0.8);
        margin: 0;
        max-width: 600px;
        margin-left: auto;
        margin-right: auto;
    }

    .feature-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 2rem;
    }

    .feature-card {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 16px;
        padding: 2rem;
        text-align: center;
        transition: all 0.2s ease;
    }

    .feature-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
        background: rgba(255, 255, 255, 0.15);
    }

    .feature-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
        filter: drop-shadow(0 4px 8px rgba(0, 0, 0, 0.2));
    }

    .feature-title {
        font-size: 1.25rem;
        font-weight: 600;
        color: white;
        margin: 0 0 1rem 0;
    }

    .feature-description {
        font-size: 0.875rem;
        color: rgba(255, 255, 255, 0.8);
        line-height: 1.6;
        margin: 0;
    }

    /* Component Panels */
    .component-panel {
        background: rgba(255, 255, 255, 0.02);
        border-radius: 12px;
        overflow: hidden;
    }

    /* Grid Layout */
    .grid-layout {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 2rem;
        padding: 2rem;
    }

    .grid-column {
        display: flex;
        flex-direction: column;
        gap: 2rem;
    }

    .component-wrapper {
        background: rgba(255, 255, 255, 0.02);
        border-radius: 12px;
        overflow: hidden;
    }

    /* Accordion Layout */
    .accordion-layout {
        padding: 2rem;
    }

    .accordion-item {
        background: rgba(255, 255, 255, 0.02);
        border-radius: 12px;
        margin-bottom: 1rem;
        overflow: hidden;
    }

    .accordion-item:last-child {
        margin-bottom: 0;
    }

    /* Animations */
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }

    @keyframes spin {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }

    /* Responsive Design */
    @media (max-width: 768px) {
        .enhanced-dashboard {
            padding: 1rem;
        }

        .header-content {
            flex-direction: column;
            gap: 1rem;
        }

        .header-stats {
            flex-wrap: wrap;
            gap: 1rem;
        }

        .title {
            font-size: 2rem;
        }

        .health-grid {
            grid-template-columns: 1fr;
        }

        .grid-layout {
            grid-template-columns: 1fr;
        }

        .tab-list {
            flex-wrap: wrap;
        }

        .tab-button {
            padding: 0.75rem 1rem;
            font-size: 0.875rem;
        }
    }

    @media (max-width: 480px) {
        .header-title {
            flex-direction: column;
            text-align: center;
            gap: 0.5rem;
        }

        .title-icon {
            font-size: 2rem;
        }

        .title {
            font-size: 1.5rem;
        }

        .subtitle {
            font-size: 1rem;
        }
    }
</style>
