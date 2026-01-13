/**
 * ViewerIt - Cyberpunk Data Comparator
 * Main Application Component with Command-Center Layout
 */
import { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  BarChart3, 
  Loader2,
  Shield,
  Columns3
} from 'lucide-react';
import { 
  CyberCard, 
  FileDropzone, 
  DataTable, 
  AIChat, 
  ComparisonStats,
  AnalyticsDashboard,
  SchemaViewer,
  QualityDashboard,
  QualityCharts
} from './components';
import { Sidebar, Header, SystemTerminal, type NavTab } from './components/layout';
import { 
  useApi, 
  type ComparisonResult, 
  type MultiComparisonResult, 
  type OllamaModel,
  type OllamaStatus,
  type FileInfo,
  type SchemaAnalysisResult,
  type QualityCheckResult
} from './hooks/useApi';

function App() {


  // State
  const [activeTab, setActiveTab] = useState<NavTab>('upload');
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [uploadedFiles, setUploadedFiles] = useState<string[]>([]);
  const [fileInfos, setFileInfos] = useState<Record<string, FileInfo>>({});
  const [selectedJoinColumn, setSelectedJoinColumn] = useState<string>('');
  const [comparisonResult, setComparisonResult] = useState<ComparisonResult | null>(null);
  const [multiComparisonResult, setMultiComparisonResult] = useState<MultiComparisonResult | null>(null);
  const [selectedComparisonIndex, setSelectedComparisonIndex] = useState(0);
  
  // AI Models state
  const [models, setModels] = useState<OllamaModel[]>([]);
  const [modelStatus, setModelStatus] = useState<OllamaStatus>({
    online: false,
    count: 0,
    recommended: null,
  });
  const [selectedModel, setSelectedModel] = useState('');
  const [isRefreshingModels, setIsRefreshingModels] = useState(false);
  
  // Layout state
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [terminalOpen, setTerminalOpen] = useState(false);

  // Schema and Quality state
  const [schemaResult, setSchemaResult] = useState<SchemaAnalysisResult | null>(null);
  const [qualityResults, setQualityResults] = useState<Record<string, QualityCheckResult>>({});

  // API Hook
  const api = useApi();

  // Load AI models with priority-based auto-selection
  const loadModels = useCallback(async () => {

    setIsRefreshingModels(true);
    try {
      const response = await api.getModels();

      setModels(response.models);
      setModelStatus(response.status);
      
      // Auto-select based on priority or recommendation
      if (response.status.online && response.models.length > 0) {
        // Use server recommendation if available
        if (response.status.recommended) {
          setSelectedModel(response.status.recommended);
        } else {
          // Fallback to first available model
          const availableModel = response.models.find(m => m.is_available);
          if (availableModel) {
            setSelectedModel(availableModel.name);
          }
        }
      }
    } catch (err) {

      throw err;
    } finally {
      setIsRefreshingModels(false);
    }
  }, [api]);

  // Load models on mount
  useEffect(() => {
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
      uploadedFiles,
      [selectedJoinColumn]
    );
    
    if (result && result.comparisons.length > 0) {
      setMultiComparisonResult(result);
      setComparisonResult(result.comparisons[0]);
      setSelectedComparisonIndex(0);
    }
  };

  // Handle schema analysis
  const handleAnalyzeSchema = async () => {
    if (!sessionId || uploadedFiles.length < 2) return;
    
    const result = await api.analyzeSchema(sessionId, uploadedFiles);
    if (result) {
      setSchemaResult(result);
    }
  };

  // Handle quality check
  const handleQualityCheck = async (filename: string) => {
    if (!sessionId) return;
    
    // Use getSingleFileQuality for individual file quality checks
    const result = await api.getSingleFileQuality(sessionId, filename);
    if (result) {
      setQualityResults(prev => ({ ...prev, [filename]: result as QualityCheckResult }));
    }
  };

  // Handle AI message
  const handleAIMessage = useCallback(async (message: string): Promise<string | null> => {
    if (!comparisonResult) return null;
    
    const response = await api.analyzeWithAI(selectedModel, message, comparisonResult as unknown as Record<string, unknown>);
    return response?.response || response?.error || null;
  }, [api, selectedModel, comparisonResult]);

  // Common columns between files
  const commonColumns = uploadedFiles.length >= 2 && fileInfos[uploadedFiles[0]] && fileInfos[uploadedFiles[1]]
    ? fileInfos[uploadedFiles[0]].column_names.filter(c => fileInfos[uploadedFiles[1]].column_names.includes(c))
    : [];



  return (
    <div className="h-screen flex flex-col bg-[#0a0a0f] text-[#e0e0e0] overflow-hidden">
      {/* CRT Scanline Overlay */}
      <div className="crt-overlay" />
      
      {/* Background Effects */}
      <div className="fixed inset-0 pointer-events-none z-0">
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
        {/* Animated gradient sweep */}
        <motion.div 
          className="absolute inset-0 opacity-5"
          style={{
            background: 'linear-gradient(90deg, transparent, rgba(0, 245, 255, 0.2), transparent)',
            backgroundSize: '200% 100%',
          }}
          animate={{
            backgroundPosition: ['0% 0%', '200% 0%'],
          }}
          transition={{
            duration: 8,
            repeat: Infinity,
            ease: 'linear',
          }}
        />
      </div>

      {/* Header */}
      <Header 
        sessionId={sessionId}
        aiOnline={modelStatus.online}
        aiModelCount={modelStatus.count}
        onOpenTerminal={() => setTerminalOpen(true)}
      />

      {/* Main Layout */}
      <div className="flex-1 flex overflow-hidden relative z-10">
        {/* Sidebar Navigation */}
        <Sidebar
          activeTab={activeTab}
          onTabChange={setActiveTab}
          uploadedFiles={uploadedFiles}
          fileInfos={fileInfos}
          isCollapsed={sidebarCollapsed}
          onToggleCollapse={() => setSidebarCollapsed(!sidebarCollapsed)}
        />

        {/* Main Content Area */}
        <main className="flex-1 overflow-y-auto p-6">
          <AnimatePresence mode="wait">
            {/* Upload Tab */}
            {activeTab === 'upload' && (
              <motion.div
                key="upload"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                className="max-w-4xl mx-auto"
              >
                <CyberCard title="Data Import" accent="cyan">
                  <p className="text-[#888899] mb-6" style={{ fontFamily: 'Rajdhani, sans-serif' }}>
                    Upload two or more data files to compare. Supports CSV, Excel, Parquet, JSON, and eDiscovery formats.
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

                {/* Multiple Comparison Selector */}
                {multiComparisonResult && multiComparisonResult.comparisons.length > 1 && (
                   <CyberCard title="Select Comparison Pair" accent="yellow">
                      <div className="flex gap-2 flex-wrap">
                        {multiComparisonResult.comparisons.map((comp, idx) => (
                          <button
                             key={idx}
                             onClick={() => {
                               setComparisonResult(comp);
                               setSelectedComparisonIndex(idx);
                             }}
                             className={`px-4 py-2 rounded border transition-all duration-300 ${selectedComparisonIndex === idx ? 'bg-[#00f5ff] text-[#0a0a0f] border-[#00f5ff] font-bold' : 'bg-transparent text-[#e0e0e0] border-[#2a2a3a] hover:border-[#00f5ff]'}`}
                             style={{ fontFamily: 'JetBrains Mono, monospace' }}
                          >
                             {comp.file1} vs {comp.file2}
                          </button>
                        ))}
                      </div>
                   </CyberCard>
                )}

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
              >
                {sessionId && uploadedFiles.length >= 2 && comparisonResult ? (
                  <AnalyticsDashboard 
                    comparisonResult={comparisonResult}
                    fileInfos={fileInfos}
                    uploadedFiles={uploadedFiles}
                  />
                ) : (
                  <CyberCard className="h-[500px] flex items-center justify-center">
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

            {/* Quality Tab */}
            {activeTab === 'quality' && (
              <motion.div
                key="quality"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                className="space-y-6"
              >
                {uploadedFiles.length > 0 ? (
                  <>
                    {/* File selector for quality check */}
                    <CyberCard title="Select File for Quality Analysis" accent="cyan">
                      <div className="flex gap-2 flex-wrap">
                        {uploadedFiles.map((file) => (
                          <button
                            key={file}
                            onClick={() => handleQualityCheck(file)}
                            disabled={api.loading}
                            className={`px-4 py-2 rounded border transition-all duration-300 ${
                              qualityResults[file] 
                                ? 'bg-[#39ff14]/20 text-[#39ff14] border-[#39ff14]' 
                                : 'bg-transparent text-[#e0e0e0] border-[#2a2a3a] hover:border-[#00f5ff]'
                            }`}
                            style={{ fontFamily: 'JetBrains Mono, monospace' }}
                          >
                            {api.loading ? <Loader2 size={14} className="animate-spin inline mr-2" /> : null}
                            {file}
                          </button>
                        ))}
                      </div>
                    </CyberCard>

                    {/* Quality results */}
                    {Object.entries(qualityResults).map(([filename, result]) => (
                      <div key={filename} className="space-y-6">
                        <CyberCard title={`Quality Report: ${filename}`} accent="pink">
                          <QualityDashboard result={result} />
                        </CyberCard>
                        <QualityCharts result={result} />
                      </div>
                    ))}

                    {Object.keys(qualityResults).length === 0 && (
                      <CyberCard className="h-[400px] flex items-center justify-center">
                        <div className="text-center">
                          <Shield size={64} className="text-[#555566] mx-auto mb-4" />
                          <p className="text-lg text-[#888899]" style={{ fontFamily: 'Rajdhani, sans-serif' }}>
                            Select a file above to run quality analysis
                          </p>
                        </div>
                      </CyberCard>
                    )}
                  </>
                ) : (
                  <CyberCard className="h-[500px] flex items-center justify-center">
                    <div className="text-center">
                      <Shield size={64} className="text-[#555566] mx-auto mb-4" />
                      <p className="text-lg text-[#888899]" style={{ fontFamily: 'Rajdhani, sans-serif' }}>
                        Upload files to run quality checks
                      </p>
                    </div>
                  </CyberCard>
                )}
              </motion.div>
            )}

            {/* Schema Tab */}
            {activeTab === 'schema' && (
              <motion.div
                key="schema"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                className="space-y-6"
              >
                {uploadedFiles.length >= 2 ? (
                  <>
                    <CyberCard title="Schema Analysis" accent="cyan">
                      <div className="flex items-center gap-4">
                        <p className="text-[#888899] flex-1" style={{ fontFamily: 'Rajdhani, sans-serif' }}>
                          Analyze schema compatibility across {uploadedFiles.length} loaded files.
                        </p>
                        <motion.button
                          onClick={handleAnalyzeSchema}
                          disabled={api.loading}
                          className="px-6 py-2 rounded-lg bg-gradient-to-r from-[#00f5ff] to-[#ff00ff] text-[#0a0a0f] font-bold uppercase tracking-wider"
                          style={{ fontFamily: 'Orbitron, monospace' }}
                          whileHover={{ scale: 1.02 }}
                          whileTap={{ scale: 0.98 }}
                        >
                          {api.loading ? (
                            <span className="flex items-center gap-2">
                              <Loader2 size={16} className="animate-spin" />
                              Analyzing...
                            </span>
                          ) : (
                            'Analyze Schema'
                          )}
                        </motion.button>
                      </div>
                    </CyberCard>

                    {schemaResult && (
                      <CyberCard title="Schema Analysis Results" accent="pink">
                        <SchemaViewer result={schemaResult} />
                      </CyberCard>
                    )}

                    {!schemaResult && (
                      <CyberCard className="h-[400px] flex items-center justify-center">
                        <div className="text-center">
                          <Columns3 size={64} className="text-[#555566] mx-auto mb-4" />
                          <p className="text-lg text-[#888899]" style={{ fontFamily: 'Rajdhani, sans-serif' }}>
                            Click "Analyze Schema" to compare file structures
                          </p>
                        </div>
                      </CyberCard>
                    )}
                  </>
                ) : (
                  <CyberCard className="h-[500px] flex items-center justify-center">
                    <div className="text-center">
                      <Columns3 size={64} className="text-[#555566] mx-auto mb-4" />
                      <p className="text-lg text-[#888899]" style={{ fontFamily: 'Rajdhani, sans-serif' }}>
                        Upload at least 2 files to analyze schema
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
                className="h-[calc(100vh-200px)]"
              >
                <CyberCard className="h-full p-0 overflow-hidden" accent="pink">
                  <AIChat
                    models={models}
                    modelStatus={modelStatus}
                    selectedModel={selectedModel}
                    onModelChange={setSelectedModel}
                    onRefreshModels={loadModels}
                    isRefreshingModels={isRefreshingModels}
                    onSendMessage={handleAIMessage}
                    isLoading={api.loading}
                    disabled={!comparisonResult}
                  />
                </CyberCard>
              </motion.div>
            )}
          </AnimatePresence>
        </main>
      </div>

      {/* System Terminal */}
      <SystemTerminal 
        isOpen={terminalOpen} 
        onClose={() => setTerminalOpen(false)} 
      />

      {/* Footer Status Bar */}
      <footer className="relative z-10 border-t border-[#2a2a3a] bg-[#0d0d14] px-6 py-2">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4 text-xs text-[#555566]" style={{ fontFamily: 'JetBrains Mono, monospace' }}>
            <span>ViewerIt v2.0.0</span>
            <span>•</span>
            <span>React UI</span>
          </div>
          <div className="flex items-center gap-4 text-xs">
            <span className="text-[#555566]">Files: {uploadedFiles.length}</span>
            {comparisonResult && (
              <span className={comparisonResult.matches ? 'text-[#39ff14]' : 'text-[#ff0080]'}>
                {comparisonResult.matches ? '● MATCH' : '● DIFFERENCES'}
              </span>
            )}
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;
