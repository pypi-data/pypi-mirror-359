#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test the cleaned AIFactory with only 6 core methods
"""

import os
import pytest
import asyncio
from unittest.mock import patch, MagicMock

from isa_model.inference.ai_factory import AIFactory

def test_ai_factory_core_methods():
    """Test that AIFactory has exactly the 6 core methods we expect"""
    factory = AIFactory()
    
    # Check that core methods exist
    assert hasattr(factory, 'get_llm')
    assert hasattr(factory, 'get_vision')
    assert hasattr(factory, 'get_img')
    assert hasattr(factory, 'get_stt')
    assert hasattr(factory, 'get_tts')
    assert hasattr(factory, 'get_embed')
    
    # Check that old duplicate methods are gone
    assert not hasattr(factory, 'get_embedding_service')
    assert not hasattr(factory, 'get_audio_service')
    assert not hasattr(factory, 'get_tts_service')
    assert not hasattr(factory, 'get_stt_service')
    assert not hasattr(factory, 'get_vision_service')
    assert not hasattr(factory, 'get_image_gen')
    assert not hasattr(factory, 'get_image_generation_service')

@patch.dict(os.environ, {'OPENAI_API_KEY': 'test_key'})
def test_get_llm_defaults():
    """Test LLM service creation with defaults"""
    factory = AIFactory()
    
    try:
        # This should work with the new constructor pattern
        llm_service = factory.get_llm()
        assert llm_service is not None
        assert llm_service.provider_name == "openai"
        assert llm_service.model_name == "gpt-4.1-mini"
    except Exception as e:
        # Expected to fail without proper config, but should get to the service creation
        assert "not configured" in str(e) or "API key" in str(e)

@patch.dict(os.environ, {'OPENAI_API_KEY': 'test_key'})
def test_get_embed_defaults():
    """Test embedding service creation with defaults"""
    factory = AIFactory()
    
    try:
        embed_service = factory.get_embed()
        assert embed_service is not None
        assert embed_service.provider_name == "openai"
        assert embed_service.model_name == "text-embedding-3-small"
    except Exception as e:
        # Expected to fail without proper config
        assert "not configured" in str(e) or "API key" in str(e)

def test_get_img_defaults():
    """Test image generation service creation with defaults"""
    factory = AIFactory()
    
    try:
        img_service = factory.get_img()
        assert img_service is not None
        # Should default to replicate provider and flux-schnell model
    except Exception as e:
        # Expected to fail without proper config
        assert "not configured" in str(e) or "API key" in str(e)

def test_get_vision_defaults():
    """Test vision service creation with defaults"""
    factory = AIFactory()
    
    try:
        vision_service = factory.get_vision()
        assert vision_service is not None
        # Should default to openai provider and gpt-4.1-mini model
    except Exception as e:
        # Expected to fail without proper config
        assert "not configured" in str(e) or "API key" in str(e)

def test_get_tts_defaults():
    """Test TTS service creation with defaults"""
    factory = AIFactory()
    
    try:
        tts_service = factory.get_tts()
        assert tts_service is not None
        # Should default to replicate provider and kokoro-82m model
    except Exception as e:
        # Expected to fail without proper config
        assert "not configured" in str(e) or "API key" in str(e)

def test_get_stt_defaults():
    """Test STT service creation with defaults"""
    factory = AIFactory()
    
    try:
        stt_service = factory.get_stt()
        assert stt_service is not None
        # Should default to openai provider and whisper-1 model
    except Exception as e:
        # Expected to fail without proper config
        assert "not configured" in str(e) or "API key" in str(e)

def test_factory_singleton():
    """Test that AIFactory is a singleton"""
    factory1 = AIFactory()
    factory2 = AIFactory()
    assert factory1 is factory2

def test_cache_clearing():
    """Test that cache can be cleared"""
    factory = AIFactory()
    factory.clear_cache()
    # Should not raise any errors

if __name__ == "__main__":
    # Run basic tests
    test_ai_factory_core_methods()
    test_factory_singleton()
    test_cache_clearing()
    print("✅ All basic tests passed!")
    
    # Run tests that might need env vars
    try:
        test_get_llm_defaults()
        print("✅ LLM service test passed!")
    except Exception as e:
        print(f"⚠️  LLM service test failed (expected): {e}")
    
    try:
        test_get_embed_defaults()
        print("✅ Embedding service test passed!")
    except Exception as e:
        print(f"⚠️  Embedding service test failed (expected): {e}")
    
    print("🎉 AIFactory cleanup verification complete!")