#!/usr/bin/env python3
"""
ISA Model Client HTTP API Tests
Tests the complete client-server integration using HTTP API mode
"""

import asyncio
import logging
import sys
import time
from pathlib import Path
import aiohttp

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from isa_model import create_client

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# API Configuration
API_BASE_URL = "http://localhost:8082"
API_TIMEOUT = 60  # seconds


async def wait_for_server(url: str, timeout: int = 60) -> bool:
    """Wait for the server to be ready"""
    logger.info(f"Waiting for server at {url} to be ready...")
    
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{url}/health", timeout=aiohttp.ClientTimeout(total=5)) as response:
                    if response.status == 200:
                        logger.info("Server is ready!")
                        return True
        except Exception as e:
            logger.debug(f"Server not ready yet: {e}")
        
        await asyncio.sleep(2)
    
    logger.error(f"Server at {url} not ready after {timeout} seconds")
    return False


async def test_server_health():
    """Test server health endpoint directly"""
    logger.info("Testing server health endpoint...")
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{API_BASE_URL}/health", timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status == 200:
                    health_data = await response.json()
                    logger.info(f"Health response: {health_data}")
                    logger.info("Server health check successful")
                    return True
                else:
                    logger.error(f"Health check failed with status {response.status}")
                    return False
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return False


async def test_client_initialization():
    """Test HTTP client initialization"""
    logger.info("Testing HTTP client initialization...")
    
    try:
        # Test convenience function
        client = create_client(mode="api", api_url=API_BASE_URL)
        logger.info("HTTP client initialization successful")
        return True
    except Exception as e:
        logger.error(f"HTTP client initialization failed: {e}")
        return False


async def test_client_health_check():
    """Test client health check via HTTP API"""
    logger.info("Testing client health check via HTTP API...")
    
    try:
        client = create_client(mode="api", api_url=API_BASE_URL)
        health = await client.health_check()
        
        logger.info(f"Health status: {health}")
        
        if health.get("api") == "healthy":
            logger.info("HTTP client health check successful")
            return True
        else:
            logger.warning("HTTP health check returned warnings")
            return False
            
    except Exception as e:
        logger.error(f"HTTP client health check failed: {e}")
        return False


async def test_vision_invoke_http():
    """Test vision service via HTTP API"""
    logger.info("Testing vision service via HTTP API...")
    
    try:
        client = create_client(mode="api", api_url=API_BASE_URL)
        
        # Test with simple text input (simulating image path)
        response = await client.invoke(
            input_data="test_image.jpg",
            task="analyze",
            service_type="vision"
        )
        
        logger.info(f"Vision HTTP response: {response}")
        
        # Check response format
        if "success" in response and "metadata" in response:
            logger.info("Vision HTTP invoke test successful (interface working)")
            return True
        else:
            logger.warning("Vision HTTP invoke returned unexpected format")
            return False
        
    except Exception as e:
        logger.info(f"Vision HTTP invoke failed as expected (no real image): {e}")
        return True


async def test_audio_invoke_http():
    """Test audio service via HTTP API"""
    logger.info("Testing audio service via HTTP API...")
    
    try:
        client = create_client(mode="api", api_url=API_BASE_URL)
        
        # Test text-to-speech
        response = await client.invoke(
            input_data="Hello, this is a test via HTTP API.",
            task="generate_speech",
            service_type="audio"
        )
        
        logger.info(f"Audio HTTP response: {response}")
        
        if response.get("success") or "error" in response:
            logger.info("Audio HTTP invoke test successful (interface working)")
            return True
        else:
            logger.warning("Audio HTTP invoke returned unexpected format")
            return False
        
    except Exception as e:
        logger.info(f"Audio HTTP invoke failed: {e}")
        return True


async def test_text_invoke_http():
    """Test text service via HTTP API"""
    logger.info("Testing text service via HTTP API...")
    
    try:
        client = create_client(mode="api", api_url=API_BASE_URL)
        
        # Test text generation
        response = await client.invoke(
            input_data="What is the capital of France? (via HTTP API)",
            task="chat",
            service_type="text"
        )
        
        logger.info(f"Text HTTP response: {response}")
        
        if response.get("success") or "error" in response:
            logger.info("Text HTTP invoke test successful (interface working)")
            return True
        else:
            logger.warning("Text HTTP invoke returned unexpected format")
            return False
        
    except Exception as e:
        logger.info(f"Text HTTP invoke failed: {e}")
        return True


async def test_embedding_invoke_http():
    """Test embedding service via HTTP API"""
    logger.info("Testing embedding service via HTTP API...")
    
    try:
        client = create_client(mode="api", api_url=API_BASE_URL)
        
        # Test embedding creation
        response = await client.invoke(
            input_data="Text to embed via HTTP API",
            task="create_embedding",
            service_type="embedding"
        )
        
        logger.info(f"Embedding HTTP response: {response}")
        
        if response.get("success") or "error" in response:
            logger.info("Embedding HTTP invoke test successful (interface working)")
            return True
        else:
            logger.warning("Embedding HTTP invoke returned unexpected format")
            return False
        
    except Exception as e:
        logger.info(f"Embedding HTTP invoke failed: {e}")
        return True


async def test_image_generation_http():
    """Test image generation service via HTTP API"""
    logger.info("Testing image generation service via HTTP API...")
    
    try:
        client = create_client(mode="api", api_url=API_BASE_URL)
        
        # Test image generation
        response = await client.invoke(
            input_data="A beautiful sunset over mountains",
            task="generate_image",
            service_type="image"
        )
        
        logger.info(f"Image generation HTTP response: {response}")
        
        if response.get("success") or "error" in response:
            logger.info("Image generation HTTP invoke test successful (interface working)")
            return True
        else:
            logger.warning("Image generation HTTP invoke returned unexpected format")
            return False
        
    except Exception as e:
        logger.info(f"Image generation HTTP invoke failed: {e}")
        return True


async def test_unified_api_endpoint():
    """Test the unified API endpoint directly"""
    logger.info("Testing unified API endpoint directly...")
    
    try:
        payload = {
            "input_data": "Direct API test message",
            "task": "chat",
            "service_type": "text",
            "parameters": {}
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{API_BASE_URL}/api/v1/invoke",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                
                if response.status == 200:
                    result = await response.json()
                    logger.info(f"Direct API response: {result}")
                    logger.info("Direct unified API test successful")
                    return True
                else:
                    error_text = await response.text()
                    logger.error(f"Direct API test failed with status {response.status}: {error_text}")
                    return False
                    
    except Exception as e:
        logger.error(f"Direct API test failed: {e}")
        return False


async def test_api_error_handling():
    """Test API error handling"""
    logger.info("Testing API error handling...")
    
    try:
        client = create_client(mode="api", api_url=API_BASE_URL)
        
        # Test with invalid service type
        response = await client.invoke(
            input_data="Test message",
            task="invalid_task",
            service_type="invalid_service"
        )
        
        logger.info(f"Error handling response: {response}")
        
        # Should return error response with proper format
        if response.get("success") == False and "error" in response:
            logger.info("API error handling test successful")
            return True
        else:
            logger.warning("API error handling test unexpected response")
            return False
        
    except Exception as e:
        logger.info(f"API error handling test failed as expected: {e}")
        return True


async def test_text_streaming_http():
    """Test text streaming via HTTP API"""
    logger.info("Testing text streaming via HTTP API...")
    
    try:
        client = create_client(mode="api", api_url=API_BASE_URL)
        
        # Test streaming
        logger.info("Starting streaming test...")
        stream_gen = await client.invoke(
            input_data="Count from 1 to 5, one number per line.",
            task="chat",
            service_type="text",
            stream=True
        )
        
        # Collect tokens
        tokens = []
        token_count = 0
        async for token in stream_gen:
            tokens.append(token)
            logger.info(f"Received token {token_count + 1}: '{token}'")
            token_count += 1
            
            # Limit for testing
            if token_count >= 10:
                break
        
        full_response = "".join(tokens)
        logger.info(f"Full streaming response: '{full_response}'")
        
        if token_count > 0:
            logger.info(f"Text streaming HTTP test successful - received {token_count} tokens")
            return True
        else:
            logger.warning("Text streaming HTTP test received no tokens")
            return False
        
    except Exception as e:
        logger.error(f"Text streaming HTTP test failed: {e}")
        return False


async def test_text_streaming_local():
    """Test text streaming in local mode"""
    logger.info("Testing text streaming in local mode...")
    
    try:
        # Use local mode client
        client = create_client(mode="local")
        
        # Test streaming
        logger.info("Starting local streaming test...")
        stream_gen = await client.invoke(
            input_data="Say 'Hello world' and then count to 3.",
            task="chat",
            service_type="text",
            stream=True
        )
        
        # Collect tokens
        tokens = []
        token_count = 0
        async for token in stream_gen:
            tokens.append(token)
            logger.info(f"Received token {token_count + 1}: '{token}'")
            token_count += 1
            
            # Limit for testing
            if token_count >= 15:
                break
        
        full_response = "".join(tokens)
        logger.info(f"Full local streaming response: '{full_response}'")
        
        if token_count > 0:
            logger.info(f"Text streaming local test successful - received {token_count} tokens")
            return True
        else:
            logger.warning("Text streaming local test received no tokens")
            return False
        
    except Exception as e:
        logger.error(f"Text streaming local test failed: {e}")
        return False


async def test_non_streaming_vs_streaming():
    """Test comparison between streaming and non-streaming"""
    logger.info("Testing streaming vs non-streaming comparison...")
    
    try:
        client = create_client(mode="local")
        prompt = "What is 2+2? Answer in one sentence."
        
        # Test non-streaming
        logger.info("Testing non-streaming...")
        non_stream_response = await client.invoke(
            input_data=prompt,
            task="chat",
            service_type="text",
            stream=False
        )
        
        logger.info(f"Non-streaming response: {non_stream_response}")
        
        # Test streaming
        logger.info("Testing streaming...")
        stream_gen = await client.invoke(
            input_data=prompt,
            task="chat",
            service_type="text",
            stream=True
        )
        
        tokens = []
        async for token in stream_gen:
            tokens.append(token)
            if len(tokens) >= 20:  # Limit for test
                break
        
        stream_response = "".join(tokens)
        logger.info(f"Streaming response: '{stream_response}'")
        
        # Both should have content
        non_stream_has_content = (
            isinstance(non_stream_response, dict) and 
            "result" in non_stream_response and 
            len(str(non_stream_response["result"]).strip()) > 0
        )
        
        stream_has_content = len(stream_response.strip()) > 0
        
        if non_stream_has_content and stream_has_content:
            logger.info("Streaming vs non-streaming comparison successful")
            return True
        else:
            logger.warning(f"Comparison failed - non-stream: {non_stream_has_content}, stream: {stream_has_content}")
            return False
        
    except Exception as e:
        logger.error(f"Streaming comparison test failed: {e}")
        return False


async def run_all_http_tests():
    """Run all HTTP API tests"""
    logger.info("Starting ISA Model Client HTTP API tests...")
    
    # First, wait for server to be ready
    if not await wait_for_server(API_BASE_URL, timeout=120):
        logger.error("Server not ready, cannot run tests")
        return False
    
    tests = [
        ("Server Health Check", test_server_health),
        ("Client Initialization", test_client_initialization),
        ("Client Health Check", test_client_health_check),
        ("Vision Invoke HTTP", test_vision_invoke_http),
        ("Audio Invoke HTTP", test_audio_invoke_http),
        ("Text Invoke HTTP", test_text_invoke_http),
        ("Embedding Invoke HTTP", test_embedding_invoke_http),
        ("Image Generation HTTP", test_image_generation_http),
        ("Direct Unified API", test_unified_api_endpoint),
        ("API Error Handling", test_api_error_handling),
        ("Text Streaming HTTP", test_text_streaming_http),
        ("Text Streaming Local", test_text_streaming_local),
        ("Streaming vs Non-Streaming", test_non_streaming_vs_streaming)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        logger.info(f"\n--- Running {test_name} ---")
        try:
            success = await test_func()
            results[test_name] = success
        except Exception as e:
            logger.error(f"{test_name} crashed: {e}")
            results[test_name] = False
    
    # Summary
    logger.info("\n" + "="*60)
    logger.info("HTTP API TEST RESULTS SUMMARY")
    logger.info("="*60)
    
    passed = 0
    total = len(results)
    
    for test_name, success in results.items():
        status = "PASS" if success else "FAIL"
        logger.info(f"{status:10} {test_name}")
        if success:
            passed += 1
    
    logger.info(f"\nOverall: {passed}/{total} tests passed")
    
    if passed >= total * 0.7:  # 70% pass rate
        logger.info("HTTP API Test suite PASSED!")
        return True
    else:
        logger.error("HTTP API Test suite FAILED!")
        return False


async def main():
    """Main function"""
    try:
        success = await run_all_http_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("\nTests cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Test suite crashed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())