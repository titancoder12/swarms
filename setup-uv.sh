#!/bin/bash
echo "Setting up Python environment with uv..."

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "uv not found. Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    source $HOME/.cargo/env
fi

# Create virtual environment and install dependencies
echo "Creating virtual environment and installing dependencies..."
uv sync

echo "Setup complete! To activate the environment, run:"
echo "source .venv/bin/activate"
