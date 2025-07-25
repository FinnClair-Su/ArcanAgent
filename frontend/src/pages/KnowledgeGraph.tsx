import { Card, CardHeader, CardTitle, CardDescription } from '@components/ui'

export function KnowledgeGraph() {
  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
          Knowledge Graph
        </h1>
        <p className="text-gray-600 dark:text-gray-300">
          Visualize and explore your knowledge network
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Knowledge Graph</CardTitle>
          <CardDescription>
            This page will be implemented in the next development phase
          </CardDescription>
        </CardHeader>
      </Card>
    </div>
  )
}