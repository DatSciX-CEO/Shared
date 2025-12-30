/**
 * Header - Cyberpunk command-center style header
 */
import { motion } from 'framer-motion';
import { Zap, Terminal, Settings, Bell, Bot } from 'lucide-react';
import { GlitchText } from '../GlitchText';

interface HeaderProps {
  sessionId: string | null;
  aiOnline?: boolean;
  aiModelCount?: number;
  onOpenTerminal?: () => void;
}

export function Header({ sessionId, aiOnline = false, aiModelCount = 0, onOpenTerminal }: HeaderProps) {
  return (
    <header className="relative z-20 border-b border-[#2a2a3a] bg-[#0d0d14]/95 backdrop-blur-md">
      {/* Animated top border */}
      <div className="absolute top-0 left-0 right-0 h-[2px] overflow-hidden">
        <motion.div
          className="h-full bg-gradient-to-r from-transparent via-[#00f5ff] to-transparent"
          animate={{ x: ['-100%', '100%'] }}
          transition={{ duration: 3, repeat: Infinity, ease: 'linear' }}
        />
      </div>

      <div className="flex items-center justify-between px-6 py-3">
        {/* Logo & Title */}
        <div className="flex items-center gap-4">
          <motion.div
            className="relative w-10 h-10"
            whileHover={{ scale: 1.05 }}
          >
            {/* Rotating border */}
            <motion.div
              className="absolute inset-0 rounded-lg bg-gradient-to-br from-[#00f5ff] to-[#ff00ff] p-[2px]"
              animate={{ rotate: 360 }}
              transition={{ duration: 20, repeat: Infinity, ease: 'linear' }}
            >
              <div className="w-full h-full rounded-lg bg-[#0a0a0f]" />
            </motion.div>
            {/* Icon */}
            <div className="absolute inset-0 flex items-center justify-center">
              <Zap size={20} className="text-[#00f5ff]" />
            </div>
          </motion.div>
          
          <div>
            <GlitchText 
              text="VIEWERIT" 
              as="h1" 
              className="text-xl font-bold text-[#00f5ff] tracking-wider" 
            />
            <p 
              className="text-xs text-[#555566] uppercase tracking-widest"
              style={{ fontFamily: 'Rajdhani, sans-serif' }}
            >
              Data Command Center
            </p>
          </div>
        </div>

        {/* Center Status */}
        <div className="flex items-center gap-6">
          {/* System Status Indicators */}
          <div className="hidden md:flex items-center gap-4">
            <div className="flex items-center gap-2 px-3 py-1 rounded border border-[#2a2a3a] bg-[#12121a]/50">
              <div className="w-2 h-2 rounded-full bg-[#39ff14] animate-pulse" />
              <span className="text-xs text-[#888899]" style={{ fontFamily: 'JetBrains Mono, monospace' }}>
                API ONLINE
              </span>
            </div>
            
            {/* AI Status Indicator */}
            <motion.div 
              className={`flex items-center gap-2 px-3 py-1 rounded border ${
                aiOnline 
                  ? 'border-[#ff00ff]/50 bg-[#ff00ff]/5' 
                  : 'border-[#2a2a3a] bg-[#12121a]/50'
              }`}
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
            >
              <Bot size={12} className={aiOnline ? 'text-[#ff00ff]' : 'text-[#555566]'} />
              <div className={`w-2 h-2 rounded-full ${aiOnline ? 'bg-[#ff00ff] animate-pulse' : 'bg-[#555566]'}`} />
              <span 
                className={`text-xs ${aiOnline ? 'text-[#ff00ff]' : 'text-[#555566]'}`} 
                style={{ fontFamily: 'JetBrains Mono, monospace' }}
              >
                {aiOnline ? `AI: ${aiModelCount} MODELS` : 'AI OFFLINE'}
              </span>
            </motion.div>
            
            {sessionId && (
              <div className="flex items-center gap-2 px-3 py-1 rounded border border-[#2a2a3a] bg-[#12121a]/50">
                <div className="w-2 h-2 rounded-full bg-[#00f5ff]" />
                <span className="text-xs text-[#888899]" style={{ fontFamily: 'JetBrains Mono, monospace' }}>
                  SESSION: {sessionId.slice(0, 8)}
                </span>
              </div>
            )}
          </div>
        </div>

        {/* Right Actions */}
        <div className="flex items-center gap-2">
          {onOpenTerminal && (
            <motion.button
              onClick={onOpenTerminal}
              className="p-2 rounded-lg border border-[#2a2a3a] bg-[#12121a]/50 text-[#888899] hover:text-[#00f5ff] hover:border-[#00f5ff]/50 transition-colors"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              title="Open Terminal"
            >
              <Terminal size={18} />
            </motion.button>
          )}
          <motion.button
            className="p-2 rounded-lg border border-[#2a2a3a] bg-[#12121a]/50 text-[#888899] hover:text-[#ff00ff] hover:border-[#ff00ff]/50 transition-colors relative"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            title="Notifications"
          >
            <Bell size={18} />
            <span className="absolute top-1 right-1 w-2 h-2 rounded-full bg-[#ff0080]" />
          </motion.button>
          <motion.button
            className="p-2 rounded-lg border border-[#2a2a3a] bg-[#12121a]/50 text-[#888899] hover:text-[#f0ff00] hover:border-[#f0ff00]/50 transition-colors"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            title="Settings"
          >
            <Settings size={18} />
          </motion.button>
        </div>
      </div>
    </header>
  );
}

export default Header;

