# 🔮 ArcanAgent 🔮

**A Unified Knowledge-Memory Architecture for LLM Agents, based on Bidirectional Linking.**

**一个基于双向链接的、为大型语言模型智能体（LLM Agent）设计的知识库-记忆统一架构。**

---

> ArcanAgent is a research platform and Personal Knowledge Management (PKM) system designed to validate a core hypothesis: a simple, text-based system of bidirectional links can serve as a unified and effective knowledge base and memory architecture for LLM agents. Drawing inspiration from the seminal paper "Attention is All You Need," we propose that for many knowledge-intensive tasks, **Bidirectional Linking is All You Need.**

> ArcanAgent 是一个研究平台和个人知识管理（PKM）系统，其核心目标是验证一个关键假设：**一个基于双向链接的简单文本系统，可以作为 LLM Agent 的统一且高效的知识库和记忆架构。** 受开创性论文《Attention is All You Need》的启发，我们相信，对于许多知识密集型任务，**双向链接即你所需。**

---

## 🧠 Core Philosophy: Cognitive Science Meets AI

### 🧠 核心理念：认知科学与人工智能的融合

> ArcanAgent is built on a foundation of cognitive science principles, adapted for the world of LLM agents and personal knowledge management. This is not just a software architecture; it's a model for machine cognition.

> ArcanAgent 的构建根植于认知科学的深厚土壤，并将其原理应用于 LLM Agent 与个人知识管理的世界。这不仅是一个软件架构，更是一个机器认知模型。

#### **1. Unified Knowledge-Memory Architecture** / **知识库-记忆统一架构**

> The `knowledge_base` directory, consisting of simple Markdown files, serves a dual purpose. It is both the user's personal knowledge repository and the LLM agent's long-term memory. This eliminates the need for separate, complex memory systems (like vector databases) and ensures that the agent's "mind" is always transparent, human-readable, and directly editable by the user.

> 项目的 `knowledge_base` 目录由简单的 Markdown 文件组成，它服务于双重目的：**既是用户的个人知识库，也是 LLM Agent 的长期记忆。** 这消除了对独立、复杂的记忆系统（如向量数据库）的需求，并确保了 Agent 的“思想”对用户来说始终是透明、可读且可直接编辑的。

#### **2. Bidirectional Linking as Associative Memory** / **双向链接作为联想记忆**

> We treat `[[wiki-style]]` links as the fundamental building blocks of associative memory. When an agent or user creates a link, they are forming a direct, contextual connection between two pieces of information, mirroring how human memory works. This allows for efficient knowledge traversal and discovery without the overhead of vector similarity searches.

> 我们将 `[[wiki-style]]` 链接视为联想记忆的基本构建块。当 Agent 或用户创建一个链接时，他们是在两个信息片段之间建立了一个直接的、有上下文的连接，这模仿了人类记忆的工作方式。这使得高效的知识遍历和发现成为可能，而无需向量相似性搜索的开销。

#### **3. Learning in the Zone of Proximal Development (ZPD)** / **在最近发展区（ZPD）中学习**

> The learning workflow is guided by Lev Vygotsky's concept of the ZPD. The system first assesses what the user already knows and then generates new content that is challenging but not overwhelming, creating an optimal path for knowledge acquisition. Link density and path analysis are used to map the learning sequence, providing the necessary "scaffolding" for growth.

> 学习工作流由列夫·维果茨基的“最近发展区”理论指导。系统首先评估用户的现有知识，然后生成具有挑战性但又不过于困难的新内容，从而为知识获取创建一条最佳路径。系统通过链接密度和路径分析来规划学习序列，为用户的知识增长提供必要的“支架”。

---

## 🛠️ Advanced Architecture: Context & Agent Engineering

### 🛠️ 核心架构：上下文与智能体工程

> As detailed in our `specs`, ArcanAgent implements a sophisticated architecture inspired by successful frameworks like NagaAgent, focusing on efficiency, stability, and structured reasoning.

> 正如我们的 `specs`（设计规格文档）中所详述，ArcanAgent 实现了一个受 NagaAgent 等成功框架启发的复杂架构，其核心聚焦于效率、稳定性与结构化推理。

#### **1. The 6 Principles of Context Engineering** / **上下文工程六大原则**

> To ensure our agent operates with maximum efficiency and reliability, we strictly adhere to six core principles of context engineering, which are critical for managing the LLM's limited attention and optimizing performance.

> 为确保我们的 Agent 以最高的效率和可靠性运行，我们严格遵守六大上下文工程核心原则。这些原则对于管理 LLM 有限的注意力窗口和优化性能至关重要。

1.  **KV-Cache Optimization / KV-Cache 优化**: Use static, deterministic prompt prefixes to maximize cache hits, reducing latency and cost. / *使用静态、确定性的提示词前缀来最大化缓存命中率，从而降低延迟和成本。*
2.  **Tool Availability Management / 工具可用性管理**: Manage tools via `logits_masking` instead of dynamically altering tool definitions in the context. / *通过 `logits_masking`（解码器干预）来管理工具的可用性，而不是在上下文中动态修改工具定义。*
3.  **File System as Context / 文件系统即上下文**: Use the local file system as a vast, persistent external memory, referenced by file paths in the context. / *将本地文件系统作为庞大、持久的外部记忆体，在上下文中仅保留文件路径作为引用。*
4.  **Attention Manipulation via Recitation / 通过复述引导注意力**: Periodically re-inject the core task plan into the context to prevent goal-drifting during long tasks. / *在长任务执行过程中，周期性地将核心任务计划重新注入上下文，以防止目标偏离。*
5.  **Error Information Retention / 错误信息保留**: Keep full error messages and stack traces in the context to allow the agent to learn from its mistakes. / *在上下文中完整保留失败动作及其产生的错误信息，使 Agent 能从错误中学习和适应。*
6.  **Context Diversity / 上下文多样性**: Introduce structured variations in prompts and responses to prevent the model from getting stuck in repetitive loops. / *在提示和响应中引入受控的、结构化的变体，以打破上下文的模式重复性，避免模型行为僵化。*

#### **2. The Title-Summary-Details Structure** / **标题-摘要-详情分层结构**

> A key innovation derived from our context engineering principles is the **Title-Summary-Details** structure for every note. This allows our `ContextManager` to be highly efficient: it can load just titles for browsing, summaries for assessing relevance, and full details only when deep analysis is required. This mimics the human ability to skim, read abstracts, and then dive deep, preventing cognitive overload for both the user and the LLM.

> 从我们的上下文工程原则中衍生出的一个核心创新，是为每个笔记设计的 **标题-摘要-详情（Title-Summary-Details）** 三层结构。这使得我们的 `ContextManager` 能够高效运作：在浏览时，它仅加载标题；在评估相关性时，它使用摘要；只有在需要深入分析时，它才会将完整的详情加载到 LLM 的上下文窗口中。这模仿了人类首先略读、然后阅读摘要、最后再深入研究的能力，从而有效防止了用户和 LLM 的认知过载。

---

## ⚙️ How It Works: The Arcana-Powered Learning Workflow

### ⚙️ 工作原理：由“奥秘”驱动的学习工作流

> ArcanAgent uses a pipeline of five specialized AI agents to guide you through a complete learning cycle. This entire process is orchestrated by a sophisticated backend and accessible through a user-friendly frontend.

> ArcanAgent 使用由五个专业化的 AI 智能体组成的流水线，引导您完成一个完整的学习周期。整个过程由一个复杂的后端进行编排，并通过一个用户友好的前端界面呈现。

1.  **Initiate Learning (Frontend) / 启动学习 (前端)**: Your journey begins in the **Learning Hub**. You enter a topic you want to learn about. / *您的旅程始于 **学习中心**。您输入一个您想学习的主题。*
2.  **Orchestration (Backend) / 流程编排 (后端)**: The system receives your query and triggers the `ArcanAgentOrchestrator`, which manages the five-agent pipeline. / *系统接收到您的请求，并触发 `ArcanaAgentOrchestrator`，由它来管理五个 Agent 的协作流水线。*
3.  **The High Priestess (🔮 Knowledge Assessment) / 女祭司 (知识评估)**: First, The High Priestess analyzes your existing `knowledge_base` to assess your current understanding of the topic. / *首先，女祭司会分析您现有的 `knowledge_base`，以评估您对该主题的当前理解程度。*
4.  **The Hermit (🏮 Path Planning) / 隐士 (路径规划)**: Based on the assessment, The Hermit identifies your Zone of Proximal Development (ZPD) and charts an optimal learning path. / *基于评估结果，隐士会识别您的“最近发展区”（ZPD），并为您规划出一条最佳的学习路径。*
5.  **The Magician (✨ Content Generation) / 魔术师 (内容生成)**: The Magician takes the learning path and generates personalized educational content, automatically weaving in `[[bidirectional links]]` to your existing knowledge. / *魔术师会根据学习路径，生成个性化的学习内容，并自动将 `[[双向链接]]` 嵌入其中，与您的现有知识相关联。*
6.  **Justice (⚖️ Understanding Evaluation) / 正义 (理解评估)**: After you've reviewed the content, Justice assesses your comprehension by generating questions and evaluating your ability to form new connections. / *在您阅读完内容后，正义会通过生成问题、评估您建立新连接的能力等方式，来检测您的理解程度。*
7.  **The Empress (🌸 Memory Consolidation) / 皇后 (记忆巩固)**: Finally, The Empress helps consolidate what you've learned, integrating the new knowledge into your permanent knowledge base by creating and updating notes. / *最后，皇后会帮助您巩固所学知识，通过创建和更新笔记，将新知识整合到您的永久知识库中。*

---

## 🚀 Getting Started

### 🚀 快速开始

> The easiest way to get ArcanAgent running is with Docker.

> 运行 ArcanAgent 最简单的方式是使用 Docker。

#### **Prerequisites / 先决条件**

-   Docker and Docker Compose
-   Git
-   An LLM API key (e.g., from OpenAI, Anthropic)

#### **1. Configuration / 配置**

> First, clone the repository and set up your configuration.

> 首先，克隆仓库并设置您的配置。

```bash
git clone https://github.com/FinnClair-Su/ArcanAgent.git
cd ArcanAgent

# Create a .env file from the example
# 从示例文件创建 .env 文件
cp .env.example .env
```

> Now, open the `.env` file and add your LLM API key.

> 现在，打开 `.env` 文件并添加您的 LLM API 密钥。

```env
# .env
OPENAI_API_KEY="sk-..."
```

#### **2. Run with Docker Compose / 使用 Docker Compose 运行**

> With Docker running, execute the following command from the project root:

> 在 Docker 运行的情况下，在项目根目录执行以下命令：

```bash
docker-compose up --build
```

#### **3. Usage / 使用**

-   **Access the Frontend / 访问前端**: Open your browser and navigate to `http://localhost:3000`. / *打开浏览器并访问 `http://localhost:3000`。*
-   **Start Learning / 开始学习**: Go to the **Learning Hub** from the homepage. / *从主页进入 **学习中心**。*
-   **Enter Your Query / 输入您的查询**: Type a topic you want to learn about. / *输入您想学习的主题。*
-   **Begin Session / 开始会话**: Click "Begin Learning Session" and watch the magic happen. / *点击“开始学习会话”，然后见证魔法的发生。*

---

## 🛣️ Future Development / 未来开发

-   **Full-Fledged Note Management / 功能完备的笔记管理**: Implementing full CRUD functionalities for notes and enhancing the "Notes Manager" UI. / *为笔记实现完整的增删改查（CRUD）功能，并增强“笔记管理器”的用户界面。*
-   **Interactive Knowledge Graph / 交互式知识图谱**: Bringing the "Knowledge Graph" page to life with dynamic, explorable visualizations. / *通过动态、可探索的可视化，让“知识图谱”页面焕发生机。*
-   **Refining Core Engines / 优化核心引擎**: Improving the `ContextManager` and `BidirectionalLinkEngine`. / *持续改进 `ContextManager` 和 `BidirectionalLinkEngine`。*
-   **Enhanced Testing / 增强测试**: Expanding the test suite for both backend and frontend. / *为前端和后端扩展更全面的测试套件。*

## 🤝 Contributing / 贡献

> We welcome contributions! Please see our (forthcoming) `CONTRIBUTING.md` for details.

> 我们欢迎任何形式的贡献！详情请参阅我们（即将发布）的 `CONTRIBUTING.md` 文件。

## 🙏 Acknowledgments / 致谢

-   Inspired by the "Attention is All You Need" paper by Vaswani et al. / *灵感来源于 Vaswani 等人的论文《Attention is All You Need》。*
-   Built on Zone of Proximal Development theory by Lev Vygotsky & Cognitive Load Theory by John Sweller. / *构建于维果茨基的“最近发展区”理论和斯威勒的“认知负荷理论”之上。*
-   The Obsidian community for pioneering bidirectional linking. / *感谢 Obsidian 社区在双向链接领域的开拓性工作。*
-   The NagaAgent project for architectural inspiration. / *感谢 NagaAgent 项目提供的架构灵感。*