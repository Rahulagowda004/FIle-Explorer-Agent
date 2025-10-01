# 🤖 File Explorer Agent

A sophisticated AI-powered file management assistant built with Streamlit, LangChain, and MCP (Model Context Protocol). This application provides an intelligent chat interface for interacting with your file system using natural language commands.

## ✨ Features

- **🗣️ Natural Language File Operations**: Interact with your file system using conversational commands
- **💬 Multi-Session Chat**: Create and manage multiple chat sessions for different tasks
- **🔧 MCP Integration**: Leverages Model Context Protocol for seamless tool integration
- **🧠 AI-Powered**: Uses Azure OpenAI for intelligent responses and file operations
- **💾 Persistent Sessions**: Chat history is saved and can be resumed across application restarts
- **🔄 Real-time Operations**: Asynchronous operations for better performance

## 🛠️ Core Capabilities

The File Explorer Agent can help you with:

- File and directory creation, deletion, and modification
- File search and content analysis
- Directory navigation and exploration
- File copying, moving, and renaming
- Content reading and writing operations
- System information and file metadata retrieval

## 🏗️ Architecture

### Components

1. **Streamlit Frontend** (`app.py`): Interactive web interface with session management
2. **MCP File Handler Server** (`servers/filehandler.py`): Backend server handling file operations
3. **LangChain Integration**: Orchestrates AI responses and tool usage
4. **SQLite Databases**: Stores chat sessions and conversation history

### Technology Stack

- **Frontend**: Streamlit
- **AI/LLM**: Azure OpenAI with LangChain
- **Tool Integration**: Model Context Protocol (MCP)
- **Database**: SQLite (async)
- **Package Management**: UV

## 📋 Prerequisites

- Python 3.12 or higher
- Azure OpenAI API access
- UV package manager (recommended) or pip

## 🚀 Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd folder-Agent
   ```

2. **Install dependencies**:
   ```bash
   # Using UV (recommended)
   uv sync

   # Or using pip
   pip install -r requirements.txt
   ```

3. **Environment Setup**:
   Create a `.env` file in the project root with your Azure OpenAI credentials:
   ```env
   AZURE_OPENAI_ENDPOINT=your_azure_endpoint
   AZURE_OPENAI_LLM_DEPLOYMENT=your_deployment_name
   AZURE_OPENAI_API_VERSION=your_api_version
   AZURE_OPENAI_API_KEY=your_api_key
   ```

## 🎯 Usage

### Starting the Application

**Option 1: Using the batch file (Windows)**:
```bash
run_app.bat
```

**Option 2: Using UV**:
```bash
uv run streamlit run app.py
```

**Option 3: Using Python directly**:
```bash
streamlit run app.py
```

### Using the Interface

1. **Create a New Session**: Click "➕ New Session" in the sidebar
2. **Select a Session**: Click on any existing session to continue the conversation
3. **Chat with the Agent**: Type natural language commands in the chat input
4. **Manage Sessions**: Use the 🗑️ button to delete unwanted sessions

### Example Commands

```
"Show me all Python files in the current directory"
"Create a new folder called 'projects'"
"Copy all .txt files to the backup folder"
"What's the size of the app.py file?"
"Delete the temporary files in the temp directory"
"Search for files containing 'config' in their name"
```

## 📁 Project Structure

```
folder-Agent/
├── app.py                 # Main Streamlit application
├── main.py               # Entry point (minimal)
├── pyproject.toml        # Project configuration and dependencies
├── run_app.bat          # Windows batch file to start the app
├── servers/
│   └── filehandler.py   # MCP server for file operations
├── chatbot.db           # SQLite database for chat history
├── sessions.db          # SQLite database for session management
├── .env                 # Environment variables (not tracked)
└── README.md           # This file
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `AZURE_OPENAI_ENDPOINT` | Azure OpenAI service endpoint | Yes |
| `AZURE_OPENAI_LLM_DEPLOYMENT` | Deployment name for your model | Yes |
| `AZURE_OPENAI_API_VERSION` | API version (e.g., 2024-02-15-preview) | Yes |
| `AZURE_OPENAI_API_KEY` | Your Azure OpenAI API key | Yes |

### File Handler Server

The MCP file handler server (`servers/filehandler.py`) provides the following capabilities:
- File system operations (CRUD)
- Directory management
- File search and filtering
- Content analysis
- System information retrieval

## 🔍 Development

### Running in Development Mode

```bash
# Start the Streamlit app with auto-reload
uv run streamlit run app.py --reload
```

### Testing

```bash
# Run the test file
python test_filehandler.py
```

## 🐛 Troubleshooting

### Common Issues

1. **Missing Environment Variables**: Ensure all required Azure OpenAI variables are set in `.env`
2. **Permission Errors**: Make sure the application has necessary file system permissions
3. **Port Conflicts**: If port 8501 is busy, Streamlit will automatically use the next available port
4. **Database Lock**: If you encounter SQLite lock errors, ensure no other instances are running

### Logs and Debugging

- Check the Streamlit console output for error messages
- Database files (`chatbot.db`, `sessions.db`) store persistent data
- The MCP server logs can help debug file operation issues

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [Streamlit](https://streamlit.io/) for the web interface
- Powered by [LangChain](https://langchain.com/) for AI orchestration
- Uses [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) for tool integration
- Utilizes [Azure OpenAI](https://azure.microsoft.com/en-us/products/cognitive-services/openai-service/) for AI capabilities

## 🚀 Future Enhancements

- [ ] Support for additional file formats and operations
- [ ] Integration with cloud storage services
- [ ] Advanced search and filtering capabilities
- [ ] File versioning and backup features
- [ ] Multi-user support and permissions
- [ ] Plugin system for custom file handlers

---

**Need help?** Open an issue or start a discussion in the repository!