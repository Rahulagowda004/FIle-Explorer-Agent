import os
import asyncio
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
import aiosqlite


load_dotenv()

llm = AzureChatOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    azure_deployment=os.getenv("AZURE_OPENAI_LLM_DEPLOYMENT"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
)

server_params = StdioServerParameters(
    command="python",
    args=["C:/vscode/folder-Agent/servers/filehandler.py"],
    transport="stdio",
)

async def main():
    # Create async checkpointer
    db_path = "chatbot.db"
    async with AsyncSqliteSaver.from_conn_string(db_path) as checkpointer:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                # Initialize the connection
                await session.initialize()

                # Get tools
                tools = await load_mcp_tools(session)

                # Create and run the agent
                agent = create_react_agent(llm, tools, checkpointer=checkpointer)
                
                while True:
                    user_input = input("Enter your command (or 'exit' to quit): ")
                    if user_input.lower() == 'exit':
                        break
                    
                    # Add required config for checkpointer
                    config = {"configurable": {"thread_id": "default"}}
                    response = await agent.ainvoke({"messages": user_input}, config=config)
                    print(f"Agent: {response['messages'][-1].content}")
            
if __name__ == "__main__":
    asyncio.run(main())
