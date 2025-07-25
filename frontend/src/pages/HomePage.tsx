import { Link } from 'react-router-dom'
import { Card, CardHeader, CardTitle, CardDescription, CardContent, Button } from '@components/ui'
import { ARCANA_AGENTS, APP_PHILOSOPHY } from '@utils/constants'

export function HomePage() {
  return (
    <div className="space-y-8">
      {/* Hero Section */}
      <div className="text-center">
        <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-4">
          Welcome to ArcanAgent
        </h1>
        <p className="text-xl text-gray-600 dark:text-gray-300 mb-2">
          {APP_PHILOSOPHY}
        </p>
        <p className="text-gray-500 dark:text-gray-400 max-w-2xl mx-auto">
          A personal knowledge management and learning system powered by five Arcana agents,
          designed to help you explore, learn, and connect knowledge through bidirectional linking.
        </p>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <span className="text-2xl">🎓</span>
              <span>Start Learning</span>
            </CardTitle>
            <CardDescription>
              Begin a new learning session with our five Arcana agents
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Link to="/learning">
              <Button className="w-full">
                Launch Learning Hub
              </Button>
            </Link>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <span className="text-2xl">🕸️</span>
              <span>Explore Graph</span>
            </CardTitle>
            <CardDescription>
              Visualize your knowledge network and discover connections
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Link to="/graph">
              <Button variant="outline" className="w-full">
                Open Knowledge Graph
              </Button>
            </Link>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <span className="text-2xl">📝</span>
              <span>Browse Notes</span>
            </CardTitle>
            <CardDescription>
              Manage your notes and explore bidirectional links
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Link to="/notes">
              <Button variant="outline" className="w-full">
                View Notes
              </Button>
            </Link>
          </CardContent>
        </Card>
      </div>

      {/* Arcana Agents Overview */}
      <div>
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">
          Meet Your Arcana Agents
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
          {Object.values(ARCANA_AGENTS).map((agent) => (
            <Card key={agent.name} className="text-center">
              <CardContent className="pt-6">
                <div 
                  className="text-4xl mb-3"
                  style={{ color: agent.color }}
                >
                  {agent.symbol}
                </div>
                <h3 className="font-semibold text-sm mb-2">
                  {agent.displayName}
                </h3>
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  {agent.description}
                </p>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>

      {/* System Status */}
      <Card>
        <CardHeader>
          <CardTitle>System Status</CardTitle>
          <CardDescription>
            Current system health and performance
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center space-x-2">
            <div className="h-3 w-3 rounded-full bg-green-500"></div>
            <span className="text-sm text-gray-600 dark:text-gray-300">
              All systems operational
            </span>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}