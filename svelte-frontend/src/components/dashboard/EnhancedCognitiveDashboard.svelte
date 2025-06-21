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

    // Subscriptions
    let unsubscribe;

    onMount(() => {
        // Subscribe to cognitive state
        unsubscribe = enhancedCognitive.subscribe(state => {
            cognitiveState = state;
            systemHealth = state.health;
            isConnected = state.streaming.isConnected;
            lastUpdate = new Date();
        });

        // Initialize enhanced cognitive systems
        enhancedCognitive.initializeEnhancedSystems();
    });

    onDestroy(() => {
        if (unsubscribe) unsubscribe();
    });

    function getHealthStatus() {
        if (!systemHealth) return { status: 'unknown', color: 'gray' };
        
        const components = [
            systemHealth.inferenceEngine,
            systemHealth.knowledgeStore,
            systemHealth.autonomousLearning,
            systemHealth.cognitiveStreaming
        ];
        
        const healthy = components.filter(c => c?.status === 'healthy').length;
        const total = components.length;
        
        if (healthy === total) return { status: 'excellent', color: 'green' };
        if (healthy >= total * 0.75) return { status: 'good', color: 'yellow' };
        if (healthy >= total * 0.5) return { status: 'degraded', color: 'orange' };
        return { status: 'critical', color: 'red' };
    }

    function formatUptime(seconds) {
        if (!seconds) return 'Unknown';
        const hours = Math.floor(seconds / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        return `${hours}h ${minutes}m`;
    }

    function getConnectionStatusIcon() {
        return isConnected ? '🟢' : '🔴';
    }

    function refreshAllSystems() {
        enhancedCognitive.refreshSystemHealth();
        enhancedCognitive.refreshAutonomousState();
        enhancedCognitive.refreshStreamingState();
    }

    $: healthStatus = getHealthStatus();
</script>

<div class="enhanced-cognitive-dashboard">
    <!-- Dashboard Header -->
    <div class="dashboard-header bg-gradient-to-r from-blue-600 to-purple-600 text-white p-6 rounded-t-lg">
        <div class="flex items-center justify-between">
            <div>
                <h2 class="text-2xl font-bold mb-2">Enhanced Cognitive Dashboard</h2>
                <p class="text-blue-100">Real-time monitoring of autonomous cognitive processes</p>
            </div>
            
            <div class="text-right">
                <div class="flex items-center space-x-4 text-sm">
                    <div class="flex items-center space-x-1">
                        <span>{getConnectionStatusIcon()}</span>
                        <span>{isConnected ? 'Connected' : 'Disconnected'}</span>
                    </div>
                    <div class="flex items-center space-x-1">
                        <span>🏥</span>
                        <span class="capitalize">{healthStatus.status}</span>
                    </div>
                </div>
                {#if lastUpdate}
                    <div class="text-xs text-blue-200 mt-1">
                        Last update: {lastUpdate.toLocaleTimeString()}
                    </div>
                {/if}
            </div>
        </div>
    </div>

    <!-- System Health Overview -->
    {#if showHealth && systemHealth}
        <div class="p-4 bg-gray-50 border-b border-gray-200">
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                <!-- Inference Engine -->
                <div class="bg-white p-3 rounded-lg shadow-sm">
                    <div class="flex items-center justify-between mb-2">
                        <span class="text-sm font-medium text-gray-600">Inference</span>
                        <span class="w-3 h-3 rounded-full bg-{systemHealth.inferenceEngine?.status === 'healthy' ? 'green' : 'red'}-400"></span>
                    </div>
                    <div class="text-xs text-gray-500">
                        {systemHealth.inferenceEngine?.response_time || 'N/A'}ms avg
                    </div>
                </div>

                <!-- Knowledge Store -->
                <div class="bg-white p-3 rounded-lg shadow-sm">
                    <div class="flex items-center justify-between mb-2">
                        <span class="text-sm font-medium text-gray-600">Knowledge</span>
                        <span class="w-3 h-3 rounded-full bg-{systemHealth.knowledgeStore?.status === 'healthy' ? 'green' : 'red'}-400"></span>
                    </div>
                    <div class="text-xs text-gray-500">
                        {systemHealth.knowledgeStore?.entities || 0} entities
                    </div>
                </div>

                <!-- Autonomous Learning -->
                <div class="bg-white p-3 rounded-lg shadow-sm">
                    <div class="flex items-center justify-between mb-2">
                        <span class="text-sm font-medium text-gray-600">Learning</span>
                        <span class="w-3 h-3 rounded-full bg-{systemHealth.autonomousLearning?.status === 'healthy' ? 'green' : 'red'}-400"></span>
                    </div>
                    <div class="text-xs text-gray-500">
                        {systemHealth.autonomousLearning?.active_plans || 0} plans
                    </div>
                </div>

                <!-- Cognitive Streaming -->
                <div class="bg-white p-3 rounded-lg shadow-sm">
                    <div class="flex items-center justify-between mb-2">
                        <span class="text-sm font-medium text-gray-600">Streaming</span>
                        <span class="w-3 h-3 rounded-full bg-{systemHealth.cognitiveStreaming?.status === 'healthy' ? 'green' : 'red'}-400"></span>
                    </div>
                    <div class="text-xs text-gray-500">
                        {systemHealth.cognitiveStreaming?.connected_clients || 0} clients
                    </div>
                </div>
            </div>
            
            <div class="flex items-center justify-between mt-4">
                <div class="text-sm text-gray-600">
                    System Uptime: {formatUptime(systemHealth.uptime)}
                </div>
                <button
                    on:click={refreshAllSystems}
                    class="px-3 py-1 text-sm bg-blue-100 text-blue-800 rounded hover:bg-blue-200 transition-colors"
                >
                    🔄 Refresh
                </button>
            </div>
        </div>
    {/if}

    <!-- Layout Selection -->
    {#if layout === 'tabs'}
        <!-- Tab Navigation -->
        <div class="flex border-b border-gray-200 bg-white">
            <button
                on:click={() => activeTab = 'overview'}
                class="px-4 py-2 text-sm font-medium border-b-2 transition-colors
                    {activeTab === 'overview' 
                        ? 'border-blue-500 text-blue-600' 
                        : 'border-transparent text-gray-500 hover:text-gray-700'}"
            >
                Overview
            </button>
            <button
                on:click={() => activeTab = 'consciousness'}
                class="px-4 py-2 text-sm font-medium border-b-2 transition-colors
                    {activeTab === 'consciousness' 
                        ? 'border-blue-500 text-blue-600' 
                        : 'border-transparent text-gray-500 hover:text-gray-700'}"
            >
                Stream of Consciousness
            </button>
            <button
                on:click={() => activeTab = 'learning'}
                class="px-4 py-2 text-sm font-medium border-b-2 transition-colors
                    {activeTab === 'learning' 
                        ? 'border-blue-500 text-blue-600' 
                        : 'border-transparent text-gray-500 hover:text-gray-700'}"
            >
                Autonomous Learning
            </button>
            <button
                on:click={() => activeTab = 'cognitive'}
                class="px-4 py-2 text-sm font-medium border-b-2 transition-colors
                    {activeTab === 'cognitive' 
                        ? 'border-blue-500 text-blue-600' 
                        : 'border-transparent text-gray-500 hover:text-gray-700'}"
            >
                Cognitive State
            </button>
        </div>

        <!-- Tab Content -->
        <div class="tab-content">
            {#if activeTab === 'overview'}
                <div class="p-6 bg-white">
                    <div class="text-center">
                        <h3 class="text-lg font-semibold text-gray-800 mb-4">System Overview</h3>
                        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                            <div class="text-center">
                                <div class="text-3xl mb-2">🧠</div>
                                <div class="text-sm text-gray-600">
                                    Enhanced cognitive capabilities with autonomous learning and real-time stream of consciousness
                                </div>
                            </div>
                            <div class="text-center">
                                <div class="text-3xl mb-2">📚</div>
                                <div class="text-sm text-gray-600">
                                    Autonomous knowledge acquisition with gap detection and strategic learning
                                </div>
                            </div>
                            <div class="text-center">
                                <div class="text-3xl mb-2">👁️</div>
                                <div class="text-sm text-gray-600">
                                    Real-time transparency into cognitive processes and decision making
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            {:else if activeTab === 'consciousness'}
                <StreamOfConsciousnessMonitor {compactMode} />
            {:else if activeTab === 'learning'}
                <AutonomousLearningMonitor {compactMode} />
            {:else if activeTab === 'cognitive'}
                <CognitiveStateMonitor {compactMode} />
            {/if}
        </div>
    {:else if layout === 'grid'}
        <!-- Grid Layout -->
        <div class="grid grid-cols-1 {compactMode ? 'lg:grid-cols-2' : 'xl:grid-cols-2'} gap-6 p-6 bg-gray-50">
            <div class="space-y-6">
                <StreamOfConsciousnessMonitor {compactMode} />
                <CognitiveStateMonitor {compactMode} />
            </div>
            <div class="space-y-6">
                <AutonomousLearningMonitor {compactMode} />
            </div>
        </div>
    {:else if layout === 'accordion'}
        <!-- Accordion Layout -->
        <div class="accordion-layout bg-white">
            <div class="border-b border-gray-200">
                <StreamOfConsciousnessMonitor {compactMode} showFilters={false} />
            </div>
            <div class="border-b border-gray-200">
                <AutonomousLearningMonitor {compactMode} showDetails={false} />
            </div>
            <div>
                <CognitiveStateMonitor {compactMode} />
            </div>
        </div>
    {/if}
</div>

<style>
    .enhanced-cognitive-dashboard {
        @apply bg-white rounded-lg shadow-lg overflow-hidden;
    }
    
    .dashboard-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    .tab-content {
        @apply min-h-96;
    }
    
    .accordion-layout {
        @apply divide-y divide-gray-200;
    }
</style>
