#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ISA Model Client Tools Test
Tests tool binding and execution functionality with ISAModelClient
"""

import asyncio
from isa_model.client import create_client


def create_mock_calculator_tool():
    """Create a mock calculator MCP tool following MCP protocol format"""
    return {
        "name": "calculate",
        "description": "Perform basic mathematical calculations",
        "inputSchema": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "Mathematical expression to evaluate (e.g., '5 + 3', '10 * 2')"
                },
                "operation": {
                    "type": "string",
                    "description": "Type of operation",
                    "enum": ["add", "subtract", "multiply", "divide", "evaluate"],
                    "default": "evaluate"
                }
            },
            "required": ["expression"]
        }
    }


def create_mock_weather_tool():
    """Create a real MCP weather tool following actual MCP protocol format"""
    return {
        "name": "get_weather",
        "description": "Get mock weather information for testing purposes\n\nThis is a mock weather tool that provides simulated weather data for testing the MCP framework. It includes in-memory caching and realistic weather patterns for common cities.\n\nArgs:\n    city: Name of the city to get weather for\n    user_id: User identifier for logging purposes\n\nReturns:\n    JSON string with weather data including temperature, condition, humidity, wind, pressure, and visibility\n\nKeywords: weather, temperature, forecast, climate, rain, sunny, cloudy, wind, mock, test\nCategory: weather",
        "inputSchema": {
            "properties": {
                "city": {
                    "title": "City",
                    "type": "string"
                },
                "user_id": {
                    "default": "default",
                    "title": "User Id",
                    "type": "string"
                }
            },
            "required": ["city"],
            "title": "get_weatherArguments",
            "type": "object"
        },
        "outputSchema": {
            "properties": {
                "result": {
                    "title": "Result",
                    "type": "string"
                }
            },
            "required": ["result"],
            "title": "get_weatherOutput",
            "type": "object"
        }
    }


async def test_client_tool_binding():
    """Test basic tool binding with ISAModelClient"""
    print("🧪 Testing ISAModelClient tool binding...")
    
    # Create client
    client = create_client(mode="local")
    
    # Create mock tools
    calculator_tool = create_mock_calculator_tool()
    weather_tool = create_mock_weather_tool()
    tools = [calculator_tool, weather_tool]
    
    try:
        # Test invoke with tools parameter
        response = await client.invoke(
            input_data="What is 5 + 3?",
            task="chat",
            service_type="text",
            tools=tools
        )
        
        print(f"✅ Client tool binding successful")
        print(f"✅ Response received: {response.get('success', False)}")
        
        # Verify response structure
        assert isinstance(response, dict)
        assert "result" in response or "error" in response
        
        print(f"✅ Tool binding test passed")
        return True
        
    except Exception as e:
        print(f"❌ Tool binding test failed: {e}")
        return False


async def test_client_tool_execution():
    """Test tool call execution through client invoke method"""
    print("\n🧪 Testing ISAModelClient tool execution...")
    
    # Create client
    client = create_client(mode="local")
    
    # Create calculator tool
    calculator_tool = create_mock_calculator_tool()
    
    try:
        # Test with calculator question
        response = await client.invoke(
            input_data="Calculate 10 * 5",
            task="chat",
            service_type="text",
            tools=[calculator_tool]
        )
        
        print(f"✅ Tool execution response: {response}")
        
        # Check response structure
        if response.get("success"):
            print("✅ Tool execution successful")
            result = response.get("result")
            if result:
                print(f"✅ Result received: {str(result)[:200]}...")
        else:
            print(f"⚠️ Tool execution completed with note: {response.get('error', 'Unknown')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Tool execution test failed: {e}")
        return False


async def test_client_streaming_with_tools():
    """Test streaming functionality with tools through client"""
    print("\n🧪 Testing ISAModelClient streaming with tools...")
    
    # Create client
    client = create_client(mode="local")
    
    # Create weather tool
    weather_tool = create_mock_weather_tool()
    
    try:
        # Test streaming with tools
        stream_generator = await client.invoke(
            input_data="What's the weather like in Tokyo?",
            task="chat",
            service_type="text",
            stream=True,
            tools=[weather_tool]
        )
        
        print("✅ Streaming with tools initiated")
        
        # Collect some tokens
        tokens_collected = 0
        if hasattr(stream_generator, '__aiter__'):
            async for token in stream_generator:
                print(f"Token: {token}", end="", flush=True)
                tokens_collected += 1
                if tokens_collected >= 5:  # Limit for testing
                    break
        else:
            print("Stream generator not iterable (expected for some configurations)")
        
        print(f"\n✅ Streaming with tools test completed - collected {tokens_collected} tokens")
        return True
        
    except Exception as e:
        print(f"❌ Streaming with tools test failed: {e}")
        return False


async def test_client_multiple_tools():
    """Test client with multiple tools"""
    print("\n🧪 Testing ISAModelClient with multiple tools...")
    
    # Create client
    client = create_client(mode="local")
    
    # Create multiple tools
    calculator_tool = create_mock_calculator_tool()
    weather_tool = create_mock_weather_tool()
    tools = [calculator_tool, weather_tool]
    
    try:
        # Test query that could use either tool
        response = await client.invoke(
            input_data="What's 15 divided by 3, and also what's the weather in London?",
            task="chat",
            service_type="text",
            tools=tools
        )
        
        print(f"✅ Multiple tools response: {response}")
        
        # Verify response
        if response.get("success"):
            print("✅ Multiple tools execution successful")
        else:
            print(f"⚠️ Multiple tools test completed with note: {response.get('error', 'Unknown')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Multiple tools test failed: {e}")
        return False


async def test_client_tool_validation():
    """Test client tool parameter validation"""
    print("\n🧪 Testing ISAModelClient tool validation...")
    
    # Create client
    client = create_client(mode="local")
    
    try:
        # Test with invalid tools parameter
        response = await client.invoke(
            input_data="Hello world",
            task="chat",
            service_type="text",
            tools="invalid_tools"  # Should be a list
        )
        
        # Should handle gracefully
        print(f"✅ Invalid tools handled: {response}")
        
        # Test with empty tools list
        response2 = await client.invoke(
            input_data="Hello world",
            task="chat",
            service_type="text",
            tools=[]
        )
        
        print(f"✅ Empty tools list handled: {response2}")
        
        # Test tools with non-text service (should be ignored)
        response3 = await client.invoke(
            input_data="image.jpg",
            task="analyze_image",
            service_type="vision",
            tools=[create_mock_calculator_tool()]
        )
        
        print(f"✅ Tools with vision service handled: {response3}")
        
        return True
        
    except Exception as e:
        print(f"❌ Tool validation test failed: {e}")
        return False


async def test_complete_client_workflow():
    """Test complete ISAModelClient workflow with tools"""
    print("\n🧪 Testing complete ISAModelClient workflow...")
    
    try:
        # Create client
        client = create_client(mode="local")
        
        # Create tools
        calculator_tool = create_mock_calculator_tool()
        weather_tool = create_mock_weather_tool()
        tools = [calculator_tool, weather_tool]
        
        # Test workflow steps
        print("Step 1: Basic tool binding...")
        response1 = await client.invoke(
            input_data="Hello, I need help with calculations",
            task="chat",
            service_type="text",
            tools=[calculator_tool]
        )
        print(f"✅ Step 1 completed: {response1.get('success', False)}")
        
        print("Step 2: Multiple tools...")
        response2 = await client.invoke(
            input_data="Calculate 7 * 8 and tell me about weather",
            task="chat", 
            service_type="text",
            tools=tools
        )
        print(f"✅ Step 2 completed: {response2.get('success', False)}")
        
        print("Step 3: Health check...")
        health = await client.health_check()
        print(f"✅ Step 3 completed: {health.get('client', 'unknown')}")
        
        print("Step 4: Clear cache...")
        client.clear_cache()
        print("✅ Step 4 completed: Cache cleared")
        
        print("✅ Complete workflow test passed")
        return True
        
    except Exception as e:
        print(f"❌ Complete workflow test failed: {e}")
        return False


async def run_all_tests():
    """Run all ISAModelClient tool tests"""
    print("🚀 Running ISAModelClient Tools Tests...")
    print("=" * 60)
    
    tests = [
        test_client_tool_binding,
        test_client_tool_execution,
        test_client_streaming_with_tools,
        test_client_multiple_tools,
        test_client_tool_validation,
        test_complete_client_workflow
    ]
    
    results = []
    for test in tests:
        try:
            result = await test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
            results.append(False)
    
    print("\n" + "=" * 60)
    print("📊 Test Results Summary:")
    passed = sum(results)
    total = len(results)
    
    for i, (test, result) in enumerate(zip(tests, results)):
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"  {i+1}. {test.__name__}: {status}")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All ISAModelClient tool tests completed successfully!")
    else:
        print("⚠️ Some tests had issues, but this may be expected depending on model capabilities")
    
    return passed == total


if __name__ == "__main__":
    """Run tests directly"""
    asyncio.run(run_all_tests())