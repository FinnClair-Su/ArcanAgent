import type { ArcanaAgent } from '@/types'

// System Constants
export const APP_NAME = 'ArcanAgent'
export const APP_PHILOSOPHY = 'Bidirectional Linking is All You Need 🔗'
export const APP_VERSION = '1.0.0'

// API Configuration
export const API_BASE_URL = '/api/v1'
export const WS_BASE_URL = '/ws'

// Arcana Agents Configuration
export const ARCANA_AGENTS: Record<string, ArcanaAgent> = {
  the_high_priestess: {
    name: 'the_high_priestess',
    displayName: 'The High Priestess',
    symbol: '🔮',
    description: 'Knowledge Assessment & Intuitive Analysis',
    color: '#8b5cf6',
    capabilities: ['knowledge_assessment', 'cognitive_analysis', 'learning_readiness']
  },
  the_hermit: {
    name: 'the_hermit',
    displayName: 'The Hermit',
    symbol: '🏮',
    description: 'Learning Path Planning & Guidance',
    color: '#f59e0b',
    capabilities: ['path_planning', 'learning_guidance', 'knowledge_mapping']
  },
  the_magician: {
    name: 'the_magician',
    displayName: 'The Magician',
    symbol: '✨',
    description: 'Content Generation & Manifestation',
    color: '#10b981',
    capabilities: ['content_generation', 'knowledge_synthesis', 'creative_learning']
  },
  justice: {
    name: 'justice',
    displayName: 'Justice',
    symbol: '⚖️',
    description: 'Understanding Evaluation & Assessment',
    color: '#ef4444',
    capabilities: ['understanding_evaluation', 'assessment', 'knowledge_validation']
  },
  the_empress: {
    name: 'the_empress',
    displayName: 'The Empress',
    symbol: '🌸',
    description: 'Memory Consolidation & Growth',
    color: '#ec4899',
    capabilities: ['memory_consolidation', 'knowledge_integration', 'learning_nurturing']
  }
}

// Learning Stage Configuration
export const LEARNING_STAGES = [
  {
    id: 'assess_knowledge',
    agent: 'the_high_priestess',
    name: 'Knowledge Assessment',
    description: 'Analyzing current knowledge state and learning readiness'
  },
  {
    id: 'plan_path',
    agent: 'the_hermit',
    name: 'Learning Path Planning',
    description: 'Creating personalized learning pathway and strategy'
  },
  {
    id: 'generate_content',
    agent: 'the_magician',
    name: 'Content Generation',
    description: 'Generating tailored learning materials and resources'
  },
  {
    id: 'evaluate_understanding',
    agent: 'justice',
    name: 'Understanding Evaluation',
    description: 'Assessing comprehension and knowledge integration'
  },
  {
    id: 'consolidate_memory',
    agent: 'the_empress',
    name: 'Memory Consolidation',
    description: 'Integrating new knowledge into existing knowledge network'
  }
]

// UI Constants
export const BREAKPOINTS = {
  sm: 640,
  md: 768,
  lg: 1024,
  xl: 1280,
  '2xl': 1536
} as const

export const ANIMATION_DURATION = {
  fast: 150,
  normal: 300,
  slow: 500
} as const

// Graph Visualization Constants
export const GRAPH_CONFIG = {
  nodeRadius: {
    min: 5,
    max: 20,
    default: 8
  },
  linkStrength: {
    weak: 0.1,
    normal: 0.5,
    strong: 1.0
  },
  simulation: {
    forceStrength: -300,
    centerForce: 0.1,
    alphaDecay: 0.02
  }
} as const

// WebSocket Event Types
export const WS_EVENTS = {
  LEARNING_PROGRESS: 'progress',
  STAGE_COMPLETE: 'result', 
  SESSION_COMPLETE: 'result',
  ERROR: 'error',
  STATUS_UPDATE: 'status'
} as const

// Local Storage Keys
export const STORAGE_KEYS = {
  USER_PREFERENCES: 'arcanagent_user_preferences',
  THEME: 'arcanagent_theme',
  RECENT_SESSIONS: 'arcanagent_recent_sessions',
  NOTES_CACHE: 'arcanagent_notes_cache'
} as const

// Error Codes
export const ERROR_CODES = {
  NETWORK_ERROR: 'NETWORK_ERROR',
  VALIDATION_ERROR: 'VALIDATION_ERROR',
  AUTHENTICATION_ERROR: 'AUTHENTICATION_ERROR',
  AUTHORIZATION_ERROR: 'AUTHORIZATION_ERROR',
  NOT_FOUND: 'NOT_FOUND',
  INTERNAL_ERROR: 'INTERNAL_ERROR',
  WEBSOCKET_ERROR: 'WEBSOCKET_ERROR'
} as const

// Default Values
export const DEFAULTS = {
  pageSize: 20,
  sessionTimeout: 30 * 60 * 1000, // 30 minutes
  maxRetries: 3,
  debounceDelay: 300,
  searchMinLength: 2
} as const