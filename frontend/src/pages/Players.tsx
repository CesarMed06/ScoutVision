import { useState, useEffect } from 'react'
import { Search, Loader2 } from 'lucide-react'
import { searchPlayers } from '../api'
import type { PlayerSummary } from '../api'
import PlayerCard from '../components/PlayerCard'

const FAMOUS_NAMES = ['Messi', 'Ronaldo', 'Neymar', 'Suárez', 'Lewandowski', 'Mbappé', 'Haaland', 'Salah', 'De Bruyne', 'Kroos']

export default function Players() {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState<PlayerSummary[]>([])
  const [loading, setLoading] = useState(false)
const [featured, setFeatured] = useState<PlayerSummary[]>([])

  useEffect(() => {
    Promise.all(
      FAMOUS_NAMES.map((name) =>
        searchPlayers(name).then((r) => r.slice(0, 1)).catch(() => [] as PlayerSummary[])
      )
    ).then((batches) => {
      const seen = new Set<number>()
      setFeatured(batches.flat().filter(p => {
        if (seen.has(p.player_id)) return false
        seen.add(p.player_id)
        return true
      }).slice(0, 12))
    })
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
            {featured.map((p) => (
              <PlayerCard key={`${p.player_id}-${p.match_id}`} player={p} />
            ))}
          </div>
        </>
      )}
    </div>
  )
}
