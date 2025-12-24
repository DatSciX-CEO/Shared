/**
 * StreamlitEmbed Component - IFrame container for Streamlit dashboard
 */
import { motion } from 'framer-motion';
import { ExternalLink, RefreshCw, Maximize2 } from 'lucide-react';
import { useState } from 'react';

interface StreamlitEmbedProps {
  sessionId: string;
  file1: string;
  file2: string;
  port?: number;
}

export function StreamlitEmbed({ 
  sessionId, 
  file1, 
  file2, 
  port = 8501 
}: StreamlitEmbedProps) {
  const [isLoading, setIsLoading] = useState(true);
  const [key, setKey] = useState(0);
  
  const streamlitUrl = `http://localhost:${port}?session_id=${sessionId}&file1=${encodeURIComponent(file1)}&file2=${encodeURIComponent(file2)}`;

  const handleRefresh = () => {
    setIsLoading(true);
    setKey(prev => prev + 1);
  };

  const handleOpenExternal = () => {
    window.open(streamlitUrl, '_blank');
  };

  return (
    <div className="relative h-full rounded-lg overflow-hidden border border-[#2a2a3a]">
      {/* Header Bar */}
      <div className="absolute top-0 left-0 right-0 z-10 flex items-center justify-between px-4 py-2 bg-[#12121a]/90 backdrop-blur-sm border-b border-[#2a2a3a]">
        <span 
          className="text-sm uppercase tracking-wider text-[#00f5ff]"
          style={{ fontFamily: 'Orbitron, monospace' }}
        >
          Visualization Dashboard
        </span>
        <div className="flex items-center gap-2">
          <button
            onClick={handleRefresh}
            className="p-2 rounded hover:bg-[#2a2a3a] transition-colors text-[#888899] hover:text-[#00f5ff]"
            title="Refresh"
          >
            <RefreshCw size={16} />
          </button>
          <button
            onClick={handleOpenExternal}
            className="p-2 rounded hover:bg-[#2a2a3a] transition-colors text-[#888899] hover:text-[#00f5ff]"
            title="Open in new tab"
          >
            <ExternalLink size={16} />
          </button>
        </div>
      </div>

      {/* Loading Overlay */}
      {isLoading && (
        <motion.div
          initial={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="absolute inset-0 flex items-center justify-center bg-[#0a0a0f] z-20"
        >
          <div className="text-center">
            <div className="cyber-spinner mx-auto mb-4" />
            <p 
              className="text-sm text-[#888899]"
              style={{ fontFamily: 'Rajdhani, sans-serif' }}
            >
              Loading Streamlit Dashboard...
            </p>
          </div>
        </motion.div>
      )}

      {/* IFrame */}
      <iframe
        key={key}
        src={streamlitUrl}
        className="w-full h-full pt-12"
        style={{ 
          border: 'none',
          backgroundColor: '#0a0a0f',
        }}
        onLoad={() => setIsLoading(false)}
        title="Streamlit Visualization"
      />
    </div>
  );
}

export default StreamlitEmbed;

