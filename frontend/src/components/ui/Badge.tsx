import React from 'react'
import { cva, type VariantProps } from 'class-variance-authority'
import { clsx } from 'clsx'

const badgeVariants = cva(
  'inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2',
  {
    variants: {
      variant: {
        default: 'border-transparent bg-primary-600 text-white',
        secondary: 'border-transparent bg-gray-100 text-gray-900 dark:bg-gray-800 dark:text-gray-100',
        destructive: 'border-transparent bg-red-600 text-white',
        outline: 'text-gray-900 dark:text-gray-100',
        success: 'border-transparent bg-green-600 text-white',
        warning: 'border-transparent bg-yellow-600 text-white',
        arcana: 'border-transparent bg-gradient-to-r from-purple-600 to-blue-600 text-white'
      }
    },
    defaultVariants: {
      variant: 'default'
    }
  }
)

export interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {}

function Badge({ className, variant, ...props }: BadgeProps) {
  return (
    <div className={clsx(badgeVariants({ variant }), className)} {...props} />
  )
}

export { Badge, badgeVariants }