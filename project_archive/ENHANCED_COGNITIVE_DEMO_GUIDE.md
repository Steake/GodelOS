# GödelOS Enhanced Cognitive Features Demo Guide

## 🧠 Complete System Demo Instructions

### Prerequisites
- Python virtual environment activated (`source godel_venv/bin/activate`)
- All dependencies installed (`pip install -r requirements.txt`)
- Node.js and npm installed for frontend
- Ports 8000 (backend) and 5173 (frontend) available

### Quick Start (Automated)
```bash
# Run the complete automated demo
./start_enhanced_demo.sh
```

### Manual Start (Step by Step)

#### 1. Start Backend Server
```bash
# Clean startup
python backend/start_server.py --debug
```

#### 2. Verify Enhanced Cognitive API
```bash
# Check if enhanced cognitive features are running
curl http://localhost:8000/api/enhanced-cognitive/stream/status | jq '.'

# Expected output should show:
# - stream_coordinator_available: true
# - enhanced_metacognition.is_running: true
# - autonomous_learning.enabled: true
# - cognitive_streaming.enabled: true
```

#### 3. Start Frontend
```bash
cd svelte-frontend
npm run dev
```

#### 4. Test WebSocket Streaming
```bash
# Test real-time cognitive streaming
python test_websocket_streaming.py
```

### 🎯 Demo Features Checklist

#### ✅ Enhanced Metacognition
- [ ] Stream coordinator initialization
- [ ] WebSocket manager with cognitive streaming
- [ ] Enhanced metacognition manager running
- [ ] Configuration management working

#### ✅ Autonomous Learning
- [ ] Knowledge gap detection active
- [ ] Autonomous acquisition triggers
- [ ] Learning progress monitoring
- [ ] Gap priority assessment

#### ✅ Real-Time Streaming
- [ ] WebSocket cognitive event streaming
- [ ] Configurable granularity levels (minimal, standard, detailed, debug)
- [ ] Event type subscriptions (reasoning, knowledge_gap, reflection, acquisition)
- [ ] Client connection management

#### ✅ Stream of Consciousness
- [ ] Real-time cognitive event broadcasting
- [ ] Event history and buffering
- [ ] Performance metrics tracking
- [ ] Multi-client support

#### ✅ Frontend Integration
- [ ] Enhanced Cognitive Dashboard component
- [ ] Real-time WebSocket connection
- [ ] Cognitive state monitoring
- [ ] Autonomous learning status display
- [ ] Stream of consciousness visualization

### 🔍 Demo Scenarios

#### Scenario 1: Basic System Health
1. Check backend API status: `curl http://localhost:8000/health`
2. Verify enhanced cognitive status: `curl http://localhost:8000/api/enhanced-cognitive/stream/status`
3. Confirm frontend loads: Open `http://localhost:5173`

#### Scenario 2: Real-Time Streaming
1. Run WebSocket test: `python test_websocket_streaming.py`
2. Open browser dev tools on frontend
3. Monitor WebSocket tab for real-time events
4. Verify event types and granularity filtering

#### Scenario 3: Autonomous Learning Demo
1. Open frontend Enhanced Cognitive Dashboard
2. Submit complex queries through the interface
3. Monitor knowledge gap detection in real-time
4. Observe autonomous acquisition triggers
5. Check learning progress updates

#### Scenario 4: Query Processing with Learning
```bash
# Test query with autonomous learning
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How does quantum consciousness relate to information integration theory?",
    "context": "philosophy of mind",
    "max_tokens": 200
  }'
```

#### Scenario 5: Stream Configuration
1. Connect to WebSocket with different granularity levels
2. Test subscription filtering for specific event types
3. Verify client configuration updates
4. Monitor performance metrics

### 📊 Key Metrics to Monitor

#### Backend Health
- Enhanced metacognition manager status
- Stream coordinator availability
- WebSocket connection count
- Event generation rate

#### Autonomous Learning
- Active knowledge acquisitions
- Detected knowledge gaps
- Gap priority distribution
- Learning success rate

#### Cognitive Streaming
- Connected clients count
- Events per second
- Buffer utilization
- Connection stability

#### Frontend Integration
- WebSocket connection status
- Real-time data flow
- UI responsiveness
- Component state updates

### 🔧 Troubleshooting

#### Backend Issues
```bash
# Check backend logs
tail -f logs/backend_demo.log

# Verify port availability
lsof -i :8000

# Test specific endpoints
curl http://localhost:8000/docs  # API documentation
```

#### Frontend Issues
```bash
# Check frontend logs
tail -f logs/frontend_demo.log

# Verify dependencies
cd svelte-frontend && npm list

# Check port availability
lsof -i :5173
```

#### WebSocket Issues
```bash
# Test WebSocket connection
python test_websocket_streaming.py

# Check browser developer tools
# Navigate to Network tab -> WS (WebSockets)
```

### 🌟 Expected Demo Outcomes

After running the complete demo, you should observe:

1. **Real-Time Cognitive Streaming**: Live events flowing from backend to frontend
2. **Autonomous Learning**: Automatic detection and acquisition of knowledge gaps
3. **Enhanced Metacognition**: Sophisticated self-monitoring and reflection
4. **Interactive Dashboard**: Responsive UI showing cognitive state in real-time
5. **Configurable Streaming**: Adjustable granularity and event filtering
6. **Performance Monitoring**: Metrics and status tracking across all components

### 📝 Demo Success Criteria

- ✅ Backend starts without errors
- ✅ Enhanced cognitive API responds correctly
- ✅ WebSocket connections establish successfully
- ✅ Frontend loads and connects to backend
- ✅ Real-time events display in browser
- ✅ Autonomous learning triggers on complex queries
- ✅ All dashboard components show live data
- ✅ Configuration changes apply immediately
- ✅ System maintains stability under load

### 🚀 Next Steps After Demo

1. **Query Testing**: Submit various complex queries to test learning
2. **Customization**: Modify granularity levels and subscriptions
3. **Monitoring**: Observe long-term autonomous learning behavior
4. **Integration**: Connect additional data sources for richer learning
5. **Scaling**: Test with multiple concurrent WebSocket clients
