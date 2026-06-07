import { useState, useEffect } from 'react'
import { useSearchParams, Link } from 'react-router-dom'
import { Loader2, ArrowLeft } from 'lucide-react'
import { getPlayerMetrics, searchPlayers } from '../api'
import type { PlayerMetricsResponse, PlayerSummary } from '../api'
import MetricRadar from '../components/MetricRadar'

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

export default function Compare() {
  const [searchParams, setSearchParams] = useSearchParams()
  const aId = searchParams.get('a')
  const bId = searchParams.get('b')

  const [playerA, setPlayerA] = useState<PlayerMetricsResponse | null>(null)
  const [playerB, setPlayerB] = useState<PlayerMetricsResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [searchQ, setSearchQ] = useState('')
  const [searchR, setSearchR] = useState<PlayerSummary[]>([])
  const [selecting, setSelecting] = useState<'a' | 'b' | null>(null)

  useEffect(() => {
    if (!aId || !bId) { setLoading(false); return }
    setLoading(true)
    Promise.all([
      getPlayerMetrics(Number(aId)),
      getPlayerMetrics(Number(bId)),
    ])
      .then(([a, b]) => { setPlayerA(a); setPlayerB(b) })
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [aId, bId])

  useEffect(() => {
    if (!searchQ.trim()) { setSearchR([]); return }
    const t = setTimeout(() => {
      searchPlayers(searchQ).then((r) => {
        const seen = new Set<number>()
        setSearchR(r.filter(p => { if (seen.has(p.player_id)) return false; seen.add(p.player_id); return true }))
      }).catch(() => {})
    }, 300)
    return () => clearTimeout(t)
  }, [searchQ])

  function selectPlayer(slot: 'a' | 'b', id: number) {
    if (slot === 'a') setSearchParams({ a: String(id), b: bId || '' })
    else setSearchParams({ a: aId || '', b: String(id) })
    setSearchQ('')
    setSearchR([])
    setSelecting(null)
  }

  const radarData = (playerA?.totals && playerB?.totals)
    ? RADAR_METRICS.map((m) => {
        const valA = (playerA.totals[m.key] as number) || 0
        const valB = (playerB.totals[m.key] as number) || 0
        const maxVal = m.key.includes('pct') ? 100 : Math.max(valA * 1.5, valB * 1.5, 5)
        return {
          metric: m.label,
          value: Math.min(100, valA / maxVal * 100),
          avg: Math.min(100, valB / maxVal * 100),
        }
      })
    : []

  if (loading) {
    return <div className="flex items-center justify-center py-32"><Loader2 className="w-8 h-8 text-emerald-400 animate-spin" /></div>
  }

  if (!aId || !bId) {
    return (
      <div className="max-w-4xl mx-auto px-4 sm:px-6 py-12">
        <h1 className="text-2xl font-bold text-white mb-6">Compare Players</h1>
        <p className="text-gray-400 mb-6">Search and select two players to compare:</p>
        <div className="grid sm:grid-cols-2 gap-6">
          <div>
            <p className="text-gray-300 mb-2 font-medium">Player A {aId && playerA && `- ${playerA.player_name}`}</p>
            <input
              type="text"
              placeholder="Search..."
              value={selecting === 'a' ? searchQ : ''}
              onFocus={() => { setSelecting('a'); setSearchQ(''); setSearchR([]) }}
              onChange={(e) => { setSelecting('a'); setSearchQ(e.target.value) }}
              className="w-full px-4 py-2 bg-gray-900 border border-gray-700 rounded-lg text-white mb-2"
            />
            {selecting === 'a' && searchR.slice(0, 5).map((p) => (
              <button key={p.player_id} onClick={() => selectPlayer('a', p.player_id)}
                className="block w-full text-left px-3 py-2 text-sm text-gray-300 hover:bg-gray-800 rounded transition-colors">
                {p.player_name}
              </button>
            ))}
          </div>
          <div>
            <p className="text-gray-300 mb-2 font-medium">Player B {bId && playerB && `- ${playerB.player_name}`}</p>
            <input
              type="text"
              placeholder="Search..."
              value={selecting === 'b' ? searchQ : ''}
              onFocus={() => { setSelecting('b'); setSearchQ(''); setSearchR([]) }}
              onChange={(e) => { setSelecting('b'); setSearchQ(e.target.value) }}
              className="w-full px-4 py-2 bg-gray-900 border border-gray-700 rounded-lg text-white mb-2"
            />
            {selecting === 'b' && searchR.slice(0, 5).map((p) => (
              <button key={p.player_id} onClick={() => selectPlayer('b', p.player_id)}
                className="block w-full text-left px-3 py-2 text-sm text-gray-300 hover:bg-gray-800 rounded transition-colors">
                {p.player_name}
              </button>
            ))}
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 py-8">
      <Link to="/players" className="inline-flex items-center gap-1 text-gray-400 hover:text-white mb-6 transition-colors">
        <ArrowLeft className="w-4 h-4" /> Back to Players
      </Link>

      <div className="grid sm:grid-cols-2 gap-6 mb-8">
        <Link to={`/players/${aId}`} className="bg-gray-900 border border-gray-800 rounded-xl p-4 hover:border-emerald-500/50 transition-colors">
          <p className="text-xs text-gray-500 mb-1">Player A</p>
          <p className="text-lg font-bold text-white">{playerA?.player_name || 'Loading...'}</p>
        </Link>
        <Link to={`/players/${bId}`} className="bg-gray-900 border border-gray-800 rounded-xl p-4 hover:border-emerald-500/50 transition-colors">
          <p className="text-xs text-gray-500 mb-1">Player B</p>
          <p className="text-lg font-bold text-white">{playerB?.player_name || 'Loading...'}</p>
        </Link>
      </div>

      {radarData.length > 0 && (
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-4 mb-8">
          <h3 className="text-white font-semibold mb-4">Comparison Radar</h3>
          <MetricRadar data={radarData} />
        </div>
      )}
    </div>
  )
}
