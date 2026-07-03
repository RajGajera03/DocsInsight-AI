import os
import uuid
import shutil
from typing import List
from dotenv import load_dotenv

from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

# ==========================================
# 1. Pipeline Components Configuration
# ==========================================

# Text Splitter
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)

# Embeddings (Gemini API)
embeddings = GoogleGenerativeAIEmbeddings(model='gemini-embedding-001')

# Vector Store
PERSIST_DIRECTORY = "chroma_data"
vectorstore = Chroma(
    collection_name="pdf_documents",
    embedding_function=embeddings,
    persist_directory=PERSIST_DIRECTORY
)

# LLM (Gemini API)
# Assumes GOOGLE_API_KEY is set in environment variables
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.3
)

# Prompt Template
qa_system_prompt = """You are a helpful assistant for question-answering tasks. 
Use the following pieces of retrieved context to answer the question. 
If you don't know the answer, just say that you don't know.
Make sure to cite the specific page numbers from the context if available.

Context: {context}

Question: {question}
"""
prompt = ChatPromptTemplate.from_messages([
    ("system", qa_system_prompt),
    ("human", "{question}"),
])

# ==========================================
# 2. Pipeline Chains
# ==========================================

def format_docs(docs):
    return "\n\n".join(f"[Page {doc.metadata.get('page', 'Unknown')}]\n{doc.page_content}" for doc in docs)

# ==========================================
# 3. Exported Functions (API Integration)
# ==========================================

def process_pdf_and_store(file_path: str, source_doc_id: int):
    """Parses a PDF, chunks it, and stores it in the vector DB."""
    loader = PyMuPDFLoader(file_path)
    docs = loader.load()
    
    for doc in docs:
        doc.metadata["source_doc_id"] = str(source_doc_id)
        
    chunks = text_splitter.split_documents(docs)
    
    ids = [str(uuid.uuid4()) for _ in range(len(chunks))]
    vectorstore.add_documents(documents=chunks, ids=ids)

def delete_document_from_vectorstore(source_doc_id: str):
    """Deletes all chunks associated with a specific document ID."""
    collection = vectorstore.get()
    
    ids_to_delete = []
    for i, metadata in enumerate(collection["metadatas"]):
        if metadata and metadata.get("source_doc_id") == source_doc_id:
            ids_to_delete.append(collection["ids"][i])
            
    if ids_to_delete:
        vectorstore.delete(ids=ids_to_delete)

def ask_question(question: str, document_id: str = None) -> str:
    """Executes the RAG chain to answer a question."""
    
    # 1. Setup Retriever
    search_kwargs = {"k": 4}
    if document_id:
        search_kwargs["filter"] = {"source_doc_id": document_id}
        
    retriever = vectorstore.as_retriever(search_kwargs=search_kwargs)
    
    # 2. Build LCEL Chain
    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    
    # 3. Invoke Chain
    return rag_chain.invoke(question)
