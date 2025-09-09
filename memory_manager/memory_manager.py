"""
Memory Manager Module

Manages vector store integration, persistence, tagging, and provenance metadata.
Uses ChromaDB for vector storage and retrieval.

Chosen libraries:
- ChromaDB: Vector database for embedding storage and retrieval
- SentenceTransformers: Local embedding generation
- OpenAI: Remote embedding generation
- pydantic: Data validation and type safety

Adapted from: exp-pj-m-multi-agent-system (https://github.com/krik8235/exp-pj-m-multi-agent-system)
Pattern: Vector store integration with metadata filtering
"""

import asyncio
import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

import chromadb
import openai
import pydantic
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)


class MemoryEntry(pydantic.BaseModel):
    """Model for memory entries with provenance metadata."""
    source_id: str
    chunk_id: str
    original_filename: str
    ingestion_timestamp: datetime
    agent_id: Optional[str] = None
    provenance_notes: str = ""
    tags: List[str] = []
    retrieval_score: float = 0.0
    content: str
    metadata: Dict[str, str] = {}


class RetrievalResult(pydantic.BaseModel):
    """Model for retrieval results."""
    content: str
    chunk_id: str
    source_id: str
    score: float
    metadata: Dict[str, str] = {}


class MemoryManager:
    """
    Manages persistent memory using ChromaDB for vector storage and retrieval.
    
    Responsibilities:
    - Store and retrieve document embeddings
    - Manage provenance metadata and tagging
    - Handle both local and remote embedding generation
    - Provide context assembly for RAG
    - Maintain retrieval scoring and context management
    """
    
    def __init__(
        self,
        persist_directory: str = "./memory_db",
        embedding_model: str = "all-MiniLM-L6-v2",
        use_remote_embeddings: bool = False,
        openai_api_key: Optional[str] = None
    ):
        """
        Initialize the memory manager.
        
        Args:
            persist_directory: Directory to persist ChromaDB data
            embedding_model: SentenceTransformers model name for local embeddings
            use_remote_embeddings: Whether to use OpenAI embeddings
            openai_api_key: OpenAI API key for remote embeddings
        """
        self.persist_directory = Path(persist_directory)
        self.persist_directory.mkdir(parents=True, exist_ok=True)
        
        # Initialize ChromaDB
        self.client = chromadb.PersistentClient(path=str(self.persist_directory))
        self.collection = self.client.get_or_create_collection(
            name="documents",
            metadata={"hnsw:space": "cosine"}
        )
        
        # Initialize embedding models
        self.use_remote_embeddings = use_remote_embeddings
        if use_remote_embeddings:
            if not openai_api_key:
                raise ValueError("OpenAI API key required for remote embeddings")
            openai.api_key = openai_api_key
            self.embedding_model = None
        else:
            self.embedding_model = SentenceTransformer(embedding_model)
        
        # Provenance log file
        self.provenance_log_path = self.persist_directory / "provenance.log"
        
        logger.info(f"Memory manager initialized with persist directory: {self.persist_directory}")
    
    async def store_document_chunks(
        self,
        metadata: 'DocumentMetadata',
        chunks: List['DocumentChunk'],
        agent_id: Optional[str] = None
    ) -> List[str]:
        """
        Store document chunks in the vector database.
        
        Args:
            metadata: Document metadata
            chunks: List of document chunks
            agent_id: ID of the agent storing the chunks
            
        Returns:
            List of stored chunk IDs
        """
        if not chunks:
            return []
        
        # Prepare data for ChromaDB
        chunk_ids = []
        documents = []
        metadatas = []
        embeddings = []
        
        for chunk in chunks:
            chunk_id = chunk.chunk_id
            chunk_ids.append(chunk_id)
            documents.append(chunk.content)
            
            # Create metadata for ChromaDB
            chunk_metadata = {
                "source_id": chunk.source_id,
                "chunk_id": chunk_id,
                "original_filename": metadata.original_filename,
                "ingestion_timestamp": metadata.ingestion_timestamp.isoformat(),
                "agent_id": agent_id or "",
                "chunk_index": str(chunk.chunk_index),
                "word_count": str(chunk.word_count),
                "char_count": str(chunk.char_count),
                **chunk.metadata
            }
            metadatas.append(chunk_metadata)
            
            # Generate embedding
            embedding = await self._generate_embedding(chunk.content)
            embeddings.append(embedding)
        
        # Store in ChromaDB
        try:
            self.collection.add(
                ids=chunk_ids,
                documents=documents,
                metadatas=metadatas,
                embeddings=embeddings
            )
            
            # Log provenance
            await self._log_provenance(metadata, chunks, agent_id, "store")
            
            logger.info(f"Stored {len(chunks)} chunks from {metadata.original_filename}")
            return chunk_ids
            
        except Exception as e:
            logger.error(f"Failed to store chunks: {e}")
            raise
    
    async def retrieve_relevant_chunks(
        self,
        query: str,
        top_k: int = 5,
        filter_metadata: Optional[Dict[str, str]] = None,
        min_score: float = 0.0
    ) -> List[RetrievalResult]:
        """
        Retrieve relevant chunks based on query similarity.
        
        Args:
            query: Search query
            top_k: Number of top results to return
            filter_metadata: Metadata filters to apply
            min_score: Minimum similarity score threshold
            
        Returns:
            List of retrieval results
        """
        try:
            # Generate query embedding
            query_embedding = await self._generate_embedding(query)
            
            # Query ChromaDB
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                where=filter_metadata,
                include=["documents", "metadatas", "distances"]
            )
            
            # Process results
            retrieval_results = []
            if results["documents"] and results["documents"][0]:
                for i, (doc, metadata, distance) in enumerate(zip(
                    results["documents"][0],
                    results["metadatas"][0],
                    results["distances"][0]
                )):
                    # Convert distance to similarity score (1 - distance for cosine similarity)
                    score = 1 - distance
                    
                    if score >= min_score:
                        result = RetrievalResult(
                            content=doc,
                            chunk_id=metadata.get("chunk_id", ""),
                            source_id=metadata.get("source_id", ""),
                            score=score,
                            metadata=metadata
                        )
                        retrieval_results.append(result)
            
            # Log retrieval
            await self._log_retrieval(query, retrieval_results)
            
            return retrieval_results
            
        except Exception as e:
            logger.error(f"Failed to retrieve chunks: {e}")
            raise
    
    async def get_context_for_generation(
        self,
        query: str,
        max_tokens: int = 4000,
        top_k: int = 10,
        filter_metadata: Optional[Dict[str, str]] = None
    ) -> Tuple[str, List[RetrievalResult]]:
        """
        Get context for RAG generation with token budget management.
        
        Args:
            query: Search query
            max_tokens: Maximum number of tokens for context
            top_k: Maximum number of chunks to retrieve
            filter_metadata: Metadata filters to apply
            
        Returns:
            Tuple of (context_string, retrieval_results)
        """
        # Retrieve relevant chunks
        results = await self.retrieve_relevant_chunks(
            query=query,
            top_k=top_k,
            filter_metadata=filter_metadata
        )
        
        if not results:
            return "", []
        
        # Assemble context within token budget
        context_parts = []
        used_tokens = 0
        selected_results = []
        
        for result in results:
            # Estimate tokens (rough approximation: 1 token ≈ 4 characters)
            chunk_tokens = len(result.content) // 4
            
            if used_tokens + chunk_tokens <= max_tokens:
                context_parts.append(f"[Source: {result.metadata.get('original_filename', 'Unknown')}]\n{result.content}")
                used_tokens += chunk_tokens
                selected_results.append(result)
            else:
                # Try to fit partial content
                remaining_tokens = max_tokens - used_tokens
                if remaining_tokens > 100:  # Only if we have meaningful space left
                    partial_content = result.content[:remaining_tokens * 4]
                    context_parts.append(f"[Source: {result.metadata.get('original_filename', 'Unknown')}]\n{partial_content}...")
                    selected_results.append(result)
                break
        
        context = "\n\n".join(context_parts)
        
        logger.info(f"Assembled context with {used_tokens} tokens from {len(selected_results)} chunks")
        return context, selected_results
    
    async def add_agent_notes(
        self,
        content: str,
        agent_id: str,
        tags: List[str] = None,
        provenance_notes: str = ""
    ) -> str:
        """
        Add agent-generated notes to memory.
        
        Args:
            content: Note content
            agent_id: ID of the agent creating the note
            tags: Tags for the note
            provenance_notes: Additional provenance information
            
        Returns:
            ID of the stored note
        """
        # Generate unique ID for the note
        note_id = f"agent_note_{agent_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Create memory entry
        memory_entry = MemoryEntry(
            source_id="agent_notes",
            chunk_id=note_id,
            original_filename=f"agent_notes_{agent_id}",
            ingestion_timestamp=datetime.now(),
            agent_id=agent_id,
            provenance_notes=provenance_notes,
            tags=tags or [],
            content=content,
            metadata={"type": "agent_note", "agent_id": agent_id}
        )
        
        # Store in ChromaDB
        try:
            embedding = await self._generate_embedding(content)
            
            self.collection.add(
                ids=[note_id],
                documents=[content],
                metadatas=[memory_entry.dict()],
                embeddings=[embedding]
            )
            
            # Log provenance
            await self._log_provenance(None, [memory_entry], agent_id, "agent_note")
            
            logger.info(f"Added agent note from {agent_id}")
            return note_id
            
        except Exception as e:
            logger.error(f"Failed to add agent note: {e}")
            raise
    
    async def search_by_tags(self, tags: List[str], top_k: int = 10) -> List[RetrievalResult]:
        """
        Search for content by tags.
        
        Args:
            tags: List of tags to search for
            top_k: Number of results to return
            
        Returns:
            List of retrieval results
        """
        # ChromaDB doesn't support direct tag search, so we'll use metadata filtering
        # This is a simplified implementation - in practice, you might want to use
        # a more sophisticated tagging system
        results = []
        
        for tag in tags:
            filter_metadata = {"tags": {"$contains": tag}}
            tag_results = await self.retrieve_relevant_chunks(
                query=tag,
                top_k=top_k,
                filter_metadata=filter_metadata
            )
            results.extend(tag_results)
        
        # Remove duplicates and sort by score
        seen_chunks = set()
        unique_results = []
        for result in results:
            if result.chunk_id not in seen_chunks:
                unique_results.append(result)
                seen_chunks.add(result.chunk_id)
        
        return sorted(unique_results, key=lambda x: x.score, reverse=True)[:top_k]
    
    async def _generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text."""
        if self.use_remote_embeddings:
            return await self._generate_openai_embedding(text)
        else:
            return await self._generate_local_embedding(text)
    
    async def _generate_local_embedding(self, text: str) -> List[float]:
        """Generate embedding using SentenceTransformers."""
        try:
            # Run in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            embedding = await loop.run_in_executor(
                None, self.embedding_model.encode, text
            )
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Failed to generate local embedding: {e}")
            raise
    
    async def _generate_openai_embedding(self, text: str) -> List[float]:
        """Generate embedding using OpenAI API."""
        try:
            response = await openai.Embedding.acreate(
                model="text-embedding-ada-002",
                input=text
            )
            return response["data"][0]["embedding"]
        except Exception as e:
            logger.error(f"Failed to generate OpenAI embedding: {e}")
            raise
    
    async def _log_provenance(
        self,
        metadata: Optional['DocumentMetadata'],
        chunks: List[Union['DocumentChunk', MemoryEntry]],
        agent_id: Optional[str],
        action: str
    ):
        """Log provenance information."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "agent_id": agent_id,
            "source_id": metadata.source_id if metadata else "agent_notes",
            "chunk_count": len(chunks),
            "chunk_ids": [chunk.chunk_id for chunk in chunks]
        }
        
        with open(self.provenance_log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry) + "\n")
    
    async def _log_retrieval(self, query: str, results: List[RetrievalResult]):
        """Log retrieval operations."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "action": "retrieval",
            "query": query,
            "result_count": len(results),
            "chunk_ids": [result.chunk_id for result in results],
            "scores": [result.score for result in results]
        }
        
        with open(self.provenance_log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry) + "\n")
    
    def get_stats(self) -> Dict[str, int]:
        """Get statistics about stored content."""
        try:
            count = self.collection.count()
            return {
                "total_chunks": count,
                "collection_name": self.collection.name
            }
        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            return {"total_chunks": 0, "collection_name": "unknown"}
    
    async def clear_memory(self):
        """Clear all stored memory (use with caution)."""
        try:
            self.client.delete_collection("documents")
            self.collection = self.client.create_collection(
                name="documents",
                metadata={"hnsw:space": "cosine"}
            )
            logger.info("Memory cleared")
        except Exception as e:
            logger.error(f"Failed to clear memory: {e}")
            raise