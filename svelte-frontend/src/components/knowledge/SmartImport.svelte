<script>
  import { onMount } from 'svelte';
  import { knowledgeState, uiState } from '../../stores/cognitive.js';
  import { GödelOSAPI } from '../../utils/api.js';
  
  let fileInput;
  let dragActive = false;
  let uploadProgress = 0;
  let isUploading = false;
  let importResults = null;
  let selectedFormat = 'auto';
  let selectedSource = 'file';
  let urlInput = '';
  let apiKeyInput = '';
  let textInput = '';
  let textTitle = 'Manual Text Input';
  
  // Progress tracking for active imports
  let activeImports = new Map();
  let importProgress = {};
  
  // Reactive variable to track active imports count
  $: activeImportsCount = activeImports.size;
  $: activeImportsArray = [...activeImports.values()];
  
  // Import formats supported
  const supportedFormats = [
    { id: 'auto', name: 'Auto-detect', desc: 'Automatically detect file format' },
    { id: 'pdf', name: 'PDF Documents', desc: 'Extract text and structure from PDFs' },
    { id: 'txt', name: 'Plain Text', desc: 'Simple text files' },
    { id: 'md', name: 'Markdown', desc: 'Structured markdown documents' },
    { id: 'json', name: 'JSON Data', desc: 'Structured JSON knowledge bases' },
    { id: 'csv', name: 'CSV Data', desc: 'Tabular data and relationships' },
    { id: 'web', name: 'Web Content', desc: 'Scrape and analyze web pages' },
    { id: 'api', name: 'API Sources', desc: 'Connect to external knowledge APIs' }
  ];
  
  // Import sources
  const importSources = [
    { id: 'file', name: '📁 File Upload', desc: 'Upload files from your device' },
    { id: 'text', name: '📝 Text Input', desc: 'Enter text for advanced pipeline processing' },
    { id: 'url', name: '🌐 Web URL', desc: 'Import from web pages or documents' },
    { id: 'api', name: '🔗 API Connection', desc: 'Connect to external knowledge sources' },
    { id: 'bulk', name: '📦 Bulk Import', desc: 'Import multiple sources at once' }
  ];
  
  // Processing options
  let processingOptions = {
    extractEntities: true,
    generateSummaries: true,
    createRelationships: true,
    enableEmbeddings: true,
    confidenceThreshold: 0.7,
    chunkSize: 1000,
    overlapSize: 200
  };
  
  onMount(() => {
    // Initialize drag and drop
    setupDragAndDrop();
  });
  
  function setupDragAndDrop() {
    const container = document.querySelector('.import-container');
    if (!container) return;
    
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
      container.addEventListener(eventName, preventDefaults, false);
    });
    
    ['dragenter', 'dragover'].forEach(eventName => {
      container.addEventListener(eventName, handleDragEnter, false);
    });
    
    ['dragleave', 'drop'].forEach(eventName => {
      container.addEventListener(eventName, handleDragLeave, false);
    });
    
    container.addEventListener('drop', handleDrop, false);
  }
  
  function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
  }
  
  function handleDragEnter() {
    dragActive = true;
  }
  
  function handleDragLeave() {
    dragActive = false;
  }
  
  function handleDrop(e) {
    dragActive = false;
    const files = Array.from(e.dataTransfer.files);
    processFiles(files);
  }
  
  function handleFileSelect() {
    if (fileInput.files.length > 0) {
      const files = Array.from(fileInput.files);
      processFiles(files);
    }
  }
  
  async function processFiles(files) {
    isUploading = true;
    uploadProgress = 0;
    importResults = null;
    
    try {
      const results = {
        totalFiles: files.length,
        processed: 0,
        successful: 0,
        failed: 0,
        entities: 0,
        concepts: 0,
        relationships: 0,
        details: [],
        activeImports: []
      };
      
      for (let i = 0; i < files.length; i++) {
        const file = files[i];
        uploadProgress = ((i + 1) / files.length) * 50; // First 50% for uploads
        
        try {
          // Use real API to import file
          const importResponse = await GödelOSAPI.importFromFile(file);
          const importId = importResponse.import_id;
          
          // Store active import for monitoring (trigger reactivity)
          activeImports.set(importId, {
            id: importId,
            filename: file.name,
            status: 'started',
            type: 'file',
            startTime: Date.now()
          });
          activeImports = activeImports; // Force Svelte reactivity
          
          results.activeImports.push(importId);
          
          // Start progress monitoring
          monitorImportProgress(importId, results);
          
          results.processed++;
          results.successful++;
          results.details.push({
            filename: file.name,
            status: 'queued',
            size: file.size,
            type: file.type,
            import_id: importId
          });
        } catch (error) {
          results.processed++;
          results.failed++;
          results.details.push({
            filename: file.name,
            status: 'error',
            error: error.message,
            size: file.size,
            type: file.type
          });
        }
      }
      
      importResults = results;
      
      // Set upload progress to complete, but keep monitoring imports
      uploadProgress = 100;
      
    } catch (error) {
      console.error('Import error:', error);
      importResults = {
        error: error.message,
        totalFiles: files.length,
        processed: 0,
        successful: 0,
        failed: files.length
      };
    } finally {
      isUploading = false;
    }
  }

  async function monitorImportProgress(importId, results) {
    const checkProgress = async () => {
      try {
        const progress = await GödelOSAPI.getImportProgress(importId);
        
        if (progress) {
          importProgress[importId] = progress;
          
          // Update the result details with progress
          if (results && results.details) {
            const detail = results.details.find(d => d.import_id === importId);
            if (detail) {
              detail.progress = progress.progress || 0;
              detail.status = progress.status;
              detail.message = progress.message;
            }
          }
          
          // Update summary stats based on progress
          if (progress.status === 'completed') {
            results.entities += progress.details?.items_created || 0;
            results.concepts += Math.floor((progress.details?.items_created || 0) * 0.7);
            results.relationships += Math.floor((progress.details?.items_created || 0) * 0.5);
            activeImports.delete(importId);
            return;
          } else if (progress.status === 'failed') {
            activeImports.delete(importId);
            return;
          }
        }
        
        // Continue monitoring if still in progress
        if (activeImports.has(importId)) {
          setTimeout(checkProgress, 2000);
        }
      } catch (error) {
        console.error('Failed to get import progress:', error);
        activeImports.delete(importId);
      }
    };
    
    checkProgress();
  }

  
  async function importFromUrl() {
    if (!urlInput.trim()) return;
    
    isUploading = true;
    uploadProgress = 0;
    
    try {
      // Use real API to import from URL
      const importResponse = await GödelOSAPI.importFromUrl(urlInput);
      const importId = importResponse.import_id;
      
      // Store active import for monitoring
      activeImports.set(importId, {
        id: importId,
        source: urlInput,
        status: 'started',
        type: 'url',
        startTime: Date.now()
      });
      
      // Start progress monitoring
      uploadProgress = 50; // Initial progress
      
      const checkProgress = async () => {
        try {
          const progress = await GödelOSAPI.getImportProgress(importId);
          
          if (progress) {
            importProgress[importId] = progress;
            uploadProgress = progress.progress || 50;
            
            if (progress.status === 'completed') {
              importResults = {
                totalFiles: 1,
                processed: 1,
                successful: 1,
                failed: 0,
                entities: progress.details?.items_created || 15,
                concepts: Math.floor((progress.details?.items_created || 15) * 0.8),
                relationships: Math.floor((progress.details?.items_created || 15) * 0.5),
                details: [{
                  filename: urlInput,
                  status: 'success',
                  type: 'web-content',
                  import_id: importId,
                  entities: progress.details?.items_created || 15,
                  message: progress.message
                }]
              };
              activeImports.delete(importId);
              urlInput = '';
              return;
            } else if (progress.status === 'failed') {
              importResults = {
                error: progress.error_message || 'Import failed',
                totalFiles: 1,
                processed: 1,
                successful: 0,
                failed: 1
              };
              activeImports.delete(importId);
              return;
            }
          }
          
          // Continue monitoring if still in progress
          if (activeImports.has(importId)) {
            setTimeout(checkProgress, 2000);
          }
        } catch (error) {
          console.error('Failed to get import progress:', error);
          importResults = {
            error: error.message,
            totalFiles: 1,
            processed: 1,
            successful: 0,
            failed: 1
          };
          activeImports.delete(importId);
        }
      };
      
      // Start monitoring
      checkProgress();
      
    } catch (error) {
      importResults = {
        error: error.message,
        totalFiles: 1,
        processed: 1,
        successful: 0,
        failed: 1
      };
    } finally {
      isUploading = false;
    }
  }
  
  async function connectToApi() {
    if (!apiKeyInput.trim()) return;
    
    isUploading = true;
    uploadProgress = 0;
    
    try {
      // For now, simulate API connection since we don't have a specific endpoint
      // This would be replaced with actual external API integration
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      importResults = {
        totalFiles: 1,
        processed: 1,
        successful: 1,
        failed: 0,
        entities: 45,
        concepts: 32,
        relationships: 28,
        details: [{
          filename: 'API Knowledge Base',
          status: 'success',
          type: 'api-data',
          entities: 45,
          concepts: 32,
          relationships: 28,
          confidence: 0.92
        }]
      };
      
      apiKeyInput = '';
    } catch (error) {
      importResults = {
        error: error.message,
        totalFiles: 1,
        processed: 1,
        successful: 0,
        failed: 1
      };
    } finally {
      isUploading = false;
      uploadProgress = 0;
    }
  }

  async function importFromWikipedia(topic) {
    if (!topic?.trim()) return;
    
    isUploading = true;
    uploadProgress = 0;
    
    try {
      // Use real API to import from Wikipedia
      const importResponse = await GödelOSAPI.importFromWikipedia(topic);
      const importId = importResponse.import_id;
      
      // Store active import for monitoring
      activeImports.set(importId, {
        id: importId,
        source: topic,
        status: 'started',
        type: 'wikipedia',
        startTime: Date.now()
      });
      
      // Start progress monitoring
      uploadProgress = 30;
      
      const checkProgress = async () => {
        try {
          const progress = await GödelOSAPI.getImportProgress(importId);
          
          if (progress) {
            importProgress[importId] = progress;
            uploadProgress = progress.progress || 30;
            
            if (progress.status === 'completed') {
              importResults = {
                totalFiles: 1,
                processed: 1,
                successful: 1,
                failed: 0,
                entities: progress.details?.items_created || 25,
                concepts: Math.floor((progress.details?.items_created || 25) * 0.9),
                relationships: Math.floor((progress.details?.items_created || 25) * 0.6),
                details: [{
                  filename: `Wikipedia: ${topic}`,
                  status: 'success',
                  type: 'wikipedia',
                  import_id: importId,
                  entities: progress.details?.items_created || 25,
                  message: progress.message
                }]
              };
              activeImports.delete(importId);
              return;
            } else if (progress.status === 'failed') {
              importResults = {
                error: progress.error_message || 'Wikipedia import failed',
                totalFiles: 1,
                processed: 1,
                successful: 0,
                failed: 1
              };
              activeImports.delete(importId);
              return;
            }
          }
          
          // Continue monitoring if still in progress
          if (activeImports.has(importId)) {
            setTimeout(checkProgress, 2000);
          }
        } catch (error) {
          console.error('Failed to get Wikipedia import progress:', error);
          importResults = {
            error: error.message,
            totalFiles: 1,
            processed: 1,
            successful: 0,
            failed: 1
          };
          activeImports.delete(importId);
        }
      };
      
      // Start monitoring
      checkProgress();
      
    } catch (error) {
      importResults = {
        error: error.message,
        totalFiles: 1,
        processed: 1,
        successful: 0,
        failed: 1
      };
    } finally {
      isUploading = false;
    }
  }

  async function importFromText(content, title = 'Manual Text Input') {
    if (!content?.trim()) return;
    
    isUploading = true;
    uploadProgress = 0;
    
    try {
      // Use real API to import text
      const importResponse = await GödelOSAPI.importFromText(content, title);
      const importId = importResponse.import_id;
      
      // Store active import for monitoring
      activeImports.set(importId, {
        id: importId,
        source: title,
        status: 'started',
        type: 'text',
        startTime: Date.now()
      });
      
      // Start progress monitoring
      uploadProgress = 40;
      
      const checkProgress = async () => {
        try {
          const progress = await GödelOSAPI.getImportProgress(importId);
          
          if (progress) {
            importProgress[importId] = progress;
            uploadProgress = progress.progress || 40;
            
            if (progress.status === 'completed') {
              importResults = {
                totalFiles: 1,
                processed: 1,
                successful: 1,
                failed: 0,
                entities: progress.details?.items_created || 8,
                concepts: Math.floor((progress.details?.items_created || 8) * 0.75),
                relationships: Math.floor((progress.details?.items_created || 8) * 0.5),
                details: [{
                  filename: title,
                  status: 'success',
                  type: 'manual-text',
                  import_id: importId,
                  entities: progress.details?.items_created || 8,
                  message: progress.message
                }]
              };
              activeImports.delete(importId);
              return;
            } else if (progress.status === 'failed') {
              importResults = {
                error: progress.error_message || 'Text import failed',
                totalFiles: 1,
                processed: 1,
                successful: 0,
                failed: 1
              };
              activeImports.delete(importId);
              return;
            }
          }
          
          // Continue monitoring if still in progress
          if (activeImports.has(importId)) {
            setTimeout(checkProgress, 2000);
          }
        } catch (error) {
          console.error('Failed to get text import progress:', error);
          importResults = {
            error: error.message,
            totalFiles: 1,
            processed: 1,
            successful: 0,
            failed: 1
          };
          activeImports.delete(importId);
        }
      };
      
      // Start monitoring
      checkProgress();
      
    } catch (error) {
      importResults = {
        error: error.message,
        totalFiles: 1,
        processed: 1,
        successful: 0,
        failed: 1
      };
    } finally {
      isUploading = false;
    }
  }

  // Advanced Pipeline Processing Function
  async function processWithAdvancedPipeline(content, title = 'Manual Text') {
    if (!content.trim()) return;
    
    isUploading = true;
    uploadProgress = 0;
    importResults = null;
    
    try {
      uploadProgress = 25;
      
      // Check pipeline status first
      const pipelineStatus = await GödelOSAPI.getPipelineStatus();
      if (!pipelineStatus || !pipelineStatus.initialized) {
        throw new Error('Advanced knowledge pipeline is not available');
      }
      
      uploadProgress = 50;
      
      // Process through advanced pipeline
      const pipelineResult = await GödelOSAPI.processTextWithPipeline(
        content, 
        title, 
        { 
          processingOptions: processingOptions,
          source: 'manual_text',
          timestamp: Date.now()
        }
      );
      
      uploadProgress = 100;
      
      // Create results object with pipeline data
      importResults = {
        totalFiles: 1,
        processed: 1,
        successful: pipelineResult.success ? 1 : 0,
        failed: pipelineResult.success ? 0 : 1,
        entities: pipelineResult.entities_extracted || 0,
        concepts: pipelineResult.entities_extracted || 0, // Entities are concepts
        relationships: pipelineResult.relationships_extracted || 0,
        processing_time: pipelineResult.processing_time_seconds || 0,
        details: [{
          filename: title,
          status: pipelineResult.success ? 'success' : 'error',
          type: 'advanced-pipeline',
          entities: pipelineResult.entities_extracted || 0,
          relationships: pipelineResult.relationships_extracted || 0,
          knowledge_items: pipelineResult.knowledge_items || [],
          processing_time: pipelineResult.processing_time_seconds || 0,
          message: `Advanced processing completed: ${pipelineResult.entities_extracted || 0} entities, ${pipelineResult.relationships_extracted || 0} relationships`
        }],
        pipeline_result: pipelineResult
      };
      
    } catch (error) {
      console.error('Advanced pipeline processing error:', error);
      importResults = {
        error: error.message,
        totalFiles: 1,
        processed: 1,
        successful: 0,
        failed: 1,
        pipeline_error: true
      };
    } finally {
      isUploading = false;
    }
  }

  function clearResults() {
    importResults = null;
    uploadProgress = 0;
    activeImports.clear();
    importProgress = {};
  }
</script>

<div class="smart-import-container">
  <!-- Modern Header -->
  <div class="import-header">
    <div class="title-section">
      <h2 class="import-title">
        <span class="title-icon">🧠</span>
        Smart Knowledge Import
        <span class="version-badge">AI-Powered</span>
      </h2>
      <p class="subtitle">Advanced pipeline for extracting, analyzing, and integrating diverse knowledge sources</p>
    </div>
    
    <div class="stats-dashboard">
      <div class="stat-card">
        <span class="stat-value">{$knowledgeState.totalDocuments}</span>
        <span class="stat-label">Documents</span>
        <div class="stat-icon">📄</div>
      </div>
      <div class="stat-card">
        <span class="stat-value">{$knowledgeState.totalConcepts}</span>
        <span class="stat-label">Concepts</span>
        <div class="stat-icon">💡</div>
      </div>
      <div class="stat-card">
        <span class="stat-value">{activeImportsCount}</span>
        <span class="stat-label">Active</span>
        <div class="stat-icon">⚡</div>
      </div>
    </div>
  </div>

  <!-- Modern Source Selection -->
  <div class="source-selection-panel">
    <div class="panel-header">
      <h3 class="panel-title">
        <span class="panel-icon">📥</span>
        Import Source
      </h3>
      <div class="source-tabs">
        {#each importSources as source}
          <button 
            class="source-tab {selectedSource === source.id ? 'active' : ''}"
            on:click={() => selectedSource = source.id}
            title={source.desc}
          >
            <span class="tab-icon">{source.name.split(' ')[0]}</span>
            <span class="tab-name">{source.name.split(' ').slice(1).join(' ')}</span>
          </button>
        {/each}
      </div>
    </div>
  </div>

  <!-- Modern Import Interface -->
  <div class="import-interface {dragActive ? 'drag-active' : ''}">
    {#if selectedSource === 'file'}
      <div class="import-panel file-panel">
        <div class="panel-content">
          <div class="upload-zone-modern">
            <div class="upload-visual">
              <div class="upload-icon-large">📁</div>
              <div class="upload-ripple"></div>
            </div>
            <div class="upload-content">
              <h4 class="upload-title">Drag & Drop Files</h4>
              <p class="upload-description">Support for PDF, TXT, MD, JSON, CSV and more</p>
              <div class="upload-features">
                <span class="feature-tag">🔍 Auto-detect</span>
                <span class="feature-tag">🧠 AI Analysis</span>
                <span class="feature-tag">⚡ Batch Processing</span>
              </div>
            </div>
          </div>
          <input 
            type="file" 
            bind:this={fileInput}
            on:change={handleFileSelect}
            multiple
            style="display: none"
          />
          <button class="modern-upload-btn" on:click={() => fileInput.click()}>
            <span class="btn-icon">📂</span>
            <span class="btn-text">Choose Files</span>
            <span class="btn-shine"></span>
          </button>
        </div>
      </div>
    {:else if selectedSource === 'url'}
      <div class="import-panel url-panel">
        <div class="panel-content">
          <div class="input-section">
            <div class="input-header">
              <span class="input-icon">🌐</span>
              <label class="input-label">Web URL or Document Link</label>
            </div>
            <div class="modern-input-group">
              <input 
                type="url" 
                bind:value={urlInput}
                placeholder="https://example.com/document.pdf"
                class="modern-input url-input"
              />
              <button 
                class="input-action-btn" 
                on:click={importFromUrl} 
                disabled={!urlInput.trim() || isUploading}
              >
                {isUploading ? '⏳' : '🚀'}
              </button>
            </div>
            <div class="input-help">
              Supports: Web pages, PDFs, Google Docs, GitHub repos, and more
            </div>
          </div>
        </div>
      </div>
    {:else if selectedSource === 'text'}
      <div class="import-panel text-panel">
        <div class="panel-content">
          <div class="input-section">
            <div class="input-header">
              <span class="input-icon">📝</span>
              <label class="input-label">Text Content for AI Processing</label>
            </div>
            <div class="modern-input-group">
              <input 
                type="text" 
                bind:value={textTitle}
                placeholder="Enter a title for this content"
                class="modern-input title-input"
              />
            </div>
            <div class="textarea-container">
              <textarea 
                bind:value={textInput}
                placeholder="Enter or paste your content here. Our AI will extract entities, relationships, and semantic insights automatically."
                class="modern-textarea"
                rows="8"
              ></textarea>
              <div class="textarea-features">
                <div class="feature-indicator">
                  <span class="indicator-dot active"></span>
                  <span class="indicator-text">Entity Recognition</span>
                </div>
                <div class="feature-indicator">
                  <span class="indicator-dot active"></span>
                  <span class="indicator-text">Relationship Extraction</span>
                </div>
                <div class="feature-indicator">
                  <span class="indicator-dot active"></span>
                  <span class="indicator-text">Semantic Analysis</span>
                </div>
              </div>
            </div>
          <button 
            class="ai-process-btn" 
            on:click={() => processWithAdvancedPipeline(textInput, textTitle)} 
            disabled={!textInput.trim() || isUploading}
          >
            <span class="ai-btn-icon">🚀</span>
            <span class="ai-btn-text">{isUploading ? 'Processing...' : 'Process with AI'}</span>
            <div class="ai-btn-glow"></div>
          </button>
            </div>
          </div>
        </div>
    {:else if selectedSource === 'api'}
      <div class="import-panel api-panel">
        <div class="panel-content">
          <div class="input-section">
            <div class="input-header">
              <span class="input-icon">🔗</span>
              <label class="input-label">API Connection</label>
            </div>
            <div class="modern-input-group">
              <input 
                type="password" 
                bind:value={apiKeyInput}
                placeholder="Enter API key or connection string"
                class="modern-input api-input"
              />
              <button 
                class="input-action-btn" 
                on:click={connectToApi} 
                disabled={!apiKeyInput.trim()}
              >
                🔌
              </button>
            </div>
            <div class="input-help">
              Connect to external knowledge bases, APIs, and databases
            </div>
          </div>
        </div>
      </div>
    {/if}
  </div>

  <!-- Modern Format & Options Panel -->
    <div class="panel-section">
      <div class="section-header">
        <h3 class="section-title">
          <span class="section-icon">🎯</span>
          Format & Processing
        </h3>
      </div>
      
      <div class="format-selector-modern">
        <div class="format-tabs">
          {#each supportedFormats as format}
            <button 
              class="format-tab {selectedFormat === format.id ? 'active' : ''}"
              on:click={() => selectedFormat = format.id}
              title={format.desc}
            >
              <div class="format-content">
                <span class="format-name">{format.name}</span>
                <span class="format-desc">{format.desc}</span>
              </div>
              {#if selectedFormat === format.id}
                <div class="active-indicator">✓</div>
              {/if}
            </button>
          {/each}
        </div>
      </div>
    </div>
    
    <div class="panel-section">
      <div class="section-header">
        <h3 class="section-title">
          <span class="section-icon">⚙️</span>
          AI Processing Options
        </h3>
      </div>
      
      <div class="processing-controls">
        <div class="toggle-options">
          <label class="modern-option-toggle">
            <input type="checkbox" bind:checked={processingOptions.extractEntities} />
            <span class="toggle-slider"></span>
            <div class="toggle-content">
              <span class="toggle-icon">🏷️</span>
              <div class="toggle-text">
                <span class="toggle-title">Extract Entities</span>
                <span class="toggle-desc">Identify people, places, organizations</span>
              </div>
            </div>
          </label>
          
          <label class="modern-option-toggle">
            <input type="checkbox" bind:checked={processingOptions.generateSummaries} />
            <span class="toggle-slider"></span>
            <div class="toggle-content">
              <span class="toggle-icon">📋</span>
              <div class="toggle-text">
                <span class="toggle-title">Generate Summaries</span>
                <span class="toggle-desc">Create intelligent content summaries</span>
              </div>
            </div>
          </label>
          
          <label class="modern-option-toggle">
            <input type="checkbox" bind:checked={processingOptions.createRelationships} />
            <span class="toggle-slider"></span>
            <div class="toggle-content">
              <span class="toggle-icon">🔗</span>
              <div class="toggle-text">
                <span class="toggle-title">Create Relationships</span>
                <span class="toggle-desc">Build semantic connections</span>
              </div>
            </div>
          </label>
          
          <label class="modern-option-toggle">
            <input type="checkbox" bind:checked={processingOptions.enableEmbeddings} />
            <span class="toggle-slider"></span>
            <div class="toggle-content">
              <span class="toggle-icon">🧠</span>
              <div class="toggle-text">
                <span class="toggle-title">Enable Embeddings</span>
                <span class="toggle-desc">Generate vector representations</span>
              </div>
            </div>
          </label>
        </div>
        
        <div class="advanced-controls">
          <div class="control-group">
            <label class="control-slider">
              <div class="slider-header">
                <span class="slider-icon">🎯</span>
                <span class="slider-title">Confidence Threshold</span>
                <span class="slider-value">{Math.round(processingOptions.confidenceThreshold * 100)}%</span>
              </div>
              <input 
                type="range" 
                min="0.1" 
                max="1" 
                step="0.1" 
                bind:value={processingOptions.confidenceThreshold}
                class="modern-slider"
              />
              <div class="slider-track-labels">
                <span>Low</span>
                <span>High</span>
              </div>
            </label>
          </div>
          
          <div class="control-group">
            <label class="control-slider">
              <div class="slider-header">
                <span class="slider-icon">�</span>
                <span class="slider-title">Chunk Size</span>
                <span class="slider-value">{processingOptions.chunkSize}</span>
              </div>
              <input 
                type="range" 
                min="500" 
                max="2000" 
                step="100" 
                bind:value={processingOptions.chunkSize}
                class="modern-slider"
              />
              <div class="slider-track-labels">
                <span>Small</span>
                <span>Large</span>
              </div>
            </label>
          </div>
        </div>
      </div>
    </div>
  </div>

  {#if isUploading}
    <div class="upload-progress">
      <div class="textarea-container">
                <textarea 
                  bind:value={textInput}
                  placeholder="Enter or paste your content here. Our AI will extract entities, relationships, and semantic insights automatically."
                  class="modern-textarea"
                  rows="8"
                ></textarea>
                <div class="textarea-features">
                  <div class="feature-indicator">
                    <span class="indicator-dot active"></span>
                    <span class="indicator-text">Entity Recognition</span>
                  </div>
                  <div class="feature-indicator">
                    <span class="indicator-dot active"></span>
                    <span class="indicator-text">Relationship Extraction</span>
                  </div>
                  <div class="feature-indicator">
                    <span class="indicator-dot active"></span>
                    <span class="indicator-text">Semantic Analysis</span>
                  </div>
                </div>
              </div>
              <button 
                class="ai-process-btn" 
                on:click={() => processWithAdvancedPipeline(textInput, textTitle)} 
                disabled={!textInput.trim() || isUploading}
              >
                <span class="ai-btn-icon">🚀</span>
                <span class="ai-btn-text">{isUploading ? 'Processing...' : 'Process with AI'}</span>
                <div class="ai-btn-glow"></div>
              </button>
            </div>
    {/if}
  
  <div class="format-selector">
      {#each supportedFormats as format}
        <button 
          class="format-option {selectedFormat === format.id ? 'active' : ''}"
          on:click={() => selectedFormat = format.id}
        >
          <span class="format-name">{format.name}</span>
          <span class="format-desc">{format.desc}</span>
        </button>
      {/each}    </div>

  <div class="processing-options">
    <h4>⚙️ Processing Options</h4>
    <div class="options-grid">
      <label class="option-item">
        <input type="checkbox" bind:checked={processingOptions.extractEntities} />
        <span>Extract Entities</span>
      </label>
      <label class="option-item">
        <input type="checkbox" bind:checked={processingOptions.generateSummaries} />
        <span>Generate Summaries</span>
      </label>
      <label class="option-item">
        <input type="checkbox" bind:checked={processingOptions.createRelationships} />
        <span>Create Relationships</span>
      </label>
      <label class="option-item">
        <input type="checkbox" bind:checked={processingOptions.enableEmbeddings} />
        <span>Enable Embeddings</span>
      </label>
    </div>
    
    <div class="advanced-options">
      <div class="slider-option">
        <label for="confidence-threshold">Confidence Threshold: {processingOptions.confidenceThreshold}</label>
        <input 
          id="confidence-threshold"
          type="range" 
          min="0.1" 
          max="1" 
          step="0.1" 
          bind:value={processingOptions.confidenceThreshold}
        />
      </div>
      <div class="slider-option">
        <label for="chunk-size">Chunk Size: {processingOptions.chunkSize}</label>
        <input 
          id="chunk-size"
          type="range" 
          min="500" 
          max="2000" 
          step="100" 
          bind:value={processingOptions.chunkSize}
        />
      </div>
    </div>
  </div>
  
  {#if isUploading}
    <div class="upload-progress">
      <h4>🔄 Processing Knowledge...</h4>
      <div class="progress-bar">
        <div class="progress-fill" style="width: {uploadProgress}%"></div>
      </div>
      <p>Processing... {Math.round(uploadProgress)}% complete</p>
    </div>
  {/if}

  {#if activeImportsCount > 0}
    <div class="active-imports">
      <h4>⏳ Active Imports</h4>
      <div class="imports-list">
        {#each activeImportsArray as importItem}
          <div class="import-item">
            <div class="import-header">
              <span class="import-source">{importItem.source || importItem.filename}</span>
              <span class="import</div>-type">{importItem.type}</span>
          </div>
        </div>
        {#if importProgress[importItem.id]}
          <div class="import-progress">
            <div class="progress-bar small">
              <div class="progress-fill" style="width: {importProgress[importItem.id].progress || 0}%"></div>
            </div>
            <div class="progress-details">
              <span class="progress-status">{importProgress[importItem.id].status}</span>
              <span class="progress-message">{importProgress[importItem.id].message || importProgress[importItem.id].current_step}</span>
            </div>
          </div>
        {:else}
          <div class="import-progress">
            <div class="progress-bar small">
              <div class="progress-fill" style="width: 10%"></div>
            </div>
            <div class="progress-details">
              <span class="progress-status">initializing</span>
              <span class="progress-message">Starting import...</span>
            </div>
          </div>
        {/if}
      {/each}
    </div>
  </div>
{/if}

{#if importResults}
  <div class="import-results">
    <div class="results-header">
      <h4>📊 Import Results</h4>
      <button class="clear-btn" on:click={clearResults}>Clear</button>
    </div>
      
      {#if importResults.error}
        <div class="error-message">
          <span class="error-icon">❌</span>
          <span>Import failed: {importResults.error}</span>
        </div>
      {:else}
        <div class="results-summary">
          <div class="summary-card">
            <span class="summary-value">{importResults.successful}</span>
            <span class="summary-label">Successful</span>
          </div>
          <div class="summary-card">
            <span class="summary-value">{importResults.failed}</span>
            <span class="summary-label">Failed</span>
          </div>
          <div class="summary-card">
            <span class="summary-value">{importResults.entities}</span>
            <span class="summary-label">Entities</span>
          </div>
          <div class="summary-card">
            <span class="summary-value">{importResults.concepts}</span>
            <span class="summary-label">Concepts</span>
          </div>
          <div class="summary-card">
            <span class="summary-value">{importResults.relationships}</span>
            <span class="summary-label">Relationships</span>
          </div>
        </div>
        
        <div class="results-details">
          <h5>📋 File Details</h5>
          <div class="details-list">
            {#each importResults.details as detail}
              <div class="detail-item {detail.status}">
                <div class="detail-header">
                  <span class="detail-name">{detail.filename}</span>
                  <span class="detail-status {detail.status}">
                    {detail.status === 'success' ? '✅' : '❌'} {detail.status}
                  </span>
                </div>
                {#if detail.status === 'success'}
                  <div class="detail-metrics">
                    {#if detail.entities !== undefined}
                      <span>Entities: {detail.entities}</span>
                    {/if}
                    {#if detail.concepts !== undefined}
                      <span>Concepts: {detail.concepts}</span>
                    {/if}
                    {#if detail.relationships !== undefined}
                      <span>Relationships: {detail.relationships}</span>
                    {/if}
                    {#if detail.confidence !== undefined}
                      <span>Confidence: {Math.round(detail.confidence * 100)}%</span>
                    {/if}
                    {#if detail.import_id}
                      <span class="import-id">ID: {detail.import_id.substring(0, 8)}...</span>
                    {/if}
                  </div>
                {:else if detail.status === 'queued'}
                  <div class="detail-metrics">
                    <span>Import ID: {detail.import_id.substring(0, 8)}...</span>
                    <span>Status: Processing...</span>
                    {#if detail.progress !== undefined}
                      <span>Progress: {detail.progress}%</span>
                    {/if}
                  </div>
                {:else}
                  <div class="detail-error">
                    {detail.error}
                  </div>
                {/if}
              </div>
            {/each}
          </div>
        </div>
      {/if}
    </div>
  {/if}

<style>
  .smart-import-container {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 32px;
    border-radius: 20px;
    box-shadow: 0 25px 50px rgba(0, 0, 0, 0.3);
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    min-height: 800px;
    position: relative;
    overflow: hidden;
  }

  .smart-import-container::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: radial-gradient(circle at 20% 80%, rgba(120, 119, 198, 0.3) 0%, transparent 50%),
                radial-gradient(circle at 80% 20%, rgba(255, 255, 255, 0.1) 0%, transparent 50%);
    pointer-events: none;
  }

  /* Modern Header */
  .import-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 32px;
    padding-bottom: 24px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.2);
    position: relative;
    z-index: 1;
  }

  .title-section h2 {
    margin: 0;
    font-size: 32px;
    font-weight: 700;
    display: flex;
    align-items: center;
    gap: 16px;
  }

  .title-icon {
    font-size: 36px;
    animation: pulse 2s infinite;
  }

  @keyframes pulse {
    0%, 100% { transform: scale(1); }
    50% { transform: scale(1.05); }
  }

  .version-badge {
    background: linear-gradient(135deg, #4CAF50, #2E7D32);
    padding: 6px 16px;
    border-radius: 16px;
    font-size: 12px;
    font-weight: 600;
    letter-spacing: 0.5px;
    text-transform: uppercase;
  }

  .subtitle {
    margin: 12px 0 0 0;
    opacity: 0.85;
    font-size: 16px;
    line-height: 1.5;
    max-width: 600px;
  }

  .stats-dashboard {
    display: flex;
    gap: 16px;
  }

  .stat-card {
    background: rgba(255, 255, 255, 0.12);
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 16px;
    padding: 20px;
    text-align: center;
    min-width: 80px;
    position: relative;
    transition: all 0.3s ease;
    backdrop-filter: blur(10px);
  }

  .stat-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 25px rgba(0, 0, 0, 0.15);
  }

  .stat-value {
    display: block;
    font-size: 28px;
    font-weight: 700;
    line-height: 1;
    color: #FFD700;
  }

  .stat-label {
    display: block;
    font-size: 12px;
    opacity: 0.8;
    margin-top: 8px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  .stat-icon {
    position: absolute;
    top: -8px;
    right: -8px;
    background: linear-gradient(135deg, #4CAF50, #2E7D32);
    border-radius: 50%;
    width: 32px;
    height: 32px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 14px;
  }

  /* Source Selection Panel */
  .source-selection-panel {
    margin-bottom: 24px;
    position: relative;
    z-index: 1;
  }

  .panel-header {
    margin-bottom: 20px;
  }

  .panel-title {
    font-size: 20px;
    font-weight: 600;
    margin: 0 0 16px 0;
    display: flex;
    align-items: center;
    gap: 12px;
  }

  .panel-icon {
    font-size: 24px;
  }

  .source-tabs {
    display: flex;
    gap: 8px;
    background: rgba(255, 255, 255, 0.08);
    padding: 6px;
    border-radius: 16px;
    border: 1px solid rgba(255, 255, 255, 0.15);
  }

  .source-tab {
    flex: 1;
    background: transparent;
    border: none;
    color: white;
    padding: 12px 20px;
    border-radius: 12px;
    cursor: pointer;
    transition: all 0.3s ease;
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 14px;
    position: relative;
    overflow: hidden;
  }

  .source-tab::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: linear-gradient(135deg, rgba(76, 175, 80, 0.2), rgba(46, 125, 50, 0.2));
    opacity: 0;
    transition: opacity 0.3s ease;
  }

  .source-tab:hover::before {
    opacity: 1;
  }

  .source-tab.active {
    background: linear-gradient(135deg, rgba(76, 175, 80, 0.3), rgba(46, 125, 50, 0.3));
    box-shadow: 0 0 0 2px rgba(76, 175, 80, 0.5);
  }

  .source-tab.active::before {
    opacity: 1;
  }

  .tab-icon {
    font-size: 16px;
    z-index: 1;
  }

  .tab-name {
    font-weight: 500;
    z-index: 1;
  }

  /* Import Interface */
  .import-interface {
    background: rgba(255, 255, 255, 0.06);
    border: 2px dashed rgba(255, 255, 255, 0.2);
    border-radius: 20px;
    padding: 32px;
    margin-bottom: 32px;
    transition: all 0.3s ease;
    position: relative;
    z-index: 1;
  }

  .import-interface.drag-active {
    border-color: #4CAF50;
    background: rgba(76, 175, 80, 0.1);
    transform: scale(1.02);
    box-shadow: 0 0 0 4px rgba(76, 175, 80, 0.2);
  }

  .import-panel {
    min-height: 300px;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .panel-content {
    width: 100%;
    max-width: 600px;
    text-align: center;
  }

  /* File Upload Modern */
  .upload-zone-modern {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 32px;
    margin-bottom: 32px;
  }

  .upload-visual {
    position: relative;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .upload-icon-large {
    font-size: 80px;
    position: relative;
    z-index: 2;
    animation: float 3s ease-in-out infinite;
  }

  @keyframes float {
    0%, 100% { transform: translateY(0px); }
    50% { transform: translateY(-10px); }
  }

  .upload-ripple {
    position: absolute;
    width: 120px;
    height: 120px;
    border: 2px solid rgba(76, 175, 80, 0.3);
    border-radius: 50%;
    animation: ripple 2s infinite;
  }

  @keyframes ripple {
    0% { transform: scale(0.8); opacity: 1; }
    100% { transform: scale(1.2); opacity: 0; }
  }

  .upload-content h4 {
    font-size: 24px;
    font-weight: 600;
    margin: 0 0 12px 0;
  }

  .upload-description {
    font-size: 16px;
    opacity: 0.8;
    margin: 0 0 24px 0;
  }

  .upload-features {
    display: flex;
    gap: 12px;
    justify-content: center;
    flex-wrap: wrap;
  }

  .feature-tag {
    background: rgba(76, 175, 80, 0.2);
    color: #4CAF50;
    padding: 6px 12px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 500;
    border: 1px solid rgba(76, 175, 80, 0.3);
  }

  /* Modern Buttons */
  .modern-upload-btn {
    background: linear-gradient(135deg, #4CAF50, #2E7D32);
    border: none;
    border-radius: 16px;
    color: white;
    padding: 16px 32px;
    font-size: 16px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
    display: flex;
    align-items: center;
    gap: 12px;
    min-width: 180px;
    justify-content: center;
  }

  .modern-upload-btn:hover {
    transform: translateY(-3px);
    box-shadow: 0 12px 25px rgba(76, 175, 80, 0.4);
  }

  .btn-icon {
    font-size: 18px;
  }

  .btn-text {
    font-weight: 600;
  }

  .btn-shine {
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
    transition: left 0.5s ease;
  }

  .modern-upload-btn:hover .btn-shine {
    left: 100%;
  }

  /* Input Sections */
  .input-section {
    margin-bottom: 24px;
    text-align: left;
  }

  .input-header {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 12px;
  }

  .input-icon {
    font-size: 20px;
  }

  .input-label {
    font-size: 16px;
    font-weight: 600;
    margin: 0;
  }

  .modern-input-group {
    display: flex;
    gap: 12px;
    align-items: center;
  }

  .modern-input {
    flex: 1;
    background: rgba(255, 255, 255, 0.1);
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 12px;
    color: white;
    padding: 14px 18px;
    font-size: 16px;
    transition: all 0.3s ease;
  }

  .modern-input:focus {
    outline: none;
    border-color: #4CAF50;
    box-shadow: 0 0 0 3px rgba(76, 175, 80, 0.2);
    background: rgba(255, 255, 255, 0.15);
  }

  .modern-input::placeholder {
    color: rgba(255, 255, 255, 0.5);
  }

  .input-action-btn {
    background: rgba(76, 175, 80, 0.2);
    border: 1px solid rgba(76, 175, 80, 0.4);
    border-radius: 12px;
    color: #4CAF50;
    padding: 14px 18px;
    font-size: 18px;
    cursor: pointer;
    transition: all 0.3s ease;
    min-width: 60px;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .input-action-btn:hover:not(:disabled) {
    background: rgba(76, 175, 80, 0.3);
    transform: scale(1.05);
  }

  .input-action-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .input-help {
    font-size: 14px;
    opacity: 0.7;
    margin-top: 8px;
    font-style: italic;
  }

  /* Text Import Modern */
  .ai-badge {
    background: linear-gradient(135deg, #FF6B6B, #4ECDC4);
    padding: 4px 12px;
    border-radius: 12px;
    font-size: 12px;
    font-weight: 600;
    display: flex;
    align-items: center;
    gap: 6px;
    margin-left: auto;
  }

  .ai-icon {
    font-size: 14px;
  }

  .textarea-container {
    position: relative;
  }

  .modern-textarea {
    width: 100%;
    min-height: 160px;
    background: rgba(255, 255, 255, 0.1);
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 16px;
    color: white;
    padding: 18px;
    font-size: 16px;
    font-family: inherit;
    resize: vertical;
    transition: all 0.3s ease;
  }

  .modern-textarea:focus {
    outline: none;
    border-color: #4CAF50;
    box-shadow: 0 0 0 3px rgba(76, 175, 80, 0.2);
    background: rgba(255, 255, 255, 0.15);
  }

  .modern-textarea::placeholder {
    color: rgba(255, 255, 255, 0.5);
  }

  .textarea-features {
    display: flex;
    gap: 16px;
    margin-top: 12px;
    justify-content: center;
  }

  .feature-indicator {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 12px;
  }

  .indicator-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #4CAF50;
    position: relative;
  }

  .indicator-dot.active::after {
    content: '';
    position: absolute;
    top: -2px;
    left: -2px;
    right: -2px;
    bottom: -2px;
    border: 1px solid #4CAF50;
    border-radius: 50%;
    animation: pulse-ring 2s infinite;
  }

  @keyframes pulse-ring {
    0% { transform: scale(1); opacity: 1; }
    100% { transform: scale(1.5); opacity: 0; }
  }

  .ai-process-btn {
    background: linear-gradient(135deg, #FF6B6B, #4ECDC4);
    border: none;
    border-radius: 16px;
    color: white;
    padding: 18px 36px;
    font-size: 16px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
    display: flex;
    align-items: center;
    gap: 12px;
    margin: 24px auto 0;
    min-width: 200px;
    justify-content: center;
  }

  .ai-process-btn:hover:not(:disabled) {
    transform: translateY(-3px);
    box-shadow: 0 12px 25px rgba(255, 107, 107, 0.4);
  }

  .ai-process-btn:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  .ai-btn-glow {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: linear-gradient(45deg, transparent, rgba(255, 255, 255, 0.1), transparent);
    animation: glow-sweep 2s infinite;
  }

  @keyframes glow-sweep {
    0% { transform: translateX(-100%); }
    100% { transform: translateX(100%); }
  }

  /* Format Options Panel */
  .format-options-panel {
    background: rgba(255, 255, 255, 0.08);
    border-radius: 20px;
    padding: 32px;
    margin-bottom: 32px;
    border: 1px solid rgba(255, 255, 255, 0.15);
    position: relative;
    z-index: 1;
  }

  .panel-section {
    margin-bottom: 32px;
  }

  .panel-section:last-child {
    margin-bottom: 0;
  }

  .section-header {
    margin-bottom: 24px;
  }

  .section-title {
    font-size: 20px;
    font-weight: 600;
    margin: 0;
    display: flex;
    align-items: center;
    gap: 12px;
  }

  .section-icon {
    font-size: 24px;
  }

  /* Format Tabs */
  .format-selector-modern {
    margin-bottom: 24px;
  }

  .format-tabs {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 12px;
  }

  .format-tab {
    background: rgba(255, 255, 255, 0.08);
    border: 1px solid rgba(255, 255, 255, 0.15);
    border-radius: 16px;
    padding: 20px;
    cursor: pointer;
    transition: all 0.3s ease;
    text-align: left;
    position: relative;
    overflow: hidden;
    color: white;
  }

  .format-tab::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: linear-gradient(135deg, rgba(76, 175, 80, 0.1), rgba(46, 125, 50, 0.1));
    opacity: 0;
    transition: opacity 0.3s ease;
  }

  .format-tab:hover::before {
    opacity: 1;
  }

  .format-tab.active {
    background: linear-gradient(135deg, rgba(76, 175, 80, 0.2), rgba(46, 125, 50, 0.2));
    border-color: #4CAF50;
    box-shadow: 0 0 0 2px rgba(76, 175, 80, 0.3);
  }

  .format-tab.active::before {
    opacity: 1;
  }

  .format-content {
    position: relative;
    z-index: 1;
  }

  .format-name {
    display: block;
    font-size: 16px;
    font-weight: 600;
    margin-bottom: 8px;
  }

  .format-desc {
    display: block;
    font-size: 14px;
    opacity: 0.8;
    line-height: 1.4;
  }

  .active-indicator {
    position: absolute;
    top: 12px;
    right: 12px;
    background: #4CAF50;
    border-radius: 50%;
    width: 24px;
    height: 24px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 14px;
    z-index: 2;
  }

  /* Processing Controls */
  .processing-controls {
    display: grid;
    gap: 32px;
  }

  .toggle-options {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 16px;
  }

  .modern-option-toggle {
    display: flex;
    align-items: center;
    gap: 16px;
    padding: 20px;
    background: rgba(255, 255, 255, 0.06);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 16px;
    cursor: pointer;
    transition: all 0.3s ease;
  }

  .modern-option-toggle:hover {
    background: rgba(255, 255, 255, 0.1);
    border-color: rgba(255, 255, 255, 0.2);
  }

  .toggle-slider {
    position: relative;
    width: 48px;
    height: 26px;
    background: rgba(255, 255, 255, 0.2);
    border-radius: 13px;
    transition: all 0.3s ease;
    flex-shrink: 0;
  }

  .toggle-slider::before {
    content: '';
    position: absolute;
    top: 2px;
    left: 2px;
    width: 22px;
    height: 22px;
    background: white;
    border-radius: 50%;
    transition: all 0.3s ease;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
  }

  input[type="checkbox"]:checked + .toggle-slider {
    background: linear-gradient(135deg, #4CAF50, #2E7D32);
  }

  input[type="checkbox"]:checked + .toggle-slider::before {
    transform: translateX(22px);
  }

  input[type="checkbox"] {
    display: none;
  }

  .toggle-content {
    display: flex;
    align-items: center;
    gap: 16px;
    flex: 1;
  }

  .toggle-icon {
    font-size: 20px;
    min-width: 20px;
  }

  .toggle-text {
    flex: 1;
  }

  .toggle-title {
    display: block;
    font-size: 16px;
    font-weight: 600;
    line-height: 1.2;
    margin-bottom: 4px;
  }

  .toggle-desc {
    display: block;
    font-size: 14px;
    opacity: 0.7;
    line-height: 1.3;
  }

  /* Advanced Controls */
  .advanced-controls {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 24px;
  }

  .control-group {
    background: rgba(255, 255, 255, 0.06);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 16px;
    padding: 24px;
  }

  .control-slider {
    display: flex;
    flex-direction: column;
    gap: 16px;
  }

  .slider-header {
    display: flex;
    align-items: center;
    gap: 12px;
  }

  .slider-icon {
    font-size: 18px;
  }

  .slider-title {
    flex: 1;
    font-size: 16px;
    font-weight: 600;
  }

  .slider-value {
    font-size: 14px;
    font-weight: 600;
    color: #4CAF50;
    background: rgba(76, 175, 80, 0.2);
    padding: 4px 12px;
    border-radius: 12px;
  }

  .modern-slider {
    width: 100%;
    height: 8px;
    background: rgba(255, 255, 255, 0.2);
    border-radius: 4px;
    outline: none;
    appearance: none;
    cursor: pointer;
    transition: background 0.3s ease;
  }

  .modern-slider:hover {
    background: rgba(255, 255, 255, 0.25);
  }

  .modern-slider::-webkit-slider-thumb {
    appearance: none;
    width: 20px;
    height: 20px;
    background: linear-gradient(135deg, #4CAF50, #2E7D32);
    border-radius: 50%;
    cursor: pointer;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.2);
    transition: all 0.3s ease;
  }

  .modern-slider::-webkit-slider-thumb:hover {
    transform: scale(1.1);
    box-shadow: 0 4px 12px rgba(76, 175, 80, 0.4);
  }

  .slider-track-labels {
    display: flex;
    justify-content: space-between;
    font-size: 12px;
    opacity: 0.6;
    font-weight: bold;
    margin-bottom: 5px;
  }
  
  .pipeline-info small {
    color: rgba(255, 255, 255, 0.7);
    text-align: center;
    font-size: 11px;
  }
  
  .process-btn {
    width: 100%;
    background: linear-gradient(45deg, #4CAF50, #45a049);
    color: white;
    border: none;
    padding: 12px 20px;
    border-radius: 6px;
    font-size: 14px;
    font-weight: bold;
    cursor: pointer;
    transition: all 0.3s ease;
  }
  
  .process-btn:hover:not(:disabled) {
    background: linear-gradient(45deg, #45a049, #4CAF50);
    transform: translateY(-1px);
    box-shadow: 0 4px 8px rgba(76, 175, 80, 0.3);
  }
  
  .process-btn:disabled {
    opacity: 0.6;
    cursor: not-allowed;
    transform: none;
  }
  
  .advanced-btn {
    background: linear-gradient(45deg, #FF6B6B, #4ECDC4, #45B7D1);
    background-size: 200% 200%;
    animation: gradientShift 3s ease infinite;
  }

  @keyframes gradientShift {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
  }
  
  .options-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 10px;
    margin-bottom: 15px;
  }
  
  .option-item {
    display: flex;
    align-items: center;
    gap: 8px;
    cursor: pointer;
    font-size: 12px;
  }
  
  .option-item input[type="checkbox"] {
    transform: scale(1.2);
  }
  
  .advanced-options {
    background: rgba(255, 255, 255, 0.05);
    border-radius: 8px;
    padding: 15px;
    margin-top: 15px;
  }
  
  .slider-option {
    margin-bottom: 15px;
  }
  
  .slider-option label {
    display: block;
    font-size: 12px;
    margin-bottom: 5px;
    color: rgba(255, 255, 255, 0.8);
  }
  
  .slider-option input[type="range"] {
    width: 100%;
    height: 4px;
    background: rgba(255, 255, 255, 0.3);
    border-radius: 2px;
    outline: none;
  }
  
  .upload-progress {
    background: rgba(255, 255, 255, 0.1);
    border-radius: 8px;
    padding: 20px;
    margin-bottom: 20px;
    text-align: center;
  }
  
  .upload-progress h4 {
    margin: 0 0 15px 0;
    font-size: 16px;
  }
  
  .progress-bar {
    background: rgba(255, 255, 255, 0.2);
    border-radius: 10px;
    height: 8px;
    margin-bottom: 10px;
    overflow: hidden;
  }
  
  .progress-fill {
    background: linear-gradient(90deg, #4CAF50, #8BC34A);
    height: 100%;
    border-radius: 10px;
    transition: width 0.3s ease;
  }
  
  .import-results {
    background: rgba(255, 255, 255, 0.1);
    border-radius: 8px;
    padding: 20px;
    border: 1px solid rgba(255, 255, 255, 0.2);
  }
  
  .results-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 15px;
  }
  
  .results-header h4 {
    margin: 0;
    font-size: 16px;
  }
  
  .clear-btn {
    background: rgba(255, 255, 255, 0.2);
    border: 1px solid rgba(255, 255, 255, 0.3);
    border-radius: 6px;
    color: white;
    padding: 6px 12px;
    font-size: 12px;
    cursor: pointer;
  }
  
  .error-message {
    display: flex;
    align-items: center;
    gap: 10px;
    background: rgba(244, 67, 54, 0.2);
    border: 1px solid rgba(244, 67, 54, 0.5);
    border-radius: 6px;
    padding: 15px;
    color: #ffcdd2;
  }
  
  .results-summary {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(80px, 1fr));
    gap: 10px;
    margin-bottom: 20px;
  }
  
  .summary-card {
    background: rgba(255, 255, 255, 0.1);
    border-radius: 6px;
    padding: 10px;
    text-align: center;
  }
  
  .summary-value {
    display: block;
    font-size: 18px;
    font-weight: bold;
    color: #FFD700;
  }
  
  .summary-label {
    display: block;
    font-size: 10px;
    color: rgba(255, 255, 255, 0.7);
  }
  
  .results-details h5 {
    margin: 0 0 10px 0;
    font-size: 14px;
    color: rgba(255, 255, 255, 0.9);
  }
  
  .details-list {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }
  
  .detail-item {
    background: rgba(255, 255, 255, 0.05);
    border-radius: 6px;
    padding: 12px;
    border-left: 3px solid;
  }
  
  .detail-item.success {
    border-left-color: #4CAF50;
  }
  
  .detail-item.error {
    border-left-color: #F44336;
  }
  
  .detail-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;
  }
  
  .detail-name {
    font-weight: bold;
    font-size: 12px;
  }
  
  .detail-status {
    font-size: 10px;
    padding: 2px 6px;
    border-radius: 4px;
    text-transform: uppercase;
  }
  
  .detail-status.success {
    background: rgba(76, 175, 80, 0.3);
    color: #4CAF50;
  }
  
  .detail-status.error {
    background: rgba(244, 67, 54, 0.3);
    color: #F44336;
  }
  
  .detail-metrics {
    display: flex;
    gap: 15px;
    font-size: 11px;
    color: rgba(255, 255, 255, 0.7);
  }
  
  .detail-error {
    font-size: 11px;
    color: #ffcdd2;
  }

  .active-imports {
    background: rgba(255, 193, 7, 0.1);
    border: 1px solid rgba(255, 193, 7, 0.3);
    border-radius: 8px;
    padding: 20px;
    margin-bottom: 20px;
  }

  .active-imports h4 {
    margin: 0 0 15px 0;
    color: #FFC107;
    font-size: 16px;
  }

  .imports-list {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }

  .import-item {
    background: rgba(255, 255, 255, 0.05);
    border-radius: 6px;
    padding: 12px;
    border-left: 3px solid #FFC107;
  }

  .import-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;
  }

  .import-source {
    font-weight: bold;
    font-size: 12px;
    color: #FFF;
    max-width: 200px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .import-type {
    font-size: 10px;
    background: rgba(255, 193, 7, 0.3);
    color: #FFC107;
    padding: 2px 6px;
    border-radius: 4px;
    text-transform: uppercase;
  }

  .import-progress .progress-bar.small {
    height: 4px;
    margin-bottom: 6px;
  }

  .progress-details {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 10px;
  }

  .progress-status {
    color: #FFC107;
    font-weight: bold;
    text-transform: uppercase;
  }

  .progress-message {
    color: rgba(255, 255, 255, 0.7);
    font-style: italic;
    max-width: 150px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .import-id {
    color: rgba(255, 193, 7, 0.8);
    font-family: monospace;
    font-size: 10px;
  }

  .detail-item.queued {
    border-left-color: #FFC107;
  }

  .detail-status.queued {
    background: rgba(255, 193, 7, 0.3);
    color: #FFC107;
  }
</style>
