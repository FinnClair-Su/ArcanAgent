import React from 'react'
import { clsx } from 'clsx'

export interface ProgressProps extends React.HTMLAttributes<HTMLDivElement> {
  value?: number
  max?: number
  variant?: 'default' | 'arcana' | 'success' | 'warning' | 'error'
  size?: 'sm' | 'md' | 'lg'
  showLabel?: boolean
}

const Progress = React.forwardRef<HTMLDivElement, ProgressProps>(
  ({ 
    className, 
    value = 0, 
    max = 100, 
    variant = 'default',
    size = 'md',
    showLabel = false,
    ...props 
  }, ref) => {
    const percentage = Math.min(Math.max((value / max) * 100, 0), 100)
    
    const variantClasses = {
      default: 'bg-primary-600',
      arcana: 'bg-gradient-to-r from-purple-600 to-blue-600',
      success: 'bg-green-600',
      warning: 'bg-yellow-600',
      error: 'bg-red-600'
    }
    
    const sizeClasses = {
      sm: 'h-1',
      md: 'h-2',
      lg: 'h-3'
    }
    
    return (
      <div className={clsx('relative w-full', className)} ref={ref} {...props}>
        <div className={clsx(
          'w-full rounded-full bg-gray-200 dark:bg-gray-800',
          sizeClasses[size]
        )}>
          <div
            className={clsx(
              'rounded-full transition-all duration-300 ease-in-out',
              variantClasses[variant],
              sizeClasses[size]
            )}
            style={{ width: `${percentage}%` }}
          />
        </div>
        {showLabel && (
          <div className="mt-1 flex justify-between text-xs text-gray-500 dark:text-gray-400">
            <span>{Math.round(percentage)}%</span>
            <span>{value}/{max}</span>
          </div>
        )}
      </div>
    )
  }
)
Progress.displayName = 'Progress'

export { Progress }