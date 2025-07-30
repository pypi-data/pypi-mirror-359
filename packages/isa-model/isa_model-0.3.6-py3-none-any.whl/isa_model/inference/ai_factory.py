#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Simplified AI Factory for creating inference services
Uses the new unified service architecture with centralized managers
"""

from typing import Dict, Any, Optional, TYPE_CHECKING
import logging
from isa_model.inference.services.base_service import BaseService
from isa_model.core.models.model_manager import ModelManager
from isa_model.core.config import ConfigManager

if TYPE_CHECKING:
    from isa_model.inference.services.audio.base_stt_service import BaseSTTService
    from isa_model.inference.services.audio.base_tts_service import BaseTTSService
    from isa_model.inference.services.vision.base_vision_service import BaseVisionService
    from isa_model.inference.services.img.base_image_gen_service import BaseImageGenService

logger = logging.getLogger(__name__)

class AIFactory:
    """
    Modernized AI Factory using centralized ModelManager and ConfigManager
    Provides unified interface with only 6 core methods: get_llm, get_vision, get_img, get_stt, get_tts, get_embed
    """
    
    _instance = None
    _is_initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize the AI Factory."""
        if not self._is_initialized:
            # Use centralized managers
            self.model_manager = ModelManager()
            self.config_manager = ConfigManager()
            self._cached_services: Dict[str, BaseService] = {}
            
            logger.info("AI Factory initialized with centralized ModelManager and ConfigManager")
            AIFactory._is_initialized = True
    
    # Core service methods using centralized architecture
    def get_llm(self, model_name: Optional[str] = None, provider: Optional[str] = None,
                config: Optional[Dict[str, Any]] = None) -> BaseService:
        """
        Get a LLM service instance with automatic defaults
        
        Args:
            model_name: Name of the model to use (defaults: OpenAI="gpt-4.1-mini", Ollama="llama3.2:3b", YYDS="claude-sonnet-4-20250514")
            provider: Provider name (defaults to 'openai' for production, 'ollama' for dev)
            config: Optional configuration dictionary
            
        Returns:
            LLM service instance
        """
        # Set defaults based on provider
        if provider == "openai":
            final_model_name = model_name or "gpt-4.1-mini"
            final_provider = provider
        elif provider == "ollama":
            final_model_name = model_name or "llama3.2:3b-instruct-fp16"
            final_provider = provider
        elif provider == "yyds":
            final_model_name = model_name or "claude-sonnet-4-20250514"
            final_provider = provider
        else:
            # Default provider selection - OpenAI with cheapest model
            final_provider = provider or "openai"
            if final_provider == "openai":
                final_model_name = model_name or "gpt-4.1-mini"
            elif final_provider == "ollama":
                final_model_name = model_name or "llama3.2:3b-instruct-fp16"
            else:
                final_model_name = model_name or "gpt-4.1-mini"
        
        # Create service using new centralized approach
        try:
            if final_provider == "openai":
                from isa_model.inference.services.llm.openai_llm_service import OpenAILLMService
                return OpenAILLMService(provider_name=final_provider, model_name=final_model_name, 
                                      model_manager=self.model_manager, config_manager=self.config_manager)
            elif final_provider == "ollama":
                from isa_model.inference.services.llm.ollama_llm_service import OllamaLLMService
                return OllamaLLMService(provider_name=final_provider, model_name=final_model_name,
                                      model_manager=self.model_manager, config_manager=self.config_manager)
            elif final_provider == "yyds":
                from isa_model.inference.services.llm.yyds_llm_service import YydsLLMService
                return YydsLLMService(provider_name=final_provider, model_name=final_model_name,
                                    model_manager=self.model_manager, config_manager=self.config_manager)
            else:
                raise ValueError(f"Unsupported LLM provider: {final_provider}")
        except Exception as e:
            logger.error(f"Failed to create LLM service: {e}")
            raise
    
    def get_vision(
        self,
        model_name: Optional[str] = None,
        provider: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None
    ) -> 'BaseVisionService':
        """
        Get vision service with automatic defaults
        
        Args:
            model_name: Model name. Special names:
                       - "isa_vision_table": Table extraction service
                       - "isa_vision_ui": UI detection service  
                       - "isa_vision_doc": Document analysis service
                       - Default: "gpt-4.1-mini"
            provider: Provider name (auto-detected for ISA services)
            config: Optional configuration override
            
        Returns:
            Vision service instance
        """
        # Handle special ISA vision services
        if model_name in ["isa_vision_table", "isa_vision_ui", "isa_vision_doc"]:
            try:
                from isa_model.inference.services.vision.auto_deploy_vision_service import AutoDeployVisionService
                logger.info(f"Creating auto-deploy service wrapper for {model_name}")
                return AutoDeployVisionService(model_name, config)
            except Exception as e:
                logger.error(f"Failed to create ISA vision service: {e}")
                raise
        
        # Set defaults for regular services
        if provider == "openai":
            final_model_name = model_name or "gpt-4.1-mini"
            final_provider = provider
        elif provider == "ollama":
            final_model_name = model_name or "llama3.2-vision:latest"
            final_provider = provider
        elif provider == "replicate":
            final_model_name = model_name or "meta/llama-2-70b-chat"
            final_provider = provider
        else:
            # Default provider selection
            final_provider = provider or "openai"
            if final_provider == "openai":
                final_model_name = model_name or "gpt-4.1-mini"
            elif final_provider == "ollama":
                final_model_name = model_name or "llama3.2-vision:latest"
            else:
                final_model_name = model_name or "gpt-4.1-mini"
        
        # Create service using new centralized approach
        try:
            if final_provider == "openai":
                from isa_model.inference.services.vision.openai_vision_service import OpenAIVisionService
                return OpenAIVisionService(provider_name=final_provider, model_name=final_model_name,
                                         model_manager=self.model_manager, config_manager=self.config_manager)
            elif final_provider == "replicate":
                from isa_model.inference.services.vision.replicate_vision_service import ReplicateVisionService
                return ReplicateVisionService(provider_name=final_provider, model_name=final_model_name,
                                            model_manager=self.model_manager, config_manager=self.config_manager)
            else:
                raise ValueError(f"Unsupported vision provider: {final_provider}")
        except Exception as e:
            logger.error(f"Failed to create vision service: {e}")
            raise
    
    def get_img(self, type: str = "t2i", model_name: Optional[str] = None, provider: Optional[str] = None,
                config: Optional[Dict[str, Any]] = None) -> 'BaseImageGenService':
        """
        Get an image generation service with type-specific defaults
        
        Args:
            type: Image generation type:
                  - "t2i" (text-to-image): Uses flux-schnell ($3 per 1000 images)
                  - "i2i" (image-to-image): Uses flux-kontext-pro ($0.04 per image)
            model_name: Optional model name override
            provider: Provider name (defaults to 'replicate')
            config: Optional configuration dictionary
            
        Returns:
            Image generation service instance
            
        Usage:
            # Text-to-image (default)
            img_service = AIFactory().get_img()
            img_service = AIFactory().get_img(type="t2i")
            
            # Image-to-image
            img_service = AIFactory().get_img(type="i2i")
            
            # Custom model
            img_service = AIFactory().get_img(type="t2i", model_name="custom-model")
        """
        # Set defaults based on type
        final_provider = provider or "replicate"
        
        if type == "t2i":
            # Text-to-image: flux-schnell
            final_model_name = model_name or "black-forest-labs/flux-schnell"
        elif type == "i2i":
            # Image-to-image: flux-kontext-pro
            final_model_name = model_name or "black-forest-labs/flux-kontext-pro"
        else:
            raise ValueError(f"Unknown image generation type: {type}. Use 't2i' or 'i2i'")
        
        # Create service using new centralized architecture
        try:
            if final_provider == "replicate":
                from isa_model.inference.services.img.replicate_image_gen_service import ReplicateImageGenService
                return ReplicateImageGenService(provider_name=final_provider, model_name=final_model_name,
                                              model_manager=self.model_manager, config_manager=self.config_manager)
            else:
                raise ValueError(f"Unsupported image generation provider: {final_provider}")
        except Exception as e:
            logger.error(f"Failed to create image generation service: {e}")
            raise

    def get_stt(self, model_name: Optional[str] = None, provider: Optional[str] = None,
                config: Optional[Dict[str, Any]] = None) -> 'BaseSTTService':
        """
        Get Speech-to-Text service with automatic defaults
        
        Args:
            model_name: Name of the model to use (defaults: "whisper-1")
            provider: Provider name (defaults to 'openai')
            config: Optional configuration dictionary
            
        Returns:
            STT service instance
        """
        # Set defaults
        final_provider = provider or "openai"
        final_model_name = model_name or "whisper-1"
        
        # Create service using new centralized approach
        try:
            if final_provider == "openai":
                from isa_model.inference.services.audio.openai_stt_service import OpenAISTTService
                return OpenAISTTService(provider_name=final_provider, model_name=final_model_name,
                                      model_manager=self.model_manager, config_manager=self.config_manager)
            else:
                raise ValueError(f"Unsupported STT provider: {final_provider}")
        except Exception as e:
            logger.error(f"Failed to create STT service: {e}")
            raise

    def get_tts(self, model_name: Optional[str] = None, provider: Optional[str] = None,
                config: Optional[Dict[str, Any]] = None) -> 'BaseTTSService':
        """
        Get Text-to-Speech service with automatic defaults
        
        Args:
            model_name: Name of the model to use (defaults: Replicate="kokoro-82m", OpenAI="tts-1")
            provider: Provider name (defaults to 'replicate' for production, 'openai' for dev)
            config: Optional configuration dictionary
            
        Returns:
            TTS service instance
        """
        # Set defaults based on provider
        if provider == "replicate":
            final_model_name = model_name or "kokoro-82m"
            final_provider = provider
        elif provider == "openai":
            final_model_name = model_name or "tts-1"
            final_provider = provider
        else:
            # Default provider selection
            final_provider = provider or "replicate"
            if final_provider == "replicate":
                final_model_name = model_name or "kokoro-82m"
            else:
                final_model_name = model_name or "tts-1"
        
        # Create service using new centralized approach
        try:
            if final_provider == "replicate":
                from isa_model.inference.services.audio.replicate_tts_service import ReplicateTTSService
                # Use full model name for Replicate
                if final_model_name == "kokoro-82m":
                    final_model_name = "jaaari/kokoro-82m:f559560eb822dc509045f3921a1921234918b91739db4bf3daab2169b71c7a13"
                return ReplicateTTSService(provider_name=final_provider, model_name=final_model_name,
                                         model_manager=self.model_manager, config_manager=self.config_manager)
            elif final_provider == "openai":
                from isa_model.inference.services.audio.openai_tts_service import OpenAITTSService
                return OpenAITTSService(provider_name=final_provider, model_name=final_model_name,
                                      model_manager=self.model_manager, config_manager=self.config_manager)
            else:
                raise ValueError(f"Unsupported TTS provider: {final_provider}")
        except Exception as e:
            logger.error(f"Failed to create TTS service: {e}")
            raise
    
    def get_embed(self, model_name: Optional[str] = None, provider: Optional[str] = None,
                     config: Optional[Dict[str, Any]] = None) -> BaseService:
        """
        Get embedding service with automatic defaults
        
        Args:
            model_name: Name of the model to use (defaults: OpenAI="text-embedding-3-small", Ollama="bge-m3")
            provider: Provider name (defaults to 'openai' for production)
            config: Optional configuration dictionary
            
        Returns:
            Embedding service instance
        """
        # Set defaults based on provider
        if provider == "openai":
            final_model_name = model_name or "text-embedding-3-small"
            final_provider = provider
        elif provider == "ollama":
            final_model_name = model_name or "bge-m3"
            final_provider = provider
        else:
            # Default provider selection
            final_provider = provider or "openai"
            if final_provider == "openai":
                final_model_name = model_name or "text-embedding-3-small"
            else:
                final_model_name = model_name or "bge-m3"
        
        # Create service using new centralized approach
        try:
            if final_provider == "openai":
                from isa_model.inference.services.embedding.openai_embed_service import OpenAIEmbedService
                return OpenAIEmbedService(provider_name=final_provider, model_name=final_model_name,
                                        model_manager=self.model_manager, config_manager=self.config_manager)
            elif final_provider == "ollama":
                from isa_model.inference.services.embedding.ollama_embed_service import OllamaEmbedService
                return OllamaEmbedService(provider_name=final_provider, model_name=final_model_name,
                                        model_manager=self.model_manager, config_manager=self.config_manager)
            else:
                raise ValueError(f"Unsupported embedding provider: {final_provider}")
        except Exception as e:
            logger.error(f"Failed to create embedding service: {e}")
            raise

    def clear_cache(self):
        """Clear the service cache"""
        self._cached_services.clear()
        logger.info("Service cache cleared")
    
    @classmethod
    def get_instance(cls) -> 'AIFactory':
        """Get the singleton instance"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance