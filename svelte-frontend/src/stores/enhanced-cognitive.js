/**
 * Enhanced Cognitive State Store with Autonomous Learning and Streaming
 * 
 * Extends the existing cognitive state management with:
 * - Autonomous learning state tracking
 * - Real-time cognitive event streaming
 * - Enhanced system health monitoring
 * - Stream of consciousness coordination
 */

import { writable, derived, get } from 'svelte/store';

// API Configuration
const API_BASE_URL = 'http://localhost:8000';

// Core cognitive state (existing)
export const enhancedCognitiveState = writable({
  // Existing manifest consciousness
  manifestConsciousness: {
    currentFocus: null,
    attentionDepth: 0,
    processingMode: 'idle',
    cognitiveLoad: 0,
    lastActivity: null
  },
  
  // New autonomous learning state
  autonomousLearning: {
    enabled: true,
    activeAcquisitions: [],
    detectedGaps: [],
    acquisitionHistory: [],
    lastGapDetection: null,
    statistics: {
      totalGapsDetected: 0,
      totalAcquisitions: 0,
      successRate: 0,
      averageAcquisitionTime: 0
    }
  },
  
  // New cognitive streaming state
  cognitiveStreaming: {
    enabled: false,
    connected: false,
    granularity: 'standard',
    eventRate: 0,
    lastEvent: null,
    eventHistory: [],
    connectionId: null,
    subscriptions: []
  },
  
  // Enhanced system health
  systemHealth: {
    overall: 'unknown',
    overallScore: 0,
    inferenceEngine: 'unknown',
    knowledgeStore: 'unknown',
    autonomousLearning: 'unknown',
    cognitiveStreaming: 'unknown',
    lastHealthCheck: null,
    anomalies: [],
    recommendations: []
  }
});

// Configuration store
export const cognitiveConfig = writable({
  autonomousLearning: {
    enabled: true,
    gapDetectionInterval: 300,
    confidenceThreshold: 0.7,
    autoApprovalThreshold: 0.8,
    maxConcurrentAcquisitions: 3
  },
  cognitiveStreaming: {
    enabled: true,
    granularity: 'standard',
    maxEventRate: 100,
    bufferSize: 1000,
    autoReconnect: true
  }
});

// WebSocket connection for cognitive streaming
let cognitiveWebSocket = null;
let reconnectAttempts = 0;
const maxReconnectAttempts = 5;
let reconnectTimeout = null;

/**
 * Enhanced Cognitive State Manager
 */
class EnhancedCognitiveStateManager {
  constructor() {
    this.isInitialized = false;
    this.eventBuffer = [];
    this.maxBufferSize = 1000;
  }

  /**
   * Initialize the enhanced cognitive state system
   */
  async initialize() {
    if (this.isInitialized) return;

    try {
      // Initialize cognitive streaming if enabled
      const config = get(cognitiveConfig);
      if (config.cognitiveStreaming.enabled) {
        await this.connectCognitiveStream();
      }

      // Load initial system health
      try {
        await this.updateSystemHealth();
      } catch (error) {
        console.warn('System health update failed:', error);
      }

      // Load autonomous learning status
      try {
        await this.updateAutonomousLearningState();
      } catch (error) {
        console.warn('Autonomous learning state update failed:', error);
      }

      // Start periodic health checks
      this.startHealthMonitoring();

      this.isInitialized = true;
      console.log('✅ Enhanced cognitive state manager initialized');

    } catch (error) {
      // Silently handle initialization errors when backend is unavailable
      state.apiConnected = false;
      state.lastUpdate = new Date().toISOString();
    }
  }

  /**
   * Connect to cognitive event stream
   */
  async connectCognitiveStream() {
    try {
      const config = get(cognitiveConfig);
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const host = window.location.host;
      
      // Disconnect existing connection
      if (cognitiveWebSocket) {
        cognitiveWebSocket.close();
      }

      // Build WebSocket URL with parameters
      const params = new URLSearchParams({
        granularity: config.cognitiveStreaming.granularity,
        subscriptions: config.cognitiveStreaming.subscriptions?.join(',') || ''
      });

      const wsUrl = `ws://localhost:8000/api/enhanced-cognitive/stream?${params}`;
      
      cognitiveWebSocket = new WebSocket(wsUrl);

      cognitiveWebSocket.onopen = () => {
        console.log('🔗 Cognitive stream connected');
        reconnectAttempts = 0;
        
        enhancedCognitiveState.update(state => ({
          ...state,
          cognitiveStreaming: {
            ...state.cognitiveStreaming,
            connected: true,
            connectionId: Date.now().toString(),
            lastEvent: new Date().toISOString()
          }
        }));
      };

      cognitiveWebSocket.onmessage = (event) => {
        try {
          const cognitiveEvent = JSON.parse(event.data);
          this.handleCognitiveEvent(cognitiveEvent);
        } catch (error) {
          // Silently handle parsing errors for malformed events
        }
      };

      cognitiveWebSocket.onclose = () => {
        // Silently handle cognitive stream disconnection when backend is unavailable
        
        enhancedCognitiveState.update(state => ({
          ...state,
          cognitiveStreaming: {
            ...state.cognitiveStreaming,
            connected: false
          }
        }));

        // Attempt to reconnect if configured
        const config = get(cognitiveConfig);
        if (config.cognitiveStreaming.autoReconnect && reconnectAttempts < maxReconnectAttempts) {
          reconnectAttempts++;
          const delay = Math.min(1000 * Math.pow(2, reconnectAttempts), 30000);
          
          // Silently attempt to reconnect cognitive stream when backend is unavailable
          
          reconnectTimeout = setTimeout(() => {
            this.connectCognitiveStream();
          }, delay);
        }
      };

      cognitiveWebSocket.onerror = (error) => {
        // Silently handle WebSocket errors when backend is unavailable
      };

    } catch (error) {
      // Silently handle cognitive stream connection errors when backend is unavailable
    }
  }

  /**
   * Handle incoming cognitive events
   */
  handleCognitiveEvent(event) {
    // Add to event buffer
    this.eventBuffer.push(event);
    if (this.eventBuffer.length > this.maxBufferSize) {
      this.eventBuffer.shift();
    }

    // Update state based on event type
    enhancedCognitiveState.update(state => {
      const newState = { ...state };
      
      // Update streaming state
      newState.cognitiveStreaming = {
        ...state.cognitiveStreaming,
        lastEvent: event,
        eventHistory: [...state.cognitiveStreaming.eventHistory, event].slice(-100),
        eventRate: this.calculateEventRate()
      };

      // Handle specific event types
      switch (event.type) {
        case 'gaps_detected':
        case 'autonomous_gaps_detected':
          if (event.data?.gaps) {
            newState.autonomousLearning.detectedGaps = [
              ...state.autonomousLearning.detectedGaps,
              ...event.data.gaps
            ];
          }
          break;

        case 'acquisition_started':
          if (event.data?.plan_id) {
            newState.autonomousLearning.activeAcquisitions = [
              ...state.autonomousLearning.activeAcquisitions,
              {
                id: event.data.plan_id,
                started: event.timestamp,
                gap_id: event.data.gap_id
              }
            ];
          }
          break;

        case 'acquisition_completed':
        case 'acquisition_failed':
          if (event.data?.plan_id) {
            // Remove from active acquisitions
            newState.autonomousLearning.activeAcquisitions = 
              state.autonomousLearning.activeAcquisitions.filter(
                acq => acq.id !== event.data.plan_id
              );
            
            // Add to history
            newState.autonomousLearning.acquisitionHistory = [
              ...state.autonomousLearning.acquisitionHistory,
              {
                id: event.data.plan_id,
                completed: event.timestamp,
                success: event.type === 'acquisition_completed',
                executionTime: event.data.execution_time,
                acquiredConcepts: event.data.acquired_concepts || 0
              }
            ].slice(-50); // Keep last 50
          }
          break;

        case 'query_started':
          newState.manifestConsciousness = {
            ...state.manifestConsciousness,
            currentFocus: event.data?.query || 'Processing query',
            processingMode: 'active',
            lastActivity: event.timestamp
          };
          break;

        case 'query_completed':
          newState.manifestConsciousness = {
            ...state.manifestConsciousness,
            processingMode: 'idle',
            lastActivity: event.timestamp
          };
          break;
      }

      return newState;
    });
  }

  /**
   * Calculate current event rate
   */
  calculateEventRate() {
    const now = Date.now();
    const oneSecondAgo = now - 1000;
    
    const recentEvents = this.eventBuffer.filter(event => {
      const eventTime = new Date(event.timestamp).getTime();
      return eventTime >= oneSecondAgo;
    });

    return recentEvents.length;
  }

  /**
   * Update system health information
   */
  async updateSystemHealth() {
    try {
      const response = await fetch(`${API_BASE_URL}/api/enhanced-cognitive/health`);
      if (response.ok) {
        const healthData = await response.json();
        
        enhancedCognitiveState.update(state => ({
          ...state,
          systemHealth: {
            overall: healthData.overall_status || 'unknown',
            overallScore: healthData.overall_health_score || 0,
            inferenceEngine: healthData.base_system?.status || 'unknown',
            knowledgeStore: healthData.base_system?.knowledge_store || 'unknown',
            autonomousLearning: healthData.autonomous_learning?.status || 'unknown',
            cognitiveStreaming: healthData.cognitive_streaming?.status || 'unknown',
            lastHealthCheck: new Date().toISOString(),
            anomalies: healthData.anomalies || [],
            recommendations: [
              ...(healthData.autonomous_learning?.recommendations || []),
              ...(healthData.cognitive_streaming?.recommendations || [])
            ]
          }
        }));
      }
    } catch (error) {
      // Only log non-network errors to reduce console noise
      if (!error.message.includes('NetworkError') && error.name !== 'TypeError') {
        console.error('Failed to update system health:', error);
      }
      // Update connection status
      enhancedCognitiveState.update(state => ({
        ...state,
        connectionStatus: 'disconnected'
      }));
    }
  }

  /**
   * Update autonomous learning state
   */
  async updateAutonomousLearningState() {
    try {
      const response = await fetch(`${API_BASE_URL}/api/enhanced-cognitive/autonomous/status`, {
        signal: AbortSignal.timeout(5000) // 5 second timeout
      });
      if (response.ok) {
        const statusData = await response.json();
        
        enhancedCognitiveState.update(state => ({
          ...state,
          autonomousLearning: {
            ...state.autonomousLearning,
            enabled: statusData.enabled || false,
            statistics: {
              totalGapsDetected: statusData.detected_gaps || 0,
              totalAcquisitions: statusData.acquisition_history_size || 0,
              successRate: statusData.success_rate || 0,
              averageAcquisitionTime: statusData.average_acquisition_time || 0
            }
          },
          connectionStatus: 'connected'
        }));
      }
    } catch (error) {
      // Only log non-network errors to reduce console noise
      if (!error.message.includes('NetworkError') && error.name !== 'TypeError') {
        console.error('Failed to update autonomous learning state:', error);
      }
    }
  }

  /**
   * Start periodic health monitoring
   */
  startHealthMonitoring() {
    // Update health every 30 seconds
    setInterval(() => {
      this.updateSystemHealth();
    }, 30000);

    // Update autonomous learning state every 60 seconds
    setInterval(() => {
      this.updateAutonomousLearningState();
    }, 60000);
  }

  /**
   * Configure autonomous learning
   */
  async configureAutonomousLearning(config) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/enhanced-cognitive/autonomous/configure`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(config)
      });

      if (response.ok) {
        cognitiveConfig.update(state => ({
          ...state,
          autonomousLearning: { ...state.autonomousLearning, ...config }
        }));
        
        await this.updateAutonomousLearningState();
        return true;
      }
      return false;
    } catch (error) {
      // Silently handle configuration errors when backend is unavailable
      return false;
    }
  }

  /**
   * Configure cognitive streaming
   */
  async configureCognitiveStreaming(config) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/enhanced-cognitive/stream/configure`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(config)
      });

      if (response.ok) {
        cognitiveConfig.update(state => ({
          ...state,
          cognitiveStreaming: { ...state.cognitiveStreaming, ...config }
        }));

        // Reconnect with new configuration
        if (cognitiveWebSocket && config.granularity) {
          await this.connectCognitiveStream();
        }
        
        return true;
      }
      return false;
    } catch (error) {
      // Silently handle streaming configuration errors when backend is unavailable
      return false;
    }
  }

  /**
   * Trigger manual knowledge acquisition
   */
  async triggerKnowledgeAcquisition(concepts, priority = 0.8) {
    try {
      const response = await fetch('/api/enhanced-cognitive/autonomous/trigger-acquisition', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          concepts,
          priority,
          strategy: 'concept_expansion'
        })
      });

      return response.ok;
    } catch (error) {
      // Silently handle knowledge acquisition trigger errors when backend is unavailable
      return false;
    }
  }

  /**
   * Send message through cognitive stream
   */
  sendCognitiveMessage(message) {
    if (cognitiveWebSocket && cognitiveWebSocket.readyState === WebSocket.OPEN) {
      cognitiveWebSocket.send(JSON.stringify(message));
    }
  }

  /**
   * Get cognitive event history
   */
  getCognitiveEventHistory(limit = 100) {
    return this.eventBuffer.slice(-limit);
  }

  /**
   * Disconnect cognitive stream
   */
  disconnectCognitiveStream() {
    if (cognitiveWebSocket) {
      cognitiveWebSocket.close();
      cognitiveWebSocket = null;
    }
    
    if (reconnectTimeout) {
      clearTimeout(reconnectTimeout);
      reconnectTimeout = null;
    }
  }
}

// Create global instance
export const enhancedCognitiveStateManager = new EnhancedCognitiveStateManager();

// Derived stores for convenient access
export const autonomousLearningState = derived(
  enhancedCognitiveState,
  $state => $state.autonomousLearning
);

export const cognitiveStreamingState = derived(
  enhancedCognitiveState,
  $state => $state.cognitiveStreaming
);

// Alias for easier access
export const streamState = cognitiveStreamingState;

export const enhancedSystemHealth = derived(
  enhancedCognitiveState,
  $state => $state.systemHealth
);

export const manifestConsciousness = derived(
  enhancedCognitiveState,
  $state => $state.manifestConsciousness
);

// Utility functions
export function getHealthColor(status) {
  switch (status) {
    case 'healthy': return '#4ade80';
    case 'warning': return '#fbbf24';
    case 'critical': return '#ef4444';
    case 'unknown': return '#6b7280';
    default: return '#6b7280';
  }
}

export function formatDuration(seconds) {
  if (seconds < 60) return `${seconds.toFixed(1)}s`;
  if (seconds < 3600) return `${(seconds / 60).toFixed(1)}m`;
  return `${(seconds / 3600).toFixed(1)}h`;
}

export function formatEventRate(rate) {
  if (rate < 1) return `${(rate * 1000).toFixed(0)}ms⁻¹`;
  return `${rate.toFixed(1)}/s`;
}

// Initialize on module load
if (typeof window !== 'undefined') {
  enhancedCognitiveStateManager.initialize();
}

// Main enhanced cognitive interface for components
export const enhancedCognitive = {
  subscribe: enhancedCognitiveState.subscribe,
  update: enhancedCognitiveState.update,
  set: enhancedCognitiveState.set,
  
  // Manager methods
  initializeEnhancedSystems: () => enhancedCognitiveStateManager.initialize(),
  enableCognitiveStreaming: (granularity) => enhancedCognitiveStateManager.configureCognitiveStreaming({ granularity, enabled: true }),
  disableCognitiveStreaming: () => enhancedCognitiveStateManager.disconnectCognitiveStream(),
  enableAutonomousLearning: () => enhancedCognitiveStateManager.configureAutonomousLearning({ enabled: true }),
  disableAutonomousLearning: () => enhancedCognitiveStateManager.configureAutonomousLearning({ enabled: false }),
  updateHealthStatus: () => enhancedCognitiveStateManager.updateSystemHealth(),
  
  // Additional missing methods for components
  refreshSystemHealth: () => enhancedCognitiveStateManager.updateSystemHealth(),
  refreshAutonomousState: () => enhancedCognitiveStateManager.updateAutonomousLearningState(),
  refreshStreamingState: () => enhancedCognitiveStateManager.connectCognitiveStream(),
  pauseAutonomousLearning: () => enhancedCognitiveStateManager.configureAutonomousLearning({ enabled: false }),
  resumeAutonomousLearning: () => enhancedCognitiveStateManager.configureAutonomousLearning({ enabled: true }),
  updateLearningConfiguration: (config) => enhancedCognitiveStateManager.configureAutonomousLearning(config),
  triggerManualAcquisition: (concept, context) => enhancedCognitiveStateManager.triggerKnowledgeAcquisition([concept]),
  clearEventHistory: () => {
    enhancedCognitiveStateManager.eventBuffer = [];
    enhancedCognitiveState.update(state => ({
      ...state,
      cognitiveStreaming: {
        ...state.cognitiveStreaming,
        eventHistory: []
      }
    }));
  },
  
  // Stream subscription method
  subscribeToStream: (callback) => {
    // For now, return a no-op unsubscribe function
    // This can be enhanced when WebSocket streaming is fully implemented
    return () => {};
  },
  
  // Start cognitive streaming method
  startCognitiveStreaming: (granularity = 'standard') => enhancedCognitiveStateManager.connectCognitiveStream(),
  
  // State access
  autonomousLearning: autonomousLearningState,
  streaming: cognitiveStreamingState,
  health: enhancedSystemHealth,
  consciousness: manifestConsciousness
};

// Default export for easier importing
export default enhancedCognitive;
