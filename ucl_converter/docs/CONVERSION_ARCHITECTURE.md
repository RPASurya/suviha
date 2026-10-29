# UCL conversion architecture and next implementation milestones

## Current pipeline
1. Validate upload size and extension.
2. Safely inspect ZIP members; reject absolute/traversal paths.
3. Identify source platform and collect supported text files.
4. Load encrypted provider credentials from SQLite.
5. Build a project-aware prompt with inventory and source file contents.
6. Ask the selected LLM to emit a target file manifest and conversion report.
7. Parse the manifest and reject unsafe output paths.
8. Perform static checks on XAML/XML, JSON and Python files.
9. Add conversion report and package output as ZIP.

## Recommended next milestones

### Milestone 2 — Intermediate representation (IR)
Create a versioned platform-neutral process graph with nodes, edges, expressions, variables, arguments, data types, selectors, external integrations, exception routes, and project references. Store source references on every IR element for traceability.

### Milestone 3 — Multi-pass project analysis
Use an inventory pass, dependency/reference graph, per-workflow semantic extraction, IR consistency validation, and target code generation. Avoid sending all project content in one model call when large.

### Milestone 4 — UiPath-specific generators
Create separate generators for Sequence, Flowchart, State Machine and supported Long Running Workflow constructs. Generate project.json and XAML against explicit package/version profiles. Add fixtures for each supported Studio version.

### Milestone 5 — Verification
Run XML/XAML parse checks, package/reference checks, variable/argument resolution checks, expression checks, and target-specific linting. Where possible, execute tests in isolated Windows agents with the matching UiPath Studio/Robot version. Report test evidence separately from LLM confidence.

### Milestone 6 — Source format adapters
Implement and test native Blue Prism release/export parsing for documented schemas and known versions. Preserve object/process references, pages/stages, data items, collections, loops, decisions, calculations, exception paths, and application model details. Never infer missing source details silently.

### Milestone 7 — Production readiness
Add user accounts/roles, per-user API keys or billing quotas, job queue, audit trail, retention and deletion controls, rate limiting, secrets scanning, sandboxed workers, and deployment health checks.
