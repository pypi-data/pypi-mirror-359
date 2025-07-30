#!/usr/bin/env python3
"""
增强的模型注册脚本
从 YAML 配置文件中读取模型定义，注册到 Supabase 数据库，并生成向量嵌入

Features:
- 支持注册到 Supabase 的 models 和 model_capabilities 表
- 自动生成模型描述的向量嵌入并存储到 model_embedding 表
- 支持批量注册、更新和验证
- 支持新的 omni 模型类型

Usage:
    python register_models_with_embeddings.py --all                    # 注册所有providers的模型
    python register_models_with_embeddings.py --provider openai        # 只注册openai的模型
    python register_models_with_embeddings.py --dry-run               # 仅验证配置，不实际注册
    python register_models_with_embeddings.py --update                # 更新已存在的模型
    python register_models_with_embeddings.py --embeddings-only       # 只生成嵌入，不注册模型
"""

import argparse
import asyncio
import logging
import sys
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
import yaml

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

try:
    from isa_model.core.storage.supabase_storage import SupabaseModelRegistry
    from isa_model.inference.ai_factory import AIFactory
    SUPABASE_AVAILABLE = True
except ImportError as e:
    logger.error(f"Required dependencies not available: {e}")
    SUPABASE_AVAILABLE = False


class EnhancedModelRegistrationScript:
    """增强的模型注册脚本，支持 Supabase 和向量嵌入"""
    
    def __init__(self):
        if not SUPABASE_AVAILABLE:
            raise ImportError("Supabase and other required dependencies not available")
        
        self.registry = SupabaseModelRegistry()
        self.ai_factory = AIFactory.get_instance()
        self.embedding_service = None
        self.config_dir = project_root / "config" / "models"
        
        # 支持的模型类型（包含新的 omni）
        self.supported_model_types = {
            "vision", "image", "audio", "text", "embedding", "omni"
        }
        
        # 支持的能力
        self.supported_capabilities = {
            "text_generation", "chat", "reasoning", "code_generation",
            "image_analysis", "image_understanding", "ocr", "ui_detection", 
            "table_detection", "image_generation", "style_transfer",
            "text_to_speech", "speech_to_text", "audio_transcription",
            "text_embedding", "image_enhancement"
        }
    
    async def initialize_embedding_service(self):
        """初始化嵌入服务"""
        try:
            self.embedding_service = self.ai_factory.get_embed("text-embedding-3-small", "openai")
            logger.info("Embedding service initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize embedding service: {e}")
            self.embedding_service = None
    
    def load_provider_config(self, provider: str) -> Dict[str, Any]:
        """加载 provider 的 YAML 配置"""
        config_file = self.config_dir / f"{provider}_models.yaml"
        
        if not config_file.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_file}")
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            logger.info(f"Loaded configuration for provider '{provider}' with {len(config.get('models', []))} models")
            return config
            
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in {config_file}: {e}")
    
    def validate_model_config(self, model_config: Dict[str, Any], provider: str) -> bool:
        """验证单个模型配置"""
        required_fields = ["model_id", "model_type", "capabilities", "metadata"]
        
        for field in required_fields:
            if field not in model_config:
                logger.error(f"Missing required field '{field}' in model config: {model_config}")
                return False
        
        # 验证 model_type
        model_type = model_config["model_type"]
        if model_type not in self.supported_model_types:
            logger.error(f"Invalid model_type '{model_type}' for model {model_config['model_id']}")
            logger.info(f"Supported types: {', '.join(self.supported_model_types)}")
            return False
        
        # 验证 capabilities
        capabilities = model_config["capabilities"]
        if not isinstance(capabilities, list) or not capabilities:
            logger.error(f"Capabilities must be a non-empty list for model {model_config['model_id']}")
            return False
        
        for cap in capabilities:
            if cap not in self.supported_capabilities:
                logger.warning(f"Unknown capability '{cap}' for model {model_config['model_id']}")
                # 不失败，只是警告
        
        # 验证 metadata
        metadata = model_config["metadata"]
        required_metadata = ["description", "performance_tier", "provider_model_name"]
        
        for field in required_metadata:
            if field not in metadata:
                logger.error(f"Missing required metadata field '{field}' for model {model_config['model_id']}")
                return False
        
        return True
    
    def validate_provider_config(self, config: Dict[str, Any], provider: str) -> bool:
        """验证 provider 的完整配置"""
        if "provider" not in config:
            logger.error(f"Missing 'provider' field in config")
            return False
        
        if config["provider"] != provider:
            logger.error(f"Provider mismatch: expected '{provider}', got '{config['provider']}'")
            return False
        
        if "models" not in config:
            logger.error(f"Missing 'models' field in config")
            return False
        
        models = config["models"]
        if not isinstance(models, list) or not models:
            logger.error(f"Models must be a non-empty list")
            return False
        
        # 验证每个模型
        valid_count = 0
        for i, model_config in enumerate(models):
            if self.validate_model_config(model_config, provider):
                valid_count += 1
            else:
                logger.error(f"Invalid configuration for model #{i+1}")
        
        if valid_count != len(models):
            logger.error(f"Only {valid_count}/{len(models)} models have valid configuration")
            return False
        
        logger.info(f"All {len(models)} models in {provider} configuration are valid")
        return True
    
    def create_search_text(self, model_config: Dict[str, Any]) -> str:
        """创建用于嵌入的搜索文本"""
        metadata = model_config.get("metadata", {})
        
        # 组合描述、能力和专业任务
        parts = []
        
        # 添加描述
        description = metadata.get("description", "")
        if description:
            parts.append(description)
        
        # 添加能力
        capabilities = model_config.get("capabilities", [])
        if capabilities:
            parts.append(f"Capabilities: {', '.join(capabilities)}")
        
        # 添加专业任务
        specialized_tasks = metadata.get("specialized_tasks", [])
        if specialized_tasks:
            parts.append(f"Tasks: {', '.join(specialized_tasks)}")
        
        # 添加性能层级
        performance_tier = metadata.get("performance_tier", "")
        if performance_tier:
            parts.append(f"Performance: {performance_tier}")
        
        return " ".join(parts)
    
    async def create_embedding(self, search_text: str) -> Optional[List[float]]:
        """创建文本的向量嵌入"""
        if not self.embedding_service:
            logger.warning("Embedding service not available")
            return None
        
        try:
            embedding = await self.embedding_service.create_text_embedding(search_text)
            return embedding
        except Exception as e:
            logger.error(f"Failed to create embedding: {e}")
            return None
    
    async def register_model(self, model_config: Dict[str, Any], provider: str, update: bool = False, embeddings_only: bool = False) -> bool:
        """注册单个模型到 Supabase"""
        try:
            model_id = model_config["model_id"]
            model_type = model_config["model_type"]
            capabilities = model_config["capabilities"]
            metadata = model_config["metadata"].copy()
            metadata["provider"] = provider
            
            # 检查模型是否已存在
            existing_model = self.registry.get_model_info(model_id)
            
            if existing_model and not update and not embeddings_only:
                logger.warning(f"Model {model_id} already exists. Use --update to overwrite.")
                return False
            
            success = True
            
            # 注册模型到基础表（除非只生成嵌入）
            if not embeddings_only:
                if existing_model and update:
                    logger.info(f"Updating existing model {model_id}")
                else:
                    logger.info(f"Registering new model {model_id}")
                
                reg_success = self.registry.register_model(
                    model_id=model_id,
                    model_type=model_type,
                    capabilities=capabilities,
                    metadata=metadata
                )
                
                if not reg_success:
                    logger.error(f"❌ Failed to register model {model_id} to basic tables")
                    success = False
            
            # 生成并存储嵌入
            if self.embedding_service:
                try:
                    search_text = self.create_search_text(model_config)
                    embedding = await self.create_embedding(search_text)
                    
                    if embedding:
                        # 存储到 model_embedding 表
                        embed_success = await self._store_model_embedding(
                            model_id, provider, model_type, 
                            metadata.get("description", ""),
                            search_text, metadata, embedding
                        )
                        
                        if embed_success:
                            logger.info(f"✅ Created embedding for {model_id}")
                        else:
                            logger.warning(f"⚠️ Failed to store embedding for {model_id}")
                    else:
                        logger.warning(f"⚠️ Failed to create embedding for {model_id}")
                        
                except Exception as e:
                    logger.error(f"❌ Error creating embedding for {model_id}: {e}")
            
            if success:
                action = "embedding generated" if embeddings_only else "registered"
                logger.info(f"✅ Successfully {action} for {model_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Error processing model {model_config.get('model_id', 'unknown')}: {e}")
            return False
    
    async def _store_model_embedding(
        self, 
        model_id: str, 
        provider: str, 
        model_type: str,
        description: str,
        search_text: str, 
        metadata: Dict[str, Any], 
        embedding: List[float]
    ) -> bool:
        """存储模型嵌入到数据库"""
        try:
            # 这里需要直接访问 Supabase 客户端
            supabase = self.registry.supabase
            
            embedding_data = {
                'model_id': model_id,
                'provider': provider,
                'model_type': model_type,
                'description': description,
                'search_text': search_text,
                'metadata': json.dumps(metadata),
                'embedding': embedding
            }
            
            # 插入或更新
            result = supabase.table('model_embedding').upsert(
                embedding_data, 
                on_conflict='model_id'
            ).execute()
            
            return bool(result.data)
            
        except Exception as e:
            logger.error(f"Failed to store embedding for {model_id}: {e}")
            return False
    
    async def register_provider_models(self, provider: str, dry_run: bool = False, update: bool = False, embeddings_only: bool = False) -> bool:
        """注册 provider 的所有模型"""
        try:
            # 加载配置
            config = self.load_provider_config(provider)
            
            # 验证配置
            if not self.validate_provider_config(config, provider):
                logger.error(f"❌ Invalid configuration for provider {provider}")
                return False
            
            if dry_run:
                logger.info(f"✅ Dry run successful for provider {provider} - configuration is valid")
                return True
            
            # 初始化嵌入服务
            if not embeddings_only:  # 注册模式需要检查嵌入服务
                await self.initialize_embedding_service()
            else:  # 只生成嵌入模式，必须有嵌入服务
                await self.initialize_embedding_service()
                if not self.embedding_service:
                    logger.error("❌ Embedding service required for embeddings-only mode")
                    return False
            
            # 注册所有模型
            models = config["models"]
            success_count = 0
            
            action = "generating embeddings for" if embeddings_only else "registering"
            logger.info(f"🚀 Starting {action} {len(models)} models for provider {provider}")
            
            for model_config in models:
                if await self.register_model(model_config, provider, update, embeddings_only):
                    success_count += 1
            
            # 汇总结果
            if success_count == len(models):
                logger.info(f"🎉 All {len(models)} models processed successfully for provider {provider}")
            else:
                logger.warning(f"⚠️ Only {success_count}/{len(models)} models processed successfully for provider {provider}")
            
            return success_count == len(models)
            
        except Exception as e:
            logger.error(f"❌ Failed to process models for provider {provider}: {e}")
            return False
    
    async def register_all_providers(self, dry_run: bool = False, update: bool = False, embeddings_only: bool = False) -> bool:
        """注册所有 providers 的模型"""
        providers = ["openai", "replicate", "yyds", "ollama"]
        
        action = "embedding generation" if embeddings_only else "registration"
        logger.info(f"🚀 Starting {action} for all providers: {', '.join(providers)}")
        
        overall_success = True
        results = {}
        
        for provider in providers:
            logger.info(f"\n📁 Processing provider: {provider}")
            try:
                success = await self.register_provider_models(provider, dry_run, update, embeddings_only)
                results[provider] = success
                if not success:
                    overall_success = False
            except FileNotFoundError:
                logger.warning(f"⚠️ Configuration file not found for provider {provider}, skipping")
                results[provider] = None
            except Exception as e:
                logger.error(f"❌ Unexpected error with provider {provider}: {e}")
                results[provider] = False
                overall_success = False
        
        # 打印汇总报告
        logger.info("\n" + "="*60)
        logger.info("📊 PROCESSING SUMMARY")
        logger.info("="*60)
        
        for provider, success in results.items():
            if success is True:
                logger.info(f"✅ {provider}: SUCCESS")
            elif success is False:
                logger.error(f"❌ {provider}: FAILED")
            else:
                logger.warning(f"⚠️ {provider}: SKIPPED (no config)")
        
        if overall_success:
            action = "embedding generation" if embeddings_only else "model registration"
            logger.info(f"\n🎉 All {action} completed successfully!")
        else:
            logger.error("\n❌ Some operations failed. Check logs for details.")
        
        return overall_success
    
    def list_available_providers(self) -> List[str]:
        """列出可用的 provider 配置文件"""
        providers = []
        for config_file in self.config_dir.glob("*_models.yaml"):
            provider = config_file.stem.replace("_models", "")
            providers.append(provider)
        return sorted(providers)


async def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="Register models from YAML configuration files to Supabase with vector embeddings",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python register_models_with_embeddings.py --all                    # Register all providers
  python register_models_with_embeddings.py --provider openai        # Register only OpenAI models
  python register_models_with_embeddings.py --dry-run --all         # Validate all configs
  python register_models_with_embeddings.py --update --provider openai  # Update existing models
  python register_models_with_embeddings.py --embeddings-only --all  # Only generate embeddings
        """
    )
    
    parser.add_argument("--all", action="store_true", 
                       help="Process models from all provider config files")
    parser.add_argument("--provider", type=str,
                       help="Process models from specific provider (e.g., openai, replicate)")
    parser.add_argument("--dry-run", action="store_true",
                       help="Validate configuration without actually processing models")
    parser.add_argument("--update", action="store_true",
                       help="Update existing models if they already exist")
    parser.add_argument("--embeddings-only", action="store_true",
                       help="Only generate and store embeddings, don't register models")
    parser.add_argument("--list-providers", action="store_true",
                       help="List available provider configuration files")
    
    args = parser.parse_args()
    
    # 检查依赖
    if not SUPABASE_AVAILABLE:
        logger.error("❌ Required dependencies not available. Please install supabase-py and other dependencies.")
        sys.exit(1)
    
    # 创建注册脚本实例
    try:
        script = EnhancedModelRegistrationScript()
    except Exception as e:
        logger.error(f"❌ Failed to initialize script: {e}")
        sys.exit(1)
    
    # 处理 list-providers
    if args.list_providers:
        providers = script.list_available_providers()
        logger.info("Available provider configurations:")
        for provider in providers:
            logger.info(f"  - {provider}")
        return
    
    # 验证参数
    if not args.all and not args.provider:
        parser.error("Must specify either --all or --provider")
    
    if args.all and args.provider:
        parser.error("Cannot specify both --all and --provider")
    
    # 执行处理
    try:
        if args.dry_run:
            logger.info("🔍 Running in DRY-RUN mode - no actual processing will occur")
        
        if args.embeddings_only:
            logger.info("🎯 Running in EMBEDDINGS-ONLY mode - only generating vector embeddings")
        
        if args.all:
            success = await script.register_all_providers(args.dry_run, args.update, args.embeddings_only)
        else:
            success = await script.register_provider_models(args.provider, args.dry_run, args.update, args.embeddings_only)
        
        if success:
            logger.info("✅ Script completed successfully")
            sys.exit(0)
        else:
            logger.error("❌ Script completed with errors")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("\n⏹️ Processing cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())