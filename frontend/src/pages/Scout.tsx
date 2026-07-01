import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { Loader2, SlidersHorizontal, Search, ArrowUpDown, Target, ImageIcon, ChevronLeft, ChevronRight } from 'lucide-react'
import { getPlayerPhoto } from '../api'

interface ScoutFilters {
  min_goals_per_90: number
  min_xg_per_90: number
  min_xa_per_90: number
  min_key_passes_per_90: number
  min_tackles_per_90: number
  min_pass_pct: number
  min_dribble_pct: number
  min_aerial_pct: number
  min_pressures_per_90: number
}

const PAGE_SIZE = 10

const DEFAULT_FILTERS: ScoutFilters = {
  min_goals_per_90: 0,
  min_xg_per_90: 0,
  min_xa_per_90: 0,
  min_key_passes_per_90: 0,
  min_tackles_per_90: 0,
  min_pass_pct: 0,
  min_dribble_pct: 0,
  min_aerial_pct: 0,
  min_pressures_per_90: 0,
}

interface ScoutResult {
  player_id: number
  player_name: string
  team: string
  competition: string
  matches: number
  minutes: number
  goals_per_90: number
  xg_per_90: number
  xa_per_90: number
  key_passes_per_90: number
  tackles_per_90: number
  pass_pct: number
  dribble_pct: number
  aerial_pct: number
  pressures_per_90: number
}

const FILTER_CONFIG = [
  { key: 'min_goals_per_90' as const, label: 'Min Goals/90', max: 3, step: 0.05 },
  { key: 'min_xg_per_90' as const, label: 'Min xG/90', max: 2, step: 0.05 },
  { key: 'min_xa_per_90' as const, label: 'Min xA/90', max: 1.5, step: 0.05 },
  { key: 'min_key_passes_per_90' as const, label: 'Min Key Passes/90', max: 5, step: 0.1 },
  { key: 'min_tackles_per_90' as const, label: 'Min Tackles/90', max: 6, step: 0.1 },
  { key: 'min_pass_pct' as const, label: 'Min Pass %', max: 100, step: 1 },
  { key: 'min_dribble_pct' as const, label: 'Min Dribble %', max: 100, step: 1 },
  { key: 'min_aerial_pct' as const, label: 'Min Aerial %', max: 100, step: 1 },
  { key: 'min_pressures_per_90' as const, label: 'Min Pressures/90', max: 25, step: 0.5 },
]

const SORT_OPTIONS = [
  { value: 'goals_per_90', label: 'Goals/90' },
  { value: 'xg_per_90', label: 'xG/90' },
  { value: 'xa_per_90', label: 'xA/90' },
  { value: 'key_passes_per_90', label: 'Key Passes/90' },
  { value: 'tackles_per_90', label: 'Tackles/90' },
  { value: 'pass_pct', label: 'Pass %' },
  { value: 'dribble_pct', label: 'Dribble %' },
  { value: 'aerial_pct', label: 'Aerial %' },
  { value: 'pressures_per_90', label: 'Pressures/90' },
]

async function scoutSearch(query: string): Promise<ScoutResult[]> {
  const controller = new AbortController()
  const timer = setTimeout(() => controller.abort(), 30000)
  try {
    const res = await fetch(`/api/v1/players/search/advanced?${query}`, { signal: controller.signal })
    if (!res.ok) throw new Error(`Search failed: ${res.status}`)
    return res.json()
  } finally {
    clearTimeout(timer)
  }
}

export default function Scout() {
  const [filters, setFilters] = useState<ScoutFilters>(DEFAULT_FILTERS)
  const [results, setResults] = useState<ScoutResult[]>([])
  const [loading, setLoading] = useState(false)
  const [searched, setSearched] = useState(false)
  const [sortBy, setSortBy] = useState('goals_per_90')
  const [sortDir, setSortDir] = useState<'asc' | 'desc'>('desc')
  const [photos, setPhotos] = useState<Record<number, string | null>>({})
  const [page, setPage] = useState(1)

  function buildQuery() {
    const params = new URLSearchParams()
    for (const [k, v] of Object.entries(filters)) {
      if (v > 0) params.set(k, String(v))
    }
    params.set('sort_by', sortBy)
    params.set('sort_dir', sortDir)
    params.set('limit', '50')
    return params.toString()
  }

  async function doSearch() {
    setLoading(true)
    setSearched(true)
    try {
      const data = await scoutSearch(buildQuery())
      setResults(data)
      setPage(1)
    } catch {
      setResults([])
    }
    setLoading(false)
  }

  useEffect(() => {
    if (results.length === 0) return
    const ids = results.map(p => p.player_id)
    const photoPromises = ids.map(id => {
      const p = results.find(r => r.player_id === id)!
      return getPlayerPhoto(p.player_name)
        .then(res => ({ id, url: res.photo_url }))
        .catch(() => ({ id, url: null }))
    })
    Promise.all(photoPromises).then(photoResults => {
      const map: Record<number, string | null> = {}
      photoResults.forEach(r => { map[r.id] = r.url })
      setPhotos(map)
    })
  }, [results])

  const activeCount = Object.values(filters).filter(v => v > 0).length
  const totalPages = Math.ceil(results.length / PAGE_SIZE)
  const paged = results.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE)

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 py-8">
      <div className="flex items-center gap-3 mb-6">
        <SlidersHorizontal className="w-6 h-6 text-emerald-400" />
        <h1 className="text-2xl font-bold text-white">Scout Filter</h1>
        {activeCount > 0 && (
          <span className="px-2 py-0.5 text-xs bg-emerald-500/20 text-emerald-400 rounded-full">
            {activeCount} active
          </span>
        )}
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl p-4 sm:p-6 mb-6">
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4 mb-4">
          {FILTER_CONFIG.map((cfg) => (
            <div key={cfg.key}>
              <label className="flex items-center justify-between text-sm text-gray-400 mb-1">
                <span>{cfg.label}</span>
                <span className="font-mono text-white">
                  {cfg.step < 1 ? filters[cfg.key].toFixed(2) : filters[cfg.key].toFixed(0)}
                </span>
              </label>
              <input
                type="range"
                min={0}
                max={cfg.max}
                step={cfg.step}
                value={filters[cfg.key]}
                onChange={(e) => setFilters(prev => ({ ...prev, [cfg.key]: parseFloat(e.target.value) }))}
                className="w-full h-1.5 rounded-full appearance-none cursor-pointer
                  bg-gray-700 accent-emerald-500
                  [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-4
                  [&::-webkit-slider-thumb]:h-4 [&::-webkit-slider-thumb]:rounded-full
                  [&::-webkit-slider-thumb]:bg-emerald-500
                  [&::-moz-range-thumb]:w-4 [&::-moz-range-thumb]:h-4
                  [&::-moz-range-thumb]:rounded-full [&::-moz-range-thumb]:bg-emerald-500
                  [&::-moz-range-thumb]:border-0"
              />
            </div>
          ))}
        </div>

        <div className="flex flex-wrap items-center gap-3 pt-3 border-t border-gray-800">
          <div className="flex items-center gap-2">
            <label className="text-sm text-gray-400">Sort by</label>
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="px-3 py-1.5 bg-gray-800 border border-gray-700 rounded-lg text-sm text-white focus:outline-none focus:border-emerald-500"
            >
              {SORT_OPTIONS.map(opt => (
                <option key={opt.value} value={opt.value}>{opt.label}</option>
              ))}
            </select>
          </div>
          <button
            onClick={() => setSortDir(d => d === 'desc' ? 'asc' : 'desc')}
            className="px-3 py-1.5 bg-gray-800 border border-gray-700 rounded-lg text-sm text-gray-400 hover:text-white transition-colors flex items-center gap-1"
          >
            <ArrowUpDown className="w-3.5 h-3.5" />
            {sortDir === 'desc' ? 'High → Low' : 'Low → High'}
          </button>
          <button
            onClick={doSearch}
            disabled={loading}
            className="px-6 py-2 bg-emerald-500 hover:bg-emerald-400 disabled:bg-gray-700 text-black font-semibold rounded-lg transition-all flex items-center gap-2 ml-auto"
          >
            {loading ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Search className="w-4 h-4" />
            )}
            {activeCount > 0 ? 'Apply Filters' : 'Show All Players'}
          </button>
        </div>
      </div>

      {loading && (
        <div className="flex items-center justify-center py-16">
          <Loader2 className="w-8 h-8 text-emerald-400 animate-spin" />
        </div>
      )}

      {!loading && searched && results.length === 0 && (
        <div className="text-center py-16">
          <Target className="w-12 h-12 text-gray-700 mx-auto mb-3" />
          <p className="text-gray-500 text-lg">No players match your filters</p>
          <p className="text-gray-600 text-sm mt-1">Try lowering the thresholds</p>
        </div>
      )}

      {!loading && results.length > 0 && (
        <>
          <p className="text-gray-400 text-sm mb-3">
            {results.length} players found
            {totalPages > 1 && <span className="text-gray-600"> · Page {page}/{totalPages}</span>}
          </p>
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {paged.map((p) => (
              <Link
                key={p.player_id}
                to={`/players/${p.player_id}`}
                className="block p-4 bg-gray-900 border border-gray-800 rounded-lg hover:border-emerald-500/50 transition-all group"
              >
                <div className="flex items-start gap-3">
                  <div className="w-10 h-10 rounded-full bg-gray-800 shrink-0 overflow-hidden">
                    {photos[p.player_id] ? (
                      <img src={photos[p.player_id]!} alt={p.player_name} className="w-full h-full object-cover" />
                    ) : (
                      <div className="w-full h-full flex items-center justify-center">
                        <ImageIcon className="w-5 h-5 text-gray-500" />
                      </div>
                    )}
                  </div>
                  <div className="min-w-0 flex-1">
                    <p className="text-white font-semibold truncate group-hover:text-emerald-400 transition-colors">{p.player_name}</p>
                    <p className="text-xs text-gray-500">{p.team} · {p.competition}</p>
                    <div className="flex flex-wrap gap-x-3 gap-y-0.5 mt-1.5 text-xs">
                      <span style={{ color: '#f87171' }}>G/90: {p.goals_per_90.toFixed(2)}</span>
                      <span style={{ color: '#38bdf8' }}>xG: {p.xg_per_90.toFixed(2)}</span>
                      <span style={{ color: '#38bdf8' }}>xA: {p.xa_per_90.toFixed(2)}</span>
                      <span style={{ color: '#a78bfa' }}>Tkl: {p.tackles_per_90.toFixed(2)}</span>
                      <span style={{ color: '#60a5fa' }}>P%: {p.pass_pct}%</span>
                    </div>
                  </div>
                </div>
              </Link>
            ))}
          </div>
          {totalPages > 1 && (
            <div className="flex items-center justify-center gap-3 mt-6">
              <button
                onClick={() => setPage(p => Math.max(1, p - 1))}
                disabled={page === 1}
                className="px-3 py-1.5 bg-gray-800 border border-gray-700 rounded-lg text-sm text-gray-400 hover:text-white disabled:opacity-30 disabled:cursor-not-allowed transition-colors flex items-center gap-1"
              >
                <ChevronLeft className="w-4 h-4" />
                Previous
              </button>
              <span className="text-xs text-gray-500">
                Page {page} of {totalPages}
              </span>
              <button
                onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                disabled={page === totalPages}
                className="px-3 py-1.5 bg-gray-800 border border-gray-700 rounded-lg text-sm text-gray-400 hover:text-white disabled:opacity-30 disabled:cursor-not-allowed transition-colors flex items-center gap-1"
              >
                Next
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          )}
        </>
      )}

      {!searched && !loading && (
        <div className="text-center py-16">
          <SlidersHorizontal className="w-12 h-12 text-gray-700 mx-auto mb-3" />
          <p className="text-gray-500">Adjust the filters above and click "Apply Filters"</p>
          <p className="text-gray-600 text-sm mt-1">Find players by minimum performance thresholds</p>
        </div>
      )}
    </div>
  )
}
