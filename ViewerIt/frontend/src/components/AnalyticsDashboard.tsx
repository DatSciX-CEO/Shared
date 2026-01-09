/**
 * AnalyticsDashboard - Native React visualization dashboard
 * Enhanced with professional cyberpunk theming and neon glow effects
 */
import { motion } from 'framer-motion';
import { 
  Activity, 
  PieChart, 
  AlertTriangle,
  CheckCircle2,
  TrendingUp,
  Database
} from 'lucide-react';
import { BarChartViz, PieChartViz } from './charts';
import { CyberCard } from './CyberCard';
import type { ComparisonResult, FileInfo } from '../hooks/useApi';

interface AnalyticsDashboardProps {
  comparisonResult: ComparisonResult | null;
  fileInfos: Record<string, FileInfo>;
  uploadedFiles: string[];
}

// Metric Card Component for summary stats
interface MetricCardProps {
  icon: React.ReactNode;
  value: string | number;
  label: string;
  color: 'cyan' | 'magenta' | 'yellow' | 'green' | 'pink';
  delay?: number;
}

function MetricCard({ icon, value, label, color, delay = 0 }: MetricCardProps) {
  const colorConfig = {
    cyan: { text: '#00f5ff', glow: 'rgba(0, 245, 255, 0.5)', border: 'rgba(0, 245, 255, 0.3)' },
    magenta: { text: '#ff00ff', glow: 'rgba(255, 0, 255, 0.5)', border: 'rgba(255, 0, 255, 0.3)' },
    yellow: { text: '#f0ff00', glow: 'rgba(240, 255, 0, 0.5)', border: 'rgba(240, 255, 0, 0.3)' },
    green: { text: '#39ff14', glow: 'rgba(57, 255, 20, 0.5)', border: 'rgba(57, 255, 20, 0.3)' },
    pink: { text: '#ff0080', glow: 'rgba(255, 0, 128, 0.5)', border: 'rgba(255, 0, 128, 0.3)' },
  };

  const config = colorConfig[color];

  return (
    <motion.div 
      initial={{ opacity: 0, y: 20, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ delay, duration: 0.4, ease: 'easeOut' }}
      className="relative p-5 rounded-lg bg-gradient-to-br from-[#12121a] to-[#1a1a24] border cyber-corners overflow-hidden"
      style={{ borderColor: config.border }}
    >
      {/* Animated top accent */}
      <motion.div 
        className="absolute top-0 left-0 right-0 h-[2px]"
        style={{ background: `linear-gradient(90deg, transparent, ${config.text}, transparent)` }}
        animate={{ opacity: [0.5, 1, 0.5] }}
        transition={{ duration: 2, repeat: Infinity }}
      />
      
      {/* Icon with glow */}
      <div 
        className="mx-auto mb-3 w-10 h-10 rounded-lg flex items-center justify-center"
        style={{ 
          background: `${config.text}15`,
          boxShadow: `0 0 15px ${config.glow}`,
        }}
      >
        <span style={{ color: config.text }}>{icon}</span>
      </div>
      
      {/* Value with neon glow */}
      <motion.div 
        className="text-2xl font-bold text-center"
        style={{ 
          fontFamily: 'Orbitron, monospace',
          color: config.text,
          textShadow: `0 0 10px ${config.glow}`,
        }}
        animate={{ textShadow: [`0 0 10px ${config.glow}`, `0 0 20px ${config.glow}`, `0 0 10px ${config.glow}`] }}
        transition={{ duration: 2, repeat: Infinity }}
      >
        {typeof value === 'number' ? value.toLocaleString() : value}
      </motion.div>
      
      {/* Label */}
      <div 
        className="text-xs text-center uppercase tracking-widest mt-2"
        style={{ fontFamily: 'Rajdhani, sans-serif', color: '#9999aa' }}
      >
        {label}
      </div>
    </motion.div>
  );
}

export function AnalyticsDashboard({ 
  comparisonResult, 
  fileInfos,
  uploadedFiles 
}: AnalyticsDashboardProps) {
  if (!comparisonResult) {
    return null;
  }

  // Safely access summary properties with fallbacks
  const df1Rows = comparisonResult.summary?.df1_rows ?? 0;
  const df2Rows = comparisonResult.summary?.df2_rows ?? 0;
  const commonRows = comparisonResult.summary?.common_rows ?? 0;
  const df1Name = comparisonResult.summary?.df1_name ?? 'File A';
  const df2Name = comparisonResult.summary?.df2_name ?? 'File B';
  const isMatch = comparisonResult.matches ?? false;

  // Prepare data for row distribution pie chart
  const rowDistributionData = [
    { 
      name: 'Common Rows', 
      value: commonRows, 
      color: '#39ff14' 
    },
    { 
      name: `Only in ${df1Name}`, 
      value: comparisonResult.rows?.only_in_df1_count ?? 0, 
      color: '#00f5ff' 
    },
    { 
      name: `Only in ${df2Name}`, 
      value: comparisonResult.rows?.only_in_df2_count ?? 0, 
      color: '#ff00ff' 
    },
  ].filter(d => d.value > 0);

  // Prepare data for column mismatch bar chart - use column_stats, not columns.mismatches
  const columnStats = comparisonResult.column_stats ?? [];
  const columnMismatchData = columnStats
    .filter(col => col.mismatch_count > 0)
    .slice(0, 10)
    .map((col, index) => ({
      name: col.column.length > 15 ? col.column.slice(0, 15) + '...' : col.column,
      value: col.mismatch_count,
      color: index % 2 === 0 ? '#ff0080' : '#ff00ff'
    }));

  // Prepare file size comparison data - use 'rows' not 'row_count'
  const fileSizeData = uploadedFiles
    .filter(f => fileInfos[f])
    .map(f => ({
      name: f.length > 20 ? f.slice(0, 20) + '...' : f,
      value: fileInfos[f]?.rows ?? 0,
      color: uploadedFiles.indexOf(f) === 0 ? '#00f5ff' : '#ff00ff'
    }));

  // Prepare column comparison data
  const file1Cols = fileInfos[uploadedFiles[0]]?.column_names ?? [];
  const file2Cols = fileInfos[uploadedFiles[1]]?.column_names ?? [];
  const commonCols = file1Cols.filter(c => file2Cols.includes(c));
  const onlyInFile1 = file1Cols.filter(c => !file2Cols.includes(c));
  const onlyInFile2 = file2Cols.filter(c => !file1Cols.includes(c));

  const columnDistributionData = [
    { name: 'Common', value: commonCols.length, color: '#39ff14' },
    { name: `Only in File 1`, value: onlyInFile1.length, color: '#00f5ff' },
    { name: `Only in File 2`, value: onlyInFile2.length, color: '#ff00ff' },
  ].filter(d => d.value > 0);

  // Calculate match percentage
  const totalRows = df1Rows + df2Rows;
  const matchPercentage = totalRows > 0 
    ? ((commonRows * 2) / totalRows * 100).toFixed(1)
    : '0.0';

  return (
    <div className="space-y-6">
      {/* Summary Metric Cards */}
      <div className="grid grid-cols-4 gap-4">
        <MetricCard
          icon={<Database size={20} />}
          value={df1Rows}
          label={`${df1Name} Rows`}
          color="cyan"
          delay={0}
        />
        <MetricCard
          icon={<Database size={20} />}
          value={df2Rows}
          label={`${df2Name} Rows`}
          color="magenta"
          delay={0.1}
        />
        <MetricCard
          icon={<TrendingUp size={20} />}
          value={`${matchPercentage}%`}
          label="Match Rate"
          color="yellow"
          delay={0.2}
        />
        <MetricCard
          icon={isMatch ? <CheckCircle2 size={20} /> : <AlertTriangle size={20} />}
          value={isMatch ? 'MATCH' : 'DIFF'}
          label="Status"
          color={isMatch ? 'green' : 'pink'}
          delay={0.3}
        />
      </div>

      {/* Charts Row 1 */}
      <div className="grid grid-cols-2 gap-6">
        {/* Row Distribution Pie */}
        <CyberCard title="Row Distribution" accent="cyan" showCorners={true}>
          {rowDistributionData.length > 0 ? (
            <div className="chart-glow">
              <PieChartViz 
                data={rowDistributionData} 
                height={280}
                innerRadius={50}
                outerRadius={90}
              />
            </div>
          ) : (
            <div className="h-[280px] flex items-center justify-center text-[#9999aa]">
              No data to display
            </div>
          )}
        </CyberCard>

        {/* Column Distribution Pie */}
        <CyberCard title="Column Distribution" accent="pink" showCorners={true}>
          {columnDistributionData.length > 0 ? (
            <div className="chart-glow">
              <PieChartViz 
                data={columnDistributionData} 
                height={280}
                innerRadius={50}
                outerRadius={90}
              />
            </div>
          ) : (
            <div className="h-[280px] flex items-center justify-center text-[#9999aa]">
              No data to display
            </div>
          )}
        </CyberCard>
      </div>

      {/* Charts Row 2 */}
      <div className="grid grid-cols-2 gap-6">
        {/* File Row Count Comparison */}
        <CyberCard title="File Size Comparison (Rows)" accent="yellow" showCorners={true}>
          {fileSizeData.length > 0 ? (
            <div className="chart-glow">
              <BarChartViz 
                data={fileSizeData} 
                height={250}
                yAxisLabel="Row Count"
              />
            </div>
          ) : (
            <div className="h-[250px] flex items-center justify-center text-[#9999aa]">
              No data to display
            </div>
          )}
        </CyberCard>

        {/* Column Mismatches */}
        <CyberCard title="Top Column Mismatches" accent="pink" showCorners={true}>
          {columnMismatchData.length > 0 ? (
            <div className="chart-glow">
              <BarChartViz 
                data={columnMismatchData} 
                height={250}
                yAxisLabel="Mismatch Count"
              />
            </div>
          ) : (
            <div className="h-[250px] flex items-center justify-center">
              <motion.div 
                className="text-center"
                initial={{ scale: 0.9 }}
                animate={{ scale: 1 }}
                transition={{ duration: 0.3 }}
              >
                <motion.div
                  animate={{ 
                    boxShadow: [
                      '0 0 10px rgba(57, 255, 20, 0.3)',
                      '0 0 25px rgba(57, 255, 20, 0.5)',
                      '0 0 10px rgba(57, 255, 20, 0.3)'
                    ]
                  }}
                  transition={{ duration: 2, repeat: Infinity }}
                  className="inline-block rounded-full p-3 mb-3"
                  style={{ background: 'rgba(57, 255, 20, 0.1)' }}
                >
                  <CheckCircle2 size={40} className="text-[#39ff14]" />
                </motion.div>
                <p className="text-[#39ff14] font-semibold" style={{ fontFamily: 'Rajdhani, sans-serif' }}>
                  No column mismatches detected!
                </p>
              </motion.div>
            </div>
          )}
        </CyberCard>
      </div>

      {/* Detailed Comparison Table */}
      <CyberCard title="Column Comparison Matrix" accent="cyan" showCorners={true}>
        <div className="overflow-x-auto">
          <table className="data-grid w-full">
            <thead>
              <tr>
                <th>Column Name</th>
                <th>Mismatch Count</th>
                <th>Match %</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {columnStats.length > 0 ? (
                columnStats.map((col, index) => {
                  const matchPct = commonRows > 0
                    ? ((commonRows - col.mismatch_count) / commonRows * 100)
                    : 100;
                  return (
                    <motion.tr 
                      key={col.column}
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: 0.05 * index }}
                    >
                      <td style={{ fontFamily: 'JetBrains Mono, monospace' }}>{col.column}</td>
                      <td className={col.mismatch_count > 0 ? 'text-[#ff0080]' : 'text-[#39ff14]'}>
                        {col.mismatch_count.toLocaleString()}
                      </td>
                      <td>
                        <div className="flex items-center gap-2">
                          <div className="flex-1 h-2 bg-[#2a2a3a] rounded-full overflow-hidden max-w-[100px]">
                            <motion.div 
                              className={`h-full rounded-full ${matchPct === 100 ? 'bg-[#39ff14]' : matchPct > 90 ? 'bg-[#f0ff00]' : 'bg-[#ff0080]'}`}
                              initial={{ width: 0 }}
                              animate={{ width: `${Math.max(0, Math.min(100, matchPct))}%` }}
                              transition={{ delay: 0.1 * index, duration: 0.5 }}
                            />
                          </div>
                          <span className="text-xs text-[#9999aa]">{matchPct.toFixed(1)}%</span>
                        </div>
                      </td>
                      <td>
                        <span className={`px-2 py-1 rounded text-xs font-medium ${
                          col.mismatch_count === 0 
                            ? 'bg-[#39ff14]/20 text-[#39ff14]' 
                            : 'bg-[#ff0080]/20 text-[#ff0080]'
                        }`}>
                          {col.mismatch_count === 0 ? 'MATCH' : 'DIFFERS'}
                        </span>
                      </td>
                    </motion.tr>
                  );
                })
              ) : (
                <tr>
                  <td colSpan={4} className="text-center text-[#9999aa] py-4">
                    No column statistics available
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </CyberCard>
    </div>
  );
}

export default AnalyticsDashboard;
