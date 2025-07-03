# GödelOS Frontend - Web Demonstration Interface

A sophisticated web interface for the GödelOS cognitive architecture system, built with vanilla HTML, CSS, and JavaScript. This frontend provides real-time visualization of knowledge graphs, cognitive processes, and natural language query processing.

## Features

### 🧠 Cognitive Layers Visualization
- **Manifest Consciousness**: Real-time attention focus and working memory visualization
- **Agentic Processes**: Live monitoring of query processing, knowledge retrieval, and inference engines
- **Daemon Threads**: Background process activity including memory consolidation and learning systems

### 🔍 Knowledge Visualization
- **Interactive Knowledge Graph**: D3.js-powered network visualization with drag-and-drop nodes
- **Concept Hierarchy**: Tree-based visualization of knowledge relationships
- **Semantic Network**: Multi-typed node visualization for concepts, relations, and instances

### 💬 Natural Language Interface
- **Query Input**: Natural language query form with type selection and confidence thresholds
- **Multi-format Responses**: Natural language, formal logic, metadata, and reasoning trace outputs
- **Real-time Processing**: Live updates during query processing with visual feedback

### 🌐 Real-time Communication
- **WebSocket Integration**: Placeholder WebSocket implementation for backend communication
- **Live Updates**: Real-time cognitive layer updates and system status monitoring
- **Connection Management**: Automatic reconnection and connection status indicators

## Architecture

### File Structure
```
godelos-frontend/
├── index.html                 # Main application entry point
├── src/
│   ├── styles/
│   │   ├── main.css          # Core layout and styling
│   │   ├── components.css    # Reusable component styles
│   │   └── visualizations.css # Visualization-specific styles
│   └── scripts/
│       ├── main.js           # Main application controller
│       ├── websocket.js      # WebSocket connection manager
│       ├── visualization.js  # D3.js knowledge graph handler
│       ├── cognitive-layers.js # Cognitive processes visualization
│       └── query-handler.js  # Query form and response management
└── README.md
```

### Component Architecture

#### Main Application (`main.js`)
- Coordinates all components and manages global application state
- Handles keyboard shortcuts, window resizing, and error management
- Manages panel toggles and responsive layout

#### WebSocket Manager (`websocket.js`)
- Manages real-time communication with backend (currently simulated)
- Handles connection states, reconnection logic, and message queuing
- Provides mock data generation for demonstration purposes

#### Visualization Manager (`visualization.js`)
- D3.js-based knowledge graph rendering with force simulation
- Support for multiple visualization types (graph, hierarchy, network)
- Interactive node selection, dragging, and information display

#### Cognitive Layers (`cognitive-layers.js`)
- Real-time visualization of consciousness layers
- Animated attention focus and working memory displays
- Process and daemon thread activity monitoring

#### Query Handler (`query-handler.js`)
- Form validation and submission management
- Response formatting across multiple tabs (natural language, formal logic, metadata, reasoning trace)
- Query history and export functionality

## Getting Started

### Prerequisites
- Modern web browser with JavaScript enabled
- Local web server (recommended for development)

### Installation

1. **Clone or download the frontend files**
   ```bash
   # If part of the larger GödelOS project
   cd godelos-frontend
   ```

2. **Serve the files using a local web server**
   ```bash
   # Using Python
   python -m http.server 8000
   
   # Using Node.js
   npx serve .
   
   # Using PHP
   php -S localhost:8000
   ```

3. **Open in browser**
   ```
   http://localhost:8000
   ```

### Usage

#### Submitting Queries
1. Enter a natural language question in the query panel
2. Select query type (Knowledge Retrieval, Logical Reasoning, Learning Task, Metacognitive Analysis)
3. Adjust confidence threshold if needed
4. Click "Submit Query" or press Ctrl+Enter

#### Exploring Visualizations
- **Knowledge Graph**: Click and drag nodes to explore relationships
- **Node Information**: Hover over nodes to see detailed information
- **Visualization Types**: Switch between graph, hierarchy, and network views using the dropdown

#### Monitoring Cognitive Processes
- **Manifest Consciousness**: Watch attention focus and working memory updates
- **Agentic Processes**: Monitor active processes during query processing
- **Daemon Threads**: Observe background system activities

#### Viewing Results
- **Natural Language**: Human-readable response
- **Formal Logic**: Logical representation of the response
- **Metadata**: Processing statistics and confidence metrics
- **Reasoning Trace**: Step-by-step reasoning process

## Configuration

### WebSocket Connection
To connect to a real GödelOS backend, modify the WebSocket URL in `main.js`:

```javascript
getWebSocketURL() {
    return 'ws://your-backend-host:8080';
}
```

### Styling Customization
- Modify CSS custom properties in `main.css` for color themes
- Adjust layout breakpoints for responsive design
- Customize animation timings and effects

### Mock Data
Current implementation includes comprehensive mock data for demonstration. To disable mock mode and use real backend:

1. Set `MOCK_MODE = false` in `websocket.js`
2. Implement actual WebSocket event handlers
3. Remove mock data generation functions

## Browser Compatibility

- **Chrome/Chromium**: 80+
- **Firefox**: 75+
- **Safari**: 13+
- **Edge**: 80+

### Required Features
- ES6+ JavaScript support
- CSS Grid and Flexbox
- SVG and Canvas support
- WebSocket API
- Local Storage API

## Development

### Adding New Visualizations
1. Create visualization function in `visualization.js`
2. Add corresponding CSS styles in `visualizations.css`
3. Update visualization type selector in HTML

### Extending Cognitive Layers
1. Add new layer visualization in `cognitive-layers.js`
2. Create corresponding HTML structure
3. Implement update methods for real-time data

### Custom Components
1. Define component styles in `components.css`
2. Add component logic to appropriate script file
3. Initialize in `main.js` if needed

## Performance Considerations

### Optimization Features
- Debounced window resize handlers
- Animation pausing when page is hidden
- Efficient D3.js force simulation
- Minimal DOM manipulation

### Recommended Practices
- Use browser dev tools to monitor performance
- Test with large knowledge graphs (1000+ nodes)
- Monitor memory usage during extended sessions
- Optimize for target device capabilities

## Troubleshooting

### Common Issues

**Visualization not rendering**
- Check browser console for JavaScript errors
- Ensure D3.js library is loaded
- Verify SVG element dimensions

**WebSocket connection fails**
- Check backend server status
- Verify WebSocket URL configuration
- Review browser network tab for connection attempts

**Slow performance**
- Reduce knowledge graph complexity
- Disable non-essential animations
- Check for memory leaks in browser dev tools

**Responsive layout issues**
- Test at various screen sizes
- Check CSS media queries
- Verify flexbox/grid browser support

## Future Enhancements

### Planned Features
- Three.js 3D knowledge graph visualization
- Advanced query syntax highlighting
- Collaborative session support
- Export to various formats (PDF, PNG, JSON)
- Accessibility improvements (ARIA labels, keyboard navigation)

### Integration Opportunities
- Real-time collaboration via WebRTC
- Voice query input via Web Speech API
- Augmented reality visualization via WebXR
- Machine learning model visualization

## Contributing

When contributing to the frontend:

1. Follow existing code style and patterns
2. Test across multiple browsers
3. Ensure responsive design compatibility
4. Document new features and components
5. Consider accessibility implications

## License

This frontend implementation is part of the larger GödelOS project. Please refer to the main project license for usage terms.

## Support

For technical support or questions about the frontend implementation:

1. Check browser console for error messages
2. Review this documentation
3. Test with mock data to isolate issues
4. Report bugs with browser and system information