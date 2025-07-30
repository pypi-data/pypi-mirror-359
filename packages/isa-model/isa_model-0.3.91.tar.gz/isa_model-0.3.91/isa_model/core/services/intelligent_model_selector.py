#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Intelligent Model Selector - Simple similarity-based model selection
Uses embedding similarity matching against model descriptions and metadata
"""

import logging
import asyncio
import json
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import yaml

logger = logging.getLogger(__name__)

try:
    import asyncpg
    from pgvector.asyncpg import register_vector
    PGVECTOR_AVAILABLE = True
except ImportError:
    PGVECTOR_AVAILABLE = False
    logger.warning("pgvector not available, model selector will use in-memory fallback")

try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    logger.warning("Supabase not available, falling back to SQLite")


class IntelligentModelSelector:
    """
    Simple intelligent model selector using embedding similarity
    
    Features:
    - Embeds model descriptions and metadata
    - Stores embeddings in pgvector for fast similarity search
    - Falls back to in-memory similarity if pgvector unavailable
    - Has default models for each service type
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.db_pool = None
        self.supabase_client = None
        self.embedding_service = None
        self.model_embeddings: Dict[str, List[float]] = {}
        self.models_metadata: Dict[str, Dict[str, Any]] = {}
        
        # Default models for each service type
        self.default_models = {
            "vision": {"model_id": "gpt-4.1-mini", "provider": "openai"},
            "audio": {"model_id": "whisper-1", "provider": "openai"},
            "text": {"model_id": "gpt-4.1-mini", "provider": "openai"},
            "image": {"model_id": "flux-schnell", "provider": "replicate"},
            "embedding": {"model_id": "text-embedding-3-small", "provider": "openai"},
            "omni": {"model_id": "gpt-4.1", "provider": "openai"}
        }
        
        logger.info("Intelligent Model Selector initialized")
    
    async def initialize(self):
        """Initialize the model selector"""
        try:
            # Initialize embedding service
            await self._init_embedding_service()
            
            # Initialize database - try Supabase first, then PostgreSQL
            if SUPABASE_AVAILABLE and self.config.get("supabase"):
                await self._init_supabase()
            elif PGVECTOR_AVAILABLE:
                await self._init_database()
            
            # Load and embed models
            await self._load_models()
            
            logger.info("Model selector fully initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize model selector: {e}")
            # Continue with fallback mode
    
    async def _init_embedding_service(self):
        """Initialize embedding service for text similarity"""
        try:
            from isa_model.inference.ai_factory import AIFactory
            factory = AIFactory.get_instance()
            self.embedding_service = factory.get_embed("text-embedding-3-small", "openai")
            logger.info("Embedding service initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize embedding service: {e}")
    
    async def _init_supabase(self):
        """Initialize Supabase client for vector search"""
        try:
            supabase_config = self.config.get("supabase", {})
            url = supabase_config.get("url")
            key = supabase_config.get("key")
            
            if not url or not key:
                # Try environment variables
                import os
                url = url or os.getenv("SUPABASE_URL")
                key = key or os.getenv("SUPABASE_ANON_KEY")
            
            if not url or not key:
                raise ValueError("Supabase URL and key are required")
            
            self.supabase_client = create_client(url, key)
            logger.info("Supabase client initialized successfully")
            
        except Exception as e:
            logger.warning(f"Supabase initialization failed: {e}, using in-memory fallback")
            self.supabase_client = None
    
    async def _init_database(self):
        """Initialize pgvector database connection"""
        try:
            # Get database configuration
            db_config = self.config.get("database", {
                "host": "localhost",
                "port": 5432,
                "database": "isa_model", 
                "user": "postgres",
                "password": "password"
            })
            
            # Create connection pool
            self.db_pool = await asyncpg.create_pool(
                host=db_config["host"],
                port=db_config["port"], 
                database=db_config["database"],
                user=db_config["user"],
                password=db_config["password"],
                min_size=1,
                max_size=5
            )
            
            # Register vector extension
            async with self.db_pool.acquire() as conn:
                await register_vector(conn)
                
                # Create models table if not exists
                await conn.execute("""
                    CREATE EXTENSION IF NOT EXISTS vector;
                    
                    CREATE TABLE IF NOT EXISTS model_embeddings (
                        id SERIAL PRIMARY KEY,
                        model_id VARCHAR(255) UNIQUE NOT NULL,
                        provider VARCHAR(100) NOT NULL,
                        model_type VARCHAR(50) NOT NULL,
                        description TEXT,
                        metadata JSONB,
                        embedding vector(1536),
                        created_at TIMESTAMP DEFAULT NOW(),
                        updated_at TIMESTAMP DEFAULT NOW()
                    );
                    
                    CREATE INDEX IF NOT EXISTS idx_model_embeddings_similarity 
                    ON model_embeddings USING ivfflat (embedding vector_cosine_ops);
                """)
            
            logger.info("Database initialized successfully")
            
        except Exception as e:
            logger.warning(f"Database initialization failed: {e}, using in-memory fallback")
            self.db_pool = None
    
    async def _load_models(self):
        """Load models from YAML configs and create embeddings"""
        try:
            # Get config directory
            config_dir = Path(__file__).parent.parent.parent / "config" / "models"
            
            if not config_dir.exists():
                logger.warning(f"Model config directory not found: {config_dir}")
                return
            
            # Load all YAML files
            for yaml_file in config_dir.glob("*.yaml"):
                await self._load_models_from_file(yaml_file)
            
            logger.info(f"Loaded {len(self.models_metadata)} models for similarity matching")
            
        except Exception as e:
            logger.error(f"Failed to load models: {e}")
    
    async def _load_models_from_file(self, yaml_file: Path):
        """Load models from a specific YAML file"""
        try:
            with open(yaml_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            provider = data.get("provider", "unknown")
            models = data.get("models", [])
            
            for model in models:
                await self._process_model(model, provider)
                
        except Exception as e:
            logger.error(f"Failed to load models from {yaml_file}: {e}")
    
    async def _process_model(self, model: Dict[str, Any], provider: str):
        """Process a single model and create embeddings"""
        try:
            model_id = model.get("model_id")
            if not model_id:
                return
            
            # Create searchable text from description and metadata
            description = model.get("metadata", {}).get("description", "")
            specialized_tasks = model.get("metadata", {}).get("specialized_tasks", [])
            capabilities = model.get("capabilities", [])
            
            # Combine all text for embedding
            search_text = f"{description} "
            search_text += f"Capabilities: {', '.join(capabilities)} "
            search_text += f"Tasks: {', '.join(specialized_tasks)}"
            
            # Create embedding
            if self.embedding_service:
                try:
                    embedding = await self.embedding_service.create_text_embedding(search_text)
                    
                    # Store model metadata
                    self.models_metadata[model_id] = {
                        "provider": provider,
                        "model_type": model.get("model_type"),
                        "capabilities": capabilities,
                        "metadata": model.get("metadata", {}),
                        "search_text": search_text
                    }
                    
                    # Store embedding
                    if self.db_pool:
                        await self._store_model_embedding(model_id, provider, model, embedding)
                    else:
                        self.model_embeddings[model_id] = embedding
                        
                except Exception as e:
                    logger.warning(f"Failed to create embedding for {model_id}: {e}")
            
        except Exception as e:
            logger.error(f"Failed to process model {model.get('model_id', 'unknown')}: {e}")
    
    async def _store_model_embedding(
        self, 
        model_id: str, 
        provider: str, 
        model: Dict[str, Any], 
        embedding: List[float]
    ):
        """Store model embedding in database"""
        try:
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO model_embeddings 
                    (model_id, provider, model_type, description, metadata, embedding)
                    VALUES ($1, $2, $3, $4, $5, $6)
                    ON CONFLICT (model_id) 
                    DO UPDATE SET 
                        provider = $2,
                        model_type = $3,
                        description = $4,
                        metadata = $5,
                        embedding = $6,
                        updated_at = NOW()
                """, 
                    model_id,
                    provider,
                    model.get("model_type"),
                    model.get("metadata", {}).get("description", ""),
                    json.dumps(model.get("metadata", {})),
                    embedding
                )
                
        except Exception as e:
            logger.error(f"Failed to store embedding for {model_id}: {e}")
    
    async def select_model(
        self,
        request: str,
        service_type: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Select best model using similarity matching
        
        Args:
            request: User's request/query
            service_type: Type of service needed
            context: Additional context
            
        Returns:
            Selection result with model info and reasoning
        """
        try:
            # Get embedding for user request
            if not self.embedding_service:
                return self._get_default_selection(service_type, "No embedding service available")
            
            request_embedding = await self.embedding_service.create_text_embedding(request)
            
            # Find similar models
            if self.supabase_client:
                candidates = await self._find_similar_models_supabase(request_embedding, service_type)
            elif self.db_pool:
                candidates = await self._find_similar_models_db(request_embedding, service_type)
            else:
                candidates = await self._find_similar_models_memory(request_embedding, service_type)
            
            if not candidates:
                return self._get_default_selection(service_type, "No suitable models found")
            
            # Return best match
            best_match = candidates[0]
            
            return {
                "success": True,
                "selected_model": {
                    "model_id": best_match["model_id"],
                    "provider": best_match["provider"]
                },
                "selection_reason": f"Best similarity match (score: {best_match['similarity']:.3f})",
                "alternatives": candidates[1:3],  # Top 2 alternatives
                "similarity_score": best_match["similarity"]
            }
            
        except Exception as e:
            logger.error(f"Model selection failed: {e}")
            return self._get_default_selection(service_type, f"Selection error: {e}")
    
    async def _find_similar_models_supabase(
        self, 
        request_embedding: List[float], 
        service_type: str
    ) -> List[Dict[str, Any]]:
        """Find similar models using Supabase RPC function"""
        try:
            # Use the RPC function we created in SQL
            result = self.supabase_client.rpc(
                'search_similar_models',
                {
                    'query_embedding': request_embedding,
                    'similarity_threshold': 0.3,  # Minimum similarity threshold
                    'match_count': 10,
                    'filter_model_type': service_type
                }
            ).execute()
            
            candidates = []
            for row in result.data:
                candidates.append({
                    "model_id": row["model_id"],
                    "provider": row["provider"],
                    "model_type": row["model_type"],
                    "similarity": float(row["similarity"]),
                    "description": row.get("description", "")
                })
            
            return candidates
            
        except Exception as e:
            logger.error(f"Supabase similarity search failed: {e}")
            return []
    
    async def _find_similar_models_db(
        self, 
        request_embedding: List[float], 
        service_type: str
    ) -> List[Dict[str, Any]]:
        """Find similar models using database"""
        try:
            async with self.db_pool.acquire() as conn:
                # Query for similar models
                rows = await conn.fetch("""
                    SELECT 
                        model_id, 
                        provider, 
                        model_type,
                        description,
                        metadata,
                        1 - (embedding <=> $1) as similarity
                    FROM model_embeddings
                    WHERE model_type = $2 OR model_type = 'omni'
                    ORDER BY embedding <=> $1
                    LIMIT 10
                """, request_embedding, service_type)
                
                candidates = []
                for row in rows:
                    candidates.append({
                        "model_id": row["model_id"],
                        "provider": row["provider"],
                        "model_type": row["model_type"],
                        "similarity": float(row["similarity"]),
                        "description": row["description"]
                    })
                
                return candidates
                
        except Exception as e:
            logger.error(f"Database similarity search failed: {e}")
            return []
    
    async def _find_similar_models_memory(
        self, 
        request_embedding: List[float], 
        service_type: str
    ) -> List[Dict[str, Any]]:
        """Find similar models using in-memory search"""
        try:
            candidates = []
            
            for model_id, embedding in self.model_embeddings.items():
                metadata = self.models_metadata.get(model_id, {})
                model_type = metadata.get("model_type")
                
                # Filter by service type (including omni models)
                if model_type not in [service_type, "omni"]:
                    continue
                
                # Calculate cosine similarity
                similarity = self._cosine_similarity(request_embedding, embedding)
                
                candidates.append({
                    "model_id": model_id,
                    "provider": metadata.get("provider"),
                    "model_type": model_type,
                    "similarity": similarity,
                    "description": metadata.get("metadata", {}).get("description", "")
                })
            
            # Sort by similarity score
            candidates.sort(key=lambda x: x["similarity"], reverse=True)
            return candidates[:10]
            
        except Exception as e:
            logger.error(f"Memory similarity search failed: {e}")
            return []
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        try:
            import math
            
            dot_product = sum(a * b for a, b in zip(vec1, vec2))
            norm1 = math.sqrt(sum(a * a for a in vec1))
            norm2 = math.sqrt(sum(b * b for b in vec2))
            
            if norm1 * norm2 == 0:
                return 0.0
                
            return dot_product / (norm1 * norm2)
            
        except Exception:
            return 0.0
    
    def _get_default_selection(self, service_type: str, reason: str) -> Dict[str, Any]:
        """Get default model selection"""
        default = self.default_models.get(service_type, self.default_models["vision"])
        
        return {
            "success": True,
            "selected_model": default,
            "selection_reason": f"Default selection ({reason})",
            "alternatives": [],
            "similarity_score": 0.0
        }
    
    async def get_available_models(self, service_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get list of available models"""
        try:
            if self.supabase_client:
                # Query Supabase
                query = self.supabase_client.table("model_embedding").select("model_id, provider, model_type, description, metadata")
                
                if service_type:
                    query = query.or_(f"model_type.eq.{service_type},model_type.eq.omni")
                
                result = query.order("model_id").execute()
                return result.data
                
            elif self.db_pool:
                async with self.db_pool.acquire() as conn:
                    if service_type:
                        rows = await conn.fetch("""
                            SELECT model_id, provider, model_type, description, metadata
                            FROM model_embeddings 
                            WHERE model_type = $1 OR model_type = 'omni'
                            ORDER BY model_id
                        """, service_type)
                    else:
                        rows = await conn.fetch("""
                            SELECT model_id, provider, model_type, description, metadata
                            FROM model_embeddings 
                            ORDER BY model_type, model_id
                        """)
                    
                    return [dict(row) for row in rows]
            else:
                # In-memory fallback
                models = []
                for model_id, metadata in self.models_metadata.items():
                    model_type = metadata.get("model_type")
                    if service_type and model_type not in [service_type, "omni"]:
                        continue
                    
                    models.append({
                        "model_id": model_id,
                        "provider": metadata.get("provider"),
                        "model_type": model_type,
                        "description": metadata.get("metadata", {}).get("description", ""),
                        "metadata": metadata.get("metadata", {})
                    })
                
                return models
                
        except Exception as e:
            logger.error(f"Failed to get available models: {e}")
            return []
    
    async def close(self):
        """Clean up resources"""
        if self.db_pool:
            await self.db_pool.close()
            logger.info("Database connection closed")
        if self.supabase_client:
            # Supabase client doesn't need explicit closing
            logger.info("Supabase client cleaned up")


# Singleton instance
_selector_instance = None

async def get_model_selector(config: Optional[Dict[str, Any]] = None) -> IntelligentModelSelector:
    """Get singleton model selector instance"""
    global _selector_instance
    
    if _selector_instance is None:
        _selector_instance = IntelligentModelSelector(config)
        await _selector_instance.initialize()
    
    return _selector_instance