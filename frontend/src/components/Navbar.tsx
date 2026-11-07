import { useEffect, useState } from 'react'
import { Search, Home, GitCompare, SlidersHorizontal } from 'lucide-react'
import { Link, useLocation } from 'react-router-dom'
import { getHealth } from '../api'
import { useLanguage } from '../i18n'

export default function Navbar() {
  const loc = useLocation()
  const { language, setLanguage, t } = useLanguage()
  const [dbStatus, setDbStatus] = useState<'loading' | number>('loading')
  const [demoMode, setDemoMode] = useState(false)

  useEffect(() => {
    let active = true
    function poll() {
      getHealth().then(h => {
        if (!active) return
        setDemoMode(h.demo_mode)
        if (h.vector_db_initialized) setDbStatus(h.vector_db_size)
        else setTimeout(poll, 2000)
      }).catch(() => { if (active) setTimeout(poll, 5000) })
    }
    poll()
    return () => { active = false }
  }, [])

  return (
    <nav className="border-b border-gray-800 bg-gray-950/90 backdrop-blur-sm sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-3 sm:px-6 lg:px-8 h-14 flex items-center justify-between">
        <Link to="/" className="flex items-center gap-2.5 text-white hover:opacity-80 transition-opacity shrink-0">
          <img src="/logo-icon.svg" alt="ScoutVision" className="w-7 h-7" />
          <span className="hidden sm:inline font-bold text-lg tracking-tight">Scout<span className="text-emerald-400">Vision</span></span>
          {demoMode && <span className="hidden sm:inline-block text-[10px] px-1.5 py-0.5 rounded-full border border-amber-500/30 bg-amber-500/10 text-amber-300">{t('Demo')}</span>}
          <span
            className={`ml-1 text-[10px] px-1.5 py-0.5 rounded-full border ${
              dbStatus === 'loading'
                ? 'text-yellow-400 border-yellow-500/30 bg-yellow-500/10'
                : 'text-emerald-400 border-emerald-500/30 bg-emerald-500/10'
            }`}
            role="status"
            title={dbStatus === 'loading' ? t('Indexing players...') : `${dbStatus} ${t('players indexed')}`}
            aria-label={dbStatus === 'loading' ? t('Indexing players...') : `${dbStatus} ${t('players indexed')}`}
          >
            {dbStatus === 'loading' ? '···' : dbStatus}
          </span>
        </Link>

        <div className="flex items-center gap-1">
          <Link
            to="/"
            aria-label={t('Home')}
            aria-current={loc.pathname === '/' ? 'page' : undefined}
            className={`px-2 sm:px-3 py-1.5 rounded-md text-sm transition-colors ${
              loc.pathname === '/' ? 'bg-gray-800 text-white' : 'text-gray-400 hover:text-white hover:bg-gray-800/50'
            }`}
          >
            <Home className="w-4 h-4 inline mr-1.5" />
            <span className="hidden sm:inline">{t('Home')}</span>
          </Link>
          <Link
            to="/players"
            aria-label={t('Players')}
            aria-current={loc.pathname.startsWith('/players') ? 'page' : undefined}
            className={`px-2 sm:px-3 py-1.5 rounded-md text-sm transition-colors ${
              loc.pathname.startsWith('/players') ? 'bg-gray-800 text-white' : 'text-gray-400 hover:text-white hover:bg-gray-800/50'
            }`}
          >
            <Search className="w-4 h-4 inline mr-1.5" />
            <span className="hidden sm:inline">{t('Players')}</span>
          </Link>
          <Link
            to="/scout"
            aria-label={t('Scout')}
            aria-current={loc.pathname.startsWith('/scout') ? 'page' : undefined}
            className={`px-2 sm:px-3 py-1.5 rounded-md text-sm transition-colors ${
              loc.pathname.startsWith('/scout') ? 'bg-gray-800 text-white' : 'text-gray-400 hover:text-white hover:bg-gray-800/50'
            }`}
          >
            <SlidersHorizontal className="w-4 h-4 inline mr-1.5" />
            <span className="hidden sm:inline">{t('Scout')}</span>
          </Link>
          <Link
            to="/compare"
            aria-label={t('Compare')}
            aria-current={loc.pathname.startsWith('/compare') ? 'page' : undefined}
            className={`px-2 sm:px-3 py-1.5 rounded-md text-sm transition-colors ${
              loc.pathname.startsWith('/compare') ? 'bg-gray-800 text-white' : 'text-gray-400 hover:text-white hover:bg-gray-800/50'
            }`}
          >
            <GitCompare className="w-4 h-4 inline mr-1.5" />
            <span className="hidden sm:inline">{t('Compare')}</span>
          </Link>
        </div>
        <div className="ml-1 sm:ml-2 flex items-center rounded-md bg-gray-900 p-0.5" role="group" aria-label={language === 'en' ? 'Interface language' : 'Idioma de la interfaz'}>
          <button type="button" onClick={() => setLanguage('en')} aria-label="English" aria-pressed={language === 'en'} className={`px-1.5 sm:px-2 py-1 rounded text-xs font-medium ${language === 'en' ? 'bg-gray-700 text-white' : 'text-gray-400 hover:text-white'}`}>
            <svg className="w-4 h-3 sm:w-5 sm:h-4 rounded-sm" viewBox="0 0 60 30" aria-hidden="true"><rect fill="#012169" width="60" height="30"/><path d="M0 0l60 30M60 0L0 30" stroke="#fff" strokeWidth="10"/><path d="M30 0v30M0 15h60" stroke="#fff" strokeWidth="12"/><path d="M30 0v30M0 15h60" stroke="#C8102E" strokeWidth="8"/></svg>
          </button>
          <button type="button" onClick={() => setLanguage('es')} aria-label="Español" aria-pressed={language === 'es'} className={`px-1.5 sm:px-2 py-1 rounded text-xs font-medium ${language === 'es' ? 'bg-gray-700 text-white' : 'text-gray-400 hover:text-white'}`}>
            <svg className="w-4 h-3 sm:w-5 sm:h-4 rounded-sm" viewBox="0 0 60 30" aria-hidden="true"><rect fill="#AA151B" width="60" height="12"/><rect fill="#F1BF00" y="12" width="60" height="6"/><rect fill="#AA151B" y="18" width="60" height="12"/></svg>
          </button>
        </div>
      </div>
    </nav>
  )
}
