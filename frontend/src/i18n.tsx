import { createContext, useContext, useEffect, useState, type ReactNode } from 'react'

export type Language = 'en' | 'es'

const translations: Record<string, string> = {
  'Indexing players...': 'Indexando jugadores...',
  'players indexed': 'jugadores indexados',
  'Interface language': 'Idioma de la interfaz',
  Demo: 'Demostración',
  Home: 'Inicio', Players: 'Jugadores', Scout: 'Buscar', Compare: 'Comparar',
  'Player Discovery': 'Descubrimiento de jugadores',
  'Search through thousands of players from top European leagues. Find prospects by name, team, or competition.': 'Busca entre miles de jugadores de las principales ligas europeas. Encuentra promesas por nombre, equipo o competición.',
  'Advanced Metrics': 'Estadísticas avanzadas',
  'Deep-dive into per-90 stats, percentile comparisons, and radar charts. xG, xA, progressive passes, and more.': 'Analiza estadísticas por 90 minutos, comparaciones percentiles y gráficos de radar. xG, xA, pases progresivos y mucho más.',
  'AI Scouting Reports': 'Informes de scouting con IA',
  'Get natural language scouting reports powered by Llama 3. Every player evaluated with strengths, weaknesses, and a grade.': 'Genera informes de scouting con Llama 3. Evalúa las fortalezas, debilidades y calificación de cada jugador.',
  'AI-powered football scouting engine. Uncover hidden gems from leagues around the world.': 'Plataforma de scouting de fútbol con IA. Descubre talentos ocultos en ligas de todo el mundo.',
  'Explore Players': 'Explorar jugadores', Source: 'Código fuente',
  'Search players by name...': 'Buscar jugadores por nombre...',
  'Built with StatsBomb Open Data · Llama 3 · FastAPI · React': 'Desarrollado con datos abiertos de StatsBomb · Llama 3 · FastAPI · React',
  'Featured Players': 'Jugadores destacados',
  'No players found': 'No se encontraron jugadores',
  'Scout Filter': 'Filtros de scouting', active: 'activos',
  'Min Goals/90': 'Mín. goles/90', 'Min xG/90': 'Mín. xG/90', 'Min xA/90': 'Mín. xA/90',
  'Min Key Passes/90': 'Mín. pases clave/90', 'Min Tackles/90': 'Mín. entradas/90',
  'Min Pass %': 'Mín. pases %', 'Min Dribble %': 'Mín. regates %', 'Min Aerial %': 'Mín. duelos aéreos %',
  'Min Pressures/90': 'Mín. presiones/90', 'Sort by': 'Ordenar por',
  'High → Low': 'Mayor → menor', 'Low → High': 'Menor → mayor',
  'Apply Filters': 'Aplicar filtros', 'Show All Players': 'Mostrar todos los jugadores',
  'No players match your filters': 'Ningún jugador coincide con los filtros',
  'Try lowering the thresholds': 'Prueba a reducir los valores mínimos',
  'players found': 'jugadores encontrados', Page: 'Página', of: 'de', Previous: 'Anterior', Next: 'Siguiente',
  'Adjust the filters above and click "Apply Filters"': 'Ajusta los filtros y pulsa «Aplicar filtros»',
  'Find players by minimum performance thresholds': 'Encuentra jugadores según su rendimiento mínimo',
  'Player not found': 'Jugador no encontrado', 'No data': 'Sin datos', 'Back to Players': 'Volver a jugadores',
  '1 match': '1 partido', matches: 'partidos', players: 'jugadores',
  Attack: 'Ataque', Passing: 'Pases', 'Dribbling & Carries': 'Regates y conducciones',
  Defense: 'Defensa', Physical: 'Físico', Efficiency: 'Eficiencia',
  'Per 90 vs Average': 'Por 90 min vs. promedio', 'Avg from': 'Promedio de',
  Goals: 'Goles', Assists: 'Asistencias', Shots: 'Tiros', 'Shots On Target': 'Tiros a puerta',
  Passes: 'Pases', 'Passes Completed': 'Pases completados', 'Key Passes': 'Pases clave',
  'Prog. Passes': 'Pases prog.', 'Final Third Passes': 'Pases al último tercio',
  Dribbles: 'Regates', 'Dribbles Completed': 'Regates completados', Carries: 'Conducciones', 'Prog. Carries': 'Conducciones prog.',
  Tackles: 'Entradas', 'Tackles Won': 'Entradas ganadas', Interceptions: 'Intercepciones', Pressures: 'Presiones',
  'Ball Recoveries': 'Recuperaciones de balón',
  'Aerial Duels': 'Duelos aéreos', 'Aerial Duels Won': 'Duelos aéreos ganados', Duels: 'Duelos',
  'Duels Won': 'Duelos ganados', 'Fouls Won': 'Faltas recibidas',
  'Fouls Comm.': 'Faltas cometidas', 'Pass %': 'Pases %', 'Shot Acc.': 'Precisión de tiro',
  'Dribble %': 'Regates %', 'Duels Won %': 'Duelos ganados %', 'Tackle %': 'Entradas %',
  'Aerial %': 'Duelos aéreos %', 'AI Scouting Report': 'Informe de scouting con IA',
  'Scout Report': 'Informe de scouting', 'Similar Players': 'Jugadores similares',
  match: 'coincidencia', 'Match Log': 'Registro de partidos', Match: 'Partido', Min: 'Min',
  'View visualizations': 'Ver visualizaciones', 'Visualizations —': 'Visualizaciones —',
  Heatmap: 'Mapa de calor', 'Pass Map': 'Mapa de pases', 'Shot Map': 'Mapa de tiros',
  'Not available for this match': 'No disponible para este partido', 'Loading…': 'Cargando…',
  'Page not found': 'Página no encontrada',
  "The page you're looking for doesn't exist or has been moved.": 'La página que buscas no existe o se ha movido.',
  'Go Home': 'Ir al inicio', 'Browse Players': 'Ver jugadores', 'Compare Players': 'Comparar jugadores',
  'Change player': 'Cambiar jugador', Player: 'Jugador', 'Select Player': 'Seleccionar jugador',
  'Try again': 'Intentar de nuevo', 'Search players...': 'Buscar jugadores...',
  'Loading player data... (first load may take ~30s)': 'Cargando datos del jugador... (la primera carga puede tardar ~30 s)',
  'Could not load player': 'No se pudo cargar el jugador',
  'Comparison Radar': 'Radar comparativo',
  'Computing league averages... (first load ~15s)': 'Calculando promedios de la liga... (la primera carga tarda ~15 s)',
  'Player A vs League Avg (blue dashed) — scaled against league averages': 'Jugador A vs. promedio de la liga (línea azul discontinua), según los promedios de la liga',
  'Stats Comparison': 'Comparación de estadísticas', 'Green indicates the better value': 'El verde indica el mejor valor',
  Metric: 'Estadística', 'Select two players above to compare their stats.': 'Selecciona dos jugadores para comparar sus estadísticas.',
  'Goals/90': 'Goles/90', 'Key Passes/90': 'Pases clave/90', 'Dribbles/90': 'Regates/90',
  'Pressures/90': 'Presiones/90',
  'Prog. Passes/90': 'Pases prog./90', 'Prog. Carries/90': 'Conducciones prog./90',
  'Int./90': 'Intercepciones/90', 'Tackles/90': 'Entradas/90',
  Dribbling: 'Regates', 'xG/90': 'xG/90', 'xA/90': 'xA/90',
  'Something went wrong': 'Algo salió mal',
  'The app encountered an unexpected error. This is likely temporary — try reloading.': 'La aplicación encontró un error inesperado. Puede ser temporal; prueba a recargar.',
  'Reload Page': 'Recargar página',  'Error details': 'Detalles del error', Avg: 'Prom.',
  'Search failed': 'Error en la búsqueda',
  'No response body': 'La respuesta no contiene datos',
  'Report generation failed': 'No se pudo generar el informe. Comprueba la conexión y la configuración de la API.',
  'Report timed out': 'Se agotó el tiempo de espera del informe',
  'Stream failed': 'Error al recibir el informe',
  'No match data found for player ID': 'No se encontraron datos de partidos para el jugador',
  'GROQ_API_KEY not configured': 'La clave de Groq no está configurada',
  'Error:': 'Error:',
  Minutes: 'Minutos', Visualizations: 'Visualizaciones',
}

interface LanguageContextValue {
  language: Language
  setLanguage: (language: Language) => void
  t: (text: string) => string
}

const LanguageContext = createContext<LanguageContextValue>({
  language: 'en',
  setLanguage: () => {},
  t: text => text,
})

export function LanguageProvider({ children }: { children: ReactNode }) {
  const [language, setLanguage] = useState<Language>(() =>
    localStorage.getItem('scoutvision-language') === 'es' ? 'es' : 'en',
  )

  useEffect(() => {
    localStorage.setItem('scoutvision-language', language)
    document.documentElement.lang = language
  }, [language])

  const t = (text: string) => translateText(text, language)

  return (
    <LanguageContext.Provider value={{ language, setLanguage, t }}>
      {children}
    </LanguageContext.Provider>
  )
}

export function useLanguage() {
  return useContext(LanguageContext)
}

function translateText(text: string, language: Language): string {
  if (language !== 'es') return text
  if (text.startsWith('Could not load player ')) return `${translations['Could not load player']}${text.slice('Could not load player'.length)}`
  if (text.startsWith('No match data found for player ID ')) return `${translations['No match data found for player ID']} ${text.slice('No match data found for player ID '.length)}`
  if (text.startsWith('GROQ_API_KEY not configured')) return translations['GROQ_API_KEY not configured']
  if (text.startsWith('Error: ')) {
    const detail = text.slice('Error: '.length)
    if (/^HTTP \d+$/.test(detail)) return `${translations['Report generation failed']} (${detail})`
    const translated = translateText(detail, language)
    return translated === detail ? translations['Report generation failed'] : `${translations['Error:']} ${translated}`
  }
  return translations[text] || text
}

export function translate(text: string): string {
  return translateText(text, localStorage.getItem('scoutvision-language') === 'es' ? 'es' : 'en')
}
