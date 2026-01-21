# AI Academician

A multi-agent research paper writing system that generates publication-ready academic papers using AI.

## Features

- **8 Specialized Agents** working collaboratively:
  - **Research Agent**: User interaction, topic refinement, title formulation
  - **Source Finder (Agent 1)**: Web and academic search using Google and arXiv
  - **Summarizer (Agent 2)**: Content reading and detailed summarization
  - **Planner (Agent 3)**: Research gap analysis and paper structure planning
  - **Body Writer (Agent 4)**: Writes 15,000-22,000 word research body
  - **Intro Writer (Agent 5)**: Introduction, conclusion, and abstract
  - **Reviewer (Agent 6)**: Quality review with minimum 2 cycles
  - **Editor (Agent 7)**: Edits based on reviewer feedback

- **Multiple LLM Support**: OpenAI GPT, Google Gemini, Anthropic Claude, HuggingFace models
- **Academic Search**: Google Custom Search + arXiv integration
- **Citation Styles**: APA, MLA, Chicago, IEEE, Harvard
- **Export Formats**: PDF, Word (.docx), LaTeX

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/ai-academician.git
cd ai-academician

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e .

# For development
pip install -e ".[dev]"
```

## Configuration

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Fill in your API keys in `.env`:
```env
# Required: At least one LLM provider
GOOGLE_API_KEY=your_google_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
OPENAI_API_KEY=your_openai_api_key

# Required for search
GOOGLE_CSE_ID=your_google_custom_search_engine_id

# Optional
HUGGINGFACE_API_KEY=your_huggingface_api_key
DEFAULT_LLM_PROVIDER=gemini
```

## Usage

### Interactive Mode

```bash
ai-academician generate -i
```

### Command Line

```bash
# Generate a paper with default settings
ai-academician generate -t "Impact of AI on Healthcare Diagnostics"

# Specify citation style and word count
ai-academician generate -t "Machine Learning in Finance" -s APA -w 20000

# Export to all formats
ai-academician generate -t "Climate Change Effects" -f pdf -f docx -f latex

# With custom output directory
ai-academician generate -t "Your Topic" -o ./my_papers
```

### Options

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--topic` | `-t` | Research topic | Required |
| `--style` | `-s` | Citation style (APA, MLA, Chicago, IEEE, Harvard) | APA |
| `--words` | `-w` | Target word count | 18000 |
| `--output` | `-o` | Output directory | ./output |
| `--format` | `-f` | Export format (can use multiple) | pdf, docx |
| `--interactive` | `-i` | Interactive mode | False |
| `--debug` | | Enable debug logging | False |

### Other Commands

```bash
# Show configuration
ai-academician config

# Show version
ai-academician version
```

## Project Structure

```
ai-academician/
├── src/
│   ├── agents/           # 8 specialized agents
│   ├── llm/              # LLM provider implementations
│   ├── search/           # Search API integrations
│   ├── models/           # Data models
│   ├── export/           # PDF, Word, LaTeX exporters
│   ├── citations/        # Citation formatters
│   ├── storage/          # Database and file management
│   ├── utils/            # Utilities
│   ├── config.py         # Configuration
│   ├── orchestrator.py   # Agent orchestration
│   └── main.py           # CLI entry point
├── tests/
├── specs/                # Feature specifications
├── pyproject.toml
├── .env.example
└── README.md
```

## Agent Workflow

```
User Input → Research Agent → Source Finder → Summarizer → Planner
                                                              ↓
Export ← Source Finder ← Editor ← Reviewer ← Intro Writer ← Body Writer
         (format review)    ↑________↓
                         (review loop)
```

## Development

### Running Tests

```bash
pytest
pytest --cov=src  # With coverage
```

### Code Quality

```bash
# Format code
black src tests

# Lint
ruff check src tests

# Type check
mypy src
```

## API Keys Setup

### Google Custom Search
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable the Custom Search API
4. Create credentials (API Key)
5. Go to [Programmable Search Engine](https://programmablesearchengine.google.com/)
6. Create a search engine
7. Get your Search Engine ID (cx)

### LLM Providers
- **OpenAI**: Get API key from [OpenAI Platform](https://platform.openai.com/)
- **Google Gemini**: Get API key from [Google AI Studio](https://makersuite.google.com/)
- **Anthropic Claude**: Get API key from [Anthropic Console](https://console.anthropic.com/)
- **HuggingFace**: Get API key from [HuggingFace Settings](https://huggingface.co/settings/tokens)

## License

MIT License

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## Acknowledgments

Built with:
- [OpenAI Agents SDK](https://github.com/openai/openai-agents-sdk)
- [Google Generative AI](https://ai.google.dev/)
- [Anthropic Claude](https://www.anthropic.com/)
- [arXiv API](https://arxiv.org/help/api/)
