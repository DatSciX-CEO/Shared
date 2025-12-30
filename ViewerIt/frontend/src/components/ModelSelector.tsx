/**
 * ModelSelector - Cyberpunk-themed AI model selection component
 * Features auto-detection, search/filter, and detailed model metadata display
 */
import { useState, useEffect, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Bot, 
  RefreshCw, 
  Search, 
  Cpu, 
  HardDrive, 
  Zap,
  ChevronDown,
  Check,
  AlertTriangle,
  Wifi,
  WifiOff
} from 'lucide-react';
import { type OllamaModel, type OllamaStatus } from '../hooks/useApi';

interface ModelSelectorProps {
  models: OllamaModel[];
  status: OllamaStatus;
  selectedModel: string;
  onModelChange: (model: string) => void;
  onRefresh: () => void;
  isRefreshing?: boolean;
  disabled?: boolean;
}

export function ModelSelector({
  models,
  status,
  selectedModel,
  onModelChange,
  onRefresh,
  isRefreshing = false,
  disabled = false,
}: ModelSelectorProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  
  // Filter models based on search
  const filteredModels = useMemo(() => {
    if (!searchQuery.trim()) return models;
    const query = searchQuery.toLowerCase();
    return models.filter(model => 
      model.name.toLowerCase().includes(query) ||
      model.family.toLowerCase().includes(query) ||
      model.parameter_size.toLowerCase().includes(query)
    );
  }, [models, searchQuery]);

  // Get currently selected model details
  const selectedModelData = useMemo(() => 
    models.find(m => m.name === selectedModel),
    [models, selectedModel]
  );

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      const target = e.target as HTMLElement;
      if (!target.closest('.model-selector-container')) {
        setIsOpen(false);
      }
    };
    document.addEventListener('click', handleClickOutside);
    return () => document.removeEventListener('click', handleClickOutside);
  }, []);

  const getFamilyColor = (family: string): string => {
    const colors: Record<string, string> = {
      'llama': '#00f5ff',
      'mistral': '#ff00ff',
      'phi': '#39ff14',
      'gemma': '#ff6b35',
      'qwen': '#ffd700',
      'default': '#888899',
    };
    return colors[family.toLowerCase()] || colors.default;
  };

  const getQuantBadgeColor = (quant: string): string => {
    if (quant.includes('Q8') || quant.includes('F16') || quant.includes('F32')) {
      return 'bg-green-500/20 text-green-400 border-green-500/50';
    }
    if (quant.includes('Q5') || quant.includes('Q6')) {
      return 'bg-blue-500/20 text-blue-400 border-blue-500/50';
    }
    if (quant.includes('Q4')) {
      return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/50';
    }
    return 'bg-gray-500/20 text-gray-400 border-gray-500/50';
  };

  return (
    <div className="model-selector-container relative">
      {/* Status Header */}
      <div className="flex items-center justify-between mb-2">
        <label 
          className="flex items-center gap-2 text-xs uppercase tracking-wider text-[#888899]"
          style={{ fontFamily: 'Orbitron, monospace' }}
        >
          <Bot size={14} className="text-[#00f5ff]" />
          AI Model
        </label>
        
        <div className="flex items-center gap-2">
          {/* Online/Offline Status */}
          <motion.div 
            className={`flex items-center gap-1 text-[10px] px-2 py-0.5 rounded-full ${
              status.online 
                ? 'bg-green-500/20 text-green-400 border border-green-500/50' 
                : 'bg-red-500/20 text-red-400 border border-red-500/50'
            }`}
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
          >
            {status.online ? <Wifi size={10} /> : <WifiOff size={10} />}
            <span style={{ fontFamily: 'JetBrains Mono, monospace' }}>
              {status.online ? `${status.count} MODELS` : 'OFFLINE'}
            </span>
          </motion.div>

          {/* Refresh Button */}
          <motion.button
            onClick={(e) => {
              e.stopPropagation();
              onRefresh();
            }}
            disabled={isRefreshing || disabled}
            className={`p-1.5 rounded-lg border transition-all duration-300 ${
              isRefreshing || disabled
                ? 'border-[#2a2a3a] text-[#555566] cursor-not-allowed'
                : 'border-[#00f5ff]/30 text-[#00f5ff] hover:bg-[#00f5ff]/10 hover:border-[#00f5ff]/60'
            }`}
            whileHover={!isRefreshing && !disabled ? { scale: 1.05 } : {}}
            whileTap={!isRefreshing && !disabled ? { scale: 0.95 } : {}}
          >
            <RefreshCw 
              size={14} 
              className={isRefreshing ? 'animate-spin' : ''} 
            />
          </motion.button>
        </div>
      </div>

      {/* Main Selector Button */}
      <motion.button
        onClick={() => !disabled && setIsOpen(!isOpen)}
        disabled={disabled}
        className={`w-full px-4 py-3 rounded-lg border transition-all duration-300 text-left ${
          disabled
            ? 'bg-[#12121a]/50 border-[#2a2a3a] text-[#555566] cursor-not-allowed'
            : isOpen
              ? 'bg-[#12121a] border-[#00f5ff] shadow-[0_0_15px_rgba(0,245,255,0.3)]'
              : 'bg-[#12121a] border-[#2a2a3a] hover:border-[#00f5ff]/50'
        }`}
        whileHover={!disabled ? { scale: 1.01 } : {}}
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3 flex-1 min-w-0">
            {/* Model Icon with Family Color */}
            <div 
              className="w-8 h-8 rounded-lg flex items-center justify-center shrink-0"
              style={{ 
                backgroundColor: `${getFamilyColor(selectedModelData?.family || 'default')}15`,
                borderColor: `${getFamilyColor(selectedModelData?.family || 'default')}40`,
                borderWidth: '1px',
              }}
            >
              <Cpu 
                size={16} 
                style={{ color: getFamilyColor(selectedModelData?.family || 'default') }} 
              />
            </div>

            {/* Model Info */}
            <div className="flex-1 min-w-0">
              <div 
                className="text-sm text-[#e0e0e0] truncate"
                style={{ fontFamily: 'JetBrains Mono, monospace' }}
              >
                {selectedModel || 'Select a model...'}
              </div>
              {selectedModelData && (
                <div className="flex items-center gap-2 mt-0.5">
                  <span 
                    className="text-[10px] text-[#888899]"
                    style={{ fontFamily: 'Rajdhani, sans-serif' }}
                  >
                    {selectedModelData.family}
                  </span>
                  <span className="text-[#2a2a3a]">•</span>
                  <span 
                    className="text-[10px] text-[#888899]"
                    style={{ fontFamily: 'Rajdhani, sans-serif' }}
                  >
                    {selectedModelData.size_human}
                  </span>
                </div>
              )}
            </div>
          </div>

          {/* Dropdown Arrow */}
          <ChevronDown 
            size={18} 
            className={`text-[#888899] transition-transform duration-300 ${isOpen ? 'rotate-180' : ''}`} 
          />
        </div>
      </motion.button>

      {/* Dropdown Panel */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: -10, scaleY: 0.95 }}
            animate={{ opacity: 1, y: 0, scaleY: 1 }}
            exit={{ opacity: 0, y: -10, scaleY: 0.95 }}
            transition={{ duration: 0.2 }}
            className="absolute z-50 w-full mt-2 rounded-lg border border-[#00f5ff]/30 bg-[#0a0a0f]/95 backdrop-blur-xl shadow-[0_0_30px_rgba(0,245,255,0.2)] overflow-hidden"
            style={{ transformOrigin: 'top' }}
          >
            {/* Search Bar */}
            <div className="p-3 border-b border-[#2a2a3a]">
              <div className="relative">
                <Search 
                  size={14} 
                  className="absolute left-3 top-1/2 -translate-y-1/2 text-[#555566]" 
                />
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Search models..."
                  className="w-full pl-9 pr-4 py-2 rounded-lg bg-[#12121a] border border-[#2a2a3a] text-sm text-[#e0e0e0] placeholder-[#555566] focus:border-[#00f5ff]/50 focus:outline-none transition-colors"
                  style={{ fontFamily: 'JetBrains Mono, monospace' }}
                  onClick={(e) => e.stopPropagation()}
                />
              </div>
            </div>

            {/* Models List */}
            <div className="max-h-[280px] overflow-y-auto scrollbar-thin scrollbar-thumb-[#2a2a3a] scrollbar-track-transparent">
              {!status.online && (
                <div className="p-4 text-center">
                  <AlertTriangle size={24} className="mx-auto mb-2 text-yellow-500" />
                  <p 
                    className="text-sm text-yellow-400 mb-1"
                    style={{ fontFamily: 'Rajdhani, sans-serif' }}
                  >
                    Ollama is offline
                  </p>
                  {status.setup_hint && (
                    <p 
                      className="text-xs text-[#888899]"
                      style={{ fontFamily: 'JetBrains Mono, monospace' }}
                    >
                      {status.setup_hint}
                    </p>
                  )}
                </div>
              )}

              {filteredModels.length === 0 && status.online && (
                <div className="p-4 text-center">
                  <p 
                    className="text-sm text-[#888899]"
                    style={{ fontFamily: 'Rajdhani, sans-serif' }}
                  >
                    No models found
                  </p>
                </div>
              )}

              {filteredModels.map((model, idx) => (
                <motion.button
                  key={model.name}
                  onClick={() => {
                    onModelChange(model.name);
                    setIsOpen(false);
                    setSearchQuery('');
                  }}
                  disabled={!model.is_available}
                  className={`w-full px-4 py-3 text-left transition-all duration-200 border-b border-[#1a1a2e] last:border-b-0 ${
                    !model.is_available
                      ? 'opacity-50 cursor-not-allowed'
                      : selectedModel === model.name
                        ? 'bg-[#00f5ff]/10'
                        : 'hover:bg-[#1a1a2e]'
                  }`}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: idx * 0.03 }}
                >
                  <div className="flex items-center gap-3">
                    {/* Family Icon */}
                    <div 
                      className="w-9 h-9 rounded-lg flex items-center justify-center shrink-0"
                      style={{ 
                        backgroundColor: `${getFamilyColor(model.family)}15`,
                        borderColor: `${getFamilyColor(model.family)}40`,
                        borderWidth: '1px',
                      }}
                    >
                      <Cpu 
                        size={18} 
                        style={{ color: getFamilyColor(model.family) }} 
                      />
                    </div>

                    {/* Model Details */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <span 
                          className="text-sm text-[#e0e0e0] truncate"
                          style={{ fontFamily: 'JetBrains Mono, monospace' }}
                        >
                          {model.name}
                        </span>
                        {status.recommended === model.name && (
                          <span className="px-1.5 py-0.5 text-[9px] rounded bg-[#00f5ff]/20 text-[#00f5ff] border border-[#00f5ff]/30">
                            REC
                          </span>
                        )}
                      </div>
                      
                      <div className="flex items-center gap-3 mt-1">
                        {/* Family */}
                        <span 
                          className="text-[10px] uppercase tracking-wide"
                          style={{ 
                            fontFamily: 'Orbitron, monospace',
                            color: getFamilyColor(model.family),
                          }}
                        >
                          {model.family}
                        </span>

                        {/* Size */}
                        <span className="flex items-center gap-1 text-[10px] text-[#888899]">
                          <HardDrive size={10} />
                          {model.size_human}
                        </span>

                        {/* Parameters */}
                        {model.parameter_size !== 'Unknown' && (
                          <span className="flex items-center gap-1 text-[10px] text-[#888899]">
                            <Zap size={10} />
                            {model.parameter_size}
                          </span>
                        )}
                      </div>
                    </div>

                    {/* Selection Indicator & Quant Badge */}
                    <div className="flex items-center gap-2 shrink-0">
                      {model.quantization !== 'Default' && model.quantization !== 'Unknown' && (
                        <span 
                          className={`px-1.5 py-0.5 text-[9px] rounded border ${getQuantBadgeColor(model.quantization)}`}
                          style={{ fontFamily: 'JetBrains Mono, monospace' }}
                        >
                          {model.quantization}
                        </span>
                      )}
                      
                      {selectedModel === model.name && (
                        <motion.div
                          initial={{ scale: 0 }}
                          animate={{ scale: 1 }}
                          className="w-5 h-5 rounded-full bg-[#00f5ff]/20 flex items-center justify-center"
                        >
                          <Check size={12} className="text-[#00f5ff]" />
                        </motion.div>
                      )}
                    </div>
                  </div>
                </motion.button>
              ))}
            </div>

            {/* Footer with Model Count */}
            {status.online && (
              <div 
                className="px-4 py-2 border-t border-[#2a2a3a] text-[10px] text-[#555566] text-center"
                style={{ fontFamily: 'JetBrains Mono, monospace' }}
              >
                {filteredModels.length} of {models.length} model(s) • Pull more with{' '}
                <code className="px-1 py-0.5 bg-[#1a1a2e] rounded text-[#00f5ff]">
                  ollama pull &lt;model&gt;
                </code>
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

export default ModelSelector;

