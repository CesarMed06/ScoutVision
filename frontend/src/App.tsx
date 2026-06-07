import { Routes, Route } from 'react-router-dom'
import Navbar from './components/Navbar'
import Home from './pages/Home'
import Players from './pages/Players'
import PlayerProfile from './pages/PlayerProfile'
import Compare from './pages/Compare'
import NotFound from './pages/NotFound'

export default function App() {
  return (
    <div className="min-h-screen bg-gray-950 text-white">
      <Navbar />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/players" element={<Players />} />
        <Route path="/players/:playerId" element={<PlayerProfile />} />
        <Route path="/compare" element={<Compare />} />
        <Route path="*" element={<NotFound />} />
      </Routes>
    </div>
  )
}
