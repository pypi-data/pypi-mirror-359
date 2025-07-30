#!/usr/bin/env python3
"""
模型注册脚本

从YAML配置文件中读取模型定义，并注册到ModelRegistry中。
支持批量注册、更新和验证。

Usage:
    python register_models.py --all                    # 注册所有providers的模型
    python register_models.py --provider openai        # 只注册openai的模型
    python register_models.py --dry-run               # 仅验证配置，不实际注册
    python register_models.py --update                # 更新已存在的模型
"""

import argparse
import asyncio
import logging
import sys
from pathlib import Path
from typing import Dict, List, Any
import yaml

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from isa_model.core.models.model_manager import ModelManager
from isa_model.core.models.model_repo import ModelType, ModelCapability

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ModelRegistrationScript:
    """模型注册脚本类"""
    
    def __init__(self):
        self.model_manager = ModelManager()
        self.config_dir = project_root / "isa_model" / "config" / "models"
        
        # 能力映射
        self.capability_mapping = {
            "text_generation": ModelCapability.TEXT_GENERATION,
            "chat": ModelCapability.CHAT,
            "embedding": ModelCapability.EMBEDDING,
            "reranking": ModelCapability.RERANKING,
            "reasoning": ModelCapability.REASONING,
            "image_generation": ModelCapability.IMAGE_GENERATION,
            "image_analysis": ModelCapability.IMAGE_ANALYSIS,
            "audio_transcription": ModelCapability.AUDIO_TRANSCRIPTION,
            "image_understanding": ModelCapability.IMAGE_UNDERSTANDING,
            "ui_detection": ModelCapability.UI_DETECTION,
            "ocr": ModelCapability.OCR,
            "table_detection": ModelCapability.TABLE_DETECTION,
            "table_structure_recognition": ModelCapability.TABLE_STRUCTURE_RECOGNITION,
        }
        
        # 模型类型映射
        self.type_mapping = {
            "llm": ModelType.LLM,
            "embedding": ModelType.EMBEDDING,
            "rerank": ModelType.RERANK,
            "image": ModelType.IMAGE,
            "audio": ModelType.AUDIO,
            "video": ModelType.VIDEO,
            "vision": ModelType.VISION,
        }
    
    def load_provider_config(self, provider: str) -> Dict[str, Any]:
        """加载provider的YAML配置"""
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
        
        # 验证model_type
        model_type = model_config["model_type"]
        if model_type not in self.type_mapping:
            logger.error(f"Invalid model_type '{model_type}' for model {model_config['model_id']}")
            return False
        
        # 验证capabilities
        capabilities = model_config["capabilities"]
        if not isinstance(capabilities, list) or not capabilities:
            logger.error(f"Capabilities must be a non-empty list for model {model_config['model_id']}")
            return False
        
        for cap in capabilities:
            if cap not in self.capability_mapping:
                logger.error(f"Invalid capability '{cap}' for model {model_config['model_id']}")
                return False
        
        # 验证metadata
        metadata = model_config["metadata"]
        required_metadata = ["description", "performance_tier", "provider_model_name"]
        
        for field in required_metadata:
            if field not in metadata:
                logger.error(f"Missing required metadata field '{field}' for model {model_config['model_id']}")
                return False
        
        return True
    
    def validate_provider_config(self, config: Dict[str, Any], provider: str) -> bool:
        """验证provider的完整配置"""
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
    
    async def register_model(self, model_config: Dict[str, Any], provider: str, update: bool = False) -> bool:
        """注册单个模型"""
        try:
            model_id = model_config["model_id"]
            model_type = self.type_mapping[model_config["model_type"]]
            
            # 转换capabilities
            capabilities = [
                self.capability_mapping[cap] for cap in model_config["capabilities"]
            ]
            
            # 准备metadata
            metadata = model_config["metadata"].copy()
            metadata["provider"] = provider
            
            # 检查模型是否已存在
            existing_model = await self.model_manager.get_model_info(model_id)
            
            if existing_model and not update:
                logger.warning(f"Model {model_id} already exists. Use --update to overwrite.")
                return False
            
            if existing_model and update:
                logger.info(f"Updating existing model {model_id}")
            else:
                logger.info(f"Registering new model {model_id}")
            
            # 注册模型
            success = await self.model_manager.register_model_for_lifecycle(
                model_id=model_id,
                model_type=model_type,
                capabilities=capabilities,
                provider=provider,
                provider_model_name=metadata["provider_model_name"],
                metadata=metadata
            )
            
            if success:
                logger.info(f"✅ Successfully registered {model_id}")
            else:
                logger.error(f"❌ Failed to register {model_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Error registering model {model_config.get('model_id', 'unknown')}: {e}")
            return False
    
    async def register_provider_models(self, provider: str, dry_run: bool = False, update: bool = False) -> bool:
        """注册provider的所有模型"""
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
            
            # 注册所有模型
            models = config["models"]
            success_count = 0
            
            logger.info(f"🚀 Starting registration of {len(models)} models for provider {provider}")
            
            for model_config in models:
                if await self.register_model(model_config, provider, update):
                    success_count += 1
            
            # 汇总结果
            if success_count == len(models):
                logger.info(f"🎉 All {len(models)} models registered successfully for provider {provider}")
            else:
                logger.warning(f"⚠️ Only {success_count}/{len(models)} models registered successfully for provider {provider}")
            
            return success_count == len(models)
            
        except Exception as e:
            logger.error(f"❌ Failed to register models for provider {provider}: {e}")
            return False
    
    async def register_all_providers(self, dry_run: bool = False, update: bool = False) -> bool:
        """注册所有providers的模型"""
        providers = ["openai", "replicate", "yyds", "ollama"]
        
        logger.info(f"🚀 Starting registration for all providers: {', '.join(providers)}")
        
        overall_success = True
        results = {}
        
        for provider in providers:
            logger.info(f"\n📁 Processing provider: {provider}")
            try:
                success = await self.register_provider_models(provider, dry_run, update)
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
        logger.info("📊 REGISTRATION SUMMARY")
        logger.info("="*60)
        
        for provider, success in results.items():
            if success is True:
                logger.info(f"✅ {provider}: SUCCESS")
            elif success is False:
                logger.error(f"❌ {provider}: FAILED")
            else:
                logger.warning(f"⚠️ {provider}: SKIPPED (no config)")
        
        if overall_success:
            logger.info("\n🎉 All model registration completed successfully!")
        else:
            logger.error("\n❌ Some models failed to register. Check logs for details.")
        
        return overall_success
    
    def list_available_providers(self) -> List[str]:
        """列出可用的provider配置文件"""
        providers = []
        for config_file in self.config_dir.glob("*_models.yaml"):
            provider = config_file.stem.replace("_models", "")
            providers.append(provider)
        return sorted(providers)


async def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="Register models from YAML configuration files to ModelRegistry",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python register_models.py --all                    # Register all providers
  python register_models.py --provider openai        # Register only OpenAI models
  python register_models.py --dry-run --all         # Validate all configs without registering
  python register_models.py --update --provider openai  # Update existing OpenAI models
        """
    )
    
    parser.add_argument("--all", action="store_true", 
                       help="Register models from all provider config files")
    parser.add_argument("--provider", type=str,
                       help="Register models from specific provider (e.g., openai, replicate)")
    parser.add_argument("--dry-run", action="store_true",
                       help="Validate configuration without actually registering models")
    parser.add_argument("--update", action="store_true",
                       help="Update existing models if they already exist")
    parser.add_argument("--list-providers", action="store_true",
                       help="List available provider configuration files")
    
    args = parser.parse_args()
    
    # 创建注册脚本实例
    script = ModelRegistrationScript()
    
    # 处理list-providers
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
    
    # 执行注册
    try:
        if args.dry_run:
            logger.info("🔍 Running in DRY-RUN mode - no models will actually be registered")
        
        if args.all:
            success = await script.register_all_providers(args.dry_run, args.update)
        else:
            success = await script.register_provider_models(args.provider, args.dry_run, args.update)
        
        if success:
            logger.info("✅ Script completed successfully")
            sys.exit(0)
        else:
            logger.error("❌ Script completed with errors")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("\n⏹️ Registration cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())