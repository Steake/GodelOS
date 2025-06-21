// WebSocket integration for real-time cognitive state updates
import { cognitiveState, knowledgeState, evolutionState } from '../stores/cognitive.js';
import { get } from 'svelte/store';

let ws = null;
let reconnectTimer = null;
let reconnectAttempts = 0;
const MAX_RECONNECT_ATTEMPTS = 10;
const RECONNECT_DELAY = 2000;

// API client for fetching initial data
const API_BASE_URL = 'http://localhost:8000';

async function fetchFromAPI(endpoint) {
  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`);
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    return await response.json();
  } catch (error) {
    console.error(`Failed to fetch ${endpoint}:`, error);
    return null;
  }
}

// Load initial data from backend APIs
async function loadInitialData() {
  console.log('🔄 Loading initial data from backend...');
  
  // Fetch cognitive state
  const cognitiveData = await fetchFromAPI('/api/cognitive/state');
  if (cognitiveData) {
    updateCognitiveStateFromAPI(cognitiveData);
  }
  
  // Fetch knowledge graph data
  const knowledgeData = await fetchFromAPI('/api/transparency/knowledge-graph/export');
  if (knowledgeData && knowledgeData.graph_data) {
    updateKnowledgeStateFromAPI(knowledgeData);
  }
  
  // Fetch system health
  const healthData = await fetchFromAPI('/api/health');
  if (healthData) {
    updateSystemHealthFromAPI(healthData);
  }
  
  console.log('✅ Initial data loaded');
}

// Update cognitive state from API response
function updateCognitiveStateFromAPI(data) {
  cognitiveState.update(state => ({
    ...state,
    manifestConsciousness: {
      attention: data.attention_focus || [],
      workingMemory: data.working_memory || {},
      processingLoad: data.manifest_consciousness?.awareness_level || 0,
      currentQuery: data.manifest_consciousness?.current_focus || null,
      focusDepth: 'surface'
    },
    agenticProcesses: data.agentic_processes || [],
    daemonThreads: data.daemon_threads || [],
    systemHealth: {
      inferenceEngine: Math.random() * 0.2 + 0.8, // Will be updated via WebSocket
      knowledgeStore: Math.random() * 0.2 + 0.8,
      reflectionEngine: Math.random() * 0.2 + 0.8,
      learningModules: Math.random() * 0.2 + 0.8,
      websocketConnection: 1.0
    },
    capabilities: {
      reasoning: data.manifest_consciousness?.coherence_level || 0.8,
      knowledge: data.manifest_consciousness?.integration_level || 0.8,
      creativity: Math.random() * 0.3 + 0.7,
      reflection: Math.random() * 0.3 + 0.7,
      learning: Math.random() * 0.3 + 0.7
    },
    lastUpdate: Date.now()
  }));
}

// Update knowledge state from API response
function updateKnowledgeStateFromAPI(data) {
  const nodes = data.graph_data?.nodes || [];
  const edges = data.graph_data?.edges || [];
  
  knowledgeState.update(state => ({
    ...state,
    totalConcepts: nodes.length,
    totalConnections: edges.length,
    currentGraph: {
      nodes: nodes.map(node => ({
        id: node.id,
        label: node.label || node.id,
        type: node.type || 'concept',
        confidence: node.confidence || 1.0
      })),
      links: edges.map(edge => ({
        source: edge.source,
        target: edge.target,
        type: edge.type || 'relation',
        confidence: edge.confidence || 1.0
      }))
    },
    categories: [...new Set(nodes.map(n => n.type || 'concept'))],
    totalRelationships: edges.length,
    lastUpdate: Date.now()
  }));
}

// Update system health from API response
function updateSystemHealthFromAPI(data) {
  if (data.status === 'healthy') {
    cognitiveState.update(state => ({
      ...state,
      systemHealth: {
        ...state.systemHealth,
        websocketConnection: 1.0
      }
    }));
  }
}

// WebSocket connection setup
export async function setupWebSocket() {
  if (ws && ws.readyState === WebSocket.OPEN) {
    return;
  }

  // First, fetch initial data from the API
  await loadInitialData();

  try {
    // Connect to GödelOS backend WebSocket endpoint
    ws = new WebSocket('ws://localhost:8000/ws/cognitive-stream');
    
    ws.onopen = (event) => {
      console.log('Connected to GödelOS cognitive stream');
      reconnectAttempts = 0;
      updateConnectionStatus(true);
      
      // Request initial state
      sendMessage({
        type: 'request_state',
        components: ['cognitive', 'knowledge', 'evolution']
      });
    };

    ws.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data);
        handleCognitiveUpdate(message);
      } catch (error) {
        console.error('Error parsing WebSocket message:', error);
      }
    };

    ws.onclose = (event) => {
      console.log('WebSocket connection closed:', event.code, event.reason);
      updateConnectionStatus(false);
      
      if (!event.wasClean && reconnectAttempts < MAX_RECONNECT_ATTEMPTS) {
        scheduleReconnect();
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      updateConnectionStatus(false);
    };

  } catch (error) {
    console.error('Failed to setup WebSocket:', error);
    updateConnectionStatus(false);
    throw error;
  }
}

// Handle incoming cognitive updates
function handleCognitiveUpdate(message) {
  switch (message.type) {
    case 'cognitive_state_update':
      updateCognitiveState(message.data);
      break;
      
    case 'knowledge_update':
      updateKnowledgeState(message.data);
      break;
      
    case 'evolution_update':
      updateEvolutionState(message.data);
      break;
      
    case 'agent_spawned':
      handleAgentSpawned(message.data);
      break;
      
    case 'daemon_activity':
      handleDaemonActivity(message.data);
      break;
      
    case 'reflection_generated':
      handleReflectionGenerated(message.data);
      break;
      
    case 'query_processed':
      handleQueryProcessed(message.data);
      break;
      
    case 'system_alert':
      handleSystemAlert(message.data);
      break;
      
    case 'performance_metric':
      handlePerformanceMetric(message.data);
      break;
      
    default:
      console.log('Unknown message type:', message.type);
  }
}

// Update cognitive state store
function updateCognitiveState(data) {
  cognitiveState.update(state => {
    return {
      ...state,
      ...data,
      lastUpdate: Date.now()
    };
  });
}

// Update knowledge state store
function updateKnowledgeState(data) {
  knowledgeState.update(state => {
    return {
      ...state,
      ...data
    };
  });
}

// Update evolution state store
function updateEvolutionState(data) {
  evolutionState.update(state => {
    return {
      ...state,
      ...data
    };
  });
}

// Handle agent spawning
function handleAgentSpawned(agent) {
  cognitiveState.update(state => {
    const newAgents = [...state.agenticProcesses, {
      id: agent.id,
      type: agent.type,
      goal: agent.goal,
      status: 'active',
      spawnTime: Date.now(),
      resources: agent.resources || {}
    }];
    
    return {
      ...state,
      agenticProcesses: newAgents,
      lastUpdate: Date.now()
    };
  });
}

// Handle daemon thread activity
function handleDaemonActivity(daemon) {
  cognitiveState.update(state => {
    const daemonIndex = state.daemonThreads.findIndex(d => d.id === daemon.id);
    let newDaemons;
    
    if (daemonIndex >= 0) {
      // Update existing daemon
      newDaemons = [...state.daemonThreads];
      newDaemons[daemonIndex] = {
        ...newDaemons[daemonIndex],
        ...daemon,
        lastActivity: Date.now()
      };
    } else {
      // Add new daemon
      newDaemons = [...state.daemonThreads, {
        ...daemon,
        lastActivity: Date.now()
      }];
    }
    
    return {
      ...state,
      daemonThreads: newDaemons,
      lastUpdate: Date.now()
    };
  });
}

// Handle reflection generation
function handleReflectionGenerated(reflection) {
  cognitiveState.update(state => {
    const updatedMemory = [...state.manifestConsciousness.workingMemory];
    
    // Add reflection to working memory if relevant
    if (reflection.relevance > 0.7) {
      updatedMemory.push({
        type: 'reflection',
        content: reflection.content,
        timestamp: Date.now(),
        relevance: reflection.relevance
      });
      
      // Keep working memory manageable
      if (updatedMemory.length > 10) {
        updatedMemory.sort((a, b) => b.relevance - a.relevance);
        updatedMemory.splice(8);
      }
    }
    
    return {
      ...state,
      manifestConsciousness: {
        ...state.manifestConsciousness,
        workingMemory: updatedMemory
      },
      lastUpdate: Date.now()
    };
  });
}

// Handle query processing updates
function handleQueryProcessed(queryResult) {
  cognitiveState.update(state => {
    return {
      ...state,
      manifestConsciousness: {
        ...state.manifestConsciousness,
        currentQuery: queryResult.query,
        processingLoad: queryResult.processingLoad || state.manifestConsciousness.processingLoad
      },
      lastUpdate: Date.now()
    };
  });
  
  // Update knowledge state if new concepts discovered
  if (queryResult.newConcepts) {
    knowledgeState.update(state => {
      return {
        ...state,
        totalConcepts: state.totalConcepts + queryResult.newConcepts.length,
        recentImports: [...queryResult.newConcepts, ...state.recentImports].slice(0, 20)
      };
    });
  }
}

// Handle system alerts
function handleSystemAlert(alert) {
  cognitiveState.update(state => {
    const newAlerts = [...state.alerts, {
      id: Date.now(),
      ...alert,
      timestamp: Date.now()
    }];
    
    // Keep only recent alerts
    const cutoff = Date.now() - (5 * 60 * 1000); // 5 minutes
    const filteredAlerts = newAlerts.filter(a => a.timestamp > cutoff);
    
    return {
      ...state,
      alerts: filteredAlerts,
      lastUpdate: Date.now()
    };
  });
}

// Handle performance metrics
function handlePerformanceMetric(metric) {
  cognitiveState.update(state => {
    const newSystemHealth = { ...state.systemHealth };
    
    if (metric.component && typeof metric.value === 'number') {
      newSystemHealth[metric.component] = Math.max(0, Math.min(1, metric.value));
    }
    
    return {
      ...state,
      systemHealth: newSystemHealth,
      lastUpdate: Date.now()
    };
  });
}

// Update connection status in cognitive state
function updateConnectionStatus(connected) {
  cognitiveState.update(state => {
    return {
      ...state,
      systemHealth: {
        ...state.systemHealth,
        websocketConnection: connected ? 1.0 : 0.0
      },
      lastUpdate: Date.now()
    };
  });
}

// Send message to backend
export function sendMessage(message) {
  if (ws && ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify(message));
  } else {
    console.warn('WebSocket not connected, cannot send message:', message);
  }
}

// Send query to backend
export function sendQuery(query, options = {}) {
  sendMessage({
    type: 'query',
    query: query,
    options: {
      enableReflection: true,
      trackProcessing: true,
      ...options
    },
    timestamp: Date.now()
  });
}

// Request cognitive state snapshot
export function requestCognitiveSnapshot() {
  sendMessage({
    type: 'request_snapshot',
    components: ['cognitive', 'knowledge', 'evolution'],
    timestamp: Date.now()
  });
}

// Schedule reconnection
function scheduleReconnect() {
  if (reconnectTimer) {
    clearTimeout(reconnectTimer);
  }
  
  reconnectAttempts++;
  const delay = RECONNECT_DELAY * Math.pow(2, Math.min(reconnectAttempts - 1, 5));
  
  console.log(`Scheduling reconnection attempt ${reconnectAttempts} in ${delay}ms`);
  
  reconnectTimer = setTimeout(() => {
    console.log(`Reconnection attempt ${reconnectAttempts}`);
    setupWebSocket();
  }, delay);
}

// Close WebSocket connection
export function closeConnection() {
  if (reconnectTimer) {
    clearTimeout(reconnectTimer);
    reconnectTimer = null;
  }
  
  if (ws) {
    ws.close(1000, 'Client disconnecting');
    ws = null;
  }
}

// Connect to cognitive stream (alias for setupWebSocket)
export const connectToCognitiveStream = setupWebSocket;

// Export WebSocket status
export function getConnectionStatus() {
  return ws ? ws.readyState : WebSocket.CLOSED;
}

// Mock data simulator for development (when backend not available)
export function startMockCognitiveUpdates() {
  console.log('Starting mock cognitive updates for development');
  
  // Simulate cognitive state changes
  setInterval(() => {
    const mockUpdate = {
      type: 'cognitive_state_update',
      data: {
        manifestConsciousness: {
          processingLoad: Math.random() * 0.3 + 0.4,
          attention: Math.random() > 0.7 ? `Concept_${Math.floor(Math.random() * 100)}` : null
        },
        systemHealth: {
          inferenceEngine: Math.random() * 0.2 + 0.8,
          knowledgeStore: Math.random() * 0.1 + 0.9,
          reflectionEngine: Math.random() * 0.3 + 0.6,
          learningModules: Math.random() * 0.2 + 0.7
        }
      }
    };
    
    handleCognitiveUpdate(mockUpdate);
  }, 2000);
  
  // Simulate daemon activity
  setInterval(() => {
    const mockDaemon = {
      type: 'daemon_activity',
      data: {
        id: `daemon_${Math.floor(Math.random() * 5)}`,
        name: ['PatternScanner', 'MemoryConsolidator', 'NoveltyDetector', 'ResourceOptimizer', 'BackgroundLearner'][Math.floor(Math.random() * 5)],
        activity: ['scanning', 'consolidating', 'optimizing', 'learning'][Math.floor(Math.random() * 4)],
        load: Math.random() * 0.5
      }
    };
    
    handleCognitiveUpdate(mockDaemon);
  }, 5000);
  
  // Simulate occasional alerts
  setInterval(() => {
    if (Math.random() > 0.8) {
      const mockAlert = {
        type: 'system_alert',
        data: {
          severity: ['info', 'warning', 'error'][Math.floor(Math.random() * 3)],
          title: 'System Event',
          message: ['Processing load spike detected', 'New knowledge integration complete', 'Reflection depth increased'][Math.floor(Math.random() * 3)]
        }
      };
      
      handleCognitiveUpdate(mockAlert);
    }
  }, 10000);
}
