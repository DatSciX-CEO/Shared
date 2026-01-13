/**
 * PieChartViz - Cyberpunk styled pie/donut chart using Recharts
 */
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts';

interface PieChartData {
  name: string;
  value: number;
  color?: string;
}

interface PieChartVizProps {
  data: PieChartData[];
  height?: number;
  innerRadius?: number;
  outerRadius?: number;
  showLegend?: boolean;
  showLabels?: boolean;
}

// Cyberpunk color palette
const CYBER_COLORS = ['#00f5ff', '#ff00ff', '#f0ff00', '#39ff14', '#ff0080', '#ff6600'];

export function PieChartViz({ 
  data, 
  height = 300,
  innerRadius = 60,
  outerRadius = 100,
  showLegend = true,
  showLabels = false
}: PieChartVizProps) {
  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const item = payload[0];
      const total = data.reduce((sum, d) => sum + d.value, 0);
      const percentage = ((item.value / total) * 100).toFixed(1);
      
      return (
        <div 
          className="px-3 py-2 rounded border border-[#00f5ff]/50"
          style={{ 
            background: 'rgba(10, 10, 15, 0.95)',
            fontFamily: 'JetBrains Mono, monospace',
            boxShadow: '0 0 10px rgba(0, 245, 255, 0.3)'
          }}
        >
          <p className="text-sm font-bold" style={{ color: item.payload.fill }}>{item.name}</p>
          <p className="text-[#e0e0e0] text-xs">
            Count: <span className="text-[#ff00ff]">{item.value.toLocaleString()}</span>
          </p>
          <p className="text-[#e0e0e0] text-xs">
            Share: <span className="text-[#00f5ff]">{percentage}%</span>
          </p>
        </div>
      );
    }
    return null;
  };

  const renderCustomLabel = ({ cx, cy, midAngle, innerRadius, outerRadius, percent, name }: any) => {
    if (percent < 0.05) return null; // Don't show labels for small segments
    
    const RADIAN = Math.PI / 180;
    const radius = innerRadius + (outerRadius - innerRadius) * 1.4;
    const x = cx + radius * Math.cos(-midAngle * RADIAN);
    const y = cy + radius * Math.sin(-midAngle * RADIAN);

    return (
      <text 
        x={x} 
        y={y} 
        fill="#e0e0e0" 
        textAnchor={x > cx ? 'start' : 'end'} 
        dominantBaseline="central"
        style={{ fontSize: '11px', fontFamily: 'Rajdhani, sans-serif' }}
      >
        {`${name} (${(percent * 100).toFixed(0)}%)`}
      </text>
    );
  };

  const CustomLegend = ({ payload }: any) => (
    <div className="flex flex-wrap justify-center gap-4 mt-4">
      {payload.map((entry: any, index: number) => (
        <div key={`legend-${index}`} className="flex items-center gap-2">
          <div 
            className="w-3 h-3 rounded-sm"
            style={{ 
              backgroundColor: entry.color,
              boxShadow: `0 0 6px ${entry.color}`
            }}
          />
          <span 
            className="text-xs text-[#e0e0e0]"
            style={{ fontFamily: 'Rajdhani, sans-serif' }}
          >
            {entry.value}
          </span>
        </div>
      ))}
    </div>
  );

  return (
    <ResponsiveContainer width="100%" height={height}>
      <PieChart>
        <defs>
          {data.map((_, index) => (
            <filter key={`glow-${index}`} id={`glow-${index}`}>
              <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
              <feMerge>
                <feMergeNode in="coloredBlur"/>
                <feMergeNode in="SourceGraphic"/>
              </feMerge>
            </filter>
          ))}
        </defs>
        <Pie
          data={data as any}
          cx="50%"
          cy="50%"
          innerRadius={innerRadius}
          outerRadius={outerRadius}
          paddingAngle={2}
          dataKey="value"
          label={showLabels ? renderCustomLabel : false}
          labelLine={showLabels}
          strokeWidth={2}
          stroke="#0a0a0f"
        >
          {data.map((entry, index) => (
            <Cell 
              key={`cell-${index}`} 
              fill={entry.color || CYBER_COLORS[index % CYBER_COLORS.length]}
              style={{ filter: `drop-shadow(0 0 8px ${entry.color || CYBER_COLORS[index % CYBER_COLORS.length]})` }}
            />
          ))}
        </Pie>
        <Tooltip content={<CustomTooltip />} />
        {showLegend && <Legend content={<CustomLegend />} />}
      </PieChart>
    </ResponsiveContainer>
  );
}

export default PieChartViz;

