/**
 * AIChat Component - Ollama-powered AI assistant chat interface
 * Enhanced with ModelSelector integration and status feedback
 */
import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Send, Bot, User, Sparkles, AlertCircle, Zap } from 'lucide-react';
import { ModelSelector } from './ModelSelector';
import { type OllamaModel, type OllamaStatus } from '../hooks/useApi';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

interface AIChatProps {
  models: OllamaModel[];
  modelStatus: OllamaStatus;
  selectedModel: string;
  onModelChange: (model: string) => void;
  onRefreshModels: () => void;
  isRefreshingModels?: boolean;
  onSendMessage: (message: string) => Promise<string | null>;
  isLoading?: boolean;
  disabled?: boolean;
}

export function AIChat({ 
  models,
  modelStatus,
  selectedModel, 
  onModelChange,
  onRefreshModels,
  isRefreshingModels = false,
  onSendMessage,
  isLoading = false,
  disabled = false
}: AIChatProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || isLoading || disabled) return;

    const userMessage: Message = {
      role: 'user',
      content: input.trim(),
      timestamp: new Date(),
    };
    
    setMessages(prev => [...prev, userMessage]);
    setInput('');

    const response = await onSendMessage(input.trim());
    
    if (response) {
      const assistantMessage: Message = {
        role: 'assistant',
        content: response,
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, assistantMessage]);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  // Check if AI is ready (model selected and online)
  const isAIReady = modelStatus.online && selectedModel && !disabled;

  return (
    <div className="flex flex-col h-full">
      {/* Model Selector Header */}
      <div className="p-4 border-b border-[#2a2a3a]">
        <ModelSelector
          models={models}
          status={modelStatus}
          selectedModel={selectedModel}
          onModelChange={onModelChange}
          onRefresh={onRefreshModels}
          isRefreshing={isRefreshingModels}
          disabled={disabled}
        />
        
        {/* AI Ready Indicator */}
        {isAIReady && (
          <motion.div 
            initial={{ opacity: 0, y: -5 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-3 flex items-center gap-2 text-xs text-[#39ff14]"
            style={{ fontFamily: 'JetBrains Mono, monospace' }}
          >
            <motion.div
              animate={{ 
                boxShadow: [
                  '0 0 5px rgba(57, 255, 20, 0.5)',
                  '0 0 15px rgba(57, 255, 20, 0.8)',
                  '0 0 5px rgba(57, 255, 20, 0.5)',
                ]
              }}
              transition={{ duration: 2, repeat: Infinity }}
              className="w-2 h-2 rounded-full bg-[#39ff14]"
            />
            <Zap size={12} />
            <span>AI Ready - {selectedModel.split(':')[0]}</span>
          </motion.div>
        )}
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full text-center px-8">
            {!modelStatus.online ? (
              <>
                <AlertCircle size={40} className="text-yellow-500 mb-4" />
                <p 
                  className="text-lg text-yellow-400 mb-2"
                  style={{ fontFamily: 'Rajdhani, sans-serif' }}
                >
                  Ollama is Offline
                </p>
                <p 
                  className="text-sm text-[#888899] mb-4 max-w-md"
                  style={{ fontFamily: 'Rajdhani, sans-serif' }}
                >
                  Start Ollama to enable AI-powered analysis of your comparison results.
                </p>
                {modelStatus.setup_hint && (
                  <div className="p-3 rounded-lg bg-[#1a1a2e] border border-[#2a2a3a]">
                    <code 
                      className="text-xs text-[#00f5ff]"
                      style={{ fontFamily: 'JetBrains Mono, monospace' }}
                    >
                      {modelStatus.setup_hint}
                    </code>
                  </div>
                )}
              </>
            ) : disabled ? (
              <>
                <Sparkles size={40} className="text-[#888899] mb-4" />
                <p 
                  className="text-lg text-[#888899]"
                  style={{ fontFamily: 'Rajdhani, sans-serif' }}
                >
                  Run a comparison first to enable AI analysis
                </p>
              </>
            ) : (
              <>
                <motion.div
                  animate={{ 
                    scale: [1, 1.1, 1],
                    rotate: [0, 5, -5, 0],
                  }}
                  transition={{ duration: 3, repeat: Infinity }}
                >
                  <Sparkles size={40} className="text-[#ff00ff]" />
                </motion.div>
                <p 
                  className="text-lg text-[#888899] mt-4"
                  style={{ fontFamily: 'Rajdhani, sans-serif' }}
                >
                  Ask me about your data comparison results...
                </p>
                <p 
                  className="text-xs text-[#555566] mt-2 max-w-sm"
                  style={{ fontFamily: 'JetBrains Mono, monospace' }}
                >
                  Examples: "What are the main differences?" • "Why are these rows missing?" • "Suggest data fixes"
                </p>
              </>
            )}
          </div>
        )}

        <AnimatePresence>
          {messages.map((msg, idx) => (
            <motion.div
              key={idx}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              className={`flex gap-3 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}
            >
              <div className={`
                flex-shrink-0 w-8 h-8 rounded-lg flex items-center justify-center
                ${msg.role === 'user' 
                  ? 'bg-[#ff0080]/20 text-[#ff0080]' 
                  : 'bg-[#00f5ff]/20 text-[#00f5ff]'
                }
              `}>
                {msg.role === 'user' ? <User size={18} /> : <Bot size={18} />}
              </div>
              
              <div className={`
                flex-1 p-3 rounded-lg max-w-[85%]
                ${msg.role === 'user' 
                  ? 'bg-[#ff0080]/10 border border-[#ff0080]/30' 
                  : 'bg-[#00f5ff]/10 border border-[#00f5ff]/30'
                }
              `}>
                <p 
                  className="text-sm text-[#e0e0e0] whitespace-pre-wrap"
                  style={{ fontFamily: 'Rajdhani, sans-serif' }}
                >
                  {msg.content}
                </p>
                <span 
                  className="text-[10px] text-[#555566] mt-1 block"
                  style={{ fontFamily: 'JetBrains Mono, monospace' }}
                >
                  {msg.timestamp.toLocaleTimeString()}
                </span>
              </div>
            </motion.div>
          ))}
        </AnimatePresence>

        {isLoading && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="flex gap-3"
          >
            <div className="w-8 h-8 rounded-lg bg-[#00f5ff]/20 text-[#00f5ff] flex items-center justify-center">
              <Bot size={18} />
            </div>
            <div className="p-3 rounded-lg bg-[#00f5ff]/10 border border-[#00f5ff]/30">
              <motion.div
                className="flex gap-1"
                initial={{ opacity: 0.5 }}
                animate={{ opacity: 1 }}
                transition={{ repeat: Infinity, repeatType: 'reverse', duration: 0.5 }}
              >
                <span className="w-2 h-2 rounded-full bg-[#00f5ff]" />
                <span className="w-2 h-2 rounded-full bg-[#00f5ff]" />
                <span className="w-2 h-2 rounded-full bg-[#00f5ff]" />
              </motion.div>
            </div>
          </motion.div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="p-4 border-t border-[#2a2a3a]">
        <div className="flex gap-2">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyPress}
            disabled={!isAIReady || isLoading}
            placeholder={
              !modelStatus.online 
                ? 'Ollama offline...' 
                : disabled 
                  ? 'Run comparison first...' 
                  : 'Ask about the data...'
            }
            className={`flex-1 px-4 py-3 rounded-lg bg-[#12121a] border text-[#e0e0e0] placeholder-[#555566] focus:outline-none resize-none transition-all duration-300 disabled:opacity-50 ${
              isAIReady 
                ? 'border-[#2a2a3a] focus:border-[#00f5ff] focus:shadow-[0_0_10px_rgba(0,245,255,0.2)]' 
                : 'border-[#2a2a3a]'
            }`}
            style={{ fontFamily: 'Rajdhani, sans-serif' }}
            rows={2}
          />
          <motion.button
            onClick={handleSend}
            disabled={!input.trim() || isLoading || !isAIReady}
            className={`
              px-4 rounded-lg transition-all duration-300
              ${!input.trim() || isLoading || !isAIReady
                ? 'bg-[#2a2a3a] text-[#555566] cursor-not-allowed'
                : 'bg-gradient-to-r from-[#00f5ff] to-[#ff00ff] text-[#0a0a0f] hover:shadow-[0_0_20px_rgba(0,245,255,0.5)]'
              }
            `}
            whileHover={input.trim() && !isLoading && isAIReady ? { scale: 1.05 } : {}}
            whileTap={input.trim() && !isLoading && isAIReady ? { scale: 0.95 } : {}}
          >
            <Send size={20} />
          </motion.button>
        </div>
        
        {/* Status hint when offline */}
        {!modelStatus.online && (
          <motion.p 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="text-[10px] text-yellow-500/70 mt-2 text-center"
            style={{ fontFamily: 'JetBrains Mono, monospace' }}
          >
            Start Ollama service to enable AI chat
          </motion.p>
        )}
      </div>
    </div>
  );
}

export default AIChat;

