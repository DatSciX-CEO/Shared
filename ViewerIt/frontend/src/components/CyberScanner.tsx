/**
 * CyberScanner Component - Themed loading animation for data processing
 * Professional "data scanning" visual feedback for the Command Center aesthetic
 */
import { motion } from 'framer-motion';

interface CyberScannerProps {
  message?: string;
  progress?: number;
  variant?: 'default' | 'compact' | 'inline';
}

export function CyberScanner({ 
  message = 'Scanning data...', 
  progress,
  variant = 'default' 
}: CyberScannerProps) {
  const isCompact = variant === 'compact';
  const isInline = variant === 'inline';

  if (isInline) {
    return (
      <div className="flex items-center gap-3">
        <div className="relative w-5 h-5">
          <motion.div
            className="absolute inset-0 rounded-full border-2 border-[#00f5ff]/30"
          />
          <motion.div
            className="absolute inset-0 rounded-full border-2 border-transparent border-t-[#00f5ff]"
            animate={{ rotate: 360 }}
            transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
          />
        </div>
        <span 
          className="text-sm text-[#00f5ff]"
          style={{ fontFamily: 'Rajdhani, sans-serif' }}
        >
          {message}
        </span>
      </div>
    );
  }

  return (
    <motion.div 
      className={`relative ${isCompact ? 'py-3' : 'py-6'}`}
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
    >
      {/* Header with status text */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <motion.div
            className="w-2 h-2 rounded-full bg-[#00f5ff]"
            animate={{ 
              opacity: [1, 0.4, 1],
              scale: [1, 1.2, 1],
            }}
            transition={{ duration: 1, repeat: Infinity }}
            style={{ boxShadow: '0 0 8px rgba(0, 245, 255, 0.8)' }}
          />
          <span 
            className="text-xs uppercase tracking-widest text-[#00f5ff]"
            style={{ fontFamily: 'Orbitron, monospace' }}
          >
            {message}
          </span>
        </div>
        
        {progress !== undefined && (
          <span 
            className="text-xs text-[#9999aa]"
            style={{ fontFamily: 'JetBrains Mono, monospace' }}
          >
            {Math.round(progress)}%
          </span>
        )}
      </div>

      {/* Main scanner bar */}
      <div className="relative h-[3px] bg-[#1a1a24] rounded-full overflow-hidden">
        {/* Background pulse */}
        <motion.div
          className="absolute inset-0 bg-gradient-to-r from-transparent via-[#00f5ff]/20 to-transparent"
          animate={{ x: ['-100%', '200%'] }}
          transition={{ duration: 2, repeat: Infinity, ease: 'easeInOut' }}
        />
        
        {/* Progress bar (if progress is provided) */}
        {progress !== undefined ? (
          <motion.div
            className="absolute top-0 left-0 h-full bg-gradient-to-r from-[#00f5ff] to-[#ff00ff] rounded-full"
            initial={{ width: 0 }}
            animate={{ width: `${progress}%` }}
            transition={{ duration: 0.3 }}
            style={{ boxShadow: '0 0 10px rgba(0, 245, 255, 0.5)' }}
          />
        ) : (
          /* Scanning sweep animation */
          <motion.div
            className="absolute top-0 left-0 h-full w-[40%] bg-gradient-to-r from-transparent via-[#00f5ff] to-transparent rounded-full"
            animate={{ x: ['-100%', '350%'] }}
            transition={{ duration: 1.5, repeat: Infinity, ease: 'easeInOut' }}
            style={{ boxShadow: '0 0 15px rgba(0, 245, 255, 0.6)' }}
          />
        )}
      </div>

      {/* Data blocks visualization */}
      {!isCompact && (
        <div className="flex gap-1 mt-3">
          {Array.from({ length: 12 }).map((_, i) => (
            <motion.div
              key={i}
              className="flex-1 h-[4px] rounded-sm"
              style={{ background: '#1a1a24' }}
              animate={{
                background: ['#1a1a24', '#00f5ff', '#1a1a24'],
                boxShadow: [
                  'none',
                  '0 0 6px rgba(0, 245, 255, 0.5)',
                  'none'
                ],
              }}
              transition={{
                duration: 1.2,
                delay: i * 0.08,
                repeat: Infinity,
                ease: 'easeInOut',
              }}
            />
          ))}
        </div>
      )}

      {/* Hexagonal decorators (default variant only) */}
      {!isCompact && (
        <div className="flex justify-center gap-4 mt-4">
          {[0, 1, 2].map((i) => (
            <motion.div
              key={i}
              className="w-3 h-3 rotate-45 border border-[#2a2a3a]"
              animate={{
                borderColor: ['#2a2a3a', '#00f5ff', '#2a2a3a'],
                scale: [1, 1.1, 1],
              }}
              transition={{
                duration: 1.5,
                delay: i * 0.3,
                repeat: Infinity,
              }}
            />
          ))}
        </div>
      )}
    </motion.div>
  );
}

export default CyberScanner;

