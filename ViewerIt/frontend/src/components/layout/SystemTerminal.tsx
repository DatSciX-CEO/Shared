/**
 * SystemTerminal - Command-center style status terminal
 */
import { motion, AnimatePresence } from 'framer-motion';
import { Terminal, X, Minus, ChevronUp, ChevronDown } from 'lucide-react';
import { useState, useEffect, useRef } from 'react';

interface LogEntry {
  id: string;
  timestamp: Date;
  level: 'info' | 'success' | 'warning' | 'error';
  message: string;
  source?: string;
}

interface SystemTerminalProps {
  isOpen: boolean;
  onClose: () => void;
  logs?: LogEntry[];
}

export function SystemTerminal({ isOpen, onClose, logs: externalLogs }: SystemTerminalProps) {
  const [isMinimized, setIsMinimized] = useState(false);
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const terminalRef = useRef<HTMLDivElement>(null);

  // Add external logs when they come in
  useEffect(() => {
    if (externalLogs) {
      setLogs(externalLogs);
    }
  }, [externalLogs]);

  // Add initial system boot messages
  useEffect(() => {
    if (isOpen && logs.length === 0) {
      const bootSequence: LogEntry[] = [
        { id: '1', timestamp: new Date(), level: 'info', message: 'ViewerIt System v2.0.0 initializing...', source: 'SYSTEM' },
        { id: '2', timestamp: new Date(), level: 'success', message: 'Backend API connected on port 8000', source: 'API' },
        { id: '3', timestamp: new Date(), level: 'success', message: 'Frontend services loaded', source: 'UI' },
        { id: '4', timestamp: new Date(), level: 'info', message: 'Ready for data comparison operations', source: 'SYSTEM' },
      ];
      
      bootSequence.forEach((log, index) => {
        setTimeout(() => {
          setLogs(prev => [...prev, log]);
        }, index * 200);
      });
    }
  }, [isOpen]);

  // Auto-scroll to bottom
  useEffect(() => {
    if (terminalRef.current && !isMinimized) {
      terminalRef.current.scrollTop = terminalRef.current.scrollHeight;
    }
  }, [logs, isMinimized]);

  const getLevelColor = (level: LogEntry['level']) => {
    switch (level) {
      case 'success': return '#39ff14';
      case 'warning': return '#f0ff00';
      case 'error': return '#ff0080';
      default: return '#00f5ff';
    }
  };

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString('en-US', { 
      hour12: false, 
      hour: '2-digit', 
      minute: '2-digit', 
      second: '2-digit' 
    });
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial={{ y: 300, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          exit={{ y: 300, opacity: 0 }}
          transition={{ type: 'spring', bounce: 0.2 }}
          className="fixed bottom-0 left-0 right-0 z-50"
        >
          <div className="border-t border-[#2a2a3a] bg-[#0a0a0f]/98 backdrop-blur-md">
            {/* Header */}
            <div className="flex items-center justify-between px-4 py-2 border-b border-[#2a2a3a]">
              <div className="flex items-center gap-2">
                <Terminal size={14} className="text-[#00f5ff]" />
                <span 
                  className="text-xs uppercase tracking-wider text-[#00f5ff]"
                  style={{ fontFamily: 'Orbitron, monospace' }}
                >
                  System Terminal
                </span>
                <span className="text-xs text-[#555566]">
                  ({logs.length} entries)
                </span>
              </div>
              <div className="flex items-center gap-1">
                <button
                  onClick={() => setIsMinimized(!isMinimized)}
                  className="p-1 rounded hover:bg-[#2a2a3a] text-[#888899] hover:text-[#f0ff00] transition-colors"
                >
                  {isMinimized ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
                </button>
                <button
                  onClick={() => setIsMinimized(true)}
                  className="p-1 rounded hover:bg-[#2a2a3a] text-[#888899] hover:text-[#f0ff00] transition-colors"
                >
                  <Minus size={14} />
                </button>
                <button
                  onClick={onClose}
                  className="p-1 rounded hover:bg-[#2a2a3a] text-[#888899] hover:text-[#ff0080] transition-colors"
                >
                  <X size={14} />
                </button>
              </div>
            </div>

            {/* Terminal Content */}
            <motion.div
              animate={{ height: isMinimized ? 0 : 180 }}
              transition={{ duration: 0.2 }}
              className="overflow-hidden"
            >
              <div 
                ref={terminalRef}
                className="h-[180px] overflow-y-auto p-4 font-mono text-xs"
                style={{ fontFamily: 'JetBrains Mono, monospace' }}
              >
                {logs.map((log, index) => (
                  <motion.div
                    key={log.id}
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.02 }}
                    className="flex gap-2 mb-1"
                  >
                    <span className="text-[#555566] flex-shrink-0">
                      [{formatTime(log.timestamp)}]
                    </span>
                    {log.source && (
                      <span 
                        className="flex-shrink-0"
                        style={{ color: getLevelColor(log.level) }}
                      >
                        [{log.source}]
                      </span>
                    )}
                    <span className="text-[#e0e0e0]">{log.message}</span>
                  </motion.div>
                ))}
                <div className="flex items-center gap-1 text-[#00f5ff] mt-2">
                  <span>&gt;</span>
                  <motion.span
                    animate={{ opacity: [1, 0] }}
                    transition={{ duration: 0.8, repeat: Infinity }}
                  >
                    _
                  </motion.span>
                </div>
              </div>
            </motion.div>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}

export default SystemTerminal;

