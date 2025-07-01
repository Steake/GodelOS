/**
 * Cognitive Layers Module
 * Manages the cognitive architecture layers and their interactions
 */

class CognitiveLayers {
    constructor(containerId = '#cognitiveLayers') {
        this.containerId = containerId;
        this.layers = new Map();
        this.isInitialized = false;
        this.eventListeners = new Map();
        
        console.log('🧠 Cognitive Layers module loaded');
        this.init();
    }

    /**
     * Initialize the cognitive layers system
     */
    async init() {
        try {
            this.setupLayers();
            this.setupEventHandlers();
            this.isInitialized = true;
            console.log('✅ Cognitive Layers initialized successfully');
        } catch (error) {
            console.error('❌ Failed to initialize Cognitive Layers:', error);
        }
    }

    /**
     * Setup the cognitive layers
     */
    setupLayers() {
        // Define the cognitive layers
        this.layers.set('perception', {
            name: 'Perception Layer',
            active: true,
            processes: ['sensory_input', 'pattern_recognition', 'feature_extraction']
        });

        this.layers.set('attention', {
            name: 'Attention Layer',
            active: true,
            processes: ['focus_management', 'relevance_filtering', 'priority_assignment']
        });

        this.layers.set('memory', {
            name: 'Memory Layer',
            active: true,
            processes: ['encoding', 'storage', 'retrieval', 'consolidation']
        });

        this.layers.set('reasoning', {
            name: 'Reasoning Layer',
            active: true,
            processes: ['logical_inference', 'analogical_reasoning', 'causal_reasoning']
        });

        this.layers.set('metacognition', {
            name: 'Metacognitive Layer',
            active: true,
            processes: ['self_monitoring', 'strategy_selection', 'cognitive_control']
        });

        console.log('🧠 Cognitive layers configured:', Array.from(this.layers.keys()));
    }

    /**
     * Setup event handlers
     */
    setupEventHandlers() {
        // Listen for cognitive state changes
        this.on('layerActivation', (data) => {
            this.handleLayerActivation(data);
        });

        this.on('processUpdate', (data) => {
            this.handleProcessUpdate(data);
        });
    }

    /**
     * Activate a specific cognitive layer
     */
    activateLayer(layerName) {
        if (this.layers.has(layerName)) {
            const layer = this.layers.get(layerName);
            layer.active = true;
            this.emit('layerActivation', { layer: layerName, active: true });
            console.log(`🧠 Activated cognitive layer: ${layerName}`);
        } else {
            console.warn(`⚠️ Unknown cognitive layer: ${layerName}`);
        }
    }

    /**
     * Deactivate a specific cognitive layer
     */
    deactivateLayer(layerName) {
        if (this.layers.has(layerName)) {
            const layer = this.layers.get(layerName);
            layer.active = false;
            this.emit('layerActivation', { layer: layerName, active: false });
            console.log(`🧠 Deactivated cognitive layer: ${layerName}`);
        } else {
            console.warn(`⚠️ Unknown cognitive layer: ${layerName}`);
        }
    }

    /**
     * Get the current state of all layers
     */
    getLayerStates() {
        const states = {};
        for (const [name, layer] of this.layers) {
            states[name] = {
                active: layer.active,
                processes: layer.processes
            };
        }
        return states;
    }

    /**
     * Update cognitive processing state
     */
    updateProcessingState(layerName, processName, state) {
        if (this.layers.has(layerName)) {
            this.emit('processUpdate', {
                layer: layerName,
                process: processName,
                state: state
            });
        }
    }

    /**
     * Handle layer activation events
     */
    handleLayerActivation(data) {
        console.log(`🧠 Layer activation event:`, data);
        // Update UI or other systems as needed
    }

    /**
     * Handle process update events
     */
    handleProcessUpdate(data) {
        console.log(`🧠 Process update event:`, data);
        // Update cognitive state tracking
    }

    /**
     * Event emitter functionality
     */
    on(event, callback) {
        if (!this.eventListeners.has(event)) {
            this.eventListeners.set(event, []);
        }
        this.eventListeners.get(event).push(callback);
    }

    emit(event, data) {
        if (this.eventListeners.has(event)) {
            this.eventListeners.get(event).forEach(callback => {
                try {
                    callback(data);
                } catch (error) {
                    console.error(`Error in event listener for ${event}:`, error);
                }
            });
        }
    }

    /**
     * Get cognitive layer metrics
     */
    getMetrics() {
        return {
            totalLayers: this.layers.size,
            activeLayers: Array.from(this.layers.values()).filter(layer => layer.active).length,
            layerStates: this.getLayerStates(),
            isInitialized: this.isInitialized
        };
    }

    /**
     * Cleanup resources
     */
    destroy() {
        this.eventListeners.clear();
        this.layers.clear();
        this.isInitialized = false;
        console.log('🧠 Cognitive Layers destroyed');
    }
}

// Make the class available globally
window.CognitiveLayers = CognitiveLayers;

console.log('✅ Cognitive Layers module loaded and available as window.CognitiveLayers');