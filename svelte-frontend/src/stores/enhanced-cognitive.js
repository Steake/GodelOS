/**
 * Enhanced Cognitive State Store with Autonomous Learning and Streaming
 * 
 * Extends the existing cognitive state management with:
 * - Autonomous learning state tracking
 * - Real-time cognitive event streaming
 * - Enhanced system health monitoring
 * - Stream of consciousness coordination
 * - Unified state coordination with basic cognitive store
 */

import { writable, derived, get } from 'svelte/store';
import { cognitiveState } from './cognitive.js';

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
    this.fallbackPollingInterval = null;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.reconnectTimeout = null;
  }

  /**
   * Initialize the enhanced cognitive state system
   */
  async initialize() {
    if (this.isInitialized) return;

    try {
      console.log('🧠 Initializing enhanced cognitive systems...');
      
      // Check backend connectivity first
      try {
        const healthResponse = await fetch(`${API_BASE_URL}/api/enhanced-cognitive/health`, {
          signal: AbortSignal.timeout(5000)
        });
        if (healthResponse.ok) {
          console.log('✅ Enhanced cognitive API is available');
          enhancedCognitiveState.update(state => ({
            ...state,
            apiConnected: true,
            connectionStatus: 'connected'
          }));
        } else {
          throw new Error('Enhanced cognitive API not available');
        }
      } catch (error) {
        console.log('⚠️ Enhanced cognitive API not available, using fallback mode');
        enhancedCognitiveState.update(state => ({
          ...state,
          apiConnected: false,
          connectionStatus: 'disconnected'
        }));
      }

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
      console.warn('Enhanced cognitive initialization failed:', error);
      // Silently handle initialization errors when backend is unavailable
      enhancedCognitiveState.update(state => ({
        ...state,
        apiConnected: false,
        connectionStatus: 'disconnected',
        lastUpdate: new Date().toISOString()
      }));
    }
  }

  /**
   * Connect to cognitive event stream with enhanced error handling and reconnection
   */
  async connectCognitiveStream() {
    try {
      const config = get(cognitiveConfig);
      
      // Disconnect existing connection
      if (cognitiveWebSocket) {
        cognitiveWebSocket.close();
      }

      // Check if WebSocket endpoint is available first
      try {
        const streamStatusResponse = await fetch(`${API_BASE_URL}/api/enhanced-cognitive/stream/status`);
        if (!streamStatusResponse.ok) {
          throw new Error('Cognitive stream endpoint not available');
        }
      } catch (error) {
        console.log('⚠️ Cognitive streaming not available, using fallback polling');
        this.enableFallbackPolling();
        return;
      }

      // Build WebSocket URL with parameters
      const params = new URLSearchParams({
        granularity: config.cognitiveStreaming.granularity,
        subscriptions: config.cognitiveStreaming.subscriptions?.join(',') || ''
      });

      const wsUrl = `ws://localhost:8000/ws/cognitive-stream?${params}`;
      
      console.log('🔗 Connecting to cognitive stream:', wsUrl);
      cognitiveWebSocket = new WebSocket(wsUrl);

      cognitiveWebSocket.onopen = () => {
        console.log('🔗 Cognitive stream connected successfully');
        this.reconnectAttempts = 0;
        
        // Clear any pending reconnection attempts
        if (this.reconnectTimeout) {
          clearTimeout(this.reconnectTimeout);
          this.reconnectTimeout = null;
        }
        
        enhancedCognitiveState.update(state => ({
          ...state,
          cognitiveStreaming: {
            ...state.cognitiveStreaming,
            connected: true,
            enabled: true,
            connectionId: Date.now().toString(),
            lastEvent: new Date().toISOString()
          },
          connectionStatus: 'connected'
        }));

        // Send initial configuration
        if (cognitiveWebSocket && cognitiveWebSocket.readyState === WebSocket.OPEN) {
          cognitiveWebSocket.send(JSON.stringify({
            type: 'configure',
            granularity: config.cognitiveStreaming.granularity,
            subscriptions: config.cognitiveStreaming.subscriptions || []
          }));
        }
      };

      cognitiveWebSocket.onmessage = (event) => {
        try {
          const cognitiveEvent = JSON.parse(event.data);
          console.log('📥 Received cognitive event:', cognitiveEvent.type);
          this.handleCognitiveEvent(cognitiveEvent);
        } catch (error) {
          console.error('❌ Error parsing cognitive event:', error, 'Raw data:', event.data);
        }
      };

      cognitiveWebSocket.onclose = (event) => {
        console.log(`🔌 Cognitive stream disconnected. Code: ${event.code}, Reason: ${event.reason || 'No reason provided'}`);
        
        enhancedCognitiveState.update(state => ({
          ...state,
          cognitiveStreaming: {
            ...state.cognitiveStreaming,
            connected: false
          },
          connectionStatus: 'disconnected'
        }));

        // Attempt reconnection if not a normal closure
        if (event.code !== 1000 && this.reconnectAttempts < this.maxReconnectAttempts) {
          this.scheduleReconnection();
        } else {
          console.log('🔄 Falling back to polling mode');
          this.enableFallbackPolling();
        }
      };

      cognitiveWebSocket.onerror = (error) => {
        console.log('❌ Cognitive stream error, will attempt fallback');
        
        enhancedCognitiveState.update(state => ({
          ...state,
          cognitiveStreaming: {
            ...state.cognitiveStreaming,
            connected: false
          },
          connectionStatus: 'error'
        }));
      };

    } catch (error) {
      console.log('⚠️ WebSocket connection failed, using fallback polling:', error);
      this.enableFallbackPolling();
    }
  }

  /**
   * Enable fallback polling when WebSocket is not available
   */
  enableFallbackPolling() {
    console.log('🔄 Enabling fallback polling for cognitive updates');
    
    // Update every 5 seconds as fallback
    if (!this.fallbackPollingInterval) {
      this.fallbackPollingInterval = setInterval(async () => {
        try {
          await this.updateSystemHealth();
          await this.updateAutonomousLearningState();
        } catch (error) {
          // Silently handle polling errors
        }
      }, 5000);
    }

    enhancedCognitiveState.update(state => ({
      ...state,
      cognitiveStreaming: {
        ...state.cognitiveStreaming,
        connected: false,
        enabled: false,
        fallbackMode: true
      }
    }));
  }

  /**
   * Disconnect from cognitive stream
   */
  disconnectCognitiveStream() {
    if (cognitiveWebSocket) {
      cognitiveWebSocket.close(1000, 'Client disconnect');
      cognitiveWebSocket = null;
    }

    if (this.reconnectTimeout) {
      clearTimeout(this.reconnectTimeout);
      this.reconnectTimeout = null;
    }

    if (this.fallbackPollingInterval) {
      clearInterval(this.fallbackPollingInterval);
      this.fallbackPollingInterval = null;
    }

    enhancedCognitiveState.update(state => ({
      ...state,
      cognitiveStreaming: {
        ...state.cognitiveStreaming,
        connected: false,
        enabled: false,
        fallbackMode: false
      }
    }));

    console.log('🔌 Disconnected from cognitive stream');
  }

  /**
   * Configure cognitive streaming settings
   */
  async configureCognitiveStreaming(config) {
    try {
      // Update local configuration
      cognitiveConfig.update(state => ({
        ...state,
        cognitiveStreaming: { ...state.cognitiveStreaming, ...config }
      }));

      // If streaming is being enabled, connect
      if (config.enabled) {
        await this.connectCognitiveStream();
      } else {
        this.disconnectCognitiveStream();
      }

      // Send configuration to backend if connected
      if (cognitiveWebSocket && cognitiveWebSocket.readyState === WebSocket.OPEN) {
        cognitiveWebSocket.send(JSON.stringify({
          type: 'configure',
          ...config
        }));
      } else {
        // Use HTTP API as fallback
        try {
          const response = await fetch(`${API_BASE_URL}/api/enhanced-cognitive/stream/configure`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(config)
          });
          if (response.ok) {
            console.log('✅ Cognitive streaming configured via HTTP API');
          }
        } catch (error) {
          console.warn('Failed to configure streaming via HTTP API:', error);
        }
      }

      return true;
    } catch (error) {
      console.error('Failed to configure cognitive streaming:', error);
      return false;
    }
  }

  /**
   * Schedule reconnection attempt
   */
  scheduleReconnection() {
    if (this.reconnectTimeout) return;

    this.reconnectAttempts++;
    const delay = Math.min(1000 * Math.pow(2, this.reconnectAttempts), 30000); // Max 30 seconds

    console.log(`🔄 Scheduling reconnection attempt ${this.reconnectAttempts} in ${delay}ms`);
    
    this.reconnectTimeout = setTimeout(() => {
      this.reconnectTimeout = null;
      this.connectCognitiveStream();
    }, delay);
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
            overallScore: healthData.overall_health_score || 85, // Default good score
            inferenceEngine: healthData.basic_status?.is_running ? 'healthy' : 'unknown',
            knowledgeStore: healthData.basic_status?.is_running ? 'healthy' : 'unknown', 
            autonomousLearning: healthData.basic_status?.autonomous_learning?.enabled ? 'healthy' : 'unknown',
            cognitiveStreaming: healthData.basic_status?.cognitive_streaming?.enabled ? 'healthy' : 'unknown',
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

// State Coordination - Bridge between basic and enhanced cognitive stores
function synchronizeWithBasicCognitive() {
  // Subscribe to basic cognitive state changes and enhance them
  cognitiveState.subscribe(basicState => {
    enhancedCognitiveState.update(enhancedState => ({
      ...enhancedState,
      // Sync manifest consciousness with enhanced features
      manifestConsciousness: {
        ...enhancedState.manifestConsciousness,
        currentFocus: basicState.manifestConsciousness?.currentQuery || 
                     basicState.manifestConsciousness?.attention || 
                     enhancedState.manifestConsciousness.currentFocus,
        attentionDepth: enhancedState.manifestConsciousness.attentionDepth,
        processingMode: basicState.manifestConsciousness?.processingLoad > 0.7 ? 'intensive' :
                       basicState.manifestConsciousness?.processingLoad > 0.3 ? 'active' : 'idle',
        cognitiveLoad: basicState.manifestConsciousness?.processingLoad || enhancedState.manifestConsciousness.cognitiveLoad,
        lastActivity: basicState.lastUpdate ? new Date(basicState.lastUpdate).toISOString() : enhancedState.manifestConsciousness.lastActivity
      },
      // Enhance system health with basic cognitive health data
      systemHealth: {
        ...enhancedState.systemHealth,
        inferenceEngine: basicState.systemHealth?.inferenceEngine > 0.8 ? 'healthy' :
                        basicState.systemHealth?.inferenceEngine > 0.5 ? 'degraded' : 'critical',
        knowledgeStore: basicState.systemHealth?.knowledgeStore > 0.8 ? 'healthy' :
                       basicState.systemHealth?.knowledgeStore > 0.5 ? 'degraded' : 'critical',
        websocketConnection: basicState.systemHealth?.websocketConnection > 0.5 ? 'connected' : 'disconnected'
      },
      // Update connection status based on basic cognitive state
      connectionStatus: basicState.systemHealth?.websocketConnection > 0.5 ? 'connected' : 'disconnected',
      lastUpdate: new Date().toISOString()
    }));
  });
}

// Initialize on module load
if (typeof window !== 'undefined') {
  enhancedCognitiveStateManager.initialize();
  // Start state synchronization
  synchronizeWithBasicCognitive();
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
  
  // Enhanced methods for better integration
  refreshSystemHealth: () => enhancedCognitiveStateManager.updateSystemHealth(),
  refreshAutonomousState: () => enhancedCognitiveStateManager.updateAutonomousLearningState(),
  refreshStreamingState: () => enhancedCognitiveStateManager.connectCognitiveStream(),
  updateAutonomousLearningState: () => enhancedCognitiveStateManager.updateAutonomousLearningState(),
  updateStreamingStatus: () => enhancedCognitiveStateManager.connectCognitiveStream(),
  pauseAutonomousLearning: () => enhancedCognitiveStateManager.configureAutonomousLearning({ enabled: false }),
  resumeAutonomousLearning: () => enhancedCognitiveStateManager.configureAutonomousLearning({ enabled: true }),
  updateLearningConfiguration: (config) => enhancedCognitiveStateManager.configureAutonomousLearning(config),
  
  // Stream management
  configureCognitiveStreaming: (config) => enhancedCognitiveStateManager.configureCognitiveStreaming(config),
  startCognitiveStreaming: (granularity = 'standard') => enhancedCognitiveStateManager.configureCognitiveStreaming({ enabled: true, granularity }),
  stopCognitiveStreaming: () => enhancedCognitiveStateManager.disconnectCognitiveStream(),
  
  // Event management
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
  
  // Manual triggers
  triggerManualAcquisition: async (concept, context) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/enhanced-cognitive/autonomous/acquire`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ concept, context })
      });
      return response.ok;
    } catch (error) {
      console.warn('Failed to trigger manual acquisition:', error);
      return false;
    }
  },
  
  triggerSystemRefresh: async () => {
    try {
      await Promise.all([
        enhancedCognitiveStateManager.updateSystemHealth(),
        enhancedCognitiveStateManager.updateAutonomousLearningState()
      ]);
      return true;
    } catch (error) {
      console.warn('System refresh failed:', error);
      return false;
    }
  },
  
  // Stream subscription method for real-time updates
  subscribeToStream: (callback) => {
    // Subscribe to cognitive streaming events
    const unsubscribe = enhancedCognitiveState.subscribe(state => {
      if (state.cognitiveStreaming?.lastEvent) {
        callback(state.cognitiveStreaming.lastEvent);
      }
    });
    return unsubscribe;
  },
  
  // Connection status
  getConnectionStatus: () => {
    const state = get(enhancedCognitiveState);
    return {
      apiConnected: state.apiConnected,
      streamConnected: state.cognitiveStreaming?.connected || false,
      connectionStatus: state.connectionStatus,
      fallbackMode: state.cognitiveStreaming?.fallbackMode || false
    };
  },
  
  // State access helpers
  autonomousLearning: autonomousLearningState,
  streaming: cognitiveStreamingState,
  health: enhancedSystemHealth,
  consciousness: manifestConsciousness
};

// Default export for easier importing
export default enhancedCognitive;
