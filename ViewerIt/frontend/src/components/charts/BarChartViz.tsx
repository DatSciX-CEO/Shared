/**
 * BarChartViz - Cyberpunk styled bar chart using Recharts
 */
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';

interface BarChartData {
  name: string;
  value: number;
  color?: string;
}

interface BarChartVizProps {
  data: BarChartData[];
  height?: number;
  xAxisLabel?: string;
  yAxisLabel?: string;
  showGrid?: boolean;
  gradientColors?: [string, string];
}

// Cyberpunk color palette
const CYBER_COLORS = ['#00f5ff', '#ff00ff', '#f0ff00', '#39ff14', '#ff0080', '#ff6600'];

export function BarChartViz({ 
  data, 
  height = 300,
  xAxisLabel,
  yAxisLabel,
  showGrid = true,
  gradientColors = ['#00f5ff', '#ff00ff']
}: BarChartVizProps) {
  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div 
          className="px-3 py-2 rounded border border-[#00f5ff]/50"
          style={{ 
            background: 'rgba(10, 10, 15, 0.95)',
            fontFamily: 'JetBrains Mono, monospace',
            boxShadow: '0 0 10px rgba(0, 245, 255, 0.3)'
          }}
        >
          <p className="text-[#00f5ff] text-sm font-bold">{label}</p>
          <p className="text-[#e0e0e0] text-xs">
            Value: <span className="text-[#ff00ff]">{payload[0].value.toLocaleString()}</span>
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <ResponsiveContainer width="100%" height={height}>
      <BarChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
        <defs>
          <linearGradient id="barGradient" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor={gradientColors[0]} stopOpacity={0.9}/>
            <stop offset="100%" stopColor={gradientColors[1]} stopOpacity={0.7}/>
          </linearGradient>
        </defs>
        {showGrid && (
          <CartesianGrid 
            strokeDasharray="3 3" 
            stroke="#2a2a3a" 
            vertical={false}
          />
        )}
        <XAxis 
          dataKey="name" 
          stroke="#888899"
          tick={{ fill: '#888899', fontSize: 11, fontFamily: 'Rajdhani, sans-serif' }}
          axisLine={{ stroke: '#2a2a3a' }}
          label={xAxisLabel ? { value: xAxisLabel, position: 'bottom', fill: '#888899', fontSize: 12 } : undefined}
        />
        <YAxis 
          stroke="#888899"
          tick={{ fill: '#888899', fontSize: 11, fontFamily: 'JetBrains Mono, monospace' }}
          axisLine={{ stroke: '#2a2a3a' }}
          tickFormatter={(value) => value.toLocaleString()}
          label={yAxisLabel ? { value: yAxisLabel, angle: -90, position: 'insideLeft', fill: '#888899', fontSize: 12 } : undefined}
        />
        <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(0, 245, 255, 0.1)' }} />
        <Bar 
          dataKey="value" 
          fill="url(#barGradient)"
          radius={[4, 4, 0, 0]}
        >
          {data.map((entry, index) => (
            <Cell 
              key={`cell-${index}`} 
              fill={entry.color || CYBER_COLORS[index % CYBER_COLORS.length]}
              style={{ filter: 'drop-shadow(0 0 6px currentColor)' }}
            />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}

export default BarChartViz;

