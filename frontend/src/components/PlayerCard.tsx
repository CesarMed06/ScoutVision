import { useState, useEffect } from 'react'
import { ImageIcon } from 'lucide-react'
import { Link } from 'react-router-dom'
import { getPlayerPhoto } from '../api'
import type { PlayerSummary } from '../api'

export default function PlayerCard({ player }: { player: PlayerSummary }) {
  const [photo, setPhoto] = useState<string | null>(null)

  useEffect(() => {
    getPlayerPhoto(player.player_name)
      .then((p) => setPhoto(p.photo_url))
      .catch(() => {})
  }, [player.player_name])

  return (
    <Link
      to={`/players/${player.player_id}`}
      className="block p-4 bg-gray-900 border border-gray-800 rounded-lg hover:border-emerald-500/50 hover:bg-gray-800/50 transition-all group"
    >
      <div className="flex items-start gap-3">
        {photo ? (
          <img src={photo} alt={player.player_name} className="w-10 h-10 rounded-full object-cover shrink-0 border border-gray-700" />
        ) : (
          <div className="w-10 h-10 rounded-full bg-gray-800 flex items-center justify-center shrink-0 group-hover:bg-emerald-900/30 transition-colors">
            <ImageIcon className="w-5 h-5 text-gray-400 group-hover:text-emerald-400 transition-colors" />
          </div>
        )}
        <div className="min-w-0">
          <h3 className="text-white font-medium truncate group-hover:text-emerald-400 transition-colors">
            {player.player_name}
          </h3>
          {player.team && (
            <p className="text-sm text-gray-400 truncate">{player.team}</p>
          )}
          {player.competition && (
            <p className="text-xs text-gray-500 mt-0.5">
              {player.competition}{player.season ? ` · ${player.season}` : ''}
            </p>
          )}
        </div>
      </div>
    </Link>
  )
}
