import streamlit as st
import requests
import json
import os
from typing import Dict, Any

# Environment-aware configuration
ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')
if ENVIRONMENT == 'production':
    API_BASE_URL = os.getenv('API_URL', "http://api:8000")  # Internal Docker network
    PAGE_TITLE = "RAG Knowledge Base - Production"
    PAGE_ICON = "🏭"
else:
    API_BASE_URL = os.getenv('API_URL', "http://localhost:8080")
    PAGE_TITLE = "RAG Knowledge Base - Development"
    PAGE_ICON = "🔧"

st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon=PAGE_ICON,
    layout="wide"
)


def ingest_url(url: str) -> Dict[str, Any]:
    """Submit URL for ingestion"""
    # working_endpoint = get_working_api_endpoint()
    working_endpoint = API_BASE_URL
    try:
        response = requests.post(
            f"{working_endpoint}/api/ingest-url",
            json={"url": url},
            timeout=30
        )
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"API returned status {response.status_code}: {response.text}"}
    except requests.exceptions.RequestException as e:
        return {"error": f"Connection error: {str(e)}"}

def query_knowledge_base(question: str) -> Dict[str, Any]:
    """Query the knowledge base"""
    # working_endpoint = get_working_api_endpoint()
    working_endpoint = API_BASE_URL
    try:
        response = requests.post(
            f"{working_endpoint}/api/query",
            json={"query": question},
            timeout=50
        )
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"API returned status {response.status_code}: {response.text}"}
    except requests.exceptions.RequestException as e:
        return {"error": f"Connection error: {str(e)}"}

def check_health() -> Dict[str, Any]:
    """Check API health with multiple endpoint attempts"""
    endpoints_to_try = [
        API_BASE_URL,
        "http://localhost:8000",
        "http://localhost:8001"  # Production port
    ]
    
    for endpoint in endpoints_to_try:
        try:
            response = requests.get(f"{endpoint}/health", timeout=5)
            if response.status_code == 200:
                return {
                    "success": True, 
                    "data": response.json(),
                    "endpoint": endpoint
                }
        except Exception:
            continue
    
    return {
        "success": False, 
        "error": f"Could not connect to API. Tried: {', '.join(endpoints_to_try)}"
    }

def main():
    # Header with environment indicator
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title(f"Ask Questions to Web Content")
    with col2:
        if ENVIRONMENT == 'production':
            st.success("🏭  Production")
        else:
            st.info("🔧  Development")
    
    # st.markdown(f"**Environment:** {ENVIRONMENT.title()}")
    st.markdown("---")

    # Sidebar for system status
    with st.sidebar:
        st.header("System Status")
        
        # Auto-check health on load
        health = check_health()
        if health["success"]:
            data = health["data"]
            working_endpoint = health.get("endpoint", API_BASE_URL)
            st.success("Server Connected")
            st.info(f"**Endpoint:** {working_endpoint}")
            
            # Show API status details
            with st.expander("API Details"):
                st.json(data)
        else:
            st.error("❌ API Disconnected")
            st.error(health['error'])
            st.warning("Please start the API server")
        
        if st.button("🔄 Refresh Status"):
            st.rerun()

    # Initialize session state for ingestion tracking
    if 'ingesting' not in st.session_state:
        st.session_state.ingesting = False
    if 'last_ingested_url' not in st.session_state:
        st.session_state.last_ingested_url = None
    if 'ingestion_complete' not in st.session_state:
        st.session_state.ingestion_complete = False

    # Grid layout with two columns
    col1, col2 = st.columns([1, 1], gap="large")

    # Left column - URL Ingestion
    with col1:
        st.markdown("#### 📥  Ingest URLs")
        
        url_input = st.text_input(
            "Enter a URL to fetch and process its content into the knowledge base.:",
            placeholder="https://example.com/article",
            key="url_input"
        )
        
        if st.button("🚀 Ingest URL", type="primary", key="ingest_btn"):
            if url_input:
                st.session_state.ingesting = True
                st.session_state.ingestion_complete = False
                st.session_state.last_ingested_url = url_input
                
                with st.spinner("Processing URL..."):
                    result = ingest_url(url_input)
                
                if "error" in result:
                    st.error(f"Error: {result['error']}")
                    st.session_state.ingesting = False
                else:
                    st.success("✅ URL submitted for processing!")
                    st.info("⏳ Content is being processed in the background...")
                    st.info(result.get("message", ""))
                    # st.json(result)
                    
                    # # Simulate processing completion (in real app, you'd check task status)

                    st.session_state.ingesting = False
                    st.session_state.ingestion_complete = True

                    if(result.get("message") != "Processed Earlier & Unchanged"):
                        # import time
                        # time.sleep(2)
                        st.success("🎉 Content ingested successfully! You can now ask questions.")

                    # st.rerun()
            else:
                st.warning("Please enter a URL")
        
        # Show ingestion status
        if st.session_state.ingesting:
            st.warning("🔄 Processing URL... Please wait.")
        # elif st.session_state.ingestion_complete and st.session_state.last_ingested_url:
        #     st.success(f"✅ Last ingested: {st.session_state.last_ingested_url}")

    # Right column - Query Knowledge Base
    with col2:
        st.markdown("#### ❓ Query Knowledge")
        
        # Disable querying if ingestion is in progress
        query_disabled = st.session_state.ingesting
        
        if query_disabled:
            st.warning("🚫 Querying disabled while URL is being processed")
            st.info("Please wait for ingestion to complete before asking questions.")
        elif st.session_state.ingestion_complete:
            st.success("✅ Ready to answer questions!")
        
        question_input = st.text_area(
            "Ask question from the knowledge base:",
            placeholder="What is the main topic of the ingested content?",
            height=100,
            disabled=query_disabled,
            key="question_input"
        )
        
        query_button = st.button(
            "🔍 Ask Question", 
            type="primary", 
            disabled=query_disabled,
            key="query_btn"
        )
        
        if query_button and not query_disabled:
            if question_input:
                with st.spinner("Generating answer..."):
                    result = query_knowledge_base(question_input)
                
                if "error" in result:
                    st.error(f"Error: {result['error']}")
                else:
                    st.success("Answer generated!")
                    
                    # Display answer
                    if "answer" in result:
                        st.markdown("### 📝 Answer")
                        st.markdown(result["answer"])
                    
                    # Display sources if available
                    if "sources" in result and result["sources"]:
                        st.markdown("### 📚 Sources")
                        for i, source in enumerate(result["sources"], 1):
                            if isinstance(source, dict):
                                url = source.get("url", "Unknown URL")
                                preview = source.get("content_preview", "No preview available")
                                score = source.get("relevance_score", "N/A")
                                
                                st.markdown(f"**Source {i}:** {url}")
                                st.markdown(f"*Relevance: {score}*")
                                st.markdown(f"Preview: {preview}")
                                st.markdown("---")
                            else:
                                st.markdown(f"- {source}")
                    
                    # Display full response
                    with st.expander("🔍 Full Response"):
                        st.json(result)
            else:
                st.warning("Please enter a question")

    # Footer
    st.markdown("---")
    # working_endpoint = get_working_api_endpoint()
    working_endpoint = API_BASE_URL
    st.markdown(f"**Environment:** {ENVIRONMENT.title()} | **API:** {working_endpoint}")
    
    # Show connection status in footer
    try:
        response = requests.get(f"{working_endpoint}/health", timeout=2)
        if response.status_code == 200:
            st.success("🟢 API Online")
        else:
            st.error("🔴 API Error")
    except:
        st.error("🔴 API Offline")

if __name__ == "__main__":
    main()
