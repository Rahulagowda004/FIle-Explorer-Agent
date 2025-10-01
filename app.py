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

def get_quick_commands():
    """Return categorized quick command examples"""
    return {
        "📁 File Operations": [
            "List all files in Documents folder",
            "Create a new directory called 'Projects'",
            "Copy readme.txt to backup folder",
            "Rename old_file.txt to new_file.txt"
        ],
        "🔍 Search & Find": [
            "Search for all .py files in current directory",
            "Find duplicate files in Downloads folder",
            "Search for files containing 'config' in name",
            "Find all PDF files on C drive"
        ],
        "📊 File Analysis": [
            "Get file information for document.pdf",
            "Calculate hash for important.zip",
            "Count lines in script.py",
            "Compare file1.txt with file2.txt"
        ],
        "🛠️ Maintenance": [
            "Clean up temporary files",
            "Backup important.doc",
            "Get system information",
            "Monitor Downloads directory for changes"
        ]
    }

def main():
    st.set_page_config(
        page_title="File Explorer Agent", 
        page_icon="🤖",
        layout="wide"
    )
    
    # Initialize sessions database
    init_sessions_db()
    st.session_state.sessions = load_sessions()
    
    # Sidebar
    with st.sidebar:
        st.header("💬 Chat Sessions")
        
        # New session
        if st.button("➕ New Chat", type="primary", use_container_width=True):
            new_session_id = str(uuid.uuid4())
            session_name = f"Chat {len(st.session_state.sessions) + 1}"
            save_session(new_session_id, session_name)
            st.session_state.sessions[new_session_id] = {
                "name": session_name, 
                "created_at": datetime.now().isoformat()
            }
            st.session_state.current_session_id = new_session_id
            st.session_state.messages[new_session_id] = []
            st.rerun()
        
        st.divider()
        
        # Session list
        if st.session_state.sessions:
            for session_id, session_data in st.session_state.sessions.items():
                col1, col2 = st.columns([4, 1])
                
                with col1:
                    is_current = session_id == st.session_state.current_session_id
                    button_type = "primary" if is_current else "secondary"
                    
                    if st.button(
                        session_data["name"], 
                        key=f"session_{session_id}",
                        type=button_type,
                        use_container_width=True
                    ):
                        if not is_current:
                            st.session_state.current_session_id = session_id
                            if session_id not in st.session_state.messages:
                                st.session_state.messages[session_id] = []
                            st.rerun()
                
                with col2:
                    if st.button("🗑️", key=f"delete_{session_id}"):
                        delete_session(session_id)
                        if session_id in st.session_state.sessions:
                            del st.session_state.sessions[session_id]
                        if session_id in st.session_state.messages:
                            del st.session_state.messages[session_id]
                        if st.session_state.current_session_id == session_id:
                            st.session_state.current_session_id = None
                        st.rerun()
        else:
            st.info("No chats yet. Start a new one!")
        
        # Quick reference
        st.divider()
        with st.expander("🚀 Quick Reference"):
            st.markdown("""
            **Available Operations:**
            
            📂 **File Management**
            • List, create, copy, rename
            • Read, write, append
            • Backup, delete files
            
            🔍 **Search & Analysis**
            • Find files & duplicates
            • Search content
            • File statistics & info
            
            🛠️ **System Tools**
            • System information
            • Directory monitoring
            • Temp file cleanup
            • File permissions
            """)
    
    # Main area
    st.title("🤖 File Explorer Assistant")
    st.caption("Your intelligent file management companion")
    
    if st.session_state.current_session_id is None:
        # Welcome state with quick commands
        st.markdown("### Welcome! 👋")
        st.info("🚀 Create a new chat session to start exploring and managing your files.")
        
        # Quick command examples
        st.markdown("### 💡 What can I help you with?")
        
        quick_commands = get_quick_commands()
        
        # Create tabs for different categories
        tabs = st.tabs(list(quick_commands.keys()))
        
        for i, (category, commands) in enumerate(quick_commands.items()):
            with tabs[i]:
                for cmd in commands:
                    if st.button(f"💭 {cmd}", key=f"quick_{cmd}", use_container_width=True):
                        # Create new session and use this command
                        new_session_id = str(uuid.uuid4())
                        session_name = f"Chat {len(st.session_state.sessions) + 1}"
                        save_session(new_session_id, session_name)
                        st.session_state.sessions[new_session_id] = {
                            "name": session_name, 
                            "created_at": datetime.now().isoformat()
                        }
                        st.session_state.current_session_id = new_session_id
                        st.session_state.messages[new_session_id] = [
                            {"role": "user", "content": cmd}
                        ]
                        st.rerun()
        
        # Current system info
        st.divider()
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"👤 **Current User:** ITCartofficial")
        with col2:
            st.info(f"🕐 **Current Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return
    
    current_session = st.session_state.current_session_id
    
    # Initialize messages
    if current_session not in st.session_state.messages:
        st.session_state.messages[current_session] = []
    
    # Auto-process initial message if exists
    if (len(st.session_state.messages[current_session]) == 1 and 
        st.session_state.messages[current_session][0]["role"] == "user"):
        
        initial_prompt = st.session_state.messages[current_session][0]["content"]
        
        with st.chat_message("user"):
            st.markdown(initial_prompt)
        
        with st.chat_message("assistant"):
            with st.spinner("Processing your request..."):
                try:
                    response = asyncio.run(get_agent_response(initial_prompt, current_session))
                    st.markdown(response)
                    st.session_state.messages[current_session].append({"role": "assistant", "content": response})
                except Exception as e:
                    error_msg = f"Sorry, I encountered an error: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages[current_session].append({"role": "assistant", "content": error_msg})
    else:
        # Display existing chat messages
        for message in st.session_state.messages[current_session]:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask me anything about file operations..."):
        # User message
        st.session_state.messages[current_session].append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Assistant response
        with st.chat_message("assistant"):
            with st.spinner("Processing..."):
                try:
                    response = asyncio.run(get_agent_response(prompt, current_session))
                    st.markdown(response)
                    st.session_state.messages[current_session].append({"role": "assistant", "content": response})
                except Exception as e:
                    error_msg = f"Sorry, I encountered an error: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages[current_session].append({"role": "assistant", "content": error_msg})
                 
if __name__ == "__main__":
    main()