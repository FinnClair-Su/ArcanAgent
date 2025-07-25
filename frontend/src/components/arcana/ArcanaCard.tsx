import { motion } from 'framer-motion'
import { CardContent, Button, Badge, Spinner } from '@components/ui'
import type { ArcanaAgent, LearningStage } from '@/types'
import { clsx } from 'clsx'

interface ArcanaCardProps {
  agent: ArcanaAgent
  stage?: LearningStage
  onExecute: (agentName: string, query: string) => void
  onViewResult?: () => void
  disabled?: boolean
  className?: string
}

export function ArcanaCard({ 
  agent, 
  stage,
  onExecute, 
  onViewResult,
  disabled = false,
  className 
}: ArcanaCardProps) {
  const isExecuting = stage?.status === 'in_progress'
  const isCompleted = stage?.status === 'completed'
  const hasError = stage?.status === 'error'
  
  const handleExecute = () => {
    if (!disabled && !isExecuting) {
      onExecute(agent.name, '')
    }
  }

  const getStatusColor = () => {
    if (hasError) return 'destructive'
    if (isCompleted) return 'success'
    if (isExecuting) return 'arcana'
    return 'secondary'
  }

  const getStatusText = () => {
    if (hasError) return 'Error'
    if (isCompleted) return 'Completed'
    if (isExecuting) return 'Processing'
    return 'Ready'
  }

  return (
    <motion.div
      className={clsx(
        'arcana-card group relative overflow-hidden rounded-xl border border-gray-200 bg-white transition-all duration-300',
        'hover:shadow-lg hover:border-opacity-50 dark:border-gray-800 dark:bg-gray-900',
        disabled && 'opacity-50 cursor-not-allowed',
        isExecuting && 'animate-pulse-arcana',
        className
      )}
      whileHover={disabled ? {} : { scale: 1.02, y: -4 }}
      whileTap={disabled ? {} : { scale: 0.98 }}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      {/* Background Gradient */}
      <div 
        className="absolute inset-0 opacity-0 transition-opacity duration-300 group-hover:opacity-10"
        style={{ 
          background: `linear-gradient(135deg, ${agent.color}20 0%, ${agent.color}10 100%)` 
        }}
      />
      
      {/* Status Badge */}
      <div className="absolute top-4 right-4 z-10">
        <Badge variant={getStatusColor()}>
          {getStatusText()}
        </Badge>
      </div>

      <CardContent className="p-6">
        {/* Agent Symbol */}
        <div className="flex items-center justify-center mb-4">
          <div 
            className="flex h-16 w-16 items-center justify-center rounded-full text-3xl transition-transform duration-300 group-hover:scale-110"
            style={{ 
              backgroundColor: `${agent.color}15`,
              color: agent.color,
              border: `2px solid ${agent.color}30`
            }}
          >
            {isExecuting ? (
              <Spinner size="lg" variant="arcana" />
            ) : (
              agent.symbol
            )}
          </div>
        </div>

        {/* Agent Info */}
        <div className="text-center mb-6">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
            {agent.displayName}
          </h3>
          <p className="text-sm text-gray-600 dark:text-gray-300 leading-relaxed">
            {agent.description}
          </p>
        </div>

        {/* Stage Progress */}
        {stage && (
          <div className="mb-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-medium text-gray-500 dark:text-gray-400">
                {stage.name}
              </span>
              {isExecuting && (
                <span className="text-xs text-gray-500 dark:text-gray-400">
                  {Math.round(stage.progress * 100)}%
                </span>
              )}
            </div>
            {isExecuting && (
              <div className="w-full bg-gray-200 rounded-full h-1.5 dark:bg-gray-700">
                <div 
                  className="h-1.5 rounded-full transition-all duration-300"
                  style={{ 
                    width: `${stage.progress * 100}%`,
                    backgroundColor: agent.color
                  }}
                />
              </div>
            )}
          </div>
        )}

        {/* Capabilities */}
        <div className="mb-6">
          <div className="flex flex-wrap gap-1 justify-center">
            {agent.capabilities.slice(0, 2).map((capability) => (
              <span 
                key={capability}
                className="px-2 py-1 text-xs rounded-md bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-300"
              >
                {capability.replace('_', ' ')}
              </span>
            ))}
          </div>
        </div>

        {/* Action Buttons */}
        <div className="space-y-2">
          <Button
            onClick={handleExecute}
            disabled={disabled || isExecuting}
            className="w-full"
            style={{ backgroundColor: agent.color }}
          >
            {isExecuting ? (
              <>
                <Spinner size="sm" variant="white" className="mr-2" />
                Processing...
              </>
            ) : (
              'Execute'
            )}
          </Button>
          
          {isCompleted && onViewResult && (
            <Button
              onClick={onViewResult}
              variant="outline"
              className="w-full"
            >
              View Result
            </Button>
          )}
        </div>

        {/* Execution Time */}
        {stage?.endTime && stage?.startTime && (
          <div className="mt-3 text-center">
            <span className="text-xs text-gray-500 dark:text-gray-400">
              Completed in {Math.round(
                (new Date(stage.endTime).getTime() - new Date(stage.startTime).getTime()) / 1000
              )}s
            </span>
          </div>
        )}
      </CardContent>
    </motion.div>
  )
}