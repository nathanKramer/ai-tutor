import os
from pathlib import Path
from typing import Dict, List, Any, Optional 
from core.interfaces import ToolInterface, LoggerInterface


class ToolPlugin(ToolInterface):
    """Base class for tool plugins"""
    
    def __init__(self, working_directory: str | None = None, logger: Optional[LoggerInterface] = None):
        self.working_directory = working_directory or os.getcwd()
        self.logger = logger
    
    def _is_safe_path(self, file_path: str) -> bool:
        """Check if the file path is safe (within working directory)"""
        try:
            full_path = os.path.abspath(os.path.join(self.working_directory, file_path))
            working_dir_abs = os.path.abspath(self.working_directory)
            return full_path.startswith(working_dir_abs)
        except:
            return False
    
    def _log_operation(self, operation: str, details: str = ""):
        """Log tool operation if logger is available"""
        if self.logger:
            self.logger.info(f"Tool {self.get_name()}: {operation} {details}")


class FileSystemPlugin(ToolPlugin):
    """File system operations plugin"""
    
    def get_name(self) -> str:
        return "filesystem"
    
    def get_description(self) -> str:
        return "File system operations including read, list, and info"
    
    def get_parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": ["read_file", "list_files", "get_file_info"],
                    "description": "File system operation to perform"
                },
                "file_path": {
                    "type": "string",
                    "description": "Path to file (for read_file and get_file_info)"
                },
                "directory": {
                    "type": "string",
                    "description": "Directory to list (for list_files)",
                    "default": "."
                },
                "pattern": {
                    "type": "string",
                    "description": "File pattern to match (for list_files)",
                    "default": "*"
                },
                "show_hidden": {
                    "type": "boolean",
                    "description": "Show hidden files (for list_files)",
                    "default": False
                },
                "max_lines": {
                    "type": "integer",
                    "description": "Maximum lines to read (for read_file)"
                }
            },
            "required": ["operation"]
        }
    
    def execute(self, **kwargs) -> str:
        operation = kwargs.get("operation")
        
        if operation == "read_file":
            return self._read_file(
                kwargs.get("file_path", ""),
                kwargs.get("max_lines")
            )
        elif operation == "list_files":
            return self._list_files(
                kwargs.get("directory", "."),
                kwargs.get("pattern", "*"),
                kwargs.get("show_hidden", False)
            )
        elif operation == "get_file_info":
            return self._get_file_info(kwargs.get("file_path", ""))
        else:
            return f"Error: Unknown filesystem operation '{operation}'"
    
    def is_safe(self, **kwargs) -> bool:
        operation = kwargs.get("operation")
        
        if operation in ["read_file", "get_file_info"]:
            file_path = kwargs.get("file_path", "")
            return self._is_safe_path(file_path)
        elif operation == "list_files":
            directory = kwargs.get("directory", ".")
            return self._is_safe_path(directory)
        
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
            self._log_operation(f"reading file {file_path}")
            
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
        except Exception as e:
            return f"Error reading file: {str(e)}"
    
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
            self._log_operation(f"listing files in {directory}")
            
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
            self._log_operation(f"getting info for {file_path}")
            
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


class PluginManager:
    """Manages tool plugins"""
    
    def __init__(self, logger: Optional[LoggerInterface] = None):
        self.logger = logger
        self._plugins: Dict[str, ToolInterface] = {}
        self._load_built_in_plugins()
    
    def _load_built_in_plugins(self):
        """Load built-in plugins"""
        working_dir = os.getcwd()
        
        # Load filesystem plugin
        filesystem_plugin = FileSystemPlugin(working_dir, self.logger)
        self.register_plugin(filesystem_plugin)
    
    def register_plugin(self, plugin: ToolInterface):
        """Register a tool plugin"""
        plugin_name = plugin.get_name()
        self._plugins[plugin_name] = plugin
        
        if self.logger:
            self.logger.info(f"Registered tool plugin: {plugin_name}")
    
    def unregister_plugin(self, plugin_name: str):
        """Unregister a tool plugin"""
        if plugin_name in self._plugins:
            del self._plugins[plugin_name]
            
            if self.logger:
                self.logger.info(f"Unregistered tool plugin: {plugin_name}")
    
    def get_plugin(self, plugin_name: str) -> Optional[ToolInterface]:
        """Get a specific plugin"""
        return self._plugins.get(plugin_name)
    
    def list_plugins(self) -> List[str]:
        """List all registered plugins"""
        return list(self._plugins.keys())
    
    def get_all_tool_definitions(self) -> List[Dict[str, Any]]:
        """Get tool definitions for all plugins"""
        definitions = []
        
        for plugin_name, plugin in self._plugins.items():
            # Create individual tool definitions for each plugin
            if plugin_name == "filesystem":
                # Special handling for filesystem plugin - create separate tools
                definitions.extend(self._get_filesystem_tool_definitions())
            else:
                definitions.append({
                    "type": "function",
                    "function": {
                        "name": plugin_name,
                        "description": plugin.get_description(),
                        "parameters": plugin.get_parameters_schema()
                    }
                })
        
        return definitions
    
    def _get_filesystem_tool_definitions(self) -> List[Dict[str, Any]]:
        """Get individual tool definitions for filesystem operations"""
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
        # Handle filesystem operations
        if tool_name in ["read_file", "list_files", "get_file_info"]:
            filesystem_plugin = self.get_plugin("filesystem")
            if filesystem_plugin:
                # Add operation to arguments
                arguments["operation"] = tool_name
                return filesystem_plugin.execute(**arguments)
            else:
                return f"Error: Filesystem plugin not available"
        
        # Handle other plugins
        plugin = self.get_plugin(tool_name)
        if not plugin:
            return f"Error: Unknown tool '{tool_name}'"
        
        # Check if operation is safe
        if not plugin.is_safe(**arguments):
            return f"Error: Unsafe operation blocked for tool '{tool_name}'"
        
        try:
            return plugin.execute(**arguments)
        except Exception as e:
            error_msg = f"Error executing {tool_name}: {str(e)}"
            if self.logger:
                self.logger.error(error_msg)
            return error_msg
    
    def load_plugins_from_directory(self, plugin_dir: str):
        """Load plugins from a directory (for future extensibility)"""
        plugin_path = Path(plugin_dir)
        
        if not plugin_path.exists() or not plugin_path.is_dir():
            if self.logger:
                self.logger.warning(f"Plugin directory not found: {plugin_dir}")
            return
        
        # This could be implemented later to load external plugins
        if self.logger:
            self.logger.info(f"Plugin directory scanning not yet implemented: {plugin_dir}")
