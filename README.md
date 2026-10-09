
# LLM File Assistant

A Python application that uses an LLM to select and call file-system
tools for working with resume documents.

## Features

- Read TXT, PDF, and DOCX files
- List files with optional extension filtering
- Write text files and create directories
- Search resume text case-insensitively with surrounding context
- Use OpenRouter and the OpenAI SDK for LLM tool calling
- Return file metadata and handle common errors

## Requirements

Python 3.12 or later, an OpenRouter API key, and a model
that supports tool calling.

## Setup

1. Create and activate a virtual environment.
2. Install dependencies:

   `python -m pip install -r requirements.txt`

3. Create `.env` in the project root:

   `OPENROUTER_API_KEY=your_key_here`

   `OPENROUTER_MODEL=openai/gpt-4o-mini`

4. Run the assistant:

   `python llm_file_assistant.py`

## Example requests

- List all resumes in the resumes folder.
- Find resumes mentioning Python experience.
- Read resumes/john_doe.txt.
- Create a summary file for resumes/john_doe.txt.

## File tools

- `read_file(filepath)`
- `list_files(directory, extension=None)`
- `write_file(filepath, content)`
- `search_in_file(filepath, keyword)`

## Limitations

PDF text extraction does not perform OCR on scanned documents.
The assistant restricts file operations to the project directory.
LLM availability depends on the configured provider, model, and account.

## Sample data

The resumes folder contains dummy resume data for testing.