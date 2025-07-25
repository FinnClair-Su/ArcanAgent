/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        // Primary colors - 神秘蓝
        primary: {
          50: '#eff6ff',
          100: '#dbeafe', 
          200: '#bfdbfe',
          300: '#93c5fd',
          400: '#60a5fa',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
          800: '#1e40af',
          900: '#1e293b',
          950: '#172554'
        },
        
        // Arcana Agent Colors
        arcana: {
          'high-priestess': '#8b5cf6',  // 紫色 - 智慧
          'hermit': '#f59e0b',          // 金色 - 指引  
          'magician': '#10b981',        // 绿色 - 创造
          'justice': '#ef4444',         // 红色 - 公正
          'empress': '#ec4899'          // 粉色 - 丰饶
        },
        
        // Knowledge Graph Colors
        graph: {
          'node-default': '#64748b',
          'node-active': '#3b82f6',
          'link-default': '#cbd5e1', 
          'link-active': '#60a5fa'
        },
        
        // Semantic Colors
        success: '#22c55e',
        warning: '#f59e0b',
        error: '#ef4444',
        info: '#3b82f6'
      },
      
      fontFamily: {
        'primary': ['Inter', '-apple-system', 'BlinkMacSystemFont', 'sans-serif'],
        'heading': ['Playfair Display', 'serif'],
        'mono': ['JetBrains Mono', 'monospace']
      },
      
      animation: {
        'fade-in': 'fadeIn 0.5s ease-in-out',
        'slide-up': 'slideUp 0.3s ease-out',
        'pulse-slow': 'pulse 3s infinite',
        'float': 'float 6s ease-in-out infinite'
      },
      
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' }
        },
        slideUp: {
          '0%': { transform: 'translateY(20px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' }
        },
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-10px)' }
        }
      },
      
      backdropBlur: {
        xs: '2px'
      },
      
      boxShadow: {
        'arcana': '0 10px 25px -5px rgba(139, 92, 246, 0.2), 0 10px 10px -5px rgba(139, 92, 246, 0.04)',
        'graph': '0 4px 6px -1px rgba(59, 130, 246, 0.1), 0 2px 4px -1px rgba(59, 130, 246, 0.06)'
      }
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography')
  ],
}