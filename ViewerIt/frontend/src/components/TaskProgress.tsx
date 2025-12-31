/**
 * TaskProgress Component - Cyberpunk-styled progress indicator
 * Shows task progress with animated effects and status messages
 */
import { motion, AnimatePresence } from 'framer-motion';
import { Loader2, CheckCircle, XCircle, Clock } from 'lucide-react';

interface TaskProgressProps {
  progress: number;
  message: string;
  status: 'pending' | 'in_progress' | 'completed' | 'failed';
  taskType?: string;
  showPercentage?: boolean;
  compact?: boolean;
}

export function TaskProgress({
  progress,
  message,
  status,
  taskType = 'Task',
  showPercentage = true,
  compact = false,
}: TaskProgressProps) {
  // Color based on status
  const getStatusColor = () => {
    switch (status) {
      case 'completed':
        return '#39ff14'; // Neon green
      case 'failed':
        return '#ff3366'; // Neon red
      case 'in_progress':
        return '#00f5ff'; // Cyan
      default:
        return '#888899'; // Gray
    }
  };

  const statusColor = getStatusColor();

  // Icon based on status
  const StatusIcon = () => {
    switch (status) {
      case 'completed':
        return <CheckCircle size={compact ? 16 : 20} className="text-[#39ff14]" />;
      case 'failed':
        return <XCircle size={compact ? 16 : 20} className="text-[#ff3366]" />;
      case 'in_progress':
        return (
          <motion.div
            animate={{ rotate: 360 }}
            transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
          >
            <Loader2 size={compact ? 16 : 20} className="text-[#00f5ff]" />
          </motion.div>
        );
      default:
        return <Clock size={compact ? 16 : 20} className="text-[#888899]" />;
    }
  };

  if (compact) {
    return (
      <div className="flex items-center gap-2">
        <StatusIcon />
        <div className="flex-1">
          <div className="h-1.5 bg-[#1a1a2e] rounded-full overflow-hidden">
            <motion.div
              className="h-full rounded-full"
              style={{ backgroundColor: statusColor }}
              initial={{ width: 0 }}
              animate={{ width: `${progress}%` }}
              transition={{ duration: 0.3 }}
            />
          </div>
        </div>
        {showPercentage && (
          <span 
            className="text-xs tabular-nums"
            style={{ color: statusColor, fontFamily: 'JetBrains Mono, monospace' }}
          >
            {progress}%
          </span>
        )}
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -10 }}
      className="p-4 rounded-lg bg-[#12121a] border border-[#2a2a3a]"
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <StatusIcon />
          <span 
            className="text-sm font-medium"
            style={{ fontFamily: 'Rajdhani, sans-serif', color: statusColor }}
          >
            {taskType}
          </span>
        </div>
        {showPercentage && (
          <motion.span 
            className="text-sm tabular-nums"
            style={{ color: statusColor, fontFamily: 'JetBrains Mono, monospace' }}
            key={progress}
            initial={{ scale: 1.2 }}
            animate={{ scale: 1 }}
          >
            {progress}%
          </motion.span>
        )}
      </div>

      {/* Progress bar */}
      <div className="relative h-2 bg-[#1a1a2e] rounded-full overflow-hidden mb-2">
        {/* Animated background pattern */}
        <motion.div
          className="absolute inset-0 opacity-30"
          style={{
            background: `repeating-linear-gradient(
              90deg,
              transparent,
              transparent 10px,
              ${statusColor}20 10px,
              ${statusColor}20 20px
            )`,
          }}
          animate={status === 'in_progress' ? { x: [0, 20] } : {}}
          transition={{ duration: 0.5, repeat: Infinity, ease: 'linear' }}
        />
        
        {/* Progress fill */}
        <motion.div
          className="absolute inset-y-0 left-0 rounded-full"
          style={{ backgroundColor: statusColor }}
          initial={{ width: 0 }}
          animate={{ width: `${progress}%` }}
          transition={{ duration: 0.5, ease: 'easeOut' }}
        />

        {/* Glow effect at the edge */}
        {status === 'in_progress' && (
          <motion.div
            className="absolute inset-y-0 w-4 rounded-full blur-sm"
            style={{ 
              backgroundColor: statusColor,
              left: `calc(${progress}% - 8px)`,
            }}
            animate={{ opacity: [0.5, 1, 0.5] }}
            transition={{ duration: 1, repeat: Infinity }}
          />
        )}
      </div>

      {/* Message */}
      <AnimatePresence mode="wait">
        <motion.p
          key={message}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="text-xs text-[#888899] truncate"
          style={{ fontFamily: 'JetBrains Mono, monospace' }}
        >
          {message || 'Processing...'}
        </motion.p>
      </AnimatePresence>

      {/* Scanline effect when in progress */}
      {status === 'in_progress' && (
        <motion.div
          className="absolute inset-0 pointer-events-none rounded-lg overflow-hidden"
          style={{
            background: `linear-gradient(
              transparent 0%,
              ${statusColor}08 50%,
              transparent 100%
            )`,
            backgroundSize: '100% 4px',
          }}
          animate={{ backgroundPositionY: ['0%', '100%'] }}
          transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
        />
      )}
    </motion.div>
  );
}

export default TaskProgress;

