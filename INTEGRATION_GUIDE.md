# GödelOS Web Demonstration Interface - Integration Guide

## Overview

This guide provides comprehensive instructions for integrating and testing the GödelOS web demonstration interface, which consists of:

- **Backend**: FastAPI server with GödelOS integration, real-time WebSocket streaming, and comprehensive API endpoints
- **Frontend**: HTML/CSS/JavaScript interface with D3.js visualizations, cognitive layers display, and WebSocket support

## Architecture

```
┌─────────────────┐    HTTP/WebSocket    ┌──────────────────┐
│                 │ ◄─────────────────► │                  │
│    Frontend     │                     │     Backend      │
│  (Port 3000)    │                     │   (Port 8000)    │
│                 │                     │                  │
└─────────────────┘                     └──────────────────┘
                                                 │
                                                 ▼
                                        ┌──────────────────┐
                                        │                  │
                                        │   GödelOS Core   │
                                        │     System       │
                                        │                  │
                                        └──────────────────┘
```

## Quick Start

### Method 1: Automated Startup (Recommended)

```bash
# Make the startup script executable (if not already done)
chmod +x start-system.sh

# Start the complete system
./start-system.sh
```

This script will:
1. Create a Python virtual environment for the backend
2. Install all required dependencies
3. Start the backend server on port 8000
4. Start the frontend server on port 3000
5. Perform health checks
6. Display status information

### Method 2: Manual Startup

#### Step 1: Start the Backend

```bash
cd backend

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start the backend server
python main.py
```

The backend will start on `http://localhost:8000`

#### Step 2: Start the Frontend

```bash
cd godelos-frontend

# Start a simple HTTP server
python3 -m http.server 3000
# Or use any other static file server
```

The frontend will be available at `http://localhost:3000`

## Integration Testing

### Automated Integration Tests

Run the comprehensive integration test suite:

```bash
# Install test dependencies
pip install requests websockets

# Run integration tests (ensure both services are running)
python test-integration.py
```

The test suite validates:
- ✅ Backend health and API endpoints
- ✅ Natural language query processing
- ✅ Knowledge base operations
- ✅ Cognitive state retrieval
- ✅ WebSocket connectivity and real-time streaming
- ✅ Frontend accessibility

### Manual Testing Checklist

#### Backend API Testing

1. **Health Check**
   ```bash
   curl http://localhost:8000/health
   ```

2. **Process Query**
   ```bash
   curl -X POST http://localhost:8000/api/query \
     -H "Content-Type: application/json" \
     -d '{"query": "What is consciousness?", "include_reasoning": true}'
   ```

3. **Get Knowledge**
   ```bash
   curl http://localhost:8000/api/knowledge?limit=10
   ```

4. **Cognitive State**
   ```bash
   curl http://localhost:8000/api/cognitive-state
   ```

#### Frontend Testing

1. **Open the Interface**
   - Navigate to `http://localhost:3000`
   - Verify all panels load correctly

2. **Test Query Submission**
   - Enter a natural language query
   - Submit and verify response appears
   - Check reasoning trace displays

3. **Test Real-time Updates**
   - Observe cognitive layer animations
   - Verify WebSocket connection status

4. **Test Visualizations**
   - Switch between visualization types
   - Interact with knowledge graph elements

## API Endpoints

### Core Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | System information |
| GET | `/health` | Health status |
| POST | `/api/query` | Process natural language query |
| GET | `/api/knowledge` | Retrieve knowledge base items |
| POST | `/api/knowledge` | Add knowledge to system |
| GET | `/api/cognitive-state` | Get current cognitive state |

### WebSocket Endpoints

| Endpoint | Description |
|----------|-------------|
| `/ws/cognitive-stream` | Real-time cognitive events stream |

## Data Flow

### Query Processing Flow

1. **Frontend** → User enters query
2. **Frontend** → HTTP POST to `/api/query`
3. **Backend** → Processes query through GödelOS
4. **Backend** → Returns structured response
5. **Frontend** → Displays response and updates UI
6. **Backend** → Broadcasts cognitive events via WebSocket
7. **Frontend** → Updates real-time visualizations

### Real-time Updates Flow

1. **Backend** → Cognitive state changes
2. **Backend** → Broadcasts event via WebSocket
3. **Frontend** → Receives WebSocket message
4. **Frontend** → Updates cognitive layer visualizations
5. **Frontend** → Animates changes in real-time

## Configuration

### Backend Configuration

Edit `backend/config.py` or set environment variables:

```python
# Server settings
HOST = "0.0.0.0"
PORT = 8000
DEBUG = True

# CORS settings
ALLOWED_ORIGINS = ["http://localhost:3000", "http://127.0.0.1:3000"]

# GödelOS settings
GODELOS_LOG_LEVEL = "INFO"
ENABLE_REAL_TIME_STREAMING = True
```

### Frontend Configuration

Edit frontend JavaScript files to modify:

```javascript
// API and WebSocket URLs
const API_BASE_URL = 'http://localhost:8000';
const WEBSOCKET_URL = 'ws://localhost:8000/ws/cognitive-stream';

// Visualization settings
const UPDATE_INTERVAL = 1000; // ms
const MAX_HISTORY_SIZE = 100;
```

## Troubleshooting

### Common Issues

#### Backend Issues

**Issue**: Backend fails to start
```
Solution: 
1. Check Python version (3.8+ required)
2. Verify all dependencies installed
3. Check port 8000 availability
4. Review backend logs for errors
```

**Issue**: GödelOS integration errors
```
Solution:
1. Ensure GödelOS core system is properly installed
2. Check Python path includes GödelOS modules
3. Verify all required dependencies are available
```

#### Frontend Issues

**Issue**: WebSocket connection fails
```
Solution:
1. Verify backend is running and healthy
2. Check CORS configuration
3. Ensure WebSocket endpoint is accessible
4. Check browser console for errors
```

**Issue**: API calls fail with CORS errors
```
Solution:
1. Add frontend URL to backend CORS allowed origins
2. Ensure proper Content-Type headers
3. Check network connectivity
```

#### Integration Issues

**Issue**: Query processing fails
```
Solution:
1. Test backend API directly with curl
2. Check request/response data formats
3. Verify GödelOS system is responding
4. Review backend logs for processing errors
```

### Performance Optimization

#### Backend Performance

1. **Enable caching** for frequently accessed data
2. **Optimize query processing** with parallel execution
3. **Limit WebSocket broadcast frequency** to reduce overhead
4. **Use connection pooling** for database operations

#### Frontend Performance

1. **Debounce user inputs** to reduce API calls
2. **Implement virtual scrolling** for large data sets
3. **Optimize visualization rendering** with requestAnimationFrame
4. **Cache static assets** with appropriate headers

## Development Guidelines

### Adding New API Endpoints

1. Define Pydantic models in `backend/models.py`
2. Implement endpoint in `backend/main.py`
3. Add corresponding frontend API client methods
4. Update integration tests
5. Document the new endpoint

### Adding New Visualizations

1. Create visualization component in appropriate frontend script
2. Add data processing logic
3. Implement real-time update handlers
4. Add user interaction controls
5. Test with various data scenarios

### Error Handling

#### Backend Error Handling

```python
try:
    result = await godelos_integration.process_query(query)
    return QueryResponse(**result)
except Exception as e:
    logger.error(f"Query processing failed: {e}")
    raise HTTPException(status_code=500, detail=str(e))
```

#### Frontend Error Handling

```javascript
try {
    const response = await apiClient.processQuery(query);
    this.handleQueryResponse(response);
} catch (error) {
    console.error('Query failed:', error);
    this.showError(`Query failed: ${error.message}`);
}
```

## Security Considerations

1. **Input Validation**: All user inputs are validated on both frontend and backend
2. **CORS Configuration**: Properly configured to allow only trusted origins
3. **Rate Limiting**: Implement rate limiting for API endpoints
4. **WebSocket Security**: Validate all WebSocket messages
5. **Error Information**: Avoid exposing sensitive system information in errors

## Deployment

### Production Deployment

1. **Backend**: Use production ASGI server (e.g., Gunicorn with Uvicorn workers)
2. **Frontend**: Serve static files through a web server (e.g., Nginx)
3. **Reverse Proxy**: Use Nginx or similar for load balancing and SSL termination
4. **Monitoring**: Implement logging, metrics, and health checks
5. **Security**: Enable HTTPS, proper CORS, and security headers

### Docker Deployment

```dockerfile
# Example Dockerfile for backend
FROM python:3.9-slim
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install -r requirements.txt
COPY backend/ .
COPY godelOS/ ./godelOS/
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Support and Maintenance

### Monitoring

1. **Health Checks**: Regular automated health checks
2. **Performance Metrics**: Monitor response times and resource usage
3. **Error Tracking**: Centralized error logging and alerting
4. **User Analytics**: Track usage patterns and performance

### Updates and Maintenance

1. **Dependency Updates**: Regular security and feature updates
2. **Backup Procedures**: Regular backups of knowledge base and configurations
3. **Testing**: Comprehensive testing before deployments
4. **Documentation**: Keep documentation updated with changes

---

For additional support or questions, please refer to the main GödelOS documentation or contact the development team.