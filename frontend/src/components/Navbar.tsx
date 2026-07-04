import { useEffect, useState } from 'react'
import { Search, Home, GitCompare, SlidersHorizontal } from 'lucide-react'
import { Link, useLocation } from 'react-router-dom'
import { getHealth } from '../api'

export default function Navbar() {
  const loc = useLocation()
  const [dbStatus, setDbStatus] = useState<'loading' | 'ready' | number>('loading')

  useEffect(() => {
    let active = true
    function poll() {
      getHealth().then(h => {
        if (!active) return
        if (h.vector_db_initialized && h.vector_db_size > 0) setDbStatus(h.vector_db_size)
        else setTimeout(poll, 2000)
      }).catch(() => { if (active) setTimeout(poll, 5000) })
    }
    poll()
    return () => { active = false }
  }, [])

  return (
    <nav className="border-b border-gray-800 bg-gray-950/90 backdrop-blur-sm sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-14 flex items-center justify-between">
        <Link to="/" className="flex items-center gap-2.5 text-white hover:opacity-80 transition-opacity shrink-0">
          <img src="/logo-icon.svg" alt="ScoutVision" className="w-7 h-7" />
          <span className="font-bold text-lg tracking-tight">Scout<span className="text-emerald-400">Vision</span></span>
          <span
            className={`ml-1 text-[10px] px-1.5 py-0.5 rounded-full border ${
              dbStatus === 'loading'
                ? 'text-yellow-400 border-yellow-500/30 bg-yellow-500/10'
                : 'text-emerald-400 border-emerald-500/30 bg-emerald-500/10'
            }`}
            title={dbStatus === 'loading' ? 'Indexing players...' : `${dbStatus} players indexed`}
          >
            {dbStatus === 'loading' ? '···' : dbStatus}
          </span>
        </Link>

        <div className="flex items-center gap-1">
          <Link
            to="/"
            className={`px-3 py-1.5 rounded-md text-sm transition-colors ${
              loc.pathname === '/' ? 'bg-gray-800 text-white' : 'text-gray-400 hover:text-white hover:bg-gray-800/50'
            }`}
          >
            <Home className="w-4 h-4 inline mr-1.5" />
            Home
          </Link>
          <Link
            to="/players"
            className={`px-3 py-1.5 rounded-md text-sm transition-colors ${
              loc.pathname.startsWith('/players') ? 'bg-gray-800 text-white' : 'text-gray-400 hover:text-white hover:bg-gray-800/50'
            }`}
          >
            <Search className="w-4 h-4 inline mr-1.5" />
            Players
          </Link>
          <Link
            to="/scout"
            className={`px-3 py-1.5 rounded-md text-sm transition-colors ${
              loc.pathname.startsWith('/scout') ? 'bg-gray-800 text-white' : 'text-gray-400 hover:text-white hover:bg-gray-800/50'
            }`}
          >
            <SlidersHorizontal className="w-4 h-4 inline mr-1.5" />
            Scout
          </Link>
          <Link
            to="/compare"
            className={`px-3 py-1.5 rounded-md text-sm transition-colors ${
              loc.pathname.startsWith('/compare') ? 'bg-gray-800 text-white' : 'text-gray-400 hover:text-white hover:bg-gray-800/50'
            }`}
          >
            <GitCompare className="w-4 h-4 inline mr-1.5" />
            Compare
          </Link>
        </div>
      </div>
    </nav>
  )
}
