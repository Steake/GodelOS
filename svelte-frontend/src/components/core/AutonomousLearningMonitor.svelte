<script>
    import { onMount, onDestroy } from 'svelte';
    import { enhancedCognitive } from '../../stores/enhanced-cognitive.js';
    import { writable } from 'svelte/store';

    // Component props
    export let compactMode = false;
    export let showDetails = true;
    export let autoRefresh = true;
    export let refreshInterval = 5000;

    // Local state
    let learningState = null;
    let acquisitionHistory = [];
    let knowledgeGaps = [];
    let autonomousPlans = [];
    let isExpanded = true;
    let refreshTimer;

    // Reactive derived state
    $: activeAcquisitions = acquisitionHistory.filter(a => a.status === 'active').length;
    $: completedAcquisitions = acquisitionHistory.filter(a => a.status === 'completed').length;
    $: failedAcquisitions = acquisitionHistory.filter(a => a.status === 'failed').length;
    $: highPriorityGaps = knowledgeGaps.filter(g => g.priority === 'high').length;

    // Subscriptions
    let unsubscribe;

    onMount(() => {
        // Subscribe to cognitive state
        unsubscribe = enhancedCognitive.subscribe(state => {
            learningState = state.autonomous;
            acquisitionHistory = state.autonomous.acquisitionHistory || [];
            knowledgeGaps = state.autonomous.currentGaps || [];
            autonomousPlans = state.autonomous.activePlans || [];
        });

        // Set up auto refresh
        if (autoRefresh) {
            refreshTimer = setInterval(() => {
                enhancedCognitive.refreshAutonomousState();
            }, refreshInterval);
        }

        // Initial data load
        enhancedCognitive.refreshAutonomousState();
    });

    onDestroy(() => {
        if (unsubscribe) unsubscribe();
        if (refreshTimer) clearInterval(refreshTimer);
    });

    function triggerManualAcquisition(gap) {
        enhancedCognitive.triggerManualAcquisition(gap.concept, gap.context);
    }

    function pauseAutonomousLearning() {
        enhancedCognitive.pauseAutonomousLearning();
    }

    function resumeAutonomousLearning() {
        enhancedCognitive.resumeAutonomousLearning();
    }

    function adjustLearningRate(rate) {
        enhancedCognitive.updateLearningConfiguration({ learning_rate: rate });
    }

    function getStatusColor(status) {
        switch (status) {
            case 'active': return 'text-blue-600 bg-blue-100';
            case 'completed': return 'text-green-600 bg-green-100';
            case 'failed': return 'text-red-600 bg-red-100';
            case 'paused': return 'text-yellow-600 bg-yellow-100';
            default: return 'text-gray-600 bg-gray-100';
        }
    }

    function getPriorityColor(priority) {
        switch (priority) {
            case 'high': return 'text-red-600 bg-red-100';
            case 'medium': return 'text-yellow-600 bg-yellow-100';
            case 'low': return 'text-green-600 bg-green-100';
            default: return 'text-gray-600 bg-gray-100';
        }
    }

    function formatDuration(seconds) {
        if (seconds < 60) return `${seconds}s`;
        if (seconds < 3600) return `${Math.floor(seconds / 60)}m`;
        return `${Math.floor(seconds / 3600)}h ${Math.floor((seconds % 3600) / 60)}m`;
    }

    function formatTimestamp(timestamp) {
        return new Date(timestamp).toLocaleString();
    }
</script>

<div class="learning-monitor {compactMode ? 'compact' : 'full'}">
    <!-- Header -->
    <div class="flex items-center justify-between p-4 border-b border-gray-200">
        <div class="flex items-center space-x-2">
            <button 
                on:click={() => isExpanded = !isExpanded}
                class="text-gray-500 hover:text-gray-700"
            >
                {isExpanded ? '📉' : '📈'}
            </button>
            <h3 class="text-lg font-semibold text-gray-800">
                Autonomous Learning Monitor
            </h3>
            <div class="flex items-center space-x-1 text-sm">
                <span class="w-2 h-2 rounded-full {learningState?.isEnabled ? 'bg-green-400 animate-pulse' : 'bg-gray-400'}"></span>
                <span class="text-gray-500">
                    {learningState?.isEnabled ? 'Active' : 'Inactive'}
                </span>
            </div>
        </div>
        
        <div class="flex items-center space-x-2">
            {#if learningState?.isEnabled}
                <button
                    on:click={pauseAutonomousLearning}
                    class="px-3 py-1 text-sm bg-yellow-100 text-yellow-800 rounded hover:bg-yellow-200"
                >
                    Pause
                </button>
            {:else}
                <button
                    on:click={resumeAutonomousLearning}
                    class="px-3 py-1 text-sm bg-green-100 text-green-800 rounded hover:bg-green-200"
                >
                    Resume
                </button>
            {/if}
            
            <button
                on:click={() => enhancedCognitive.refreshAutonomousState()}
                class="px-3 py-1 text-sm text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded"
                title="Refresh"
            >
                🔄
            </button>
        </div>
    </div>

    {#if isExpanded}
        <!-- Overview Stats -->
        <div class="p-4 bg-gray-50 border-b border-gray-200">
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
                <div class="bg-white p-3 rounded-lg shadow-sm">
                    <div class="text-2xl font-bold text-blue-600">{activeAcquisitions}</div>
                    <div class="text-sm text-gray-600">Active</div>
                </div>
                <div class="bg-white p-3 rounded-lg shadow-sm">
                    <div class="text-2xl font-bold text-green-600">{completedAcquisitions}</div>
                    <div class="text-sm text-gray-600">Completed</div>
                </div>
                <div class="bg-white p-3 rounded-lg shadow-sm">
                    <div class="text-2xl font-bold text-red-600">{highPriorityGaps}</div>
                    <div class="text-sm text-gray-600">High Priority Gaps</div>
                </div>
                <div class="bg-white p-3 rounded-lg shadow-sm">
                    <div class="text-2xl font-bold text-purple-600">{autonomousPlans.length}</div>
                    <div class="text-sm text-gray-600">Active Plans</div>
                </div>
            </div>
        </div>

        <!-- Learning Configuration -->
        {#if showDetails && learningState}
            <div class="p-4 border-b border-gray-200">
                <h4 class="font-medium text-gray-800 mb-3">Configuration</h4>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                    <div>
                        <label class="block text-gray-600 mb-1">Learning Rate</label>
                        <div class="flex items-center space-x-2">
                            <input
                                type="range"
                                min="0.1"
                                max="2.0"
                                step="0.1"
                                value={learningState.config?.learning_rate || 1.0}
                                on:change={(e) => adjustLearningRate(parseFloat(e.target.value))}
                                class="flex-1"
                            />
                            <span class="w-12 text-right">{learningState.config?.learning_rate || 1.0}</span>
                        </div>
                    </div>
                    
                    <div>
                        <label class="block text-gray-600 mb-1">Gap Detection Sensitivity</label>
                        <div class="text-gray-800">
                            {learningState.config?.gap_detection_sensitivity || 'medium'}
                        </div>
                    </div>
                    
                    <div>
                        <label class="block text-gray-600 mb-1">Max Concurrent Acquisitions</label>
                        <div class="text-gray-800">
                            {learningState.config?.max_concurrent_acquisitions || 3}
                        </div>
                    </div>
                    
                    <div>
                        <label class="block text-gray-600 mb-1">Auto Trigger Threshold</label>
                        <div class="text-gray-800">
                            {learningState.config?.auto_trigger_threshold || 0.7}
                        </div>
                    </div>
                </div>
            </div>
        {/if}

        <!-- Knowledge Gaps -->
        <div class="p-4 border-b border-gray-200">
            <div class="flex items-center justify-between mb-3">
                <h4 class="font-medium text-gray-800">Knowledge Gaps</h4>
                <span class="text-sm text-gray-500">{knowledgeGaps.length} identified</span>
            </div>
            
            {#if knowledgeGaps.length === 0}
                <div class="text-center py-4 text-gray-500">
                    <div class="text-2xl mb-2">✅</div>
                    <p>No knowledge gaps detected</p>
                </div>
            {:else}
                <div class="space-y-3 max-h-64 overflow-y-auto">
                    {#each knowledgeGaps.slice(0, 10) as gap}
                        <div class="bg-white p-3 rounded border border-gray-200 hover:border-gray-300 transition-colors">
                            <div class="flex items-start justify-between">
                                <div class="flex-1">
                                    <div class="flex items-center space-x-2 mb-1">
                                        <span class="font-medium text-gray-800">{gap.concept}</span>
                                        <span class="px-2 py-1 text-xs rounded {getPriorityColor(gap.priority)}">
                                            {gap.priority}
                                        </span>
                                        <span class="text-xs text-gray-500">
                                            Confidence: {(gap.confidence * 100).toFixed(0)}%
                                        </span>
                                    </div>
                                    <p class="text-sm text-gray-600 mb-2">{gap.context}</p>
                                    {#if gap.suggestedSources && gap.suggestedSources.length > 0}
                                        <div class="text-xs text-gray-500">
                                            Sources: {gap.suggestedSources.join(', ')}
                                        </div>
                                    {/if}
                                </div>
                                <button
                                    on:click={() => triggerManualAcquisition(gap)}
                                    class="ml-3 px-3 py-1 text-xs bg-blue-100 text-blue-800 rounded hover:bg-blue-200 transition-colors"
                                >
                                    Learn Now
                                </button>
                            </div>
                        </div>
                    {/each}
                </div>
            {/if}
        </div>

        <!-- Active Acquisition Plans -->
        <div class="p-4 border-b border-gray-200">
            <div class="flex items-center justify-between mb-3">
                <h4 class="font-medium text-gray-800">Active Plans</h4>
                <span class="text-sm text-gray-500">{autonomousPlans.length} running</span>
            </div>
            
            {#if autonomousPlans.length === 0}
                <div class="text-center py-4 text-gray-500">
                    <div class="text-2xl mb-2">💤</div>
                    <p>No active acquisition plans</p>
                </div>
            {:else}
                <div class="space-y-3 max-h-64 overflow-y-auto">
                    {#each autonomousPlans as plan}
                        <div class="bg-white p-3 rounded border border-gray-200">
                            <div class="flex items-start justify-between mb-2">
                                <div>
                                    <div class="font-medium text-gray-800">{plan.target_concept}</div>
                                    <div class="text-sm text-gray-600">{plan.strategy}</div>
                                </div>
                                <span class="px-2 py-1 text-xs rounded {getStatusColor(plan.status)}">
                                    {plan.status}
                                </span>
                            </div>
                            
                            {#if plan.progress}
                                <div class="mb-2">
                                    <div class="flex justify-between text-xs text-gray-600 mb-1">
                                        <span>Progress</span>
                                        <span>{(plan.progress * 100).toFixed(0)}%</span>
                                    </div>
                                    <div class="w-full bg-gray-200 rounded-full h-2">
                                        <div 
                                            class="bg-blue-600 h-2 rounded-full transition-all duration-300"
                                            style="width: {plan.progress * 100}%"
                                        ></div>
                                    </div>
                                </div>
                            {/if}
                            
                            <div class="text-xs text-gray-500">
                                Started: {formatTimestamp(plan.created_at)}
                                {#if plan.estimated_duration}
                                    • ETA: {formatDuration(plan.estimated_duration)}
                                {/if}
                            </div>
                        </div>
                    {/each}
                </div>
            {/if}
        </div>

        <!-- Recent Acquisition History -->
        <div class="p-4">
            <div class="flex items-center justify-between mb-3">
                <h4 class="font-medium text-gray-800">Recent Activity</h4>
                <span class="text-sm text-gray-500">{acquisitionHistory.length} total</span>
            </div>
            
            {#if acquisitionHistory.length === 0}
                <div class="text-center py-4 text-gray-500">
                    <div class="text-2xl mb-2">📚</div>
                    <p>No acquisition history</p>
                </div>
            {:else}
                <div class="space-y-2 max-h-64 overflow-y-auto">
                    {#each acquisitionHistory.slice(-10).reverse() as acquisition}
                        <div class="flex items-center justify-between p-2 bg-gray-50 rounded text-sm">
                            <div class="flex-1">
                                <div class="font-medium text-gray-800">{acquisition.concept}</div>
                                <div class="text-gray-600">{acquisition.strategy}</div>
                            </div>
                            <div class="text-right">
                                <span class="px-2 py-1 text-xs rounded {getStatusColor(acquisition.status)}">
                                    {acquisition.status}
                                </span>
                                <div class="text-xs text-gray-500 mt-1">
                                    {formatTimestamp(acquisition.timestamp)}
                                </div>
                            </div>
                        </div>
                    {/each}
                </div>
            {/if}
        </div>
    {/if}
</div>

<style>
    .learning-monitor {
        @apply border border-gray-200 rounded-lg bg-white shadow-sm;
    }
    
    .learning-monitor.compact {
        @apply text-sm;
    }
    
    .learning-monitor.full {
        @apply min-h-96;
    }
</style>
