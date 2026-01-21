<p align="center">
  <h1 align="center">AI Academician</h1>
  <p align="center">
    <strong>Multi-Agent AI System for Academic Research Paper Generation</strong>
  </p>
  <p align="center">
    <a href="https://github.com/AutoSpaien-Pvt-Ltd/ai-academician/blob/main/LICENSE"><img src="https://img.shields.io/badge/License-MIT-blue.svg" alt="License: MIT"></a>
    <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/Python-3.11+-green.svg" alt="Python 3.11+"></a>
    <a href="https://github.com/AutoSpaien-Pvt-Ltd/ai-academician/issues"><img src="https://img.shields.io/github/issues/AutoSpaien-Pvt-Ltd/ai-academician" alt="Issues"></a>
    <a href="https://github.com/AutoSpaien-Pvt-Ltd/ai-academician/stargazers"><img src="https://img.shields.io/github/stars/AutoSpaien-Pvt-Ltd/ai-academician" alt="Stars"></a>
  </p>
</p>

---

Generate **publication-ready academic research papers** with an intelligent multi-agent system. AI Academician orchestrates 8 specialized AI agents to research, write, review, and format papers automatically.

## Key Features

| Feature | Description |
|---------|-------------|
| **8 Specialized Agents** | Collaborative AI agents for end-to-end paper generation |
| **Multi-LLM Support** | OpenAI GPT-4, Google Gemini, Anthropic Claude, HuggingFace |
| **Academic Search** | Google Custom Search + arXiv integration |
| **5 Citation Styles** | APA, MLA, Chicago, IEEE, Harvard |
| **3 Export Formats** | PDF, Word (.docx), LaTeX |
| **Quality Assurance** | Minimum 2 review cycles before approval |

## Agent Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           AI ACADEMICIAN WORKFLOW                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   User Input                                                                 │
│       │                                                                      │
│       ▼                                                                      │
│   ┌──────────────┐    ┌──────────────┐    ┌──────────────┐                  │
│   │   Research   │───▶│    Source    │───▶│  Summarizer  │                  │
│   │    Agent     │    │    Finder    │    │   (Agent 2)  │                  │
│   └──────────────┘    │   (Agent 1)  │    └──────────────┘                  │
│                       └──────────────┘            │                          │
│                                                   ▼                          │
│   ┌──────────────┐    ┌──────────────┐    ┌──────────────┐                  │
│   │    Editor    │◀───│   Reviewer   │◀───│   Planner    │                  │
│   │   (Agent 7)  │    │   (Agent 6)  │    │   (Agent 3)  │                  │
│   └──────────────┘    └──────────────┘    └──────────────┘                  │
│          │                   ▲                    │                          │
│          │            ┌──────┴──────┐             ▼                          │
│          │            │ Review Loop │    ┌──────────────┐                   │
│          │            │  (min 2x)   │    │ Body Writer  │                   │
│          │            └─────────────┘    │   (Agent 4)  │                   │
│          │                   ▲           └──────────────┘                   │
│          │                   │                    │                          │
│          ▼                   │                    ▼                          │
│   ┌──────────────┐           │           ┌──────────────┐                   │
│   │    Export    │           └───────────│ Intro Writer │                   │
│   │  PDF/DOCX/   │                       │   (Agent 5)  │                   │
│   │    LaTeX     │                       └──────────────┘                   │
│   └──────────────┘                                                          │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Agent Responsibilities

| Agent | Role | Output |
|-------|------|--------|
| **Research Agent** | User interaction, topic refinement | Refined research topic & title |
| **Source Finder** | Web & academic search (Google + arXiv) | 20-30 credible sources |
| **Summarizer** | Content analysis & summarization | Detailed source summaries |
| **Planner** | Research gap analysis & structure | Paper outline & methodology |
| **Body Writer** | Core research content | 15,000-22,000 words |
| **Intro Writer** | Introduction, conclusion, abstract | Complete paper framing |
| **Reviewer** | Quality assurance (min 2 cycles) | Feedback & improvement areas |
| **Editor** | Content refinement | Publication-ready paper |

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/AutoSpaien-Pvt-Ltd/ai-academician.git
cd ai-academician

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install package
pip install -e .
```

### Configuration

```bash
# Copy environment template
cp .env.example .env
```

Edit `.env` with your API keys:

```env
# LLM Providers (at least one required)
OPENAI_API_KEY=your_openai_key
GOOGLE_API_KEY=your_google_key
ANTHROPIC_API_KEY=your_anthropic_key

# Search (required)
GOOGLE_CSE_ID=your_search_engine_id

# Defaults
DEFAULT_LLM_PROVIDER=gemini
DEFAULT_CITATION_STYLE=APA
```

### Generate a Paper

```bash
# Interactive mode (recommended)
ai-academician generate -i

# Direct generation
ai-academician generate -t "Impact of Artificial Intelligence on Healthcare Diagnostics"

# With options
ai-academician generate \
  -t "Machine Learning in Finance" \
  -s APA \
  -w 20000 \
  -f pdf -f docx -f latex
```

## CLI Reference

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--topic` | `-t` | Research topic | Required |
| `--style` | `-s` | Citation style (APA/MLA/Chicago/IEEE/Harvard) | APA |
| `--words` | `-w` | Target word count | 18,000 |
| `--output` | `-o` | Output directory | ./output |
| `--format` | `-f` | Export format (can use multiple) | pdf, docx |
| `--interactive` | `-i` | Interactive mode | False |
| `--debug` | | Enable debug logging | False |

## Supported LLM Providers

| Provider | Models | Best For |
|----------|--------|----------|
| **OpenAI** | GPT-4, GPT-4 Turbo | High-quality generation |
| **Google Gemini** | Gemini Pro | Cost-effective, fast |
| **Anthropic Claude** | Claude 3 Opus/Sonnet | Long-form content |
| **HuggingFace** | Mixtral, Llama | Open-source alternative |

## Project Structure

```
ai-academician/
├── src/
│   ├── agents/           # 8 specialized AI agents
│   ├── llm/              # LLM provider implementations
│   ├── search/           # Google & arXiv integrations
│   ├── citations/        # APA, MLA, Chicago, IEEE, Harvard
│   ├── export/           # PDF, DOCX, LaTeX exporters
│   ├── models/           # Data models
│   ├── storage/          # SQLite & file management
│   ├── utils/            # Utilities & helpers
│   ├── config.py         # Configuration management
│   ├── orchestrator.py   # Agent coordination
│   └── main.py           # CLI entry point
├── tests/                # Test suite
├── .env.example          # Environment template
├── pyproject.toml        # Project configuration
└── README.md
```

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run with coverage
pytest --cov=src

# Code quality
black src tests        # Format
ruff check src tests   # Lint
mypy src               # Type check
```

## API Keys Setup

<details>
<summary><b>Google Custom Search</b></summary>

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a project and enable Custom Search API
3. Create credentials (API Key)
4. Go to [Programmable Search Engine](https://programmablesearchengine.google.com/)
5. Create a search engine and get the Search Engine ID
</details>

<details>
<summary><b>LLM Providers</b></summary>

- **OpenAI**: [platform.openai.com](https://platform.openai.com/)
- **Google Gemini**: [makersuite.google.com](https://makersuite.google.com/)
- **Anthropic Claude**: [console.anthropic.com](https://console.anthropic.com/)
- **HuggingFace**: [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)
</details>

## Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Security

For security concerns, please see our [Security Policy](SECURITY.md).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

Built with:
- [OpenAI](https://openai.com/) | [Google AI](https://ai.google.dev/) | [Anthropic](https://www.anthropic.com/)
- [arXiv API](https://arxiv.org/help/api/) | [Google Custom Search](https://developers.google.com/custom-search)

---

<p align="center">
  <sub>Built with passion by <a href="https://autospaien.com">AutoSpaien Pvt Ltd</a></sub>
</p>
