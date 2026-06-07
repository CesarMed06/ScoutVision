import { Shield, Search, Home, GitCompare } from 'lucide-react'
import { Link, useLocation } from 'react-router-dom'

export default function Navbar() {
  const loc = useLocation()

  return (
    <nav className="border-b border-gray-800 bg-gray-950/90 backdrop-blur-sm sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-14 flex items-center justify-between">
        <Link to="/" className="flex items-center gap-2 text-white hover:text-emerald-400 transition-colors">
          <Shield className="w-6 h-6 text-emerald-400" />
          <span className="font-bold text-lg tracking-tight">ScoutVision</span>
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
