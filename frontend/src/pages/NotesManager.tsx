import { Card, CardHeader, CardTitle, CardDescription } from '@components/ui'

export function NotesManager() {
  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
          Notes Manager
        </h1>
        <p className="text-gray-600 dark:text-gray-300">
          Manage your notes and explore bidirectional links
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Notes Manager</CardTitle>
          <CardDescription>
            This page will be implemented in the next development phase
          </CardDescription>
        </CardHeader>
      </Card>
    </div>
  )
}