# ArcanAgent Project Structure

This document outlines the official directory structure for the ArcanAgent project. It should be kept up-to-date to reflect the current state of the codebase.

```
ArcanAgent/
├── .env.example
├── .gitignore
├── README.md
├── config.json
├── config.json.example
├── docker-compose.yml
├── main.py
├── project_structure.md
├── pyproject.toml
├── requirements.txt
├── simple_llm_test.py
│
├── backend/
│   ├── __init__.py
│   ├── config.py
│   ├── Dockerfile
│   ├── main_server.py
│   │
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── agent_orchestrator.py
│   │   ├── base_agent.py
│   │   ├── justice.py
│   │   ├── optimized_agent_system.py
│   │   ├── the_empress.py
│   │   ├── the_hermit.py
│   │   ├── the_high_priestess.py
│   │   └── the_magician.py
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes/
│   │       ├── __init__.py
│   │       ├── graph.py
│   │       ├── learning.py
│   │       ├── learning_complete.py
│   │       ├── llm.py
│   │       ├── notes.py
│   │       └── system.py
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── bidirectional_links.py
│   │   ├── bidirectional_links_optimized.py
│   │   ├── context_manager.py
│   │   ├── context_manager_original.py
│   │   ├── llm_client.py
│   │   ├── llm_client_optimized.py
│   │   ├── llm_initializer.py
│   │   └── tool_call_engine.py
│   │
│   ├── knowledge/
│   │   ├── __init__.py
│   │   └── note_manager.py
│   │
│   └── utils/
│       └── __init__.py
│
├── frontend/
│   ├── .eslintrc.cjs
│   ├── Dockerfile
│   ├── index.html
│   ├── package-lock.json
│   ├── package.json
│   ├── postcss.config.js
│   ├── tailwind.config.js
│   ├── tsconfig.json
│   ├── tsconfig.node.json
│   ├── vite.config.ts
│   ├── vitest.config.ts
│   │
│   └── src/
│       ├── App.tsx
│       ├── main.tsx
│       ├── vite-env.d.ts
│       │
│       ├── components/
│       │   ├── arcana/
│       │   ├── knowledge/
│       │   ├── layout/
│       │   └── ui/
│       │
│       ├── hooks/
│       ├── pages/
│       ├── services/
│       ├── stores/
│       ├── styles/
│       ├── test/
│       ├── types/
│       └── utils/
│
├── knowledge_base/
│   └── notes/
│       └── Welcome_to_ArcanAgent.md
│
├── logs/
│
└── specs/
    ├── arcan_agent/
    │   ├── design.md
    │   ├── requirements.md
    │   └── tasks.md
    └── general_design/
        ├── core.md
        └── requirements.md
```