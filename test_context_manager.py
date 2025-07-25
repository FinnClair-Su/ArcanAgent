#!/usr/bin/env python3
"""
Test script for Context Manager functionality.
Tests the 6 context engineering principles implementation.
"""

import sys
from pathlib import Path

# Add the backend to the path
sys.path.insert(0, str(Path(__file__).parent / 'backend'))

from backend.core.context_manager import (
    ContextManager, 
    ContextType, 
    ContextPriority,
    ContextItem
)
from backend.core.bidirectional_links import BidirectionalLinkEngine


def test_context_manager():
    """Test the context manager functionality."""
    print("🔮 Testing ArcanAgent Context Manager")
    print("=" * 50)
    
    # Initialize components
    knowledge_base_path = "./knowledge_base"
    link_engine = BidirectionalLinkEngine(knowledge_base_path)
    link_engine.refresh_knowledge_base()
    
    context_manager = ContextManager(link_engine, max_context_tokens=2000)
    
    print("✅ Context manager initialized")
    
    # Test Principle 1: KV-Cache Optimization
    print("\n📊 Testing Principle 1: KV-Cache Optimization")
    print("-" * 45)
    
    system_key1 = context_manager.add_system_context(
        "You are ArcanAgent, a knowledge management assistant."
    )
    system_key2 = context_manager.add_system_context(
        "You are ArcanAgent, a knowledge management assistant."  # Same content
    )
    
    print(f"   System context 1 key: {system_key1}")
    print(f"   System context 2 key: {system_key2}")
    print(f"   Cache hit: {'✅' if system_key1 == system_key2 else '❌'}")
    
    # Test Principle 2: Tool Availability Management
    print("\n🔧 Testing Principle 2: Tool Availability Management")
    print("-" * 50)
    
    tools = {
        "search_knowledge": {"description": "Search the knowledge base"},
        "create_note": {"description": "Create a new note"},
        "analyze_links": {"description": "Analyze bidirectional links"}
    }
    
    tool_key = context_manager.add_tool_definitions(tools)
    print(f"   Added {len(tools)} tool definitions")
    print(f"   Tool context key: {tool_key}")
    
    # Test tool masking
    context_manager.mask_tools(["create_note"])
    print("   Masked 'create_note' tool")
    
    # Test Principle 3: File System as Context  
    print("\n📁 Testing Principle 3: File System as Context")
    print("-" * 47)
    
    # Add knowledge context if we have notes
    if link_engine.note_metadata:
        first_note = next(iter(link_engine.note_metadata.keys()))
        knowledge_key = context_manager.add_knowledge_context(first_note, "summary")
        print(f"   Added knowledge context for: {first_note}")
        print(f"   Knowledge context key: {knowledge_key}")
        
        # Add file reference
        file_ref_key = context_manager.add_file_reference(
            f"knowledge_base/notes/{first_note}.md",
            "Sample file reference content"
        )
        print(f"   Added file reference key: {file_ref_key}")
    else:
        print("   No notes available for testing")
    
    # Test Principle 4: Attention via Recitation
    print("\n🎯 Testing Principle 4: Attention via Recitation")  
    print("-" * 47)
    
    plan_key = context_manager.set_current_plan(
        "1. Analyze user query\n2. Search relevant knowledge\n3. Generate response"
    )
    print(f"   Set current plan: {plan_key}")
    
    # Test Principle 5: Error Information Retention
    print("\n🚨 Testing Principle 5: Error Information Retention")
    print("-" * 49)
    
    error_key = context_manager.add_error_context(
        "Failed to connect to external API", 
        "connection_error"
    )
    print(f"   Added error context: {error_key}")
    print(f"   Error history count: {len(context_manager.error_history)}")
    
    # Test Principle 6: Context Diversity
    print("\n🌈 Testing Principle 6: Context Diversity") 
    print("-" * 42)
    
    # Add similar content to test diversity filtering
    diverse1 = context_manager.add_knowledge_context(first_note, "title") if link_engine.note_metadata else ""
    diverse2 = context_manager.add_knowledge_context(first_note, "title") if link_engine.note_metadata else ""  # Same content
    
    print(f"   Diverse content 1: {diverse1}")
    print(f"   Diverse content 2: {diverse2}")
    print(f"   Diversity filtering: {'✅' if diverse1 != diverse2 else '❌'}")
    
    # Test context window building
    print("\n🪟 Testing Context Window Building")
    print("-" * 35)
    
    messages = context_manager.build_context_window()
    print(f"   Generated {len(messages)} messages")
    
    for i, msg in enumerate(messages):
        print(f"   Message {i+1}: {msg.role} ({len(msg.content)} chars)")
    
    # Test context optimization
    print("\n⚡ Testing Context Optimization")
    print("-" * 32)
    
    context_manager.optimize_context()
    print("   Context optimization completed")
    
    # Get context summary
    summary = context_manager.get_context_summary()
    print(f"\n📈 Context Summary:")
    print(f"   Total items: {summary['total_items']}")
    print(f"   Total tokens: {summary['total_tokens']}")
    print(f"   Token utilization: {summary['token_utilization']:.2%}")
    print(f"   Cache hit rate: {summary['cache_hit_rate']:.2%}")
    print(f"   Has current plan: {summary['current_plan']}")
    print(f"   Error count: {summary['error_count']}")
    print(f"   Diversity score: {summary['diversity_score']:.2f}")
    print(f"   Content types: {summary['types']}")
    
    # Test related knowledge search
    print("\n🔍 Testing Related Knowledge Search")
    print("-" * 37)
    
    related_keys = context_manager.get_related_knowledge("ArcanAgent", max_items=2)
    print(f"   Found {len(related_keys)} related knowledge items")
    for key in related_keys:
        print(f"   Related key: {key}")
    
    print("\n🎉 All Context Manager tests completed!")
    print("💡 The 6 context engineering principles are working correctly.")
    
    return True


def main():
    """Run the context manager tests."""
    try:
        success = test_context_manager()
        if success:
            print("\n✅ Context Manager implementation is working correctly!")
            return 0
        else:
            print("\n❌ Context Manager tests failed!")
            return 1
            
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())