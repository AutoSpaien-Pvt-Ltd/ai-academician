# Tasks: AI Academician - Multi-Agent Research Paper Writing System

**Input**: Design documents from `/specs/001-multi-agent-research/`
**Prerequisites**: plan.md (required), spec.md (required)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create project directory structure as defined in plan.md
- [ ] T002 Initialize Python project with pyproject.toml and dependencies
- [ ] T003 [P] Create .env.example with required API keys template
- [ ] T004 [P] Configure logging in src/utils/logger.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY agent implementation

- [ ] T005 Create base agent class in src/agents/base.py
- [ ] T006 [P] Create base LLM provider interface in src/llm/base.py
- [ ] T007 [P] Create data models in src/models/ (session.py, source.py, paper.py, review.py, citation.py)
- [ ] T008 [P] Set up SQLite database layer in src/storage/database.py
- [ ] T009 [P] Create file manager in src/storage/file_manager.py
- [ ] T010 Create configuration management in src/config.py
- [ ] T011 [P] Implement retry utility with exponential backoff in src/utils/retry.py
- [ ] T012 [P] Implement text utilities in src/utils/text_utils.py

**Checkpoint**: Foundation ready - agent implementation can begin

---

## Phase 3: User Story 1 - Complete Research Paper Generation (P1)

**Goal**: End-to-end paper generation from topic to final document

### 3.1 LLM Provider Implementation

- [ ] T013 [P] [US1] Implement OpenAI provider in src/llm/openai_provider.py
- [ ] T014 [P] [US1] Implement Gemini provider in src/llm/gemini_provider.py
- [ ] T015 [P] [US1] Implement Claude provider in src/llm/claude_provider.py
- [ ] T016 [P] [US1] Implement HuggingFace provider in src/llm/huggingface_provider.py
- [ ] T017 [US1] Create LLM provider factory with fallback in src/llm/__init__.py

### 3.2 Search API Implementation

- [ ] T018 [P] [US1] Implement Google Custom Search in src/search/google_search.py
- [ ] T019 [P] [US1] Implement arXiv search in src/search/arxiv_search.py

### 3.3 Agent Implementation (Core Pipeline)

- [ ] T020 [US1] Implement Research Agent in src/agents/research_agent.py
- [ ] T021 [US1] Implement Agent 1 (Source Finder) in src/agents/source_finder.py
- [ ] T022 [US1] Implement Agent 2 (Summarizer) in src/agents/summarizer.py
- [ ] T023 [US1] Implement Agent 3 (Planner) in src/agents/planner.py
- [ ] T024 [US1] Implement Agent 4 (Body Writer) in src/agents/body_writer.py
- [ ] T025 [US1] Implement Agent 5 (Intro Writer) in src/agents/intro_writer.py
- [ ] T026 [US1] Implement Agent 6 (Reviewer) in src/agents/reviewer.py
- [ ] T027 [US1] Implement Agent 7 (Editor) in src/agents/editor.py

### 3.4 Orchestrator

- [ ] T028 [US1] Implement orchestrator in src/orchestrator.py
- [ ] T029 [US1] Implement agent workflow and state management

**Checkpoint**: Core paper generation pipeline functional

---

## Phase 4: User Story 2 - Interactive Topic Refinement (P1)

**Goal**: Research Agent can refine vague topics through conversation

- [ ] T030 [US2] Add clarifying question generation to Research Agent
- [ ] T031 [US2] Add academic title formulation logic
- [ ] T032 [US2] Add user preference collection (citation style, word count, journal)

**Checkpoint**: Interactive topic refinement working

---

## Phase 5: User Story 3 - Source Discovery (P1)

**Goal**: Agent 1 discovers 20+ relevant sources from Google and arXiv

- [ ] T033 [US3] Add relevance scoring to source finder
- [ ] T034 [US3] Add source deduplication logic
- [ ] T035 [US3] Add credibility rating system
- [ ] T036 [US3] Implement minimum 20 sources requirement

**Checkpoint**: Source discovery returns quality sources

---

## Phase 6: User Story 4 - Literature Review (P2)

**Goal**: Generate comprehensive literature review with themes

- [ ] T037 [US4] Add theme identification to Agent 3 (Planner)
- [ ] T038 [US4] Add research gap analysis to Agent 3
- [ ] T039 [US4] Implement thematic synthesis in Agent 4

**Checkpoint**: Literature review with themes generated

---

## Phase 7: User Story 5 - Multi-Format Export (P2)

**Goal**: Export papers in PDF, Word, and LaTeX formats

- [ ] T040 [P] [US5] Implement PDF exporter in src/export/pdf_exporter.py
- [ ] T041 [P] [US5] Implement Word exporter in src/export/docx_exporter.py
- [ ] T042 [P] [US5] Implement LaTeX exporter in src/export/latex_exporter.py
- [ ] T043 [US5] Create base exporter interface in src/export/base.py

**Checkpoint**: All three export formats working

---

## Phase 8: User Story 6 - Quality Review Cycle (P2)

**Goal**: Papers undergo minimum 2 review cycles

- [ ] T044 [US6] Implement review cycle counter in Agent 6
- [ ] T045 [US6] Add issue categorization (missing citation, inconsistency, vague claim)
- [ ] T046 [US6] Implement severity assessment (critical, major, minor)
- [ ] T047 [US6] Add "never approve first instance" logic
- [ ] T048 [US6] Implement max 5 cycles limit

**Checkpoint**: Review loop enforces quality standards

---

## Phase 9: User Story 7 - Citation Style Management (P3)

**Goal**: Support all citation styles with consistent formatting

- [ ] T049 [P] [US7] Implement APA formatter in src/citations/apa.py
- [ ] T050 [P] [US7] Implement MLA formatter in src/citations/mla.py
- [ ] T051 [P] [US7] Implement Chicago formatter in src/citations/chicago.py
- [ ] T052 [P] [US7] Implement IEEE formatter in src/citations/ieee.py
- [ ] T053 [P] [US7] Implement Harvard formatter in src/citations/harvard.py
- [ ] T054 [US7] Create base citation formatter in src/citations/base.py

**Checkpoint**: All citation styles format correctly

---

## Phase 10: User Story 8 - LLM Provider Flexibility (P3)

**Goal**: Configure different LLM providers per agent

- [ ] T055 [US8] Add per-agent LLM configuration
- [ ] T056 [US8] Implement provider fallback mechanism
- [ ] T057 [US8] Add provider health checking

**Checkpoint**: LLM providers configurable and fallback working

---

## Phase 11: CLI & Integration

**Purpose**: User interface and final integration

- [ ] T058 Create CLI entry point in src/main.py
- [ ] T059 Add interactive mode with prompts
- [ ] T060 Add progress display during generation
- [ ] T061 Add session save/resume capability

**Checkpoint**: CLI fully functional

---

## Phase 12: Polish & Documentation

**Purpose**: Final polish and documentation

- [ ] T062 [P] Create README.md with usage instructions
- [ ] T063 [P] Add example configuration files
- [ ] T064 [P] Create unit tests in tests/unit/
- [ ] T065 [P] Create integration tests in tests/integration/
- [ ] T066 Final code cleanup and refactoring

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies
- **Phase 2 (Foundational)**: Depends on Phase 1
- **Phase 3-5 (P1 Stories)**: Depend on Phase 2, can run sequentially
- **Phase 6-8 (P2 Stories)**: Depend on Phase 3-5
- **Phase 9-10 (P3 Stories)**: Depend on Phase 2
- **Phase 11 (CLI)**: Depends on all agent phases
- **Phase 12 (Polish)**: Depends on all phases

### Parallel Opportunities

- All tasks marked [P] within same phase can run in parallel
- LLM providers (T013-T016) can be implemented in parallel
- Search APIs (T018-T019) can be implemented in parallel
- Citation formatters (T049-T053) can be implemented in parallel
- Exporters (T040-T042) can be implemented in parallel

---

## Total: 66 Tasks
