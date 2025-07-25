import { Card, CardHeader, CardTitle, CardDescription } from '@components/ui'

export function SystemConsole() {
  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
          System Console
        </h1>
        <p className="text-gray-600 dark:text-gray-300">
          Monitor system health and manage configuration
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>System Console</CardTitle>
          <CardDescription>
            This page will be implemented in the next development phase
          </CardDescription>
        </CardHeader>
      </Card>
    </div>
  )
}