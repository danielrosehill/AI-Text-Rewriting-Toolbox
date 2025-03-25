# AI Text Transformer Toolbox

A Linux-based application that allows users to apply various text transformations using a local large language model (LLM) via the Ollama API.

## Features

- Two-sided interface with input and output text areas
- Multiple transformation options using pre-defined system prompts
- Integration with local LLMs via Ollama API
- Support for various input formats (TXT, Markdown, DOCX, PDF)
- Ability to save transformed text to files
- Persistent user preferences for model selection

## Installation

1. Ensure you have Python 3.8+ installed
2. Install Ollama from https://ollama.com/
3. Install required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

1. Start the application:

```bash
streamlit run app.py
```

2. Enter or upload text in the left panel
3. Select transformation options in the center panel
4. View and edit the transformed text in the right panel
5. Download the transformed text as needed

## System Requirements

- Linux operating system
- Python 3.8+
- Ollama installed and running locally
- Internet connection (for initial setup only)

## License

This project is open source and available under the MIT License.
