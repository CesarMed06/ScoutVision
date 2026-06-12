const BASE = '/api/v1'
const TIMEOUT = 15000

async function get<T>(path: string, timeoutMs = TIMEOUT): Promise<T> {
  const controller = new AbortController()
  const timer = setTimeout(() => controller.abort(), timeoutMs)
  try {
    const res = await fetch(`${BASE}${path}`, { signal: controller.signal })
    if (!res.ok) throw new Error(`GET ${path} failed: ${res.status}`)
    return res.json()
  } finally {
    clearTimeout(timer)
  }
}

export interface HealthResponse {
  status: string
  version: string
  vector_db_initialized: boolean
  vector_db_size: number
}

export interface PlayerSummary {
  player_id: number
  player_name: string
  team: string
  match_id: number
  competition: string
  season: string
}

export interface PlayerMetricsTotals {
  matches: number
  minutes: number
  goals: number
  assists: number
  shots: number
  shots_on_target: number
  xg: number
  xa: number
  goals_per_90: number
  xg_per_90: number
  xa_per_90: number
  shot_accuracy: number
  passes: number
  passes_completed: number
  pass_completion_pct: number
  key_passes: number
  progressive_passes: number
  dribbles: number
  dribbles_completed: number
  dribble_success_pct: number
  carries: number
  progressive_carries: number
  tackles: number
  tackles_won: number
  tackle_success_pct: number
  pressures: number
  interceptions: number
  duels: number
  duels_won: number
  duel_success_pct: number
  aerial_duels: number
  aerial_duels_won: number
  aerial_success_pct: number
  fouls_committed: number
  fouls_won: number
  [key: string]: number | string
}

export interface PlayerMetricsResponse {
  player_id: number
  player_name: string
  matches: number
  match_details: Array<Record<string, number | string>>
  totals: PlayerMetricsTotals
}

export interface AiReportResponse {
  player_id: number
  language: string
  report: string
}

export interface SimilarPlayer {
  player_id: number
  player_name: string
  similarity: number
}

export interface AveragesResponse {
  goals_per_90: number
  xg_per_90: number
  xa_per_90: number
  key_passes_per_90: number
  dribbles_per_90: number
  pass_completion_pct: number
  tackles_per_90: number
  aerial_success_pct: number
  players_sampled?: number
}

export interface FeaturedPlayer {
  player_id: number
  player_name: string
  team: string
  match_id: number
  competition: string
  season: string
}

export interface PhotoResponse {
  player_name: string
  photo_url: string | null
}

export async function searchPlayers(query: string): Promise<PlayerSummary[]> {
  return get<PlayerSummary[]>(`/players?q=${encodeURIComponent(query)}`)
}

export async function getPlayerMetrics(playerId: number): Promise<PlayerMetricsResponse> {
  return get<PlayerMetricsResponse>(`/metrics/player/${playerId}`)
}

export async function getAiReport(playerId: number, lang = 'en'): Promise<AiReportResponse> {
  return get<AiReportResponse>(`/players/${playerId}/report?lang=${lang}`)
}

export async function getFeaturedPlayers(): Promise<FeaturedPlayer[]> {
  return get<FeaturedPlayer[]>('/players/featured')
}

export async function getPlayerPhoto(playerName: string): Promise<PhotoResponse> {
  return get<PhotoResponse>(`/players/photo?player_name=${encodeURIComponent(playerName)}`)
}

export async function getSimilarPlayers(playerId: number): Promise<SimilarPlayer[]> {
  return get<SimilarPlayer[]>(`/players/${playerId}/similar`, 30000)
}

export async function getPlayerAverages(playerName: string): Promise<AveragesResponse> {
  return get<AveragesResponse>(`/metrics/averages/${encodeURIComponent(playerName)}`)
}

export function getVizUrl(type: 'radar' | 'heatmap' | 'passes' | 'shots', playerId: number, matchId?: number): string {
  if (type === 'radar') return `${BASE}/viz/player/${playerId}/radar`
  return `${BASE}/viz/player/${playerId}/${type}?match_id=${matchId}`
}

export async function getHealth(): Promise<HealthResponse> {
  const controller = new AbortController()
  const timer = setTimeout(() => controller.abort(), 5000)
  try {
    const res = await fetch('/health', { signal: controller.signal })
    if (!res.ok) throw new Error(`Health check failed: ${res.status}`)
    return res.json()
  } finally {
    clearTimeout(timer)
  }
}
