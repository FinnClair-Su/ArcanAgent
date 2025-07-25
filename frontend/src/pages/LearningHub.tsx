import { useState } from 'react'
import { useParams } from 'react-router-dom'
import { Card, CardHeader, CardTitle, CardDescription, CardContent, Button } from '@components/ui'
import { ArcanaGrid, LearningProgress } from '@components/arcana'
import { useLearningSession } from '@/hooks'
import { APP_PHILOSOPHY } from '@utils/constants'

export function LearningHub() {
  const { sessionId } = useParams()
  const [query, setQuery] = useState('')
  
  const {
    session,
    isLoading,
    error,
    startSession,
    executeAgent,
    wsConnectionState
  } = useLearningSession({
    enableWebSocket: true,
    onProgress: (progress: any) => {
      console.log('Learning progress:', progress)
    },
    onStageComplete: (stage: any) => {
      console.log('Stage completed:', stage)
    },
    onSessionComplete: (session: any) => {
      console.log('Session completed:', session)
    },
    onError: (error: any) => {
      console.error('Learning session error:', error)
    }
  })
  
  // Suppress unused variable warning
  console.log('Session ID:', sessionId)

  const handleStartSession = async () => {
    if (query.trim()) {
      await startSession(query.trim())
    }
  }

  const handleExecuteAgent = async (agentName: string, agentQuery: string) => {
    await executeAgent(agentName, agentQuery || query)
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
          Learning Hub
        </h1>
        <p className="text-gray-600 dark:text-gray-300">
          Embark on a learning journey guided by the five Arcana agents
        </p>
        <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
          {APP_PHILOSOPHY}
        </p>
      </div>

      {/* Learning Query Input */}
      {!session && (
        <Card>
          <CardHeader>
            <CardTitle>Start Your Learning Journey</CardTitle>
            <CardDescription>
              Enter a topic or question you'd like to learn about. Our five Arcana agents will guide you through a comprehensive learning experience.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div>
                <label htmlFor="query" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  What would you like to learn about?
                </label>
                <textarea
                  id="query"
                  rows={3}
                  className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500 dark:border-gray-600 dark:bg-gray-800 dark:text-white"
                  placeholder="e.g., 'Explain quantum computing fundamentals' or 'How do neural networks work?'"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                />
              </div>
              <Button 
                onClick={handleStartSession}
                disabled={!query.trim() || isLoading}
                className="w-full"
              >
                {isLoading ? 'Starting Session...' : 'Begin Learning Session'}
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Error Display */}
      {error && (
        <Card className="border-red-200 bg-red-50 dark:border-red-800 dark:bg-red-900/20">
          <CardContent className="pt-6">
            <div className="flex items-center space-x-2">
              <span className="text-red-600 dark:text-red-400">⚠️</span>
              <span className="text-red-800 dark:text-red-200">{error}</span>
            </div>
          </CardContent>
        </Card>
      )}

      {/* WebSocket Connection Status */}
      {session && (
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2 text-sm">
            <span className="text-gray-600 dark:text-gray-300">Real-time updates:</span>
            <div className="flex items-center space-x-1">
              <div className={`w-2 h-2 rounded-full ${
                wsConnectionState === 'connected' ? 'bg-green-500' : 
                wsConnectionState === 'connecting' ? 'bg-yellow-500' : 
                'bg-red-500'
              }`} />
              <span className="text-xs text-gray-500 dark:text-gray-400 capitalize">
                {wsConnectionState}
              </span>
            </div>
          </div>
          
          {session && (
            <div className="text-sm text-gray-500 dark:text-gray-400">
              Session: {session.id}
            </div>
          )}
        </div>
      )}

      {/* Learning Progress */}
      {session && (
        <LearningProgress session={session} />
      )}

      {/* Arcana Agents Grid */}
      {session && (
        <div>
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
            Arcana Agents
          </h2>
          <ArcanaGrid
            session={session}
            onExecuteAgent={handleExecuteAgent}
            onViewResult={(agentName) => {
              console.log('View result for agent:', agentName)
              // TODO: Implement result viewing
            }}
            disabled={isLoading}
          />
        </div>
      )}

      {/* Session Results */}
      {session?.status === 'completed' && session.results && (
        <Card>
          <CardHeader>
            <CardTitle>Learning Session Results</CardTitle>
            <CardDescription>
              Your complete learning journey results
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {Object.entries(session.results).map(([agentName, result]) => (
                <div key={agentName} className="border rounded-lg p-4">
                  <h4 className="font-medium text-gray-900 dark:text-white mb-2">
                    {agentName.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                  </h4>
                  <p className="text-sm text-gray-600 dark:text-gray-300 mb-2">
                    Confidence: {Math.round((result as any).confidence * 100)}% | 
                    Execution Time: {(result as any).executionTime}ms
                  </p>
                  <div className="text-sm bg-gray-50 dark:bg-gray-800 rounded p-3">
                    {(result as any).content}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}