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

st.title("💬 MCP File Handler Chatbot")
st.caption("🚀 A Streamlit chatbot powered by Azure OpenAI with MCP file handling tools")

# Sidebar with information
with st.sidebar:
    st.header("Available Tools")
    st.write("This chatbot has access to the following file operations:")
    st.write("• **List files** - List files in a directory")
    st.write("• **Read file** - Read the content of a file")
    st.write("• **Remove file** - Delete a file from the filesystem")
    st.write("")
    st.write("**Example commands:**")
    st.write("- 'List files in the current directory'")
    st.write("- 'Read the content of app.py'")
    st.write("- 'Show me what files are in the servers folder'")
    st.divider()
    st.write("Configuration loaded from .env file")
    st.success("✅ Azure OpenAI configured")

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
    st.error("Failed to initialize the Azure OpenAI client. Please check your .env file configuration.")
    st.stop()
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "Hello! I'm a file handler chatbot. I can help you with file operations like reading, listing, and removing files. What would you like to do?"}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input():
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    
    # Get response from MCP agent
    with st.spinner("Processing your request..."):
        try:
            # Run the async function
            response = asyncio.run(get_agent_response(prompt, llm, server_params, checkpointer))
            
            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.chat_message("assistant").write(response)
        except Exception as e:
            error_msg = f"Sorry, I encountered an error: {str(e)}"
            st.session_state.messages.append({"role": "assistant", "content": error_msg})
            st.chat_message("assistant").write(error_msg)