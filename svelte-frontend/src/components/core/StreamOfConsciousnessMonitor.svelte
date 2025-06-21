<script>
    import { onMount, onDestroy } from 'svelte';
    import { enhancedCognitive } from '../../stores/enhanced-cognitive.js';
    import { writable } from 'svelte/store';

    // Component props
    export let maxEvents = 100;
    export let showFilters = true;
    export let autoScroll = true;
    export let compactMode = false;

    // Local reactive state
    let streamEvents = [];
    let filteredEvents = [];
    let selectedEventTypes = new Set(['reasoning', 'knowledge_gap', 'acquisition', 'reflection']);
    let selectedGranularities = new Set(['detailed', 'summary', 'minimal']);
    let searchTerm = '';
    let isExpanded = true;
    let eventContainer;

    // Subscriptions
    let unsubscribe;
    let streamUnsubscribe;

    onMount(() => {
        // Subscribe to cognitive state
        unsubscribe = enhancedCognitive.subscribe(state => {
            if (state.streaming.isConnected) {
                streamEvents = state.streaming.eventHistory.slice(-maxEvents);
                filterEvents();
            }
        });

        // Subscribe to real-time stream events
        streamUnsubscribe = enhancedCognitive.subscribeToStream((event) => {
            streamEvents = [...streamEvents.slice(-(maxEvents-1)), event];
            filterEvents();
            
            if (autoScroll && eventContainer) {
                setTimeout(() => {
                    eventContainer.scrollTop = eventContainer.scrollHeight;
                }, 50);
            }
        });

        // Start streaming if not already connected
        enhancedCognitive.startCognitiveStreaming();
    });

    onDestroy(() => {
        if (unsubscribe) unsubscribe();
        if (streamUnsubscribe) streamUnsubscribe();
    });

    function filterEvents() {
        filteredEvents = streamEvents.filter(event => {
            const typeMatch = selectedEventTypes.has(event.event_type);
            const granularityMatch = selectedGranularities.has(event.granularity);
            const searchMatch = !searchTerm || 
                event.content.toLowerCase().includes(searchTerm.toLowerCase()) ||
                event.event_type.toLowerCase().includes(searchTerm.toLowerCase());
            
            return typeMatch && granularityMatch && searchMatch;
        });
    }

    function toggleEventType(type) {
        if (selectedEventTypes.has(type)) {
            selectedEventTypes.delete(type);
        } else {
            selectedEventTypes.add(type);
        }
        selectedEventTypes = selectedEventTypes;
        filterEvents();
    }

    function toggleGranularity(granularity) {
        if (selectedGranularities.has(granularity)) {
            selectedGranularities.delete(granularity);
        } else {
            selectedGranularities.add(granularity);
        }
        selectedGranularities = selectedGranularities;
        filterEvents();
    }

    function clearEvents() {
        enhancedCognitive.clearEventHistory();
        streamEvents = [];
        filteredEvents = [];
    }

    function exportEvents() {
        const data = JSON.stringify(streamEvents, null, 2);
        const blob = new Blob([data], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `cognitive-stream-${new Date().toISOString()}.json`;
        a.click();
        URL.revokeObjectURL(url);
    }

    function getEventIcon(eventType) {
        switch (eventType) {
            case 'reasoning': return '🧠';
            case 'knowledge_gap': return '❓';
            case 'acquisition': return '📚';
            case 'reflection': return '🤔';
            case 'learning': return '💡';
            case 'synthesis': return '🔄';
            default: return '💭';
        }
    }

    function getEventColor(eventType) {
        switch (eventType) {
            case 'reasoning': return 'text-blue-600';
            case 'knowledge_gap': return 'text-yellow-600';
            case 'acquisition': return 'text-green-600';
            case 'reflection': return 'text-purple-600';
            case 'learning': return 'text-indigo-600';
            case 'synthesis': return 'text-teal-600';
            default: return 'text-gray-600';
        }
    }

    function formatTimestamp(timestamp) {
        return new Date(timestamp).toLocaleTimeString();
    }

    function getGranularityBadge(granularity) {
        const colors = {
            'detailed': 'bg-blue-100 text-blue-800',
            'summary': 'bg-green-100 text-green-800',
            'minimal': 'bg-gray-100 text-gray-800'
        };
        return colors[granularity] || 'bg-gray-100 text-gray-800';
    }
</script>

<div class="stream-monitor {compactMode ? 'compact' : 'full'}">
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
                Stream of Consciousness
            </h3>
            <div class="flex items-center space-x-1 text-sm text-gray-500">
                <span class="w-2 h-2 bg-green-400 rounded-full animate-pulse"></span>
                <span>{filteredEvents.length} events</span>
            </div>
        </div>
        
        <div class="flex items-center space-x-2">
            <button
                on:click={clearEvents}
                class="px-3 py-1 text-sm text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded"
                title="Clear events"
            >
                Clear
            </button>
            <button
                on:click={exportEvents}
                class="px-3 py-1 text-sm text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded"
                title="Export events"
            >
                Export
            </button>
            <label class="flex items-center space-x-1 text-sm">
                <input 
                    type="checkbox" 
                    bind:checked={autoScroll}
                    class="w-4 h-4"
                />
                <span>Auto-scroll</span>
            </label>
        </div>
    </div>

    {#if isExpanded}
        <!-- Filters -->
        {#if showFilters}
            <div class="p-4 bg-gray-50 border-b border-gray-200 space-y-3">
                <!-- Search -->
                <div>
                    <input
                        type="text"
                        bind:value={searchTerm}
                        on:input={filterEvents}
                        placeholder="Search events..."
                        class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                </div>

                <!-- Event Type Filters -->
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Event Types:</label>
                    <div class="flex flex-wrap gap-2">
                        {#each ['reasoning', 'knowledge_gap', 'acquisition', 'reflection', 'learning', 'synthesis'] as type}
                            <button
                                on:click={() => toggleEventType(type)}
                                class="px-3 py-1 text-sm rounded-full border transition-colors
                                    {selectedEventTypes.has(type) 
                                        ? 'bg-blue-100 border-blue-300 text-blue-800' 
                                        : 'bg-white border-gray-300 text-gray-600 hover:bg-gray-50'}"
                            >
                                {getEventIcon(type)} {type.replace('_', ' ')}
                            </button>
                        {/each}
                    </div>
                </div>

                <!-- Granularity Filters -->
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Granularity:</label>
                    <div class="flex gap-2">
                        {#each ['detailed', 'summary', 'minimal'] as granularity}
                            <button
                                on:click={() => toggleGranularity(granularity)}
                                class="px-3 py-1 text-sm rounded border transition-colors
                                    {selectedGranularities.has(granularity) 
                                        ? 'bg-green-100 border-green-300 text-green-800' 
                                        : 'bg-white border-gray-300 text-gray-600 hover:bg-gray-50'}"
                            >
                                {granularity}
                            </button>
                        {/each}
                    </div>
                </div>
            </div>
        {/if}

        <!-- Event Stream -->
        <div 
            bind:this={eventContainer}
            class="overflow-y-auto {compactMode ? 'h-64' : 'h-96'} bg-white"
        >
            {#if filteredEvents.length === 0}
                <div class="flex items-center justify-center h-full text-gray-500">
                    <div class="text-center">
                        <div class="text-4xl mb-2">🧠</div>
                        <p>No cognitive events to display</p>
                        <p class="text-sm mt-1">
                            {streamEvents.length === 0 ? 'Waiting for stream...' : 'Try adjusting filters'}
                        </p>
                    </div>
                </div>
            {:else}
                <div class="divide-y divide-gray-100">
                    {#each filteredEvents as event, index (event.id || index)}
                        <div class="p-4 hover:bg-gray-50 transition-colors">
                            <div class="flex items-start space-x-3">
                                <div class="flex-shrink-0 text-lg">
                                    {getEventIcon(event.event_type)}
                                </div>
                                
                                <div class="flex-1 min-w-0">
                                    <div class="flex items-center justify-between mb-1">
                                        <div class="flex items-center space-x-2">
                                            <span class="font-medium {getEventColor(event.event_type)}">
                                                {event.event_type.replace('_', ' ')}
                                            </span>
                                            <span class="px-2 py-1 text-xs rounded {getGranularityBadge(event.granularity)}">
                                                {event.granularity}
                                            </span>
                                        </div>
                                        <span class="text-xs text-gray-500">
                                            {formatTimestamp(event.timestamp)}
                                        </span>
                                    </div>
                                    
                                    <p class="text-sm text-gray-700 leading-relaxed">
                                        {event.content}
                                    </p>
                                    
                                    {#if event.metadata && Object.keys(event.metadata).length > 0}
                                        <div class="mt-2 text-xs text-gray-500">
                                            {#each Object.entries(event.metadata) as [key, value]}
                                                <span class="inline-block mr-3">
                                                    <strong>{key}:</strong> {JSON.stringify(value)}
                                                </span>
                                            {/each}
                                        </div>
                                    {/if}
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
    .stream-monitor {
        @apply border border-gray-200 rounded-lg bg-white shadow-sm;
    }
    
    .stream-monitor.compact {
        @apply text-sm;
    }
    
    .stream-monitor.full {
        @apply min-h-96;
    }
</style>
