<script>
  import { onMount } from 'svelte';
  import { cognitiveState } from './stores/cognitive.js';
  
  let isLoading = true;
  let loadingStep = 'Initializing...';
  
  onMount(async () => {
    try {
      loadingStep = 'Loading stores...';
      console.log('🚀 GödelOS Frontend starting...');
      
      // Simple initialization without complex components
      setTimeout(() => {
        isLoading = false;
        console.log('✅ Basic frontend loaded');
      }, 1000);
      
    } catch (error) {
      console.error('❌ Frontend initialization failed:', error);
      loadingStep = `Error: ${error.message}`;
    }
  });
</script>

<main class="godelos-interface">
  {#if isLoading}
    <div class="loading-screen">
      <div class="loading-content">
        <div class="logo">🦉</div>
        <h1>GödelOS</h1>
        <div class="loading-spinner"></div>
        <p>{loadingStep}</p>
      </div>
    </div>
  {:else}
    <header class="interface-header">
      <div class="header-content">
        <h1 class="system-title">
          <span class="logo">🦉</span>
          <span class="title-text">GödelOS</span>
          <span class="subtitle">Cognitive Interface</span>
        </h1>
        <div class="connection-status">
          <div class="status-indicator"></div>
          <span class="status-text">Connected</span>
        </div>
      </div>
    </header>

    <div class="main-content">
      <div class="welcome-panel">
        <h2>Welcome to GödelOS</h2>
        <p>The cognitive transparency interface is now running.</p>
        <div class="status-grid">
          <div class="status-item">
            <span class="status-label">Frontend</span>
            <span class="status-value">✅ Active</span>
          </div>
          <div class="status-item">
            <span class="status-label">Backend</span>
            <span class="status-value">🔄 Connecting...</span>
          </div>
        </div>
      </div>
    </div>
  {/if}
</main>

<style>
  .godelos-interface {
    width: 100%;
    height: 100vh;
    background: linear-gradient(135deg, #0f1419 0%, #1a1f29 50%, #0f1629 100%);
    color: #e1e5e9;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    overflow: hidden;
  }

  .loading-screen {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100vh;
    background: radial-gradient(circle at center, rgba(100, 181, 246, 0.1) 0%, transparent 50%);
  }

  .loading-content {
    text-align: center;
    background: rgba(0, 0, 0, 0.3);
    padding: 3rem;
    border-radius: 20px;
    border: 1px solid rgba(100, 181, 246, 0.2);
    backdrop-filter: blur(10px);
  }

  .logo {
    font-size: 4rem;
    margin-bottom: 1rem;
    display: block;
    filter: drop-shadow(0 0 20px rgba(100, 181, 246, 0.5));
  }

  .loading-content h1 {
    font-size: 2.5rem;
    color: #64b5f6;
    margin: 0 0 2rem 0;
    font-weight: 700;
  }

  .loading-spinner {
    width: 40px;
    height: 40px;
    border: 3px solid rgba(100, 181, 246, 0.3);
    border-radius: 50%;
    border-top-color: #64b5f6;
    animation: spin 1s ease-in-out infinite;
    margin: 0 auto 1rem auto;
  }

  @keyframes spin {
    to { transform: rotate(360deg); }
  }

  .interface-header {
    padding: 1rem 2rem;
    background: rgba(0, 0, 0, 0.3);
    border-bottom: 1px solid rgba(100, 181, 246, 0.2);
    backdrop-filter: blur(10px);
  }

  .header-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .system-title {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin: 0;
    font-size: 1.5rem;
    font-weight: 600;
    color: #64b5f6;
  }

  .system-title .logo {
    font-size: 2rem;
    filter: drop-shadow(0 0 8px rgba(100, 181, 246, 0.3));
  }

  .subtitle {
    font-size: 0.9rem;
    opacity: 0.7;
    font-weight: 400;
  }

  .connection-status {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem 1rem;
    border-radius: 8px;
    background: rgba(129, 199, 132, 0.1);
    border: 1px solid rgba(129, 199, 132, 0.4);
  }

  .status-indicator {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #4CAF50;
    animation: pulse 2s infinite;
  }

  @keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
  }

  .main-content {
    padding: 2rem;
    height: calc(100vh - 80px);
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .welcome-panel {
    background: rgba(0, 0, 0, 0.3);
    border: 1px solid rgba(100, 181, 246, 0.2);
    border-radius: 16px;
    padding: 3rem;
    max-width: 600px;
    text-align: center;
    backdrop-filter: blur(10px);
  }

  .welcome-panel h2 {
    color: #64b5f6;
    font-size: 2rem;
    margin: 0 0 1rem 0;
  }

  .welcome-panel p {
    font-size: 1.1rem;
    opacity: 0.8;
    margin-bottom: 2rem;
  }

  .status-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1rem;
  }

  .status-item {
    background: rgba(100, 181, 246, 0.1);
    padding: 1rem;
    border-radius: 10px;
    border: 1px solid rgba(100, 181, 246, 0.2);
  }

  .status-label {
    display: block;
    font-size: 0.9rem;
    opacity: 0.7;
    margin-bottom: 0.5rem;
  }

  .status-value {
    display: block;
    font-weight: 600;
    color: #64b5f6;
  }
</style>
