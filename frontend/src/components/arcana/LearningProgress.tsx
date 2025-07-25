import { motion } from 'framer-motion'
import { Card, CardHeader, CardTitle, CardContent, Progress } from '@components/ui'
import type { LearningSession } from '@/types'
import { ARCANA_AGENTS } from '@utils/constants'
import { clsx } from 'clsx'

interface LearningProgressProps {
  session: LearningSession
  className?: string
}

export function LearningProgress({ session, className }: LearningProgressProps) {
  const currentStageIndex = session.currentStage
  const overallProgress = session.progress
  
  const getStageStatus = (index: number) => {
    if (index < currentStageIndex) return 'completed'
    if (index === currentStageIndex) return 'active'
    return 'pending'
  }
  
  const getStageAgent = (stageId: string) => {
    return Object.values(ARCANA_AGENTS).find(agent => 
      stageId.includes(agent.name.replace('_', '_'))
    ) || ARCANA_AGENTS.the_high_priestess
  }

  return (
    <Card className={clsx('learning-progress', className)}>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <span>Learning Progress</span>
          <span className="text-sm font-normal text-gray-500 dark:text-gray-400">
            {Math.round(overallProgress * 100)}% Complete
          </span>
        </CardTitle>
        <Progress 
          value={overallProgress * 100} 
          variant="arcana" 
          className="mt-2" 
        />
      </CardHeader>
      
      <CardContent>
        <div className="space-y-4">
          {session.stages.map((stage, index) => {
            const status = getStageStatus(index)
            const agent = getStageAgent(stage.id)
            
            return (
              <motion.div
                key={stage.id}
                className={clsx(
                  'stage-item flex items-center space-x-4 rounded-lg border p-4 transition-all duration-300',
                  {
                    'border-gray-200 bg-white dark:border-gray-700 dark:bg-gray-800': status === 'pending',
                    'border-yellow-300 bg-yellow-50 dark:border-yellow-600 dark:bg-yellow-900/20': status === 'active',
                    'border-green-300 bg-green-50 dark:border-green-600 dark:bg-green-900/20': status === 'completed'
                  }
                )}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
              >
                {/* Stage Icon */}
                <div className="flex-shrink-0">
                  <div 
                    className={clsx(
                      'flex h-10 w-10 items-center justify-center rounded-full text-lg transition-all duration-300',
                      {
                        'bg-gray-100 text-gray-400 dark:bg-gray-700 dark:text-gray-500': status === 'pending',
                        'bg-yellow-100 text-yellow-600 dark:bg-yellow-900/30 dark:text-yellow-400': status === 'active',
                        'bg-green-100 text-green-600 dark:bg-green-900/30 dark:text-green-400': status === 'completed'
                      }
                    )}
                    style={status !== 'pending' ? { borderColor: agent.color } : {}}
                  >
                    {status === 'completed' ? '✓' : agent.symbol}
                  </div>
                </div>
                
                {/* Stage Info */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between mb-1">
                    <h4 className="text-sm font-medium text-gray-900 dark:text-white truncate">
                      {stage.name}
                    </h4>
                    {status === 'active' && (
                      <span className="text-xs text-gray-500 dark:text-gray-400">
                        {Math.round(stage.progress * 100)}%
                      </span>
                    )}
                  </div>
                  
                  <p className="text-xs text-gray-600 dark:text-gray-300 mb-2">
                    {stage.description}
                  </p>
                  
                  {/* Stage Progress Bar */}
                  {status === 'active' && (
                    <div className="w-full bg-gray-200 rounded-full h-1 dark:bg-gray-700">
                      <div 
                        className="h-1 rounded-full transition-all duration-300"
                        style={{ 
                          width: `${stage.progress * 100}%`,
                          backgroundColor: agent.color
                        }}
                      />
                    </div>
                  )}
                  
                  {/* Timing Information */}
                  {(stage.startTime || stage.endTime) && (
                    <div className="mt-2 text-xs text-gray-500 dark:text-gray-400">
                      {stage.startTime && !stage.endTime && (
                        <span>Started at {new Date(stage.startTime).toLocaleTimeString()}</span>
                      )}
                      {stage.endTime && stage.startTime && (
                        <span>
                          Completed in {Math.round(
                            (new Date(stage.endTime).getTime() - new Date(stage.startTime).getTime()) / 1000
                          )}s
                        </span>
                      )}
                    </div>
                  )}
                </div>
                
                {/* Status Indicator */}
                <div className="flex-shrink-0">
                  {status === 'active' && (
                    <div className="flex space-x-1">
                      <div className="w-1 h-1 bg-yellow-400 rounded-full animate-pulse" />
                      <div className="w-1 h-1 bg-yellow-400 rounded-full animate-pulse" style={{ animationDelay: '0.2s' }} />
                      <div className="w-1 h-1 bg-yellow-400 rounded-full animate-pulse" style={{ animationDelay: '0.4s' }} />
                    </div>
                  )}
                  {status === 'completed' && (
                    <div className="w-2 h-2 bg-green-400 rounded-full" />
                  )}
                  {status === 'pending' && (
                    <div className="w-2 h-2 bg-gray-300 rounded-full dark:bg-gray-600" />
                  )}
                </div>
              </motion.div>
            )
          })}
        </div>
        
        {/* Session Info */}
        <div className="mt-6 pt-4 border-t border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400">
            <span>Session ID: {session.id}</span>
            <span>Status: {session.status}</span>
          </div>
          <div className="mt-1 text-xs text-gray-500 dark:text-gray-400">
            <span>Started: {new Date(session.createdAt).toLocaleString()}</span>
            {session.updatedAt !== session.createdAt && (
              <span className="ml-4">Updated: {new Date(session.updatedAt).toLocaleString()}</span>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  )
}