import type {
  LearningSession,
  Note,
  CreateNoteRequest,
  UpdateNoteRequest,
  GraphData,
  LearningPath,
  SystemStatus,
  SystemConfig,
  ApiResponse,
  SearchResult,
  SearchQuery
} from '@/types'
import { API_BASE_URL } from '@/utils/constants'

class ApiService {
  private baseURL: string

  constructor() {
    this.baseURL = API_BASE_URL
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`
    
    const defaultHeaders = {
      'Content-Type': 'application/json'
    }

    const config: RequestInit = {
      ...options,
      headers: {
        ...defaultHeaders,
        ...options.headers
      }
    }

    try {
      const response = await fetch(url, config)
      
      if (!response.ok) {
        const errorText = await response.text()
        throw new Error(`HTTP ${response.status}: ${errorText}`)
      }

      const data = await response.json()
      return data
    } catch (error) {
      console.error('API request failed:', error)
      throw error
    }
  }

  private get<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, { method: 'GET' })
  }

  private post<T>(endpoint: string, data?: any): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined
    })
  }

  private put<T>(endpoint: string, data?: any): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'PUT',
      body: data ? JSON.stringify(data) : undefined
    })
  }

  private delete<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, { method: 'DELETE' })
  }

  // Learning API
  learning = {
    assessKnowledge: (query: string): Promise<ApiResponse> =>
      this.post('/learning/assess-knowledge', { user_query: query }),

    planPath: (query: string, sessionId?: string): Promise<ApiResponse> =>
      this.post('/learning/plan-path', { 
        user_query: query, 
        session_id: sessionId 
      }),

    generateContent: (query: string, sessionId?: string): Promise<ApiResponse> =>
      this.post('/learning/generate-content', { 
        user_query: query, 
        session_id: sessionId 
      }),

    evaluateUnderstanding: (query: string, sessionId?: string): Promise<ApiResponse> =>
      this.post('/learning/evaluate-understanding', { 
        user_query: query, 
        session_id: sessionId 
      }),

    consolidateMemory: (query: string, sessionId?: string): Promise<ApiResponse> =>
      this.post('/learning/consolidate-memory', { 
        user_query: query, 
        session_id: sessionId 
      }),

    orchestrate: (query: string, enableWebsocket = true): Promise<ApiResponse<LearningSession>> =>
      this.post('/learning/orchestrate', {
        user_query: query,
        enable_websocket: enableWebsocket
      }),

    getSession: (sessionId: string): Promise<ApiResponse<LearningSession>> =>
      this.get(`/learning/session/${sessionId}`),

    getStatus: (): Promise<ApiResponse> =>
      this.get('/learning/status')
  }

  // Knowledge Management API
  knowledge = {
    getNotes: (): Promise<ApiResponse<Note[]>> =>
      this.get('/notes'),

    getNote: (noteId: string): Promise<ApiResponse<Note>> =>
      this.get(`/notes/${noteId}`),

    createNote: (note: CreateNoteRequest): Promise<ApiResponse<Note>> =>
      this.post('/notes', note),

    updateNote: (noteId: string, note: UpdateNoteRequest): Promise<ApiResponse<Note>> =>
      this.put(`/notes/${noteId}`, note),

    deleteNote: (noteId: string): Promise<ApiResponse> =>
      this.delete(`/notes/${noteId}`),

    searchNotes: (query: SearchQuery): Promise<ApiResponse<SearchResult[]>> => {
      const params = new URLSearchParams()
      params.append('query', query.query)
      if (query.type) params.append('search_type', query.type)
      if (query.limit) params.append('limit', query.limit.toString())
      if (query.offset) params.append('offset', query.offset.toString())
      
      return this.get(`/notes/search?${params.toString()}`)
    }
  }

  // Graph API
  graph = {
    getOverview: (includeOrphans = true, maxNodes = 500): Promise<ApiResponse<GraphData>> => {
      const params = new URLSearchParams()
      params.append('include_orphans', includeOrphans.toString())
      params.append('max_nodes', maxNodes.toString())
      
      return this.get(`/graph/overview?${params.toString()}`)
    },

    findPath: (fromNote: string, toNote: string, algorithm = 'shortest', maxDepth = 10): Promise<ApiResponse<LearningPath>> => {
      const params = new URLSearchParams()
      params.append('algorithm', algorithm)
      params.append('max_depth', maxDepth.toString())
      
      return this.get(`/graph/path/${fromNote}/${toNote}?${params.toString()}`)
    },

    getNeighbors: (noteId: string, depth = 1, includeMetadata = true): Promise<ApiResponse> => {
      const params = new URLSearchParams()
      params.append('depth', depth.toString())
      params.append('include_metadata', includeMetadata.toString())
      
      return this.get(`/graph/neighbors/${noteId}?${params.toString()}`)
    },

    getClusters: (minClusterSize = 3, algorithm = 'community'): Promise<ApiResponse> => {
      const params = new URLSearchParams()
      params.append('min_cluster_size', minClusterSize.toString())
      params.append('algorithm', algorithm)
      
      return this.get(`/graph/clusters?${params.toString()}`)
    },

    getAnalytics: (): Promise<ApiResponse> =>
      this.get('/graph/analytics'),

    searchGraph: (query: string, searchType = 'semantic', limit = 20): Promise<ApiResponse> => {
      const params = new URLSearchParams()
      params.append('query', query)
      params.append('search_type', searchType)
      params.append('limit', limit.toString())
      
      return this.get(`/graph/search?${params.toString()}`)
    }
  }

  // System API
  system = {
    getInfo: (): Promise<ApiResponse> =>
      this.get('/system/info'),

    getConfig: (): Promise<ApiResponse<SystemConfig>> =>
      this.get('/system/config'),

    getStatus: (): Promise<ApiResponse<SystemStatus>> =>
      this.get('/system/status'),

    reloadConfig: (): Promise<ApiResponse> =>
      this.post('/system/reload-config')
  }
}

export const api = new ApiService()
export default api