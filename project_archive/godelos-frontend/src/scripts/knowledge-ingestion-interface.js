class KnowledgeIngestionInterface {
    constructor(containerId, endpoint = '/api/knowledge') {
        this.containerId = containerId;
        this.container = document.getElementById(containerId);
        this.endpoint = endpoint;
        this.activeImports = new Map(); // To track active import processes
        this.initialized = false;

        if (!this.container) {
            console.error(`Knowledge Ingestion container #${containerId} not found.`);
            return;
        }
        this.renderInterface();
        this.initialized = true;

        // Use the global WebSocket manager
        if (window.wsManager) {
            this.registerWebSocketHandlers(window.wsManager);
        } else {
            // Fallback or error if wsManager is not ready, might need to wait for DOMContentLoaded
            // or for wsManager to be initialized.
            document.addEventListener('DOMContentLoaded', () => {
                if (window.wsManager) {
                    this.registerWebSocketHandlers(window.wsManager);
                } else {
                    console.error("Global WebSocketManager (wsManager) not available for KnowledgeIngestionInterface.");
                }
            });
        }
    }

    registerWebSocketHandlers(wsManager) {
        // Register with the global event system instead of directly with wsManager
        window.addEventListener('importStarted', (event) => this.handleImportStarted(event.detail));
        window.addEventListener('importProgress', (event) => this.handleImportProgress(event.detail));
        window.addEventListener('importCompleted', (event) => this.handleImportCompleted(event.detail));
        window.addEventListener('importFailed', (event) => this.handleImportFailed(event.detail));
        
        console.log("KnowledgeIngestionInterface registered handlers with global event system.");
    }

    handleImportStarted(data) {
        console.log('Import started:', data);
        if (data.import_id && data.source_type && data.source) {
            this.addToProgress(data.import_id, data.source_type, data.source);
        }
    }

    handleImportProgress(data) {
        this.updateProgress(data.import_id, data.progress, data.status, data.message);
    }

    handleImportCompleted(data) {
        this.updateProgress(data.import_id, 100, 'completed', data.message || 'Import completed successfully');
    }

    handleImportFailed(data) {
        this.updateProgress(data.import_id, 0, 'failed', data.error || data.message || 'Import failed');
    }

    initializeInterface(containerId = 'knowledgeIngestion') {
        this.container = document.getElementById(containerId);
        if (!this.container) {
            throw new Error(`Container #${containerId} not found`);
        }
        
        // Clear any existing content
        this.container.innerHTML = '';
        
        // Render the complete interface
        this.renderInterface();
        
        this.initialized = true;
        console.log('Knowledge Ingestion Interface initialized with full UI');
        return this;
    }

    renderInterface() {
        this.container.innerHTML = `
            <div class="knowledge-ingestion-interface">
                <div class="ingestion-header">
                    <h2>Knowledge Ingestion</h2>
                    <p class="text-secondary">Import knowledge from various sources into the system</p>
                </div>

                <div class="ingestion-tabs">
                    <button class="tab-btn active" data-tab="file">📁 File Upload</button>
                    <button class="tab-btn" data-tab="text">📝 Manual Text</button>
                    <button class="tab-btn" data-tab="url">🌐 Web URL</button>
                    <button class="tab-btn" data-tab="wikipedia">📖 Wikipedia</button>
                    <button class="tab-btn" data-tab="batch">🔄 Batch Import</button>
                </div>

                <div class="ingestion-content">
                    <!-- File Upload Tab -->
                    <div class="tab-content active" id="file-tab">
                        <div class="file-upload-area" id="fileUploadArea">
                            <div class="upload-content">
                                <div class="upload-icon">📁</div>
                                <h3>Drop files here or click to browse</h3>
                                <p>Supported formats: PDF, TXT, DOCX, JSON, CSV, MD</p>
                                <button class="btn btn-primary" id="browseFilesBtn">Browse Files</button>
                            </div>
                        </div>
                        <input type="file" id="fileInput" multiple accept=".pdf,.txt,.docx,.json,.csv,.md" style="display: none;">
                        
                        <div class="upload-options">
                            <div class="form-group">
                                <label for="fileEncoding">Encoding:</label>
                                <select id="fileEncoding">
                                    <option value="utf-8">UTF-8</option>
                                    <option value="latin1">Latin-1</option>
                                    <option value="ascii">ASCII</option>
                                </select>
                            </div>
                            <div class="form-group">
                                <label for="fileCategories">Categories (comma-separated):</label>
                                <input type="text" id="fileCategories" placeholder="science, technology, research">
                            </div>
                        </div>
                    </div>

                    <!-- Manual Text Tab -->
                    <div class="tab-content" id="text-tab">
                        <div class="text-import-form">
                            <div class="form-group">
                                <label for="textTitle">Title:</label>
                                <input type="text" id="textTitle" placeholder="Enter title for this knowledge">
                            </div>
                            <div class="form-group">
                                <label for="textContent">Content:</label>
                                <textarea id="textContent" rows="10" placeholder="Enter your knowledge content here..."></textarea>
                            </div>
                            <div class="form-group">
                                <label for="textType">Knowledge Type:</label>
                                <select id="textType">
                                    <option value="fact">Fact</option>
                                    <option value="concept">Concept</option>
                                    <option value="rule">Rule</option>
                                    <option value="procedure">Procedure</option>
                                    <option value="hypothesis">Hypothesis</option>
                                </select>
                            </div>
                            <div class="form-group">
                                <label for="textCategories">Categories (comma-separated):</label>
                                <input type="text" id="textCategories" placeholder="science, technology, research">
                            </div>
                            <button class="btn btn-primary" id="importTextBtn">Import Text</button>
                        </div>
                    </div>

                    <!-- URL Import Tab -->
                    <div class="tab-content" id="url-tab">
                        <div class="url-import-form">
                            <div class="form-group">
                                <label for="urlInput">URL:</label>
                                <input type="url" id="urlInput" placeholder="https://example.com/article">
                            </div>
                            <div class="form-group">
                                <label for="urlCategories">Categories (comma-separated):</label>
                                <input type="text" id="urlCategories" placeholder="web, article, research">
                            </div>
                            <div class="form-group">
                                <label>
                                    <input type="checkbox" id="followLinks"> Follow internal links
                                </label>
                            </div>
                            <div class="form-group">
                                <label for="maxDepth">Max depth:</label>
                                <input type="number" id="maxDepth" value="1" min="1" max="5">
                            </div>
                            <button class="btn btn-primary" id="importUrlBtn">Import URL</button>
                        </div>
                    </div>

                    <!-- Wikipedia Tab -->
                    <div class="tab-content" id="wikipedia-tab">
                        <div class="wikipedia-import-form">
                            <div class="form-group">
                                <label for="wikipediaTitle">Wikipedia Page Title:</label>
                                <input type="text" id="wikipediaTitle" placeholder="Artificial Intelligence">
                            </div>
                            <div class="form-group">
                                <label for="wikipediaLanguage">Language:</label>
                                <select id="wikipediaLanguage">
                                    <option value="en">English</option>
                                    <option value="es">Spanish</option>
                                    <option value="fr">French</option>
                                    <option value="de">German</option>
                                    <option value="it">Italian</option>
                                    <option value="pt">Portuguese</option>
                                    <option value="zh">Chinese</option>
                                    <option value="ja">Japanese</option>
                                </select>
                            </div>
                            <div class="form-group">
                                <label>
                                    <input type="checkbox" id="includeReferences"> Include references
                                </label>
                            </div>
                            <div class="form-group">
                                <label>
                                    <input type="checkbox" id="includeInfobox"> Include infobox
                                </label>
                            </div>
                            <button class="btn btn-primary" id="importWikipediaBtn">Import Wikipedia Page</button>
                        </div>
                    </div>

                    <!-- Batch Import Tab -->
                    <div class="tab-content" id="batch-tab">
                        <div class="batch-import-form">
                            <p>Upload a JSON file with multiple import requests:</p>
                            <div class="file-upload-area" id="batchUploadArea">
                                <div class="upload-content">
                                    <div class="upload-icon">📂</div>
                                    <h3>Drop batch file here or click to browse</h3>
                                    <p>JSON format with import specifications</p>
                                    <button class="btn btn-primary" id="browseBatchBtn">Browse Batch File</button>
                                </div>
                            </div>
                            <input type="file" id="batchFileInput" accept=".json" style="display: none;">
                            
                            <div class="batch-example">
                                <h4>Example JSON format:</h4>
                                <pre><code>{
  "imports": [
    {
      "type": "url",
      "source": "https://example.com",
      "categories": ["web", "article"]
    },
    {
      "type": "wikipedia",
      "source": "Machine Learning",
      "language": "en"
    }
  ]
}</code></pre>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Progress Section -->
                <div class="import-progress-section" id="progressSection" style="display: none;">
                    <h3>Import Progress</h3>
                    <div class="progress-list" id="progressList"></div>
                </div>

                <!-- Import History -->
                <div class="import-history-section">
                    <h3>Recent Imports</h3>
                    <div class="history-list" id="historyList">
                        <div class="status-message">
                            <p>No recent imports</p>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // Initialize event listeners
        this.initializeEventListeners();
        
        // Load import history
        this.loadImportHistory();
    }

    initializeEventListeners() {
        // Tab switching
        const tabBtns = this.container.querySelectorAll('.tab-btn');
        const tabContents = this.container.querySelectorAll('.tab-content');
        
        tabBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                const tabId = btn.dataset.tab;
                
                // Update active tab
                tabBtns.forEach(b => b.classList.remove('active'));
                tabContents.forEach(c => c.classList.remove('active'));
                
                btn.classList.add('active');
                this.container.querySelector(`#${tabId}-tab`).classList.add('active');
            });
        });

        // File upload
        this.initializeFileUpload();
        
        // Text import
        const importTextBtn = this.container.querySelector('#importTextBtn');
        importTextBtn.addEventListener('click', () => this.importText());
        
        // URL import
        const importUrlBtn = this.container.querySelector('#importUrlBtn');
        importUrlBtn.addEventListener('click', () => this.importUrl());
        
        // Wikipedia import
        const importWikipediaBtn = this.container.querySelector('#importWikipediaBtn');
        importWikipediaBtn.addEventListener('click', () => this.importWikipedia());
        
        // Batch import
        this.initializeBatchUpload();
    }

    initializeFileUpload() {
        const uploadArea = this.container.querySelector('#fileUploadArea');
        const fileInput = this.container.querySelector('#fileInput');
        const browseBtn = this.container.querySelector('#browseFilesBtn');

        // Click to browse
        browseBtn.addEventListener('click', () => fileInput.click());
        uploadArea.addEventListener('click', () => fileInput.click());

        // Drag and drop
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('drag-over');
        });

        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('drag-over');
        });

        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('drag-over');
            
            const files = Array.from(e.dataTransfer.files);
            this.handleFileUpload(files);
        });

        // File input change
        fileInput.addEventListener('change', (e) => {
            const files = Array.from(e.target.files);
            this.handleFileUpload(files);
        });
    }

    initializeBatchUpload() {
        const batchArea = this.container.querySelector('#batchUploadArea');
        const batchInput = this.container.querySelector('#batchFileInput');
        const browseBatchBtn = this.container.querySelector('#browseBatchBtn');

        browseBatchBtn.addEventListener('click', () => batchInput.click());
        batchArea.addEventListener('click', () => batchInput.click());

        batchInput.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (file) {
                this.handleBatchUpload(file);
            }
        });
    }

    async handleFileUpload(files) {
        const encoding = this.container.querySelector('#fileEncoding').value;
        const categories = this.container.querySelector('#fileCategories').value
            .split(',').map(c => c.trim()).filter(c => c);

        for (const file of files) {
            try {
                const formData = new FormData();
                formData.append('file', file);
                formData.append('filename', file.name);
                formData.append('file_type', file.type || 'text/plain');
                formData.append('encoding', encoding);
                formData.append('categorization_hints', JSON.stringify(categories));

                const response = await fetch('http://localhost:8000/api/knowledge/import/file', {
                    method: 'POST',
                    body: formData
                });

                const result = await response.json();
                
                if (response.ok) {
                    this.showNotification(`File upload started: ${file.name}`, 'success');
                    // Don't manually add to progress - WebSocket import_started event will handle it
                } else {
                    this.showNotification(`Failed to upload ${file.name}: ${result.detail}`, 'error');
                }
            } catch (error) {
                this.showNotification(`Error uploading ${file.name}: ${error.message}`, 'error');
            }
        }
    }

    async importText() {
        const title = this.container.querySelector('#textTitle').value.trim();
        const content = this.container.querySelector('#textContent').value.trim();
        const knowledgeType = this.container.querySelector('#textType').value;
        const categories = this.container.querySelector('#textCategories').value
            .split(',').map(c => c.trim()).filter(c => c);

        if (!content) {
            this.showNotification('Please enter some content', 'error');
            return;
        }

        try {
            const requestData = {
                source: {
                    source_type: "text",
                    source_identifier: title || 'Manual Text Entry',
                    metadata: { source: 'manual_entry' }
                },
                content: content,
                title: title || 'Manual Text Entry',
                format_type: "plain",
                categorization_hints: categories
            };

            const response = await fetch('http://localhost:8000/api/knowledge/import/text', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(requestData)
            });

            const result = await response.json();
            
            if (response.ok) {
                this.showNotification('Text import started', 'success');
                
                // Clear form
                this.container.querySelector('#textTitle').value = '';
                this.container.querySelector('#textContent').value = '';
                this.container.querySelector('#textCategories').value = '';
                // Don't manually add to progress - WebSocket import_started event will handle it
            } else {
                this.showNotification(`Import failed: ${result.detail}`, 'error');
            }
        } catch (error) {
            this.showNotification(`Error: ${error.message}`, 'error');
        }
    }

    async importUrl() {
        const url = this.container.querySelector('#urlInput').value.trim();
        const categories = this.container.querySelector('#urlCategories').value
            .split(',').map(c => c.trim()).filter(c => c);
        const followLinks = this.container.querySelector('#followLinks').checked;
        const maxDepth = parseInt(this.container.querySelector('#maxDepth').value);

        if (!url) {
            this.showNotification('Please enter a URL', 'error');
            return;
        }

        try {
            const requestData = {
                source: {
                    source_type: "url",
                    source_identifier: url,
                    metadata: { source: 'url_import' }
                },
                url: url,
                max_depth: maxDepth,
                follow_links: followLinks,
                content_selectors: [],
                categorization_hints: categories
            };

            const response = await fetch('http://localhost:8000/api/knowledge/import/url', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(requestData)
            });

            const result = await response.json();
            
            if (response.ok) {
                this.showNotification('URL import started', 'success');
                
                // Clear form
                this.container.querySelector('#urlInput').value = '';
                this.container.querySelector('#urlCategories').value = '';
                // Don't manually add to progress - WebSocket import_started event will handle it
            } else {
                this.showNotification(`Import failed: ${result.detail}`, 'error');
            }
        } catch (error) {
            this.showNotification(`Error: ${error.message}`, 'error');
        }
    }

    async importWikipedia() {
        const pageTitle = this.container.querySelector('#wikipediaTitle').value.trim();
        const language = this.container.querySelector('#wikipediaLanguage').value;
        const includeReferences = this.container.querySelector('#includeReferences').checked;
        const includeInfobox = this.container.querySelector('#includeInfobox').checked;

        if (!pageTitle) {
            this.showNotification('Please enter a Wikipedia page title', 'error');
            return;
        }

        try {
            const requestData = {
                source: {
                    source_type: "wikipedia",
                    source_identifier: pageTitle,
                    metadata: { source: 'wikipedia_import' }
                },
                page_title: pageTitle,
                language: language,
                include_references: includeReferences,
                section_filter: []
            };

            const response = await fetch('http://localhost:8000/api/knowledge/import/wikipedia', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(requestData)
            });

            const result = await response.json();
            
            if (response.ok) {
                this.showNotification('Wikipedia import started', 'success');
                
                // Clear form
                this.container.querySelector('#wikipediaTitle').value = '';
                // Don't manually add to progress - WebSocket import_started event will handle it
            } else {
                this.showNotification(`Import failed: ${result.detail}`, 'error');
            }
        } catch (error) {
            this.showNotification(`Error: ${error.message}`, 'error');
        }
    }

    async handleBatchUpload(file) {
        try {
            const content = await this.readFileAsText(file);
            const batchData = JSON.parse(content);

            const response = await fetch('http://localhost:8000/api/knowledge/import/batch', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(batchData)
            });

            const result = await response.json();
            
            if (response.ok) {
                result.import_ids.forEach(importId => {
                    this.addToProgress(importId, 'batch', `Batch Import ${importId.slice(0, 8)}`);
                });
                this.showNotification(`Batch import started with ${result.batch_size} items`, 'success');
            } else {
                this.showNotification(`Batch import failed: ${result.detail}`, 'error');
            }
        } catch (error) {
            this.showNotification(`Error processing batch file: ${error.message}`, 'error');
        }
    }

    readFileAsText(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = () => resolve(reader.result);
            reader.onerror = reject;
            reader.readAsText(file);
        });
    }

    addToProgress(importId, type, source) {
        const progressSection = this.container.querySelector('#progressSection');
        const progressList = this.container.querySelector('#progressList');
        
        progressSection.style.display = 'block';
        
        const progressItem = document.createElement('div');
        progressItem.className = 'progress-item';
        progressItem.id = `progress-${importId}`;
        progressItem.innerHTML = `
            <div class="progress-header">
                <span class="progress-source">${this.getTypeIcon(type)} ${source}</span>
                <span class="progress-status">Queued</span>
            </div>
            <div class="progress-bar">
                <div class="progress-fill" style="width: 0%"></div>
            </div>
            <div class="progress-details">
                <span class="progress-text">Preparing import...</span>
                <button class="btn btn-sm btn-secondary cancel-btn" onclick="window.knowledgeIngestionInterface.cancelImport('${importId}')">Cancel</button>
            </div>
        `;
        
        progressList.appendChild(progressItem);
        this.activeImports.set(importId, { type, source, status: 'queued' });
    }

    updateProgress(importId, progress, status, message) {
        const progressItem = this.container.querySelector(`#progress-${importId}`);
        if (!progressItem) return;

        const progressFill = progressItem.querySelector('.progress-fill');
        const progressText = progressItem.querySelector('.progress-text');
        const progressStatus = progressItem.querySelector('.progress-status');

        if (progressFill) progressFill.style.width = `${progress}%`;
        if (progressText) progressText.textContent = message || 'Processing...';
        if (progressStatus) progressStatus.textContent = status;

        // Update active imports tracking
        if (this.activeImports.has(importId)) {
            this.activeImports.get(importId).status = status;
        }

        // If completed, move to history after a delay
        if (status === 'completed' || status === 'failed') {
            setTimeout(() => {
                this.moveToHistory(importId);
            }, 3000);
        }
    }

    async cancelImport(importId) {
        try {
            const response = await fetch(`http://localhost:8000/api/knowledge/import/${importId}`, {
                method: 'DELETE'
            });

            if (response.ok) {
                this.updateProgress(importId, 0, 'cancelled', 'Import cancelled');
                this.showNotification('Import cancelled', 'info');
            } else {
                this.showNotification('Failed to cancel import', 'error');
            }
        } catch (error) {
            this.showNotification(`Error cancelling import: ${error.message}`, 'error');
        }
    }

    moveToHistory(importId) {
        const progressItem = this.container.querySelector(`#progress-${importId}`);
        const historyList = this.container.querySelector('#historyList');
        
        if (progressItem && historyList) {
            // Remove status message if it exists
            const statusMessage = historyList.querySelector('.status-message');
            if (statusMessage) {
                statusMessage.remove();
            }

            // Convert progress item to history item
            progressItem.classList.add('history-item');
            progressItem.querySelector('.cancel-btn')?.remove();
            
            // Add timestamp
            const timestamp = document.createElement('div');
            timestamp.className = 'history-timestamp';
            timestamp.textContent = new Date().toLocaleString();
            progressItem.querySelector('.progress-details').appendChild(timestamp);
            
            // Move to history
            historyList.insertBefore(progressItem, historyList.firstChild);
            
            // Remove from active imports
            this.activeImports.delete(importId);
            
            // Hide progress section if no active imports
            if (this.activeImports.size === 0) {
                this.container.querySelector('#progressSection').style.display = 'none';
            }
        }
    }

    async loadImportHistory() {
        // This would load recent import history from the backend
        // For now, we'll just show the placeholder
    }

    getTypeIcon(type) {
        const icons = {
            file: '📁',
            text: '📝',
            url: '🌐',
            wikipedia: '📖',
            batch: '🔄'
        };
        return icons[type] || '📄';
    }

    showNotification(message, type = 'info') {
        // Create a simple notification system
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 12px 20px;
            background: ${type === 'error' ? '#dc3545' : type === 'success' ? '#28a745' : '#17a2b8'};
            color: white;
            border-radius: 4px;
            z-index: 10000;
            animation: slideIn 0.3s ease;
        `;

        document.body.appendChild(notification);

        setTimeout(() => {
            notification.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }

    async fetchSources() {
        if (!this.initialized) {
            throw new Error('Interface not initialized');
        }
        
        try {
            const response = await fetch(`${this.endpoint}/sources`);
            return await response.json();
        } catch (error) {
            console.error('Failed to fetch knowledge sources:', error);
            throw error;
        }
    }

    refresh() {
        this.loadImportHistory();
        return Promise.resolve();
    }
} // End of KnowledgeIngestionInterface class

// Explicitly attach the class to the window object
if (typeof window !== 'undefined') {
    window.KnowledgeIngestionInterface = KnowledgeIngestionInterface;
}