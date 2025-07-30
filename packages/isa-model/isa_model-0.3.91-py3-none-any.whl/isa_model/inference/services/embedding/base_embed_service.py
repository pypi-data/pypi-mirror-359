from abc import ABC, abstractmethod
from typing import Dict, Any, List, Union, Optional
from isa_model.inference.services.base_service import BaseService

class BaseEmbedService(BaseService):
    """Base class for embedding services with unified task dispatch"""
    
    async def invoke(
        self, 
        input_data: Union[str, List[str]],
        task: Optional[str] = None,
        **kwargs
    ) -> Union[List[float], List[List[float]], List[Dict[str, Any]], Dict[str, Any]]:
        """
        统一的任务分发方法 - Base类提供通用实现
        
        Args:
            input_data: 输入数据，可以是:
                - str: 单个文本
                - List[str]: 多个文本（批量处理）
            task: 任务类型，支持多种embedding任务
            **kwargs: 任务特定的附加参数
            
        Returns:
            Various types depending on task
        """
        task = task or "embed"
        
        # ==================== 嵌入生成类任务 ====================
        if task == "embed":
            if isinstance(input_data, list):
                return await self.create_text_embeddings(input_data)
            else:
                return await self.create_text_embedding(input_data)
        elif task == "embed_batch":
            if not isinstance(input_data, list):
                input_data = [input_data]
            return await self.create_text_embeddings(input_data)
        elif task == "chunk_and_embed":
            if isinstance(input_data, list):
                raise ValueError("chunk_and_embed task requires single text input")
            return await self.create_chunks(input_data, kwargs.get("metadata"))
        elif task == "similarity":
            embedding1 = kwargs.get("embedding1")
            embedding2 = kwargs.get("embedding2")
            if not embedding1 or not embedding2:
                raise ValueError("similarity task requires embedding1 and embedding2 parameters")
            similarity = await self.compute_similarity(embedding1, embedding2)
            return {"similarity": similarity}
        elif task == "find_similar":
            query_embedding = kwargs.get("query_embedding")
            candidate_embeddings = kwargs.get("candidate_embeddings")
            if not query_embedding or not candidate_embeddings:
                raise ValueError("find_similar task requires query_embedding and candidate_embeddings parameters")
            return await self.find_similar_texts(
                query_embedding, 
                candidate_embeddings, 
                kwargs.get("top_k", 5)
            )
        else:
            raise NotImplementedError(f"{self.__class__.__name__} does not support task: {task}")
    
    def get_supported_tasks(self) -> List[str]:
        """
        获取支持的任务列表
        
        Returns:
            List of supported task names
        """
        return ["embed", "embed_batch", "chunk_and_embed", "similarity", "find_similar"]
    
    @abstractmethod
    async def create_text_embedding(self, text: str) -> List[float]:
        """
        Create embedding for single text
        
        Args:
            text: Input text to embed
            
        Returns:
            List of float values representing the embedding vector
        """
        pass
    
    @abstractmethod
    async def create_text_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Create embeddings for multiple texts
        
        Args:
            texts: List of input texts to embed
            
        Returns:
            List of embedding vectors, one for each input text
        """
        pass
    
    @abstractmethod
    async def create_chunks(self, text: str, metadata: Optional[Dict] = None) -> List[Dict]:
        """
        Create text chunks with embeddings
        
        Args:
            text: Input text to chunk and embed
            metadata: Optional metadata to attach to chunks
            
        Returns:
            List of dictionaries containing:
            - text: The chunk text
            - embedding: The embedding vector
            - metadata: Associated metadata
            - start_index: Start position in original text
            - end_index: End position in original text
        """
        pass
    
    @abstractmethod
    async def compute_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """
        Compute similarity between two embeddings
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            
        Returns:
            Similarity score (typically cosine similarity, range -1 to 1)
        """
        pass
    
    @abstractmethod
    async def find_similar_texts(
        self, 
        query_embedding: List[float], 
        candidate_embeddings: List[List[float]], 
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Find most similar texts based on embeddings
        
        Args:
            query_embedding: Query embedding vector
            candidate_embeddings: List of candidate embedding vectors
            top_k: Number of top similar results to return
            
        Returns:
            List of dictionaries containing:
            - index: Index in candidate_embeddings
            - similarity: Similarity score
        """
        pass
    
    @abstractmethod
    def get_embedding_dimension(self) -> int:
        """
        Get the dimension of embeddings produced by this service
        
        Returns:
            Integer dimension of embedding vectors
        """
        pass
    
    @abstractmethod
    def get_max_input_length(self) -> int:
        """
        Get maximum input text length supported
        
        Returns:
            Maximum number of characters/tokens supported
        """
        pass
    
    @abstractmethod
    async def close(self):
        """Cleanup resources"""
        pass
