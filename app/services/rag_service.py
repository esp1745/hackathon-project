"""
RAG service for document processing and retrieval
"""

import os
import uuid
import hashlib
from typing import List, Dict, Any, Optional
from pathlib import Path
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from openai import OpenAI

from app.config import settings


class RAGService:
    """Service for RAG (Retrieval-Augmented Generation) operations"""
    
    def __init__(self):
        """Initialize the RAG service"""
        # Check if we have a valid API key
        self.demo_mode = (not settings.OPENAI_API_KEY or 
                         settings.OPENAI_API_KEY == "your_openai_api_key_here" or 
                         not settings.OPENAI_API_KEY.startswith("sk-"))
        
        if not self.demo_mode:
            self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        else:
            self.client = None
            
        self.embedding_model = settings.EMBEDDING_MODEL
        self.persist_directory = settings.CHROMA_PERSIST_DIRECTORY
        
        # Initialize ChromaDB
        os.makedirs(self.persist_directory, exist_ok=True)
        self.chroma_client = chromadb.PersistentClient(
            path=self.persist_directory,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Get or create collection
        self.collection = self.chroma_client.get_or_create_collection(
            name="documents",
            metadata={"hnsw:space": "cosine"}
        )
        
        # Initialize sentence transformer for local embeddings
        self.sentence_transformer = SentenceTransformer('all-MiniLM-L6-v2')
    
    async def add_document(self, content: str, filename: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Add a document to the RAG system
        
        Args:
            content: Document content
            filename: Original filename
            metadata: Additional metadata
            
        Returns:
            Document ID
        """
        try:
            # Generate document ID
            doc_id = str(uuid.uuid4())
            
            # Create metadata
            doc_metadata = {
                "filename": filename,
                "content_hash": hashlib.md5(content.encode()).hexdigest(),
                "created_at": str(uuid.uuid1().time),
                **(metadata or {})
            }
            
            # Split content into chunks
            chunks = self._split_text(content)
            
            # Generate embeddings for chunks
            embeddings = []
            chunk_ids = []
            chunk_metadatas = []
            chunk_contents = []
            
            for i, chunk in enumerate(chunks):
                chunk_id = f"{doc_id}_chunk_{i}"
                chunk_metadata = {
                    **doc_metadata,
                    "chunk_index": i,
                    "total_chunks": len(chunks)
                }
                
                # Generate embedding
                embedding = await self._get_embedding(chunk)
                
                embeddings.append(embedding)
                chunk_ids.append(chunk_id)
                chunk_metadatas.append(chunk_metadata)
                chunk_contents.append(chunk)
            
            # Add to ChromaDB
            self.collection.add(
                embeddings=embeddings,
                documents=chunk_contents,
                metadatas=chunk_metadatas,
                ids=chunk_ids
            )
            
            return doc_id
            
        except Exception as e:
            raise Exception(f"Failed to add document: {str(e)}")
    
    async def search_documents(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Search for relevant documents
        
        Args:
            query: Search query
            top_k: Number of top results to return
            
        Returns:
            List of relevant document chunks
        """
        try:
            # Generate query embedding
            query_embedding = await self._get_embedding(query)
            
            # Search in ChromaDB
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                include=["documents", "metadatas", "distances"]
            )
            
            # Format results
            formatted_results = []
            if results["documents"] and results["documents"][0]:
                for i, (doc, metadata, distance) in enumerate(zip(
                    results["documents"][0],
                    results["metadatas"][0],
                    results["distances"][0]
                )):
                    formatted_results.append({
                        "content": doc,
                        "metadata": metadata,
                        "similarity_score": 1 - distance,  # Convert distance to similarity
                        "rank": i + 1
                    })
            
            return formatted_results
            
        except Exception as e:
            raise Exception(f"Document search failed: {str(e)}")
    
    async def get_context_for_query(self, query: str, max_chunks: int = 3) -> List[str]:
        """
        Get relevant context for a query
        
        Args:
            query: User query
            max_chunks: Maximum number of chunks to return
            
        Returns:
            List of relevant context strings
        """
        try:
            # Search for relevant documents
            results = await self.search_documents(query, top_k=max_chunks)
            
            # Extract context from results
            context = []
            for result in results:
                context.append(f"From {result['metadata']['filename']}: {result['content']}")
            
            return context
            
        except Exception as e:
            raise Exception(f"Failed to get context: {str(e)}")
    
    async def delete_document(self, filename: str) -> bool:
        """
        Delete a document from the RAG system
        
        Args:
            filename: Filename to delete
            
        Returns:
            True if deleted, False if not found
        """
        try:
            # Search for documents with this filename
            results = self.collection.get(
                where={"filename": filename}
            )
            
            if results["ids"]:
                # Delete all chunks for this document
                self.collection.delete(ids=results["ids"])
                return True
            
            return False
            
        except Exception as e:
            raise Exception(f"Failed to delete document: {str(e)}")
    
    async def list_documents(self) -> List[Dict[str, Any]]:
        """
        List all documents in the RAG system
        
        Returns:
            List of document metadata
        """
        try:
            # Get all documents
            results = self.collection.get()
            
            # Group by filename
            documents = {}
            for i, metadata in enumerate(results["metadatas"]):
                filename = metadata["filename"]
                if filename not in documents:
                    documents[filename] = {
                        "filename": filename,
                        "content_hash": metadata["content_hash"],
                        "created_at": metadata["created_at"],
                        "chunks": 0,
                        "metadata": {k: v for k, v in metadata.items() 
                                   if k not in ["filename", "content_hash", "created_at", "chunk_index", "total_chunks"]}
                    }
                documents[filename]["chunks"] += 1
            
            return list(documents.values())
            
        except Exception as e:
            raise Exception(f"Failed to list documents: {str(e)}")
    
    async def _get_embedding(self, text: str) -> List[float]:
        """
        Get embedding for text
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector
        """
        try:
            # Use OpenAI embeddings if available
            if not self.demo_mode and self.client:
                response = self.client.embeddings.create(
                    model=self.embedding_model,
                    input=text
                )
                return response.data[0].embedding
            else:
                # Use local embeddings
                embedding = self.sentence_transformer.encode(text)
                return embedding.tolist()
            
        except Exception as e:
            # Fallback to local embeddings
            embedding = self.sentence_transformer.encode(text)
            return embedding.tolist()
    
    def _split_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """
        Split text into overlapping chunks
        
        Args:
            text: Text to split
            chunk_size: Size of each chunk
            overlap: Overlap between chunks
            
        Returns:
            List of text chunks
        """
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            
            # Try to break at sentence boundary
            if end < len(text):
                # Look for sentence endings
                for i in range(end, max(start, end - 100), -1):
                    if text[i] in '.!?':
                        end = i + 1
                        break
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            start = end - overlap
            if start >= len(text):
                break
        
        return chunks
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the document collection
        
        Returns:
            Collection statistics
        """
        try:
            count = self.collection.count()
            return {
                "total_documents": count,
                "embedding_model": self.embedding_model,
                "persist_directory": self.persist_directory
            }
        except Exception as e:
            raise Exception(f"Failed to get collection stats: {str(e)}")


# Create global RAG service instance
rag_service = RAGService() 