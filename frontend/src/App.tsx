import { Shield, Github } from 'lucide-react'

export default function App() {
  return (
    <div className="min-h-screen bg-gray-950 text-white flex flex-col items-center justify-center p-8">
      <div className="flex items-center gap-3 mb-6">
        <Shield className="w-10 h-10 text-emerald-400" />
        <h1 className="text-4xl font-bold tracking-tight">ScoutVision AI</h1>
      </div>
      <p className="text-gray-400 text-lg mb-8 text-center max-w-md">
        AI-powered football scouting engine. Uncover hidden gems from leagues around the world.
      </p>
      <div className="flex gap-4">
        <a
          href="#"
          className="px-6 py-3 bg-emerald-500 hover:bg-emerald-400 text-black font-semibold rounded-lg transition-colors"
        >
          Explore Players
        </a>
        <a
          href="https://github.com"
          target="_blank"
          rel="noopener noreferrer"
          className="px-6 py-3 border border-gray-700 hover:border-gray-500 rounded-lg transition-colors flex items-center gap-2"
        >
          <Github className="w-5 h-5" />
          Source
        </a>
      </div>
      <div className="mt-12 text-sm text-gray-600">
        Built with StatsBomb Open Data &middot; Llama 3 &middot; FastAPI &middot; React
      </div>
    </div>
  )
}
