"""
app_ui.py
Streamlit web UI for the News GraphRAG Chatbot.
Run with: streamlit run app_ui.py
"""
import streamlit as st
import sys
import os
import pathlib

# Resolve paths relative to this script's directory
BASE_DIR = pathlib.Path(__file__).parent.resolve()
sys.path.insert(0, str(BASE_DIR))

from chatbot import ask, get_articles

# Page config
st.set_page_config(
    page_title="News GraphRAG Chatbot",
    page_icon="🌍",
    layout="wide"
)

# Sidebar
with st.sidebar:
    st.title("🌍 News Chatbot")
    st.markdown("**Powered by GraphRAG + Gemini**")
    st.divider()

    # Stats
    articles = get_articles()
    st.metric("Articles in DB", len(articles))

    st.divider()
    st.markdown("### Data Source")
    
    # 1. MongoDB / Cloud Storage check
    mongo_connected = False
    try:
        from pymongo import MongoClient
        mongo_uri = st.secrets.get("MONGO_URI", "mongodb://localhost:27017/")
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=1500)
        client.server_info()
        mongo_connected = True
        st.success("✅ MongoDB Connected")
    except Exception:
        # Clean production label instead of a warning
        st.info("📦 JSON Knowledge Base (Active)")

    # 2. Robust GraphRAG Output check (handles both Linux casing & relative paths)
    output_dir = BASE_DIR / "output"
    if not output_dir.exists():
        output_dir = BASE_DIR / "Output"

    if output_dir.exists():
        st.success("✅ GraphRAG Index Ready")
    else:
        st.warning("⚠️ GraphRAG indexing pending")

    st.divider()
    st.markdown("### 24h Refresh")
    if st.button("🔄 Refresh Data Now"):
        if not mongo_connected:
            st.info("ℹ️ Live re-syncing requires MongoDB Atlas. Serving static indexed snapshot.")
        else:
            try:
                from mongo_loader import load_json_to_mongo, export_to_txt
                load_json_to_mongo()
                export_to_txt()
                st.success("Data refreshed!")
            except Exception as e:
                st.error(f"Error: {e}")

# Main chat area
st.title("🌍 Geopolitical News Chatbot")
st.caption("Ask anything about the latest geopolitical news")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({
        "role": "assistant",
        "content": "Hello! I'm your geopolitical news analyst. Ask me anything about current world events, conflicts, diplomacy, or international relations."
    })

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat input
if prompt := st.chat_input("Ask about world news..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get response
    with st.chat_message("assistant"):
        with st.spinner("Analyzing news graph..."):
            response = ask(prompt)
        st.markdown(response)

    st.session_state.messages.append({"role": "assistant", "content": response})
