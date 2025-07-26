#!/bin/bash
echo "Setting up Python environment with uv..."

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "uv not found. Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    
    # Add uv to PATH for this session
    export PATH="$HOME/.local/bin:$PATH"
    
    # Verify installation
    if ! command -v uv &> /dev/null; then
        echo "Error: uv installation failed. Please install manually:"
        echo "Visit: https://docs.astral.sh/uv/getting-started/installation/"
        exit 1
    fi
fi

# Create virtual environment and install dependencies
echo "Creating virtual environment and installing dependencies..."
uv sync

echo "Setup complete! To activate the environment, run:"
echo "source .venv/bin/activate"
