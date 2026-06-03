import {
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  ResponsiveContainer,
} from 'recharts'

interface MetricRadarProps {
  data: Array<{ metric: string; value: number; avg?: number }>
}

export default function MetricRadar({ data }: MetricRadarProps) {
  if (!data.length) return null

  return (
    <ResponsiveContainer width="100%" height={360}>
      <RadarChart cx="50%" cy="50%" outerRadius="75%" data={data}>
        <PolarGrid stroke="#374151" />
        <PolarAngleAxis
          dataKey="metric"
          tick={{ fill: '#9CA3AF', fontSize: 11 }}
          stroke="#4B5563"
        />
        <PolarRadiusAxis
          angle={90}
          domain={[0, 100]}
          tick={false}
          axisLine={false}
          stroke="#4B5563"
        />
        <Radar
          name="Player"
          dataKey="value"
          stroke="#34D399"
          fill="#34D399"
          fillOpacity={0.15}
          strokeWidth={2}
        />
        {data[0]?.avg !== undefined && (
          <Radar
            name="Position Avg"
            dataKey="avg"
            stroke="#60A5FA"
            fill="#60A5FA"
            fillOpacity={0.08}
            strokeWidth={1.5}
            strokeDasharray="4 4"
          />
        )}
      </RadarChart>
    </ResponsiveContainer>
  )
}
