import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'
import { ErrorBoundary } from './components/ErrorBoundary'

/**
 * ViewerIt - Local-only eDiscovery Data Comparison Platform
 * No external analytics, telemetry, or third-party services.
 */

try {
  const rootEl = document.getElementById('root');
  
  if (!rootEl) {
    throw new Error('Root element not found');
  }

  createRoot(rootEl).render(
    <StrictMode>
      <ErrorBoundary>
        <App />
      </ErrorBoundary>
    </StrictMode>,
  );
  
} catch (err) {
  console.error('Fatal error during app initialization:', err);
  
  // Show error in the loading indicator
  const loadingEl = document.getElementById('loading-debug');
  if (loadingEl) {
    loadingEl.innerHTML = `ERROR: ${(err as Error)?.message || String(err)}`;
    loadingEl.style.background = '#f00';
    loadingEl.style.color = '#fff';
    loadingEl.style.display = 'block';
  }
}
