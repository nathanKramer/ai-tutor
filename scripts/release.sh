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
cp dist/ai "$RELEASE_DIR/"
cp dist/README.txt "$RELEASE_DIR/"

# Copy additional documentation
cp CLAUDE.md "$RELEASE_DIR/PROJECT_INFO.md"

# Get file size
EXECUTABLE_SIZE=$(du -h "$RELEASE_DIR/ai" | cut -f1)

# Create release info
cat > "$RELEASE_DIR/RELEASE_INFO.txt" << EOF
AI Tutor Release v${VERSION}
============================

Build Date: $(date)
Executable Size: ${EXECUTABLE_SIZE}
Platform: $(uname -s) $(uname -m)

Features:
- Standalone executable (no Python required)
- Multiple AI providers (OpenAI GPT, Anthropic Claude)
- File system access for code analysis
- Socratic teaching methodology
- Multi-line input support
- Conversation history management

Files Included:
- ai: Main executable
- README.txt: User documentation
- PROJECT_INFO.md: Project documentation
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


