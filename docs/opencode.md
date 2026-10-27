<table width="100%">
  <tr>
    <td align="left" valign="middle">
      <strong>Agentic Product Concept Modeling 2026</strong><br>
      Laurent Balmelli, Hidekazu Nishimura<br>
      vers 18, 27/10/26
    </td>
    <td align="right" valign="middle">
      <img src="./keio-logo.png" alt="Keio University" width="140">
    </td>
  </tr>
</table>

---

# Using OpenCode in JupyterLab

OpenCode appears in JupyterLab's native Jupyter AI chat panel. It runs as an ACP process inside the same container as Jupyter and uses Jupyter's notebook MCP tools. The default course agent is **SysML Design Coach**. There is one browser URL: `http://localhost:8888/lab`.

## 1. Start Jupyter and sign in to a provider

From the repository root, prepare the existing samples and start the course environment:

```bash
make samples
make build
make up
```

Open JupyterLab at `http://localhost:8888/lab` and sign in with the Jupyter token (`opensysml` by default). The notebooks work without OpenCode or provider credentials.

Open a second terminal in the repository and run:

```bash
make opencode-auth
```

Connect **OpenCode Zen** in the interactive login and enter its API key at the CLI prompt. Do not paste a key into a notebook, model, chat, or source file. Authentication state is kept in the `opencode-state` Docker volume. Select an available OpenCode Zen model in Jupyter AI's chat controls. Provider names and free-tier availability depend on the pinned OpenCode version and provider.

## 2. Open and place Chat

1. Open or create a notebook in JupyterLab.
2. Click the **Chat** icon in JupyterLab's left sidebar and choose **New Chat**.
3. Right-click the Chat icon and choose **Switch Sidebar Side** to move it right. Drag the panel divider to resize it; JupyterLab saves its workspace layout.
4. In the chat toolbar, select **OpenCode** as the persona and choose an available OpenCode Zen model.

The default Jupyter MCP tools are included by Jupyter AI. The course does not configure a second MCP server. The agent can inspect the active notebook and selected cell, read current live cell contents, add or edit cells, run cells, and inspect results through the notebook's attached kernel. Live unsaved changes are available only while that notebook is open in the browser.

## 3. Start a Day 3 or Day 4 tutoring workflow

Select **SysML Design Coach** and start one of the visible workflow commands in chat:

- `/start-concept-design` loads the Day 3 `concept-design` skill.
- `/explore-poc` loads the Day 4 `poc-realization` skill.
- `/component-to-sysml-v2` loads the Day 4 `component-to-sysml-v2` skill to model a selected online component specification as a sourced `part def`. It reviews interface-relevant characteristics such as ports, connections, dimensions, and mass, then asks which properties matter for the PoC.
- `/assess-feasibility` loads the Day 4 `feasibility-assessment` skill.
- `/generate-model-report` loads the `model-report` skill to create a model-grounded Markdown report from confirmed saved Concept and PoC `.sysml` sources.

The coach provides SysML expertise and tutoring behavior; the loaded skill provides the methodology. The coach asks occasional open questions about modeling choices, offers hints or direct explanations on request, and leaves design decisions with the student. The Idea Wall comparison starts with the same question in the general assistant and after `concept-design` is loaded: [Idea Wall tutoring demonstration](../opencode/examples/idea-wall-comparison.md). More details are in [Visual Concept Making workflows](visual-concept-making-workflows.md).

### Generate a model report

Save the concept and any distinct PoC realization candidates under `models/` in JupyterLab (the host-backed `/home/keio/work/models` directory). Declare any views you want included in those model files and load the confirmed sources in the active OpenSysML notebook before requesting diagrams. Then enter `/generate-model-report` in the SysML Design Coach chat.

The coach proposes likely concept and realization files, including dependencies only when imports/relationships establish their scope. Confirm the project and complete file set, then confirm your full name, report title, subtitle, and language. Review the final summary and output path before approving generation. Ambiguous files and mixed-purpose views prompt you to choose. An unsaved notebook-only model must first be saved or given a supported source path; the workflow does not create or modify a canonical model.

The generated Markdown is saved to `/home/keio/work/reports/<project-slug>.md`, visible as `reports/<project-slug>.md` in JupyterLab. Its official Keio logo and any actual rendered image outputs are stored under `reports/assets/<project-slug>/`. Existing reports require an overwrite choice or a timestamped/versioned destination. A concept-only report is partial when no PoC file is confirmed. If the kernel is unavailable, documented model text is still reported and discovered views are listed as not rendered. Missing `doc` text is identified as undocumented; no explanation is inferred from an element name. Report facts come from the confirmed `.sysml` sources and their `doc` declarations only: `.chat` files, transcripts, and classroom interaction records are not read as evidence.

For example, a confirmed concept source with no confirmed realization produces a partial report with Concept requirements/structure/behavior coverage explicitly stated and Part II marked not yet modeled. If two realization files are confirmed, the report gives each a separate PoC section and traces only relationships declared in the model. A rendered view appears only after its real qualified view name has been loaded and `%render` returned output in the attached kernel.

## 4. Review saved chat transcripts

Jupyter AI stores the full student and agent conversation in `.chat` files at the workspace root. These files are the transcript source for interaction analysis. The course does not create a second JSONL transcript, record notebook/model activity, or upload chat data to an instructor collector. Run `./scripts/get-workspace-inventory.py --chat <chat-name>` from the repository root to display student messages in full and one-line previews of agent messages. The preview does not alter the `.chat` file, which retains the full conversation. Treat chat files as private student work and do not share them without consent.

## 5. Try the Keio course workflow

Open a student-owned notebook with **SysML v2 (OpenSysML)** selected. Run the first-model lesson's actual setup cells, including:

```text
%load /home/keio/work/samples/OpenSysML/examples/views-demo.sysml
```

The sample declares `LanderViews::interfaces`, `LanderViews::descentStates`, `LanderViews::descentFlow`, and `LanderViews::partsTable`. The Keio first-model lesson also defines `KeioVehicle` and `KeioViews::completeVehicleModel`.

Try these prompts one at a time:

> Identify my active notebook and selected cell using the notebook tools. Read what is currently in the notebook, including any unsaved edits. Explain the model and views that are actually present. Do not edit or execute anything.

> Add a Markdown cell just below the selected cell summarizing the model's defined parts. Do not change the SysML source file.

> If `KeioViews::completeVehicleModel` is available in this notebook's OpenSysML session, add a code cell below the selected cell containing `%render KeioViews::completeVehicleModel mermaid` and run it in this notebook's existing kernel. Report the actual output; if the view is not available, stop and explain.

Review any cell change and output in the notebook. The course OpenCode config automatically allows the Jupyter MCP `execute_command` tool so kernel commands do not ask for approval on every call. A specific student request still defines what the coach should run; this permission is not a guarantee that every execution is appropriate. Ask for suggestions without edits when you want a read-only answer.

## 6. Model files, notebook history, and permissions

Create new `.sysml` files in `workspace/models/` with distinct names. The folder appears as `models/` in Jupyter's file browser and is available at `/home/keio/work/models` for model loading. Copy reference models from `samples/` into `models/` before editing. The course OpenCode config allows `pwd` and `ls` without approval, and allows reading reference samples, saved model files, and `/opt/course/docs/`. Direct reads of `.ipynb`, `.chat`, and private course data remain blocked so the coach uses live notebook MCP context. Generic file edits and shell commands other than `pwd`/`ls` still ask; direct `.ipynb` file edits are denied. The **Always allow** choice in a prompt lasts only for the current OpenCode session; these config rules persist across container restarts. OpenCode merges config sources, so project or inline config can override these defaults. They are not an enforced security boundary.

Reference samples at `/home/keio/work/samples` are read-only. Jupyter notebooks, models, and chats are inside the host-backed `workspace/` directory mounted at `/home/keio/work`. Do not edit reference examples in place. JupyterLab uses its normal notebook autosave interval, so a live MCP edit can be saved through the existing autosave behavior. After editing a `.sysml` file, load it again in a SysML notebook when needed:

```text
%load /home/keio/work/models/my_model.sysml
```

Jupyter AI's native chat panel creates and discovers `.chat` files at the workspace root. They are stored in the persistent `workspace/` mount beside the `notebooks/` and `models/` folders. OpenCode login/configuration data lives in the separate `opencode-state` Docker volume. Chat files may contain private prompts; do not include credentials or sensitive information.

## 7. Diagnostics and troubleshooting

Run the nonsecret runtime check from another terminal:

```bash
make doctor
```

It reports Jupyter AI, OpenCode CLI, Jupyter extensions, the OpenSysML kernelspec, the live notebook MCP tool registry, storage permissions, and a reminder that provider authentication cannot be verified without exposing credentials. To inspect Jupyter logs, use:

```bash
make logs
```

| Symptom | Check |
| --- | --- |
| OpenCode is absent from the persona picker | Run `make doctor`, then rebuild with `make build` and restart with `make down` followed by `make up`. |
| OpenCode responds that no provider/model is configured | Run `make opencode-auth`, connect OpenCode Zen, then choose an available Zen model in Chat. |
| Notebook tools cannot identify a notebook | Keep the target notebook open in JupyterLab and select its tab and a cell. The agent reads browser-live state rather than stale `.ipynb` disk contents. |
| `%render` reports a missing view | Use the SysML v2 (OpenSysML) kernel and execute the model, view declaration, and `%load` prerequisite cells first. `%render` targets a declared view, not a package. |
| Credentials disappear after restart | Keep the named `opencode-state` volume; do not run `docker compose down --volumes`. |
| Jupyter MCP tool still asks for approval | The course config auto-allows only `Jupyter_MCP_Server_execute_command`. Rebuild and restart after updating the image; other tools may still prompt. |
| A clean start repeatedly logs `GET /mcpapi` with `404 Not Found` | The bundled Jupyter MCP server exposes `/mcp`; `/mcpapi` is an endpoint mismatch in the client/runtime path. | Run `make doctor` to check the bundled MCP tool registry. If it succeeds but `/mcpapi` polling continues when OpenCode starts, share the logs with the instructor; do not add another Jupyter MCP server. |
| Logs show `404` and `Kernel does not exist` after restarting Jupyter | The browser is trying to reconnect to a kernel ID from the previous container. | Save notebook edits, reload JupyterLab, select **SysML v2 (OpenSysML)** from the notebook's **Kernel** menu if needed, then rerun the required cells to restore the in-memory model. |
| SysML Design Coach or workflow command is absent | Image or OpenCode config is stale. | Run `make build`, then `make down` and `make up`. Run `make doctor` to inspect the installed runtime. |

Stop the environment with `make down`. Restart it with `make up`. Do not use `docker compose down --volumes` if you want to retain OpenCode authentication state.
