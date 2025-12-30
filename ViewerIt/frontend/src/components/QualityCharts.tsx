/**
 * QualityCharts - Native Recharts visualizations for data quality metrics
 */
import { BarChartViz, PieChartViz } from './charts';
import type { QualityCheckResult } from '../hooks/useApi';

interface QualityChartsProps {
  result: QualityCheckResult;
}

export function QualityCharts({ result }: QualityChartsProps) {
  // Prepare null percentage data for bar chart
  const nullPercentageData = Object.entries(result.completeness.column_completeness)
    .filter(([_, info]) => info.null_percentage > 0)
    .sort((a, b) => b[1].null_percentage - a[1].null_percentage)
    .slice(0, 10)
    .map(([col, info]) => ({
      name: col.length > 12 ? col.slice(0, 12) + '...' : col,
      value: info.null_percentage,
      color: info.null_percentage > 50 ? '#ff0080' : info.null_percentage > 20 ? '#f0ff00' : '#00f5ff'
    }));

  // Prepare completeness pie chart data
  const completenessData = [
    { 
      name: 'Complete Columns', 
      value: result.completeness.complete_columns.length, 
      color: '#39ff14' 
    },
    { 
      name: 'High Null Columns', 
      value: result.completeness.high_null_columns.length, 
      color: '#f0ff00' 
    },
    { 
      name: 'Empty Columns', 
      value: result.completeness.empty_columns.length, 
      color: '#ff0080' 
    },
  ].filter(d => d.value > 0);

  // Prepare uniqueness data
  const uniquenessData = [
    { 
      name: 'Unique Rows', 
      value: result.row_count - result.uniqueness.duplicate_row_count, 
      color: '#39ff14' 
    },
    { 
      name: 'Duplicate Rows', 
      value: result.uniqueness.duplicate_row_count, 
      color: '#ff0080' 
    },
  ].filter(d => d.value > 0);

  // Quality breakdown bar chart data
  const qualityBreakdownData = Object.entries(result.quality_score.breakdown).map(([key, value]) => ({
    name: key.charAt(0).toUpperCase() + key.slice(1),
    value: value as number,
    color: (value as number) > 20 ? '#39ff14' : (value as number) > 10 ? '#f0ff00' : '#ff0080'
  }));

  return (
    <div className="grid grid-cols-2 gap-6">
      {/* Completeness Distribution */}
      {completenessData.length > 1 && (
        <div className="cyber-card">
          <h4 
            className="text-xs uppercase tracking-wider text-[#00f5ff] mb-4"
            style={{ fontFamily: 'Orbitron, monospace' }}
          >
            Column Completeness
          </h4>
          <PieChartViz 
            data={completenessData} 
            height={220}
            innerRadius={40}
            outerRadius={70}
          />
        </div>
      )}

      {/* Uniqueness Distribution */}
      {uniquenessData.length > 1 && (
        <div className="cyber-card">
          <h4 
            className="text-xs uppercase tracking-wider text-[#ff00ff] mb-4"
            style={{ fontFamily: 'Orbitron, monospace' }}
          >
            Row Uniqueness
          </h4>
          <PieChartViz 
            data={uniquenessData} 
            height={220}
            innerRadius={40}
            outerRadius={70}
          />
        </div>
      )}

      {/* Null Percentage by Column */}
      {nullPercentageData.length > 0 && (
        <div className="cyber-card col-span-2">
          <h4 
            className="text-xs uppercase tracking-wider text-[#f0ff00] mb-4"
            style={{ fontFamily: 'Orbitron, monospace' }}
          >
            Null Percentage by Column (Top 10)
          </h4>
          <BarChartViz 
            data={nullPercentageData} 
            height={200}
            yAxisLabel="Null %"
          />
        </div>
      )}

      {/* Quality Score Breakdown */}
      <div className="cyber-card col-span-2">
        <h4 
          className="text-xs uppercase tracking-wider text-[#39ff14] mb-4"
          style={{ fontFamily: 'Orbitron, monospace' }}
        >
          Quality Score Breakdown
        </h4>
        <BarChartViz 
          data={qualityBreakdownData} 
          height={200}
          yAxisLabel="Score"
        />
      </div>
    </div>
  );
}

export default QualityCharts;

