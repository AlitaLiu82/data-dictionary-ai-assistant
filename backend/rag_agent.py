"""
Data Dictionary RAG Agent

This module provides a conversational AI agent that can answer questions
about your data dictionary using Retrieval Augmented Generation (RAG).
"""

import os
from dotenv import load_dotenv

# Load environment variables
try:
    import streamlit as st
    if hasattr(st, 'secrets') and 'OPENAI_API_KEY' in st.secrets:
        os.environ['OPENAI_API_KEY'] = st.secrets['OPENAI_API_KEY']
except:
    load_dotenv()

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough


class DataDictionaryAgent:
    """RAG-powered agent for querying data dictionary."""
    
    def __init__(self, vectorstore_path: str = "data/vectorstore"):
        """Initialize the RAG agent."""
        
        print("🚀 Initializing Data Dictionary Agent...")
        
        # Load vector store
        embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        self.vectorstore = Chroma(
            persist_directory=vectorstore_path,
            embedding_function=embeddings
        )
        
        # Initialize LLM
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0
        )
        
        # Create prompt
        self.prompt = ChatPromptTemplate.from_template("""You are a helpful data dictionary assistant.

Use the following context to answer the question. Be concise and technical.

For formulas, write them in plain text (e.g., "ROAS = Revenue / Cost").

Context:
{context}

Question: {question}

Answer:""")
        
        # Create retriever
        self.retriever = self.vectorstore.as_retriever(
            search_kwargs={"k": 5}
        )
        
        print("✅ Agent ready!")
    
    def format_docs(self, docs):
        """Format documents for context."""
        return "\n\n".join(doc.page_content for doc in docs)
    
    def query(self, question: str) -> dict:
        """Query the data dictionary."""
        
        # Retrieve documents
        docs = self.retriever.invoke(question)
        
        # Format context
        context = self.format_docs(docs)
        
        # Generate answer
        chain = (
            {"context": lambda x: context, "question": RunnablePassthrough()}
            | self.prompt
            | self.llm
            | StrOutputParser()
        )
        
        answer = chain.invoke(question)
        
        # Extract metadata
        tables = set()
        columns = []
        
        for doc in docs:
            tables.add(doc.metadata.get("table", "Unknown"))
            columns.append({
                "table": doc.metadata.get("table"),
                "column": doc.metadata.get("column"),
                "type": doc.metadata.get("type"),
                "refresh": doc.metadata.get("refresh_frequency", "unknown")
            })
        
        return {
            "answer": answer,
            "sources": docs,
            "tables": list(tables),
            "columns": columns
        }
