/**
 * Header - Cyberpunk command-center style header with telemetry displays
 * Enhanced with professional status indicators and visual feedback
 */
import { motion } from 'framer-motion';
import { Zap, Terminal, Settings, Bell, Bot, Cpu, Wifi } from 'lucide-react';
import { GlitchText } from '../GlitchText';

interface HeaderProps {
  sessionId: string | null;
  aiOnline?: boolean;
  aiModelCount?: number;
  onOpenTerminal?: () => void;
}

// Telemetry Badge Component
interface TelemetryBadgeProps {
  icon: React.ReactNode;
  label: string;
  status: 'online' | 'offline' | 'active';
  value?: string | number;
}

function TelemetryBadge({ icon, label, status, value }: TelemetryBadgeProps) {
  const statusConfig = {
    online: { 
      dotColor: '#39ff14', 
      borderColor: 'rgba(57, 255, 20, 0.3)',
      textColor: '#39ff14',
      bgGlow: 'rgba(57, 255, 20, 0.05)'
    },
    offline: { 
      dotColor: '#6a6a7a', 
      borderColor: 'rgba(106, 106, 122, 0.3)',
      textColor: '#6a6a7a',
      bgGlow: 'transparent'
    },
    active: { 
      dotColor: '#ff00ff', 
      borderColor: 'rgba(255, 0, 255, 0.3)',
      textColor: '#ff00ff',
      bgGlow: 'rgba(255, 0, 255, 0.05)'
    },
  };

  const config = statusConfig[status];

  return (
    <motion.div 
      className="flex items-center gap-2 px-3 py-1.5 rounded-md"
      style={{ 
        background: config.bgGlow,
        border: `1px solid ${config.borderColor}`,
      }}
      initial={{ opacity: 0, y: -5 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ borderColor: config.dotColor, transition: { duration: 0.2 } }}
    >
      <span style={{ color: config.textColor }}>{icon}</span>
      
      {/* Status dot with glow */}
      <motion.div 
        className="w-1.5 h-1.5 rounded-full"
        style={{ 
          background: config.dotColor,
          boxShadow: status !== 'offline' ? `0 0 6px ${config.dotColor}` : 'none'
        }}
        animate={status !== 'offline' ? { 
          opacity: [1, 0.5, 1],
          scale: [1, 1.2, 1]
        } : {}}
        transition={{ duration: 1.5, repeat: Infinity }}
      />
      
      <span 
        className="text-[10px] uppercase tracking-wider"
        style={{ 
          fontFamily: 'JetBrains Mono, monospace',
          color: config.textColor,
        }}
      >
        {label}
      </span>
      
      {value !== undefined && (
        <span 
          className="text-[10px] font-bold"
          style={{ 
            fontFamily: 'Orbitron, monospace',
            color: config.textColor,
          }}
        >
          {value}
        </span>
      )}
    </motion.div>
  );
}

export function Header({ sessionId, aiOnline = false, aiModelCount = 0, onOpenTerminal }: HeaderProps) {
  return (
    <header className="relative z-20 border-b border-[#2a2a3a] bg-[#0d0d14]/95 backdrop-blur-md">
      {/* Animated top border with sweep effect */}
      <div className="absolute top-0 left-0 right-0 h-[2px] overflow-hidden">
        <motion.div
          className="h-full w-[50%] bg-gradient-to-r from-transparent via-[#00f5ff] to-transparent"
          animate={{ x: ['-100%', '200%'] }}
          transition={{ duration: 4, repeat: Infinity, ease: 'easeInOut' }}
        />
      </div>

      <div className="flex items-center justify-between px-6 py-3">
        {/* Logo & Title */}
        <div className="flex items-center gap-4">
          <motion.div
            className="relative w-10 h-10"
            whileHover={{ scale: 1.05 }}
          >
            {/* Rotating gradient border */}
            <motion.div
              className="absolute inset-0 rounded-lg p-[2px]"
              style={{
                background: 'linear-gradient(135deg, #00f5ff, #ff00ff, #00f5ff)',
                backgroundSize: '200% 200%',
              }}
              animate={{ 
                backgroundPosition: ['0% 0%', '100% 100%', '0% 0%'],
                rotate: 360 
              }}
              transition={{ 
                backgroundPosition: { duration: 3, repeat: Infinity },
                rotate: { duration: 20, repeat: Infinity, ease: 'linear' }
              }}
            >
              <div className="w-full h-full rounded-lg bg-[#0a0a0f]" />
            </motion.div>
            {/* Icon with glow */}
            <motion.div 
              className="absolute inset-0 flex items-center justify-center"
              animate={{ 
                filter: ['drop-shadow(0 0 5px rgba(0, 245, 255, 0.5))', 'drop-shadow(0 0 10px rgba(0, 245, 255, 0.8))', 'drop-shadow(0 0 5px rgba(0, 245, 255, 0.5))']
              }}
              transition={{ duration: 2, repeat: Infinity }}
            >
              <Zap size={20} className="text-[#00f5ff]" />
            </motion.div>
          </motion.div>
          
          <div>
            <GlitchText 
              text="VIEWERIT" 
              as="h1" 
              className="text-xl font-bold text-[#00f5ff] tracking-wider" 
            />
            <p 
              className="text-xs text-[#6a6a7a] uppercase tracking-widest"
              style={{ fontFamily: 'Rajdhani, sans-serif' }}
            >
              Data Command Center
            </p>
          </div>
        </div>

        {/* Center Status - Telemetry Display */}
        <div className="flex items-center gap-3">
          <div className="hidden md:flex items-center gap-3">
            {/* API Status */}
            <TelemetryBadge 
              icon={<Wifi size={12} />}
              label="API"
              status="online"
            />
            
            {/* AI Status */}
            <TelemetryBadge 
              icon={<Bot size={12} />}
              label="AI"
              status={aiOnline ? 'active' : 'offline'}
              value={aiOnline ? aiModelCount : undefined}
            />
            
            {/* Session Status */}
            {sessionId && (
              <TelemetryBadge 
                icon={<Cpu size={12} />}
                label="SESSION"
                status="online"
                value={sessionId.slice(0, 6).toUpperCase()}
              />
            )}
          </div>
        </div>

        {/* Right Actions */}
        <div className="flex items-center gap-2">
          {onOpenTerminal && (
            <motion.button
              onClick={onOpenTerminal}
              className="p-2 rounded-lg border border-[#2a2a3a] bg-[#12121a]/50 text-[#9999aa] hover:text-[#00f5ff] hover:border-[#00f5ff]/50 transition-all duration-200"
              whileHover={{ scale: 1.05, boxShadow: '0 0 10px rgba(0, 245, 255, 0.2)' }}
              whileTap={{ scale: 0.95 }}
              title="Open Terminal"
            >
              <Terminal size={18} />
            </motion.button>
          )}
          <motion.button
            className="p-2 rounded-lg border border-[#2a2a3a] bg-[#12121a]/50 text-[#9999aa] hover:text-[#ff00ff] hover:border-[#ff00ff]/50 transition-all duration-200 relative"
            whileHover={{ scale: 1.05, boxShadow: '0 0 10px rgba(255, 0, 255, 0.2)' }}
            whileTap={{ scale: 0.95 }}
            title="Notifications"
          >
            <Bell size={18} />
            <motion.span 
              className="absolute top-1 right-1 w-2 h-2 rounded-full bg-[#ff0080]"
              animate={{ scale: [1, 1.2, 1] }}
              transition={{ duration: 1.5, repeat: Infinity }}
              style={{ boxShadow: '0 0 6px rgba(255, 0, 128, 0.8)' }}
            />
          </motion.button>
          <motion.button
            className="p-2 rounded-lg border border-[#2a2a3a] bg-[#12121a]/50 text-[#9999aa] hover:text-[#f0ff00] hover:border-[#f0ff00]/50 transition-all duration-200"
            whileHover={{ scale: 1.05, boxShadow: '0 0 10px rgba(240, 255, 0, 0.2)' }}
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

