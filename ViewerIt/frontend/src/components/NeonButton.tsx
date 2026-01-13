/**
 * NeonButton Component - Glowing cyberpunk button with RGB split effects
 * Enhanced with advanced hover animations and professional feedback
 */
import { motion } from 'framer-motion';
import { useState, type ReactNode } from 'react';

interface NeonButtonProps {
  children: ReactNode;
  onClick?: () => void;
  variant?: 'cyan' | 'pink' | 'yellow' | 'gradient';
  size?: 'sm' | 'md' | 'lg';
  disabled?: boolean;
  className?: string;
  type?: 'button' | 'submit';
  loading?: boolean;
}

export function NeonButton({ 
  children, 
  onClick, 
  variant = 'cyan', 
  size = 'md',
  disabled = false,
  className = '',
  type = 'button',
  loading = false
}: NeonButtonProps) {
  const [isHovered, setIsHovered] = useState(false);

  const variantStyles = {
    cyan: {
      base: 'border-[#00f5ff] text-[#00f5ff]',
      glow: '0 0 10px rgba(0, 245, 255, 0.4), inset 0 0 10px rgba(0, 245, 255, 0.1)',
      hoverGlow: '0 0 20px rgba(0, 245, 255, 0.6), 0 0 40px rgba(0, 245, 255, 0.3), inset 0 0 20px rgba(0, 245, 255, 0.2)',
      textShadow: '0 0 10px rgba(0, 245, 255, 0.6)',
    },
    pink: {
      base: 'border-[#ff0080] text-[#ff0080]',
      glow: '0 0 10px rgba(255, 0, 128, 0.4), inset 0 0 10px rgba(255, 0, 128, 0.1)',
      hoverGlow: '0 0 20px rgba(255, 0, 128, 0.6), 0 0 40px rgba(255, 0, 128, 0.3), inset 0 0 20px rgba(255, 0, 128, 0.2)',
      textShadow: '0 0 10px rgba(255, 0, 128, 0.6)',
    },
    yellow: {
      base: 'border-[#f0ff00] text-[#f0ff00]',
      glow: '0 0 10px rgba(240, 255, 0, 0.4), inset 0 0 10px rgba(240, 255, 0, 0.1)',
      hoverGlow: '0 0 20px rgba(240, 255, 0, 0.6), 0 0 40px rgba(240, 255, 0, 0.3), inset 0 0 20px rgba(240, 255, 0, 0.2)',
      textShadow: '0 0 10px rgba(240, 255, 0, 0.6)',
    },
    gradient: {
      base: 'border-transparent text-[#0a0a0f] bg-gradient-to-r from-[#00f5ff] to-[#ff00ff]',
      glow: '0 0 15px rgba(0, 245, 255, 0.4)',
      hoverGlow: '0 0 25px rgba(0, 245, 255, 0.6), 0 0 50px rgba(255, 0, 255, 0.4)',
      textShadow: 'none',
    },
  };

  const sizeStyles = {
    sm: 'px-4 py-2 text-xs',
    md: 'px-6 py-3 text-sm',
    lg: 'px-8 py-4 text-base',
  };

  const style = variantStyles[variant];
  const isDisabled = disabled || loading;

  return (
    <motion.button
      type={type}
      onClick={onClick}
      disabled={isDisabled}
      onHoverStart={() => setIsHovered(true)}
      onHoverEnd={() => setIsHovered(false)}
      className={`
        relative font-bold uppercase tracking-wider transition-all duration-300
        border-2 rounded-lg overflow-hidden
        ${style.base}
        ${sizeStyles[size]}
        ${isDisabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
        ${className}
      `}
      style={{
        fontFamily: 'Orbitron, monospace',
        boxShadow: isHovered && !isDisabled ? style.hoverGlow : style.glow,
        textShadow: style.textShadow,
        background: variant === 'gradient' 
          ? 'linear-gradient(90deg, #00f5ff, #ff00ff)' 
          : isHovered && !isDisabled 
            ? `rgba(${variant === 'cyan' ? '0, 245, 255' : variant === 'pink' ? '255, 0, 128' : '240, 255, 0'}, 0.1)`
            : 'transparent',
      }}
      whileHover={isDisabled ? {} : { scale: 1.02, y: -2 }}
      whileTap={isDisabled ? {} : { scale: 0.98 }}
      animate={{
        // RGB split effect on hover
        textShadow: isHovered && !isDisabled && variant !== 'gradient'
          ? [
              style.textShadow,
              `-2px 0 #00f5ff, 2px 0 #ff0080, ${style.textShadow}`,
              `2px 0 #00f5ff, -2px 0 #ff0080, ${style.textShadow}`,
              style.textShadow,
            ]
          : style.textShadow,
      }}
      transition={{
        textShadow: { duration: 0.3, times: [0, 0.25, 0.5, 1] },
      }}
    >
      {/* Scanning line effect on hover */}
      {isHovered && !isDisabled && (
        <motion.div
          className="absolute inset-0 pointer-events-none"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
        >
          <motion.div
            className="absolute top-0 left-0 w-full h-[2px]"
            style={{
              background: 'linear-gradient(90deg, transparent, rgba(255,255,255,0.6), transparent)',
            }}
            animate={{ y: ['0%', '2000%'] }}
            transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
          />
        </motion.div>
      )}

      {/* Loading spinner */}
      {loading && (
        <motion.span
          className="absolute inset-0 flex items-center justify-center bg-inherit"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
        >
          <motion.div
            className="w-5 h-5 border-2 border-current border-t-transparent rounded-full"
            animate={{ rotate: 360 }}
            transition={{ duration: 0.8, repeat: Infinity, ease: 'linear' }}
          />
        </motion.span>
      )}

      <span className={loading ? 'opacity-0' : 'relative z-10'}>{children}</span>
    </motion.button>
  );
}

export default NeonButton;

