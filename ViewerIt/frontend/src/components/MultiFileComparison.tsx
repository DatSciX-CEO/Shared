/**
 * Multi-File Comparison Component - Displays 3+ file comparison results
 * Shows cross-file reconciliation, presence matrix, and value differences
 */
import { motion } from 'framer-motion';
import { 
  Files, 
  GitCompare, 
  Table2, 
  AlertCircle,
  CheckCircle2,
  ChevronDown,
  ChevronRight,
  Layers,
  FileSearch
} from 'lucide-react';
import { useState } from 'react';
import type { MultiFileComparisonResult } from '../hooks/useApi';

interface MultiFileComparisonProps {
  result: MultiFileComparisonResult;
}

export function MultiFileComparison({ result }: MultiFileComparisonProps) {
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set(['summary', 'presence']));

  const toggleSection = (section: string) => {
    const newExpanded = new Set(expandedSections);
    if (newExpanded.has(section)) {
      newExpanded.delete(section);
    } else {
      newExpanded.add(section);
    }
    setExpandedSections(newExpanded);
  };

  const SectionHeader = ({ id, title, icon, count }: { id: string; title: string; icon: React.ReactNode; count?: number }) => (
    <button
      onClick={() => toggleSection(id)}
      className="w-full flex items-center justify-between p-3 bg-[#1a1a24] rounded-lg hover:bg-[#22222e] transition-colors"
    >
      <div className="flex items-center gap-3">
        {icon}
        <span className="font-semibold text-[#e0e0e0]" style={{ fontFamily: 'Rajdhani, sans-serif' }}>
          {title}
        </span>
        {count !== undefined && (
          <span className="px-2 py-0.5 text-xs bg-[#00f5ff]/20 text-[#00f5ff] rounded">
            {count}
          </span>
        )}
      </div>
      {expandedSections.has(id) ? <ChevronDown size={18} /> : <ChevronRight size={18} />}
    </button>
  );

  return (
    <div className="space-y-4">
      {/* Summary */}
      <div>
        <SectionHeader 
          id="summary" 
          title="Multi-File Summary" 
          icon={<Files size={18} className="text-[#00f5ff]" />}
        />
        {expandedSections.has('summary') && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            className="mt-2 p-4 bg-[#12121a] rounded-lg border border-[#2a2a3a]"
          >
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
              <div className="text-center p-3 bg-[#1a1a24] rounded-lg">
                <div className="text-2xl font-bold text-[#00f5ff]" style={{ fontFamily: 'Orbitron, monospace' }}>
                  {result.summary.file_count}
                </div>
                <div className="text-xs text-[#888899] uppercase tracking-wider">Files</div>
              </div>
              <div className="text-center p-3 bg-[#1a1a24] rounded-lg">
                <div className="text-2xl font-bold text-[#ff00ff]" style={{ fontFamily: 'Orbitron, monospace' }}>
                  {result.summary.total_unique_records.toLocaleString()}
                </div>
                <div className="text-xs text-[#888899] uppercase tracking-wider">Unique Records</div>
              </div>
              <div className="text-center p-3 bg-[#1a1a24] rounded-lg">
                <div className="text-2xl font-bold text-[#39ff14]" style={{ fontFamily: 'Orbitron, monospace' }}>
                  {result.summary.records_in_all_files.toLocaleString()}
                </div>
                <div className="text-xs text-[#888899] uppercase tracking-wider">In All Files</div>
              </div>
              <div className="text-center p-3 bg-[#1a1a24] rounded-lg">
                <div className="text-2xl font-bold text-[#f0ff00]" style={{ fontFamily: 'Orbitron, monospace' }}>
                  {result.summary.overlap_percentage}%
                </div>
                <div className="text-xs text-[#888899] uppercase tracking-wider">Overlap</div>
              </div>
            </div>

            {/* File breakdown */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
              {result.summary.file_names.map(filename => (
                <div key={filename} className="p-3 bg-[#1a1a24] rounded-lg border border-[#2a2a3a]">
                  <div className="text-sm font-semibold text-[#e0e0e0] truncate mb-2" title={filename}>
                    {filename}
                  </div>
                  <div className="flex justify-between text-xs">
                    <span className="text-[#888899]">Total:</span>
                    <span className="text-[#00f5ff]">
                      {result.summary.file_record_counts[filename]?.toLocaleString() || 0}
                    </span>
                  </div>
                  <div className="flex justify-between text-xs">
                    <span className="text-[#888899]">Exclusive:</span>
                    <span className="text-[#ff0080]">
                      {result.summary.file_exclusive_counts[filename]?.toLocaleString() || 0}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </motion.div>
        )}
      </div>

      {/* Record Distribution */}
      <div>
        <SectionHeader 
          id="distribution" 
          title="Record Distribution" 
          icon={<Layers size={18} className="text-[#ff00ff]" />}
        />
        {expandedSections.has('distribution') && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            className="mt-2 p-4 bg-[#12121a] rounded-lg border border-[#2a2a3a]"
          >
            <div className="space-y-4">
              {/* Records in ALL files */}
              <div className="p-3 bg-[#39ff14]/10 border border-[#39ff14]/30 rounded-lg">
                <div className="flex items-center gap-2 mb-2">
                  <CheckCircle2 size={16} className="text-[#39ff14]" />
                  <span className="font-semibold text-[#39ff14]">Records in ALL {result.summary.file_count} files</span>
                  <span className="ml-auto text-lg font-bold text-[#39ff14]">
                    {result.records_in_all_files.count.toLocaleString()}
                  </span>
                </div>
                {result.records_in_all_files.samples.length > 0 && (
                  <div className="text-xs text-[#888899]">
                    Sample keys: {result.records_in_all_files.samples.slice(0, 3).map((s: any) => s.key).join(', ')}
                    {result.records_in_all_files.samples.length > 3 && '...'}
                  </div>
                )}
              </div>

              {/* Records in SOME files */}
              {result.records_in_some_files.count > 0 && (
                <div className="p-3 bg-[#f0ff00]/10 border border-[#f0ff00]/30 rounded-lg">
                  <div className="flex items-center gap-2 mb-2">
                    <AlertCircle size={16} className="text-[#f0ff00]" />
                    <span className="font-semibold text-[#f0ff00]">Records in SOME files (partial overlap)</span>
                    <span className="ml-auto text-lg font-bold text-[#f0ff00]">
                      {result.records_in_some_files.count.toLocaleString()}
                    </span>
                  </div>
                  <div className="space-y-1 mt-2">
                    {Object.entries(result.records_in_some_files.by_file_count).map(([count, data]: [string, any]) => (
                      <div key={count} className="flex justify-between text-xs">
                        <span className="text-[#888899]">In {count} of {result.summary.file_count} files:</span>
                        <span className="text-[#f0ff00]">{data.count.toLocaleString()}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Records in ONE file only */}
              {result.records_in_one_file.count > 0 && (
                <div className="p-3 bg-[#ff0080]/10 border border-[#ff0080]/30 rounded-lg">
                  <div className="flex items-center gap-2 mb-2">
                    <FileSearch size={16} className="text-[#ff0080]" />
                    <span className="font-semibold text-[#ff0080]">Records in ONE file only (exclusive)</span>
                    <span className="ml-auto text-lg font-bold text-[#ff0080]">
                      {result.records_in_one_file.count.toLocaleString()}
                    </span>
                  </div>
                  <div className="space-y-1 mt-2">
                    {Object.entries(result.records_in_one_file.by_file).map(([file, count]) => (
                      <div key={file} className="flex justify-between text-xs">
                        <span className="text-[#888899] truncate" title={file}>{file}:</span>
                        <span className="text-[#ff0080]">{(count as number).toLocaleString()}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </motion.div>
        )}
      </div>

      {/* Presence Matrix */}
      <div>
        <SectionHeader 
          id="presence" 
          title="Presence Matrix" 
          icon={<Table2 size={18} className="text-[#00f5ff]" />}
          count={result.presence_matrix.rows.length}
        />
        {expandedSections.has('presence') && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            className="mt-2 p-4 bg-[#12121a] rounded-lg border border-[#2a2a3a]"
          >
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-[#2a2a3a]">
                    {result.presence_matrix.headers.map((header, idx) => (
                      <th 
                        key={idx}
                        className="p-2 text-left text-xs text-[#888899] uppercase tracking-wider"
                        style={{ fontFamily: 'Orbitron, monospace' }}
                      >
                        {header}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {result.presence_matrix.rows.slice(0, 20).map((row, rowIdx) => (
                    <tr key={rowIdx} className="border-b border-[#2a2a3a]/50 hover:bg-[#1a1a24]">
                      {row.map((cell, cellIdx) => (
                        <td key={cellIdx} className="p-2">
                          {cellIdx === 0 ? (
                            <span className="text-[#e0e0e0] font-mono text-xs">{String(cell)}</span>
                          ) : (
                            <span className={cell ? 'text-[#39ff14]' : 'text-[#ff0080]'}>
                              {cell ? '✓' : '✗'}
                            </span>
                          )}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
              {result.presence_matrix.rows.length > 20 && (
                <div className="text-center text-xs text-[#888899] mt-2">
                  Showing 20 of {result.presence_matrix.rows.length} records
                </div>
              )}
            </div>
          </motion.div>
        )}
      </div>

      {/* Value Differences */}
      {Object.keys(result.value_differences).length > 0 && (
        <div>
          <SectionHeader 
            id="differences" 
            title="Value Differences" 
            icon={<GitCompare size={18} className="text-[#f0ff00]" />}
            count={Object.keys(result.value_differences).length}
          />
          {expandedSections.has('differences') && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              className="mt-2 p-4 bg-[#12121a] rounded-lg border border-[#2a2a3a]"
            >
              <div className="space-y-4">
                {Object.entries(result.value_differences).map(([column, data]: [string, any]) => (
                  <div key={column} className="p-3 bg-[#1a1a24] rounded-lg">
                    <div className="flex items-center justify-between mb-3">
                      <span className="font-semibold text-[#e0e0e0]">{column}</span>
                      <span className="px-2 py-0.5 bg-[#f0ff00]/20 text-[#f0ff00] text-xs rounded">
                        {data.mismatch_count} mismatches
                      </span>
                    </div>
                    {data.samples.length > 0 && (
                      <div className="space-y-2">
                        {data.samples.slice(0, 5).map((sample: any, idx: number) => (
                          <div key={idx} className="p-2 bg-[#12121a] rounded text-xs">
                            <div className="text-[#888899] mb-1">Key: {sample.key}</div>
                            <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                              {Object.entries(sample.values).map(([file, value]) => (
                                <div key={file} className="flex justify-between">
                                  <span className="text-[#888899] truncate" title={file}>{file}:</span>
                                  <span className="text-[#e0e0e0] font-mono">{String(value)}</span>
                                </div>
                              ))}
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </motion.div>
          )}
        </div>
      )}

      {/* Column Analysis */}
      <div>
        <SectionHeader 
          id="columns" 
          title="Column Analysis" 
          icon={<Table2 size={18} className="text-[#ff00ff]" />}
        />
        {expandedSections.has('columns') && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            className="mt-2 p-4 bg-[#12121a] rounded-lg border border-[#2a2a3a]"
          >
            <div className="grid grid-cols-3 gap-4 mb-4">
              <div className="text-center p-3 bg-[#1a1a24] rounded-lg">
                <div className="text-xl font-bold text-[#00f5ff]">
                  {result.column_analysis.all_columns.length}
                </div>
                <div className="text-xs text-[#888899]">Total Columns</div>
              </div>
              <div className="text-center p-3 bg-[#1a1a24] rounded-lg">
                <div className="text-xl font-bold text-[#39ff14]">
                  {result.column_analysis.columns_in_all_files.length}
                </div>
                <div className="text-xs text-[#888899]">In All Files</div>
              </div>
              <div className="text-center p-3 bg-[#1a1a24] rounded-lg">
                <div className="text-xl font-bold text-[#ff0080]">
                  {Object.keys(result.column_analysis.type_mismatches).length}
                </div>
                <div className="text-xs text-[#888899]">Type Mismatches</div>
              </div>
            </div>

            {/* Common columns */}
            <div className="mb-4">
              <div className="text-sm text-[#888899] mb-2">Columns in all files:</div>
              <div className="flex flex-wrap gap-2">
                {result.column_analysis.columns_in_all_files.map(col => (
                  <span key={col} className="px-2 py-1 bg-[#39ff14]/20 text-[#39ff14] text-xs rounded border border-[#39ff14]/30">
                    {col}
                  </span>
                ))}
              </div>
            </div>

            {/* Type mismatches */}
            {Object.keys(result.column_analysis.type_mismatches).length > 0 && (
              <div>
                <div className="text-sm text-[#ff0080] mb-2">⚠️ Type mismatches:</div>
                <div className="space-y-2">
                  {Object.entries(result.column_analysis.type_mismatches).map(([col, types]) => (
                    <div key={col} className="p-2 bg-[#ff0080]/10 rounded border border-[#ff0080]/30">
                      <span className="text-[#ff0080] font-semibold">{col}:</span>
                      <div className="flex flex-wrap gap-2 mt-1">
                        {Object.entries(types as Record<string, string>).map(([file, type]) => (
                          <span key={file} className="text-xs text-[#888899]">
                            {file}: <span className="text-[#e0e0e0] font-mono">{type}</span>
                          </span>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </motion.div>
        )}
      </div>

      {/* Reconciliation Report */}
      {result.reconciliation_report && result.reconciliation_report.recommendations.length > 0 && (
        <div>
          <SectionHeader 
            id="reconciliation" 
            title="Reconciliation Recommendations" 
            icon={<AlertCircle size={18} className="text-[#f0ff00]" />}
            count={result.reconciliation_report.recommendations.length}
          />
          {expandedSections.has('reconciliation') && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              className="mt-2 p-4 bg-[#12121a] rounded-lg border border-[#2a2a3a]"
            >
              <div className="space-y-2">
                {result.reconciliation_report.recommendations.map((rec, idx) => (
                  <div key={idx} className="p-3 bg-[#f0ff00]/10 border border-[#f0ff00]/30 rounded-lg">
                    <div className="flex items-start gap-2">
                      <AlertCircle size={16} className="text-[#f0ff00] mt-0.5" />
                      <div>
                        <div className="text-sm text-[#e0e0e0]">{rec.message}</div>
                        {rec.action && (
                          <div className="text-xs text-[#888899] mt-1">Action: {rec.action}</div>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </motion.div>
          )}
        </div>
      )}
    </div>
  );
}

export default MultiFileComparison;

