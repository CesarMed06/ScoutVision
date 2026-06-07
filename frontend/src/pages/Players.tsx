import { useState, useEffect } from 'react'
import { Search, Loader2 } from 'lucide-react'
import { searchPlayers, getFeaturedPlayers } from '../api'
import type { PlayerSummary, FeaturedPlayer } from '../api'
import PlayerCard from '../components/PlayerCard'

function SkeletonCard() {
  return (
    <div className="p-4 bg-gray-900 border border-gray-800 rounded-lg animate-pulse">
      <div className="flex items-start gap-3">
        <div className="w-10 h-10 rounded-full bg-gray-800 shrink-0" />
        <div className="flex-1">
          <div className="h-4 bg-gray-800 rounded w-32 mb-2" />
          <div className="h-3 bg-gray-800 rounded w-24" />
        </div>
      </div>
    </div>
  )
}

export default function Players() {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState<PlayerSummary[]>([])
  const [loading, setLoading] = useState(false)
  const [featured, setFeatured] = useState<FeaturedPlayer[]>([])
  const [featuredLoading, setFeaturedLoading] = useState(true)

  useEffect(() => {
    let cancelled = false
    getFeaturedPlayers()
      .then((data) => { if (!cancelled) setFeatured(data) })
      .catch(() => { if (!cancelled) setFeatured([]) })
      .finally(() => { if (!cancelled) setFeaturedLoading(false) })
    return () => { cancelled = true }
  }, [])

  useEffect(() => {
    if (!query.trim()) {
      setResults([])
      return
    }
    const t = setTimeout(async () => {
      setLoading(true)
      try {
        const data = await searchPlayers(query)
        const seen = new Set<number>()
        const unique = data.filter(p => {
          if (seen.has(p.player_id)) return false
          seen.add(p.player_id)
          return true
        })
        setResults(unique)
      } catch {
        setResults([])
      }
      setLoading(false)
    }, 300)
    return () => clearTimeout(t)
  }, [query])

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 py-8">
      <div className="relative mb-8">
        <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search players by name..."
          className="w-full pl-12 pr-4 py-3 bg-gray-900 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-emerald-500 transition-colors"
          autoFocus
        />
        {loading && <Loader2 className="absolute right-4 top-1/2 -translate-y-1/2 w-5 h-5 text-emerald-400 animate-spin" />}
      </div>

      {query.trim() ? (
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-3">
          {results.map((p) => (
            <PlayerCard key={`${p.player_id}-${p.match_id}`} player={p} />
          ))}
          {!loading && results.length === 0 && (
            <p className="col-span-full text-center text-gray-500 py-12">No players found</p>
          )}
        </div>
      ) : (
        <>
          <h2 className="text-lg font-semibold text-white mb-4">Featured Players</h2>
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {featuredLoading
              ? Array.from({ length: 5 }).map((_, i) => <SkeletonCard key={i} />)
              : featured.map((p) => (
                  <PlayerCard key={p.player_id} player={p} />
                ))
            }
          </div>
        </>
      )}
    </div>
  )
}
