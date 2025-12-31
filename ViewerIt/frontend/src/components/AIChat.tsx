/**
 * AIChat Component - Ollama-powered AI assistant chat interface
 * Enhanced with ModelSelector integration, status feedback, and SSE streaming
 */
import { useState, useRef, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Send, Bot, User, Sparkles, AlertCircle, Zap, Radio } from 'lucide-react';
import { ModelSelector } from './ModelSelector';
import { type OllamaModel, type OllamaStatus } from '../hooks/useApi';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  isStreaming?: boolean;
}

interface AIChatProps {
  models: OllamaModel[];
  modelStatus: OllamaStatus;
  selectedModel: string;
  onModelChange: (model: string) => void;
  onRefreshModels: () => void;
  isRefreshingModels?: boolean;
  /** Non-streaming message handler (legacy) */
  onSendMessage: (message: string) => Promise<string | null>;
  /** Streaming message handler - yields tokens as AsyncGenerator */
  onStreamMessage?: (message: string) => AsyncGenerator<{ type: string; content?: string; error?: string }>;
  isLoading?: boolean;
  disabled?: boolean;
  /** Use streaming by default when available */
  preferStreaming?: boolean;
}

export function AIChat({ 
  models,
  modelStatus,
  selectedModel, 
  onModelChange,
  onRefreshModels,
  isRefreshingModels = false,
  onSendMessage,
  onStreamMessage,
  isLoading = false,
  disabled = false,
  preferStreaming = true,
}: AIChatProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const streamingRef = useRef<boolean>(false);

  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, scrollToBottom]);

  // Handle streaming response
  const handleStreamingSend = useCallback(async (userInput: string) => {
    if (!onStreamMessage) return;
    
    setIsStreaming(true);
    streamingRef.current = true;
    
    // Add empty assistant message that we'll update
    const streamingMessage: Message = {
      role: 'assistant',
      content: '',
      timestamp: new Date(),
      isStreaming: true,
    };
    setMessages(prev => [...prev, streamingMessage]);
    
    let fullContent = '';
    
    try {
      for await (const event of onStreamMessage(userInput)) {
        if (!streamingRef.current) break;
        
        if (event.type === 'token' && event.content) {
          fullContent += event.content;
          // Update the last message with accumulated content
          setMessages(prev => {
            const updated = [...prev];
            const lastMsg = updated[updated.length - 1];
            if (lastMsg.role === 'assistant') {
              lastMsg.content = fullContent;
            }
            return updated;
          });
        } else if (event.type === 'error') {
          setMessages(prev => {
            const updated = [...prev];
            const lastMsg = updated[updated.length - 1];
            if (lastMsg.role === 'assistant') {
              lastMsg.content = fullContent + `\n\n⚠️ Error: ${event.error}`;
              lastMsg.isStreaming = false;
            }
            return updated;
          });
          break;
        } else if (event.type === 'done') {
          setMessages(prev => {
            const updated = [...prev];
            const lastMsg = updated[updated.length - 1];
            if (lastMsg.role === 'assistant') {
              lastMsg.isStreaming = false;
            }
            return updated;
          });
        }
      }
    } finally {
      setIsStreaming(false);
      streamingRef.current = false;
    }
  }, [onStreamMessage]);

  const handleSend = async () => {
    if (!input.trim() || isLoading || isStreaming || disabled) return;

    const userInput = input.trim();
    const userMessage: Message = {
      role: 'user',
      content: userInput,
      timestamp: new Date(),
    };
    
    setMessages(prev => [...prev, userMessage]);
    setInput('');

    // Use streaming if available and preferred
    if (preferStreaming && onStreamMessage) {
      await handleStreamingSend(userInput);
    } else {
      const response = await onSendMessage(userInput);
      
      if (response) {
        const assistantMessage: Message = {
          role: 'assistant',
          content: response,
          timestamp: new Date(),
        };
        setMessages(prev => [...prev, assistantMessage]);
      }
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
  const canStream = preferStreaming && !!onStreamMessage;

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
            {canStream ? <Radio size={12} /> : <Zap size={12} />}
            <span>
              AI Ready - {selectedModel.split(':')[0]}
              {canStream && <span className="text-[#00f5ff] ml-1">(streaming)</span>}
            </span>
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
                  {/* Streaming cursor */}
                  {msg.isStreaming && (
                    <motion.span
                      className="inline-block w-2 h-4 ml-0.5 bg-[#00f5ff]"
                      animate={{ opacity: [1, 0] }}
                      transition={{ duration: 0.5, repeat: Infinity }}
                    />
                  )}
                </p>
                <span 
                  className="text-[10px] text-[#555566] mt-1 block"
                  style={{ fontFamily: 'JetBrains Mono, monospace' }}
                >
                  {msg.isStreaming ? 'streaming...' : msg.timestamp.toLocaleTimeString()}
                </span>
              </div>
            </motion.div>
          ))}
        </AnimatePresence>

        {(isLoading || isStreaming) && !messages.some(m => m.isStreaming) && (
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
            disabled={!isAIReady || isLoading || isStreaming}
            placeholder={
              !modelStatus.online 
                ? 'Ollama offline...' 
                : disabled 
                  ? 'Run comparison first...' 
                  : isStreaming
                    ? 'AI is responding...'
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
            disabled={!input.trim() || isLoading || isStreaming || !isAIReady}
            className={`
              px-4 rounded-lg transition-all duration-300
              ${!input.trim() || isLoading || isStreaming || !isAIReady
                ? 'bg-[#2a2a3a] text-[#555566] cursor-not-allowed'
                : 'bg-gradient-to-r from-[#00f5ff] to-[#ff00ff] text-[#0a0a0f] hover:shadow-[0_0_20px_rgba(0,245,255,0.5)]'
              }
            `}
            whileHover={input.trim() && !isLoading && !isStreaming && isAIReady ? { scale: 1.05 } : {}}
            whileTap={input.trim() && !isLoading && !isStreaming && isAIReady ? { scale: 0.95 } : {}}
          >
            {isStreaming ? (
              <motion.div
                animate={{ rotate: 360 }}
                transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
              >
                <Radio size={20} />
              </motion.div>
            ) : (
              <Send size={20} />
            )}
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
        
        {/* Streaming indicator */}
        {isStreaming && (
          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="flex items-center justify-center gap-2 mt-2"
          >
            <motion.div
              className="w-1.5 h-1.5 rounded-full bg-[#00f5ff]"
              animate={{ scale: [1, 1.5, 1] }}
              transition={{ duration: 0.5, repeat: Infinity }}
            />
            <span 
              className="text-[10px] text-[#00f5ff]"
              style={{ fontFamily: 'JetBrains Mono, monospace' }}
            >
              Streaming response from local AI...
            </span>
          </motion.div>
        )}
      </div>
    </div>
  );
}

export default AIChat;

