/**
 * DataTable Component - Cyberpunk styled data grid
 */
import { motion } from 'framer-motion';
import { useState } from 'react';
import { ChevronLeft, ChevronRight } from 'lucide-react';

interface DataTableProps {
  columns: string[];
  data: Record<string, unknown>[];
  pageSize?: number;
  highlightColumns?: string[];
}

export function DataTable({ 
  columns, 
  data, 
  pageSize = 25,
  highlightColumns = []
}: DataTableProps) {
  const [page, setPage] = useState(0);
  const totalPages = Math.ceil(data.length / pageSize);
  const displayData = data.slice(page * pageSize, (page + 1) * pageSize);

  const formatValue = (value: unknown): string => {
    if (value === null || value === undefined) return '—';
    if (typeof value === 'object') return JSON.stringify(value);
    return String(value);
  };

  return (
    <div className="overflow-hidden rounded-lg border border-[#2a2a3a]">
      {/* Table Container */}
      <div className="overflow-x-auto max-h-[500px] overflow-y-auto">
        <table className="data-grid w-full">
          <thead className="sticky top-0 z-10">
            <tr>
              {columns.map((col, idx) => (
                <th 
                  key={col}
                  className={`
                    whitespace-nowrap
                    ${highlightColumns.includes(col) ? 'text-[#ff0080]!' : ''}
                  `}
                  style={{
                    color: highlightColumns.includes(col) ? '#ff0080' : undefined,
                  }}
                >
                  <motion.span
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: idx * 0.02 }}
                  >
                    {col}
                  </motion.span>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {displayData.map((row, rowIdx) => (
              <motion.tr
                key={rowIdx}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: rowIdx * 0.01 }}
              >
                {columns.map((col) => (
                  <td 
                    key={col}
                    className={`
                      whitespace-nowrap max-w-[300px] truncate
                      ${highlightColumns.includes(col) ? 'bg-[#ff0080]/10' : ''}
                    `}
                    title={formatValue(row[col])}
                  >
                    {formatValue(row[col])}
                  </td>
                ))}
              </motion.tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between px-4 py-3 bg-[#12121a] border-t border-[#2a2a3a]">
          <span 
            className="text-sm text-[#888899]"
            style={{ fontFamily: 'JetBrains Mono, monospace' }}
          >
            Showing {page * pageSize + 1}-{Math.min((page + 1) * pageSize, data.length)} of {data.length}
          </span>
          
          <div className="flex items-center gap-2">
            <button
              onClick={() => setPage(p => Math.max(0, p - 1))}
              disabled={page === 0}
              className={`
                p-2 rounded transition-colors
                ${page === 0 
                  ? 'text-[#555566] cursor-not-allowed' 
                  : 'text-[#00f5ff] hover:bg-[#00f5ff]/10'
                }
              `}
            >
              <ChevronLeft size={20} />
            </button>
            
            <span 
              className="px-3 py-1 text-sm text-[#e0e0e0]"
              style={{ fontFamily: 'Orbitron, monospace' }}
            >
              {page + 1} / {totalPages}
            </span>
            
            <button
              onClick={() => setPage(p => Math.min(totalPages - 1, p + 1))}
              disabled={page === totalPages - 1}
              className={`
                p-2 rounded transition-colors
                ${page === totalPages - 1 
                  ? 'text-[#555566] cursor-not-allowed' 
                  : 'text-[#00f5ff] hover:bg-[#00f5ff]/10'
                }
              `}
            >
              <ChevronRight size={20} />
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export default DataTable;

