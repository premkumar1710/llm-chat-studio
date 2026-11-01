# LLM Chat Studio — Ollama Edition

A local LLM chat app using Python, Streamlit, and Ollama. No OpenAI API key or cloud API billing is required.

## Setup (Windows)

1. Install Ollama from https://ollama.com/download and open the Ollama app.
2. In PowerShell or the VS Code terminal, download a model:
   ```powershell
   ollama pull llama3.2:3b
   ```
3. Check the model is installed:
   ```powershell
   ollama list
   ```
4. Open this folder in VS Code.
5. Install dependencies:
   ```powershell
   python -m pip install -r requirements.txt
   ```
6. Run:
   ```powershell
   python -m streamlit run app.py
   ```
7. Open http://localhost:8501 if the browser does not open automatically.

## Features

- Local Ollama model selection
- Conversation history
- System prompt and custom instructions
- Temperature and maximum response-token controls
- JSON response mode
- Connection, missing-model, and timeout error handling
- Input/output token counts and response-time tracking
- Download chat history as JSON and performance logs as CSV

## How it works

Streamlit UI → Python requests → Ollama local API at `http://localhost:11434/api/chat` → locally installed model.

Internet is needed initially to install Ollama and download the model. After that, model inference can run offline. Performance depends on your computer's RAM, CPU/GPU, and model size.

## Troubleshooting

- Connection error: open the Ollama desktop app. If needed, run `ollama serve`.
- Model missing: run `ollama pull llama3.2:3b`, then click Refresh models.
- Slow response: try a smaller model or reduce maximum response tokens.

## Suggested resume entry

**Local LLM Chat Application | Python, Streamlit, Ollama**
- Developed a local AI chatbot by integrating Ollama's HTTP API with an interactive Streamlit interface.
- Implemented conversation history, configurable system prompts, model parameters, and structured JSON response mode.
- Added API error handling, token-usage monitoring, response-time tracking, and downloadable chat logs.
