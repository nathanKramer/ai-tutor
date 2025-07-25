import os
import json
from typing import Dict, List, Any, Optional
from pathlib import Path


class ToolRegistry:
    """Registry for available tools that the AI can use"""
    
    def __init__(self, working_directory: str = None):
        self.working_directory = working_directory or os.getcwd()
        self.tools = {
            "read_file": self._read_file,
            "list_files": self._list_files,
            "get_file_info": self._get_file_info
        }
    
    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        """Get tool definitions for AI providers"""
        return [
            {
                "type": "function",
                "function": {
                    "name": "read_file",
                    "description": "Read the contents of a file in the current working directory",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "file_path": {
                                "type": "string",
                                "description": "The path to the file to read (relative to current directory)"
                            },
                            "max_lines": {
                                "type": "integer",
                                "description": "Maximum number of lines to read (optional, default: all)",
                                "default": None
                            }
                        },
                        "required": ["file_path"]
                    }
                }
            },
            {
                "type": "function", 
                "function": {
                    "name": "list_files",
                    "description": "List files and directories in the current working directory",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "directory": {
                                "type": "string",
                                "description": "Directory to list (relative to current directory, default: current directory). Use subdirectory names to explore deeper (e.g., 'src', 'tests')",
                                "default": "."
                            },
                            "pattern": {
                                "type": "string",
                                "description": "File pattern to match (e.g., '*.py', '*.js', '*' for all files)",
                                "default": "*"
                            },
                            "show_hidden": {
                                "type": "boolean",
                                "description": "Include hidden files/directories (starting with .)",
                                "default": False
                            }
                        },
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_file_info",
                    "description": "Get information about a file (size, modified time, type)",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "file_path": {
                                "type": "string",
                                "description": "The path to the file"
                            }
                        },
                        "required": ["file_path"]
                    }
                }
            }
        ]
    
    def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """Execute a tool and return the result"""
        if tool_name not in self.tools:
            return f"Error: Unknown tool '{tool_name}'"
        
        try:
            return self.tools[tool_name](**arguments)
        except Exception as e:
            return f"Error executing {tool_name}: {str(e)}"
    
    def _is_safe_path(self, file_path: str) -> bool:
        """Check if the file path is safe (within working directory)"""
        try:
            full_path = os.path.abspath(os.path.join(self.working_directory, file_path))
            working_dir_abs = os.path.abspath(self.working_directory)
            return full_path.startswith(working_dir_abs)
        except:
            return False
    
    def _read_file(self, file_path: str, max_lines: Optional[int] = None) -> str:
        """Read file contents"""
        if not self._is_safe_path(file_path):
            return "Error: File path is outside the allowed directory"
        
        full_path = os.path.join(self.working_directory, file_path)
        
        if not os.path.exists(full_path):
            return f"Error: File '{file_path}' does not exist"
        
        if not os.path.isfile(full_path):
            return f"Error: '{file_path}' is not a file"
        
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                if max_lines:
                    lines = []
                    for i, line in enumerate(f):
                        if i >= max_lines:
                            break
                        lines.append(line.rstrip('\n\r'))
                    content = '\n'.join(lines)
                    if i >= max_lines - 1:
                        content += f"\n... (showing first {max_lines} lines)"
                else:
                    content = f.read()
            
            return f"Contents of {file_path}:\n```\n{content}\n```"
        
        except UnicodeDecodeError:
            return f"Error: '{file_path}' appears to be a binary file"
        except PermissionError:
            return f"Error: Permission denied reading '{file_path}'"
    
    def _list_files(self, directory: str = ".", pattern: str = "*", show_hidden=False) -> str:
        """List files in directory"""
        # Convert string boolean to actual boolean
        if isinstance(show_hidden, str):
            show_hidden = show_hidden.lower() in ('true', '1', 'yes', 'on')
        
        if not self._is_safe_path(directory):
            return "Error: Directory path is outside the allowed directory"
        
        full_path = os.path.join(self.working_directory, directory)
        
        if not os.path.exists(full_path):
            return f"Error: Directory '{directory}' does not exist"
        
        if not os.path.isdir(full_path):
            return f"Error: '{directory}' is not a directory"
        
        try:
            items = []
            
            # Get all items in directory
            for item in os.listdir(full_path):
                # Skip hidden files unless requested
                if item.startswith('.') and not show_hidden:
                    continue
                
                item_path = os.path.join(full_path, item)
                rel_path = os.path.relpath(item_path, self.working_directory)
                
                # Apply pattern matching
                if pattern != "*":
                    from fnmatch import fnmatch
                    if not fnmatch(item, pattern):
                        continue
                
                if os.path.isdir(item_path):
                    # Count items in subdirectory for context
                    try:
                        subdir_count = len([f for f in os.listdir(item_path) 
                                          if not f.startswith('.') or show_hidden])
                        items.append(f"📁 {rel_path}/ ({subdir_count} items)")
                    except PermissionError:
                        items.append(f"📁 {rel_path}/ (permission denied)")
                else:
                    size = os.path.getsize(item_path)
                    # Add file type context
                    _, ext = os.path.splitext(item)
                    if ext:
                        items.append(f"📄 {rel_path} ({size} bytes, {ext[1:]} file)")
                    else:
                        items.append(f"📄 {rel_path} ({size} bytes)")
            
            # Sort: directories first, then files
            dirs = [item for item in items if item.startswith("📁")]
            files = [item for item in items if item.startswith("📄")]
            
            result = f"Contents of {directory}:\n"
            
            if dirs:
                result += "\nDirectories:\n" + "\n".join(sorted(dirs))
            
            if files:
                result += "\n\nFiles:\n" + "\n".join(sorted(files))
            
            if not dirs and not files:
                result += "No items found" + (f" matching pattern '{pattern}'" if pattern != "*" else "")
            
            # Add exploration hint for directories
            if dirs and directory == ".":
                result += "\n\n💡 Use list_files with directory parameter to explore subdirectories (e.g., directory='src')"
            
            return result
        
        except Exception as e:
            return f"Error listing directory: {str(e)}"
    
    def _get_file_info(self, file_path: str) -> str:
        """Get file information"""
        if not self._is_safe_path(file_path):
            return "Error: File path is outside the allowed directory"
        
        full_path = os.path.join(self.working_directory, file_path)
        
        if not os.path.exists(full_path):
            return f"Error: '{file_path}' does not exist"
        
        try:
            stat = os.stat(full_path)
            is_file = os.path.isfile(full_path)
            is_dir = os.path.isdir(full_path)
            
            import time
            modified_time = time.ctime(stat.st_mtime)
            
            info = f"Information for {file_path}:\n"
            info += f"Type: {'File' if is_file else 'Directory' if is_dir else 'Other'}\n"
            info += f"Size: {stat.st_size} bytes\n"
            info += f"Modified: {modified_time}\n"
            
            if is_file:
                # Try to determine file type
                _, ext = os.path.splitext(file_path)
                if ext:
                    info += f"Extension: {ext}\n"
            
            return info
        
        except Exception as e:
            return f"Error getting file info: {str(e)}"


def process_tool_calls(tool_calls: List[Dict], tool_registry: ToolRegistry) -> List[Dict]:
    """Process a list of tool calls and return results"""
    results = []
    
    for tool_call in tool_calls:
        tool_name = tool_call.get("function", {}).get("name")
        arguments = tool_call.get("function", {}).get("arguments", {})
        
        # Parse arguments if they're a JSON string
        if isinstance(arguments, str):
            try:
                arguments = json.loads(arguments)
            except json.JSONDecodeError:
                results.append({
                    "tool_call_id": tool_call.get("id"),
                    "output": f"Error: Invalid JSON arguments for {tool_name}"
                })
                continue
        
        # Execute the tool
        result = tool_registry.execute_tool(tool_name, arguments)
        
        results.append({
            "tool_call_id": tool_call.get("id"),
            "output": result
        })
    
    return results