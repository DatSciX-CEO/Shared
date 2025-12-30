import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'
import { ErrorBoundary } from './components/ErrorBoundary'

// #region agent log - H1/H2: Check if main.tsx executes
console.log('[DEBUG H2] main.tsx starting, root element:', !!document.getElementById('root'));
// Remove the loading indicator to signal JS is running
if (typeof window !== 'undefined' && (window as any).__DEBUG_REACT_LOADED) {
  (window as any).__DEBUG_REACT_LOADED();
}
fetch('http://127.0.0.1:7242/ingest/3a8a666f-a328-4b4b-b7ff-fdfceaed8c3d',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'main.tsx:9',message:'main.tsx starting',data:{rootElement:!!document.getElementById('root')},timestamp:Date.now(),sessionId:'debug-session',hypothesisId:'H2'})}).catch(()=>{});
// #endregion

try {
  const rootEl = document.getElementById('root');
  // #region agent log - H2: Check root element exists
  console.log('[DEBUG H2] root element check:', { rootExists: !!rootEl, rootId: rootEl?.id });
  fetch('http://127.0.0.1:7242/ingest/3a8a666f-a328-4b4b-b7ff-fdfceaed8c3d',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'main.tsx:15',message:'root element check',data:{rootExists:!!rootEl,rootId:rootEl?.id},timestamp:Date.now(),sessionId:'debug-session',hypothesisId:'H2'})}).catch(()=>{});
  // #endregion

  createRoot(rootEl!).render(
    <StrictMode>
      <ErrorBoundary>
        <App />
      </ErrorBoundary>
    </StrictMode>,
  );
  
  // #region agent log - H2: Render completed without throw
  console.log('[DEBUG H2] createRoot.render called successfully');
  fetch('http://127.0.0.1:7242/ingest/3a8a666f-a328-4b4b-b7ff-fdfceaed8c3d',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'main.tsx:27',message:'createRoot.render called successfully',data:{},timestamp:Date.now(),sessionId:'debug-session',hypothesisId:'H2'})}).catch(()=>{});
  // #endregion
} catch (err) {
  // #region agent log - H2: Catch any top-level error
  console.error('[DEBUG H2] CRITICAL ERROR in main.tsx:', err);
  // Show error in the loading indicator
  const loadingEl = document.getElementById('loading-debug');
  if (loadingEl) {
    loadingEl.innerHTML = `ERROR: ${(err as Error)?.message || String(err)}`;
    loadingEl.style.background = '#f00';
    loadingEl.style.color = '#fff';
    loadingEl.style.display = 'block';
  }
  fetch('http://127.0.0.1:7242/ingest/3a8a666f-a328-4b4b-b7ff-fdfceaed8c3d',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'main.tsx:32',message:'CRITICAL ERROR in main.tsx',data:{error:String(err),stack:(err as Error)?.stack},timestamp:Date.now(),sessionId:'debug-session',hypothesisId:'H2'})}).catch(()=>{});
  // #endregion
  console.error('Fatal error during app initialization:', err);
}
