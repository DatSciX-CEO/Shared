/**
 * ViewerIt - Cyberpunk Data Comparator
 * Main Application Component
 */
import { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Database, 
  Zap, 
  Bot, 
  BarChart3, 
  Settings, 
  ChevronRight,
  Loader2,
  FileSpreadsheet,
  GitCompare
} from 'lucide-react';
import { 
  GlitchText, 
  CyberCard, 
  FileDropzone, 
  DataTable, 
  AIChat, 
  ComparisonStats,
  StreamlitEmbed 
} from './components';
import { useApi, type ComparisonResult, type OllamaModel, type FileInfo } from './hooks/useApi';

type Tab = 'upload' | 'compare' | 'visualize' | 'ai';

function App() {
  // State
  const [activeTab, setActiveTab] = useState<Tab>('upload');
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [uploadedFiles, setUploadedFiles] = useState<string[]>([]);
  const [fileInfos, setFileInfos] = useState<Record<string, FileInfo>>({});
  const [selectedJoinColumn, setSelectedJoinColumn] = useState<string>('');
  const [comparisonResult, setComparisonResult] = useState<ComparisonResult | null>(null);
  const [models, setModels] = useState<OllamaModel[]>([]);
  const [selectedModel, setSelectedModel] = useState('');
  const [showStreamlit, setShowStreamlit] = useState(false);

  // API Hook
  const api = useApi();

  // Load AI models on mount
  useEffect(() => {
    const loadModels = async () => {
      const fetchedModels = await api.getModels();
      setModels(fetchedModels);
      if (fetchedModels.length > 0) {
        setSelectedModel(fetchedModels[0].name);
      }
    };
    loadModels();
  }, []);

  // Handle file upload
  const handleFilesAccepted = async (files: File[]) => {
    const result = await api.uploadFiles(files);
    if (result) {
      setSessionId(result.session_id);
      setUploadedFiles(result.files);
      
      // Fetch info for each file
      const infos: Record<string, FileInfo> = {};
      for (const filename of result.files) {
        const info = await api.getFileInfo(result.session_id, filename);
        if (info) {
          infos[filename] = info;
        }
      }
      setFileInfos(infos);
      
      // Auto-select join column if there's a common column
      if (result.files.length >= 2) {
        const file1Info = infos[result.files[0]];
        const file2Info = infos[result.files[1]];
        if (file1Info && file2Info) {
          const common = file1Info.column_names.filter(c => file2Info.column_names.includes(c));
          if (common.length > 0) {
            setSelectedJoinColumn(common[0]);
          }
        }
      }
      
      setActiveTab('compare');
    }
  };

  // Handle comparison
  const handleCompare = async () => {
    if (!sessionId || uploadedFiles.length < 2 || !selectedJoinColumn) return;
    
    const result = await api.compareFiles(
      sessionId,
      uploadedFiles[0],
      uploadedFiles[1],
      [selectedJoinColumn]
    );
    
    if (result) {
      setComparisonResult(result);
    }
  };

  // Handle AI message
  const handleAIMessage = useCallback(async (message: string): Promise<string | null> => {
    if (!comparisonResult) return null;
    
    const response = await api.analyzeWithAI(selectedModel, message, comparisonResult);
    return response?.response || response?.error || null;
  }, [api, selectedModel, comparisonResult]);

  // Common columns between files
  const commonColumns = uploadedFiles.length >= 2 && fileInfos[uploadedFiles[0]] && fileInfos[uploadedFiles[1]]
    ? fileInfos[uploadedFiles[0]].column_names.filter(c => fileInfos[uploadedFiles[1]].column_names.includes(c))
    : [];

  const tabs: { id: Tab; label: string; icon: React.ReactNode }[] = [
    { id: 'upload', label: 'Upload', icon: <Database size={18} /> },
    { id: 'compare', label: 'Compare', icon: <GitCompare size={18} /> },
    { id: 'visualize', label: 'Visualize', icon: <BarChart3 size={18} /> },
    { id: 'ai', label: 'AI Analysis', icon: <Bot size={18} /> },
  ];

  return (
    <div className="min-h-screen bg-[#0a0a0f] text-[#e0e0e0]">
      {/* Background Effects */}
      <div className="fixed inset-0 pointer-events-none">
        <div className="absolute top-0 left-0 w-full h-full opacity-30">
          <div className="absolute top-0 right-0 w-1/2 h-1/2 bg-gradient-radial from-[#00f5ff]/10 to-transparent" />
          <div className="absolute bottom-0 left-0 w-1/2 h-1/2 bg-gradient-radial from-[#ff00ff]/10 to-transparent" />
        </div>
        {/* Grid pattern */}
        <div 
          className="absolute inset-0 opacity-5"
          style={{
            backgroundImage: `
              linear-gradient(rgba(0, 245, 255, 0.1) 1px, transparent 1px),
              linear-gradient(90deg, rgba(0, 245, 255, 0.1) 1px, transparent 1px)
            `,
            backgroundSize: '50px 50px',
          }}
        />
      </div>

      {/* Header */}
      <header className="relative z-10 border-b border-[#2a2a3a] bg-[#12121a]/80 backdrop-blur-sm">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <motion.div
                initial={{ rotate: 0 }}
                animate={{ rotate: 360 }}
                transition={{ duration: 20, repeat: Infinity, ease: 'linear' }}
                className="w-10 h-10 rounded-lg bg-gradient-to-br from-[#00f5ff] to-[#ff00ff] p-[2px]"
              >
                <div className="w-full h-full rounded-lg bg-[#0a0a0f] flex items-center justify-center">
                  <Zap size={20} className="text-[#00f5ff]" />
                </div>
              </motion.div>
              <GlitchText 
                text="VIEWERIT" 
                as="h1" 
                className="text-2xl font-bold text-[#00f5ff]" 
              />
            </div>
            
            {/* Session Info */}
            {sessionId && (
              <div 
                className="text-xs text-[#555566] px-3 py-1 rounded border border-[#2a2a3a]"
                style={{ fontFamily: 'JetBrains Mono, monospace' }}
              >
                Session: {sessionId.slice(0, 8)}...
              </div>
            )}
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="relative z-10 container mx-auto px-6 py-8">
        <div className="flex gap-8">
          {/* Sidebar Navigation */}
          <aside className="w-64 flex-shrink-0">
            <nav className="space-y-2">
              {tabs.map((tab) => (
                <motion.button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`
                    w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-300
                    ${activeTab === tab.id 
                      ? 'bg-gradient-to-r from-[#00f5ff]/20 to-transparent border-l-2 border-[#00f5ff] text-[#00f5ff]' 
                      : 'hover:bg-[#1a1a24] text-[#888899] hover:text-[#e0e0e0]'
                    }
                  `}
                  style={{ fontFamily: 'Rajdhani, sans-serif' }}
                  whileHover={{ x: 5 }}
                >
                  {tab.icon}
                  <span className="font-semibold uppercase tracking-wider">{tab.label}</span>
                  {activeTab === tab.id && (
                    <ChevronRight size={16} className="ml-auto" />
                  )}
                </motion.button>
              ))}
            </nav>

            {/* File Summary */}
            {uploadedFiles.length > 0 && (
              <CyberCard title="Loaded Files" className="mt-8" accent="pink">
                <div className="space-y-2">
                  {uploadedFiles.map((file, idx) => (
                    <div 
                      key={file}
                      className="flex items-center gap-2 text-sm"
                    >
                      <FileSpreadsheet size={14} className="text-[#ff0080]" />
                      <span 
                        className="truncate text-[#e0e0e0]"
                        style={{ fontFamily: 'JetBrains Mono, monospace' }}
                      >
                        {file}
                      </span>
                    </div>
                  ))}
                </div>
              </CyberCard>
            )}
          </aside>

          {/* Main Panel */}
          <div className="flex-1 min-w-0">
            <AnimatePresence mode="wait">
              {/* Upload Tab */}
              {activeTab === 'upload' && (
                <motion.div
                  key="upload"
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -20 }}
                >
                  <CyberCard title="Data Import" accent="cyan">
                    <p className="text-[#888899] mb-6" style={{ fontFamily: 'Rajdhani, sans-serif' }}>
                      Upload two or more data files to compare. Supports CSV, Excel, Parquet, and eDiscovery formats.
                    </p>
                    <FileDropzone onFilesAccepted={handleFilesAccepted} />
                    {api.loading && (
                      <div className="flex items-center gap-2 mt-4 text-[#00f5ff]">
                        <Loader2 size={16} className="animate-spin" />
                        <span style={{ fontFamily: 'Rajdhani, sans-serif' }}>Processing files...</span>
                      </div>
                    )}
                    {api.error && (
                      <p className="mt-4 text-[#ff0080]" style={{ fontFamily: 'Rajdhani, sans-serif' }}>
                        Error: {api.error}
                      </p>
                    )}
                  </CyberCard>
                </motion.div>
              )}

              {/* Compare Tab */}
              {activeTab === 'compare' && (
                <motion.div
                  key="compare"
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -20 }}
                  className="space-y-6"
                >
                  {/* Configuration */}
                  <CyberCard title="Comparison Settings" accent="cyan">
                    <div className="grid grid-cols-2 gap-6">
                      <div>
                        <label 
                          className="block text-xs uppercase tracking-wider text-[#888899] mb-2"
                          style={{ fontFamily: 'Orbitron, monospace' }}
                        >
                          Join Column (Unique Identifier)
                        </label>
                        <select
                          value={selectedJoinColumn}
                          onChange={(e) => setSelectedJoinColumn(e.target.value)}
                          className="w-full px-4 py-3 rounded-lg bg-[#12121a] border border-[#2a2a3a] text-[#e0e0e0] focus:border-[#00f5ff] focus:outline-none transition-colors"
                          style={{ fontFamily: 'JetBrains Mono, monospace' }}
                        >
                          <option value="">Select a column...</option>
                          {commonColumns.map(col => (
                            <option key={col} value={col}>{col}</option>
                          ))}
                        </select>
                      </div>
                      <div className="flex items-end">
                        <motion.button
                          onClick={handleCompare}
                          disabled={!selectedJoinColumn || api.loading}
                          className={`
                            w-full py-3 rounded-lg font-bold uppercase tracking-wider transition-all duration-300
                            ${selectedJoinColumn && !api.loading
                              ? 'bg-gradient-to-r from-[#00f5ff] to-[#ff00ff] text-[#0a0a0f] hover:shadow-[0_0_20px_rgba(0,245,255,0.5)]' 
                              : 'bg-[#2a2a3a] text-[#555566] cursor-not-allowed'
                            }
                          `}
                          style={{ fontFamily: 'Orbitron, monospace' }}
                          whileHover={selectedJoinColumn ? { scale: 1.02 } : {}}
                          whileTap={selectedJoinColumn ? { scale: 0.98 } : {}}
                        >
                          {api.loading ? (
                            <span className="flex items-center justify-center gap-2">
                              <Loader2 size={18} className="animate-spin" />
                              Analyzing...
                            </span>
                          ) : (
                            'Run Comparison'
                          )}
                        </motion.button>
                      </div>
                    </div>
                  </CyberCard>

                  {/* Results */}
                  {comparisonResult && (
                    <CyberCard title="Comparison Results" accent="pink">
                      <ComparisonStats result={comparisonResult} />
                    </CyberCard>
                  )}

                  {/* Sample Differences */}
                  {comparisonResult && comparisonResult.rows.only_in_df1_sample.length > 0 && (
                    <CyberCard title={`Rows Only in ${comparisonResult.summary.df1_name}`} accent="yellow">
                      <DataTable 
                        columns={Object.keys(comparisonResult.rows.only_in_df1_sample[0] || {})}
                        data={comparisonResult.rows.only_in_df1_sample}
                        highlightColumns={[selectedJoinColumn]}
                      />
                    </CyberCard>
                  )}
                </motion.div>
              )}

              {/* Visualize Tab */}
              {activeTab === 'visualize' && (
                <motion.div
                  key="visualize"
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -20 }}
                  className="h-[700px]"
                >
                  {sessionId && uploadedFiles.length >= 2 ? (
                    <StreamlitEmbed
                      sessionId={sessionId}
                      file1={uploadedFiles[0]}
                      file2={uploadedFiles[1]}
                    />
                  ) : (
                    <CyberCard className="h-full flex items-center justify-center">
                      <div className="text-center">
                        <BarChart3 size={64} className="text-[#555566] mx-auto mb-4" />
                        <p 
                          className="text-lg text-[#888899]"
                          style={{ fontFamily: 'Rajdhani, sans-serif' }}
                        >
                          Upload and compare files to see visualizations
                        </p>
                      </div>
                    </CyberCard>
                  )}
                </motion.div>
              )}

              {/* AI Tab */}
              {activeTab === 'ai' && (
                <motion.div
                  key="ai"
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -20 }}
                  className="h-[700px]"
                >
                  <CyberCard className="h-full p-0 overflow-hidden" accent="pink">
                    <AIChat
                      models={models}
                      selectedModel={selectedModel}
                      onModelChange={setSelectedModel}
                      onSendMessage={handleAIMessage}
                      isLoading={api.loading}
                      disabled={!comparisonResult}
                    />
                  </CyberCard>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="relative z-10 border-t border-[#2a2a3a] mt-16">
        <div className="container mx-auto px-6 py-4">
          <p 
            className="text-center text-xs text-[#555566]"
            style={{ fontFamily: 'JetBrains Mono, monospace' }}
          >
            ViewerIt v1.0.0 • eDiscovery Data Comparison Platform • Powered by Ollama AI
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;
