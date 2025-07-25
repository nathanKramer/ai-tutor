#!/usr/bin/env python3
"""
Build script for AI Tutor application
Creates a standalone executable using PyInstaller
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

# Change to project root directory (parent of scripts/)
PROJECT_ROOT = Path(__file__).parent.parent
os.chdir(PROJECT_ROOT)


def run_command(cmd, cwd=None):
    """Run a command and return success status"""
    try:
        result = subprocess.run(cmd, shell=True, cwd=cwd, check=True, 
                              capture_output=True, text=True)
        print(f"✓ {cmd}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {cmd}")
        print(f"Error: {e.stderr}")
        return False


def check_requirements():
    """Check if all requirements are available"""
    print("📋 Checking requirements...")
    
    # Check if we're in a virtual environment
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("⚠️  Warning: Not running in a virtual environment")
        print("   It's recommended to build in a virtual environment")
        response = input("Continue anyway? (y/N): ")
        if response.lower() != 'y':
            return False
    
    # Check if PyInstaller is available
    try:
        import PyInstaller
        print(f"✓ PyInstaller {PyInstaller.__version__} found")
    except ImportError:
        print("✗ PyInstaller not found")
        print("Install with: pip install pyinstaller")
        return False
    
    return True


def clean_build():
    """Clean previous build artifacts"""
    print("🧹 Cleaning previous build artifacts...")
    
    dirs_to_clean = ['build', 'dist', '__pycache__']
    files_to_clean = ['*.pyc']
    
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"✓ Removed {dir_name}/")
    
    # Clean __pycache__ directories recursively
    for root, dirs, files in os.walk('.'):
        for dir_name in dirs:
            if dir_name == '__pycache__':
                pycache_path = os.path.join(root, dir_name)
                shutil.rmtree(pycache_path)
                print(f"✓ Removed {pycache_path}")


def build_executable():
    """Build the executable using PyInstaller"""
    print("🔨 Building executable...")
    
    # Use the spec file for better control
    cmd = "pyinstaller scripts/ai_tutor.spec --clean --noconfirm"
    
    if not run_command(cmd):
        print("❌ Build failed!")
        return False
    
    print("✅ Build completed successfully!")
    return True


def create_distribution():
    """Create distribution package"""
    print("📦 Creating distribution package...")
    
    dist_dir = Path("dist")
    if not dist_dir.exists():
        print("❌ No dist directory found")
        return False
    
    # Find the executable
    exe_files = list(dist_dir.glob("ai-tutor*"))
    if not exe_files:
        print("❌ No executable found in dist directory")
        return False
    
    exe_file = exe_files[0]
    print(f"✓ Found executable: {exe_file}")
    
    # Create README for the distribution
    readme_content = """# AI Tutor - Standalone Executable

## Setup

1. **API Keys**: Set at least one API key as an environment variable:
   ```bash
   # For OpenAI (GPT models)
   export OPENAI_API_KEY="your-openai-api-key-here"
   
   # For Anthropic (Claude models)  
   export ANTHROPIC_API_KEY="your-anthropic-api-key-here"
   ```

2. **Run the application**:
   ```bash
   ./ai-tutor          # Linux/macOS
   ai-tutor.exe        # Windows
   ```

## Usage

- Type messages directly to chat with the AI tutor
- Use slash commands for special functions:
  - `/help` - Show available commands
  - `/quit` - Exit the application
  - `/clear` - Clear conversation history
  - `/provider openai` - Switch to OpenAI
  - `/provider claude` - Switch to Claude
  - `/config` - Show current configuration

## Features

- **Multiple AI Providers**: Support for OpenAI GPT and Anthropic Claude
- **File System Access**: AI can read and explore your project files
- **Socratic Teaching**: AI uses Socratic method for programming instruction
- **Multi-line Input**: Use Alt+Enter for multi-line messages
- **Conversation History**: Maintains context across the session

## Troubleshooting

- If the application doesn't start, check that your API keys are set correctly
- Use `--debug` flag for detailed logging: `./ai-tutor --debug`
- Check the logs in the `logs/` directory (when debug mode is enabled)

For more information, see the project documentation.
"""
    
    readme_path = dist_dir / "README.txt"
    with open(readme_path, 'w') as f:
        f.write(readme_content)
    
    print(f"✓ Created {readme_path}")
    
    # Make executable if on Unix-like system
    if os.name != 'nt':  # Not Windows
        os.chmod(exe_file, 0o755)
        print("✓ Made executable file executable")
    
    return True


def main():
    """Main build process"""
    print("🚀 AI Tutor Build Script")
    print("=" * 50)
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    # Clean previous build
    clean_build()
    
    # Build executable
    if not build_executable():
        sys.exit(1)
    
    # Create distribution package
    if not create_distribution():
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("🎉 Build completed successfully!")
    print(f"📁 Executable location: dist/")
    
    # Show final instructions
    exe_name = "ai-tutor.exe" if os.name == 'nt' else "ai-tutor"
    print(f"\n📋 To run:")
    print(f"   cd dist/")
    print(f"   ./{exe_name}")
    print(f"\n💡 Don't forget to set your API keys!")


if __name__ == "__main__":
    main()