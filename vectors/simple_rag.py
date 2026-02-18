"""
RAG (Retrieval-Augmented Generation) System
Simple implementation with ChromaDB vector store
"""
import os
from typing import List, Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Mock implementations for demo (replace with real imports when dependencies installed)
class MockEmbedding:
    """Mock embedding model"""
    def __init__(self, model_name="text-embedding-3-small"):
        self.model_name = model_name
        print(f"[Mock] Initialized embedding model: {model_name}")
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Mock document embedding"""
        import random
        return [[random.random() for _ in range(1536)] for _ in texts]
    
    def embed_query(self, text: str) -> List[float]:
        """Mock query embedding"""
        import random
        return [random.random() for _ in range(1536)]


class MockVectorStore:
    """Mock vector database"""
    def __init__(self, persist_dir="./chroma_db"):
        self.persist_dir = persist_dir
        self.documents = []
        self.embeddings = []
        print(f"[Mock] Initialized vector store at: {persist_dir}")
    
    def add_documents(self, texts: List[str], metadata: List[Dict] = None):
        """Add documents to store"""
        self.documents.extend(texts)
        print(f"[Mock] Added {len(texts)} documents to vector store")
    
    def similarity_search(self, query: str, k: int = 5) -> List[Dict]:
        """Mock similarity search"""
        # Return top k documents (mock)
        results = []
        for i, doc in enumerate(self.documents[:k]):
            results.append({
                "content": doc,
                "metadata": {"source": f"doc_{i}"},
                "score": 0.85 - (i * 0.05)
            })
        return results


class MockLLM:
    """Mock LLM for generation"""
    def __init__(self, model_name="gpt-3.5-turbo"):
        self.model_name = model_name
        print(f"[Mock] Initialized LLM: {model_name}")
    
    def generate(self, prompt: str) -> str:
        """Mock generation"""
        return f"[Mock LLM Response] Based on the provided context, here's an answer to your question: '{prompt[:50]}...'"


class SimpleRAG:
    """
    Simple RAG implementation
    
    Flow: Documents → Chunks → Embeddings → Vector Store → Retrieve → Generate
    """
    
    def __init__(self, 
                 embedding_model: str = "text-embedding-3-small",
                 llm_model: str = "gpt-3.5-turbo",
                 persist_dir: str = "./chroma_db"):
        """
        Initialize RAG system
        
        Args:
            embedding_model: Name of embedding model
            llm_model: Name of LLM model
            persist_dir: Directory to persist vector store
        """
        print("=" * 60)
        print("Initializing Simple RAG System")
        print("=" * 60)
        
        # Initialize components
        self.embedder = MockEmbedding(embedding_model)
        self.vector_store = MockVectorStore(persist_dir)
        self.llm = MockLLM(llm_model)
        
        # Configuration
        self.chunk_size = int(os.getenv("CHUNK_SIZE", "1000"))
        self.chunk_overlap = int(os.getenv("CHUNK_OVERLAP", "200"))
        self.top_k = int(os.getenv("TOP_K_RESULTS", "5"))
        
        print(f"\nConfiguration:")
        print(f"  Chunk Size: {self.chunk_size}")
        print(f"  Chunk Overlap: {self.chunk_overlap}")
        print(f"  Top K Results: {self.top_k}")
        print("=" * 60)
    
    def load_documents(self, texts: List[str], metadata: List[Dict] = None) -> None:
        """
        Load and index documents
        
        Args:
            texts: List of document texts
            metadata: Optional metadata for each document
        """
        print(f"\n📚 Loading {len(texts)} documents...")
        
        # Create metadata if not provided
        if metadata is None:
            metadata = [{"source": f"doc_{i}"} for i in range(len(texts))]
        
        # Chunk documents
        chunks = self._chunk_documents(texts)
        print(f"  Created {len(chunks)} chunks")
        
        # Add to vector store
        self.vector_store.add_documents(chunks, metadata)
        print(f"  ✓ Documents indexed successfully")
    
    def _chunk_documents(self, texts: List[str]) -> List[str]:
        """
        Split documents into chunks
        
        Args:
            texts: List of document texts
            
        Returns:
            List of text chunks
        """
        chunks = []
        for text in texts:
            # Simple chunking by character count
            for i in range(0, len(text), self.chunk_size - self.chunk_overlap):
                chunk = text[i:i + self.chunk_size]
                if len(chunk) > 100:  # Only keep substantial chunks
                    chunks.append(chunk)
        return chunks
    
    def query(self, question: str) -> Dict[str, Any]:
        """
        Query the RAG system
        
        Args:
            question: User question
            
        Returns:
            Dictionary with answer and context
        """
        print(f"\n🔍 Query: {question}")
        print("-" * 60)
        
        # Step 1: Retrieve relevant documents
        print("  Step 1: Retrieving relevant documents...")
        retrieved_docs = self.vector_store.similarity_search(
            query=question,
            k=self.top_k
        )
        print(f"  ✓ Retrieved {len(retrieved_docs)} documents")
        
        # Step 2: Build context from retrieved documents
        context = "\n\n".join([doc["content"] for doc in retrieved_docs])
        
        # Step 3: Generate answer
        print("  Step 2: Generating answer...")
        prompt = self._build_prompt(question, context)
        answer = self.llm.generate(prompt)
        print(f"  ✓ Answer generated")
        
        return {
            "question": question,
            "answer": answer,
            "context": retrieved_docs,
            "num_chunks_used": len(retrieved_docs)
        }
    
    def _build_prompt(self, question: str, context: str) -> str:
        """
        Build prompt for LLM
        
        Args:
            question: User question
            context: Retrieved context
            
        Returns:
            Formatted prompt
        """
        prompt = f"""Use the following context to answer the question. 
If the answer cannot be found in the context, say "I don't have enough information."

Context:
{context}

Question: {question}

Answer:"""
        return prompt
    
    def get_stats(self) -> Dict[str, Any]:
        """Get system statistics"""
        return {
            "total_documents": len(self.vector_store.documents),
            "chunk_size": self.chunk_size,
            "chunk_overlap": self.chunk_overlap,
            "embedding_model": self.embedder.model_name,
            "llm_model": self.llm.model_name
        }


def demo_rag():
    """Demonstrate RAG system"""
    print("\n" + "=" * 60)
    print("RAG (Retrieval-Augmented Generation) Demo")
    print("=" * 60)
    
    # Sample documents
    documents = [
        """
        Python is a high-level, interpreted programming language created by Guido van Rossum 
        and first released in 1991. Python's design philosophy emphasizes code readability 
        with its use of significant indentation. It supports multiple programming paradigms, 
        including structured, object-oriented, and functional programming.
        """,
        """
        LangGraph is a library for building stateful, multi-actor applications with LLMs, 
        built on top of LangChain. It extends the LangChain Expression Language with the 
        ability to coordinate multiple chains across multiple steps of computation in a cyclic manner.
        """,
        """
        Chroma is the open-source embedding database. Chroma makes it easy to build LLM apps 
        by making knowledge, facts, and skills pluggable for LLMs. It provides a simple API 
        for storing and querying embeddings with metadata.
        """,
        """
        Retrieval-Augmented Generation (RAG) is a technique that enhances large language models 
        by retrieving relevant information from a knowledge base before generating responses. 
        This approach helps reduce hallucinations and provides more accurate, grounded answers.
        """,
        """
        Vector databases store data as high-dimensional vectors, which are mathematical representations 
        of features or attributes. These vectors enable similarity search, allowing you to find 
        the most similar vectors to a query vector quickly and efficiently.
        """
    ]
    
    # Initialize RAG
    rag = SimpleRAG(
        embedding_model="text-embedding-3-small",
        llm_model="gpt-3.5-turbo"
    )
    
    # Load documents
    rag.load_documents(documents)
    
    # Show stats
    stats = rag.get_stats()
    print(f"\n📊 System Stats:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # Test queries
    test_questions = [
        "What is Python programming language?",
        "How does RAG work?",
        "What is Chroma used for?",
        "Tell me about LangGraph"
    ]
    
    print("\n" + "=" * 60)
    print("Testing Queries")
    print("=" * 60)
    
    for question in test_questions:
        result = rag.query(question)
        
        print(f"\n❓ Question: {result['question']}")
        print(f"💡 Answer: {result['answer']}")
        print(f"📄 Chunks used: {result['num_chunks_used']}")
        print("-" * 60)
    
    print("\n" + "=" * 60)
    print("RAG Demo completed!")
    print("=" * 60)
    print("\nTo use real implementation:")
    print("  1. Install dependencies: pip install -r requirements.txt")
    print("  2. Set API keys in .env file")
    print("  3. Replace Mock classes with real LangChain implementations")


if __name__ == "__main__":
    demo_rag()
