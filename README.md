# ArcanAgent 🔮

> **Bidirectional Linking is All You Need** - Personal Knowledge Management & Learning System

ArcanAgent is a revolutionary personal knowledge management and learning system built on the principle that bidirectional linking can transform how we organize, understand, and learn from our knowledge. Inspired by the seminal paper "Attention is All You Need," we propose that **bidirectional links are all you need** for effective knowledge management.

## 🌟 Core Philosophy

Just as attention mechanisms revolutionized neural machine translation by eliminating the need for recurrence and convolution, bidirectional links can revolutionize knowledge management by eliminating the need for complex graph databases and vector stores.

### Why Bidirectional Links? 

**Traditional knowledge graphs require:**
- Complex Neo4j queries and maintenance
- Vector database synchronization  
- Heavyweight indexing and embedding pipelines
- Specialized query languages and APIs

**Bidirectional links provide:**
- **Simplicity**: Pure markdown files with `[[wiki-style]]` links
- **Transparency**: Human-readable and editable knowledge base
- **Portability**: Seamless integration with Obsidian and similar tools
- **Efficiency**: File system operations replace database queries

## 🎯 Features

### 🧠 Learning Science Integration
- **Zone of Proximal Development (ZPD)**: Learn at the optimal pace
- **Cognitive Load Theory**: Optimize mental bandwidth automatically
- **Spaced Repetition**: Reinforce learning through intelligent scheduling
- **Metacognitive Support**: Guide how to learn, not just what to learn

### 🔗 Advanced Bidirectional Linking
- **Automatic Link Discovery**: AI-powered link suggestion and creation
- **Context-Aware Granularity**: Content adapts based on link density
- **Shortest Path Learning**: Find optimal paths between concepts
- **Link Density Analysis**: Mathematical elegance in knowledge organization

### 🔮 The Five Arcana Agents
Your learning journey is guided by five specialized AI agents, each named after Tarot arcana:

1. **The High Priestess** 🔮 - Knowledge state assessment and cognitive analysis
2. **The Hermit** 🏮 - Learning path planning and ZPD identification  
3. **The Magician** ✨ - Personalized content generation and real-time linking
4. **Justice** ⚖️ - Understanding evaluation and learning effectiveness
5. **The Empress** 🌸 - Knowledge integration and memory consolidation

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+ (for frontend development)
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/arcanagent/arcanagent.git
   cd ArcanAgent
   ```

2. **Set up the backend**
   ```bash
   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\\Scripts\\activate
   
   # Install dependencies
   pip install -e .
   ```

3. **Configure your API keys**
   ```bash
   cp .env.example .env
   cp config.json.example config.json
   
   # Edit .env and config.json with your LLM API keys
   # OpenAI or Anthropic API key required
   ```

4. **Start the system**
   ```bash
   python main.py
   ```

5. **Access the application**
   - API Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health
   - Frontend (coming soon): http://localhost:3000

### Your First Learning Session

1. Create a note in your `knowledge_base/notes/` directory:
   ```markdown
   ---
   title: "My Learning Goal"
   tags: [learning, goals]
   ---
   
   # My Learning Goal
   
   I want to learn about [[Artificial Intelligence]] and its applications in [[Education]].
   ```

2. Start a learning session via the API:
   ```bash
   curl -X POST "http://localhost:8000/api/v1/learning/assess-knowledge" \\
        -H "Content-Type: application/json" \\
        -d '{"user_query": "I want to learn about artificial intelligence"}'
   ```

3. Follow the guided learning flow through all five stages!

## 📁 Project Structure

```
ArcanAgent/
├── backend/                 # Python backend
│   ├── core/               # Core engines (links, context, tools)
│   ├── agents/             # The five Arcana agents
│   ├── knowledge/          # Knowledge management system
│   ├── api/                # FastAPI routes and middleware
│   └── utils/              # Utility functions
├── frontend/               # React frontend (coming soon)
├── knowledge_base/         # Your Obsidian-compatible notes
├── tests/                  # Comprehensive test suite
├── docs/                   # Documentation
└── deployment/             # Docker and deployment configs
```

## 🔧 Configuration

ArcanAgent uses a flexible configuration system supporting both JSON files and environment variables:

### Environment Variables (.env)
```bash
# LLM Provider
OPENAI_API_KEY=your-openai-key
# OR
ANTHROPIC_API_KEY=your-anthropic-key

# Server Settings
API_HOST=127.0.0.1
API_PORT=8000

# Knowledge Base
KNOWLEDGE_BASE_PATH=./knowledge_base
```

### JSON Configuration (config.json)
```json
{
  "llm": {
    "default_provider": "openai",
    "openai": {
      "model": "gpt-4-turbo-preview",
      "temperature": 0.7
    }
  },
  "learning": {
    "max_sessions": 10,
    "enable_adaptive_difficulty": true
  }
}
```

## 🧪 Development

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=backend

# Run specific test categories
pytest -m unit          # Unit tests only
pytest -m integration   # Integration tests only
pytest -m performance   # Performance tests only
```

### Code Quality
```bash
# Format code
black backend/
isort backend/

# Type checking
mypy backend/

# Linting
flake8 backend/
```

## 🔬 The Science Behind ArcanAgent

### Mathematical Foundation
Our link density analysis follows elegant mathematical principles:

```
Granularity = f(incoming_links, outgoing_links)
Context_Quality = Σ(shortest_paths) × neighborhood_expansion  
Learning_Readiness = |prerequisites ∩ known_concepts| / |prerequisites|
```

### Context Engineering Principles
ArcanAgent strictly follows six core context engineering principles for optimal performance and cost:

1. **KV-Cache Optimization** - Maximize cache hit rates
2. **Tool Availability Management** - Static tool definitions with logits masking
3. **File System as Context** - External memory through file references
4. **Attention via Recitation** - Periodic plan injection
5. **Error Information Retention** - Complete failure preservation
6. **Context Diversity** - Avoid pattern repetition

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](docs/contributing.md) for details.

### Development Setup
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Install development dependencies: `pip install -e ".[dev]"`
4. Make your changes and add tests
5. Run the test suite: `pytest`
6. Submit a pull request

## 📚 Documentation

- [Installation Guide](docs/installation.md)
- [Configuration Reference](docs/configuration.md)
- [API Documentation](docs/api_reference.md)
- [Architecture Overview](docs/architecture/overview.md)
- [Agent System Guide](docs/architecture/agents.md)
- [Bidirectional Links Deep Dive](docs/architecture/bidirectional_links.md)

## 🛣️ Roadmap

### Phase 1: Core System (Current)
- [x] Project structure and configuration
- [x] Basic API endpoints  
- [ ] Core bidirectional link engine
- [ ] Five Arcana agents implementation
- [ ] Tool call loop system

### Phase 2: Learning Features
- [ ] ZPD analysis and path planning
- [ ] Adaptive content generation
- [ ] Understanding assessment
- [ ] Memory consolidation

### Phase 3: Frontend & UX  
- [ ] React frontend application
- [ ] Interactive knowledge graph visualization
- [ ] Real-time learning progress tracking
- [ ] Mobile-responsive design

### Phase 4: Advanced Features
- [ ] FSRS spaced repetition integration
- [ ] Multi-language support
- [ ] Collaborative learning features
- [ ] Advanced analytics and insights

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Inspired by the "Attention is All You Need" paper by Vaswani et al.
- Built on Zone of Proximal Development theory by Lev Vygotsky  
- Cognitive Load Theory by John Sweller
- The Obsidian community for pioneering bidirectional linking
- NagaAgent project for architectural inspiration

## 💬 Community & Support

- **GitHub Issues**: [Report bugs and request features](https://github.com/arcanagent/arcanagent/issues)
- **Discussions**: [Join the community discussion](https://github.com/arcanagent/arcanagent/discussions)
- **Documentation**: [Read the full docs](https://docs.arcanagent.com)

---

**Remember**: In the world of knowledge management, **Bidirectional Linking is All You Need** 🔗✨