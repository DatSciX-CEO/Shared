/**
 * Quality Dashboard Component - Displays data quality metrics
 * Shows completeness, uniqueness, validity, and recommendations
 */
import { motion } from 'framer-motion';
import { 
  CheckCircle2, 
  AlertTriangle, 
  TrendingUp,
  BarChart2,
  Target,
  Zap,
  ChevronDown,
  ChevronRight
} from 'lucide-react';
import { useState } from 'react';
import type { QualityCheckResult, MultiQualityResult } from '../hooks/useApi';

interface QualityDashboardProps {
  result: QualityCheckResult | MultiQualityResult;
}

// Type guard to check if result is MultiQualityResult
function isMultiQualityResult(result: QualityCheckResult | MultiQualityResult): result is MultiQualityResult {
  return 'individual_results' in result;
}

// Score ring component
function ScoreRing({ score, grade, size = 120 }: { score: number; grade: string; size?: number }) {
  const radius = (size - 10) / 2;
  const circumference = 2 * Math.PI * radius;
  const progress = (score / 100) * circumference;
  
  const gradeColor = {
    'A': '#39ff14',
    'B': '#00f5ff',
    'C': '#f0ff00',
    'D': '#ff6600',
    'F': '#ff0080',
  }[grade] || '#888899';

  return (
    <div className="relative" style={{ width: size, height: size }}>
      <svg width={size} height={size} className="transform -rotate-90">
        {/* Background circle */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="#2a2a3a"
          strokeWidth="8"
        />
        {/* Progress circle */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke={gradeColor}
          strokeWidth="8"
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={circumference - progress}
          style={{ transition: 'stroke-dashoffset 1s ease-in-out' }}
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <div className="text-3xl font-bold" style={{ color: gradeColor, fontFamily: 'Orbitron, monospace' }}>
          {grade}
        </div>
        <div className="text-sm text-[#888899]">{score.toFixed(0)}/100</div>
      </div>
    </div>
  );
}

// Single dataset quality view
function SingleQualityView({ result }: { result: QualityCheckResult }) {
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set(['overview', 'recommendations']));

  const toggleSection = (section: string) => {
    const newExpanded = new Set(expandedSections);
    if (newExpanded.has(section)) {
      newExpanded.delete(section);
    } else {
      newExpanded.add(section);
    }
    setExpandedSections(newExpanded);
  };

  const SectionHeader = ({ id, title, icon }: { id: string; title: string; icon: React.ReactNode }) => (
    <button
      onClick={() => toggleSection(id)}
      className="w-full flex items-center justify-between p-3 bg-[#1a1a24] rounded-lg hover:bg-[#22222e] transition-colors"
    >
      <div className="flex items-center gap-3">
        {icon}
        <span className="font-semibold text-[#e0e0e0]" style={{ fontFamily: 'Rajdhani, sans-serif' }}>
          {title}
        </span>
      </div>
      {expandedSections.has(id) ? <ChevronDown size={18} /> : <ChevronRight size={18} />}
    </button>
  );

  return (
    <div className="space-y-4">
      {/* Overview */}
      <div>
        <SectionHeader id="overview" title="Quality Overview" icon={<Target size={18} className="text-[#00f5ff]" />} />
        {expandedSections.has('overview') && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            className="mt-2 p-4 bg-[#12121a] rounded-lg border border-[#2a2a3a]"
          >
            <div className="flex flex-col md:flex-row items-center gap-6">
              {/* Score Ring */}
              <ScoreRing 
                score={result.quality_score.total} 
                grade={result.quality_score.grade}
              />
              
              {/* Score Breakdown */}
              <div className="flex-1 space-y-3">
                <div className="text-sm text-[#888899] mb-2">Score Breakdown</div>
                {Object.entries(result.quality_score.breakdown).map(([key, value]) => (
                  <div key={key} className="flex items-center gap-3">
                    <span className="w-24 text-xs text-[#888899] capitalize">{key}</span>
                    <div className="flex-1 h-2 bg-[#2a2a3a] rounded-full overflow-hidden">
                      <div 
                        className="h-full bg-gradient-to-r from-[#00f5ff] to-[#ff00ff] rounded-full transition-all duration-500"
                        style={{ width: `${(value as number / (key === 'completeness' ? 30 : key === 'validity' ? 25 : key === 'uniqueness' ? 20 : key === 'consistency' ? 15 : 10)) * 100}%` }}
                      />
                    </div>
                    <span className="text-xs text-[#e0e0e0] w-10 text-right">{(value as number).toFixed(1)}</span>
                  </div>
                ))}
              </div>

              {/* Quick Stats */}
              <div className="grid grid-cols-2 gap-3">
                <div className="text-center p-3 bg-[#1a1a24] rounded-lg">
                  <div className="text-xl font-bold text-[#00f5ff]" style={{ fontFamily: 'Orbitron, monospace' }}>
                    {result.row_count.toLocaleString()}
                  </div>
                  <div className="text-xs text-[#888899]">Rows</div>
                </div>
                <div className="text-center p-3 bg-[#1a1a24] rounded-lg">
                  <div className="text-xl font-bold text-[#ff00ff]" style={{ fontFamily: 'Orbitron, monospace' }}>
                    {result.column_count}
                  </div>
                  <div className="text-xs text-[#888899]">Columns</div>
                </div>
                <div className="text-center p-3 bg-[#1a1a24] rounded-lg">
                  <div className="text-xl font-bold text-[#39ff14]" style={{ fontFamily: 'Orbitron, monospace' }}>
                    {result.completeness.overall_completeness.toFixed(1)}%
                  </div>
                  <div className="text-xs text-[#888899]">Complete</div>
                </div>
                <div className="text-center p-3 bg-[#1a1a24] rounded-lg">
                  <div className="text-xl font-bold text-[#f0ff00]" style={{ fontFamily: 'Orbitron, monospace' }}>
                    {result.uniqueness.duplicate_row_count}
                  </div>
                  <div className="text-xs text-[#888899]">Duplicates</div>
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </div>

      {/* Completeness */}
      <div>
        <SectionHeader id="completeness" title="Completeness Analysis" icon={<CheckCircle2 size={18} className="text-[#39ff14]" />} />
        {expandedSections.has('completeness') && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            className="mt-2 p-4 bg-[#12121a] rounded-lg border border-[#2a2a3a]"
          >
            <div className="grid grid-cols-3 gap-4 mb-4">
              <div className="text-center p-3 bg-[#1a1a24] rounded-lg">
                <div className="text-lg font-bold text-[#39ff14]">{result.completeness.complete_columns.length}</div>
                <div className="text-xs text-[#888899]">Complete Columns</div>
              </div>
              <div className="text-center p-3 bg-[#1a1a24] rounded-lg">
                <div className="text-lg font-bold text-[#f0ff00]">{result.completeness.high_null_columns.length}</div>
                <div className="text-xs text-[#888899]">High Null Columns</div>
              </div>
              <div className="text-center p-3 bg-[#1a1a24] rounded-lg">
                <div className="text-lg font-bold text-[#ff0080]">{result.completeness.empty_columns.length}</div>
                <div className="text-xs text-[#888899]">Empty Columns</div>
              </div>
            </div>
            
            {result.completeness.high_null_columns.length > 0 && (
              <div className="space-y-2">
                <div className="text-sm text-[#888899]">Columns with High Null %:</div>
                {result.completeness.high_null_columns.map(col => {
                  const info = result.completeness.column_completeness[col];
                  return (
                    <div key={col} className="flex items-center gap-3 p-2 bg-[#1a1a24] rounded">
                      <span className="flex-1 text-sm text-[#e0e0e0]">{col}</span>
                      <div className="w-32 h-2 bg-[#2a2a3a] rounded-full overflow-hidden">
                        <div 
                          className="h-full bg-[#f0ff00] rounded-full"
                          style={{ width: `${100 - info.null_percentage}%` }}
                        />
                      </div>
                      <span className="text-xs text-[#f0ff00] w-16 text-right">{info.null_percentage}% null</span>
                    </div>
                  );
                })}
              </div>
            )}
          </motion.div>
        )}
      </div>

      {/* Uniqueness */}
      <div>
        <SectionHeader id="uniqueness" title="Uniqueness & Duplicates" icon={<BarChart2 size={18} className="text-[#ff00ff]" />} />
        {expandedSections.has('uniqueness') && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            className="mt-2 p-4 bg-[#12121a] rounded-lg border border-[#2a2a3a]"
          >
            <div className="grid grid-cols-2 gap-4 mb-4">
              <div className="p-3 bg-[#1a1a24] rounded-lg">
                <div className="text-lg font-bold text-[#ff00ff]">
                  {result.uniqueness.duplicate_row_count.toLocaleString()}
                </div>
                <div className="text-xs text-[#888899]">Duplicate Rows ({result.uniqueness.duplicate_row_percentage.toFixed(1)}%)</div>
              </div>
              <div className="p-3 bg-[#1a1a24] rounded-lg">
                <div className="text-lg font-bold text-[#00f5ff]">
                  {result.uniqueness.potential_id_columns.length}
                </div>
                <div className="text-xs text-[#888899]">Potential ID Columns</div>
              </div>
            </div>

            {result.uniqueness.potential_id_columns.length > 0 && (
              <div className="mb-4">
                <div className="text-sm text-[#888899] mb-2">Potential ID Columns (High Uniqueness):</div>
                <div className="flex flex-wrap gap-2">
                  {result.uniqueness.potential_id_columns.map(col => (
                    <span key={col} className="px-2 py-1 bg-[#00f5ff]/20 text-[#00f5ff] text-xs rounded border border-[#00f5ff]/30">
                      {col}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {result.uniqueness.categorical_columns.length > 0 && (
              <div>
                <div className="text-sm text-[#888899] mb-2">Categorical Columns (Low Cardinality):</div>
                <div className="flex flex-wrap gap-2">
                  {result.uniqueness.categorical_columns.map(col => (
                    <span key={col} className="px-2 py-1 bg-[#f0ff00]/20 text-[#f0ff00] text-xs rounded border border-[#f0ff00]/30">
                      {col}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </motion.div>
        )}
      </div>

      {/* Outliers */}
      {result.outliers.columns_with_outliers > 0 && (
        <div>
          <SectionHeader id="outliers" title="Outlier Analysis" icon={<TrendingUp size={18} className="text-[#f0ff00]" />} />
          {expandedSections.has('outliers') && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              className="mt-2 p-4 bg-[#12121a] rounded-lg border border-[#2a2a3a]"
            >
              <div className="text-sm text-[#888899] mb-3">
                {result.outliers.columns_with_outliers} column(s) with outliers detected:
              </div>
              <div className="space-y-3">
                {Object.entries(result.outliers.column_outliers).map(([col, info]) => (
                  <div key={col} className="p-3 bg-[#1a1a24] rounded-lg">
                    <div className="flex justify-between items-center mb-2">
                      <span className="font-semibold text-[#e0e0e0]">{col}</span>
                      <span className="text-xs text-[#f0ff00]">
                        {info.outlier_count} outliers ({info.outlier_percentage.toFixed(1)}%)
                      </span>
                    </div>
                    <div className="grid grid-cols-4 gap-2 text-xs">
                      <div className="text-[#888899]">
                        Min: <span className="text-[#e0e0e0]">{info.statistics.min.toFixed(2)}</span>
                      </div>
                      <div className="text-[#888899]">
                        Max: <span className="text-[#e0e0e0]">{info.statistics.max.toFixed(2)}</span>
                      </div>
                      <div className="text-[#888899]">
                        Mean: <span className="text-[#e0e0e0]">{info.statistics.mean.toFixed(2)}</span>
                      </div>
                      <div className="text-[#888899]">
                        Std: <span className="text-[#e0e0e0]">{info.statistics.std.toFixed(2)}</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </motion.div>
          )}
        </div>
      )}

      {/* Recommendations */}
      {result.recommendations.length > 0 && (
        <div>
          <SectionHeader id="recommendations" title="Recommendations" icon={<Zap size={18} className="text-[#00f5ff]" />} />
          {expandedSections.has('recommendations') && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              className="mt-2 p-4 bg-[#12121a] rounded-lg border border-[#2a2a3a]"
            >
              <div className="space-y-2">
                {result.recommendations.map((rec, idx) => (
                  <div 
                    key={idx}
                    className={`p-3 rounded-lg border ${
                      rec.priority === 'high' 
                        ? 'bg-[#ff0080]/10 border-[#ff0080]/30' 
                        : rec.priority === 'medium'
                        ? 'bg-[#f0ff00]/10 border-[#f0ff00]/30'
                        : 'bg-[#00f5ff]/10 border-[#00f5ff]/30'
                    }`}
                  >
                    <div className="flex items-start gap-2">
                      {rec.priority === 'high' && <AlertTriangle size={16} className="text-[#ff0080] mt-0.5" />}
                      {rec.priority === 'medium' && <AlertTriangle size={16} className="text-[#f0ff00] mt-0.5" />}
                      {rec.priority === 'low' && <CheckCircle2 size={16} className="text-[#00f5ff] mt-0.5" />}
                      <div>
                        <div className="text-sm text-[#e0e0e0]">{rec.message}</div>
                        {rec.action && (
                          <div className="text-xs text-[#888899] mt-1">{rec.action}</div>
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

export function QualityDashboard({ result }: QualityDashboardProps) {
  const [selectedDataset, setSelectedDataset] = useState<string | null>(null);

  if (isMultiQualityResult(result)) {
    const datasets = Object.keys(result.individual_results);
    const currentDataset = selectedDataset || datasets[0];
    const currentResult = result.individual_results[currentDataset];

    return (
      <div className="space-y-4">
        {/* Multi-dataset overview */}
        <div className="p-4 bg-[#12121a] rounded-lg border border-[#2a2a3a]">
          <div className="text-sm text-[#888899] mb-3">Multi-Dataset Quality Comparison</div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
            <div className="text-center p-3 bg-[#1a1a24] rounded-lg">
              <div className="text-2xl font-bold text-[#00f5ff]" style={{ fontFamily: 'Orbitron, monospace' }}>
                {result.overall_summary.dataset_count}
              </div>
              <div className="text-xs text-[#888899]">Datasets</div>
            </div>
            <div className="text-center p-3 bg-[#1a1a24] rounded-lg">
              <div className="text-2xl font-bold text-[#ff00ff]" style={{ fontFamily: 'Orbitron, monospace' }}>
                {result.overall_summary.total_rows.toLocaleString()}
              </div>
              <div className="text-xs text-[#888899]">Total Rows</div>
            </div>
            <div className="text-center p-3 bg-[#1a1a24] rounded-lg">
              <div className="text-2xl font-bold text-[#39ff14]" style={{ fontFamily: 'Orbitron, monospace' }}>
                {result.overall_summary.average_quality_score.toFixed(0)}
              </div>
              <div className="text-xs text-[#888899]">Avg Score</div>
            </div>
            <div className="text-center p-3 bg-[#1a1a24] rounded-lg">
              <div className="text-2xl font-bold text-[#f0ff00]" style={{ fontFamily: 'Orbitron, monospace' }}>
                {result.comparison.best_quality}
              </div>
              <div className="text-xs text-[#888899]">Best Quality</div>
            </div>
          </div>

          {/* Dataset selector */}
          <div className="flex gap-2 flex-wrap">
            {datasets.map(name => (
              <button
                key={name}
                onClick={() => setSelectedDataset(name)}
                className={`px-4 py-2 rounded border transition-all ${
                  currentDataset === name
                    ? 'bg-[#00f5ff] text-[#0a0a0f] border-[#00f5ff] font-bold'
                    : 'bg-transparent text-[#e0e0e0] border-[#2a2a3a] hover:border-[#00f5ff]'
                }`}
                style={{ fontFamily: 'JetBrains Mono, monospace' }}
              >
                {name} ({result.comparison.scores[name].toFixed(0)})
              </button>
            ))}
          </div>
        </div>

        {/* Individual dataset view */}
        <SingleQualityView result={currentResult} />
      </div>
    );
  }

  return <SingleQualityView result={result} />;
}

export default QualityDashboard;

