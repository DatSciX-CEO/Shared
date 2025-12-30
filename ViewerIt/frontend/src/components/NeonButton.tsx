/**
 * NeonButton Component - Glowing cyberpunk button
 */
import { motion } from 'framer-motion';
import type { ReactNode } from 'react';

interface NeonButtonProps {
  children: ReactNode;
  onClick?: () => void;
  variant?: 'cyan' | 'pink' | 'yellow';
  disabled?: boolean;
  className?: string;
  type?: 'button' | 'submit';
}

export function NeonButton({ 
  children, 
  onClick, 
  variant = 'cyan', 
  disabled = false,
  className = '',
  type = 'button'
}: NeonButtonProps) {
  const variantClasses = {
    cyan: 'btn-neon',
    pink: 'btn-neon btn-neon-pink',
    yellow: 'border-[#f0ff00] text-[#f0ff00] shadow-[0_0_10px_rgba(240,255,0,0.4)]',
  };

  return (
    <motion.button
      type={type}
      onClick={onClick}
      disabled={disabled}
      className={`${variantClasses[variant]} ${className} ${disabled ? 'opacity-50 cursor-not-allowed' : ''}`}
      whileHover={disabled ? {} : { scale: 1.02 }}
      whileTap={disabled ? {} : { scale: 0.98 }}
    >
      {children}
    </motion.button>
  );
}

export default NeonButton;

