# RAG (Retrieval-Augmented Generation) Demos

This directory contains complete implementations of **Retrieval-Augmented Generation** systems using vector databases and embeddings.

## 📁 Structure

```
vectors/
├── requirements.txt         # All dependencies
├── .env.example            # Environment variables template
├── simple_rag.py           # Basic RAG implementation
├── advanced_rag.py         # Full-featured RAG system
└── README.md               # This file
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd vectors
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy the example file
cp .env.example .env

# Edit .env with your OpenAI API key
OPENAI_API_KEY=sk-your-key-here
```

### 3. Run Demos

```bash
# Basic RAG demo
python simple_rag.py

# Advanced RAG with document loading
python advanced_rag.py
```

---

## 📦 Dependencies Explained

### Core RAG Stack

```
langchain>=0.1.0          # Framework for building LLM apps
langchain-community>=0.0.10  # Community integrations
langchain-openai>=0.0.5   # OpenAI integration
```

**What it does**: LangChain provides the framework for chaining together:
- Document loaders
- Text splitters
- Embedding models
- Vector stores
- LLMs

### Vector Database

```
chromadb>=0.4.0           # Vector database
faiss-cpu>=1.7.4          # Facebook's similarity search (optional)
```

**What it does**: 
- **ChromaDB**: Stores documents as embeddings, enables similarity search
- **FAISS**: Alternative fast similarity search library

### Embeddings

```
sentence-transformers>=2.2.2  # Open-source embeddings
openai>=1.0.0             # OpenAI API for embeddings
```

**What it does**:
- **sentence-transformers**: Free, local embedding models
- **openai**: Cloud-based embeddings (requires API key)

### Document Processing

```
unstructured>=0.11.0      # Extract text from various formats
pypdf>=3.17.0             # PDF processing
python-docx>=0.8.11       # Word documents
```

**What it does**: Extract text from PDFs, Word docs, and other file formats

### Utilities

```
python-dotenv>=1.0.0      # Load environment variables
numpy>=1.24.0             # Numerical operations
tiktoken>=0.5.0           # Token counting for OpenAI
```

---

## 📚 What is RAG?

**Retrieval-Augmented Generation (RAG)** is a technique that:

1. **Retrieves** relevant information from a knowledge base
2. **Augments** the LLM prompt with that context
3. **Generates** answers grounded in the retrieved information

### Why Use RAG?

- ✅ **Reduces hallucinations** - Answers based on real documents
- ✅ **Up-to-date knowledge** - Can use latest documents
- ✅ **Domain-specific** - Can use private/internal documents
- ✅ **Citations** - Can show which documents were used

### RAG Pipeline

```
Documents → Chunking → Embeddings → Vector Store
                                      ↓
Query → Embedding → Similarity Search → Context
                                      ↓
Prompt (Query + Context) → LLM → Answer
```

---

## 🎯 Examples

### Example 1: Simple RAG (`simple_rag.py`)

**What it demonstrates**:
- Basic RAG flow
- Mock components (works without API keys)
- Chunking and embedding concepts
- Query → Retrieve → Generate pipeline

**Code overview**:
```python
# Initialize
rag = SimpleRAG()

# Load documents
rag.load_documents(["Document 1 text...", "Document 2 text..."])

# Query
result = rag.query("What is RAG?")
print(result['answer'])
```

**Run**:
```bash
python simple_rag.py
```

### Example 2: Advanced RAG (`advanced_rag.py`)

**What it demonstrates**:
- Real LangChain integration
- Document loading from files/directories
- Advanced chunking strategies
- Metadata handling
- Multiple queries

**Code overview**:
```python
from advanced_rag import RAGSystem, RAGConfig, DocumentLoader

# Configuration
config = RAGConfig(chunk_size=500, top_k=3)
rag = RAGSystem(config)

# Load from directory
docs = DocumentLoader.from_directory("./my_docs")
rag.ingest(docs)

# Query
result = rag.query("Explain this concept")
```

**Run**:
```bash
python advanced_rag.py
```

---

## 🔑 Configuration

### Environment Variables

Copy `.env.example` to `.env` and configure:

```env
# Required for real implementation
OPENAI_API_KEY=sk-************************

# Optional: For free local embeddings
HUGGINGFACE_TOKEN=hf_************************

# Vector DB settings
CHROMA_PERSIST_DIR=./chroma_db

# RAG settings
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
TOP_K_RESULTS=5
EMBEDDING_MODEL=text-embedding-3-small
LLM_MODEL=gpt-3.5-turbo
```

### Chunking Strategy

**Chunk Size**: How many characters per chunk
- Smaller (200-500): More granular, better for specific queries
- Larger (1000-2000): More context, better for broad questions

**Chunk Overlap**: How much overlap between chunks
- Ensures context isn't lost at chunk boundaries
- Typical: 10-20% of chunk size

**Example**:
```python
config = RAGConfig(
    chunk_size=500,      # 500 characters per chunk
    chunk_overlap=50,    # 50 character overlap
    top_k=3              # Retrieve top 3 chunks
)
```

---

## 📖 Usage Patterns

### Pattern 1: Load from Text

```python
from simple_rag import SimpleRAG

rag = SimpleRAG()

documents = [
    "LangGraph is a library for building stateful AI workflows...",
    "Chroma is a vector database for storing embeddings..."
]

rag.load_documents(documents)
result = rag.query("What is LangGraph?")
```

### Pattern 2: Load from Files

```python
from advanced_rag import DocumentLoader, RAGSystem

# Single file
docs = DocumentLoader.from_file("./report.pdf")

# Entire directory
docs = DocumentLoader.from_directory("./knowledge_base/")

rag = RAGSystem()
rag.ingest(docs)
```

### Pattern 3: Batch Queries

```python
questions = [
    "What is RAG?",
    "How does it work?",
    "What are the benefits?"
]

results = rag.batch_query(questions)
for result in results:
    print(f"Q: {result['question']}")
    print(f"A: {result['answer']}\n")
```

---

## 🛠️ Creating Custom RAG

Want to build your own RAG system? Here's the template:

```python
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma

# 1. Load documents
with open("my_doc.txt") as f:
    text = f.read()

# 2. Split into chunks
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)
chunks = text_splitter.split_text(text)

# 3. Create embeddings and store
embeddings = OpenAIEmbeddings()
vectorstore = Chroma.from_texts(
    texts=chunks,
    embedding=embeddings,
    persist_directory="./chroma_db"
)

# 4. Query
llm = ChatOpenAI()
query = "What does this document say about X?"

# Retrieve relevant chunks
docs = vectorstore.similarity_search(query, k=5)
context = "\n".join([d.page_content for d in docs])

# Generate answer
prompt = f"Context: {context}\n\nQuestion: {query}\n\nAnswer:"
answer = llm.predict(prompt)
print(answer)
```

---

## 🔧 Troubleshooting

### "Module not found" errors

```bash
# Make sure you're in the vectors directory
cd vectors
pip install -r requirements.txt
```

### "API key not set" errors

1. Check `.env` file exists
2. Verify OPENAI_API_KEY is set (not the example values)
3. Make sure `python-dotenv` is installed

### "Out of memory" with large documents

```python
# Use smaller chunk size
config = RAGConfig(chunk_size=200)

# Or process documents in batches
for batch in chunks(documents, batch_size=10):
    rag.ingest(batch)
```

### "No results found"

1. Check documents were loaded: `print(len(documents))`
2. Try different chunk size (might be too small/large)
3. Check similarity search is working
4. Verify embeddings are being created

---

## 🎓 Learning Path

### Beginner
1. **Start here**: Run `python simple_rag.py`
   - Understand the RAG flow
   - See mock components in action

2. **Install dependencies**: `pip install -r requirements.txt`
   - Get real components working
   - Set up OpenAI API key

### Intermediate
3. **Try advanced**: Run `python advanced_rag.py`
   - Use real LangChain components
   - Load actual documents

4. **Experiment**: Modify chunk sizes
   - Try different values (200, 500, 1000)
   - See how it affects results

### Advanced
5. **Load real data**: Use your own documents
   - PDFs, Word docs, text files
   - Load from directories

6. **Customize**: Build your own RAG
   - Add custom metadata
   - Implement filtering
   - Add evaluation metrics

---

## 📚 Resources

- **LangChain Docs**: https://python.langchain.com/
- **Chroma Docs**: https://docs.trychroma.com/
- **OpenAI Embeddings**: https://platform.openai.com/docs/guides/embeddings
- **FAISS**: https://github.com/facebookresearch/faiss

---

## 🤝 Next Steps

1. ✅ Run the demos
2. ✅ Load your own documents
3. ✅ Experiment with chunk sizes
4. ✅ Build custom RAG for your use case
5. ✅ Add evaluation metrics
6. ✅ Deploy to production

---

**Happy Building with RAG! 🔍✨**
