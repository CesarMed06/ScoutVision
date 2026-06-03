const BASE = '/api/v1'

async function get<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE}${path}`)
  if (!res.ok) throw new Error(`GET ${path} failed: ${res.status}`)
  return res.json()
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

export async function searchPlayers(query: string): Promise<PlayerSummary[]> {
  return get<PlayerSummary[]>(`/players?q=${encodeURIComponent(query)}`)
}

export async function getPlayerMetrics(playerId: number): Promise<PlayerMetricsResponse> {
  return get<PlayerMetricsResponse>(`/metrics/player/${playerId}`)
}

export async function getAiReport(playerId: number, lang = 'en'): Promise<AiReportResponse> {
  return get<AiReportResponse>(`/players/${playerId}/report?lang=${lang}`)
}

export function getVizUrl(type: 'radar' | 'heatmap' | 'passes' | 'shots', playerId: number, matchId?: number): string {
  if (type === 'radar') return `${BASE}/viz/player/${playerId}/radar`
  return `${BASE}/viz/player/${playerId}/${type}?match_id=${matchId}`
}
