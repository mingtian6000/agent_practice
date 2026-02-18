"""
Advanced RAG Implementation
Full-featured RAG with real LangChain components
"""
import os
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Try to import real LangChain components, fallback to mock
try:
    from langchain_openai import OpenAIEmbeddings, ChatOpenAI
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    REAL_MODE = True
    print("✓ Using real LangChain components")
except ImportError:
    print("⚠️  LangChain not installed, using mock implementations")
    print("   Install with: pip install langchain langchain-openai")
    REAL_MODE = False


@dataclass
class RAGConfig:
    """Configuration for RAG system"""
    chunk_size: int = 1000
    chunk_overlap: int = 200
    top_k: int = 5
    embedding_model: str = "text-embedding-3-small"
    llm_model: str = "gpt-3.5-turbo"
    temperature: float = 0.7


class DocumentLoader:
    """Load documents from various sources"""
    
    @staticmethod
    def from_text(text: str, metadata: Dict = None) -> Dict[str, Any]:
        """Load from raw text"""
        return {
            "content": text,
            "metadata": metadata or {"source": "text"}
        }
    
    @staticmethod
    def from_file(filepath: str) -> List[Dict[str, Any]]:
        """
        Load documents from file
        Supports: .txt, .md, .py, .json
        """
        documents = []
        
        if not os.path.exists(filepath):
            print(f"❌ File not found: {filepath}")
            return documents
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            ext = os.path.splitext(filepath)[1]
            metadata = {
                "source": filepath,
                "type": ext,
                "filename": os.path.basename(filepath)
            }
            
            documents.append({
                "content": content,
                "metadata": metadata
            })
            
            print(f"✓ Loaded {filepath}")
            
        except Exception as e:
            print(f"❌ Error loading {filepath}: {e}")
        
        return documents
    
    @staticmethod
    def from_directory(directory: str, extensions: List[str] = None) -> List[Dict[str, Any]]:
        """Load all documents from a directory"""
        if extensions is None:
            extensions = ['.txt', '.md', '.py', '.json']
        
        documents = []
        
        if not os.path.exists(directory):
            print(f"❌ Directory not found: {directory}")
            return documents
        
        for filename in os.listdir(directory):
            if any(filename.endswith(ext) for ext in extensions):
                filepath = os.path.join(directory, filename)
                docs = DocumentLoader.from_file(filepath)
                documents.extend(docs)
        
        return documents


class TextChunker:
    """Split text into chunks with various strategies"""
    
    def __init__(self, config: RAGConfig = None):
        self.config = config or RAGConfig()
        
        if REAL_MODE:
            self.splitter = RecursiveCharacterTextSplitter(
                chunk_size=self.config.chunk_size,
                chunk_overlap=self.config.chunk_overlap,
                length_function=len,
                separators=["\n\n", "\n", " ", ""]
            )
        else:
            self.splitter = None
    
    def split_text(self, text: str) -> List[str]:
        """Split text into chunks"""
        if REAL_MODE:
            return self.splitter.split_text(text)
        else:
            # Simple fallback chunking
            chunks = []
            step = self.config.chunk_size - self.config.chunk_overlap
            for i in range(0, len(text), step):
                chunk = text[i:i + self.config.chunk_size]
                if len(chunk) > 50:
                    chunks.append(chunk)
            return chunks
    
    def split_documents(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Split documents into chunks with metadata"""
        chunks = []
        
        for doc in documents:
            text_chunks = self.split_text(doc["content"])
            
            for i, chunk in enumerate(text_chunks):
                chunk_metadata = doc["metadata"].copy()
                chunk_metadata.update({
                    "chunk_index": i,
                    "total_chunks": len(text_chunks)
                })
                
                chunks.append({
                    "content": chunk,
                    "metadata": chunk_metadata
                })
        
        return chunks


class VectorStoreManager:
    """Manage vector database operations"""
    
    def __init__(self, embedding_model: str = None):
        self.embedding_model = embedding_model or os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
        self.store = None
        
        if REAL_MODE:
            try:
                self.embeddings = OpenAIEmbeddings(model=self.embedding_model)
                print(f"✓ Initialized embeddings: {self.embedding_model}")
            except Exception as e:
                print(f"❌ Error initializing embeddings: {e}")
                print("   Make sure OPENAI_API_KEY is set in .env")
                self.embeddings = None
        else:
            self.embeddings = None
    
    def create_store(self, chunks: List[Dict[str, Any]], persist_dir: str = None):
        """Create and populate vector store"""
        if not REAL_MODE or not self.embeddings:
            print("⚠️  Using mock vector store")
            self.store = MockVectorStore()
            return
        
        try:
            from langchain_community.vectorstores import Chroma
            
            persist_dir = persist_dir or os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
            
            # Extract texts and metadata
            texts = [chunk["content"] for chunk in chunks]
            metadatas = [chunk["metadata"] for chunk in chunks]
            
            # Create Chroma store
            self.store = Chroma.from_texts(
                texts=texts,
                embedding=self.embeddings,
                metadatas=metadatas,
                persist_directory=persist_dir
            )
            
            print(f"✓ Created vector store with {len(chunks)} chunks")
            print(f"  Persisted to: {persist_dir}")
            
        except Exception as e:
            print(f"❌ Error creating vector store: {e}")
            self.store = MockVectorStore()
    
    def similarity_search(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Search for similar documents"""
        if self.store is None:
            return []
        
        if REAL_MODE and hasattr(self.store, 'similarity_search_with_score'):
            try:
                results = self.store.similarity_search_with_score(query, k=k)
                return [
                    {
                        "content": doc.page_content,
                        "metadata": doc.metadata,
                        "score": score
                    }
                    for doc, score in results
                ]
            except Exception as e:
                print(f"❌ Search error: {e}")
                return []
        else:
            # Mock results
            return self.store.similarity_search(query, k)


class MockVectorStore:
    """Mock vector store for demo"""
    def __init__(self):
        self.documents = []
    
    def similarity_search(self, query: str, k: int = 5):
        import random
        results = []
        for i, doc in enumerate(self.documents[:k]):
            results.append({
                "content": doc,
                "metadata": {"source": f"doc_{i}"},
                "score": random.uniform(0.7, 0.95)
            })
        return results


class RAGSystem:
    """
    Complete RAG System
    
    Combines: Loading → Chunking → Embedding → Retrieval → Generation
    """
    
    def __init__(self, config: RAGConfig = None):
        self.config = config or RAGConfig()
        
        print("\n" + "=" * 60)
        print("Initializing Advanced RAG System")
        print("=" * 60)
        
        # Initialize components
        self.chunker = TextChunker(self.config)
        self.vector_store = VectorStoreManager(self.config.embedding_model)
        
        if REAL_MODE:
            try:
                self.llm = ChatOpenAI(
                    model=self.config.llm_model,
                    temperature=self.config.temperature
                )
                print(f"✓ Initialized LLM: {self.config.llm_model}")
            except Exception as e:
                print(f"❌ Error initializing LLM: {e}")
                self.llm = None
        else:
            self.llm = None
        
        print(f"\nConfiguration:")
        print(f"  Chunk Size: {self.config.chunk_size}")
        print(f"  Chunk Overlap: {self.config.chunk_overlap}")
        print(f"  Top K: {self.config.top_k}")
        print(f"  Temperature: {self.config.temperature}")
        print("=" * 60)
    
    def ingest(self, documents: List[Dict[str, Any]], persist_dir: str = None) -> None:
        """
        Ingest documents into the RAG system
        
        Pipeline: Documents → Chunks → Embeddings → Vector Store
        """
        print(f"\n📚 Ingesting {len(documents)} documents...")
        
        # Step 1: Chunk documents
        print("  Step 1: Chunking documents...")
        chunks = self.chunker.split_documents(documents)
        print(f"  ✓ Created {len(chunks)} chunks")
        
        # Step 2: Create vector store
        print("  Step 2: Creating vector embeddings...")
        self.vector_store.create_store(chunks, persist_dir)
        print(f"  ✓ Documents indexed")
    
    def query(self, question: str) -> Dict[str, Any]:
        """
        Query the RAG system
        
        Pipeline: Query → Embedding → Retrieval → Prompt → Generation
        """
        print(f"\n🔍 Query: {question}")
        print("-" * 60)
        
        # Step 1: Retrieve relevant chunks
        print("  Step 1: Retrieving relevant chunks...")
        retrieved = self.vector_store.similarity_search(
            query=question,
            k=self.config.top_k
        )
        print(f"  ✓ Retrieved {len(retrieved)} chunks")
        
        # Step 2: Build context
        context = "\n\n---\n\n".join([
            f"[Source: {r['metadata'].get('source', 'unknown')}]\n{r['content']}"
            for r in retrieved
        ])
        
        # Step 3: Generate answer
        print("  Step 2: Generating answer...")
        
        if REAL_MODE and self.llm:
            messages = [
                {
                    "role": "system",
                    "content": "You are a helpful assistant. Use the provided context to answer questions. If you cannot find the answer in the context, say so."
                },
                {
                    "role": "user",
                    "content": f"Context:\n{context}\n\nQuestion: {question}\n\nAnswer:"
                }
            ]
            
            try:
                response = self.llm.invoke(messages)
                answer = response.content
            except Exception as e:
                print(f"❌ Generation error: {e}")
                answer = f"Error generating answer: {e}"
        else:
            answer = f"[Mock Answer] Based on {len(retrieved)} retrieved chunks, here's information about: '{question[:50]}...'"
        
        print(f"  ✓ Answer generated")
        
        return {
            "question": question,
            "answer": answer,
            "context": retrieved,
            "num_chunks": len(retrieved)
        }
    
    def batch_query(self, questions: List[str]) -> List[Dict[str, Any]]:
        """Query multiple questions"""
        results = []
        for question in questions:
            result = self.query(question)
            results.append(result)
        return results


def demo_advanced_rag():
    """Demonstrate advanced RAG features"""
    print("\n" + "=" * 60)
    print("Advanced RAG System Demo")
    print("=" * 60)
    
    # Sample knowledge base
    knowledge_base = [
        {
            "content": """
            LangGraph is a Python library for building stateful, multi-step AI applications.
            It allows you to define complex workflows as graphs where each node represents
            a step in your process. Key features include:
            - State management across steps
            - Conditional routing
            - Parallel execution
            - Cyclical workflows
            """,
            "metadata": {"source": "langgraph_overview.md", "topic": "langgraph"}
        },
        {
            "content": """
            Chroma is an open-source embedding database designed for AI applications.
            It stores data as high-dimensional vectors and enables fast similarity search.
            Chroma integrates seamlessly with LangChain and supports:
            - Persistent storage
            - Metadata filtering
            - Multiple embedding models
            - REST API interface
            """,
            "metadata": {"source": "chroma_guide.md", "topic": "vector_database"}
        },
        {
            "content": """
            Retrieval-Augmented Generation (RAG) enhances LLMs by retrieving relevant
            information from a knowledge base before generating responses. The typical
            RAG pipeline includes:
            1. Document ingestion and chunking
            2. Creating vector embeddings
            3. Storing in vector database
            4. Similarity search for queries
            5. Context-aware generation
            """,
            "metadata": {"source": "rag_basics.md", "topic": "rag"}
        }
    ]
    
    # Initialize RAG with custom config
    config = RAGConfig(
        chunk_size=500,
        chunk_overlap=50,
        top_k=3,
        temperature=0.5
    )
    
    rag = RAGSystem(config)
    
    # Ingest documents
    rag.ingest(knowledge_base)
    
    # Test queries
    questions = [
        "What is LangGraph used for?",
        "How does Chroma store data?",
        "Explain the RAG pipeline steps"
    ]
    
    print("\n" + "=" * 60)
    print("Query Results")
    print("=" * 60)
    
    for q in questions:
        result = rag.query(q)
        print(f"\n❓ {result['question']}")
        print(f"💡 {result['answer']}")
        print(f"📄 Used {result['num_chunks']} chunks")
        print("-" * 60)
    
    print("\n✅ Advanced RAG Demo completed!")
    print("\nTo use with real data:")
    print("  1. Set OPENAI_API_KEY in .env")
    print("  2. Install: pip install langchain langchain-openai chromadb")
    print("  3. Load real documents with DocumentLoader.from_file() or from_directory()")


if __name__ == "__main__":
    demo_advanced_rag()
