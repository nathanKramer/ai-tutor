#!/bin/bash

# AI Tutor Release Script
# Creates a distributable package of the AI Tutor application

set -e  # Exit on any error

# Change to project root directory (parent of scripts/)
cd "$(dirname "$0")/.."

VERSION=$(date +"%Y.%m.%d")
RELEASE_NAME="ai-tutor-v${VERSION}"
RELEASE_DIR="releases/${RELEASE_NAME}"

echo "🚀 Creating AI Tutor Release v${VERSION}"
echo "========================================"

# Create releases directory
mkdir -p releases

# Remove existing release if it exists
if [ -d "$RELEASE_DIR" ]; then
    echo "🧹 Removing existing release directory..."
    rm -rf "$RELEASE_DIR"
fi

# Run the build
echo "🔨 Building executable..."
scripts/build.sh

# Create release directory
echo "📦 Creating release package..."
mkdir -p "$RELEASE_DIR"

# Copy the executable and documentation
cp dist/ai-tutor "$RELEASE_DIR/"
cp dist/README.txt "$RELEASE_DIR/"

# Copy additional documentation
cp CLAUDE.md "$RELEASE_DIR/PROJECT_INFO.md"

# Create installation script
cat > "$RELEASE_DIR/install.sh" << 'EOF'
#!/bin/bash

# AI Tutor Installation Script

echo "🚀 Installing AI Tutor..."

# Make executable
chmod +x ai-tutor

# Create symlink to system path (optional)
read -p "Create system-wide command 'ai-tutor'? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    INSTALL_DIR="/usr/local/bin"
    if [ -w "$INSTALL_DIR" ]; then
        ln -sf "$(pwd)/ai-tutor" "$INSTALL_DIR/ai-tutor"
        echo "✅ Created system command: ai-tutor"
        echo "   You can now run 'ai-tutor' from anywhere!"
    else
        echo "⚠️  Need sudo to install system-wide:"
        echo "   sudo ln -sf $(pwd)/ai-tutor /usr/local/bin/ai-tutor"
    fi
fi

echo ""
echo "🎉 Installation complete!"
echo ""
echo "📋 To run:"
echo "   ./ai-tutor"
echo ""
echo "💡 Don't forget to set your API keys:"
echo "   export OPENAI_API_KEY='your-openai-key'"
echo "   export ANTHROPIC_API_KEY='your-anthropic-key'"
EOF

chmod +x "$RELEASE_DIR/install.sh"

# Create a startup script with API key check
cat > "$RELEASE_DIR/start.sh" << 'EOF'
#!/bin/bash

# AI Tutor Startup Script with API Key Check

echo "🚀 Starting AI Tutor..."

# Check for API keys
OPENAI_KEY=${OPENAI_API_KEY}
ANTHROPIC_KEY=${ANTHROPIC_API_KEY}

if [ -z "$OPENAI_KEY" ] && [ -z "$ANTHROPIC_KEY" ]; then
    echo "⚠️  Warning: No API keys found."
    echo ""
    echo "You need at least one API key to use AI Tutor:"
    echo "• For OpenAI: export OPENAI_API_KEY='your-key-here'"
    echo "• For Anthropic: export ANTHROPIC_API_KEY='your-key-here'"
    echo ""
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
elif [ -z "$OPENAI_KEY" ]; then
    echo "ℹ️  Note: Only Anthropic API key found - OpenAI provider will be unavailable"
elif [ -z "$ANTHROPIC_KEY" ]; then
    echo "ℹ️  Note: Only OpenAI API key found - Anthropic provider will be unavailable"
else
    echo "✅ Both API keys found"
fi

echo ""
./ai-tutor "$@"
EOF

chmod +x "$RELEASE_DIR/start.sh"

# Get file size
EXECUTABLE_SIZE=$(du -h "$RELEASE_DIR/ai-tutor" | cut -f1)

# Create release info
cat > "$RELEASE_DIR/RELEASE_INFO.txt" << EOF
AI Tutor Release v${VERSION}
============================

Build Date: $(date)
Executable Size: ${EXECUTABLE_SIZE}
Platform: $(uname -s) $(uname -m)

Quick Start:
1. Run: ./install.sh (optional, for system-wide install)
2. Set API keys:
   export OPENAI_API_KEY='your-openai-key'
   export ANTHROPIC_API_KEY='your-anthropic-key'
3. Run: ./start.sh (with API key checks) or ./ai-tutor

Features:
- Standalone executable (no Python required)
- Multiple AI providers (OpenAI GPT, Anthropic Claude)
- File system access for code analysis
- Socratic teaching methodology
- Multi-line input support
- Conversation history management

Files Included:
- ai-tutor: Main executable
- README.txt: User documentation
- PROJECT_INFO.md: Project documentation
- install.sh: Installation script
- start.sh: Startup script with API key validation
- RELEASE_INFO.txt: This file

For support and source code:
See PROJECT_INFO.md for project details.
EOF

# Create a compressed archive
echo "📦 Creating compressed archive..."
cd releases
tar -czf "${RELEASE_NAME}.tar.gz" "${RELEASE_NAME}"
cd ..

# Show results
echo ""
echo "✅ Release created successfully!"
echo ""
echo "📁 Release directory: $RELEASE_DIR"
echo "📦 Archive: releases/${RELEASE_NAME}.tar.gz"
echo "💾 Executable size: $EXECUTABLE_SIZE"
echo ""
echo "📋 To distribute:"
echo "   1. Share the archive: releases/${RELEASE_NAME}.tar.gz"
echo "   2. Or share the directory: $RELEASE_DIR"
echo ""
echo "🚀 Recipients can run:"
echo "   tar -xzf ${RELEASE_NAME}.tar.gz"
echo "   cd ${RELEASE_NAME}"
echo "   ./install.sh"
echo "   ./start.sh"


