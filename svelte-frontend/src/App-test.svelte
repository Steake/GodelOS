<script>
  console.log('App.svelte script is running');
  
  // Test if basic imports work
  try {
    import { cognitiveState } from './stores/cognitive.js';
    console.log('Store import successful');
  } catch (error) {
    console.error('Store import failed:', error);
  }
  
  let testMessage = 'GödelOS Frontend Test';
</script>

<main>
  <h1>🦉 {testMessage}</h1>
  <p>If you can see this, the basic Svelte app is working.</p>
  <div class="test-section">
    <h2>Component Test</h2>
    <p>Testing if the app renders properly...</p>
  </div>
</main>

<style>
  main {
    text-align: center;
    padding: 2rem;
    font-family: Arial, sans-serif;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    min-height: 100vh;
    color: white;
  }
  
  h1 {
    font-size: 3rem;
    margin-bottom: 1rem;
  }
  
  .test-section {
    background: rgba(255, 255, 255, 0.1);
    padding: 2rem;
    border-radius: 16px;
    margin: 2rem auto;
    max-width: 600px;
  }
</style>
