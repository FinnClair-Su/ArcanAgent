import { useState, useEffect, useRef, useCallback } from 'react'
import type { WebSocketMessage, LearningProgress } from '@/types'

interface UseWebSocketOptions {
  onMessage?: (message: WebSocketMessage) => void
  onProgress?: (progress: LearningProgress) => void
  onError?: (error: Event) => void
  onConnect?: () => void
  onDisconnect?: () => void
  reconnectAttempts?: number
  reconnectDelay?: number
}

interface UseWebSocketReturn {
  isConnected: boolean
  lastMessage: WebSocketMessage | null
  sendMessage: (message: any) => void
  connect: (sessionId: string) => void
  disconnect: () => void
  connectionState: 'connecting' | 'connected' | 'disconnected' | 'error'
}

export function useWebSocket(options: UseWebSocketOptions = {}): UseWebSocketReturn {
  const {
    onMessage,
    onProgress,
    onError,
    onConnect,
    onDisconnect,
    reconnectAttempts = 3,
    reconnectDelay = 1000
  } = options

  const [isConnected, setIsConnected] = useState(false)
  const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null)
  const [connectionState, setConnectionState] = useState<'connecting' | 'connected' | 'disconnected' | 'error'>('disconnected')
  
  const socketRef = useRef<WebSocket | null>(null)
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null)
  const reconnectCountRef = useRef(0)
  const sessionIdRef = useRef<string | null>(null)

  const cleanup = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current)
      reconnectTimeoutRef.current = null
    }
    
    if (socketRef.current) {
      socketRef.current.close()
      socketRef.current = null
    }
  }, [])

  const attemptReconnect = useCallback(() => {
    if (reconnectCountRef.current < reconnectAttempts && sessionIdRef.current) {
      reconnectCountRef.current += 1
      console.log(`WebSocket reconnect attempt ${reconnectCountRef.current}/${reconnectAttempts}`)
      
      reconnectTimeoutRef.current = setTimeout(() => {
        connect(sessionIdRef.current!)
      }, reconnectDelay * reconnectCountRef.current)
    } else {
      console.error('WebSocket max reconnection attempts reached')
      setConnectionState('error')
    }
  }, [reconnectAttempts, reconnectDelay])

  const connect = useCallback((sessionId: string) => {
    cleanup()
    
    sessionIdRef.current = sessionId
    setConnectionState('connecting')
    
    try {
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
      const wsUrl = `${protocol}//${window.location.host}/api/v1/learning/ws/${sessionId}`
      
      console.log('Connecting to WebSocket:', wsUrl)
      
      const ws = new WebSocket(wsUrl)
      socketRef.current = ws

      ws.onopen = () => {
        console.log('WebSocket connected')
        setIsConnected(true)
        setConnectionState('connected')
        reconnectCountRef.current = 0
        onConnect?.()
      }

      ws.onclose = (event) => {
        console.log('WebSocket disconnected:', event.code, event.reason)
        setIsConnected(false)
        setConnectionState('disconnected')
        socketRef.current = null
        onDisconnect?.()
        
        // Attempt reconnection if not intentionally closed
        if (event.code !== 1000 && sessionIdRef.current) {
          attemptReconnect()
        }
      }

      ws.onerror = (error) => {
        console.error('WebSocket error:', error)
        setConnectionState('error')
        onError?.(error)
      }

      ws.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data)
          console.log('WebSocket message received:', message)
          
          setLastMessage(message)
          onMessage?.(message)
          
          // Handle specific message types
          if (message.type === 'progress' && onProgress) {
            onProgress(message.data as LearningProgress)
          }
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error)
        }
      }
    } catch (error) {
      console.error('Failed to create WebSocket connection:', error)
      setConnectionState('error')
    }
  }, [cleanup, onConnect, onDisconnect, onError, onMessage, onProgress, attemptReconnect])

  const disconnect = useCallback(() => {
    sessionIdRef.current = null
    cleanup()
    setIsConnected(false)
    setConnectionState('disconnected')
  }, [cleanup])

  const sendMessage = useCallback((message: any) => {
    if (socketRef.current?.readyState === WebSocket.OPEN) {
      try {
        socketRef.current.send(JSON.stringify(message))
        console.log('WebSocket message sent:', message)
      } catch (error) {
        console.error('Failed to send WebSocket message:', error)
      }
    } else {
      console.warn('WebSocket is not connected. Cannot send message:', message)
    }
  }, [])

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      cleanup()
    }
  }, [cleanup])

  return {
    isConnected,
    lastMessage,
    sendMessage,
    connect,
    disconnect,
    connectionState
  }
}