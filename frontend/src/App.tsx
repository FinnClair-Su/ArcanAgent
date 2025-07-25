import { Routes, Route } from 'react-router-dom'
import { Layout } from '@components/layout/Layout'
import { HomePage } from '@pages/HomePage'
import { LearningHub } from '@pages/LearningHub'
import { KnowledgeGraph } from '@pages/KnowledgeGraph'
import { NotesManager } from '@pages/NotesManager'
import { SystemConsole } from '@pages/SystemConsole'

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/learning" element={<LearningHub />} />
        <Route path="/learning/:sessionId" element={<LearningHub />} />
        <Route path="/graph" element={<KnowledgeGraph />} />
        <Route path="/notes" element={<NotesManager />} />
        <Route path="/notes/:noteId" element={<NotesManager />} />
        <Route path="/system/*" element={<SystemConsole />} />
      </Routes>
    </Layout>
  )
}

export default App