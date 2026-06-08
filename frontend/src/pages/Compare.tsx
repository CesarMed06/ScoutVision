import { useState, useEffect } from 'react'
import { useSearchParams, Link } from 'react-router-dom'
import { Loader2, ArrowLeft, ImageIcon, X, RefreshCw, AlertCircle } from 'lucide-react'
import { getPlayerMetrics, searchPlayers, getPlayerPhoto, getPlayerAverages } from '../api'
import type { PlayerMetricsResponse, PlayerSummary, AveragesResponse } from '../api'
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

const COMPARE_METRICS = [
  { category: 'Attack', keys: [
    { key: 'goals_per_90', label: 'Goals/90', suffix: '' },
    { key: 'xg_per_90', label: 'xG/90', suffix: '' },
    { key: 'xa_per_90', label: 'xA/90', suffix: '' },
    { key: 'shot_accuracy', label: 'Shot Acc.', suffix: '%' },
  ]},
  { category: 'Passing', keys: [
    { key: 'pass_completion_pct', label: 'Pass %', suffix: '%' },
    { key: 'key_passes_per_90', label: 'Key Passes/90', suffix: '' },
    { key: 'progressive_passes_per_90', label: 'Prog. Passes/90', suffix: '' },
  ]},
  { category: 'Dribbling', keys: [
    { key: 'dribbles_per_90', label: 'Dribbles/90', suffix: '' },
    { key: 'dribble_success_pct', label: 'Dribble %', suffix: '%' },
    { key: 'progressive_carries_per_90', label: 'Prog. Carries/90', suffix: '' },
  ]},
  { category: 'Defense', keys: [
    { key: 'tackles_per_90', label: 'Tackles/90', suffix: '' },
    { key: 'interceptions_per_90', label: 'Int./90', suffix: '' },
    { key: 'pressures_per_90', label: 'Pressures/90', suffix: '' },
  ]},
  { category: 'Physical', keys: [
    { key: 'aerial_success_pct', label: 'Aerial %', suffix: '%' },
    { key: 'duel_success_pct', label: 'Duels Won %', suffix: '%' },
    { key: 'tackle_success_pct', label: 'Tackle %', suffix: '%' },
  ]},
]

function PlayerSlot({ player, slot, loading, error, onSearch, onChange }: {
  player: PlayerMetricsResponse | null
  slot: 'a' | 'b'
  loading?: boolean
  error?: string
  onSearch: () => void
  onChange: () => void
}) {
  const [photo, setPhoto] = useState<string | null>(null)

  useEffect(() => {
    if (!player) { setPhoto(null); return }
    getPlayerPhoto(player.player_name).then(p => setPhoto(p.photo_url)).catch(() => {})
  }, [player?.player_name])

  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-4 relative group min-h-[80px]">
      {loading ? (
        <div className="flex items-center gap-3 py-2">
          <div className="w-12 h-12 rounded-full bg-gray-800 animate-pulse shrink-0" />
          <div className="flex-1">
            <div className="h-3 bg-gray-800 animate-pulse rounded w-16 mb-2" />
            <div className="h-4 bg-gray-800 animate-pulse rounded w-32" />
          </div>
        </div>
      ) : player ? (
        <>
          <button
            onClick={onChange}
            className="absolute top-2 right-2 p-1.5 bg-gray-800 rounded-lg opacity-0 group-hover:opacity-100 hover:bg-gray-700 transition-all text-gray-400 hover:text-white z-10"
            title="Change player"
          >
            <RefreshCw className="w-3.5 h-3.5" />
          </button>
          <Link to={`/players/${player.player_id}`} className="flex items-center gap-3">
            {photo ? (
              <img src={photo} alt={player.player_name} className="w-12 h-12 rounded-full object-cover shrink-0 border border-gray-700" />
            ) : (
              <div className="w-12 h-12 rounded-full bg-gray-800 flex items-center justify-center shrink-0">
                <ImageIcon className="w-6 h-6 text-gray-500" />
              </div>
            )}
            <div className="min-w-0">
              <p className="text-xs text-gray-500 mb-0.5">Player {slot.toUpperCase()}</p>
              <p className="text-base font-bold text-white truncate group-hover:text-emerald-400 transition-colors">
                {player.player_name}
              </p>
              <p className="text-xs text-gray-500">
                {player.match_details[0]?.team as string || ''} · {player.totals.minutes} min
              </p>
            </div>
          </Link>
        </>
      ) : error ? (
        <div className="flex items-center gap-3 py-2">
          <div className="w-12 h-12 rounded-full bg-red-900/30 flex items-center justify-center shrink-0">
            <AlertCircle className="w-6 h-6 text-red-400" />
          </div>
          <div>
            <p className="text-xs text-gray-500 mb-0.5">Player {slot.toUpperCase()}</p>
            <p className="text-sm text-red-400">{error}</p>
            <button onClick={onSearch} className="text-xs text-emerald-400 hover:text-emerald-300 mt-1">Try again</button>
          </div>
        </div>
      ) : (
        <button
          onClick={onSearch}
          className="w-full py-6 flex flex-col items-center gap-2 text-gray-500 hover:text-emerald-400 transition-colors"
        >
          <div className="w-12 h-12 rounded-full bg-gray-800 flex items-center justify-center">
            <ImageIcon className="w-6 h-6" />
          </div>
          <span className="text-sm font-medium">Select Player {slot.toUpperCase()}</span>
        </button>
      )}
    </div>
  )
}

function CompareRow({ label, valA, valB, suffix }: {
  label: string; valA: number; valB: number; suffix: string
}) {
  const fmt = (v: number) => v % 1 === 0 ? String(v) : v.toFixed(2)
  const aBetter = valA > valB
  const bBetter = valB > valA
  const equal = valA === valB

  return (
    <tr className="border-b border-gray-800/50 text-sm hover:bg-gray-800/20 transition-colors">
      <td className="py-2 pr-3 text-gray-400 text-xs font-medium">{label}</td>
      <td className={`py-2 px-3 text-right font-mono ${aBetter ? 'text-emerald-400 font-semibold' : equal ? 'text-gray-300' : 'text-gray-500'}`}>
        {fmt(valA)}{suffix}
      </td>
      <td className={`py-2 px-3 text-right font-mono ${bBetter ? 'text-emerald-400 font-semibold' : equal ? 'text-gray-300' : 'text-gray-500'}`}>
        {fmt(valB)}{suffix}
      </td>
    </tr>
  )
}

export default function Compare() {
  const [searchParams, setSearchParams] = useSearchParams()
  const aId = searchParams.get('a')
  const bId = searchParams.get('b')

  const [playerA, setPlayerA] = useState<PlayerMetricsResponse | null>(null)
  const [playerB, setPlayerB] = useState<PlayerMetricsResponse | null>(null)
  const [loadingA, setLoadingA] = useState(false)
  const [loadingB, setLoadingB] = useState(false)
  const [errorA, setErrorA] = useState('')
  const [errorB, setErrorB] = useState('')
  const [averages, setAverages] = useState<AveragesResponse | null>(null)
  const [averagesLoading, setAveragesLoading] = useState(false)

  const [searchQ, setSearchQ] = useState('')
  const [searchR, setSearchR] = useState<PlayerSummary[]>([])
  const [showSearchModal, setShowSearchModal] = useState<'a' | 'b' | null>(null)

  function fetchPlayer(slot: 'a' | 'b', id: string | null) {
    if (!id) return
    const setPlayer = slot === 'a' ? setPlayerA : setPlayerB
    const setLoading = slot === 'a' ? setLoadingA : setLoadingB
    const setError = slot === 'a' ? setErrorA : setErrorB
    setLoading(true)
    setError('')
    getPlayerMetrics(Number(id))
      .then((data) => setPlayer(data))
      .catch(() => setError(`Could not load player ${id}`))
      .finally(() => setLoading(false))
  }

  // Fetch player data when IDs change
  useEffect(() => {
    fetchPlayer('a', aId)
    fetchPlayer('b', bId)
  }, [aId, bId])

  // Fetch averages when both players are loaded
  useEffect(() => {
    if (!playerA || !playerB) return
    setAveragesLoading(true)
    getPlayerAverages(playerA.player_name)
      .then(setAverages)
      .catch(() => {})
      .finally(() => setAveragesLoading(false))
  }, [playerA?.player_id, playerB?.player_id])

  // Search effect
  useEffect(() => {
    if (!searchQ.trim() || !showSearchModal) { setSearchR([]); return }
    const t = setTimeout(() => {
      searchPlayers(searchQ).then((r) => {
        const seen = new Set<number>()
        setSearchR(r.filter(p => { if (seen.has(p.player_id)) return false; seen.add(p.player_id); return true }))
      }).catch(() => {})
    }, 300)
    return () => clearTimeout(t)
  }, [searchQ, showSearchModal])

  function selectPlayer(slot: 'a' | 'b', id: number) {
    if (slot === 'a') setSearchParams({ a: String(id), b: bId || '' })
    else setSearchParams({ a: aId || '', b: String(id) })
    setSearchQ('')
    setSearchR([])
    setShowSearchModal(null)
  }

  function changePlayer(slot: 'a' | 'b') {
    setShowSearchModal(slot)
    setSearchQ('')
    setSearchR([])
  }

  const showFullComparison = !!(aId && bId && playerA && playerB)

  // Build radar data with global averages as reference scale
  const radarData = (playerA?.totals && playerB?.totals && averages)
    ? RADAR_METRICS.map((m) => {
        const valA = (playerA.totals[m.key] as number) || 0
        const valB = (playerB.totals[m.key] as number) || 0
        const avgVal = (averages[m.key as keyof AveragesResponse] as number) || 0
        const maxVal = m.key.includes('pct') ? 100 : Math.max(valA, valB, avgVal * 2, 5)
        return {
          metric: m.label,
          value: Math.min(100, valA / maxVal * 100),
          avg: Math.min(100, valB / maxVal * 100),
        }
      })
    : []

  function getField(totals: Record<string, unknown>, key: string): number {
    let v = totals[key] as number | undefined
    if (v !== undefined) return v
    if (key.endsWith('_per_90')) {
      const rawKey = key.replace('_per_90', '')
      const raw = (totals[rawKey] ?? 0) as number
      const min = (totals.minutes as number) || 1
      return raw / min * 90
    }
    return 0
  }

  function SearchModal({ slot }: { slot: 'a' | 'b' }) {
    return (
      <div className="fixed inset-0 bg-black/60 z-50 flex items-start justify-center pt-24 px-4" onClick={() => setShowSearchModal(null)}>
        <div className="bg-gray-900 border border-gray-800 rounded-xl w-full max-w-md p-4" onClick={e => e.stopPropagation()}>
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-white font-semibold">Select Player {slot.toUpperCase()}</h3>
            <button onClick={() => setShowSearchModal(null)} className="text-gray-500 hover:text-white transition-colors">
              <X className="w-5 h-5" />
            </button>
          </div>
          <input
            type="text"
            placeholder="Search players..."
            value={searchQ}
            onChange={(e) => setSearchQ(e.target.value)}
            autoFocus
            className="w-full px-4 py-2.5 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-emerald-500 mb-2"
          />
          <div className="max-h-64 overflow-y-auto">
            {searchR.slice(0, 8).map((p) => (
              <button
                key={p.player_id}
                onClick={() => selectPlayer(slot, p.player_id)}
                className="w-full text-left px-3 py-2.5 text-sm text-gray-300 hover:bg-gray-800 rounded-lg transition-colors flex items-center gap-3"
              >
                <div className="w-8 h-8 rounded-full bg-gray-800 flex items-center justify-center shrink-0">
                  <ImageIcon className="w-4 h-4 text-gray-500" />
                </div>
                <div>
                  <p className="text-white font-medium">{p.player_name}</p>
                  <p className="text-gray-500 text-xs">{p.team} · {p.competition}</p>
                </div>
              </button>
            ))}
            {searchQ.trim() && searchR.length === 0 && (
              <p className="text-gray-500 text-sm text-center py-4">No players found</p>
            )}
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

      <h1 className="text-2xl font-bold text-white mb-6">Compare Players</h1>

      <div className="grid sm:grid-cols-2 gap-4 mb-8">
        <PlayerSlot
          player={playerA}
          slot="a"
          loading={loadingA}
          error={errorA}
          onSearch={() => changePlayer('a')}
          onChange={() => changePlayer('a')}
        />
        <PlayerSlot
          player={playerB}
          slot="b"
          loading={loadingB}
          error={errorB}
          onSearch={() => changePlayer('b')}
          onChange={() => changePlayer('b')}
        />
      </div>

      {showSearchModal && <SearchModal slot={showSearchModal} />}

      {showFullComparison && averagesLoading && (
        <div className="flex items-center justify-center gap-2 text-gray-400 py-4">
          <Loader2 className="w-4 h-4 animate-spin" />
          <span className="text-sm">Loading averages...</span>
        </div>
      )}

      {showFullComparison && !averagesLoading && radarData.length > 0 && (
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-4 mb-8">
          <h3 className="text-white font-semibold mb-1">Comparison Radar</h3>
          <p className="text-xs text-gray-500 mb-4">Player A (solid) vs Player B (dashed) — scaled against league averages</p>
          <MetricRadar data={radarData} />
        </div>
      )}

      {showFullComparison && !averagesLoading && (
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-4 mb-8">
          <h3 className="text-white font-semibold mb-1">Stats Comparison</h3>
          <p className="text-xs text-gray-500 mb-4">Green indicates the better value</p>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-xs text-gray-500 uppercase border-b border-gray-800">
                  <th className="text-left py-2 pr-3 font-medium">Metric</th>
                  <th className="text-right px-3 font-medium">{playerA.player_name.split(' ').pop()}</th>
                  <th className="text-right px-3 font-medium">{playerB.player_name.split(' ').pop()}</th>
                </tr>
              </thead>
              <tbody>
                {COMPARE_METRICS.map((section) => (
                  <>
                    <tr className="border-b border-gray-800">
                      <td colSpan={3} className="py-2 text-xs font-bold text-gray-300 uppercase tracking-wider">
                        {section.category}
                      </td>
                    </tr>
                    {section.keys.map((m) => (
                      <CompareRow
                        key={m.key}
                        label={m.label}
                        valA={getField(playerA.totals as Record<string, unknown>, m.key)}
                        valB={getField(playerB.totals as Record<string, unknown>, m.key)}
                        suffix={m.suffix}
                      />
                    ))}                    </>
                  ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {!showFullComparison && !loadingA && !loadingB && !aId && !bId && (
        <p className="text-center text-gray-500 mt-8">
          Select two players above to compare their stats.
        </p>
      )}
    </div>
  )
}
