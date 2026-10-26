# Model report format and evidence rules

## Required Markdown structure

```markdown
![Keio University](assets/<project-slug>/keio-logo.png)

# <Confirmed report title>

*<Confirmed subtitle>*

**Student:** <Confirmed full name>

**Course:** Agentic Product Concept Modeling 2026, Keio University

**Project:** <Confirmed project>

**Date:** <Actual generation date>

## Project Summary

<Purpose and scope grounded in confirmed model doc declarations.>

# Part I. Concept Design (WHAT)

## 1. Requirements Model

<Grounded prose, or explicitly state the aspect is absent. Existing relevant views go at the end.>

## 2. Structural Model

<Grounded prose, or explicitly state the aspect is absent. Existing relevant views go at the end.>

## 3. Behavioral Model

<Grounded prose, or explicitly state the aspect is absent. Existing relevant views go at the end.>

# Part II. PoC Realizations (HOW)

## PoC realization: <Confirmed candidate name>

<Grounded introduction and traceability to concept.>

### Requirements and criteria / applicable links

<Include only source-supported links; state when link evidence is missing.>

### Structure

<Documented candidate structure/interfaces and matching existing views.>

### Behavior

<Documented behavior/integration and matching existing views.>

## Documentation and Evidence Gaps

- <Missing aspect, undocumented element, absent/ambiguous view, unresolved link, or actual render failure.>

## Source Traceability

| Report section or artifact | SysML element/view | Source path and line | Evidence note |
| --- | --- | --- | --- |
| ... | `Package::Element` | `models/file.sysml:12` | `doc` summary / declared relationship / render result |
```

Retain all three Concept subsections even when an aspect is absent. Use this exact explicit absence wording where applicable: **Not found in the confirmed source model.** If no realization was confirmed, retain Part II and explain that no PoC realization file was confirmed and the PoC is not yet modeled. Do not invent an empty PoC candidate.

## Evidence and language

- Facts come only from the confirmed `.sysml` files and explicit project dependencies: SysML declarations, `doc` bodies, declared relationships, and validated view output. The student's confirmed cover metadata is not model evidence.
- A normal `//` or `/* ... */` comment is not a `doc` declaration. Do not use it to explain an element. An element with no explicit `doc` is “undocumented.”
- Preserve requirements' conditions, thresholds, alternatives, qualifications, and unresolved decisions when condensing `doc`. Prefer short paragraphs over raw documentation dumps.
- A declared relationship can be described structurally, but do not infer why it exists. Say “the model declares …; its rationale is unspecified” when needed.
- Preserve evidence status. For example, a `doc` statement repeating a vendor claim is a model-documented claim, not a verified test. A successful `%render` proves only that the selected view rendered in that kernel session.
- Never fill missing requirements, interfaces, behavior, test results, assumptions, sources, or feasibility conclusions with plausible prose.
- Every nontrivial model-grounded paragraph and each rendered view must map to qualified declarations/views and source paths in the traceability table. Include line numbers if available.

## Views and output

Inventory existing `view` declarations and `expose` rules. Determine placement from what the view exposes and its documentation. Put each rendered Concept view at the end of one matching aspect subsection; put PoC views under the relevant candidate/aspect. Ask where to place a genuinely mixed or ambiguous view. Render each selected view once through the attached kernel and bundled Jupyter MCP tools, and embed only actual returned output: Mermaid source in a `mermaid` fence, returned Markdown as Markdown, or supported image MIME saved under `assets/<slug>/`. Report the qualified name, render format, source, section, and actual success/failure. If rendering is unavailable or fails, omit the diagram and document the status and concise actual error. Never create views, temporary views, arbitrary-element renders, screenshots, or empty placeholders.

## Discovery, confirmation, and failure behavior

Use chat/live notebook state only to identify likely sources. Confirm the project and complete source set before generation. Resolve imports/dependencies from file evidence; ask if ownership is unclear. Exclude hidden/checkpoint folders and unrelated samples. Unsaved notebook-only models need to be saved or a supported source path confirmed. Confirm full name, title, subtitle, and language; do not guess the name. Present the final metadata, paths, and output location and wait for confirmation. Ask before replacing an existing report; offer a timestamped/versioned output path. If no concept source exists, ask for it and do not create a report. A missing PoC allows a concept-only partial report. A missing kernel allows a text-only partial report that lists views not rendered.

Output is one Markdown file at `reports/<safe-project-slug>.md` and any real rendered images at `reports/assets/<safe-project-slug>/`. Its official logo is `assets/<safe-project-slug>/keio-logo.png`. Never follow unrelated symlinks or let the slug escape the reports directory. Only write after confirmation, and use an atomic write. Never read `.chat` files or classroom interaction records.

## Worked examples

### Concept-only partial report

If the confirmed concept contains documented requirements and parts but no actions, retain all headings. Summarize requirements and structure from their `doc` bodies, write “Not found in the confirmed source model” for behavior, and say “No PoC realization file was confirmed; Part II is not yet modeled.” Mark the report **Partial report** in the summary/gaps. Do not treat a similarly named file as a PoC.

### Two independent realizations

If a concept is linked to two separately confirmed realization sources, create separate PoC headings and trace each candidate's declared links and views independently. A relationship named `realizesVoiceCaptureCriterion` supports saying that the model declares that link; absent documented rationale or test output, do not say that the candidate satisfies the criterion.

### Render unavailable

If a confirmed view `ConceptViews::requirementsModel` is in scope but no notebook kernel can be reached, omit a diagram and list `ConceptViews::requirementsModel` as “not rendered (kernel unavailable).” Do not include hypothetical Mermaid. Continue with documented text and mark the report partial.
