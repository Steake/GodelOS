class KnowledgeIngestionInterface {
    constructor() {
        this.initialized = false;
        this.containerId = 'knowledgeIngestionPane';
        this.activeImports = new Map();
    }

    initializeInterface() {
        const container = document.getElementById(this.containerId);
        if (!container) {
            throw new Error(`Container #${this.containerId} not found`);
        }

        // Create comprehensive interface HTML
        container.innerHTML = `
            <div class="ingestion-interface">
                <h3>Knowledge Ingestion</h3>
                
                <!-- Import Type Selector -->
                <div class="import-type-selector">
                    <label for="importType">Import Type:</label>
                    <select id="importType">
                        <option value="text">Manual Text</option>
                        <option value="url">Web URL</option>
                        <option value="file">File Upload</option>
                        <option value="wikipedia">Wikipedia</option>
                    </select>
                </div>

                <!-- Text Import -->
                <div id="textImport" class="import-section">
                    <h4>Manual Text Import</h4>
                    <textarea id="textContent" placeholder="Enter knowledge content..." rows="6" cols="50"></textarea>
                    <div class="form-group">
                        <label for="textTitle">Title:</label>
                        <input type="text" id="textTitle" placeholder="Knowledge title">
                    </div>
                    <div class="form-group">
                        <label for="textCategory">Category:</label>
                        <select id="textCategory">
                            <option value="fact">Fact</option>
                            <option value="rule">Rule</option>
                            <option value="concept">Concept</option>
                        </select>
                    </div>
                </div>

                <!-- URL Import -->
                <div id="urlImport" class="import-section" style="display: none;">
                    <h4>Web URL Import</h4>
                    <input type="url" id="urlInput" placeholder="https://example.com">
                    <div class="form-group">
                        <label>
                            <input type="checkbox" id="extractLinks"> Extract linked pages
                        </label>
                    </div>
                </div>

                <!-- File Import -->
                <div id="fileImport" class="import-section" style="display: none;">
                    <h4>File Upload</h4>
                    <input type="file" id="fileInput" accept=".txt,.pdf,.docx,.md">
                    <div class="file-info"></div>
                </div>

                <!-- Wikipedia Import -->
                <div id="wikipediaImport" class="import-section" style="display: none;">
                    <h4>Wikipedia Import</h4>
                    <input type="text" id="wikipediaQuery" placeholder="Search Wikipedia...">
                    <div class="form-group">
                        <label for="wikipediaLanguage">Language:</label>
                        <select id="wikipediaLanguage">
                            <option value="en">English</option>
                            <option value="es">Spanish</option>
                            <option value="fr">French</option>
                            <option value="de">German</option>
                        </select>
                    </div>
                </div>

                <!-- Import Controls -->
                <div class="ingestion-controls">
                    <button id="startImportBtn" class="primary-btn">Start Import</button>
                    <button id="clearFormBtn" class="secondary-btn">Clear Form</button>
                    <div class="status-indicator" id="statusIndicator">Ready</div>
                </div>

                <!-- Progress Section -->
                <div id="importProgress" class="progress-section" style="display: none;">
                    <div class="progress-bar">
                        <div class="progress-fill" id="progressFill"></div>
                    </div>
                    <div class="progress-text" id="progressText">Initializing...</div>
                </div>

                <!-- Recent Imports -->
                <div class="recent-imports">
                    <h4>Recent Imports</h4>
                    <div id="recentImportsList" class="imports-list">
                        <div class="no-imports">No imports yet</div>
                    </div>
                </div>
            </div>
        `;

        this.initializeEventListeners();
        this.initialized = true;
    }

    initializeEventListeners() {
        // Import type selector
        document.getElementById('importType').addEventListener('change', (e) => {
            this.showImportSection(e.target.value);
        });

        // Import button
        document.getElementById('startImportBtn').addEventListener('click', () => {
            this.handleImport();
        });

        // Clear form button
        document.getElementById('clearFormBtn').addEventListener('click', () => {
            this.clearForm();
        });

        // File input handler
        document.getElementById('fileInput').addEventListener('change', (e) => {
            this.handleFileSelection(e.target.files[0]);
        });
    }

    showImportSection(type) {
        // Hide all sections
        document.querySelectorAll('.import-section').forEach(section => {
            section.style.display = 'none';
        });

        // Show selected section
        const section = document.getElementById(`${type}Import`);
        if (section) {
            section.style.display = 'block';
        }
    }

    async handleImport() {
        const importType = document.getElementById('importType').value;
        const statusIndicator = document.getElementById('statusIndicator');
        const progressSection = document.getElementById('importProgress');
        
        try {
            statusIndicator.textContent = 'Starting import...';
            statusIndicator.className = 'status-indicator processing';
            progressSection.style.display = 'block';
            
            let importData;
            let endpoint;

            switch (importType) {
                case 'text':
                    importData = this.getTextImportData();
                    endpoint = '/api/knowledge/import/text';
                    break;
                case 'url':
                    importData = this.getUrlImportData();
                    endpoint = '/api/knowledge/import/url';
                    break;
                case 'file':
                    importData = await this.getFileImportData(); // This is FormData
                    endpoint = '/api/knowledge/import/file';
                    break;
                case 'wikipedia':
                    importData = this.getWikipediaImportData();
                    endpoint = '/api/knowledge/import/wikipedia';
                    break;
                default:
                    throw new Error('Invalid import type');
            }

            let requestOptions = {
                method: 'POST',
            };

            if (importType === 'file') {
                requestOptions.body = importData; 
            } else {
                requestOptions.headers = {
                    'Content-Type': 'application/json',
                };
                requestOptions.body = JSON.stringify(importData);
            }

            // Use the absolute base URL for the API call
            const baseApiUrl = window.apiClient && window.apiClient.baseUrl ? window.apiClient.baseUrl : 'http://localhost:8000';
            const fullEndpoint = `${baseApiUrl}${endpoint}`;
            
            console.log(`Knowledge Ingestion: Attempting fetch to: ${fullEndpoint} with method ${requestOptions.method}`);

            const response = await fetch(fullEndpoint, requestOptions);

            if (!response.ok) {
                // Try to get more detailed error from response body
                let errorDetail = response.statusText;
                try {
                    const errorResult = await response.json();
                    if (errorResult && errorResult.detail) {
                        errorDetail = errorResult.detail;
                    } else if (errorResult && errorResult.message) {
                        errorDetail = errorResult.message;
                    }
                } catch (e) {
                    // Ignore if response is not JSON or error parsing
                }
                throw new Error(`Import failed: ${errorDetail}`);
            }

            const result = await response.json();
            const importId = result.import_id;

            // Monitor import progress
            await this.monitorImportProgress(importId);
            
            statusIndicator.textContent = 'Import completed successfully';
            statusIndicator.className = 'status-indicator success';
            
            // Add to recent imports
            this.addToRecentImports(importType, importData, 'success');
            
            // Clear form
            this.clearForm();
            
        } catch (error) {
            console.error('Import failed:', error);
            statusIndicator.textContent = `Import failed: ${error.message}`;
            statusIndicator.className = 'status-indicator error';
            
            this.addToRecentImports(importType, {}, 'failed');
        } finally {
            setTimeout(() => {
                progressSection.style.display = 'none';
                statusIndicator.textContent = 'Ready';
                statusIndicator.className = 'status-indicator';
            }, 3000);
        }
    }

    getTextImportData() {
        return {
            content: document.getElementById('textContent').value,
            title: document.getElementById('textTitle').value,
            source: {
                source_type: 'text',
                source_identifier: document.getElementById('textTitle').value || 'Manual Entry',
                metadata: {
                    category: document.getElementById('textCategory').value,
                    created_by: 'user',
                    created_at: new Date().toISOString()
                }
            },
            format_type: 'plain',
            categorization_hints: [document.getElementById('textCategory').value],
            priority: 5
        };
    }

    getUrlImportData() {
        const url = document.getElementById('urlInput').value;
        return {
            url: url,
            source: {
                source_type: 'url',
                source_identifier: url,
                metadata: {
                    extract_links: document.getElementById('extractLinks').checked,
                    created_by: 'user',
                    created_at: new Date().toISOString()
                }
            },
            max_depth: document.getElementById('extractLinks').checked ? 2 : 1,
            follow_links: document.getElementById('extractLinks').checked,
            categorization_hints: [],
            priority: 5
        };
    }

    async getFileImportData() {
        const fileInput = document.getElementById('fileInput');
        const file = fileInput.files[0];
        
        if (!file) {
            throw new Error('No file selected');
        }

        // For file uploads, we need to use FormData
        const formData = new FormData();
        formData.append('file', file);
        
        // Add the source information as JSON
        const sourceData = {
            source: {
                source_type: 'file',
                source_identifier: file.name,
                metadata: {
                    file_size: file.size,
                    file_type: file.type,
                    created_by: 'user',
                    created_at: new Date().toISOString()
                }
            },
            filename: file.name,
            file_type: this.getFileTypeFromName(file.name),
            encoding: 'utf-8',
            categorization_hints: [],
            priority: 5
        };
        
        Object.keys(sourceData).forEach(key => {
            if (typeof sourceData[key] === 'object') {
                formData.append(key, JSON.stringify(sourceData[key]));
            } else {
                formData.append(key, sourceData[key]);
            }
        });

        return formData;
    }

    getWikipediaImportData() {
        const query = document.getElementById('wikipediaQuery').value;
        const language = document.getElementById('wikipediaLanguage').value;
        
        return {
            page_title: query,
            language: language,
            source: {
                source_type: 'wikipedia',
                source_identifier: `${language}:${query}`,
                metadata: {
                    language: language,
                    created_by: 'user',
                    created_at: new Date().toISOString()
                }
            },
            include_references: true,
            categorization_hints: [],
            priority: 5
        };
    }

    getFileTypeFromName(filename) {
        const extension = filename.toLowerCase().split('.').pop();
        const typeMap = {
            'pdf': 'pdf',
            'txt': 'txt',
            'json': 'json',
            'csv': 'csv',
            'docx': 'docx',
            'doc': 'docx',
            'md': 'txt'
        };
        return typeMap[extension] || 'txt';
    }

    async monitorImportProgress(importId) {
        const progressFill = document.getElementById('progressFill');
        const progressText = document.getElementById('progressText');
        const baseApiUrl = window.apiClient && window.apiClient.baseUrl ? window.apiClient.baseUrl : 'http://localhost:8000';

        while (true) {
            try {
                const response = await fetch(`${baseApiUrl}/api/knowledge/import/progress/${importId}`);
                // Check if the response is ok before trying to parse JSON
                if (!response.ok) {
                    let errorDetail = response.statusText;
                    try {
                        // Attempt to get a more specific error message from the backend if available
                        const errorResult = await response.json(); 
                        if (errorResult && errorResult.detail) {
                            errorDetail = errorResult.detail;
                        } else if (errorResult && errorResult.message) {
                            errorDetail = errorResult.message;
                        }
                    } catch (e) {
                        // If the error response isn't JSON, use the status text
                    }
                    throw new Error(`Progress monitoring failed: ${response.status} ${errorDetail}`);
                }

                const progress = await response.json();

                const percentage = progress.progress_percentage || 0;
                progressFill.style.width = `${percentage}%`;
                progressText.textContent = progress.current_step || 'Processing...';

                if (progress.status === 'completed' || progress.status === 'failed') {
                    if (progress.status === 'failed') {
                        // Use the error message from the progress object if available
                        throw new Error(progress.error_message || 'Import processing failed on server');
                    }
                    break; // Exit loop on completion or failure
                }

                await new Promise(resolve => setTimeout(resolve, 1000)); // Poll every second
            } catch (error) {
                console.error('Error monitoring progress:', error);
                progressText.textContent = `Error: ${error.message}`;
                progressFill.style.width = '100%';
                progressFill.style.backgroundColor = 'red';
                // Re-throw so it can be caught by the calling function (handleImport)
                // This will allow the main status indicator to also show the failure.
                throw error; 
            }
        }
    }
}