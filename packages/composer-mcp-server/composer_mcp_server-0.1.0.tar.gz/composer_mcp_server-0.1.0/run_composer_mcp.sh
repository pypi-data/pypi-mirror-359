#!/bin/bash

# Composer MCP Server Runner
# Converted from MCP configuration

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo "Options:"
    echo "  -a, --api-key KEY     Composer API key (required)"
    echo "  -s, --secret-key KEY  Composer secret key (required)"
    echo "  -h, --help            Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 -a my-api-key -s my-secret-key"
    echo "  $0 --api-key my-api-key --secret-key my-secret-key"
}

# Parse command line arguments
API_KEY=""
SECRET_KEY=""

while [[ $# -gt 0 ]]; do
    case $1 in
        -a|--api-key)
            API_KEY="$2"
            shift 2
            ;;
        -s|--secret-key)
            SECRET_KEY="$2"
            shift 2
            ;;
        -h|--help)
            show_usage
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Validate required parameters
if [ -z "$API_KEY" ]; then
    echo "Error: API key is required"
    show_usage
    exit 1
fi

if [ -z "$SECRET_KEY" ]; then
    echo "Error: Secret key is required"
    show_usage
    exit 1
fi

# Set environment variables
export COMPOSER_API_KEY="$API_KEY"
export COMPOSER_SECRET_KEY="$SECRET_KEY"

# Get the path to uvx
UVX_PATH=$(which uvx)

# Check if uvx is found
if [ -z "$UVX_PATH" ]; then
    echo "Error: uvx not found in PATH"
    exit 1
fi

# Run the composer MCP server
"$UVX_PATH" \
  --refresh \
  --default-index "https://test.pypi.org/simple/" \
  --index "https://pypi.org/simple/" \
  --index-strategy "unsafe-best-match" \
  composer-mcp-server@latest 