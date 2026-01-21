# Implementation Plan: AI Academician - Multi-Agent Research Paper Writing System

**Branch**: `001-multi-agent-research` | **Date**: 2026-01-21 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-multi-agent-research/spec.md`

---

## Summary

AI Academician is a multi-agent system for automated academic research paper generation. The system uses OpenAI Agents SDK to orchestrate 8 specialized agents that collaborate to produce publication-ready research papers (15,000-22,000 words). The technical approach leverages Python with async architecture, Google Search + arXiv for source discovery, and supports multiple LLM providers (Gemini, HuggingFace, Claude).

---

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**:
- `openai-agents` (OpenAI Agents SDK)
- `google-api-python-client` (Google Custom Search)
- `arxiv` (arXiv API wrapper)
- `anthropic` (Claude API)
- `google-generativeai` (Gemini API)
- `transformers` (HuggingFace models)
- `python-docx` (Word export)
- `reportlab` / `weasyprint` (PDF export)
- `pylatex` (LaTeX generation)

**Storage**: SQLite (session persistence) + File system (artifacts)
**Testing**: pytest with pytest-asyncio
**Target Platform**: Cross-platform CLI (Windows, macOS, Linux)
**Project Type**: Single CLI application
**Performance Goals**:
- Complete paper generation within 2-4 hours
- Handle 50+ sources per paper
- Support concurrent API calls

**Constraints**:
- Rate limiting for external APIs
- LLM context window limits
- Memory management for large documents

**Scale/Scope**: Single-user CLI, batch processing

---

## Project Structure

### Documentation (this feature)

```text
specs/001-multi-agent-research/
├── spec.md              # Feature specification
├── plan.md              # This file
├── research.md          # Research findings
├── data-model.md        # Entity definitions
├── contracts/           # Agent communication contracts
│   ├── research-agent.md
│   ├── source-finder.md
│   ├── summarizer.md
│   ├── planner.md
│   ├── body-writer.md
│   ├── intro-writer.md
│   ├── reviewer.md
│   └── editor.md
├── checklists/
│   └── requirements.md
└── tasks.md             # Implementation tasks
```

### Source Code (repository root)

```text
src/
├── __init__.py
├── main.py                    # CLI entry point
├── config.py                  # Configuration management
├── orchestrator.py            # Agent orchestration logic
│
├── agents/                    # All 8 agents
│   ├── __init__.py
│   ├── base.py               # Base agent class
│   ├── research_agent.py     # User interaction & title formulation
│   ├── source_finder.py      # Web/academic search (Agent 1)
│   ├── summarizer.py         # Content summarization (Agent 2)
│   ├── planner.py            # Research planning (Agent 3)
│   ├── body_writer.py        # Paper body writing (Agent 4)
│   ├── intro_writer.py       # Intro/conclusion/abstract (Agent 5)
│   ├── reviewer.py           # Quality review (Agent 6)
│   └── editor.py             # Editing (Agent 7)
│
├── llm/                       # LLM provider abstraction
│   ├── __init__.py
│   ├── base.py               # Base LLM interface
│   ├── openai_provider.py    # OpenAI/GPT models
│   ├── gemini_provider.py    # Google Gemini
│   ├── claude_provider.py    # Anthropic Claude
│   └── huggingface_provider.py # HuggingFace models
│
├── search/                    # Search APIs
│   ├── __init__.py
│   ├── google_search.py      # Google Custom Search
│   └── arxiv_search.py       # arXiv API
│
├── models/                    # Data models
│   ├── __init__.py
│   ├── session.py            # ResearchSession
│   ├── source.py             # Source entity
│   ├── paper.py              # PaperDraft, PaperOutline
│   ├── review.py             # ReviewFeedback
│   └── citation.py           # Citation handling
│
├── export/                    # Export functionality
│   ├── __init__.py
│   ├── base.py               # Base exporter
│   ├── pdf_exporter.py       # PDF generation
│   ├── docx_exporter.py      # Word document
│   └── latex_exporter.py     # LaTeX + BibTeX
│
├── citations/                 # Citation formatting
│   ├── __init__.py
│   ├── base.py               # Base citation formatter
│   ├── apa.py                # APA 7th edition
│   ├── mla.py                # MLA format
│   ├── chicago.py            # Chicago style
│   ├── ieee.py               # IEEE format
│   └── harvard.py            # Harvard style
│
├── storage/                   # Persistence
│   ├── __init__.py
│   ├── database.py           # SQLite operations
│   └── file_manager.py       # Artifact file management
│
└── utils/                     # Utilities
    ├── __init__.py
    ├── logger.py             # Logging configuration
    ├── text_utils.py         # Text processing
    └── retry.py              # Retry logic with backoff

tests/
├── __init__.py
├── conftest.py               # Pytest fixtures
├── unit/
│   ├── test_agents/
│   ├── test_llm/
│   ├── test_search/
│   ├── test_export/
│   └── test_citations/
├── integration/
│   ├── test_orchestrator.py
│   ├── test_full_pipeline.py
│   └── test_export_formats.py
└── fixtures/
    ├── sample_sources.json
    └── sample_paper.json
```

**Structure Decision**: Single project structure chosen as this is a CLI application without frontend/backend separation. All components are Python modules organized by domain responsibility.

---

## Agent Architecture

### Agent Communication Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                         ORCHESTRATOR                                 │
│  (Manages workflow, state, and agent handoffs)                      │
└─────────────────────────────────────────────────────────────────────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        ▼                       ▼                       ▼
┌───────────────┐      ┌───────────────┐      ┌───────────────┐
│ Research Agent│ ──▶  │   Agent 1     │ ──▶  │   Agent 2     │
│ (User Liaison)│      │(Source Finder)│      │ (Summarizer)  │
└───────────────┘      └───────────────┘      └───────────────┘
                                                      │
                                                      ▼
                              ┌───────────────────────────────────────┐
                              │              Agent 3                   │
                              │        (Research Planner)              │
                              │   - Identifies themes & gaps           │
                              │   - Creates paper outline              │
                              └───────────────────────────────────────┘
                                                      │
                                                      ▼
                              ┌───────────────────────────────────────┐
                              │              Agent 4                   │
                              │          (Body Writer)                 │
                              │   - Theoretical framework              │
                              │   - Methodology                        │
                              │   - Literature review                  │
                              │   - Analysis (15k-22k words)           │
                              └───────────────────────────────────────┘
                                                      │
                                                      ▼
                              ┌───────────────────────────────────────┐
                              │              Agent 5                   │
                              │      (Intro/Conclusion Writer)         │
                              │   - Introduction                       │
                              │   - Conclusion                         │
                              │   - Abstract                           │
                              └───────────────────────────────────────┘
                                                      │
                                                      ▼
                    ┌─────────────────────────────────────────────────┐
                    │                 REVIEW LOOP                      │
                    │  ┌─────────────┐         ┌─────────────┐        │
                    │  │   Agent 6   │ ──────▶ │   Agent 7   │        │
                    │  │ (Reviewer)  │ ◀────── │  (Editor)   │        │
                    │  └─────────────┘         └─────────────┘        │
                    │       │                                          │
                    │       ▼ (after min 2 cycles)                     │
                    │   [APPROVED]                                     │
                    └─────────────────────────────────────────────────┘
                                                      │
                                                      ▼
                              ┌───────────────────────────────────────┐
                              │         Agent 1 (Final)                │
                              │   - Format verification                │
                              │   - Export (PDF/Word/LaTeX)            │
                              └───────────────────────────────────────┘
```

### Agent State Machine

```
STATES:
- IDLE: Agent ready for task
- PROCESSING: Agent working on task
- WAITING_INPUT: Agent needs user input
- COMPLETED: Task finished successfully
- ERROR: Task failed (retryable)
- BLOCKED: Waiting for dependency

TRANSITIONS:
IDLE → PROCESSING: Receive task from orchestrator
PROCESSING → COMPLETED: Task finished
PROCESSING → ERROR: Task failed
PROCESSING → WAITING_INPUT: Need clarification
WAITING_INPUT → PROCESSING: User provided input
ERROR → PROCESSING: Retry triggered
COMPLETED → IDLE: Ready for next task
```

---

## Data Models

### Core Entities

```python
# ResearchSession
{
    "id": "uuid",
    "topic": "string",
    "title": "string (formal academic title)",
    "citation_style": "enum: APA|MLA|CHICAGO|IEEE|HARVARD",
    "target_word_count": "int (15000-22000)",
    "target_journal": "string (optional)",
    "status": "enum: DRAFT|IN_PROGRESS|REVIEW|COMPLETED|FAILED",
    "created_at": "datetime",
    "updated_at": "datetime",
    "llm_config": {
        "default_provider": "string",
        "agent_overrides": {"agent_name": "provider_name"}
    }
}

# Source
{
    "id": "uuid",
    "session_id": "uuid (FK)",
    "title": "string",
    "authors": ["string"],
    "year": "int",
    "url": "string",
    "doi": "string (optional)",
    "abstract": "string",
    "full_text": "string (if accessible)",
    "summary": "string (Agent 2 output)",
    "source_type": "enum: ARXIV|WEB|BOOK|JOURNAL",
    "relevance_score": "float (0-1)",
    "credibility_rating": "enum: HIGH|MEDIUM|LOW",
    "is_accessible": "boolean"
}

# PaperOutline
{
    "id": "uuid",
    "session_id": "uuid (FK)",
    "sections": [
        {
            "title": "string",
            "type": "enum: ABSTRACT|INTRO|LIT_REVIEW|METHODOLOGY|ANALYSIS|CONCLUSION|REFERENCES",
            "target_words": "int",
            "source_ids": ["uuid"],
            "subsections": [...]
        }
    ],
    "themes": ["string"],
    "research_gaps": ["string"]
}

# PaperDraft
{
    "id": "uuid",
    "session_id": "uuid (FK)",
    "version": "int",
    "sections": {
        "abstract": "string",
        "introduction": "string",
        "literature_review": "string",
        "methodology": "string",
        "theoretical_framework": "string",
        "analysis": "string",
        "conclusion": "string",
        "references": "string"
    },
    "word_count": "int",
    "status": "enum: DRAFT|IN_REVIEW|APPROVED",
    "review_cycle": "int"
}

# ReviewFeedback
{
    "id": "uuid",
    "draft_id": "uuid (FK)",
    "cycle": "int",
    "issues": [
        {
            "id": "uuid",
            "type": "enum: MISSING_CITATION|INCONSISTENCY|VAGUE_CLAIM|FORMAT_ERROR|STYLE_ISSUE",
            "severity": "enum: CRITICAL|MAJOR|MINOR",
            "location": {"section": "string", "paragraph": "int", "text_excerpt": "string"},
            "description": "string",
            "suggested_fix": "string",
            "resolved": "boolean"
        }
    ],
    "overall_assessment": "string",
    "approved": "boolean"
}

# Citation
{
    "id": "uuid",
    "source_id": "uuid (FK)",
    "style": "enum: APA|MLA|CHICAGO|IEEE|HARVARD",
    "in_text": "string",
    "bibliography": "string",
    "is_complete": "boolean"
}
```

---

## Implementation Phases

### Phase 1: Foundation (Setup & Core Infrastructure)

1. **Project Setup**
   - Initialize Python project with pyproject.toml
   - Set up virtual environment
   - Configure pytest and logging
   - Create directory structure

2. **Configuration System**
   - Environment variable handling
   - API key management
   - LLM provider configuration
   - Default settings

3. **Base Classes**
   - BaseAgent abstract class
   - BaseLLMProvider interface
   - BaseExporter interface
   - BaseCitationFormatter interface

4. **Storage Layer**
   - SQLite database setup
   - Session persistence
   - File artifact management

### Phase 2: LLM & Search Integration

1. **LLM Providers**
   - OpenAI provider (GPT-4)
   - Gemini provider
   - Claude provider
   - HuggingFace provider
   - Provider factory with fallback

2. **Search APIs**
   - Google Custom Search integration
   - arXiv API integration
   - Result ranking and filtering
   - Rate limiting and retry logic

### Phase 3: Agent Implementation

1. **Research Agent** (User Liaison)
   - Natural language input processing
   - Clarifying question generation
   - Academic title formulation
   - User preference collection

2. **Agent 1** (Source Finder)
   - Multi-source search orchestration
   - Result deduplication
   - Relevance scoring
   - Format verification (final stage)

3. **Agent 2** (Content Summarizer)
   - Source content extraction
   - Summary generation (500-1000 words each)
   - Key findings identification
   - Accessibility handling

4. **Agent 3** (Research Planner)
   - Theme identification
   - Gap analysis
   - Outline generation
   - Source-to-section mapping

5. **Agent 4** (Body Writer)
   - Section-by-section generation
   - Word count management
   - Citation integration
   - Active voice enforcement

6. **Agent 5** (Intro/Conclusion Writer)
   - Context-aware introduction
   - Summary-based conclusion
   - Abstract generation
   - Alignment verification

7. **Agent 6** (Quality Reviewer)
   - Multi-pass review logic
   - Issue categorization
   - Severity assessment
   - Approval workflow

8. **Agent 7** (Editor)
   - Issue-based editing
   - Style preservation
   - Change tracking
   - Re-review triggering

### Phase 4: Orchestrator & Workflow

1. **Orchestrator**
   - Agent lifecycle management
   - State machine implementation
   - Error handling and recovery
   - Progress reporting

2. **Workflow Engine**
   - Sequential execution
   - Review loop management
   - Timeout handling
   - Checkpoint/resume capability

### Phase 5: Export & Citations

1. **Citation Formatters**
   - APA 7th edition
   - MLA
   - Chicago
   - IEEE
   - Harvard

2. **Exporters**
   - PDF generation
   - Word document creation
   - LaTeX + BibTeX output

### Phase 6: CLI & Polish

1. **CLI Interface**
   - Command-line argument parsing
   - Interactive mode
   - Progress display
   - Error messages

2. **Testing & Documentation**
   - Unit tests for all modules
   - Integration tests
   - README and usage guide

---

## API Contracts

### Agent Communication Protocol

Each agent receives and returns standardized messages:

```python
# Agent Input
{
    "task_id": "uuid",
    "session_id": "uuid",
    "action": "string (agent-specific)",
    "payload": {
        # Action-specific data
    },
    "context": {
        "previous_outputs": {...},
        "session_state": {...}
    }
}

# Agent Output
{
    "task_id": "uuid",
    "status": "SUCCESS|FAILURE|NEEDS_INPUT",
    "result": {
        # Action-specific output
    },
    "metadata": {
        "tokens_used": "int",
        "processing_time": "float",
        "llm_provider": "string"
    },
    "errors": [
        {"code": "string", "message": "string"}
    ],
    "next_action": "string (optional)"
}
```

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| LLM rate limiting | Implement exponential backoff, provider fallback |
| Context window limits | Chunk large documents, summarize intermediate outputs |
| API costs | Track token usage, implement budget limits |
| Quality variance | Multi-cycle review, human-in-loop options |
| Long processing time | Progress updates, checkpoint/resume |

---

## Success Validation

Plan will be considered successful when:

1. All 8 agents are implemented and tested
2. End-to-end paper generation completes successfully
3. All three export formats produce valid output
4. All five citation styles format correctly
5. Review loop completes with minimum 2 cycles
6. CLI provides clear progress feedback
