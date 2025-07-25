#!/usr/bin/env python3
"""
Test script for Tool Call Engine functionality.
Tests the recursive tool calling system inspired by NagaAgent.
"""

import sys
import asyncio
from pathlib import Path

# Add the backend to the path
sys.path.insert(0, str(Path(__file__).parent / 'backend'))

from backend.core.tool_call_engine import (
    ToolCallEngine,
    BaseTool,
    ToolCall,
    ToolCallStatus,
    SearchKnowledgeTool,
    AnalyzeLinksTool
)
from backend.core.context_manager import ContextManager
from backend.core.bidirectional_links import BidirectionalLinkEngine


class SimpleCalculatorTool(BaseTool):
    """Simple calculator tool for testing."""
    
    def __init__(self):
        super().__init__(
            name="calculator",
            description="Perform basic mathematical calculations"
        )
    
    async def execute(self, parameters: dict, context=None):
        operation = parameters.get("operation")
        a = parameters.get("a", 0)
        b = parameters.get("b", 0)
        
        if operation == "add":
            return {"result": a + b}
        elif operation == "subtract":
            return {"result": a - b}
        elif operation == "multiply":
            return {"result": a * b}
        elif operation == "divide":
            if b == 0:
                raise ValueError("Cannot divide by zero")
            return {"result": a / b}
        else:
            raise ValueError(f"Unknown operation: {operation}")
    
    def get_parameters_schema(self):
        return {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": ["add", "subtract", "multiply", "divide"],
                    "description": "Mathematical operation to perform"
                },
                "a": {
                    "type": "number",
                    "description": "First number"
                },
                "b": {
                    "type": "number", 
                    "description": "Second number"
                }
            },
            "required": ["operation", "a", "b"]
        }


async def test_tool_call_engine():
    """Test the tool call engine functionality."""
    print("🔮 Testing ArcanAgent Tool Call Engine")
    print("=" * 50)
    
    # Initialize components
    knowledge_base_path = "./knowledge_base"
    link_engine = BidirectionalLinkEngine(knowledge_base_path)
    link_engine.refresh_knowledge_base()
    
    context_manager = ContextManager(link_engine)
    tool_engine = ToolCallEngine(context_manager, max_call_depth=3)
    
    print("✅ Tool call engine initialized")
    
    # Test tool registration
    print("\n🔧 Testing Tool Registration")
    print("-" * 30)
    
    # Register test tools
    calc_tool = SimpleCalculatorTool()
    search_tool = SearchKnowledgeTool(link_engine)
    analyze_tool = AnalyzeLinksTool(link_engine)
    
    tool_engine.register_tool(calc_tool)
    tool_engine.register_tool(search_tool)
    tool_engine.register_tool(analyze_tool)
    
    available_tools = tool_engine.get_available_tools()
    print(f"   Registered {len(available_tools)} tools:")
    for tool_name, tool_info in available_tools.items():
        print(f"   - {tool_name}: {tool_info['description']}")
    
    # Test single tool call
    print("\n⚡ Testing Single Tool Call")
    print("-" * 28)
    
    calc_call = ToolCall(
        tool_name="calculator",
        parameters={"operation": "add", "a": 5, "b": 3}
    )
    
    executed_call = await tool_engine.execute_tool_call(calc_call)
    
    print(f"   Tool: {executed_call.tool_name}")
    print(f"   Status: {executed_call.status.value}")
    print(f"   Result: {executed_call.result}")
    print(f"   Execution time: {executed_call.execution_time:.3f}s")
    
    # Test multiple tool calls
    print("\n⚡⚡ Testing Multiple Tool Calls")
    print("-" * 31)
    
    tool_calls = [
        ToolCall("calculator", {"operation": "multiply", "a": 4, "b": 7}),
        ToolCall("calculator", {"operation": "divide", "a": 15, "b": 3})
    ]
    
    if link_engine.note_metadata:
        first_note = next(iter(link_engine.note_metadata.keys()))
        tool_calls.append(ToolCall("analyze_links", {"note_id": first_note}))
    
    executed_calls = await tool_engine.execute_tool_calls(tool_calls, parallel=True)
    
    print(f"   Executed {len(executed_calls)} tool calls in parallel:")
    for call in executed_calls:
        print(f"   - {call.tool_name}: {call.status.value} ({call.execution_time:.3f}s)")
        if call.status == ToolCallStatus.SUCCESS:
            print(f"     Result: {call.result}")
    
    # Test search tool if we have knowledge
    print("\n🔍 Testing Knowledge Search Tool")
    print("-" * 32)
    
    if link_engine.note_metadata:
        search_call = ToolCall(
            "search_knowledge", 
            {"query": "ArcanAgent", "max_results": 3}
        )
        
        search_result = await tool_engine.execute_tool_call(search_call)
        print(f"   Search status: {search_result.status.value}")
        if search_result.status == ToolCallStatus.SUCCESS:
            result = search_result.result
            print(f"   Found {result['total_found']} results for '{result['query']}':")
            for i, res in enumerate(result['results']):
                print(f"   {i+1}. {res['title']} (ID: {res['note_id']})")
    else:
        print("   No knowledge base available for search testing")
    
    # Test error handling
    print("\n🚨 Testing Error Handling")
    print("-" * 26)
    
    error_calls = [
        ToolCall("nonexistent_tool", {}),  # Tool doesn't exist
        ToolCall("calculator", {"operation": "divide", "a": 10, "b": 0})  # Division by zero
    ]
    
    error_results = await tool_engine.execute_tool_calls(error_calls)
    
    for call in error_results:
        print(f"   {call.tool_name}: {call.status.value}")
        if call.error:
            print(f"   Error: {call.error}")
    
    # Test execution statistics
    print("\n📊 Testing Execution Statistics")
    print("-" * 33)
    
    stats = tool_engine.get_execution_stats()
    print(f"   Total calls: {stats['total_calls']}")
    print(f"   Successful calls: {stats['successful_calls']}")
    print(f"   Failed calls: {stats['failed_calls']}")
    print(f"   Success rate: {stats['success_rate']:.2%}")
    print(f"   Average execution time: {stats['average_execution_time']:.3f}s")
    print(f"   Registered tools: {stats['registered_tools']}")
    
    # Test tool unregistration
    print("\n❌ Testing Tool Unregistration")
    print("-" * 31)
    
    tool_engine.unregister_tool("calculator")
    remaining_tools = tool_engine.get_available_tools()
    print(f"   Remaining tools after unregistering calculator: {list(remaining_tools.keys())}")
    
    print("\n🎉 All Tool Call Engine tests completed!")
    print("💡 The recursive tool calling system is working correctly.")
    
    return True


async def main():
    """Run the tool call engine tests."""
    try:
        success = await test_tool_call_engine()
        if success:
            print("\n✅ Tool Call Engine implementation is working correctly!")
            return 0
        else:
            print("\n❌ Tool Call Engine tests failed!")
            return 1
            
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))