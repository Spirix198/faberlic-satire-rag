"""Advanced RAG System with Vector Database Support

Supports:
- FAISS vector indexing
- Semantic search
- Multi-language embeddings
- Caching and persistence
- Production-ready logging
"""

import os
import json
import logging
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime
import pickle
import numpy as np

try:
    import faiss
    HAS_FAISS = True
except ImportError:
    HAS_FAISS = False
    logging.warning("FAISS not installed. Vector search will be limited.")

try:
    from sentence_transformers import SentenceTransformer
    HAS_TRANSFORMERS = True
except ImportError:
    HAS_TRANSFORMERS = False
    logging.warning("sentence-transformers not installed.")

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)


@dataclass
class Document:
    """Represents a document in the RAG system"""
    id: str
    content: str
    metadata: Dict = None
    embedding: Optional[np.ndarray] = None
    created_at: str = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()


class RAGSystem:
    """Advanced RAG System with vector database support"""

    def __init__(self, model_name: str = "sentence-transformers/paraphrase-MiniLM-L6-v2",
                 index_dir: str = "./rag_index", dimension: int = 384):
        """Initialize RAG System
        
        Args:
            model_name: Sentence transformer model name
            index_dir: Directory to store indices
            dimension: Embedding dimension
        """
        self.model_name = model_name
        self.index_dir = index_dir
        self.dimension = dimension
        self.documents: Dict[str, Document] = {}
        self.index = None
        self.id_mapping = {}  # Maps index to document ID
        self.model = None
        self._initialize_model()
        self._load_or_create_index()
        
        logger.info(f"RAG System initialized with model: {model_name}")

    def _initialize_model(self):
        """Initialize embedding model"""
        if not HAS_TRANSFORMERS:
            logger.warning("sentence-transformers not available. Install with: pip install sentence-transformers")
            return
        
        try:
            self.model = SentenceTransformer(self.model_name)
            logger.info(f"Loaded embedding model: {self.model_name}")
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            self.model = None

    def _load_or_create_index(self):
        """Load existing index or create new one"""
        if not HAS_FAISS:
            logger.warning("FAISS not available. Install with: pip install faiss-cpu")
            return
        
        os.makedirs(self.index_dir, exist_ok=True)
        index_path = os.path.join(self.index_dir, "faiss.index")
        id_map_path = os.path.join(self.index_dir, "id_mapping.pkl")
        docs_path = os.path.join(self.index_dir, "documents.json")
        
        if os.path.exists(index_path):
            try:
                self.index = faiss.read_index(index_path)
                with open(id_map_path, 'rb') as f:
                    self.id_mapping = pickle.load(f)
                with open(docs_path, 'r') as f:
                    docs_data = json.load(f)
                    for doc_id, doc_info in docs_data.items():
                        self.documents[doc_id] = Document(**doc_info)
                logger.info(f"Loaded existing index with {len(self.documents)} documents")
            except Exception as e:
                logger.error(f"Error loading index: {e}")
                self._create_new_index()
        else:
            self._create_new_index()

    def _create_new_index(self):
        """Create new FAISS index"""
        if not HAS_FAISS:
            return
        
        self.index = faiss.IndexFlatL2(self.dimension)
        logger.info(f"Created new FAISS index with dimension {self.dimension}")

    def add_document(self, doc_id: str, content: str, metadata: Dict = None) -> bool:
        """Add document to RAG system
        
        Args:
            doc_id: Document ID
            content: Document content
            metadata: Optional metadata
            
        Returns:
            True if successful
        """
        try:
            if doc_id in self.documents:
                logger.warning(f"Document {doc_id} already exists. Skipping.")
                return False
            
            # Create document
            doc = Document(id=doc_id, content=content, metadata=metadata)
            
            # Generate embedding
            if self.model:
                embedding = self.model.encode([content])[0].astype(np.float32)
                doc.embedding = embedding
                
                # Add to FAISS index
                if self.index:
                    idx = len(self.id_mapping)
                    self.index.add(np.array([embedding]))
                    self.id_mapping[idx] = doc_id
            
            # Store document
            self.documents[doc_id] = doc
            logger.info(f"Added document: {doc_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding document {doc_id}: {e}")
            return False

    def search(self, query: str, k: int = 5) -> List[Tuple[str, float, Document]]:
        """Search for relevant documents
        
        Args:
            query: Search query
            k: Number of results
            
        Returns:
            List of (doc_id, score, document) tuples
        """
        if not self.model or not self.index:
            logger.warning("Search not available. Model or index not initialized.")
            return []
        
        try:
            # Encode query
            query_embedding = self.model.encode([query])[0].astype(np.float32)
            
            # Search
            distances, indices = self.index.search(np.array([query_embedding]), min(k, len(self.documents)))
            
            results = []
            for dist, idx in zip(distances[0], indices[0]):
                if idx >= 0 and idx in self.id_mapping:
                    doc_id = self.id_mapping[idx]
                    doc = self.documents[doc_id]
                    score = float(1 / (1 + dist))  # Convert distance to similarity
                    results.append((doc_id, score, doc))
            
            logger.info(f"Search for '{query}' returned {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"Error searching: {e}")
            return []

    def save(self):
        """Save index and documents to disk"""
        if not HAS_FAISS or not self.index:
            return
        
        try:
            os.makedirs(self.index_dir, exist_ok=True)
            
            # Save FAISS index
            index_path = os.path.join(self.index_dir, "faiss.index")
            faiss.write_index(self.index, index_path)
            
            # Save ID mapping
            id_map_path = os.path.join(self.index_dir, "id_mapping.pkl")
            with open(id_map_path, 'wb') as f:
                pickle.dump(self.id_mapping, f)
            
            # Save documents
            docs_path = os.path.join(self.index_dir, "documents.json")
            docs_data = {}
            for doc_id, doc in self.documents.items():
                docs_data[doc_id] = {
                    'id': doc.id,
                    'content': doc.content,
                    'metadata': doc.metadata,
                    'created_at': doc.created_at
                }
            
            with open(docs_path, 'w') as f:
                json.dump(docs_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Saved RAG index to {self.index_dir}")
            
        except Exception as e:
            logger.error(f"Error saving index: {e}")

    def get_stats(self) -> Dict:
        """Get RAG system statistics"""
        return {
            'total_documents': len(self.documents),
            'index_size': len(self.id_mapping),
            'model': self.model_name,
            'dimension': self.dimension,
            'has_faiss': HAS_FAISS and self.index is not None,
            'has_embeddings': self.model is not None
        }
