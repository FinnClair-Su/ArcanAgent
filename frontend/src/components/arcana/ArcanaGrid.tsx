import { ArcanaCard } from './ArcanaCard'
import type { LearningSession } from '@/types'
import { ARCANA_AGENTS } from '@utils/constants'
import { clsx } from 'clsx'

interface ArcanaGridProps {
  session?: LearningSession
  onExecuteAgent: (agentName: string, query: string) => void
  onViewResult?: (agentName: string) => void
  disabled?: boolean
  className?: string
}

export function ArcanaGrid({ 
  session, 
  onExecuteAgent, 
  onViewResult,
  disabled = false,
  className 
}: ArcanaGridProps) {
  const agents = Object.values(ARCANA_AGENTS)
  
  const getAgentStage = (agentName: string) => {
    if (!session) return undefined
    return session.stages.find(stage => 
      stage.id.includes(agentName.replace('_', '_'))
    )
  }
  
  return (
    <div className={clsx(
      'arcana-grid grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-6',
      className
    )}>
      {agents.map((agent) => {
        const stage = getAgentStage(agent.name)
        
        return (
          <ArcanaCard
            key={agent.name}
            agent={agent}
            stage={stage}
            onExecute={onExecuteAgent}
            onViewResult={onViewResult ? () => onViewResult(agent.name) : undefined}
            disabled={disabled}
          />
        )
      })}
    </div>
  )
}