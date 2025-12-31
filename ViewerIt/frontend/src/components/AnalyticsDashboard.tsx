/**
 * AnalyticsDashboard - Native React visualization dashboard
 * Replaces the embedded Streamlit visualizations with native Recharts
 */
import { motion } from 'framer-motion';
import { 
  Activity, 
  PieChart, 
  AlertTriangle,
  CheckCircle2
} from 'lucide-react';
import { BarChartViz, PieChartViz } from './charts';
import type { ComparisonResult, FileInfo } from '../hooks/useApi';

interface AnalyticsDashboardProps {
  comparisonResult: ComparisonResult | null;
  fileInfos: Record<string, FileInfo>;
  uploadedFiles: string[];
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
      {/* Summary Cards */}
      <div className="grid grid-cols-4 gap-4">
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0 }}
          className="cyber-card text-center p-4"
        >
          <Activity size={24} className="mx-auto mb-2 text-[#00f5ff]" />
          <div 
            className="text-2xl font-bold text-[#00f5ff]" 
            style={{ fontFamily: 'Orbitron, monospace' }}
          >
            {df1Rows.toLocaleString()}
          </div>
          <div className="text-xs text-[#888899] uppercase tracking-wider mt-1">
            {df1Name} Rows
          </div>
        </motion.div>

        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="cyber-card text-center p-4"
        >
          <Activity size={24} className="mx-auto mb-2 text-[#ff00ff]" />
          <div 
            className="text-2xl font-bold text-[#ff00ff]" 
            style={{ fontFamily: 'Orbitron, monospace' }}
          >
            {df2Rows.toLocaleString()}
          </div>
          <div className="text-xs text-[#888899] uppercase tracking-wider mt-1">
            {df2Name} Rows
          </div>
        </motion.div>

        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="cyber-card text-center p-4"
        >
          <PieChart size={24} className="mx-auto mb-2 text-[#f0ff00]" />
          <div 
            className="text-2xl font-bold text-[#f0ff00]" 
            style={{ fontFamily: 'Orbitron, monospace' }}
          >
            {matchPercentage}%
          </div>
          <div className="text-xs text-[#888899] uppercase tracking-wider mt-1">Match Rate</div>
        </motion.div>

        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="cyber-card text-center p-4"
        >
          {isMatch ? (
            <CheckCircle2 size={24} className="mx-auto mb-2 text-[#39ff14]" />
          ) : (
            <AlertTriangle size={24} className="mx-auto mb-2 text-[#ff0080]" />
          )}
          <div 
            className={`text-2xl font-bold ${isMatch ? 'text-[#39ff14]' : 'text-[#ff0080]'}`}
            style={{ fontFamily: 'Orbitron, monospace' }}
          >
            {isMatch ? 'MATCH' : 'DIFF'}
          </div>
          <div className="text-xs text-[#888899] uppercase tracking-wider mt-1">Status</div>
        </motion.div>
      </div>

      {/* Charts Row 1 */}
      <div className="grid grid-cols-2 gap-6">
        {/* Row Distribution Pie */}
        <motion.div 
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.4 }}
          className="cyber-card"
        >
          <h3 
            className="text-sm uppercase tracking-wider text-[#00f5ff] mb-4"
            style={{ fontFamily: 'Orbitron, monospace' }}
          >
            Row Distribution
          </h3>
          {rowDistributionData.length > 0 ? (
            <PieChartViz 
              data={rowDistributionData} 
              height={280}
              innerRadius={50}
              outerRadius={90}
            />
          ) : (
            <div className="h-[280px] flex items-center justify-center text-[#888899]">
              No data to display
            </div>
          )}
        </motion.div>

        {/* Column Distribution Pie */}
        <motion.div 
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.5 }}
          className="cyber-card"
        >
          <h3 
            className="text-sm uppercase tracking-wider text-[#ff00ff] mb-4"
            style={{ fontFamily: 'Orbitron, monospace' }}
          >
            Column Distribution
          </h3>
          {columnDistributionData.length > 0 ? (
            <PieChartViz 
              data={columnDistributionData} 
              height={280}
              innerRadius={50}
              outerRadius={90}
            />
          ) : (
            <div className="h-[280px] flex items-center justify-center text-[#888899]">
              No data to display
            </div>
          )}
        </motion.div>
      </div>

      {/* Charts Row 2 */}
      <div className="grid grid-cols-2 gap-6">
        {/* File Row Count Comparison */}
        <motion.div 
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.6 }}
          className="cyber-card"
        >
          <h3 
            className="text-sm uppercase tracking-wider text-[#f0ff00] mb-4"
            style={{ fontFamily: 'Orbitron, monospace' }}
          >
            File Size Comparison (Rows)
          </h3>
          {fileSizeData.length > 0 ? (
            <BarChartViz 
              data={fileSizeData} 
              height={250}
              yAxisLabel="Row Count"
            />
          ) : (
            <div className="h-[250px] flex items-center justify-center text-[#888899]">
              No data to display
            </div>
          )}
        </motion.div>

        {/* Column Mismatches */}
        <motion.div 
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.7 }}
          className="cyber-card"
        >
          <h3 
            className="text-sm uppercase tracking-wider text-[#ff0080] mb-4"
            style={{ fontFamily: 'Orbitron, monospace' }}
          >
            Top Column Mismatches
          </h3>
          {columnMismatchData.length > 0 ? (
            <BarChartViz 
              data={columnMismatchData} 
              height={250}
              yAxisLabel="Mismatch Count"
            />
          ) : (
            <div className="h-[250px] flex items-center justify-center">
              <div className="text-center">
                <CheckCircle2 size={48} className="mx-auto mb-3 text-[#39ff14]" />
                <p className="text-[#39ff14]" style={{ fontFamily: 'Rajdhani, sans-serif' }}>
                  No column mismatches detected!
                </p>
              </div>
            </div>
          )}
        </motion.div>
      </div>

      {/* Detailed Comparison Table */}
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.8 }}
        className="cyber-card"
      >
        <h3 
          className="text-sm uppercase tracking-wider text-[#00f5ff] mb-4"
          style={{ fontFamily: 'Orbitron, monospace' }}
        >
          Column Comparison Matrix
        </h3>
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
                columnStats.map((col) => {
                  const matchPct = commonRows > 0
                    ? ((commonRows - col.mismatch_count) / commonRows * 100)
                    : 100;
                  return (
                    <tr key={col.column}>
                      <td style={{ fontFamily: 'JetBrains Mono, monospace' }}>{col.column}</td>
                      <td className={col.mismatch_count > 0 ? 'text-[#ff0080]' : 'text-[#39ff14]'}>
                        {col.mismatch_count.toLocaleString()}
                      </td>
                      <td>
                        <div className="flex items-center gap-2">
                          <div className="flex-1 h-2 bg-[#2a2a3a] rounded-full overflow-hidden max-w-[100px]">
                            <div 
                              className={`h-full rounded-full ${matchPct === 100 ? 'bg-[#39ff14]' : matchPct > 90 ? 'bg-[#f0ff00]' : 'bg-[#ff0080]'}`}
                              style={{ width: `${Math.max(0, Math.min(100, matchPct))}%` }}
                            />
                          </div>
                          <span className="text-xs text-[#888899]">{matchPct.toFixed(1)}%</span>
                        </div>
                      </td>
                      <td>
                        <span className={`px-2 py-1 rounded text-xs ${
                          col.mismatch_count === 0 
                            ? 'bg-[#39ff14]/20 text-[#39ff14]' 
                            : 'bg-[#ff0080]/20 text-[#ff0080]'
                        }`}>
                          {col.mismatch_count === 0 ? 'MATCH' : 'DIFFERS'}
                        </span>
                      </td>
                    </tr>
                  );
                })
              ) : (
                <tr>
                  <td colSpan={4} className="text-center text-[#888899] py-4">
                    No column statistics available
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </motion.div>
    </div>
  );
}

export default AnalyticsDashboard;
