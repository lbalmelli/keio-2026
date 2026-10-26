---
name: render-flat-structure
description: Use when a student wants to describe, model, or draw a logical structure — a "flat structure", system structure, boxes-and-lines picture, architecture skeleton, or the parts of a concept and how they connect. Covers eliciting the parts, writing the SysML v2 part definition and connections, adding the interconnection view, loading and rendering it, and verifying the picture. Also use for "render flat", "show the internal components", "embedded structure", "single level embedding", and when a part's own parts must be shown inside it.
---

# Flat structure: describe it, model it, draw it

Produce a **flat structure**: one frame for the owner, its parts as boxes
inside, and `connection` usages as thick **undirected** lines labelled with the
connection name. No ports, no arrows. A part that declares its own parts gets a
frame inside its parent's frame.

Work in the order below. Do not jump to writing SysML before step 1 — the
point of the exercise is that the student decides what the parts are and can
say why each one exists.

## 1. Frame the question (ask, then wait)

Ask for the system in the student's own words, then elicit parts as
**responsibilities**, not products:

- "What does it do, in one sentence?"
- "What has to exist for that to happen? Name each as a job, not a device."
- For each candidate part: "What does *this* one do that no other part does?"
- "Which pairs of parts have to talk to each other, and what passes between
  them?"

Rules while eliciting:

- **A part answers a job.** Two parts with the same job are one part. A part
  whose job nobody can state is cut.
- **Three to seven parts.** Fewer is a box, more is a wiring diagram nobody
  reads. If the student names twelve, ask which of them the reader must see to
  understand the concept, and put the rest inside a nested level.
- **Capability nouns, not vendors.** "Capture", "Storage", "Display",
  "Analytics". If a student says "a Rocware mic" or "a Synology NAS", say so
  plainly: that is a real choice, but it belongs to the PoC stage as a
  realization of a part, not in the concept. Keep the concept abstract.
- **One level by default.** Offer nesting only when the student's description
  already contains sub-parts that matter to the argument — see step 2.

## 2. Choose the shape: one level or nested

Ask: "Does any part need its own internals shown for the picture to make
sense?" Two honest answers:

| Answer | Model | Result |
| --- | --- | --- |
| no (default) | `part capture : Capture;` | one flat frame, boxes side by side |
| yes | `part storage { part drive : Drive; ... }` | nested frame inside the parent |

Nesting is **lexical**: the renderer nests a feature only when the feature
declares that structure itself. So nesting costs you the reusable type — the
sub-structure is then owned by the composite.

`part inner : Inner { ... }` (typed *and* given a body) nests but warns
`Duplicate of inherited member name 'a' from Inner` for each member the type
already declares. Avoid it; pick one side of the trade.

Show the student both renderings once if they hesitate, then let them choose.

## 3. Write the definition

One file, one package, definitions only in the concept model:

```sysml
package IdeaWall {
    part def IdeaWallSystem {
        part capture : Capture;
        part storage : Storage;
        part display : Display;
        part analytics : Analytics;

        connection captureStorage   connect capture   to storage;
        connection storageDisplay   connect storage   to display;
        connection storageAnalytics connect storage   to analytics;
    }
}
```

- `connection <name> connect <a> to <b>;` — undirected. It states that the two
  parts relate, not which way data flows. Unnamed or badly named connections
  make the picture unreadable: name them `sourceSink` (`captureStorage`,
  `storageDisplay`).
- Do **not** add `flow`, ports, interfaces, or arrows at this level unless the
  student's concept genuinely needs a direction; the flat structure's job is
  the skeleton. If they ask for direction, that is a separate view and a
  separate decision.
- Star or hub topologies are fine — if one part mediates all the others, say
  so in words rather than drawing extra lines.

Nested variant:

```sysml
part def IdeaWallSystem {
    part storage {                 // no type: the parts live here
        part drive : Drive;
        part index : Index;
        connection driveIndex connect drive to index;
    }
    part display : Display;
    connection storageDisplay connect storage to display;
}
```

## 4. Add the view

```sysml
package IdeaWallViews {
    private import Views::*;

    view embeddedIdeaWallView {
        expose IdeaWall::IdeaWallSystem;      // the OWNER, not the parts
        render asInterconnectionDiagram;
    }
}
```

Two traps, both verified on this kernel:

- Exposing `a`, `b`, `c` individually gives orphan boxes and no lines.
- Exposing a `part` usage whose members come from its type gives one empty
  box. Expose the definition.

One view per intent. Do not keep a rival view that exposes the same parts
individually.

## 5. Load and render

In the active notebook, on the attached kernel:

```
%load /home/keio/work/models/idea_wall.sysml
%render IdeaWallViews::embeddedIdeaWallView mermaid
```

`%load` must report `✓ package ...` for **every** package before the render
means anything. After editing the `.sysml` file, run `%load` again — the
kernel keeps the last loaded declarations, and `%print` reflects that, not the
file on disk.

Save new models as distinct files in `/home/keio/work/models`. Never edit
course samples. The `.sysml` file is the source of truth; a change to the
picture is a change to the model or the view, then a reload — never
hand-written mermaid.

## 6. Verify before claiming success

Read the returned `text/vnd.mermaid` and count:

| Expected | Check |
| --- | --- |
| one frame per exposed definition | `subgraph nN ["\`*«part def»* **Name**\`"]` |
| one box per declared part | `nN("\`*«part»*\n**name : Type**\`")` |
| one line per declared connection | `nA ===|"connName"| nB` |
| nesting only where declared | child `subgraph` indented inside the parent frame |
| no arrows | no `-->` or `==>` |
| no ports | no `«port»` nodes |

Counts must equal the declarations. Then tell the student, in words: how many
frames, how many parts, which lines, and one judgement — is the picture still
readable, or is the structure overloaded?

## 7. Close the loop

Ask one question that makes the student own the model, e.g. "Pick one
connection: what passes through it, and what would break if it were removed?"
Wait for their answer before proposing more structure.

## Output formats

`%render` accepts `mermaid` (default), `dot`, `d2`, `plantuml`, `text`,
`markdown`. All graph forms nest identically; they differ in how a line that
leaves a nested box is anchored.

| Format | Line leaving a nested box | Use when |
| --- | --- | --- |
| `mermaid` | ends at an invisible `nN_anchor` node inside the box | default, inline in Jupyter |
| `dot` | `ltail="cluster_nN"` — starts at the box border | cleanest picture; real SVG text |
| `d2` | nested path (`n0.n1 -- n0.n4`) | text diagrams, version control |

`dot` also returns `image/svg+xml` with real `<text>` labels, so it survives
JupyterLab's mermaid sanitizer. Prefer it for reports and slides.

## Failure modes

| Symptom | Cause | Fix |
| --- | --- | --- |
| boxes, no lines | view exposes part usages | expose the owning definition |
| one box, nothing inside | exposed a usage whose parts come from its type | expose the type |
| connections drawn as boxes | tree rendering | `render asInterconnectionDiagram` |
| `unresolved reference: <view>` | model not loaded / kernel restarted | re-run `%load` |
| old picture after an edit | file changed, not reloaded | `%load`, then `%render` |
| `"X" is a reserved keyword` | connection named `join`, `and`, `or`, `from`, ... | rename (`joinLink`) or quote (`'join'`) |
| nested level missing | `part inner : Inner;` owns no members | declare the body inline |
| line from nested box stops short | mermaid anchor | render with `dot` |
| edges into tiny port boxes | connections declared port-to-port | connect parts to parts |
| duplicate-member warnings | typed usage given a body | drop the type or drop the body |

## Worked reference (this course)

`models/idea_wall.sysml`, view `IdeaWallViews::embeddedIdeaWallView` — five
packages accepted by `%load`, rendered as one `«part def» IdeaWallSystem`
frame, four part boxes, three thick undirected lines.

Verified nesting, `part inner { ... }` inside `part def OuterA`:

```
subgraph «part def» OuterA
  subgraph «part» inner
    a : Leaf
    b : Leaf
    a ===ab=== b
  side : Leaf
  inner ===hub=== side
```

## Checklist before saying "done"

- [ ] every part answers a distinct job, stated by the student
- [ ] no vendor names, prices, or product specs in the concept model
- [ ] 3–7 top-level parts; nesting only where the student asked for it
- [ ] connection names read as `sourceSink`
- [ ] no ports, flows, or arrows unless separately justified
- [ ] view exposes the owner definition
- [ ] `%load` green for every package
- [ ] counts in the rendering match the declarations
- [ ] the student has explained at least one connection in their own words
