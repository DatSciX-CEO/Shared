/**
 * Schema Viewer Component - Displays schema analysis results
 * Shows column alignment, type compatibility, and mapping suggestions
 */
import { motion } from 'framer-motion';
import { 
  Columns3, 
  AlertTriangle, 
  CheckCircle2, 
  XCircle, 
  Link2,
  ChevronDown,
  ChevronRight
} from 'lucide-react';
import { useState } from 'react';
import type { SchemaAnalysisResult } from '../hooks/useApi';

interface SchemaViewerProps {
  result: SchemaAnalysisResult;
}

export function SchemaViewer({ result }: SchemaViewerProps) {
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set(['summary', 'alignment']));

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
          title="Schema Summary" 
          icon={<Columns3 size={18} className="text-[#00f5ff]" />}
        />
        {expandedSections.has('summary') && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            className="mt-2 p-4 bg-[#12121a] rounded-lg border border-[#2a2a3a]"
          >
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center p-3 bg-[#1a1a24] rounded-lg">
                <div className="text-2xl font-bold text-[#00f5ff]" style={{ fontFamily: 'Orbitron, monospace' }}>
                  {result.summary.file_count}
                </div>
                <div className="text-xs text-[#888899] uppercase tracking-wider">Files</div>
              </div>
              <div className="text-center p-3 bg-[#1a1a24] rounded-lg">
                <div className="text-2xl font-bold text-[#ff00ff]" style={{ fontFamily: 'Orbitron, monospace' }}>
                  {result.summary.total_unique_columns}
                </div>
                <div className="text-xs text-[#888899] uppercase tracking-wider">Total Columns</div>
              </div>
              <div className="text-center p-3 bg-[#1a1a24] rounded-lg">
                <div className="text-2xl font-bold text-[#39ff14]" style={{ fontFamily: 'Orbitron, monospace' }}>
                  {result.summary.columns_in_all_files}
                </div>
                <div className="text-xs text-[#888899] uppercase tracking-wider">Common</div>
              </div>
              <div className="text-center p-3 bg-[#1a1a24] rounded-lg">
                <div className={`text-2xl font-bold ${result.summary.schema_compatibility === 'compatible' ? 'text-[#39ff14]' : 'text-[#ff0080]'}`} style={{ fontFamily: 'Orbitron, monospace' }}>
                  {result.summary.schema_compatibility === 'compatible' ? 'OK' : 'ISSUES'}
                </div>
                <div className="text-xs text-[#888899] uppercase tracking-wider">Compatibility</div>
              </div>
            </div>

            {/* Issue counts */}
            {result.summary.issue_count.total > 0 && (
              <div className="mt-4 flex gap-4 justify-center">
                {result.summary.issue_count.high > 0 && (
                  <div className="flex items-center gap-2 text-[#ff0080]">
                    <XCircle size={16} />
                    <span className="text-sm">{result.summary.issue_count.high} High Severity</span>
                  </div>
                )}
                {result.summary.issue_count.medium > 0 && (
                  <div className="flex items-center gap-2 text-[#f0ff00]">
                    <AlertTriangle size={16} />
                    <span className="text-sm">{result.summary.issue_count.medium} Medium</span>
                  </div>
                )}
              </div>
            )}
          </motion.div>
        )}
      </div>

      {/* Column Alignment */}
      <div>
        <SectionHeader 
          id="alignment" 
          title="Column Alignment" 
          icon={<Columns3 size={18} className="text-[#ff00ff]" />}
          count={result.column_alignment.all_columns.length}
        />
        {expandedSections.has('alignment') && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            className="mt-2 p-4 bg-[#12121a] rounded-lg border border-[#2a2a3a]"
          >
            {/* Columns in all files */}
            {result.column_alignment.columns_in_all_files.length > 0 && (
              <div className="mb-4">
                <div className="flex items-center gap-2 mb-2">
                  <CheckCircle2 size={16} className="text-[#39ff14]" />
                  <span className="text-sm font-semibold text-[#e0e0e0]">
                    Columns in ALL files ({result.column_alignment.columns_in_all_files.length})
                  </span>
                </div>
                <div className="flex flex-wrap gap-2">
                  {result.column_alignment.columns_in_all_files.map(col => (
                    <span key={col} className="px-2 py-1 bg-[#39ff14]/20 text-[#39ff14] text-xs rounded border border-[#39ff14]/30">
                      {col}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Columns in some files */}
            {Object.keys(result.column_alignment.columns_in_some_files).length > 0 && (
              <div className="mb-4">
                <div className="flex items-center gap-2 mb-2">
                  <AlertTriangle size={16} className="text-[#f0ff00]" />
                  <span className="text-sm font-semibold text-[#e0e0e0]">
                    Columns in SOME files ({Object.keys(result.column_alignment.columns_in_some_files).length})
                  </span>
                </div>
                <div className="space-y-1">
                  {Object.entries(result.column_alignment.columns_in_some_files).map(([col, files]) => (
                    <div key={col} className="flex items-center gap-2 text-sm">
                      <span className="px-2 py-1 bg-[#f0ff00]/20 text-[#f0ff00] text-xs rounded border border-[#f0ff00]/30">
                        {col}
                      </span>
                      <span className="text-[#888899]">→</span>
                      <span className="text-[#e0e0e0]">{files.join(', ')}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* File-unique columns */}
            {Object.entries(result.column_alignment.file_unique_columns).some(([, cols]) => cols.length > 0) && (
              <div>
                <div className="flex items-center gap-2 mb-2">
                  <XCircle size={16} className="text-[#ff0080]" />
                  <span className="text-sm font-semibold text-[#e0e0e0]">File-Unique Columns</span>
                </div>
                <div className="space-y-2">
                  {Object.entries(result.column_alignment.file_unique_columns).map(([file, cols]) => 
                    cols.length > 0 && (
                      <div key={file} className="text-sm">
                        <span className="text-[#888899]">{file}:</span>
                        <div className="flex flex-wrap gap-1 mt-1">
                          {cols.map(col => (
                            <span key={col} className="px-2 py-0.5 bg-[#ff0080]/20 text-[#ff0080] text-xs rounded">
                              {col}
                            </span>
                          ))}
                        </div>
                      </div>
                    )
                  )}
                </div>
              </div>
            )}
          </motion.div>
        )}
      </div>

      {/* Type Compatibility */}
      <div>
        <SectionHeader 
          id="types" 
          title="Type Compatibility" 
          icon={<CheckCircle2 size={18} className="text-[#39ff14]" />}
          count={result.type_compatibility.incompatible_columns.length > 0 
            ? result.type_compatibility.incompatible_columns.length 
            : undefined}
        />
        {expandedSections.has('types') && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            className="mt-2 p-4 bg-[#12121a] rounded-lg border border-[#2a2a3a]"
          >
            {result.type_compatibility.incompatible_columns.length > 0 ? (
              <div className="space-y-3">
                <div className="text-sm text-[#ff0080] mb-2">
                  ⚠️ {result.type_compatibility.incompatible_columns.length} column(s) have type mismatches:
                </div>
                {result.type_compatibility.incompatible_columns.map(col => {
                  const typeInfo = result.type_compatibility.column_types[col];
                  return (
                    <div key={col} className="p-3 bg-[#ff0080]/10 border border-[#ff0080]/30 rounded-lg">
                      <div className="font-semibold text-[#ff0080] mb-2">{col}</div>
                      <div className="grid grid-cols-2 md:grid-cols-3 gap-2 text-xs">
                        {Object.entries(typeInfo?.types || {}).map(([file, type]) => (
                          <div key={file} className="flex justify-between">
                            <span className="text-[#888899]">{file}:</span>
                            <span className="text-[#e0e0e0] font-mono">{type}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  );
                })}
              </div>
            ) : (
              <div className="text-center py-4">
                <CheckCircle2 size={32} className="mx-auto text-[#39ff14] mb-2" />
                <div className="text-[#39ff14]">All column types are compatible!</div>
              </div>
            )}
          </motion.div>
        )}
      </div>

      {/* Mapping Suggestions */}
      {result.mapping_suggestions.suggestions.length > 0 && (
        <div>
          <SectionHeader 
            id="mappings" 
            title="Column Mapping Suggestions" 
            icon={<Link2 size={18} className="text-[#f0ff00]" />}
            count={result.mapping_suggestions.suggestions.length}
          />
          {expandedSections.has('mappings') && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              className="mt-2 p-4 bg-[#12121a] rounded-lg border border-[#2a2a3a]"
            >
              <div className="space-y-2">
                {result.mapping_suggestions.suggestions.slice(0, 10).map((suggestion, idx) => (
                  <div key={idx} className="flex items-center gap-3 p-2 bg-[#1a1a24] rounded">
                    <div className="flex-1 text-right">
                      <span className="text-xs text-[#888899]">{suggestion.file1}:</span>
                      <span className="ml-1 text-[#00f5ff]">{suggestion.column1}</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <Link2 size={14} className="text-[#f0ff00]" />
                      <span className="text-xs text-[#f0ff00]">
                        {Math.round(suggestion.similarity_score * 100)}%
                      </span>
                    </div>
                    <div className="flex-1">
                      <span className="text-xs text-[#888899]">{suggestion.file2}:</span>
                      <span className="ml-1 text-[#ff00ff]">{suggestion.column2}</span>
                    </div>
                  </div>
                ))}
              </div>
            </motion.div>
          )}
        </div>
      )}

      {/* Issues */}
      {result.issues.length > 0 && (
        <div>
          <SectionHeader 
            id="issues" 
            title="Issues & Warnings" 
            icon={<AlertTriangle size={18} className="text-[#ff0080]" />}
            count={result.issues.length}
          />
          {expandedSections.has('issues') && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              className="mt-2 p-4 bg-[#12121a] rounded-lg border border-[#2a2a3a]"
            >
              <div className="space-y-2">
                {result.issues.map((issue, idx) => (
                  <div 
                    key={idx} 
                    className={`p-3 rounded-lg border ${
                      issue.severity === 'high' 
                        ? 'bg-[#ff0080]/10 border-[#ff0080]/30' 
                        : 'bg-[#f0ff00]/10 border-[#f0ff00]/30'
                    }`}
                  >
                    <div className="flex items-start gap-2">
                      {issue.severity === 'high' 
                        ? <XCircle size={16} className="text-[#ff0080] mt-0.5" />
                        : <AlertTriangle size={16} className="text-[#f0ff00] mt-0.5" />
                      }
                      <div>
                        <div className={`text-sm font-semibold ${issue.severity === 'high' ? 'text-[#ff0080]' : 'text-[#f0ff00]'}`}>
                          {issue.message}
                        </div>
                        {issue.column && (
                          <div className="text-xs text-[#888899] mt-1">Column: {issue.column}</div>
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

export default SchemaViewer;

