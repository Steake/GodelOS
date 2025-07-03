# Enhanced Cognitive Features Quick Start Guide 🚀

## Overview
GödelOS now includes autonomous knowledge acquisition and real-time stream of consciousness capabilities. This guide will help you quickly test and explore these new features.

## Prerequisites
- Python 3.8+ with virtual environment
- Node.js and npm for Svelte frontend
- All dependencies installed (`pip install -r requirements.txt`)

## Quick Setup

### 1. Install New Dependencies
```bash
cd /path/to/GödelOS.md
pip install PyYAML>=6.0.1
```

### 2. Verify Implementation
```bash
# Run the verification script
python enhanced_metacognition_verification.py
```

### 3. Start the Backend
```bash
cd backend
python main.py
```
Look for these initialization messages:
- ✅ Enhanced cognitive API initialized successfully
- ✅ Configuration loaded successfully

### 4. Start the Frontend
```bash
cd svelte-frontend
npm run dev
```

## Testing the Features

### 🧠 Test Autonomous Knowledge Acquisition

1. **Navigate to Enhanced Dashboard**
   - Open browser to `http://localhost:5173`
   - Look for "Enhanced Cognitive Dashboard" in navigation

2. **Enable Autonomous Learning**
   - Go to Autonomous Learning Monitor
   - Ensure "Active" status is showing
   - Check configuration settings

3. **Trigger Knowledge Gaps**
   - Ask questions about topics the system might not know:
     - "What is quantum annealing?"
     - "How does distributed consensus work?"
     - "Explain neuromorphic computing"

4. **Monitor Gap Detection**
   - Watch the "Knowledge Gaps" section
   - Look for automatically detected gaps
   - See priority assignments and suggested sources

### 💭 Test Stream of Consciousness

1. **Open Stream Monitor**
   - Navigate to Stream of Consciousness Monitor
   - Verify connection status (green dot)

2. **Configure Granularity**
   - Try different levels: minimal, standard, detailed, debug
   - Filter by event types: reasoning, knowledge_gap, acquisition

3. **Watch Real-Time Events**
   - Ask questions and watch cognitive events appear
   - See reasoning processes, gap detection, learning plans

4. **Test Filtering**
   - Use search to find specific events
   - Filter by event types and granularity
   - Export event history

### 📊 Test Health Monitoring

1. **System Health Overview**
   - Check the health indicators in dashboard header
   - Verify all components show "healthy" status
   - Monitor response times and performance metrics

2. **Component Health Details**
   - Inference Engine: Response times
   - Knowledge Store: Entity counts
   - Autonomous Learning: Active plans
   - Cognitive Streaming: Connected clients

### ⚙️ Test Configuration

1. **Runtime Configuration Changes**
   - Modify learning rate in Autonomous Learning Monitor
   - Change streaming granularity in Stream Monitor
   - Toggle autonomous learning on/off

2. **Configuration File Testing**
   - Edit `backend/config/enhanced_metacognition_config.yaml`
   - Restart backend to see changes
   - Verify configuration validation

## Expected Behavior

### Normal Operation
- **Green status indicators** across all components
- **Real-time events** streaming at ~1-10 events per second
- **Automatic gap detection** when asking unknown topics
- **Learning plans** created and executed autonomously

### Performance Metrics
- **Gap detection**: < 100ms response time
- **Event streaming**: < 50ms latency
- **Memory usage**: Stable with circular buffers
- **Connection handling**: Support for multiple clients

## Troubleshooting

### Common Issues

1. **Import Errors**
   ```bash
   # Ensure PyYAML is installed
   pip install PyYAML>=6.0.1
   
   # Check Python path
   python -c "import backend.config_manager; print('OK')"
   ```

2. **Configuration Not Loading**
   - Check `backend/config/enhanced_metacognition_config.yaml` exists
   - Verify YAML syntax is valid
   - Check file permissions

3. **WebSocket Connection Issues**
   - Verify backend is running on correct port
   - Check browser console for connection errors
   - Ensure CORS is configured for your frontend URL

4. **No Cognitive Events**
   - Check if enhanced metacognition is enabled in config
   - Verify WebSocket manager initialization
   - Look for error messages in backend logs

### Debug Mode
Enable debug logging by setting in config:
```yaml
logging:
  level: "DEBUG"
  log_cognitive_events: true
```

## Advanced Testing

### Load Testing
```bash
# Test with multiple concurrent connections
# Open multiple browser tabs with the dashboard
# Monitor performance metrics
```

### Integration Testing
```bash
# Run the test suite
cd tests/enhanced_metacognition
python test_integration.py

# Or with pytest
pytest test_integration.py -v
```

### Configuration Testing
```bash
# Test different configurations
cp backend/config/enhanced_metacognition_config.yaml backup.yaml

# Edit config with different settings
# Restart backend and test behavior
```

## What to Look For

### Success Indicators ✅
- Smooth streaming of cognitive events
- Automatic knowledge gap detection
- Learning plans created and executed
- Health metrics showing good performance
- No error messages in logs

### Warning Signs ⚠️
- Connection timeouts or errors
- Missing cognitive events
- High memory usage
- Component health showing "degraded"
- Import or configuration errors

## Support & Next Steps

### If Everything Works
🎉 Congratulations! You now have:
- Autonomous knowledge acquisition
- Real-time cognitive transparency
- Performance-optimized streaming
- Comprehensive health monitoring

### If Issues Occur
1. Check the verification script output
2. Review backend logs for errors
3. Ensure all dependencies are installed
4. Verify configuration file syntax

### Ready for More?
- Explore advanced configuration options
- Implement custom learning strategies
- Add LLM integration for enhanced reasoning
- Build custom cognitive event processors

## Quick Commands Reference

```bash
# Verify implementation
python enhanced_metacognition_verification.py

# Start backend with enhanced features
cd backend && python main.py

# Start frontend
cd svelte-frontend && npm run dev

# Run tests
python tests/enhanced_metacognition/test_integration.py

# Check configuration
python -c "from backend.config_manager import get_config; print(get_config())"

# Test imports
python -c "from backend.enhanced_cognitive_api import router; print('API Ready')"
```

Happy testing! 🧠✨
