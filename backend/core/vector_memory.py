"""
Advanced memory system with vector embeddings for semantic search
"""

import numpy as np
from typing import List, Dict, Any, Optional
import json
import pickle
from pathlib import Path
from datetime import datetime
from datetime import timedelta
import faiss
from sentence_transformers import SentenceTransformer
import asyncio
from collections import deque

class VectorMemory:
    """Advanced memory system using vector embeddings for semantic search"""
    
    def __init__(self, 
                 model_name: str = "all-MiniLM-L6-v2",
                 index_path: str = "data/memory/vector_index.faiss",
                 metadata_path: str = "data/memory/vector_metadata.pkl"):
        
        self.model = SentenceTransformer(model_name)
        self.embedding_dim = self.model.get_sentence_embedding_dimension()
        self.index_path = Path(index_path)
        self.metadata_path = Path(metadata_path)
        
        # Initialize or load index
        self.index = self._load_or_create_index()
        self.metadata = self._load_metadata()
        
        # Short-term memory buffer
        self.short_term_memory = deque(maxlen=50)
        
        # Long-term memory categories
        self.memory_categories = {
            'conversations': [],
            'tasks': [],
            'knowledge': [],
            'preferences': [],
            'relationships': []
        }
    
    def _load_or_create_index(self) -> faiss.IndexFlatIP:
        """Load existing index or create new one"""
        if self.index_path.exists():
            return faiss.read_index(str(self.index_path))
        else:
            # Create index with inner product (cosine similarity after normalization)
            index = faiss.IndexFlatIP(self.embedding_dim)
            return index
    
    def _load_metadata(self) -> List[Dict]:
        """Load metadata for stored vectors"""
        if self.metadata_path.exists():
            with open(self.metadata_path, 'rb') as f:
                return pickle.load(f)
        return []
    
    def _save_index(self):
        """Save index to disk"""
        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        faiss.write_index(self.index, str(self.index_path))
    
    def _save_metadata(self):
        """Save metadata to disk"""
        self.metadata_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.metadata_path, 'wb') as f:
            pickle.dump(self.metadata, f)
    
    async def encode_text(self, text: str) -> np.ndarray:
        """Encode text to vector embedding"""
        embedding = self.model.encode(text, normalize_embeddings=True)
        return embedding.astype('float32')
    
    async def add_memory(self, 
                        content: str, 
                        category: str = 'conversations',
                        metadata: Dict[str, Any] = None) -> int:
        """Add memory to vector store"""
        # Create embedding
        embedding = await self.encode_text(content)
        
        # Prepare metadata
        memory_metadata = {
            'content': content,
            'category': category,
            'timestamp': datetime.now().isoformat(),
            'metadata': metadata or {}
        }
        
        # Add to short-term memory
        self.short_term_memory.append(memory_metadata)
        
        # Add to index
        self.index.add(embedding.reshape(1, -1))
        self.metadata.append(memory_metadata)
        
        # Save periodically (every 10 memories)
        if len(self.metadata) % 10 == 0:
            self._save_index()
            self._save_metadata()
        
        return self.index.ntotal - 1
    
    async def search_memories(self, 
                             query: str, 
                             k: int = 5,
                             category: str = None,
                             threshold: float = 0.5) -> List[Dict]:
        """Search memories using semantic similarity"""
        # Encode query
        query_embedding = await self.encode_text(query)
        
        # Search in index
        scores, indices = self.index.search(query_embedding.reshape(1, -1), min(k * 2, self.index.ntotal))
        
        # Filter results
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if score >= threshold and idx < len(self.metadata):
                memory = self.metadata[idx]
                
                # Filter by category if specified
                if category and memory['category'] != category:
                    continue
                
                results.append({
                    'content': memory['content'],
                    'category': memory['category'],
                    'timestamp': memory['timestamp'],
                    'score': float(score),
                    'metadata': memory.get('metadata', {})
                })
                
                if len(results) >= k:
                    break
        
        return results
    
    async def get_context(self, query: str, max_tokens: int = 1000) -> str:
        """Get relevant context for a query"""
        memories = await self.search_memories(query, k=10)
        
        context_parts = []
        token_count = 0
        
        for memory in memories:
            content = memory['content']
            # Rough token estimation (1 token ≈ 4 characters)
            estimated_tokens = len(content) // 4
            
            if token_count + estimated_tokens <= max_tokens:
                context_parts.append(f"[{memory['category']}] {content}")
                token_count += estimated_tokens
            else:
                break
        
        return "\n---\n".join(context_parts)
    
    async def consolidate_memories(self):
        """Consolidate short-term memories into long-term storage"""
        if not self.short_term_memory:
            return
        
        # Group similar memories
        memories_text = [m['content'] for m in self.short_term_memory]
        embeddings = self.model.encode(memories_text, normalize_embeddings=True)
        
        # Cluster similar memories (simple approach)
        consolidated = []
        used_indices = set()
        
        for i, embedding in enumerate(embeddings):
            if i in used_indices:
                continue
            
            # Find similar memories
            similarities = np.dot(embeddings, embedding)
            similar_indices = np.where(similarities > 0.8)[0]
            
            # Consolidate similar memories
            similar_memories = [self.short_term_memory[idx] for idx in similar_indices]
            
            if len(similar_memories) > 1:
                # Create consolidated memory
                consolidated_content = self._summarize_memories(similar_memories)
                consolidated.append({
                    'content': consolidated_content,
                    'category': similar_memories[0]['category'],
                    'timestamp': datetime.now().isoformat(),
                    'metadata': {'consolidated': True, 'source_count': len(similar_memories)}
                })
                
                used_indices.update(similar_indices)
        
        # Add consolidated memories to long-term storage
        for memory in consolidated:
            await self.add_memory(
                memory['content'],
                memory['category'],
                memory['metadata']
            )
    
    def _summarize_memories(self, memories: List[Dict]) -> str:
        """Summarize multiple related memories"""
        # Simple concatenation for now - could use LLM for better summarization
        contents = [m['content'] for m in memories]
        return f"Consolidated memory from {len(memories)} interactions: " + " | ".join(contents)
    
    async def forget_old_memories(self, days: int = 30):
        """Remove memories older than specified days"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # Filter metadata
        new_metadata = []
        keep_indices = []
        
        for i, memory in enumerate(self.metadata):
            memory_date = datetime.fromisoformat(memory['timestamp'])
            if memory_date > cutoff_date:
                new_metadata.append(memory)
                keep_indices.append(i)
        
        # Rebuild index with remaining memories
        if keep_indices:
            old_index = self.index
            self.index = faiss.IndexFlatIP(self.embedding_dim)
            
            for idx in keep_indices:
                vector = old_index.reconstruct(int(idx))
                self.index.add(vector.reshape(1, -1))
            
            self.metadata = new_metadata
            self._save_index()
            self._save_metadata()