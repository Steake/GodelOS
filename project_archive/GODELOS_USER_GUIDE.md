# GödelOS Complete User Guide
*Modern Cognitive Architecture with Knowledge Ingestion*

## 🚀 Quick Start Guide

### **System Requirements**
- Python 3.8+ with pip
- Modern web browser (Chrome, Firefox, Safari, Edge)
- 4GB+ RAM recommended
- Internet connection for Wikipedia and web content

### **Installation & Setup**

1. **Install Dependencies**
   ```bash
   # Install Python packages
   pip install fastapi uvicorn pydantic aiohttp aiofiles PyPDF2 python-docx beautifulsoup4
   ```

2. **Start Backend Server**
   ```bash
   cd backend
   python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

3. **Start Frontend Server**
   ```bash
   cd godelos-frontend
   python3 -m http.server 3000
   ```

4. **Access Application**
   - Open browser to: `http://localhost:3000`
   - Verify connection status shows "Connected" in top navigation

## 🎯 Interface Overview

### **Main Navigation**
- **🔴/🟢 Connection Status**: Shows backend connectivity
- **⚙️ System Status**: Displays "Active" or "Idle" 
- **🔍 Query Panel**: Main interaction area
- **📊 Knowledge Graph**: Visual knowledge exploration
- **🧠 Cognitive Layers**: Real-time reasoning display

### **Key Interface Elements**

#### **Query Interface Panel**
- **Natural Language Query**: Large text area for questions
- **Query Type Dropdown**: Select reasoning approach
  - Knowledge Retrieval
  - Logical Reasoning  
  - Creative Synthesis
  - Problem Solving
- **Confidence Threshold**: Slider to filter results (0.1-1.0)
- **Suggested Queries**: Pre-built examples by category

#### **Knowledge Visualization Panel**
- **Knowledge Graph**: Interactive node-link diagram
- **Zoom Controls**: In/Out buttons for navigation
- **Layout Options**: Different arrangement algorithms
- **Node Information**: Click nodes for details

#### **Cognitive Transparency Panels**
- **Reasoning Visualizer**: Step-by-step thinking process
- **Metacognitive Dashboard**: Self-monitoring display
- **Uncertainty Analysis**: Confidence tracking
- **Provenance Explorer**: Source tracing

## 📚 Core Features Guide

### **1. Submitting Queries**

#### **Basic Query Submission**
1. Click in the "Natural Language Query" text area
2. Type your question (e.g., "What is consciousness?")
3. Select query type from dropdown (default: Knowledge Retrieval)
4. Adjust confidence threshold if needed
5. Press **Ctrl+Enter** to submit

#### **Query Types Explained**
- **Knowledge Retrieval**: Find and synthesize information
- **Logical Reasoning**: Apply formal logic and inference
- **Creative Synthesis**: Generate novel combinations
- **Problem Solving**: Systematic solution finding

#### **Using Suggested Queries**
- Browse categories: Consciousness & Cognition, AI & Machine Learning, Logic & Reasoning
- Click any suggested query to auto-fill the input area
- Modify suggested queries to customize your request

### **2. Knowledge Ingestion System**

#### **Importing from URLs**
1. Navigate to Knowledge Ingestion panel
2. Select "URL Import" tab
3. Enter webpage URL
4. Click "Import Content"
5. Wait for processing confirmation

#### **File Upload**
1. Click "File Upload" tab
2. Select file types supported:
   - **PDF**: Research papers, documents
   - **TXT**: Plain text files
   - **DOCX**: Microsoft Word documents
   - **JSON**: Structured data files
3. Drag and drop or click to browse
4. Monitor upload progress bar

#### **Wikipedia Integration**
1. Select "Wikipedia" tab
2. Enter search terms
3. Browse search results
4. Select articles to import
5. Choose specific sections if needed

#### **Manual Text Entry**
1. Click "Manual Entry" tab
2. Paste or type content directly
3. Add title and description
4. Categorize content with tags
5. Save to knowledge base

### **3. Knowledge Management**

#### **Searching Knowledge Base**
1. Use search bar in Knowledge Management panel
2. Enter keywords or phrases
3. Apply filters:
   - Content type (PDF, web, text)
   - Date range
   - Categories/tags
   - Source type
4. Sort results by relevance, date, or source

#### **Organizing Knowledge**
- **Categories**: Automatically assigned based on content
- **Tags**: Manual labels for flexible organization
- **Collections**: Group related items together
- **Favorites**: Mark important items for quick access

#### **Knowledge Export**
1. Select items to export
2. Choose format:
   - JSON (structured data)
   - PDF (formatted document)
   - TXT (plain text)
   - CSV (tabular data)
3. Download exported file

### **4. Cognitive Transparency Features**

#### **Reasoning Visualization**
- **Real-time Display**: Watch reasoning unfold step-by-step
- **Reasoning Tree**: Hierarchical thought structure
- **Confidence Indicators**: Color-coded certainty levels
- **Source Attribution**: Links to knowledge sources

#### **Knowledge Graph Exploration**
- **Interactive Navigation**: Click and drag nodes
- **Relationship Types**: Different edge colors for relation types
- **Zoom and Pan**: Mouse wheel and drag to navigate
- **Node Details**: Hover for quick info, click for full details

#### **Metacognitive Dashboard**
- **Self-Monitoring**: System awareness indicators
- **Learning Progress**: Knowledge acquisition metrics
- **Reasoning Quality**: Performance assessments
- **Uncertainty Tracking**: Confidence evolution over time

### **5. Advanced Features**

#### **Batch Processing**
- Import multiple files simultaneously
- Process large document collections
- Monitor progress for each item
- Handle errors gracefully

#### **Real-time Updates**
- WebSocket connections for live updates
- Instant reasoning visualization
- Progressive knowledge graph building
- Live connection status monitoring

#### **Provenance Tracking**
- Trace information back to sources
- Understand reasoning derivations
- Verify claim authenticity
- Explore knowledge lineage

## 🔧 Configuration Options

### **Query Processing Settings**
- **Default Query Type**: Set preferred reasoning mode
- **Confidence Threshold**: Default filtering level
- **Response Length**: Preferred answer detail level
- **Visualization Depth**: Reasoning tree complexity

### **Knowledge Import Settings**
- **Auto-categorization**: Enable/disable automatic tagging
- **Content Filtering**: Skip certain content types
- **Processing Timeout**: Maximum time for large files
- **Duplicate Detection**: Prevent duplicate imports

### **Interface Customization**
- **Theme Options**: Dark/light mode toggle
- **Panel Layout**: Rearrange interface sections
- **Notification Settings**: Control alert preferences
- **Keyboard Shortcuts**: Customize key bindings

## 🔍 Troubleshooting Guide

### **Connection Issues**
**Problem**: "Disconnected from backend" message
**Solutions**:
1. Verify backend server is running on port 8000
2. Check firewall settings
3. Restart backend server
4. Clear browser cache and reload

**Problem**: WebSocket connection fails
**Solutions**:
1. Check browser WebSocket support
2. Verify network connectivity
3. Try different browser
4. Check proxy settings

### **Query Processing Issues**
**Problem**: No response to queries
**Solutions**:
1. Check backend connection status
2. Verify query format and length
3. Try simpler query first
4. Check server logs for errors

**Problem**: Slow response times
**Solutions**:
1. Reduce confidence threshold
2. Simplify query complexity
3. Check system resources
4. Optimize knowledge base size

### **Knowledge Import Issues**
**Problem**: File upload fails
**Solutions**:
1. Check file size limits
2. Verify file format support
3. Try smaller files first
4. Check available disk space

**Problem**: Wikipedia import errors
**Solutions**:
1. Verify internet connection
2. Try different search terms
3. Check Wikipedia API status
4. Use manual text entry as backup

### **Performance Optimization**
**Problem**: Slow interface response
**Solutions**:
1. Close unused browser tabs
2. Clear browser cache
3. Reduce visualization complexity
4. Limit concurrent operations

**Problem**: High memory usage
**Solutions**:
1. Limit knowledge base size
2. Export and archive old content
3. Restart browser periodically
4. Use file-based storage

## 📊 Best Practices

### **Effective Querying**
- **Be Specific**: Clear, focused questions get better answers
- **Use Context**: Reference previous queries or knowledge
- **Iterate**: Refine queries based on initial results
- **Explore Types**: Try different query types for varied perspectives

### **Knowledge Organization**
- **Consistent Tagging**: Use standardized tag vocabulary
- **Regular Cleanup**: Remove outdated or duplicate content
- **Source Documentation**: Always note content origins
- **Category Structure**: Maintain logical organization hierarchy

### **System Maintenance**
- **Regular Backups**: Export knowledge base periodically
- **Monitor Performance**: Watch for slowdowns or errors
- **Update Dependencies**: Keep Python packages current
- **Clean Logs**: Remove old log files to save space

## 🎓 Learning Path

### **Beginner (First Week)**
1. Submit basic queries using suggested examples
2. Import simple text files and URLs
3. Explore knowledge graph visualization
4. Practice using different query types

### **Intermediate (First Month)**
1. Build substantial knowledge base from multiple sources
2. Use advanced search and filtering
3. Understand reasoning visualization patterns
4. Organize knowledge with categories and tags

### **Advanced (Ongoing)**
1. Optimize query strategies for complex problems
2. Develop systematic knowledge curation workflows
3. Leverage cognitive transparency for learning
4. Contribute to system improvement and documentation

## 🔗 Additional Resources

### **Documentation**
- [`FINAL_INTEGRATION_REPORT.md`](FINAL_INTEGRATION_REPORT.md) - Complete system overview
- [`backend/README.md`](backend/README.md) - Backend API documentation
- [`INTEGRATION_GUIDE.md`](INTEGRATION_GUIDE.md) - Technical integration details

### **Support**
- Check system logs for detailed error information
- Review browser console for frontend issues
- Monitor backend terminal for server messages
- Refer to troubleshooting section for common problems

### **Community**
- Share effective query patterns
- Contribute knowledge organization strategies
- Report bugs and suggest improvements
- Participate in system development discussions

---

*GödelOS Cognitive Architecture - Complete User Guide*
*Version 2.0 - Updated: 2025-05-27*