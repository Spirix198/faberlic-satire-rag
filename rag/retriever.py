"""RAG (Retrieval-Augmented Generation) Retriever Module

Provides document retrieval and context augmentation for LLM-based content generation.
Enables semantic search over a knowledge base of documents.
"""

import logging
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class Document:
    """Represents a document in the knowledge base."""
    id: str
    content: str
    metadata: Dict[str, any]
    embedding: Optional[np.ndarray] = None


class VectorStore:
    """In-memory vector store for document embeddings."""
    
    def __init__(self):
        self.documents: Dict[str, Document] = {}
        self.embeddings: Dict[str, np.ndarray] = {}
    
    def add_document(self, document: Document) -> None:
        """Add a document to the store."""
        self.documents[document.id] = document
        if document.embedding is not None:
            self.embeddings[document.id] = document.embedding
    
    def similarity_search(self, query_embedding: np.ndarray, 
                         top_k: int = 5) -> List[Tuple[Document, float]]:
        """Find most similar documents to query embedding."""
        if not self.embeddings:
            return []
        
        similarities = []
        for doc_id, embedding in self.embeddings.items():
            similarity = np.dot(query_embedding, embedding) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(embedding) + 1e-9
            )
            similarities.append((self.documents[doc_id], similarity))
        
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_k]


class RAGRetriever:
    """Retrieval-Augmented Generation retriever."""
    
    def __init__(self, embedding_model=None, vector_store: Optional[VectorStore] = None):
        """Initialize the RAG retriever.
        
        Args:
            embedding_model: Model for generating embeddings
            vector_store: Vector store for document storage
        """
        self.embedding_model = embedding_model
        self.vector_store = vector_store or VectorStore()
    
    def add_documents(self, documents: List[Document]) -> None:
        """Add documents to the knowledge base.
        
        Args:
            documents: List of documents to add
        """
        for doc in documents:
            if self.embedding_model and doc.embedding is None:
                doc.embedding = self.embedding_model.encode(doc.content)
            self.vector_store.add_document(doc)
            logger.info(f"Added document: {doc.id}")
    
    def retrieve(self, query: str, top_k: int = 5) -> List[Document]:
        """Retrieve relevant documents for a query.
        
        Args:
            query: Search query
            top_k: Number of results to return
            
        Returns:
            List of relevant documents
        """
        if not self.embedding_model:
            logger.warning("No embedding model configured")
            return []
        
        query_embedding = self.embedding_model.encode(query)
        results = self.vector_store.similarity_search(query_embedding, top_k)
        return [doc for doc, _ in results]
    
    def retrieve_with_scores(self, query: str, 
                            top_k: int = 5) -> List[Tuple[Document, float]]:
        """Retrieve documents with similarity scores.
        
        Args:
            query: Search query
            top_k: Number of results to return
            
        Returns:
            List of (document, score) tuples
        """
        if not self.embedding_model:
            return []
        
        query_embedding = self.embedding_model.encode(query)
        return self.vector_store.similarity_search(query_embedding, top_k)
