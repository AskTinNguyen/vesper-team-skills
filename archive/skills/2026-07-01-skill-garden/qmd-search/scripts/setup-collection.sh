#!/bin/bash
#
# QMD Collection Setup Script
#
# Quickly set up a new QMD collection from a folder of documents.
#
# Usage:
#   ./setup-collection.sh <folder-path> [collection-name] [pattern]
#
# Arguments:
#   folder-path      Path to the folder containing documents (required)
#   collection-name  Name for the collection (optional, defaults to folder name)
#   pattern          Glob pattern for files (optional, defaults to **/*.md)
#
# Examples:
#   ./setup-collection.sh ~/Documents/notes
#   ./setup-collection.sh ~/Documents/notes my-notes
#   ./setup-collection.sh ~/Documents/notes my-notes "**/*.txt"

set -e

# Check arguments
if [ -z "$1" ]; then
    echo "Usage: $0 <folder-path> [collection-name] [pattern]"
    echo ""
    echo "Examples:"
    echo "  $0 ~/Documents/notes"
    echo "  $0 ~/Documents/notes my-notes"
    echo "  $0 ~/Documents/notes my-notes '**/*.txt'"
    exit 1
fi

FOLDER_PATH="$1"
COLLECTION_NAME="${2:-$(basename "$FOLDER_PATH")}"
PATTERN="${3:-**/*.md}"

# Check if folder exists
if [ ! -d "$FOLDER_PATH" ]; then
    echo "ERROR: Folder does not exist: $FOLDER_PATH"
    exit 1
fi

# Check if QMD is installed
if ! command -v qmd &> /dev/null; then
    echo "ERROR: QMD is not installed."
    echo "Run: bun install -g https://github.com/tobi/qmd"
    exit 1
fi

echo "==================================="
echo "   Setting up QMD Collection"
echo "==================================="
echo ""
echo "Folder:     $FOLDER_PATH"
echo "Name:       $COLLECTION_NAME"
echo "Pattern:    $PATTERN"
echo ""

# Add collection
echo "Step 1/3: Adding collection..."
qmd collection add "$FOLDER_PATH" --name "$COLLECTION_NAME" --mask "$PATTERN"
echo "✓ Collection added"
echo ""

# Generate embeddings
echo "Step 2/3: Generating embeddings (this may take a while)..."
qmd embed
echo "✓ Embeddings generated"
echo ""

# Show status
echo "Step 3/3: Verifying setup..."
qmd status
echo ""

echo "==================================="
echo "   Setup Complete!"
echo "==================================="
echo ""
echo "Try searching:"
echo "  qmd search 'your query' -c $COLLECTION_NAME"
echo "  qmd vsearch 'your query' -c $COLLECTION_NAME"
echo "  qmd query 'your query' -c $COLLECTION_NAME"
echo ""
