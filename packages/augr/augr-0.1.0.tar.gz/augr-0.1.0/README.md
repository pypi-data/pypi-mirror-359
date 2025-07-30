# AUGR - AI Dataset Augmentation Tool

AI-powered dataset augmentation tool using Braintrust proxy with structured outputs.

## Features

- 🤖 **Structured AI Outputs**: Uses OpenAI's `beta.chat.completions.parse` with Pydantic schemas
- 🧠 **Braintrust Integration**: Works with Braintrust proxy for multiple AI providers
- 🔄 **Interactive Workflows**: Guided dataset augmentation with iterative refinement
- 📊 **Schema-aware Generation**: Automatically infers and respects dataset schemas
- ⚡ **Modern Tooling**: Built with `uv` for fast dependency management

## Installation

### Option 1: Install from PyPI (Coming Soon)

```bash
# Install globally
pip install augr

# Or with pipx (recommended for CLI tools)
pipx install augr

# Or with uv
uv tool install augr

# Then use anywhere
augr
```

### Option 2: Install from GitHub

```bash
# Install latest version
pip install git+https://github.com/yourusername/augr.git

# Or with uv
uv tool install git+https://github.com/yourusername/augr.git

# Then use anywhere
augr
```

### Option 3: Development Setup

For development or local installation:

```bash
git clone https://github.com/yourusername/augr.git
cd augr
uv pip install -e .

# Test the installation
python test_installation.py

# Use anywhere
augr
```

## Usage

### Environment Variables

Create a `.env` file with:

```env
BRAINTRUST_API_KEY=your_braintrust_api_key_here
# Optional: BRAINTRUST_BASE_URL=https://api.braintrust.dev/v1/proxy
```

### Running

The tool provides an interactive CLI with two main modes:

1. **Guided Dataset Augmentation**: Interactive workflow with iterative refinement
2. **Direct JSON Upload**: Upload pre-generated samples directly

```bash
uv run python run_augr.py
```

### Development

Install with development dependencies:

```bash
uv pip install -e ".[dev]"
```

Run linting and formatting:

```bash
uv run black .
uv run ruff check .
```

## Architecture

- **`ai_client.py`**: Core AI interface with structured outputs
- **`augmentation_service.py`**: Main service for dataset augmentation
- **`cli.py`**: Interactive command-line interface
- **`models.py`**: Pydantic models for data structures
- **`braintrust_client.py`**: Braintrust API integration

## API Example

```python
from augr.ai_client import create_ai
from pydantic import BaseModel

class Response(BaseModel):
    message: str
    confidence: float

# Create AI client (reads BRAINTRUST_API_KEY from env)
ai = create_ai(model="gpt-4o", temperature=0.0)

# Generate structured output
result = await ai.gen_obj(
    schema=Response,
    messages=[{"role": "user", "content": "Hello!"}],
    thinking_enabled=True  # For reasoning models
)

print(result.message)  # Structured output
```

## License

[Your License Here]
