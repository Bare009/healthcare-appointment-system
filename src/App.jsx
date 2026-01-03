import { Routes, Route } from 'react-router-dom'
import AnalyzePage from './pages/AnalyzePage'
import QueuePage from './pages/QueuePage'

function App() {
  return (
    <Routes>
      <Route path="/" element={<AnalyzePage />} />
      <Route path="/analyze" element={<AnalyzePage />} />
      <Route path="/queue" element={<QueuePage />} />
    </Routes>
  )
}

export default App

