# ArcanAgent 🔮

> **Bidirectional Linking is All You Need** - Personal Knowledge Management & Learning System

ArcanAgent is a revolutionary personal knowledge management and learning system built on the principle that bidirectional linking can transform how we organize, understand, and learn from our knowledge. Inspired by the seminal paper "Attention is All You Need," we propose that **bidirectional links are all you need** for effective knowledge management.

This project is currently in an active development phase. The core backend logic and learning pipeline are complete and functional. The frontend is connected for the primary learning workflow, with some features stubbed out for future development.

## 🌟 Core Philosophy

Just as attention mechanisms revolutionized neural machine translation by eliminating the need for recurrence and convolution, bidirectional links can revolutionize knowledge management by eliminating the need for complex graph databases and vector stores.

- **Simplicity**: Pure markdown files with `[[wiki-style]]` links.
- **Transparency**: Human-readable and editable knowledge base.
- **Portability**: Seamless integration with Obsidian and similar tools.
- **Efficiency**: File system operations replace database queries.

## ⚙️ How It Works: The Arcana-Powered Learning Workflow

ArcanAgent uses a pipeline of five specialized AI agents to guide you through a complete learning cycle. The entire process is orchestrated by a sophisticated backend and accessible through a user-friendly frontend.

1.  **Initiate Learning (Frontend)**: Your journey begins in the **Learning Hub**. You enter a topic or question you want to learn about.
2.  **Orchestration (Backend)**: The system receives your query and triggers the `ArcanaAgentOrchestrator`. This orchestrator manages the five-agent pipeline, passing the context from one agent to the next.
3.  **The High Priestess (🔮 Knowledge Assessment)**: First, The High Priestess analyzes your existing `knowledge_base` (your markdown notes) to assess your current understanding of the topic.
4.  **The Hermit (🏮 Path Planning)**: Based on the assessment, The Hermit identifies your "Zone of Proximal Development" (ZPD) and charts an optimal, step-by-step learning path for you.
5.  **The Magician (✨ Content Generation)**: The Magician takes the learning path and magically generates personalized educational content, automatically weaving in `[[bidirectional links]]` to connect with your existing knowledge.
6.  **Justice (⚖️ Understanding Evaluation)**: After you've reviewed the content, Justice assesses your comprehension by generating questions and evaluating how well you can form connections.
7.  **The Empress (🌸 Memory Consolidation)**: Finally, The Empress helps consolidate what you've learned, integrating the new knowledge into your permanent knowledge base by updating and creating notes and links.
8.  **Real-time Feedback (Frontend & Backend)**: Throughout this process, the backend sends real-time updates via **WebSockets**, which are displayed in the Learning Hub UI, so you can see the magic happen.

## 🚀 Getting Started: Deployment & Usage

The easiest way to get ArcanAgent running is with Docker.

### Prerequisites
- Docker and Docker Compose
- Git
- An LLM API key (e.g., from OpenAI, Anthropic)

### 1. Configuration
First, clone the repository and set up your configuration.

```bash
git clone https://github.com/your-username/ArcanAgent.git
cd ArcanAgent

# Create a .env file from the example
cp .env.example .env
```

Now, open the `.env` file and add your LLM API key. For example:
```env
# .env
OPENAI_API_KEY="sk-..."
```

The system defaults to using OpenAI. You can change the default provider and other settings in `config.json` (by copying from `config.json.example`).

### 2. Run with Docker Compose
With Docker running, execute the following command from the project root:

```bash
docker-compose up --build
```

This will build the images for the frontend and backend and start both services.

### 3. Usage
-   **Access the Frontend**: Open your browser and navigate to `http://localhost:3000`.
-   **Start Learning**: Go to the **Learning Hub** from the homepage.
-   **Enter Your Query**: Type a topic you want to learn about (e.g., "Explain the basics of quantum physics").
-   **Begin Session**: Click "Begin Learning Session" and watch as the Arcana agents guide you through the workflow.

## 🛣️ Future Development

The core learning pipeline is complete, but there is still much to do. Our development efforts will now focus on the following areas:

-   **Full-Fledged Note Management**:
    -   Implementing the `update` and `delete` functionalities for notes via the API.
    -   Building out the "Notes Manager" UI on the frontend to be a fully interactive CRUD interface for the `knowledge_base`.

-   **Interactive Knowledge Graph**:
    -   Implementing the backend logic for advanced graph analytics (e.g., clustering, centrality).
    -   Bringing the "Knowledge Graph" page to life using a library like D3.js or Vis.js to create a dynamic, explorable visualization of your notes and their connections.

-   **Refining Core Engines**:
    -   Improving the `ContextManager`'s "attention via recitation" mechanism to better maintain focus during long tasks.
    -   Enhancing the `BidirectionalLinkEngine` with more sophisticated link suggestion algorithms.

-   **Enhanced Testing**:
    -   Expanding the test suite with more comprehensive end-to-end tests for the learning pipeline.
    -   Adding frontend tests to ensure UI reliability.

## 🤝 Contributing

We welcome contributions! Please see our (forthcoming) `CONTRIBUTING.md` for details.

## 🙏 Acknowledgments

- Inspired by the "Attention is All You Need" paper by Vaswani et al.
- Built on Zone of Proximal Development theory by Lev Vygotsky.
- Cognitive Load Theory by John Sweller.
- The Obsidian community for pioneering bidirectional linking.
- The NagaAgent project for architectural inspiration.
