import { Routes, Route } from 'react-router-dom'
import Navbar from './components/Navbar'
import Home from './pages/Home'
import Players from './pages/Players'
import PlayerProfile from './pages/PlayerProfile'

export default function App() {
  return (
    <div className="min-h-screen bg-gray-950 text-white">
      <Navbar />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/players" element={<Players />} />
        <Route path="/players/:playerId" element={<PlayerProfile />} />
      </Routes>
    </div>
  )
}
