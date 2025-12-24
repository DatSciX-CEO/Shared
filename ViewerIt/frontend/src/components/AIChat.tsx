/**
 * AIChat Component - Ollama-powered AI assistant chat interface
 */
import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Send, Bot, User, Sparkles, AlertCircle } from 'lucide-react';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

interface AIChatProps {
  models: Array<{ name: string; family?: string }>;
  selectedModel: string;
  onModelChange: (model: string) => void;
  onSendMessage: (message: string) => Promise<string | null>;
  isLoading?: boolean;
  disabled?: boolean;
}

export function AIChat({ 
  models, 
  selectedModel, 
  onModelChange, 
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

  return (
    <div className="flex flex-col h-full">
      {/* Model Selector */}
      <div className="p-4 border-b border-[#2a2a3a]">
        <label 
          className="block text-xs uppercase tracking-wider text-[#888899] mb-2"
          style={{ fontFamily: 'Orbitron, monospace' }}
        >
          AI Model
        </label>
        <select
          value={selectedModel}
          onChange={(e) => onModelChange(e.target.value)}
          disabled={disabled}
          className="w-full px-3 py-2 rounded-lg bg-[#12121a] border border-[#2a2a3a] text-[#e0e0e0] focus:border-[#00f5ff] focus:outline-none transition-colors"
          style={{ fontFamily: 'JetBrains Mono, monospace' }}
        >
          {models.map(model => (
            <option key={model.name} value={model.name}>
              {model.name} {model.family ? `(${model.family})` : ''}
            </option>
          ))}
        </select>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full text-center">
            <Sparkles size={40} className="text-[#ff00ff] mb-4" />
            <p 
              className="text-lg text-[#888899]"
              style={{ fontFamily: 'Rajdhani, sans-serif' }}
            >
              {disabled 
                ? 'Run a comparison first to enable AI analysis'
                : 'Ask me about your data comparison results...'
              }
            </p>
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
            disabled={disabled || isLoading}
            placeholder={disabled ? 'Run comparison first...' : 'Ask about the data...'}
            className="flex-1 px-4 py-3 rounded-lg bg-[#12121a] border border-[#2a2a3a] text-[#e0e0e0] placeholder-[#555566] focus:border-[#00f5ff] focus:outline-none resize-none transition-colors disabled:opacity-50"
            style={{ fontFamily: 'Rajdhani, sans-serif' }}
            rows={2}
          />
          <motion.button
            onClick={handleSend}
            disabled={!input.trim() || isLoading || disabled}
            className={`
              px-4 rounded-lg transition-all duration-300
              ${!input.trim() || isLoading || disabled
                ? 'bg-[#2a2a3a] text-[#555566] cursor-not-allowed'
                : 'bg-gradient-to-r from-[#00f5ff] to-[#ff00ff] text-[#0a0a0f] hover:shadow-[0_0_20px_rgba(0,245,255,0.5)]'
              }
            `}
            whileHover={input.trim() && !isLoading && !disabled ? { scale: 1.05 } : {}}
            whileTap={input.trim() && !isLoading && !disabled ? { scale: 0.95 } : {}}
          >
            <Send size={20} />
          </motion.button>
        </div>
      </div>
    </div>
  );
}

export default AIChat;

