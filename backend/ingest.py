"""
Data Dictionary Ingestion Pipeline

This script loads an enhanced data dictionary CSV and creates a vector store
for semantic search using LangChain and Chroma.

The data dictionary includes:
- Column definitions and metadata
- Table dependencies (upstream/downstream)
- Refresh schedules
- Sample SQL queries
- dbt model references
"""

import pandas as pd
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.schema import Document
from dotenv import load_dotenv
import os


# Load environment variables
# Try Streamlit secrets first (for deployed app), then fall back to .env (for local)
try:
    import streamlit as st
    if hasattr(st, 'secrets') and 'OPENAI_API_KEY' in st.secrets:
        os.environ['OPENAI_API_KEY'] = st.secrets['OPENAI_API_KEY']
except:
    # Running locally or secrets not available
    load_dotenv()


def load_data_dictionary(csv_path: str) -> list[Document]:
    """
    Load enhanced data dictionary CSV and convert to LangChain documents.
    
    Args:
        csv_path: Path to the data dictionary CSV file
        
    Returns:
        List of LangChain Document objects
    """
    
    print(f"📂 Loading data dictionary from {csv_path}...")
    df = pd.read_csv(csv_path)
    print(f"✅ Loaded {len(df)} entries")
    
    documents = []
    
    for _, row in df.iterrows():
        # Create rich text content for each column entry
        content_parts = [
            f"Table: {row['table_name']}",
            f"Column: {row['column_name']}",
            f"Data Type: {row['data_type']}",
            f"Description: {row['description']}",
            f"Example Values: {row['example_values']}",
            f"Business Owner: {row['business_owner']}",
            f"Last Updated: {row['last_updated']}"
        ]
        
        # Add upstream dependencies if present
        if pd.notna(row['upstream_tables']) and row['upstream_tables']:
            content_parts.append(f"Upstream Tables: {row['upstream_tables']}")
        
        # Add downstream dependencies if present
        if pd.notna(row['downstream_tables']) and row['downstream_tables']:
            content_parts.append(f"Downstream Tables: {row['downstream_tables']}")
        
        # Add refresh information
        if pd.notna(row['refresh_frequency']):
            content_parts.append(f"Refresh Frequency: {row['refresh_frequency']}")
        
        if pd.notna(row['refresh_schedule']):
            content_parts.append(f"Refresh Schedule: {row['refresh_schedule']} (cron format)")
        
        # Add sample query if present
        if pd.notna(row['sample_query']) and row['sample_query']:
            content_parts.append(f"Sample Query: {row['sample_query']}")
        
        # Add dbt model reference
        if pd.notna(row['dbt_model']) and row['dbt_model']:
            content_parts.append(f"dbt Model: {row['dbt_model']}")
        
        content = "\n".join(content_parts)
        
        # Store metadata for filtering
        metadata = {
            "table": row['table_name'],
            "column": row['column_name'],
            "type": row['data_type'],
            "owner": row['business_owner'],
            "refresh_frequency": row['refresh_frequency'] if pd.notna(row['refresh_frequency']) else "unknown",
            "dbt_model": row['dbt_model'] if pd.notna(row['dbt_model']) else "none"
        }
        
        documents.append(Document(
            page_content=content,
            metadata=metadata
        ))
    
    print(f"📄 Created {len(documents)} document objects")
    return documents


def create_vectorstore(documents: list[Document], persist_dir: str):
    """
    Create embeddings and persist vector store to disk.
    
    Args:
        documents: List of LangChain documents
        persist_dir: Directory to save the vector store
        
    Returns:
        Chroma vectorstore instance
    """
    
    print(f"\n🧠 Creating embeddings for {len(documents)} entries...")
    print("⏳ This may take a minute...")
    
    # Initialize OpenAI embeddings (text-embedding-3-small is cost-effective)
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    
    # Create vector store
    vectorstore = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        persist_directory=persist_dir
    )
    
    print(f"✅ Vector store created successfully!")
    print(f"📍 Persisted to: {persist_dir}")
    
    return vectorstore


def test_retrieval(vectorstore, test_queries: list[str]):
    """
    Test the vector store with sample queries.
    
    Args:
        vectorstore: Chroma vectorstore instance
        test_queries: List of test questions
    """
    
    print("\n" + "="*60)
    print("🔍 Testing Retrieval")
    print("="*60)
    
    for query in test_queries:
        print(f"\n❓ Query: {query}")
        results = vectorstore.similarity_search(query, k=2)
        
        if results:
            print(f"💡 Top result:")
            print(f"   Table: {results[0].metadata['table']}")
            print(f"   Column: {results[0].metadata['column']}")
            print(f"   Refresh: {results[0].metadata.get('refresh_frequency', 'N/A')}")
        else:
            print("⚠️  No results found")


def main():
    """Main execution function"""
    
    # Configuration
    CSV_PATH = "data/raw/data_dictionary.csv"
    VECTORSTORE_DIR = "data/vectorstore"
    
    # Enhanced test queries
    TEST_QUERIES = [
        "What is CTR and how is it calculated?",
        "How do I find user information?",
        "Show me conversion metrics",
        "What tables depend on ad_impressions?",
        "Which tables refresh hourly?",
        "Give me a sample query for conversions"
    ]
    
    # Check if CSV exists
    if not os.path.exists(CSV_PATH):
        print(f"❌ Error: CSV file not found at {CSV_PATH}")
        print("Please create the data dictionary CSV first.")
        return
    
    # Load data dictionary
    documents = load_data_dictionary(CSV_PATH)
    
    # Create vector store
    vectorstore = create_vectorstore(documents, VECTORSTORE_DIR)
    
    # Test retrieval
    test_retrieval(vectorstore, TEST_QUERIES)
    
    print("\n" + "="*60)
    print("✅ Ingestion complete!")
    print("="*60)
    print(f"📊 Total entries indexed: {len(documents)}")
    print(f"💾 Vector store location: {VECTORSTORE_DIR}")
    print("\n👉 Next step: Run 'python backend/rag_agent.py' to test queries")


if __name__ == "__main__":
    main()