import { useState, useCallback } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '@services/api'
import { useWebSocket } from './useWebSocket'
import { WS_EVENTS } from '@utils/constants'
import type { LearningSession, LearningProgress, WebSocketMessage, ApiResponse } from '@/types'

interface UseLearningSessionOptions {
  enableWebSocket?: boolean
  onProgress?: (progress: LearningProgress) => void
  onStageComplete?: (stage: string) => void
  onSessionComplete?: (session: LearningSession) => void
  onError?: (error: string) => void
}

interface UseLearningSessionReturn {
  session: LearningSession | null
  isLoading: boolean
  error: string | null
  startSession: (query: string) => Promise<void>
  executeAgent: (agentName: string, query: string) => Promise<void>
  getSession: (sessionId: string) => void
  wsConnectionState: 'connecting' | 'connected' | 'disconnected' | 'error'
}

export function useLearningSession(options: UseLearningSessionOptions = {}): UseLearningSessionReturn {
  const {
    enableWebSocket = true,
    onProgress,
    onStageComplete,
    onSessionComplete,
    onError
  } = options

  const [session, setSession] = useState<LearningSession | null>(null)
  const [error, setError] = useState<string | null>(null)
  
  const queryClient = useQueryClient()

  // WebSocket connection
  const { connect, disconnect, connectionState } = useWebSocket({
    onProgress: (progress) => {
      console.log('Learning progress update:', progress)
      onProgress?.(progress)
      
      // Update local session state
      setSession(prev => {
        if (!prev || prev.id !== progress.sessionId) return prev
        
        return {
          ...prev,
          currentStage: progress.currentStage,
          progress: progress.progress,
          updatedAt: progress.lastUpdate,
          stages: prev.stages.map((stage, index) => {
            if (index === progress.currentStage) {
              return {
                ...stage,
                progress: progress.stageProgress,
                status: 'in_progress' as const
              }
            }
            if (index < progress.currentStage) {
              return {
                ...stage,
                status: 'completed' as const,
                progress: 1
              }
            }
            return stage
          })
        }
      })
    },
    
    onMessage: (message: WebSocketMessage) => {
      console.log('WebSocket message:', message)
      
      switch (message.type) {
        case WS_EVENTS.STAGE_COMPLETE:
          onStageComplete?.(message.data.stage)
          break
          
        case WS_EVENTS.SESSION_COMPLETE:
          setSession(message.data.session)
          onSessionComplete?.(message.data.session)
          disconnect()
          break
          
        case WS_EVENTS.ERROR:
          setError(message.data.error)
          onError?.(message.data.error)
          break
      }
    },
    
    onError: (error) => {
      console.error('WebSocket error:', error)
      setError('WebSocket connection failed')
      onError?.('WebSocket connection failed')
    }
  })

  // Start learning session mutation
  const startSessionMutation = useMutation({
    mutationFn: async (query: string) => {
      const response = await api.learning.orchestrate(query, enableWebSocket)
      return response
    },
    onSuccess: (response: ApiResponse<LearningSession>) => {
      if (response.success && response.data) {
        setSession(response.data)
        setError(null)
        
        // Connect to WebSocket if enabled
        if (enableWebSocket) {
          connect(response.data.id)
        }
        
        // Cache the session
        queryClient.setQueryData(['learning-session', response.data.id], response.data)
      } else {
        setError(response.error || 'Failed to start learning session')
      }
    },
    onError: (error: any) => {
      console.error('Failed to start learning session:', error)
      setError(error.message || 'Failed to start learning session')
      onError?.(error.message || 'Failed to start learning session')
    }
  })

  // Execute individual agent mutation
  const executeAgentMutation = useMutation({
    mutationFn: async ({ agentName, query }: { agentName: string; query: string }) => {
      // Map agent names to API endpoints
      const agentEndpoints: Record<string, (query: string, sessionId?: string) => Promise<ApiResponse>> = {
        'the_high_priestess': api.learning.assessKnowledge,
        'the_hermit': api.learning.planPath,
        'the_magician': api.learning.generateContent,
        'justice': api.learning.evaluateUnderstanding,
        'the_empress': api.learning.consolidateMemory
      }
      
      const endpoint = agentEndpoints[agentName]
      if (!endpoint) {
        throw new Error(`Unknown agent: ${agentName}`)
      }
      
      return endpoint(query, session?.id)
    },
    onSuccess: (response) => {
      if (!response.success) {
        setError(response.error || 'Agent execution failed')
      }
    },
    onError: (error: any) => {
      console.error('Failed to execute agent:', error)
      setError(error.message || 'Failed to execute agent')
      onError?.(error.message || 'Failed to execute agent')
    }
  })

  // Get session query
  const { isLoading: isSessionLoading } = useQuery({
    queryKey: ['learning-session', session?.id],
    queryFn: async () => {
      if (!session?.id) return null
      const response = await api.learning.getSession(session.id)
      return response.success ? response.data : null
    },
    enabled: !!session?.id,
    refetchInterval: enableWebSocket ? false : 5000 // Poll if WebSocket disabled
  })

  const startSession = useCallback(async (query: string) => {
    setError(null)
    await startSessionMutation.mutateAsync(query)
  }, [startSessionMutation])

  const executeAgent = useCallback(async (agentName: string, query: string) => {
    setError(null)
    await executeAgentMutation.mutateAsync({ agentName, query })
  }, [executeAgentMutation, session?.id])

  const getSession = useCallback((sessionId: string) => {
    queryClient.invalidateQueries({ queryKey: ['learning-session', sessionId] })
  }, [queryClient])

  return {
    session,
    isLoading: startSessionMutation.isPending || executeAgentMutation.isPending || isSessionLoading,
    error,
    startSession,
    executeAgent,
    getSession,
    wsConnectionState: connectionState
  }
}