/**
 * CyberCard Component - Styled container with neon accents and tech-corners
 * Enhanced with animated accents and professional data-center aesthetic
 */
import { motion } from 'framer-motion';
import type { ReactNode } from 'react';

interface CyberCardProps {
  children: ReactNode;
  title?: string;
  className?: string;
  accent?: 'cyan' | 'pink' | 'yellow';
  showCorners?: boolean;
  glowIntensity?: 'low' | 'medium' | 'high';
}

export function CyberCard({ 
  children, 
  title, 
  className = '', 
  accent = 'cyan',
  showCorners = true,
  glowIntensity = 'medium'
}: CyberCardProps) {
  const accentConfig = {
    cyan: {
      gradient: 'from-[#00f5ff] to-[#ff00ff]',
      color: '#00f5ff',
      glow: 'rgba(0, 245, 255, 0.5)',
      cornerClass: 'cyber-corners',
    },
    pink: {
      gradient: 'from-[#ff0080] to-[#ff00ff]',
      color: '#ff0080',
      glow: 'rgba(255, 0, 128, 0.5)',
      cornerClass: 'cyber-corners cyber-corners-pink',
    },
    yellow: {
      gradient: 'from-[#f0ff00] to-[#ff6600]',
      color: '#f0ff00',
      glow: 'rgba(240, 255, 0, 0.5)',
      cornerClass: 'cyber-corners cyber-corners-yellow',
    },
  };

  const glowStyles = {
    low: '0 0 15px rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.03)',
    medium: '0 0 20px rgba(0, 0, 0, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.05)',
    high: '0 0 30px rgba(0, 0, 0, 0.6), inset 0 1px 0 rgba(255, 255, 255, 0.08)',
  };

  const config = accentConfig[accent];

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, ease: 'easeOut' }}
      className={`
        relative p-6 rounded-lg 
        bg-gradient-to-br from-[#12121a] to-[#1a1a24] 
        border border-[#2a2a3a] 
        ${showCorners ? config.cornerClass : ''} 
        ${className}
      `}
      style={{ boxShadow: glowStyles[glowIntensity] }}
    >
      {/* Animated top accent line */}
      <motion.div 
        className={`absolute top-0 left-0 right-0 h-[2px] rounded-t-lg bg-gradient-to-r ${config.gradient}`}
        style={{ backgroundSize: '200% 100%' }}
        animate={{ 
          backgroundPosition: ['0% 0%', '100% 0%', '0% 0%'],
          opacity: [0.8, 1, 0.8]
        }}
        transition={{ 
          duration: 4, 
          repeat: Infinity, 
          ease: 'easeInOut' 
        }}
      />
      
      {/* Secondary glow line for depth */}
      <div 
        className="absolute top-[2px] left-4 right-4 h-[1px] opacity-30"
        style={{ 
          background: `linear-gradient(90deg, transparent, ${config.color}, transparent)` 
        }}
      />
      
      {title && (
        <motion.h3 
          className="text-lg font-bold uppercase tracking-wider mb-4"
          initial={{ opacity: 0, x: -10 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.1, duration: 0.3 }}
          style={{ 
            fontFamily: 'Orbitron, monospace',
            color: config.color,
            textShadow: `0 0 10px ${config.glow}`,
          }}
        >
          {title}
        </motion.h3>
      )}
      
      {children}
    </motion.div>
  );
}

export default CyberCard;

