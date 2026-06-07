import { Link } from 'react-router-dom'
import { Home, Search } from 'lucide-react'

export default function NotFound() {
  return (
    <div className="flex flex-col items-center justify-center py-32 px-6 text-center">
      <div className="text-8xl font-bold text-gray-800 mb-4">404</div>
      <h1 className="text-2xl font-bold text-white mb-2">Page not found</h1>
      <p className="text-gray-400 mb-8 max-w-md">
        The page you're looking for doesn't exist or has been moved.
      </p>
      <div className="flex gap-4">
        <Link
          to="/"
          className="px-6 py-3 bg-emerald-500 hover:bg-emerald-400 text-black font-semibold rounded-lg transition-all flex items-center gap-2"
        >
          <Home className="w-4 h-4" />
          Go Home
        </Link>
        <Link
          to="/players"
          className="px-6 py-3 border border-gray-700 hover:border-gray-500 text-gray-300 rounded-lg transition-all flex items-center gap-2"
        >
          <Search className="w-4 h-4" />
          Browse Players
        </Link>
      </div>
    </div>
  )
}
