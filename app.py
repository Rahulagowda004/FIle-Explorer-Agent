import os
import asyncio
from dotenv import load_dotenv
from openai import OpenAI
import streamlit as st
from langchain_openai import AzureChatOpenAI
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langgraph.checkpoint.memory import InMemorySaver
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent

# Load environment variables
load_dotenv()

# Page config
st.set_page_config(
    page_title="File Handler Assistant",
    page_icon="📁",
    layout="wide"
)

st.title("📁 File Handler Assistant")
st.caption("🤖 Powered by Azure OpenAI • File operations made simple")

# Sidebar with information
with st.sidebar:
    st.header("🛠️ Available Tools")
    
    st.info("📋 **List Files** - Browse directory contents")
    st.info("📖 **Read Files** - View file contents") 
    st.info("🗑️ **Remove Files** - Delete files safely")
    st.info("✏️ **Write Files** - Create or edit files")
    st.info("⚡ **Quick Search** - Fast search in common folders")
    st.info("🔍 **Drive Search** - Deep search with limits")
    st.info("📊 **File Operations** - Copy, rename, backup, compare files")
    
    st.header("💡 Example Commands")
    
    st.code("List files in current directory")
    st.code("Quick search for 'config'")
    st.code("Find .py files in Documents")
    st.code("Search for folders named 'project'")
    st.code("Find large files over 50MB")
    
    st.divider()
    
    st.success("✅ Azure OpenAI Connected")
    st.success("✅ MCP Server Ready") 
    st.success("⚡ Fast Search Available")

# Initialize Azure OpenAI client and MCP tools
@st.cache_resource
def initialize_agent():
    """Initialize the Azure OpenAI client and MCP agent"""
    try:
        # Set up Azure OpenAI LLM
        llm = AzureChatOpenAI(
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            azure_deployment=os.getenv("AZURE_OPENAI_LLM_DEPLOYMENT"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        )
        
        # Set up MCP server parameters
        server_params = StdioServerParameters(
            command="python",
            args=[os.path.join(os.getcwd(), "servers", "filehandler.py")],
            transport="stdio",
        )
        
        checkpointer = InMemorySaver()
        
        return llm, server_params, checkpointer
    except Exception as e:
        st.error(f"Failed to initialize agent: {str(e)}")
        return None, None, None

# Async function to get agent response
async def get_agent_response(user_input, llm, server_params, checkpointer):
    """Get response from the MCP agent"""
    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                # Initialize the connection
                await session.initialize()
                
                # Get tools
                tools = await load_mcp_tools(session)
                
                # Create and run the agent
                agent = create_react_agent(llm, tools, checkpointer=checkpointer)
                
                # Add required config for checkpointer
                config = {"configurable": {"thread_id": "default"}}
                response = await agent.ainvoke({"messages": user_input}, config=config)
                
                return response['messages'][-1].content
    except Exception as e:
        return f"Error: {str(e)}"

# Initialize the agent
llm, server_params, checkpointer = initialize_agent()

if llm is None:
    st.error("🚨 Failed to initialize Azure OpenAI. Please check your .env configuration.")
    st.stop()

# Initialize chat messages
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {
            "role": "assistant", 
            "content": "👋 Hello! I'm your file handler assistant. I can help you list, read, and manage files. What would you like to do?"
        }
    ]

# Display chat messages with better styling
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# Chat input and response handling
if prompt := st.chat_input("Ask me to help with your files..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)
    
    # Get response from MCP agent
    with st.chat_message("assistant"):
        with st.spinner("Processing your request..."):
            try:
                # Run the async function
                response = asyncio.run(get_agent_response(prompt, llm, server_params, checkpointer))
                
                # Display response
                st.write(response)
                
                # Add assistant response to chat history
                st.session_state.messages.append({"role": "assistant", "content": response})
                
            except Exception as e:
                error_msg = f"Sorry, I encountered an error: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})