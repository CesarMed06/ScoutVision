import { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { Loader2, Shield, Target, Zap, Footprints, Swords, FileText, ChevronDown, ChevronUp } from 'lucide-react'
import { getPlayerMetrics, getAiReport } from '../api'
import type { PlayerMetricsResponse, PlayerMetricsTotals } from '../api'
import MetricRadar from '../components/MetricRadar'

const METRIC_LABELS: Record<string, string> = {
  goals: 'Goals', shots: 'Shots', xg: 'xG', assists: 'Assists', xa: 'xA',
  key_passes: 'Key Passes', progressive_passes: 'Prog. Passes', passes_into_final_third: 'Final Third Passes',
  dribbles: 'Dribbles', carries: 'Carries', progressive_carries: 'Prog. Carries',
  tackles: 'Tackles', interceptions: 'Interceptions', pressures: 'Pressures',
  aerial_duels: 'Aerial Duels', duels: 'Duels',
  fouls_won: 'Fouls Won', fouls_committed: 'Fouls Comm.',
  pass_completion_pct: 'Pass %', shot_accuracy: 'Shot Acc.',
  dribble_success_pct: 'Dribble %', duel_success_pct: 'Duels Won %', tackle_success_pct: 'Tackle %',
  aerial_success_pct: 'Aerial %',
}

const CAPS: Record<string, number> = {
  goals_per_90: 2, xg_per_90: 1.5, xa_per_90: 1, key_passes_per_90: 3,
  dribbles_per_90: 6, tackles_per_90: 5,
  pass_completion_pct: 100, aerial_success_pct: 100,
}

const RADAR_METRICS = [
  { key: 'goals_per_90', label: 'Goals/90' },
  { key: 'xg_per_90', label: 'xG/90' },
  { key: 'xa_per_90', label: 'xA/90' },
  { key: 'key_passes_per_90', label: 'Key Passes/90' },
  { key: 'dribbles_per_90', label: 'Dribbles/90' },
  { key: 'pass_completion_pct', label: 'Pass %' },
  { key: 'tackles_per_90', label: 'Tackles/90' },
  { key: 'aerial_success_pct', label: 'Aerial %' },
]

function MetricCard({ label, value, suffix }: { label: string; value: number | string; suffix?: string }) {
  const display = typeof value === 'number' ? (Number.isInteger(value) ? value : value.toFixed(1)) : value
  return (
    <div className="p-3 bg-gray-900 border border-gray-800 rounded-lg">
      <p className="text-xs text-gray-400 mb-1">{label}</p>
      <p className="text-lg font-semibold text-white">
        {display}{suffix || ''}
      </p>
    </div>
  )
}

function Section({ title, icon, children }: { title: string; icon: React.ReactNode; children: React.ReactNode }) {
  return (
    <div className="mb-6">
      <div className="flex items-center gap-2 text-white font-semibold mb-3">
        {icon}
        {title}
      </div>
      <div className="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-5 gap-2">
        {children}
      </div>
    </div>
  )
}

export default function PlayerProfile() {
  const { playerId } = useParams()
  const [data, setData] = useState<PlayerMetricsResponse | null>(null)
  const [report, setReport] = useState<string | null>(null)
  const [reportLoading, setReportLoading] = useState(false)
  const [showReport, setShowReport] = useState(false)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    if (!playerId) return
    setLoading(true)
    setError('')
    getPlayerMetrics(Number(playerId))
      .then((d) => { setData(d); setLoading(false) })
      .catch(() => { setError('Player not found'); setLoading(false) })
  }, [playerId])

  function loadReport() {
    if (report || !playerId) return
    setReportLoading(true)
    getAiReport(Number(playerId))
      .then((r) => { setReport(r.report); setShowReport(true) })
      .catch(() => setReport('Failed to generate report'))
      .finally(() => setReportLoading(false))
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-32">
        <Loader2 className="w-8 h-8 text-emerald-400 animate-spin" />
      </div>
    )
  }

  if (error || !data) {
    return (
      <div className="text-center py-32">
        <p className="text-gray-400 text-lg">{error || 'No data'}</p>
      </div>
    )
  }

  const t = data.totals as PlayerMetricsTotals
  const matchCount = data.match_details.length

  const radarData = RADAR_METRICS.map((m) => {
    const cap = CAPS[m.key] || 5
    return {
      metric: m.label,
      value: Math.min(100, ((t[m.key] as number) || 0) / cap * 100),
      avg: m.key.includes('pct') ? 70 : 25,
    }
  })

  const attackKeys = ['goals', 'assists', 'shots', 'shots_on_target', 'xg', 'xa'] as const
  const passingKeys = ['passes', 'passes_completed', 'key_passes', 'progressive_passes', 'passes_into_final_third'] as const
  const dribbleKeys = ['dribbles', 'dribbles_completed', 'carries', 'progressive_carries'] as const
  const defenseKeys = ['tackles', 'tackles_won', 'interceptions', 'pressures', 'ball_recoveries'] as const
  const physicalKeys = ['aerial_duels', 'aerial_duels_won', 'duels', 'duels_won', 'fouls_won', 'fouls_committed'] as const

  const pctKeys = ['pass_completion_pct', 'shot_accuracy', 'dribble_success_pct', 'duel_success_pct', 'tackle_success_pct', 'aerial_success_pct'] as const

  function renderMetrics(keys: readonly string[]) {
    return keys.map((k) => (
      t[k] !== undefined ? (
        <MetricCard
          key={k}
          label={METRIC_LABELS[k] || k.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase())}
          value={(t[k] as number) || 0}
          suffix={k.endsWith('_pct') ? '%' : ''}
        />
      ) : null
    ))
  }

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 py-8">
      <div className="flex items-center gap-4 mb-8">
        <div className="w-14 h-14 rounded-full bg-emerald-900/30 border border-emerald-500/30 flex items-center justify-center">
          <Shield className="w-7 h-7 text-emerald-400" />
        </div>
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold text-white">{data.player_name}</h1>
          {data.match_details[0] && (
            <p className="text-gray-400 text-sm">
              {(data.match_details[0] as Record<string, string>).team || ''}{' '}
              · {matchCount} match{matchCount !== 1 ? 'es' : ''}{' '}
              · {t.minutes} min
            </p>
          )}
        </div>
      </div>

      <div className="grid lg:grid-cols-3 gap-6 mb-8">
        <div className="lg:col-span-2">
          <Section title="Attack" icon={<Target className="w-4 h-4 text-red-400" />}>
            {renderMetrics(attackKeys)}
          </Section>

          <Section title="Passing" icon={<Footprints className="w-4 h-4 text-blue-400" />}>
            {renderMetrics(passingKeys)}
          </Section>

          <Section title="Dribbling & Carries" icon={<Zap className="w-4 h-4 text-yellow-400" />}>
            {renderMetrics(dribbleKeys)}
          </Section>

          <Section title="Defense" icon={<Swords className="w-4 h-4 text-purple-400" />}>
            {renderMetrics(defenseKeys)}
          </Section>

          <Section title="Physical" icon={<Swords className="w-4 h-4 text-orange-400" />}>
            {renderMetrics(physicalKeys)}
          </Section>

          <Section title="Efficiency" icon={<Target className="w-4 h-4 text-emerald-400" />}>
            {renderMetrics(pctKeys)}
          </Section>
        </div>

        <div className="lg:col-span-1">
          <div className="bg-gray-900 border border-gray-800 rounded-xl p-4 mb-4">
            <h3 className="text-white font-semibold mb-2">Per 90 vs Average</h3>
            <MetricRadar data={radarData} />
          </div>

          <button
            onClick={loadReport}
            disabled={reportLoading}
            className="w-full px-4 py-3 bg-emerald-500 hover:bg-emerald-400 disabled:bg-gray-700 text-black font-semibold rounded-lg transition-all flex items-center justify-center gap-2"
          >
            {reportLoading ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : (
              <FileText className="w-5 h-5" />
            )}
            AI Scouting Report
          </button>

          {report && (
            <div className="mt-4 bg-gray-900 border border-gray-800 rounded-xl">
              <button
                onClick={() => setShowReport(!showReport)}
                className="w-full px-4 py-3 flex items-center justify-between text-white font-medium"
              >
                <span className="flex items-center gap-2">
                  <FileText className="w-4 h-4 text-emerald-400" />
                  Scout Report
                </span>
                {showReport ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
              </button>
              {showReport && (
                <div className="px-4 pb-4 text-sm text-gray-300 leading-relaxed whitespace-pre-line max-h-96 overflow-y-auto">
                  {report}
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl p-4">
        <h3 className="text-white font-semibold mb-3">Match Log ({matchCount})</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-gray-400 text-xs uppercase border-b border-gray-800">
                <th className="text-left py-2 pr-4">Match</th>
                <th className="text-right px-2">Min</th>
                <th className="text-right px-2">G</th>
                <th className="text-right px-2">A</th>
                <th className="text-right px-2">Sh</th>
                <th className="text-right px-2">xG</th>
                <th className="text-right px-2">xA</th>
                <th className="text-right px-2">KP</th>
                <th className="text-right px-2">Pas</th>
                <th className="text-right px-2">Drb</th>
                <th className="text-right px-2">Tkl</th>
              </tr>
            </thead>
            <tbody>
              {data.match_details.map((m, i) => {
                const row = m as Record<string, number | string>
                return (
                  <tr key={i} className="border-b border-gray-800/50 text-gray-300 hover:bg-gray-800/30 transition-colors">
                    <td className="py-2 pr-4 truncate max-w-40">
                      {row.team} ({(row as Record<string, string>).competition?.split(' ').pop()})
                    </td>
                    <td className="text-right px-2">{row.minutes}</td>
                    <td className="text-right px-2">{row.goals || 0}</td>
                    <td className="text-right px-2">{row.assists || 0}</td>
                    <td className="text-right px-2">{row.shots || 0}</td>
                    <td className="text-right px-2">{(row.xg as number)?.toFixed(2) || '0'}</td>
                    <td className="text-right px-2">{(row.xa as number)?.toFixed(2) || '0'}</td>
                    <td className="text-right px-2">{row.key_passes || 0}</td>
                    <td className="text-right px-2">{row.passes || 0}</td>
                    <td className="text-right px-2">{row.dribbles || 0}</td>
                    <td className="text-right px-2">{row.tackles || 0}</td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
