
import json
import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

from fs_tools import read_file, list_files, write_file, search_in_file

load_dotenv()

API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL = os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini")

if not API_KEY:
    raise RuntimeError(
        "Missing OPENROUTER_API_KEY. Add it to your .env file."
    )

client = OpenAI(
    api_key=API_KEY,
    base_url="https://openrouter.ai/api/v1",
)

# Keep file operations inside this project's folder.
PROJECT_ROOT = Path(__file__).resolve().parent


def safe_path(filepath: str) -> str:
    """Prevent tool requests from accessing files outside this project."""
    path = (PROJECT_ROOT / filepath).resolve()
    if not path.is_relative_to(PROJECT_ROOT):
        raise ValueError("File access outside the project is not allowed")
    return str(path)


def run_tool(name: str, args: dict):
    """Execute the tool selected by the LLM."""
    if name == "read_file":
        return read_file(safe_path(args["filepath"]))
    if name == "list_files":
        return list_files(
            safe_path(args["directory"]),
            args.get("extension"),
        )
    if name == "write_file":
        return write_file(
            safe_path(args["filepath"]),
            args["content"],
        )
    if name == "search_in_file":
        return search_in_file(
            safe_path(args["filepath"]),
            args["keyword"],
        )
    return {"success": False, "error": "Unknown tool"}


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read a TXT, PDF, or DOCX resume.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filepath": {"type": "string"}
                },
                "required": ["filepath"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "List files in a project directory, optionally filtered by extension.",
            "parameters": {
                "type": "object",
                "properties": {
                    "directory": {"type": "string"},
                    "extension": {"type": ["string", "null"]},
                },
                "required": ["directory", "extension"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Write a text file and create missing directories.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filepath": {"type": "string"},
                    "content": {"type": "string"},
                },
                "required": ["filepath", "content"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_in_file",
            "description": "Search a resume for a keyword, ignoring case, and return matching context.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filepath": {"type": "string"},
                    "keyword": {"type": "string"},
                },
                "required": ["filepath", "keyword"],
                "additionalProperties": False,
            },
        },
    },
]


def ask_assistant(question: str) -> str:
    """Let the LLM choose tools, execute them, and produce a final answer."""
    messages = [
        {
            "role": "system",
            "content": (
                "You are a resume file assistant. Use the available tools "
                "to read, list, search, or create files when needed. "
                "The resumes folder is named 'resumes'. "

                "For a request to find resumes mentioning a skill, list the "
                "files in resumes and search each supported resume file. "

                "For keyword searches, use search_in_file for every resume "
                "being checked. Include a resume as a keyword match only "
                "when search_in_file returns match_count greater than zero. "
                "Report the actual matched keyword and context returned by "
                "the tool. Never invent matches or match counts. If the "
                "match_count is zero, state that the keyword was not found. "

                "Summarize tool results accurately. Never claim an action "
                "succeeded unless the tool result confirms it."
            ),
        },
        {"role": "user", "content": question},
    ]

    for _ in range(10):
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
            temperature=0,
            max_tokens=1200,
        )

        message = response.choices[0].message
        messages.append(message)

        if not message.tool_calls:
            return message.content or "The model returned an empty answer."

        for call in message.tool_calls:
            name = call.function.name
            try:
                args = json.loads(call.function.arguments)
                print(f"\nCalling tool: {name}({args})")
                result = run_tool(name, args)
            except Exception as e:
                result = {"success": False, "error": str(e)}

            messages.append({
                "role": "tool",
                "tool_call_id": call.id,
                "content": json.dumps(result, ensure_ascii=False),
            })

    return "Stopped after 10 tool-calling rounds. Please try a narrower request."


if __name__ == "__main__":
    print("LLM File Assistant. Type 'exit' to quit.")
    while True:
        question = input("\nYou: ").strip()
        if question.lower() in {"exit", "quit"}:
            break
        if question:
            try:
                print("\nAssistant:", ask_assistant(question))
            except Exception as e:
                print(f"\nError: {e}")