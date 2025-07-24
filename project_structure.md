# ArcanAgent 项目目录结构设计

## 整体架构

```
ArcanAgent/
├── README.md                       # 项目说明文档
├── pyproject.toml                  # 项目配置和依赖管理
├── config.json                     # 主配置文件
├── config.json.example             # 配置文件模板
├── main.py                         # 主入口文件
├── requirements.txt                # 依赖列表(备用)
│
├── backend/                        # 后端核心代码
│   ├── __init__.py
│   ├── config.py                   # Pydantic配置系统
│   ├── main_server.py              # FastAPI服务器启动
│   │
│   ├── core/                       # 核心引擎
│   │   ├── __init__.py
│   │   ├── tool_call_engine.py     # 工具调用循环引擎
│   │   ├── context_manager.py      # 上下文管理器
│   │   ├── bidirectional_links.py  # 双向链接引擎
│   │   └── llm_client.py           # LLM API客户端
│   │
│   ├── agents/                     # Arcana Agent系统
│   │   ├── __init__.py
│   │   ├── base_agent.py           # Agent基类
│   │   ├── agent_manager.py        # 简化的Agent管理器
│   │   │
│   │   ├── arcana/                 # 五个核心Agent
│   │   │   ├── __init__.py
│   │   │   ├── the_high_priestess.py    # 知识评估
│   │   │   ├── the_hermit.py            # 路径规划
│   │   │   ├── the_magician.py          # 内容生成
│   │   │   ├── justice.py               # 理解检测
│   │   │   └── the_empress.py           # 记忆巩固
│   │   │
│   │   └── prompts/                # Agent提示词模板
│   │       ├── __init__.py
│   │       ├── system_prompts.py
│   │       └── learning_prompts.py
│   │
│   ├── knowledge/                  # 知识库管理
│   │   ├── __init__.py
│   │   ├── markdown_parser.py      # Markdown文件解析
│   │   ├── link_analyzer.py        # 链接分析和密度计算
│   │   ├── note_manager.py         # 笔记管理
│   │   └── zpd_analyzer.py         # 最近发展区分析
│   │
│   ├── api/                        # API路由和控制器
│   │   ├── __init__.py
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── learning.py         # 学习流程API
│   │   │   ├── notes.py            # 笔记管理API
│   │   │   ├── graph.py            # 知识图谱API
│   │   │   └── system.py           # 系统管理API
│   │   │
│   │   ├── middleware.py           # 中间件
│   │   ├── exceptions.py           # 异常处理
│   │   └── websocket_handler.py    # WebSocket处理
│   │
│   └── utils/                      # 工具函数
│       ├── __init__.py
│       ├── file_utils.py           # 文件操作工具
│       ├── text_utils.py           # 文本处理工具
│       ├── async_utils.py          # 异步操作工具
│       └── validation.py           # 数据验证工具
│
├── frontend/                       # 前端代码
│   ├── package.json                # 前端依赖配置
│   ├── tsconfig.json               # TypeScript配置
│   ├── tailwind.config.js          # Tailwind CSS配置
│   ├── vite.config.ts              # Vite构建配置
│   │
│   ├── public/                     # 静态资源
│   │   ├── index.html
│   │   └── favicon.ico
│   │
│   ├── src/                        # 源代码
│   │   ├── main.tsx                # 应用入口
│   │   ├── App.tsx                 # 主应用组件
│   │   │
│   │   ├── components/             # React组件
│   │   │   ├── common/             # 通用组件
│   │   │   │   ├── Header.tsx
│   │   │   │   ├── Navigation.tsx
│   │   │   │   └── LoadingSpinner.tsx
│   │   │   │
│   │   │   ├── learning/           # 学习相关组件
│   │   │   │   ├── LearningSession.tsx
│   │   │   │   ├── KnowledgeAssessment.tsx
│   │   │   │   ├── LearningPath.tsx
│   │   │   │   ├── ContentViewer.tsx
│   │   │   │   ├── UnderstandingCheck.tsx
│   │   │   │   └── ProgressTracker.tsx
│   │   │   │
│   │   │   ├── knowledge/          # 知识管理组件
│   │   │   │   ├── NoteEditor.tsx
│   │   │   │   ├── LinkGraph.tsx
│   │   │   │   ├── NoteList.tsx
│   │   │   │   └── SearchBar.tsx
│   │   │   │
│   │   │   └── visualization/      # 可视化组件
│   │   │       ├── KnowledgeGraph.tsx
│   │   │       ├── LearningPathViz.tsx
│   │   │       └── ProgressChart.tsx
│   │   │
│   │   ├── stores/                 # Zustand状态管理
│   │   │   ├── learningStore.ts    # 学习状态
│   │   │   ├── knowledgeStore.ts   # 知识库状态
│   │   │   ├── uiStore.ts          # UI状态
│   │   │   └── sessionStore.ts     # 会话状态
│   │   │
│   │   ├── services/               # API服务
│   │   │   ├── api.ts              # 基础API客户端
│   │   │   ├── learningService.ts  # 学习API
│   │   │   ├── knowledgeService.ts # 知识库API
│   │   │   └── websocketService.ts # WebSocket客户端
│   │   │
│   │   ├── types/                  # TypeScript类型定义
│   │   │   ├── learning.ts         # 学习相关类型
│   │   │   ├── knowledge.ts        # 知识相关类型
│   │   │   ├── agent.ts            # Agent相关类型
│   │   │   └── api.ts              # API相关类型
│   │   │
│   │   ├── hooks/                  # 自定义React Hooks
│   │   │   ├── useLearning.ts      # 学习功能Hook
│   │   │   ├── useKnowledge.ts     # 知识管理Hook
│   │   │   └── useWebSocket.ts     # WebSocket Hook
│   │   │
│   │   ├── utils/                  # 前端工具函数
│   │   │   ├── formatters.ts       # 格式化工具
│   │   │   ├── validators.ts       # 验证工具
│   │   │   └── constants.ts        # 常量定义
│   │   │
│   │   └── styles/                 # 样式文件
│   │       ├── index.css           # 全局样式
│   │       └── components.css      # 组件样式
│   │
│   └── dist/                       # 构建输出目录
│
├── knowledge_base/                 # 用户知识库(Obsidian兼容)
│   ├── notes/                      # 主笔记目录
│   │   └── README.md               # 示例笔记
│   ├── attachments/                # 附件目录
│   ├── templates/                  # 笔记模板
│   └── .arcan/                     # ArcanAgent专用目录
│       ├── metadata/               # 元数据索引
│       │   ├── link_index.json     # 链接索引
│       │   ├── tag_index.json      # 标签索引
│       │   └── note_summaries.json # 笔记摘要
│       ├── sessions/               # 学习会话记录
│       ├── cache/                  # 缓存文件
│       └── user_profile.json       # 用户学习档案
│
├── tests/                          # 测试代码
│   ├── __init__.py
│   ├── conftest.py                 # pytest配置
│   │
│   ├── unit/                       # 单元测试
│   │   ├── test_core/              # 核心引擎测试
│   │   ├── test_agents/            # Agent测试
│   │   ├── test_knowledge/         # 知识库测试
│   │   └── test_api/               # API测试
│   │
│   ├── integration/                # 集成测试
│   │   ├── test_learning_flow.py   # 学习流程测试
│   │   ├── test_agent_cooperation.py # Agent协作测试
│   │   └── test_api_endpoints.py   # API端点测试
│   │
│   ├── performance/                # 性能测试
│   │   ├── test_large_knowledge_base.py # 大规模测试
│   │   └── test_concurrent_requests.py  # 并发测试
│   │
│   └── fixtures/                   # 测试数据
│       ├── sample_notes/           # 示例笔记
│       ├── test_configs/           # 测试配置
│       └── mock_responses/         # 模拟响应
│
├── deployment/                     # 部署配置
│   ├── docker/
│   │   ├── Dockerfile.backend      # 后端Dockerfile
│   │   ├── Dockerfile.frontend     # 前端Dockerfile
│   │   └── docker-compose.yml      # 容器编排
│   │
│   ├── scripts/                    # 部署脚本
│   │   ├── setup.sh                # 环境设置
│   │   ├── start.sh                # 启动脚本
│   │   └── backup.sh               # 备份脚本
│   │
│   └── nginx/                      # Nginx配置
│       └── nginx.conf
│
├── docs/                           # 文档
│   ├── README.md                   # 总体文档
│   ├── installation.md             # 安装指南
│   ├── configuration.md            # 配置说明
│   ├── api_reference.md            # API参考
│   ├── user_guide.md               # 用户指南
│   │
│   ├── architecture/               # 架构文档
│   │   ├── overview.md             # 架构概览
│   │   ├── agents.md               # Agent系统
│   │   ├── knowledge_system.md     # 知识系统
│   │   └── context_engineering.md  # 上下文工程
│   │
│   └── examples/                   # 示例和教程
│       ├── basic_usage.md          # 基础使用
│       ├── advanced_features.md    # 高级功能
│       └── integration_guide.md    # 集成指南
│
├── logs/                           # 日志目录(运行时创建)
└── .env.example                    # 环境变量模板
```

## 设计原则

### 1. **借鉴NagaAgent的成功模式**
- **配置系统**: config.py + config.json的组合
- **模块化设计**: 清晰的功能分离
- **异步架构**: 支持高并发处理

### 2. **适配ArcanAgent的特殊需求**
- **knowledge_base/**: 专门的Obsidian兼容知识库目录
- **agents/arcana/**: 5个固定的塔罗牌Agent
- **双向链接专用模块**: 核心的链接分析和处理

### 3. **现代开发最佳实践**
- **前后端分离**: 清晰的API边界
- **类型安全**: TypeScript前端 + Python类型提示
- **测试完备**: 单元测试、集成测试、性能测试
- **容器化部署**: Docker支持

## 核心目录说明

### backend/core/ - 核心引擎
- 包含所有从NagaAgent借鉴的核心机制
- 工具调用循环、上下文管理、双向链接引擎

### backend/agents/arcana/ - 塔罗牌Agent
- 5个固定Agent，无需动态注册
- 每个Agent专注于学习流程的一个环节

### knowledge_base/ - 知识库
- 完全Obsidian兼容的markdown文件结构
- .arcan/隐藏目录存储ArcanAgent专用数据

### frontend/ - 现代前端架构
- React 18 + TypeScript + Tailwind CSS
- Zustand状态管理 + D3.js可视化

这个结构是否符合您的预期？有需要调整的地方吗？
