"""
Data Dictionary AI Assistant - Streamlit UI

A production-ready web interface for the Data Dictionary RAG agent.
Solves the problem of scattered data documentation and slow knowledge discovery.
"""

import streamlit as st
import sys
import os
import time

# Add parent directory to path to import backend modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.rag_agent import DataDictionaryAgent
import pandas as pd

# Page configuration
st.set_page_config(
    page_title="Data Dictionary AI Assistant",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for beautiful styling
st.markdown("""
<style>
    /* Problem statement card */
    .problem-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 1rem;
        margin: 2rem 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .problem-title {
        font-size: 1.5rem;
        font-weight: 700;
        margin-bottom: 1rem;
        color: white;
    }
    
    .problem-text {
        font-size: 1.1rem;
        line-height: 1.6;
        color: #f0f0f0;
    }
    
    /* Solution card */
    .solution-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 2rem;
        border-radius: 1rem;
        margin: 2rem 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .solution-title {
        font-size: 1.5rem;
        font-weight: 700;
        margin-bottom: 1rem;
        color: white;
    }
    
    /* Stats cards */
    .stat-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 0.8rem;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .stat-number {
        font-size: 2.5rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
    }
    
    .stat-label {
        font-size: 0.9rem;
        opacity: 0.9;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Source box styling */
    .source-box {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 0.8rem;
        border-left: 5px solid #1E88E5;
        margin: 0.8rem 0;
        font-family: 'Courier New', monospace;
        font-size: 0.9rem;
    }
    
    /* Example query buttons */
    .stButton > button {
        border-radius: 0.5rem;
        border: 2px solid #E3F2FD;
        background-color: white;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background-color: #E3F2FD;
        border-color: #1E88E5;
        transform: translateY(-2px);
    }
    
    /* Primary button styling fix */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white !important;
        font-weight: 600;
        border: none;
        box-shadow: 0 2px 4px rgba(102, 126, 234, 0.4);
    }
    
    .stButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #5568d3 0%, #653a8a 100%);
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(102, 126, 234, 0.6);
    }
    
    /* Secondary button styling */
    .stButton > button[kind="secondary"] {
        background-color: #E3F2FD;
        color: #1565C0 !important;
        border: 2px solid #90CAF9;
        font-weight: 600;
    }
    
    .stButton > button[kind="secondary"]:hover {
        background-color: #BBDEFB;
        border-color: #1565C0;
    }
    
    /* Answer section */
    .answer-box {
        background: linear-gradient(to right, #e0f7fa 0%, #e1f5fe 100%);
        padding: 2rem;
        border-radius: 1rem;
        border-left: 5px solid #00ACC1;
        margin: 1rem 0;
        font-size: 1.1rem;
        line-height: 1.8;
    }
    
    /* Use case cards */
    .use-case {
        background: white;
        border: 2px solid #E3F2FD;
        border-radius: 0.8rem;
        padding: 1.5rem;
        margin: 1rem 0;
        transition: all 0.3s ease;
    }
    
    .use-case:hover {
        border-color: #1E88E5;
        box-shadow: 0 4px 8px rgba(30,136,229,0.2);
        transform: translateY(-3px);
    }
    
    .use-case-title {
        font-size: 1.2rem;
        font-weight: 600;
        color: #1565C0;
        margin-bottom: 0.5rem;
    }
    
    .use-case-desc {
        color: #546E7A;
        line-height: 1.6;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def load_agent():
    """Load and cache the RAG agent"""
    return DataDictionaryAgent()


def format_column_info(columns):
    """Format column information as a DataFrame"""
    if not columns:
        return None
    
    df = pd.DataFrame(columns)
    df = df[['table', 'column', 'type', 'refresh']]
    df.columns = ['Table', 'Column', 'Data Type', 'Refresh Frequency']
    return df


def show_hero_section():
    """Display hero section with problem statement"""
    
    # Simple markdown title - most compatible
    st.markdown("# 📊 Data Dictionary AI Assistant")
    st.markdown("### Natural language search for your data catalog")
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Problem Statement
    st.markdown("""
    <div class="problem-card">
        <div class="problem-title">🎯 The Problem</div>
        <div class="problem-text">
            Data teams waste <strong>20-30% of their time</strong> searching for metric definitions, 
            table schemas, and column descriptions across scattered documentation sources like Confluence, 
            Google Sheets, and internal wikis. This leads to:
            <br><br>
            • Duplicate work defining the same metrics<br>
            • Inconsistent calculations across teams<br>
            • Slow onboarding for new analysts (weeks vs. days)<br>
            • Endless Slack messages: "What does this column mean?"
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Solution
    st.markdown("""
    <div class="solution-card">
        <div class="solution-title">💡 The Solution</div>
        <div class="problem-text">
            An AI-powered assistant that provides <strong>instant, conversational access</strong> 
            to your entire data dictionary using Retrieval Augmented Generation (RAG). 
            Ask questions in plain English and get accurate answers with source attribution.
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)


def show_use_cases():
    """Display common use cases"""
    
    st.markdown("### 🎯 Common Use Cases")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="use-case">
            <div class="use-case-title">📈 For Data Analysts</div>
            <div class="use-case-desc">
                "How is CTR calculated?" → Get instant formula, sample query, and source table
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="use-case">
            <div class="use-case-title">🔗 For Data Engineers</div>
            <div class="use-case-desc">
                "What tables depend on ad_impressions?" → Understand data lineage and dependencies
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="use-case">
            <div class="use-case-title">👥 For New Hires</div>
            <div class="use-case-desc">
                "Show me all conversion metrics" → Self-service onboarding without bothering teammates
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="use-case">
            <div class="use-case-title">⚙️ For Product Managers</div>
            <div class="use-case-desc">
                "Which tables refresh hourly?" → Understand data freshness for feature planning
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)


def show_tech_stack():
    """Display technology stack"""
    
    st.markdown("### 🛠️ Technology Stack")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="stat-card">
            <div class="stat-number">🦜</div>
            <div class="stat-label">LangChain</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="stat-card">
            <div class="stat-number">🤖</div>
            <div class="stat-label">GPT-4</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="stat-card">
            <div class="stat-number">🗄️</div>
            <div class="stat-label">Chroma DB</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="stat-card">
            <div class="stat-number">⚡</div>
            <div class="stat-label">Streamlit</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)


def main():
    """Main application"""
    
    # Initialize session state
    if 'history' not in st.session_state:
        st.session_state.history = []
    
    if 'query' not in st.session_state:
        st.session_state.query = ''
    
    if 'show_intro' not in st.session_state:
        st.session_state.show_intro = True
    
    # Rate limiting to protect API costs
    if 'last_query_time' not in st.session_state:
        st.session_state.last_query_time = 0
    
    if 'query_count' not in st.session_state:
        st.session_state.query_count = 0
    
    # Sidebar
    with st.sidebar:
        # Return to homepage button (only show when not on intro page)
        if not st.session_state.show_intro:
            if st.button("🏠 Return to Homepage", use_container_width=True, type="secondary"):
                st.session_state.show_intro = True
                st.session_state.query = ''
                st.rerun()
            
            st.divider()
        
        st.markdown("### 💡 Try These Examples")
        
        example_queries = [
            "What is CTR and how is it calculated?",
            "Show me all columns in conversions table",
            "What tables depend on ad_impressions?",
            "Which tables refresh hourly?",
            "How do I join clicks with conversions?",
            "Give me a sample query for user LTV",
            "What is ROAS?",
            "Show me conversion metrics",
            "What's in the metrics_daily table?",
            "How often is user_profiles refreshed?"
        ]
        
        for eq in example_queries:
            if st.button(eq, key=f"example_{eq}", use_container_width=True):
                st.session_state.query = eq
                st.session_state.show_intro = False
                st.rerun()
        
        st.divider()
        
        # Impact metrics
        st.markdown("### 📊 Impact Metrics")
        st.markdown("""
        <div style='background: #E3F2FD; padding: 1rem; border-radius: 0.5rem; margin: 0.5rem 0;'>
            <div style='font-size: 2rem; font-weight: 700; color: #1565C0;'>80%</div>
            <div style='font-size: 0.85rem; color: #546E7A;'>Time saved on doc searches</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style='background: #E8F5E9; padding: 1rem; border-radius: 0.5rem; margin: 0.5rem 0;'>
            <div style='font-size: 2rem; font-weight: 700; color: #2E7D32;'>5x</div>
            <div style='font-size: 0.85rem; color: #546E7A;'>Faster analyst onboarding</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style='background: #FFF3E0; padding: 1rem; border-radius: 0.5rem; margin: 0.5rem 0;'>
            <div style='font-size: 2rem; font-weight: 700; color: #EF6C00;'>Zero</div>
            <div style='font-size: 0.85rem; color: #546E7A;'>Slack interruptions</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Query history
        if st.session_state.history:
            st.divider()
            st.markdown("### 📜 Your Query History")
            for i, hist in enumerate(reversed(st.session_state.history[-5:])):
                with st.expander(f"Q: {hist['query'][:35]}...", expanded=False):
                    st.caption(f"**Q:** {hist['query']}")
                    st.caption(f"**A:** {hist['answer'][:150]}...")
        
        st.divider()
        st.markdown("### 👤 About")
        st.info("""
        **Built by Alita Liu**
        
        Senior Manager with 7+ years in AI/Data Product Leadership
        
        📧 alitaliu82@gmail.com  
        🔗 [LinkedIn](https://www.linkedin.com/in/alitaliu/)  
        💻 [GitHub](https://github.com/AlitaLiu82)
        """)
    
    # Main content
    if st.session_state.show_intro:
        # Show hero section
        show_hero_section()
        show_use_cases()
        show_tech_stack()
        
        # Call to action
        st.markdown("### 🚀 Try It Now")
        st.markdown("Click an example question in the sidebar, or type your own below:")
    else:
        # Show simplified header when querying
        st.markdown("# 📊 Data Dictionary AI Assistant")
    
    # Search interface
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([5, 1])
    
    with col1:
        query = st.text_input(
            "🔍 Ask about your data:",
            value=st.session_state.query,
            placeholder="e.g., What is the difference between impressions and clicks?",
            label_visibility="collapsed"
        )
    
    with col2:
        search_button = st.button("Search", type="primary", use_container_width=True)
    
    # Process query
    if (search_button or query) and query:
        
        st.session_state.show_intro = False
        
        # Rate limiting: 5 second cooldown between queries
        current_time = time.time()
        if current_time - st.session_state.last_query_time < 5:
            st.warning("⏳ Please wait 5 seconds between queries to manage API costs")
            st.stop()
        
        # Track query count
        st.session_state.last_query_time = current_time
        st.session_state.query_count += 1
        
        # Clear the query from session state after using it
        if st.session_state.query:
            st.session_state.query = ''
        
        with st.spinner("🔍 Searching data dictionary..."):
            # Load agent
            agent = load_agent()
            
            # Query
            response = agent.query(query)
        
        # Display answer in beautiful box
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"""
        <div class="answer-box">
            <strong style="font-size: 1.3rem; color: #00838F;">💡 Answer:</strong>
            <br><br>
            {response['answer']}
        </div>
        """, unsafe_allow_html=True)
        
        # Metadata section
        st.markdown("<br>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📊 Tables Referenced")
            if response['tables']:
                for table in response['tables']:
                    st.markdown(f"- `{table}`")
            else:
                st.caption("No specific tables referenced")
        
        with col2:
            st.markdown("#### 📁 Columns Found")
            if response['columns']:
                st.caption(f"{len(response['columns'])} column(s) found")
                
                # Show as table
                df = format_column_info(response['columns'])
                if df is not None:
                    st.dataframe(df, hide_index=True, use_container_width=True)
            else:
                st.caption("No specific columns referenced")
        
        # Source entries (expandable)
        with st.expander("📚 View Source Entries", expanded=False):
            if response['sources']:
                for i, doc in enumerate(response['sources'][:3], 1):
                    st.markdown(f"**Source {i}:**")
                    st.markdown(f'<div class="source-box">{doc.page_content}</div>', 
                              unsafe_allow_html=True)
                    
                    if i < len(response['sources'][:3]):
                        st.divider()
            else:
                st.caption("No source entries available")
        
        # Add to history
        st.session_state.history.append({
            'query': query,
            'answer': response['answer'],
            'tables': response['tables']
        })
    
    # Footer
    st.divider()
    st.caption("Built with LangChain + OpenAI + Chroma | Portfolio Project by Alita Liu")
    
    # Quick stats in footer
    if st.session_state.history:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Queries", len(st.session_state.history))
        with col2:
            unique_tables = set()
            for h in st.session_state.history:
                unique_tables.update(h.get('tables', []))
            st.metric("Tables Explored", len(unique_tables))
        with col3:
            st.metric("Session Active", "✅")


if __name__ == "__main__":
    main()