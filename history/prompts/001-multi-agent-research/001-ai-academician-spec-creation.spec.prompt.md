---
id: 001
title: AI Academician Spec Creation
stage: spec
date: 2026-01-21
surface: agent
model: claude-opus-4-5-20251101
feature: 001-multi-agent-research
branch: 001-multi-agent-research
user: TechTiesIbrahim
command: /sp.specify
labels: ["multi-agent", "research-paper", "openai-agents-sdk", "specification"]
links:
  spec: specs/001-multi-agent-research/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/001-multi-agent-research/spec.md
  - specs/001-multi-agent-research/checklists/requirements.md
  - history/prompts/001-multi-agent-research/001-ai-academician-spec-creation.spec.prompt.md
tests:
  - N/A (specification phase)
---

## Prompt

Aik AI researcher project krty hein. Agents kuch aisy hn gy
Research Agent: Gets user input and draws the title like an academic researcher for research paper. Or communicates with the user and asks the user for specific information if the prompt is not clear.
Agent1: Searches the Web and finds primary sources (books) and secondary sources () academic researches articles, reports, web articles and research essays. It reviews the whole research paper again to make sure it is accordance with research journal to which the user wants to get published or check any document for format before returning the final output in pdf format.
Agent2: Review the search results gathered by Agent1 and reads the content of web sources searched by Agent1. Agent2 then writes detailed summary of all search results
Agent3: Reviews the summary of Agent2 and summarises the plan for Research Article. Agent 3 finds gaps in previous researches and plans the research paper. It then securitizes the relevant information from the detailed summary or rough notes taken by Agent2
Agent4: Writes the body of Research paper: Research body includes theoretical framework, research method, literature review and detailed portion/analysis or research of the current paper after research and findings of the current paper. The body portion of research paper should be between 15000 words to 22000 words or need to be modified according to user's need. It write in active voice always, like an academic writer
Agent5: writes Introduction based on the Agent4 body content, writes conclusion of the whole research and Abstract at the end.
Agent6: reviews the whole research paper and finds inconsistencies in paragraphs, vague ideas without any research backing or evidence, finds missing footnotes or finds places where appropriate references or footnotes were required. Agent6 reviews the paper and finds room for improvement. Never approve at first instance. Only approve after reviewing 2 times at minimum.
Agents7: Edits the content based on Agent6 findings and sends

User preferences gathered via clarifying questions:
- Framework: OpenAI Agents SDK (primary)
- LLMs: Gemini, HuggingFace models, Claude (flexible)
- Search APIs: Google Search + arXiv
- Citation styles: User choice (APA, MLA, Chicago, IEEE, Harvard)
- Output formats: PDF + Word + LaTeX

## Response snapshot

Created comprehensive feature specification for AI Academician multi-agent research paper writing system with:

1. **8 Specialized Agents** defined with clear responsibilities:
   - Research Agent (User Liaison)
   - Agent 1 (Source Finder + Format Review)
   - Agent 2 (Content Summarizer)
   - Agent 3 (Research Planner)
   - Agent 4 (Body Writer - 15k-22k words)
   - Agent 5 (Intro/Conclusion/Abstract Writer)
   - Agent 6 (Quality Reviewer - min 2 review cycles)
   - Agent 7 (Editor)

2. **8 User Stories** with P1-P3 priorities and acceptance scenarios

3. **54 Functional Requirements** covering all agents and system capabilities

4. **10 Success Criteria** with measurable outcomes

5. **Edge cases**, **assumptions**, **out of scope items**, and **dependencies** documented

## Outcome

- Impact: Created complete feature specification ready for planning phase
- Tests: N/A (specification phase)
- Files: spec.md (359 lines), checklists/requirements.md
- Next prompts: /sp.plan to create implementation plan
- Reflection: User provided detailed agent descriptions in Urdu/English mix; successfully captured all requirements and clarified technical choices through interactive questions

## Evaluation notes (flywheel)

- Failure modes observed: None - spec completed successfully
- Graders run and results (PASS/FAIL): Manual validation PASS - all checklist items verified
- Prompt variant (if applicable): Standard /sp.specify with interactive clarification
- Next experiment (smallest change to try): Consider adding more specific word count targets per section in plan phase
