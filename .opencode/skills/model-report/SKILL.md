---
name: model-report
description: Generate a traceable Markdown design report from confirmed Concept Stage and separately modeled PoC SysML source files, using only model declarations and doc text as factual evidence.
---

# SysML model report

Follow [the report format and evidence rules](references/report-format.md). This is a reporting method, not a modeling workflow: never edit or complete source models, notebooks, or views.

## Start with source and metadata confirmation

1. Use the current chat and the active notebook only to identify the likely project. If notebook state matters, use Jupyter AI's bundled notebook tools and read the live notebook, including unsaved edits. Do not inspect `.chat` files, recorder data, or transcripts.
2. Inspect only the student-owned model workspace, normally `/home/keio/work/models`. Exclude hidden directories and `.ipynb_checkpoints`. Do not traverse symlinks. List `.sysml` candidates and inspect their declarations, package names, imports, and explicit relationships. Treat names such as `realization` as useful hints, not proof. Resolve a dependency only when model imports/references and file declarations establish its role. Samples and course references stay read-only and are not report sources unless the student explicitly confirms a supported source path.
3. Build a source inventory before writing: file, qualified name, kind, source line, Concept or named realization ownership, `doc` text, aspects represented, relationships, and views/expose rules. You may run `scripts/model_report_inventory.py` on the proposed source files as an aid; it is a constrained inventory, not a full SysML parser. Verify uncertain syntax against the pinned kernel when possible.
4. Propose the concept source and each in-scope realization source/dependency. Ask the student to confirm project identity and the complete source-file set before generating anything. If there are multiple plausible concepts, realization candidates, unresolved dependencies, or mixed views without a clear primary section, ask the student to choose. Never silently select a similarly named file.
5. If the model exists only in unsaved notebook cells, ask the student to save it to a distinct `.sysml` file under `/home/keio/work/models` or confirm a supported source path. Do not create or modify the canonical model.
6. Gather or confirm the student's full name, report title, subtitle, and language. Never infer a student's name. Suggest title/subtitle only from verified model `doc` text. Ask these metadata questions together. Use English only when the course context establishes it as the default.
7. Show a compact final confirmation summary with project, selected concept path, each selected PoC path (or none), name, title, subtitle, language, output path, and any existing output collision. Wait for explicit confirmation before generating. If `reports/<slug>.md` exists, ask whether to overwrite or use a timestamped/versioned path.

## Ground and compose the report

- Only confirmed SysML source declarations, their explicit `doc` bodies, relationships, and validated existing views can support factual claims. Confirmed cover metadata is allowed but is not model evidence. Do not use chat, notebook prose, comments, model names, or external sources as explanatory evidence.
- Summarize `doc` text in concise continuous prose without losing conditions, caveats, or terminology. A missing `doc` means “undocumented”; a declaration name alone does not explain its purpose. For an asserted relationship with no documented rationale, describe what is connected and say its rationale is unspecified.
- Classify actual constructs into requirements, structure, and behavior. Keep all three Concept headings and state “Not found in the confirmed source model” when absent. In PoC sections include only represented aspects and call out gaps. Keep alternatives as separate realizations.
- State whether claims are modeled intent, source-declared relationships, manufacturer/specification claims reproduced in `doc`, or observed kernel output. Do not turn a declaration or successful render into a claim of feasibility, test success, or full SysML v2 conformance.
- Use the exact report outline and traceability table in `references/report-format.md`. Include concise source paths and declaration/view qualified names, with lines where available.

## Existing views only

1. Inventory every `view` in the confirmed source scope, its qualified name, `expose` rules, associated elements, and source path. Classify by exposed content and documented purpose, not by view name alone. Do not create views or use the old `report-render` marker.
2. If an existing mixed view has no clear primary section, ask the student where to place it. Never duplicate a view across report sections unless explicitly requested.
3. Render only selected, in-scope views using the active notebook's attached OpenSysML kernel and bundled Jupyter MCP tools. Follow the installed `%load` order and `%render <qualified-view-name> <format>` contract. Read returned MIME/output before embedding. Each selected view is rendered once. Do not render arbitrary elements or add temporary cells/views.
4. Use Mermaid fences for actual Mermaid source, embed returned Markdown as Markdown, and persist actual supported image output only. Put image files in `reports/assets/<slug>/` with deterministic collision-safe names. Do not fabricate screenshots, diagrams, or placeholders.
5. If the kernel is unavailable, write a clearly partial text-only report and list all discovered views as not rendered. If a render fails, omit its diagram, record the actual concise error and continue. Never report success without returned output evidence.

## Write safely and finish

- Write only the confirmed Markdown report and its supporting assets under `/home/keio/work/reports`; do not write into the course repository or read-only samples. Sanitize the slug and ensure the resolved path remains directly under `reports/`. Copy the official `/opt/course/docs/keio-logo.png` into `reports/assets/<slug>/keio-logo.png`; use the relative link `assets/<slug>/keio-logo.png` from the report. If that runtime file is missing, report the blocker and do not substitute another logo.
- Create the report atomically after confirmation. Do not mutate source files, notebook cells, views, evidence, or chat files. Do not publish/share it.
- Finish with the output path and concise grounded summary; list included Concept aspects and each realization, exact successfully rendered view names grouped by section, material missing docs/aspects/views/errors/ambiguities, and label any incomplete result “Partial report.”
