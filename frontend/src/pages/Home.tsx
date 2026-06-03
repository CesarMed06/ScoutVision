import { Link } from 'react-router-dom'
import { Shield, Search, BarChart3, FileText, Github, ArrowRight } from 'lucide-react'

const features = [
  { icon: Search, title: 'Player Discovery', desc: 'Search through thousands of players from top European leagues. Find prospects by name, team, or competition.' },
  { icon: BarChart3, title: 'Advanced Metrics', desc: 'Deep-dive into per-90 stats, percentile comparisons, and radar charts. xG, xA, progressive passes, and more.' },
  { icon: FileText, title: 'AI Scouting Reports', desc: 'Get natural language scouting reports powered by Llama 3. Every player evaluated with strengths, weaknesses, and a grade.' },
]

export default function Home() {
  return (
    <div className="min-h-[calc(100vh-3.5rem)] flex flex-col">
      <section className="flex-1 flex flex-col items-center justify-center px-6 py-20 text-center">
        <div className="flex items-center gap-3 mb-6">
          <Shield className="w-12 h-12 text-emerald-400" />
          <h1 className="text-5xl sm:text-6xl font-bold tracking-tight text-white">
            ScoutVision
          </h1>
        </div>
        <p className="text-gray-400 text-lg sm:text-xl mb-10 max-w-xl">
          AI-powered football scouting engine. Uncover hidden gems from leagues around the world.
        </p>
        <div className="flex flex-wrap gap-4 justify-center">
          <Link
            to="/players"
            className="px-6 py-3 bg-emerald-500 hover:bg-emerald-400 text-black font-semibold rounded-lg transition-all flex items-center gap-2"
          >
            Explore Players
            <ArrowRight className="w-4 h-4" />
          </Link>
          <a
            href="https://github.com/CesarMed06/ScoutVision"
            target="_blank"
            rel="noopener noreferrer"
            className="px-6 py-3 border border-gray-700 hover:border-gray-500 hover:text-white text-gray-300 rounded-lg transition-all flex items-center gap-2"
          >
            <Github className="w-5 h-5" />
            Source
          </a>
        </div>
        <div className="mt-12 text-sm text-gray-600">
          Built with StatsBomb Open Data · Llama 3 · FastAPI · React
        </div>
      </section>

      <section className="max-w-5xl mx-auto px-6 pb-20 grid sm:grid-cols-3 gap-6">
        {features.map((f) => (
          <div key={f.title} className="p-6 bg-gray-900/50 border border-gray-800 rounded-xl">
            <f.icon className="w-8 h-8 text-emerald-400 mb-4" />
            <h3 className="text-white font-semibold mb-2">{f.title}</h3>
            <p className="text-sm text-gray-400 leading-relaxed">{f.desc}</p>
          </div>
        ))}
      </section>
    </div>
  )
}
