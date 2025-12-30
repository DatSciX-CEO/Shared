/**
 * CyberCard Component - Styled container with neon accents
 */
import { motion } from 'framer-motion';
import type { ReactNode } from 'react';

interface CyberCardProps {
  children: ReactNode;
  title?: string;
  className?: string;
  accent?: 'cyan' | 'pink' | 'yellow';
}

export function CyberCard({ children, title, className = '', accent = 'cyan' }: CyberCardProps) {
  const accentColors = {
    cyan: 'from-[#00f5ff] to-[#ff00ff]',
    pink: 'from-[#ff0080] to-[#ff00ff]',
    yellow: 'from-[#f0ff00] to-[#ff6600]',
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className={`relative p-6 rounded-lg bg-gradient-to-br from-[#12121a] to-[#1a1a24] border border-[#2a2a3a] ${className}`}
      style={{
        boxShadow: '0 0 20px rgba(0, 0, 0, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.05)',
      }}
    >
      {/* Top accent line */}
      <div 
        className={`absolute top-0 left-0 right-0 h-[2px] bg-gradient-to-r ${accentColors[accent]}`}
      />
      
      {title && (
        <h3 
          className="text-lg font-bold uppercase tracking-wider mb-4"
          style={{ 
            fontFamily: 'Orbitron, monospace',
            color: accent === 'cyan' ? '#00f5ff' : accent === 'pink' ? '#ff0080' : '#f0ff00',
            textShadow: `0 0 10px ${accent === 'cyan' ? 'rgba(0, 245, 255, 0.5)' : accent === 'pink' ? 'rgba(255, 0, 128, 0.5)' : 'rgba(240, 255, 0, 0.5)'}`,
          }}
        >
          {title}
        </h3>
      )}
      
      {children}
    </motion.div>
  );
}

export default CyberCard;

