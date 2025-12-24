/**
 * ComparisonStats Component - Display comparison metrics with cyberpunk styling
 */
import { motion } from 'framer-motion';
import { 
  CheckCircle, 
  XCircle, 
  Columns, 
  Rows3, 
  AlertTriangle,
  TrendingUp,
  TrendingDown
} from 'lucide-react';
import type { ComparisonResult } from '../hooks/useApi';

interface ComparisonStatsProps {
  result: ComparisonResult;
}

interface StatCardProps {
  label: string;
  value: string | number;
  icon: React.ReactNode;
  color: 'cyan' | 'pink' | 'yellow' | 'green' | 'red';
  delay?: number;
}

function StatCard({ label, value, icon, color, delay = 0 }: StatCardProps) {
  const colors = {
    cyan: { border: '#00f5ff', bg: 'rgba(0, 245, 255, 0.1)', text: '#00f5ff' },
    pink: { border: '#ff0080', bg: 'rgba(255, 0, 128, 0.1)', text: '#ff0080' },
    yellow: { border: '#f0ff00', bg: 'rgba(240, 255, 0, 0.1)', text: '#f0ff00' },
    green: { border: '#39ff14', bg: 'rgba(57, 255, 20, 0.1)', text: '#39ff14' },
    red: { border: '#ff0080', bg: 'rgba(255, 0, 128, 0.1)', text: '#ff0080' },
  };

  const c = colors[color];

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ delay, duration: 0.3 }}
      className="p-4 rounded-lg border"
      style={{ 
        borderColor: c.border, 
        backgroundColor: c.bg,
        boxShadow: `0 0 15px ${c.bg}`,
      }}
    >
      <div className="flex items-center gap-3">
        <div style={{ color: c.text }}>{icon}</div>
        <div>
          <p 
            className="text-2xl font-bold"
            style={{ 
              fontFamily: 'Orbitron, monospace',
              color: c.text,
              textShadow: `0 0 10px ${c.bg}`,
            }}
          >
            {typeof value === 'number' ? value.toLocaleString() : value}
          </p>
          <p 
            className="text-xs uppercase tracking-wider text-[#888899]"
            style={{ fontFamily: 'Rajdhani, sans-serif' }}
          >
            {label}
          </p>
        </div>
      </div>
    </motion.div>
  );
}

export function ComparisonStats({ result }: ComparisonStatsProps) {
  const { summary, columns, rows, matches } = result;

  return (
    <div className="space-y-6">
      {/* Match Status */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className={`
          p-4 rounded-lg border-2 flex items-center justify-center gap-3
          ${matches 
            ? 'border-[#39ff14] bg-[#39ff14]/10' 
            : 'border-[#ff0080] bg-[#ff0080]/10'
          }
        `}
      >
        {matches ? (
          <>
            <CheckCircle size={32} className="text-[#39ff14]" />
            <span 
              className="text-xl font-bold text-[#39ff14]"
              style={{ fontFamily: 'Orbitron, monospace' }}
            >
              DATASETS MATCH
            </span>
          </>
        ) : (
          <>
            <XCircle size={32} className="text-[#ff0080]" />
            <span 
              className="text-xl font-bold text-[#ff0080]"
              style={{ fontFamily: 'Orbitron, monospace' }}
            >
              DIFFERENCES DETECTED
            </span>
          </>
        )}
      </motion.div>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard
          label={`${summary.df1_name} Rows`}
          value={summary.df1_rows}
          icon={<Rows3 size={24} />}
          color="cyan"
          delay={0.1}
        />
        <StatCard
          label={`${summary.df2_name} Rows`}
          value={summary.df2_rows}
          icon={<Rows3 size={24} />}
          color="pink"
          delay={0.15}
        />
        <StatCard
          label="Common Rows"
          value={summary.common_rows}
          icon={<CheckCircle size={24} />}
          color="green"
          delay={0.2}
        />
        <StatCard
          label="Common Columns"
          value={summary.common_columns}
          icon={<Columns size={24} />}
          color="yellow"
          delay={0.25}
        />
      </div>

      {/* Difference Summary */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard
          label={`Only in ${summary.df1_name}`}
          value={rows.only_in_df1_count}
          icon={<TrendingUp size={24} />}
          color={rows.only_in_df1_count > 0 ? 'red' : 'green'}
          delay={0.3}
        />
        <StatCard
          label={`Only in ${summary.df2_name}`}
          value={rows.only_in_df2_count}
          icon={<TrendingDown size={24} />}
          color={rows.only_in_df2_count > 0 ? 'red' : 'green'}
          delay={0.35}
        />
        <StatCard
          label="Cols Only in A"
          value={columns.only_in_df1.length}
          icon={<AlertTriangle size={24} />}
          color={columns.only_in_df1.length > 0 ? 'yellow' : 'green'}
          delay={0.4}
        />
        <StatCard
          label="Cols Only in B"
          value={columns.only_in_df2.length}
          icon={<AlertTriangle size={24} />}
          color={columns.only_in_df2.length > 0 ? 'yellow' : 'green'}
          delay={0.45}
        />
      </div>

      {/* Mismatched Columns */}
      {columns.mismatched.length > 0 && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
          className="p-4 rounded-lg border border-[#ff6600] bg-[#ff6600]/10"
        >
          <h4 
            className="text-sm uppercase tracking-wider text-[#ff6600] mb-3"
            style={{ fontFamily: 'Orbitron, monospace' }}
          >
            Columns with Mismatches
          </h4>
          <div className="flex flex-wrap gap-2">
            {columns.mismatched.map(col => (
              <span
                key={col}
                className="px-3 py-1 rounded-full text-sm bg-[#ff6600]/20 text-[#ff6600] border border-[#ff6600]/50"
                style={{ fontFamily: 'JetBrains Mono, monospace' }}
              >
                {col}
              </span>
            ))}
          </div>
        </motion.div>
      )}
    </div>
  );
}

export default ComparisonStats;

