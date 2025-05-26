/**
 * Cognitive Layers Visualization Manager for GödelOS Frontend
 * Handles real-time visualization of consciousness, agentic processes, and daemon threads
 */

class CognitiveLayers {
    constructor() {
        this.manifestData = null;
        this.agenticData = null;
        this.daemonData = null;
        this.animationFrames = new Map();
        
        this.initializeLayers();
        this.setupEventListeners();
        this.startAnimations();
    }

    /**
     * Initialize cognitive layer visualizations
     */
    initializeLayers() {
        this.initializeManifestConsciousness();
        this.initializeAgenticProcesses();
        this.initializeDaemonThreads();
    }

    /**
     * Setup event listeners for cognitive updates
     */
    setupEventListeners() {
        // Listen for cognitive updates from WebSocket
        window.addEventListener('cognitiveUpdate', (e) => {
            this.updateLayers(e.detail);
        });

        // Listen for query processing updates
        window.addEventListener('queryResponse', (e) => {
            this.handleQueryProcessing(e.detail);
        });
    }

    /**
     * Initialize manifest consciousness layer
     */
    initializeManifestConsciousness() {
        const attentionFocus = document.getElementById('attentionFocus');
        const workingMemory = document.getElementById('workingMemory');

        if (attentionFocus) {
            // Create attention focus visualization
            this.createAttentionVisualization(attentionFocus);
        }

        if (workingMemory) {
            // Initialize working memory items
            this.updateWorkingMemory(['Idle', 'Waiting for input', 'System ready']);
        }
    }

    /**
     * Create attention focus visualization
     * @param {HTMLElement} container - Container element
     */
    createAttentionVisualization(container) {
        container.innerHTML = '';
        container.className = 'attention-focus-viz';

        // Create focus beam element
        const focusBeam = document.createElement('div');
        focusBeam.className = 'focus-beam';
        container.appendChild(focusBeam);

        // Create multiple target elements for dynamic attention
        for (let i = 0; i < 3; i++) {
            const target = document.createElement('div');
            target.className = 'focus-target';
            target.style.left = `${20 + i * 30}%`;
            target.style.animationDelay = `${i * 0.5}s`;
            container.appendChild(target);
        }
    }

    /**
     * Initialize agentic processes layer
     */
    initializeAgenticProcesses() {
        const processContainer = document.getElementById('agenticProcesses');
        if (!processContainer) return;

        const defaultProcesses = [
            { name: 'Query Parser', status: 'idle' },
            { name: 'Knowledge Retriever', status: 'idle' },
            { name: 'Inference Engine', status: 'idle' },
            { name: 'Response Generator', status: 'idle' },
            { name: 'Meta-Reasoner', status: 'idle' }
        ];

        this.updateAgenticProcesses(defaultProcesses);
    }

    /**
     * Initialize daemon threads layer
     */
    initializeDaemonThreads() {
        const daemonContainer = document.getElementById('daemonThreads');
        if (!daemonContainer) return;

        const defaultDaemons = [
            { name: 'Memory Consolidation', active: false, activity_level: 20 },
            { name: 'Background Learning', active: true, activity_level: 60 },
            { name: 'System Monitoring', active: true, activity_level: 80 },
            { name: 'Knowledge Indexing', active: false, activity_level: 10 },
            { name: 'Pattern Recognition', active: true, activity_level: 40 }
        ];

        this.updateDaemonThreads(defaultDaemons);
    }

    /**
     * Update all cognitive layers with new data
     * @param {Object} data - Cognitive update data
     */
    updateLayers(data) {
        if (data.manifest_consciousness) {
            this.updateManifestConsciousness(data.manifest_consciousness);
        }
        
        if (data.agentic_processes) {
            this.updateAgenticProcesses(data.agentic_processes);
        }
        
        if (data.daemon_threads) {
            this.updateDaemonThreads(data.daemon_threads);
        }
    }

    /**
     * Update manifest consciousness visualization
     * @param {Object} data - Manifest consciousness data
     */
    updateManifestConsciousness(data) {
        this.manifestData = data;

        // Update attention focus intensity
        if (data.attention_focus !== undefined) {
            this.updateAttentionFocus(data.attention_focus);
        }

        // Update working memory contents
        if (data.working_memory) {
            this.updateWorkingMemory(data.working_memory);
        }
    }

    /**
     * Update attention focus visualization
     * @param {number} intensity - Attention intensity (0-100)
     */
    updateAttentionFocus(intensity) {
        const attentionContainer = document.getElementById('attentionFocus');
        if (!attentionContainer) return;

        const focusBeam = attentionContainer.querySelector('.focus-beam');
        if (focusBeam) {
            const opacity = Math.max(0.3, intensity / 100);
            const brightness = Math.max(0.5, intensity / 100);
            
            focusBeam.style.opacity = opacity;
            focusBeam.style.filter = `brightness(${brightness})`;
            
            // Adjust animation speed based on intensity
            const duration = Math.max(1, 5 - (intensity / 25));
            focusBeam.style.animationDuration = `${duration}s`;
        }

        // Update focus targets activity
        const targets = attentionContainer.querySelectorAll('.focus-target');
        targets.forEach((target, index) => {
            if (intensity > 50 + (index * 15)) {
                target.classList.add('active');
            } else {
                target.classList.remove('active');
            }
        });
    }

    /**
     * Update working memory contents
     * @param {Array} memoryItems - Array of memory items
     */
    updateWorkingMemory(memoryItems) {
        const workingMemory = document.getElementById('workingMemory');
        if (!workingMemory) return;

        // Clear existing items
        workingMemory.innerHTML = '';

        // Add new memory items with animation
        memoryItems.forEach((item, index) => {
            const memoryItem = document.createElement('div');
            memoryItem.className = 'memory-item fade-in';
            memoryItem.textContent = item;
            memoryItem.style.animationDelay = `${index * 0.1}s`;
            workingMemory.appendChild(memoryItem);
        });
    }

    /**
     * Update agentic processes visualization
     * @param {Array} processes - Array of process data
     */
    updateAgenticProcesses(processes) {
        this.agenticData = processes;
        const container = document.getElementById('agenticProcesses');
        if (!container) return;

        // Clear existing processes
        container.innerHTML = '';

        processes.forEach((process, index) => {
            const processItem = document.createElement('div');
            processItem.className = `process-item ${process.status === 'active' ? 'active' : ''}`;
            
            const processName = document.createElement('span');
            processName.className = 'process-name';
            processName.textContent = process.name;
            
            const processStatus = document.createElement('span');
            processStatus.className = 'process-status';
            processStatus.textContent = process.status || 'idle';
            
            // Add CPU/Memory usage if available
            if (process.cpu_usage !== undefined || process.memory_usage !== undefined) {
                const usageInfo = document.createElement('div');
                usageInfo.className = 'process-usage';
                usageInfo.innerHTML = `
                    <div class="usage-bar">
                        <div class="usage-fill" style="width: ${process.cpu_usage || 0}%"></div>
                    </div>
                    <span class="usage-text">${Math.round(process.cpu_usage || 0)}%</span>
                `;
                processItem.appendChild(usageInfo);
            }
            
            processItem.appendChild(processName);
            processItem.appendChild(processStatus);
            
            // Add animation delay
            processItem.style.animationDelay = `${index * 0.1}s`;
            processItem.classList.add('slide-in-up');
            
            container.appendChild(processItem);
        });
    }

    /**
     * Update daemon threads visualization
     * @param {Array} daemons - Array of daemon data
     */
    updateDaemonThreads(daemons) {
        this.daemonData = daemons;
        const container = document.getElementById('daemonThreads');
        if (!container) return;

        // Clear existing daemons
        container.innerHTML = '';

        daemons.forEach((daemon, index) => {
            const daemonItem = document.createElement('div');
            daemonItem.className = 'daemon-item';
            
            const daemonName = document.createElement('span');
            daemonName.className = 'daemon-name';
            daemonName.textContent = daemon.name;
            
            const daemonActivity = document.createElement('div');
            daemonActivity.className = `daemon-activity ${daemon.active ? 'active' : ''}`;
            
            // Add activity level indicator
            if (daemon.activity_level !== undefined) {
                const activityLevel = document.createElement('div');
                activityLevel.className = 'activity-level';
                activityLevel.style.width = `${daemon.activity_level}%`;
                activityLevel.style.background = this.getActivityColor(daemon.activity_level);
                daemonActivity.appendChild(activityLevel);
            }
            
            daemonItem.appendChild(daemonName);
            daemonItem.appendChild(daemonActivity);
            
            // Add animation delay
            daemonItem.style.animationDelay = `${index * 0.1}s`;
            daemonItem.classList.add('slide-in-up');
            
            container.appendChild(daemonItem);
        });
    }

    /**
     * Get activity color based on level
     * @param {number} level - Activity level (0-100)
     * @returns {string} CSS color value
     */
    getActivityColor(level) {
        if (level < 30) return '#2ed573'; // Low activity - green
        if (level < 70) return '#4facfe'; // Medium activity - blue
        return '#ff6b6b'; // High activity - red
    }

    /**
     * Handle query processing updates
     * @param {Object} queryData - Query response data
     */
    handleQueryProcessing(queryData) {
        // Simulate processing stages
        const stages = [
            'Query Parser',
            'Knowledge Retriever', 
            'Inference Engine',
            'Response Generator'
        ];

        // Activate processes in sequence
        stages.forEach((stageName, index) => {
            setTimeout(() => {
                this.activateProcess(stageName);
            }, index * 500);
        });

        // Update working memory with query context
        if (queryData.original_query) {
            const memoryItems = [
                `Query: ${queryData.original_query.substring(0, 30)}...`,
                'Processing semantic analysis',
                'Retrieving relevant knowledge',
                'Constructing reasoning chain'
            ];
            this.updateWorkingMemory(memoryItems);
        }

        // Increase attention focus during processing
        this.updateAttentionFocus(85);

        // Reset after processing
        setTimeout(() => {
            this.resetProcessingState();
        }, 3000);
    }

    /**
     * Activate a specific process
     * @param {string} processName - Name of process to activate
     */
    activateProcess(processName) {
        const container = document.getElementById('agenticProcesses');
        if (!container) return;

        const processItems = container.querySelectorAll('.process-item');
        processItems.forEach(item => {
            const nameElement = item.querySelector('.process-name');
            if (nameElement && nameElement.textContent === processName) {
                item.classList.add('active');
                const statusElement = item.querySelector('.process-status');
                if (statusElement) {
                    statusElement.textContent = 'running';
                }
                
                // Add processing animation
                item.classList.add('processing');
                setTimeout(() => {
                    item.classList.remove('processing');
                }, 1000);
            }
        });
    }

    /**
     * Reset processing state after query completion
     */
    resetProcessingState() {
        // Reset attention focus
        this.updateAttentionFocus(30);

        // Reset processes to idle
        const container = document.getElementById('agenticProcesses');
        if (container) {
            const processItems = container.querySelectorAll('.process-item');
            processItems.forEach(item => {
                item.classList.remove('active');
                const statusElement = item.querySelector('.process-status');
                if (statusElement) {
                    statusElement.textContent = 'idle';
                }
            });
        }

        // Reset working memory
        this.updateWorkingMemory(['System ready', 'Awaiting next query']);
    }

    /**
     * Start background animations
     */
    startAnimations() {
        // Animate daemon activity indicators
        this.animateDaemonActivity();
        
        // Animate consciousness indicators
        this.animateConsciousnessFlow();
    }

    /**
     * Animate daemon activity indicators
     */
    animateDaemonActivity() {
        const animateDaemons = () => {
            const container = document.getElementById('daemonThreads');
            if (container) {
                const activities = container.querySelectorAll('.daemon-activity.active');
                activities.forEach(activity => {
                    // Add subtle pulsing animation
                    activity.style.transform = `scale(${0.9 + Math.random() * 0.2})`;
                });
            }
            
            // Schedule next animation
            this.animationFrames.set('daemons', 
                requestAnimationFrame(() => {
                    setTimeout(animateDaemons, 1000 + Math.random() * 2000);
                })
            );
        };
        
        animateDaemons();
    }

    /**
     * Animate consciousness flow indicators
     */
    animateConsciousnessFlow() {
        const animateConsciousness = () => {
            const attentionContainer = document.getElementById('attentionFocus');
            if (attentionContainer) {
                // Add subtle variations to attention focus
                const focusBeam = attentionContainer.querySelector('.focus-beam');
                if (focusBeam) {
                    const variation = 0.8 + Math.random() * 0.4;
                    focusBeam.style.opacity = variation;
                }
            }
            
            // Schedule next animation
            this.animationFrames.set('consciousness',
                requestAnimationFrame(() => {
                    setTimeout(animateConsciousness, 2000 + Math.random() * 3000);
                })
            );
        };
        
        animateConsciousness();
    }

    /**
     * Create processing stage visualization
     * @param {Array} stages - Array of processing stages
     */
    createProcessingVisualization(stages) {
        const container = document.querySelector('.cognitive-process-viz');
        if (!container) return;

        container.innerHTML = '';
        
        // Create process flow background
        const processFlow = document.createElement('div');
        processFlow.className = 'process-flow';
        container.appendChild(processFlow);
        
        // Create stages container
        const stagesContainer = document.createElement('div');
        stagesContainer.className = 'process-stages';
        
        stages.forEach((stage, index) => {
            const stageElement = document.createElement('div');
            stageElement.className = 'process-stage';
            
            const indicator = document.createElement('div');
            indicator.className = 'stage-indicator';
            
            const label = document.createElement('div');
            label.className = 'stage-label';
            label.textContent = stage;
            
            stageElement.appendChild(indicator);
            stageElement.appendChild(label);
            stagesContainer.appendChild(stageElement);
        });
        
        container.appendChild(stagesContainer);
    }

    /**
     * Activate processing stage
     * @param {number} stageIndex - Index of stage to activate
     */
    activateProcessingStage(stageIndex) {
        const indicators = document.querySelectorAll('.stage-indicator');
        indicators.forEach((indicator, index) => {
            if (index === stageIndex) {
                indicator.classList.add('active');
            } else {
                indicator.classList.remove('active');
            }
        });
    }

    /**
     * Cleanup animations on destroy
     */
    destroy() {
        this.animationFrames.forEach(frameId => {
            cancelAnimationFrame(frameId);
        });
        this.animationFrames.clear();
    }
}

// Create global cognitive layers manager instance
window.cognitiveManager = new CognitiveLayers();