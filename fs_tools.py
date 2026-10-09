
from pathlib import Path
from datetime import datetime
from pypdf import PdfReader
from docx import Document
import re


def read_file(filepath: str) -> dict:
    """Read TXT, PDF, or DOCX files and return text and metadata."""
    path = Path(filepath)

    if not path.is_file():
        return {"success": False, "error": f"File not found: {filepath}"}

    try:
        ext = path.suffix.lower()

        if ext == ".txt":
            content = path.read_text(encoding="utf-8")
        elif ext == ".pdf":
            reader = PdfReader(str(path))
            content = "\n".join(
                page.extract_text() or "" for page in reader.pages
            )
        elif ext == ".docx":
            doc = Document(str(path))
            content = "\n".join(p.text for p in doc.paragraphs)
        else:
            return {"success": False, "error": f"Unsupported format: {ext}"}

        stat = path.stat()
        return {
            "success": True,
            "filepath": str(path.resolve()),
            "filename": path.name,
            "extension": ext,
            "size_bytes": stat.st_size,
            "modified_date": datetime.fromtimestamp(
                stat.st_mtime
            ).isoformat(timespec="seconds"),
            "content": content,
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def list_files(directory: str, extension: str = None) -> list:
    """List files with optional extension filtering and metadata."""
    folder = Path(directory)
    if not folder.is_dir():
        return []

    if extension:
        extension = extension.lower()
        if not extension.startswith("."):
            extension = "." + extension

    results = []
    try:
        for path in folder.iterdir():
            if not path.is_file():
                continue
            if extension and path.suffix.lower() != extension:
                continue

            stat = path.stat()
            results.append({
                "name": path.name,
                "filepath": str(path.resolve()),
                "extension": path.suffix.lower(),
                "size_bytes": stat.st_size,
                "modified_date": datetime.fromtimestamp(
                    stat.st_mtime
                ).isoformat(timespec="seconds"),
            })
    except OSError:
        return []

    return results


def write_file(filepath: str, content: str) -> dict:
    """Write text to a file, creating parent directories if needed."""
    path = Path(filepath)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return {
            "success": True,
            "filepath": str(path.resolve()),
            "message": "File written successfully",
        }
    except (OSError, ValueError) as e:
        return {"success": False, "error": str(e)}





def search_in_file(filepath: str, keyword: str) -> dict:
    """Search for exact keyword occurrences, ignoring letter case."""
    if not keyword or not keyword.strip():
        return {
            "success": False,
            "error": "Keyword cannot be empty."
        }

    file_result = read_file(filepath)

    if not file_result.get("success"):
        return file_result

    content = file_result.get("content", "")
    matches = []

    # Find every literal occurrence of the keyword.
    for match in re.finditer(re.escape(keyword), content, re.IGNORECASE):
        start = max(0, match.start() - 80)
        end = min(len(content), match.end() + 80)

        matches.append({
            "matched_text": match.group(),
            "position": match.start(),
            "context": content[start:end].replace("\n", " ").strip()
        })

    return {
        "success": True,
        "filename": file_result.get("filename", filepath),
        "keyword": keyword,
        "match_count": len(matches),
        "matches": matches
    }

if __name__ == "__main__":
    print("Files:", list_files("resumes"))
    print("Search:", search_in_file("resumes/john_doe.txt", "python"))
    print("Read:", read_file("resumes/john_doe.txt")["success"])
