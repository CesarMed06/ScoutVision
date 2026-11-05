import { useLanguage } from '../i18n'
import {
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  ResponsiveContainer,
  Legend,
} from 'recharts'

interface MetricRadarProps {
  data: Array<{ metric: string; value: number; avg?: number }>
}

function angleTick({ x, y, textAnchor, payload }: { x: number; y: number; textAnchor?: string; payload?: { value?: string } }) {
  const anchor: 'start' | 'end' | 'middle' =
    textAnchor === 'start' ? 'start' : textAnchor === 'end' ? 'end' : 'middle'
  const dx = anchor === 'start' ? 4 : anchor === 'end' ? -4 : 0
  return (
    <text x={x + dx} y={y + 4} textAnchor={anchor} fill="#9CA3AF" fontSize={10}>
      {payload?.value}
    </text>
  )
}

export default function MetricRadar({ data }: MetricRadarProps) {
  const { t } = useLanguage()
  if (!data.length) return null

  return (
    <ResponsiveContainer width="100%" height={380}>
      <RadarChart cx="50%" cy="50%" outerRadius="50%" margin={{ top: 8, right: 12, bottom: 8, left: 12 }} data={data}>
        <PolarGrid stroke="#374151" />
        <PolarAngleAxis
          dataKey="metric"
          tick={angleTick as never}
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
          name={t('Player')}
          dataKey="value"
          stroke="#34D399"
          fill="#34D399"
          fillOpacity={0.15}
          strokeWidth={2}
        />
        {data[0]?.avg !== undefined && (
          <Radar
            name={t('Avg')}
            dataKey="avg"
            stroke="#60A5FA"
            fill="#60A5FA"
            fillOpacity={0.08}
            strokeWidth={1.5}
            strokeDasharray="4 4"
          />
        )}
        <Legend
          wrapperStyle={{ fontSize: 12, color: '#9CA3AF' }}
          iconType="circle"
        />
      </RadarChart>
    </ResponsiveContainer>
  )
}
