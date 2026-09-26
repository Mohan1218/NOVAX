from pathlib import Path
from typing import List, Dict, Any, Union
from backend.tools.workspace import resolve_workspace
from backend.tools.file_ops import list_files


def search_code(workspace: Union[str, Path], query: str) -> List[Dict[str, Any]]:
    """
    Recursively searches for text across readable source files in the workspace.
    Case-insensitive search. Skips binary and unreadable files.
    
    Args:
        workspace: Workspace identifier or path.
        query: String pattern to search for.
        
    Returns:
        List of dictionaries containing file relative path, 1-indexed line number, and matching line text.
    """
    if not query:
        return []
        
    ws_path = resolve_workspace(workspace)
    files = list_files(workspace)
    
    results: List[Dict[str, Any]] = []
    query_lower = query.lower()
    
    for rel_file in files:
        full_path = ws_path / rel_file
        
        try:
            with open(full_path, "r", encoding="utf-8", errors="replace") as f:
                for line_num, line in enumerate(f, start=1):
                    if query_lower in line.lower():
                        results.append({
                            "file": rel_file,
                            "line": line_num,
                            "text": line.strip()
                        })
        except (OSError, UnicodeDecodeError, PermissionError):
            # Skip unreadable or binary files gracefully
            continue
            
    return results
