import { Link } from 'react-router-dom'
import { APP_NAME, APP_PHILOSOPHY } from '@utils/constants'

export function Header() {
  return (
    <header className="border-b border-gray-200 bg-white dark:border-gray-800 dark:bg-gray-950">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="flex h-16 items-center justify-between">
          <div className="flex items-center">
            <Link 
              to="/" 
              className="flex items-center space-x-3"
            >
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-purple-600 to-blue-600">
                <span className="text-white font-bold text-sm">A</span>
              </div>
              <div>
                <h1 className="text-lg font-bold text-gray-900 dark:text-white">
                  {APP_NAME}
                </h1>
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  {APP_PHILOSOPHY}
                </p>
              </div>
            </Link>
          </div>
          
          <div className="flex items-center space-x-4">
            {/* Future: User menu, theme toggle, etc. */}
          </div>
        </div>
      </div>
    </header>
  )
}