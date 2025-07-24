#!/usr/bin/env python3
"""
ArcanAgent - Personal Knowledge Management & Learning System
Main Entry Point

This is the primary entry point for the ArcanAgent system.
It initializes the configuration, sets up logging, and starts the API server.
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from backend.config import config
from backend.main_server import create_app


def setup_logging():
    """Set up logging configuration based on config settings."""
    log_level = getattr(logging, config.system.log_level.upper(), logging.INFO)
    
    # Configure root logger
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(
                project_root / "logs" / "arcanagent.log", 
                encoding='utf-8'
            ) if (project_root / "logs").exists() else logging.StreamHandler()
        ]
    )
    
    # Set specific logger levels to reduce noise
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)
    logging.getLogger("anthropic").setLevel(logging.WARNING)
    
    logger = logging.getLogger("ArcanAgent")
    logger.info(f"ArcanAgent v{config.system.version} starting...")
    logger.info(f"Log level set to: {config.system.log_level}")
    
    return logger


def check_environment():
    """Check if the environment is properly configured."""
    logger = logging.getLogger("ArcanAgent.Environment")
    
    # Check knowledge base path
    kb_path = Path(config.system.knowledge_base_path)
    if not kb_path.exists():
        logger.warning(f"Knowledge base path does not exist: {kb_path}")
        logger.info("Creating knowledge base directory structure...")
        kb_path.mkdir(parents=True, exist_ok=True)
        (kb_path / "notes").mkdir(exist_ok=True)
        (kb_path / "attachments").mkdir(exist_ok=True)
        (kb_path / "templates").mkdir(exist_ok=True)
        (kb_path / ".arcan").mkdir(exist_ok=True)
        (kb_path / ".arcan" / "metadata").mkdir(exist_ok=True)
        (kb_path / ".arcan" / "sessions").mkdir(exist_ok=True)
        (kb_path / ".arcan" / "cache").mkdir(exist_ok=True)
        
        # Create a welcome note
        welcome_note = kb_path / "notes" / "Welcome_to_ArcanAgent.md"
        welcome_content = """---
title: Welcome to ArcanAgent
tags: [welcome, getting-started]
created: 2024-01-01
complexity: 1
mastery_level: 0
---

# Welcome to ArcanAgent 🔮

Welcome to your personal knowledge management and learning system powered by bidirectional linking!

## What is ArcanAgent?

ArcanAgent is built on the principle that **[[Bidirectional Linking]] is All You Need** for effective knowledge management. Just as attention mechanisms revolutionized neural networks, bidirectional links can revolutionize how you learn and organize knowledge.

## Getting Started

1. Create notes using standard markdown
2. Link concepts using `[[double brackets]]`
3. Let ArcanAgent analyze your knowledge and guide your learning journey

## Core Concepts

- [[Zone of Proximal Development]] - Learn at the right pace
- [[Cognitive Load Theory]] - Optimize your mental bandwidth  
- [[Bidirectional Links]] - Connect ideas naturally
- [[Spaced Repetition]] - Reinforce learning over time

## The Five Arcana

Your learning journey is guided by five specialized agents:

- **The High Priestess** 🔮 - Assesses your current knowledge
- **The Hermit** 🏮 - Plans your learning path  
- **The Magician** ✨ - Generates personalized content
- **Justice** ⚖️ - Evaluates your understanding
- **The Empress** 🌸 - Consolidates your memory

Ready to begin your journey? Start by exploring what you'd like to learn!
"""
        welcome_note.write_text(welcome_content, encoding='utf-8')
        logger.info("Created welcome note and knowledge base structure")
    
    # Check LLM configuration
    if config.llm.default_provider == "openai":
        if not config.llm.openai.api_key or config.llm.openai.api_key.startswith("sk-your-"):
            logger.error("OpenAI API key not configured!")
            logger.error("Please set OPENAI_API_KEY in your .env file or config.json")
            return False
    elif config.llm.default_provider == "anthropic":
        if not config.llm.anthropic.api_key or config.llm.anthropic.api_key.startswith("sk-ant-your-"):
            logger.error("Anthropic API key not configured!")
            logger.error("Please set ANTHROPIC_API_KEY in your .env file or config.json")
            return False
    
    # Create logs directory
    logs_dir = project_root / "logs"
    logs_dir.mkdir(exist_ok=True)
    
    logger.info("Environment check completed successfully")
    return True


async def main():
    """Main entry point for ArcanAgent."""
    print("🔮 ArcanAgent - Personal Knowledge Management & Learning System")
    print("=" * 60)
    
    # Setup logging
    logger = setup_logging()
    
    try:
        # Check environment
        if not check_environment():
            logger.error("Environment check failed. Please fix the configuration and try again.")
            sys.exit(1)
        
        # Create and configure the FastAPI app
        app = create_app()
        
        # Import uvicorn here to avoid import issues
        import uvicorn
        
        # Start the server
        logger.info(f"Starting ArcanAgent API server on {config.api.host}:{config.api.port}")
        logger.info(f"API Documentation available at: http://{config.api.host}:{config.api.port}/docs")
        logger.info(f"Knowledge Base Path: {config.system.knowledge_base_path}")
        
        # Run the server
        uvicorn.run(
            app,
            host=config.api.host,
            port=config.api.port,
            log_level=config.system.log_level.lower(),
            reload=config.system.debug,
            access_log=True
        )
        
    except KeyboardInterrupt:
        logger.info("Received shutdown signal, stopping ArcanAgent...")
    except Exception as e:
        logger.error(f"Failed to start ArcanAgent: {e}")
        if config.system.debug:
            import traceback
            logger.error(traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())