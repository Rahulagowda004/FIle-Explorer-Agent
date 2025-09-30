import os
import asyncio
import streamlit as st
from datetime import datetime
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
import aiosqlite
import sqlite3
import uuid

load_dotenv()

# Initialize session state
if "sessions" not in st.session_state:
    st.session_state.sessions = {}
if "current_session_id" not in st.session_state:
    st.session_state.current_session_id = None
if "messages" not in st.session_state:
    st.session_state.messages = {}

# Database functions for session management
def init_sessions_db():
    """Initialize the sessions database"""
    conn = sqlite3.connect("sessions.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def load_sessions():
    """Load all sessions from database"""
    conn = sqlite3.connect("sessions.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, created_at FROM sessions ORDER BY created_at DESC")
    sessions = cursor.fetchall()
    conn.close()
    return {session[0]: {"name": session[1], "created_at": session[2]} for session in sessions}

def save_session(session_id, name):
    """Save a new session to database"""
    conn = sqlite3.connect("sessions.db")
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO sessions (id, name) VALUES (?, ?)", (session_id, name))
    conn.commit()
    conn.close()

def delete_session(session_id):
    """Delete a session from database"""
    conn = sqlite3.connect("sessions.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
    conn.commit()
    conn.close()

# Initialize LLM and server parameters
@st.cache_resource
def get_llm():
    return AzureChatOpenAI(
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        azure_deployment=os.getenv("AZURE_OPENAI_LLM_DEPLOYMENT"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    )

@st.cache_resource
def get_server_params():
    return StdioServerParameters(
        command="python",
        args=["C:/vscode/folder-Agent/servers/filehandler.py"],
        transport="stdio",
    )

async def get_agent_response(user_input, session_id):
    """Get response from the agent"""
    llm = get_llm()
    server_params = get_server_params()
    
    db_path = "chatbot.db"
    async with AsyncSqliteSaver.from_conn_string(db_path) as checkpointer:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                tools = await load_mcp_tools(session)
                agent = create_react_agent(llm, tools, checkpointer=checkpointer)
                
                config = {"configurable": {"thread_id": session_id}}
                response = await agent.ainvoke({"messages": user_input}, config=config)
                return response['messages'][-1].content

def main():
    st.set_page_config(page_title="MCP Agent Chat", layout="wide")
    
    # Initialize sessions database
    init_sessions_db()
    
    # Load sessions
    st.session_state.sessions = load_sessions()
    
    # Sidebar for session management
    with st.sidebar:
        st.title("💬 Chat Sessions")
        
        # New session button
        if st.button("➕ New Session", type="primary", use_container_width=True):
            new_session_id = str(uuid.uuid4())
            session_name = f"Session {datetime.now().strftime('%m/%d %H:%M')}"
            save_session(new_session_id, session_name)
            st.session_state.sessions[new_session_id] = {
                "name": session_name, 
                "created_at": datetime.now().isoformat()
            }
            st.session_state.current_session_id = new_session_id
            st.session_state.messages[new_session_id] = []
            st.rerun()
        
        st.divider()
        
        # Display sessions
        if st.session_state.sessions:
            for session_id, session_data in st.session_state.sessions.items():
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    if st.button(
                        session_data["name"], 
                        key=f"session_{session_id}",
                        use_container_width=True,
                        type="secondary" if session_id != st.session_state.current_session_id else "primary"
                    ):
                        st.session_state.current_session_id = session_id
                        if session_id not in st.session_state.messages:
                            st.session_state.messages[session_id] = []
                        st.rerun()
                
                with col2:
                    if st.button("🗑️", key=f"delete_{session_id}", help="Delete session"):
                        delete_session(session_id)
                        if session_id in st.session_state.sessions:
                            del st.session_state.sessions[session_id]
                        if session_id in st.session_state.messages:
                            del st.session_state.messages[session_id]
                        if st.session_state.current_session_id == session_id:
                            st.session_state.current_session_id = None
                        st.rerun()
        else:
            st.info("No sessions yet. Create a new session to start chatting!")
    
    # Main chat interface
    st.title("🤖 MCP Agent Assistant")
    
    # Check if a session is selected
    if st.session_state.current_session_id is None:
        st.info("👈 Please select or create a session from the sidebar to start chatting.")
        return
    
    current_session = st.session_state.current_session_id
    
    # Initialize messages for current session if not exists
    if current_session not in st.session_state.messages:
        st.session_state.messages[current_session] = []
    
    # Display chat messages
    for message in st.session_state.messages[current_session]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Type your message here..."):
        # Add user message to chat history
        st.session_state.messages[current_session].append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get assistant response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    # Run the async function
                    response = asyncio.run(get_agent_response(prompt, current_session))
                    st.markdown(response)
                    st.session_state.messages[current_session].append({"role": "assistant", "content": response})
                except Exception as e:
                    error_msg = f"Sorry, I encountered an error: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages[current_session].append({"role": "assistant", "content": error_msg})
    
    # Session info
    if st.session_state.current_session_id:
        session_info = st.session_state.sessions.get(st.session_state.current_session_id, {})
        st.sidebar.markdown(f"**Current Session:** {session_info.get('name', 'Unknown')}")
        if session_info.get('created_at'):
            st.sidebar.markdown(f"**Created:** {session_info['created_at']}")

if __name__ == "__main__":
    main()