// Core Types
export interface User {
  id: string
  preferences: UserPreferences
  currentSession?: string
}

export interface UserPreferences {
  theme: 'light' | 'dark' | 'auto'
  language: string
  notifications: boolean
  autoSave: boolean
}

// Learning System Types
export interface LearningSession {
  id: string
  query: string
  status: 'active' | 'completed' | 'failed'
  stages: LearningStage[]
  currentStage: number
  progress: number
  createdAt: string
  updatedAt: string
  results?: Record<string, AgentResult>
}

export interface LearningStage {
  id: string
  name: string
  description: string
  icon: string
  status: 'pending' | 'in_progress' | 'completed' | 'error'
  progress: number
  startTime?: string
  endTime?: string
  result?: AgentResult
}

export interface AgentResult {
  agent: string
  confidence: number
  executionTime: number
  content: string
  metadata?: Record<string, any>
}

// Arcana Agent Types
export type ArcanaAgentType = 
  | 'the_high_priestess'
  | 'the_hermit' 
  | 'the_magician'
  | 'justice'
  | 'the_empress'

export interface ArcanaAgent {
  name: ArcanaAgentType
  displayName: string
  symbol: string
  description: string
  color: string
  capabilities: string[]
}

// Knowledge Graph Types
export interface GraphNode {
  id: string
  title: string
  tags: string[]
  linkDensity: number
  masteryLevel?: number
  complexity?: number
  x?: number
  y?: number
}

export interface GraphEdge {
  source: string
  target: string
  weight: number
  relationshipType: string
}

export interface GraphData {
  nodes: GraphNode[]
  edges: GraphEdge[]
  statistics: GraphStatistics
}

export interface GraphStatistics {
  totalNotes: number
  totalLinks: number
  avgDegree: number
  density: number
  clusters: number
}

// Notes Types
export interface Note {
  id: string
  title: string
  content: string
  tags: string[]
  createdAt: string
  updatedAt: string
  linkDensity: number
  masteryLevel?: number
  complexity?: number
  links: {
    outgoing: string[]
    incoming: string[]
  }
}

export interface CreateNoteRequest {
  title: string
  content: string
  tags?: string[]
}

export interface UpdateNoteRequest {
  title?: string
  content?: string
  tags?: string[]
}

// System Types
export interface SystemStatus {
  status: 'healthy' | 'degraded' | 'down'
  uptime: number
  version: string
  agents: Record<string, AgentStatus>
}

export interface AgentStatus {
  status: 'online' | 'offline' | 'error'
  lastSeen: string
  executionCount: number
  avgExecutionTime: number
  errorRate: number
}

export interface SystemConfig {
  system: {
    version: string
    debug: boolean
    logLevel: string
  }
  api: {
    host: string
    port: number
    enableDocs: boolean
  }
  learning: {
    maxSessions: number
    sessionTimeoutMinutes: number
  }
  agents: {
    maxToolCallLoops: number
    enabledAgents: string[]
  }
}

export interface PerformanceMetrics {
  cpu: number
  memory: number
  apiResponseTime: number
  cacheHitRate: number
  errorRate: number
}

// WebSocket Types
export interface WebSocketMessage {
  type: 'progress' | 'status' | 'result' | 'error'
  sessionId: string
  data: any
  timestamp: string
}

export interface LearningProgress {
  sessionId: string
  currentStage: number
  progress: number
  stageProgress: number
  estimatedTimeRemaining: number
  lastUpdate: string
}

// API Response Types
export interface ApiResponse<T = any> {
  success: boolean
  data: T
  message?: string
  error?: string
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  pageSize: number
  hasNext: boolean
  hasPrev: boolean
}

// Search Types
export interface SearchResult {
  id: string
  title: string
  content: string
  score: number
  highlights: string[]
  type: 'note' | 'concept' | 'tag'
}

export interface SearchQuery {
  query: string
  type?: 'semantic' | 'structural' | 'hybrid'
  limit?: number
  offset?: number
}

// Learning Path Types
export interface LearningPath {
  path: string[]
  totalDistance: number
  estimatedLearningTime: number
  difficultyProgression: number[]
}

// Error Types
export interface AppError {
  code: string
  message: string
  details?: any
  timestamp: string
}