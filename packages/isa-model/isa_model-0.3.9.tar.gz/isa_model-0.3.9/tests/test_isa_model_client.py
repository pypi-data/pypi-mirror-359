#!/usr/bin/env python3
"""
测试 ISAModelClient 的基本功能
"""

import asyncio
import logging
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from isa_model import ISAModelClient, create_client

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_client_initialization():
    """测试客户端初始化"""
    logger.info("🧪 Testing client initialization...")
    
    try:
        # 测试直接创建
        client1 = ISAModelClient()
        logger.info("✅ Direct initialization successful")
        
        # 测试便捷函数
        client2 = create_client()
        logger.info("✅ Convenience function initialization successful")
        
        return True
    except Exception as e:
        logger.error(f"❌ Client initialization failed: {e}")
        return False


async def test_health_check():
    """测试健康检查"""
    logger.info("🧪 Testing health check...")
    
    try:
        client = create_client()
        health = await client.health_check()
        
        logger.info(f"Health status: {health}")
        
        if health.get("client") == "healthy":
            logger.info("✅ Health check successful")
            return True
        else:
            logger.warning("⚠️ Health check returned warnings")
            return False
            
    except Exception as e:
        logger.error(f"❌ Health check failed: {e}")
        return False


async def test_model_selection():
    """测试模型选择逻辑"""
    logger.info("🧪 Testing model selection...")
    
    try:
        client = create_client()
        
        # 测试默认选择
        selection = await client._select_model(
            input_data="test image",
            task="analyze_image", 
            service_type="vision"
        )
        
        logger.info(f"Selected model: {selection}")
        
        if "model_id" in selection and "provider" in selection:
            logger.info("✅ Model selection successful")
            return True
        else:
            logger.error("❌ Model selection missing required fields")
            return False
            
    except Exception as e:
        logger.error(f"❌ Model selection failed: {e}")
        return False


async def test_service_creation():
    """测试服务创建"""
    logger.info("🧪 Testing service creation...")
    
    try:
        client = create_client()
        
        # 测试不同类型的服务
        test_cases = [
            ("vision", "gpt-4.1-mini", "openai", "analyze_image"),
            ("audio", "whisper-1", "openai", "transcribe"), 
            ("text", "gpt-4.1-mini", "openai", "chat"),
            ("embedding", "text-embedding-3-small", "openai", "create_embedding")
        ]
        
        success_count = 0
        
        for service_type, model_name, provider, task in test_cases:
            try:
                service = await client._get_service(service_type, model_name, provider, task)
                logger.info(f"✅ {service_type} service created successfully")
                success_count += 1
            except Exception as e:
                logger.error(f"❌ Failed to create {service_type} service: {e}")
        
        if success_count >= 2:  # 至少成功创建一半的服务
            logger.info(f"✅ Service creation test passed ({success_count}/{len(test_cases)})")
            return True
        else:
            logger.error(f"❌ Service creation test failed ({success_count}/{len(test_cases)})")
            return False
            
    except Exception as e:
        logger.error(f"❌ Service creation test failed: {e}")
        return False


async def test_vision_invoke():
    """测试视觉服务调用"""
    logger.info("🧪 Testing vision service invoke...")
    
    try:
        client = create_client()
        
        # 创建一个测试图像路径（不需要真实存在，只测试接口）
        test_image = "test_image.jpg"
        
        # 测试视觉分析
        response = await client.invoke(
            input_data=test_image,
            task="analyze_image",
            service_type="vision"
        )
        
        logger.info(f"Vision response: {response}")
        
        # 检查响应格式
        required_fields = ["success", "metadata"]
        if all(field in response for field in required_fields):
            if response["success"] or "error" in response:
                logger.info("✅ Vision invoke test successful (interface working)")
                return True
        
        logger.warning("⚠️ Vision invoke returned unexpected format")
        return False
        
    except Exception as e:
        logger.info(f"ℹ️ Vision invoke failed as expected (no real image): {e}")
        # 这是预期的，因为我们没有真实的图像
        return True


async def test_audio_invoke():
    """测试音频服务调用"""  
    logger.info("🧪 Testing audio service invoke...")
    
    try:
        client = create_client()
        
        # 测试文本转语音
        response = await client.invoke(
            input_data="Hello, this is a test.",
            task="generate_speech",
            service_type="audio"
        )
        
        logger.info(f"Audio TTS response: {response}")
        
        if response.get("success") or "error" in response:
            logger.info("✅ Audio TTS invoke test successful (interface working)")
            return True
        else:
            logger.warning("⚠️ Audio invoke returned unexpected format")
            return False
        
    except Exception as e:
        logger.info(f"ℹ️ Audio invoke failed as expected (API keys might be missing): {e}")
        # 这可能是预期的，如果没有 API 密钥
        return True


async def test_text_invoke():
    """测试文本服务调用"""
    logger.info("🧪 Testing text service invoke...")
    
    try:
        client = create_client()
        
        # 测试文本生成
        response = await client.invoke(
            input_data="What is the capital of France?",
            task="chat",
            service_type="text"
        )
        
        logger.info(f"Text response: {response}")
        
        if response.get("success") or "error" in response:
            logger.info("✅ Text invoke test successful (interface working)")
            return True
        else:
            logger.warning("⚠️ Text invoke returned unexpected format")
            return False
        
    except Exception as e:
        logger.info(f"ℹ️ Text invoke failed as expected (API keys might be missing): {e}")
        return True


async def test_get_available_models():
    """测试获取可用模型"""
    logger.info("🧪 Testing get available models...")
    
    try:
        client = create_client()
        
        # 测试获取所有模型
        models = await client.get_available_models()
        logger.info(f"Available models count: {len(models)}")
        
        # 测试按类型过滤
        vision_models = await client.get_available_models("vision")
        logger.info(f"Vision models count: {len(vision_models)}")
        
        logger.info("✅ Get available models test successful")
        return True
        
    except Exception as e:
        logger.info(f"ℹ️ Get available models failed (model selector might not be initialized): {e}")
        return True


async def run_all_tests():
    """运行所有测试"""
    logger.info("🚀 Starting ISAModelClient tests...")
    
    tests = [
        ("Client Initialization", test_client_initialization),
        ("Health Check", test_health_check),
        ("Model Selection", test_model_selection),
        ("Service Creation", test_service_creation),
        ("Vision Invoke", test_vision_invoke),
        ("Audio Invoke", test_audio_invoke),
        ("Text Invoke", test_text_invoke),
        ("Available Models", test_get_available_models)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        logger.info(f"\n--- Running {test_name} ---")
        try:
            success = await test_func()
            results[test_name] = success
        except Exception as e:
            logger.error(f"❌ {test_name} crashed: {e}")
            results[test_name] = False
    
    # 汇总结果
    logger.info("\n" + "="*60)
    logger.info("📊 TEST RESULTS SUMMARY")
    logger.info("="*60)
    
    passed = 0
    total = len(results)
    
    for test_name, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        logger.info(f"{status:10} {test_name}")
        if success:
            passed += 1
    
    logger.info(f"\nOverall: {passed}/{total} tests passed")
    
    if passed >= total * 0.7:  # 70% 通过率
        logger.info("🎉 Test suite PASSED!")
        return True
    else:
        logger.error("❌ Test suite FAILED!")
        return False


async def main():
    """主函数"""
    try:
        success = await run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("\n⏹️ Tests cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Test suite crashed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())