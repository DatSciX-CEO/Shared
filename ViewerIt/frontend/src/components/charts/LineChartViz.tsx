/**
 * LineChartViz - Cyberpunk styled line/area chart using Recharts
 */
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Area, AreaChart } from 'recharts';

interface LineChartData {
  name: string;
  value: number;
  value2?: number;
}

interface LineChartVizProps {
  data: LineChartData[];
  height?: number;
  showArea?: boolean;
  showDots?: boolean;
  lineColor?: string;
  areaColor?: string;
  secondLineColor?: string;
  showSecondLine?: boolean;
}

export function LineChartViz({ 
  data, 
  height = 300,
  showArea = true,
  showDots = true,
  lineColor = '#00f5ff',
  areaColor = '#00f5ff',
  secondLineColor = '#ff00ff',
  showSecondLine = false
}: LineChartVizProps) {
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
          <p className="text-[#888899] text-xs mb-1">{label}</p>
          {payload.map((entry: any, index: number) => (
            <p key={index} className="text-xs">
              <span style={{ color: entry.color }}>{entry.name}:</span>
              <span className="text-[#e0e0e0] ml-2">{entry.value.toLocaleString()}</span>
            </p>
          ))}
        </div>
      );
    }
    return null;
  };

  const ChartComponent = showArea ? AreaChart : LineChart;

  return (
    <ResponsiveContainer width="100%" height={height}>
      <ChartComponent data={data} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
        <defs>
          <linearGradient id="lineAreaGradient" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor={areaColor} stopOpacity={0.4}/>
            <stop offset="100%" stopColor={areaColor} stopOpacity={0}/>
          </linearGradient>
          <linearGradient id="lineAreaGradient2" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor={secondLineColor} stopOpacity={0.4}/>
            <stop offset="100%" stopColor={secondLineColor} stopOpacity={0}/>
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" stroke="#2a2a3a" vertical={false} />
        <XAxis 
          dataKey="name" 
          stroke="#888899"
          tick={{ fill: '#888899', fontSize: 11, fontFamily: 'Rajdhani, sans-serif' }}
          axisLine={{ stroke: '#2a2a3a' }}
        />
        <YAxis 
          stroke="#888899"
          tick={{ fill: '#888899', fontSize: 11, fontFamily: 'JetBrains Mono, monospace' }}
          axisLine={{ stroke: '#2a2a3a' }}
          tickFormatter={(value) => value.toLocaleString()}
        />
        <Tooltip content={<CustomTooltip />} />
        {showArea ? (
          <>
            <Area 
              type="monotone" 
              dataKey="value" 
              stroke={lineColor}
              strokeWidth={2}
              fill="url(#lineAreaGradient)"
              dot={showDots ? { fill: lineColor, strokeWidth: 2, r: 4 } : false}
              activeDot={{ r: 6, fill: lineColor, stroke: '#0a0a0f', strokeWidth: 2 }}
              name="Series 1"
            />
            {showSecondLine && (
              <Area 
                type="monotone" 
                dataKey="value2" 
                stroke={secondLineColor}
                strokeWidth={2}
                fill="url(#lineAreaGradient2)"
                dot={showDots ? { fill: secondLineColor, strokeWidth: 2, r: 4 } : false}
                activeDot={{ r: 6, fill: secondLineColor, stroke: '#0a0a0f', strokeWidth: 2 }}
                name="Series 2"
              />
            )}
          </>
        ) : (
          <>
            <Line 
              type="monotone" 
              dataKey="value" 
              stroke={lineColor}
              strokeWidth={2}
              dot={showDots ? { fill: lineColor, strokeWidth: 2, r: 4 } : false}
              activeDot={{ r: 6, fill: lineColor, stroke: '#0a0a0f', strokeWidth: 2 }}
              name="Series 1"
              style={{ filter: `drop-shadow(0 0 6px ${lineColor})` }}
            />
            {showSecondLine && (
              <Line 
                type="monotone" 
                dataKey="value2" 
                stroke={secondLineColor}
                strokeWidth={2}
                dot={showDots ? { fill: secondLineColor, strokeWidth: 2, r: 4 } : false}
                activeDot={{ r: 6, fill: secondLineColor, stroke: '#0a0a0f', strokeWidth: 2 }}
                name="Series 2"
                style={{ filter: `drop-shadow(0 0 6px ${secondLineColor})` }}
              />
            )}
          </>
        )}
      </ChartComponent>
    </ResponsiveContainer>
  );
}

export default LineChartViz;

