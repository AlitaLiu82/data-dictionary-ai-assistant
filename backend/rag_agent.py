"""
Data Dictionary RAG Agent

This module provides a conversational AI agent that can answer questions
about your data dictionary using Retrieval Augmented Generation (RAG).

Features:
- Semantic search over column definitions
- Natural language Q&A
- Source attribution for transparency
- Support for complex queries (joins, dependencies, refresh schedules)
"""

import os
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv

# Load environment variables
# Try Streamlit secrets first (for deployed app), then fall back to .env (for local)
try:
    import streamlit as st
    if hasattr(st, 'secrets') and 'OPENAI_API_KEY' in st.secrets:
        os.environ['OPENAI_API_KEY'] = st.secrets['OPENAI_API_KEY']
except:
    # Running locally or secrets not available
    load_dotenv()


class DataDictionaryAgent:
    """
    RAG-powered agent for querying data dictionary.
    """
    
    def __init__(self, vectorstore_path: str = "data/vectorstore"):
        """
        Initialize the RAG agent.
        
        Args:
            vectorstore_path: Path to the Chroma vector store
        """
        
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
            temperature=0,  # Deterministic responses for data questions
            streaming=False
        )
        
        # Create prompt template
        template = """You are a helpful data dictionary assistant for a data analytics team.
Your job is to help users understand tables, columns, metrics, dependencies, and refresh schedules.

Use the following data dictionary entries to answer the question. Be concise, precise, and technical when appropriate.

When answering:
- For metric questions (like CTR, ROAS): explain what it is, how it's calculated, and where to find it
- For formulas: write them in plain text format (e.g., "ROAS = Revenue / Cost" or "CTR = Clicks / Impressions")
- For table questions: list key columns and purpose
- For column questions: explain meaning, data type, example values, and any sample queries
- For dependency questions: explain upstream and downstream relationships clearly
- For refresh questions: mention frequency and schedule
- For "how do I" questions: provide the sample query if available

IMPORTANT: Never use LaTeX notation like \\text or [] brackets for formulas. Always write formulas in plain English.

If the information isn't in the data dictionary, say "I don't have information about that in the current data dictionary."

Data Dictionary Entries:
{context}

Question: {question}

Answer (be technical but clear, use plain text for any formulas):"""

        PROMPT = PromptTemplate(
            template=template,
            input_variables=["context", "question"]
        )
        
        # Create QA chain
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.vectorstore.as_retriever(
                search_type="similarity",
                search_kwargs={"k": 5}  # Return top 5 most relevant entries
            ),
            chain_type_kwargs={"prompt": PROMPT},
            return_source_documents=True
        )
        
        print("✅ Agent ready!")
    
    def query(self, question: str) -> dict:
        """
        Query the data dictionary.
        
        Args:
            question: Natural language question
            
        Returns:
            dict with 'answer', 'sources', 'tables', and 'columns'
        """
        
        # Execute query
        result = self.qa_chain.invoke({"query": question})
        
        # Extract unique tables mentioned
        tables = set()
        columns = []
        
        for doc in result["source_documents"]:
            tables.add(doc.metadata.get("table", "Unknown"))
            columns.append({
                "table": doc.metadata.get("table"),
                "column": doc.metadata.get("column"),
                "type": doc.metadata.get("type"),
                "refresh": doc.metadata.get("refresh_frequency", "unknown")
            })
        
        return {
            "answer": result["result"],
            "sources": result["source_documents"],
            "tables": list(tables),
            "columns": columns
        }
    
    def get_table_schema(self, table_name: str) -> list:
        """
        Get all columns for a specific table.
        
        Args:
            table_name: Name of the table
            
        Returns:
            List of documents for that table
        """
        
        # Search for all columns in this table
        results = self.vectorstore.similarity_search(
            f"table {table_name} columns schema",
            k=50,  # Get many results
        )
        
        # Filter to exact table matches
        table_results = [
            doc for doc in results 
            if doc.metadata.get("table") == table_name
        ]
        
        return table_results


def run_interactive_demo():
    """
    Run an interactive demo of the agent.
    """
    
    print("\n" + "="*60)
    print("🤖 Data Dictionary Agent - Interactive Demo")
    print("="*60)
    print("\nType 'quit' or 'exit' to stop\n")
    
    # Initialize agent
    agent = DataDictionaryAgent()
    
    while True:
        # Get user input
        question = input("\n❓ Your question: ").strip()
        
        if question.lower() in ['quit', 'exit', 'q']:
            print("\n👋 Goodbye!")
            break
        
        if not question:
            continue
        
        # Query agent
        print("\n🔍 Searching...")
        response = agent.query(question)
        
        # Display answer
        print(f"\n💡 Answer:\n{response['answer']}\n")
        
        # Display metadata
        if response['tables']:
            print(f"📊 Tables referenced: {', '.join(response['tables'])}")
        
        if response['columns']:
            print(f"📁 Columns found: {len(response['columns'])}")
            for col in response['columns'][:3]:  # Show first 3
                print(f"   • {col['table']}.{col['column']} ({col['type']}) - refreshes {col['refresh']}")


def run_test_queries():
    """
    Run a set of predefined test queries to demonstrate capabilities.
    """
    
    print("\n" + "="*60)
    print("🧪 Running Test Queries")
    print("="*60)
    
    # Initialize agent
    agent = DataDictionaryAgent()
    
    # Test queries covering different use cases
    test_queries = [
        "What is CTR and how is it calculated?",
        "Show me all columns in the conversions table",
        "What tables depend on ad_impressions?",
        "Which tables refresh hourly?",
        "How do I join ad_clicks with conversions?",
        "Give me a sample query to get user lifetime value",
        "What is ROAS?",
        "What's in the metrics_daily table?",
        "Show me all metrics related to conversions"
    ]
    
    for i, question in enumerate(test_queries, 1):
        print(f"\n{'='*60}")
        print(f"Query {i}/{len(test_queries)}: {question}")
        print('='*60)
        
        response = agent.query(question)
        
        print(f"\n💡 Answer:\n{response['answer']}\n")
        print(f"📊 Tables: {', '.join(response['tables'])}")
        print(f"📁 Columns: {len(response['columns'])} found")


def main():
    """
    Main execution function.
    """
    
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "interactive":
        # Run interactive mode
        run_interactive_demo()
    else:
        # Run test queries
        run_test_queries()
        
        print("\n" + "="*60)
        print("✅ Test complete!")
        print("="*60)
        print("\n💡 Tip: Run 'python backend/rag_agent.py interactive' for interactive mode")


if __name__ == "__main__":
    main()