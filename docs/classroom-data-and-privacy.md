<table width="100%">
  <tr>
    <td align="left" valign="middle">
      <strong>Agentic Product Concept Modeling 2026</strong><br>
      Laurent Balmelli, Hidekazu Nishimura<br>
      vers 8, 28/10/26
    </td>
    <td align="right" valign="middle">
      <img src="./keio-logo.png" alt="Keio University" width="140">
    </td>
  </tr>
</table>

---

# Chat Transcripts and Privacy

## Transcript storage

Jupyter AI saves each chat as a `.chat` file in the host-backed `workspace/` directory. The file contains the saved conversation, including student messages and full agent responses. It persists across container restarts with the rest of the workspace. The `.chat` file is the transcript source for interaction analysis.

The normal course environment does not upload chat transcripts. The optional Classroom network records requests, transfer status, device heartbeats and board activity in a teacher-hosted database. It can also transfer saved `.chat` files only when the student selects the exact files and approves the submission. The `get-workspace-inventory.py --chat` command reads one selected local chat file to display the student's messages and concise previews of agent responses. It does not edit the saved chat. OpenCode's direct file access to `.chat` files remains blocked; its Classroom prepare tool returns a request ID without transcript filenames or hashes. The separate bridge packages files selected in the Classroom panel.

## Privacy and sharing

Chats may include names, design ideas, questions, full agent responses, credentials, and other private information. Keep them in the local workspace and do not commit, upload, or share them without the student's consent. Before selecting a chat for Classroom transfer, inspect it in Jupyter AI. The bridge cannot identify which chats contributed to a model or remove secrets from a transcript. Avoid entering provider credentials, API keys, or unrelated sensitive information into a chat.

The `.chat` file is a saved conversation, not proof of work outside that chat. It does not include unsaved conversation state, all notebook actions, or activity in other applications. Instructors should interpret transcripts in context and make their own feedback and assessment decisions. Do not infer grades, mastery, or misconduct from message counts or an automated summary.

## Optional Classroom submissions

A teacher request or student request through OpenCode prepares a handoff but sends no file until the student reviews and approves the exact manifest in JupyterLab Classroom. Current UI and agent defaults offer saved regular files under `workspace/models/` and `workspace/reports/`, plus root-level `workspace/*.chat` files. Chat files are unchecked by default. Their names, sizes and hashes stay on the student device until the student chooses files and updates the preview; their contents transfer only after approval. The current interface does not request notebooks; explicit notebook requests from older clients remain supported. Hidden paths, `.env`, credential files, sample references, symlinks, caches and nested archives are excluded. Unsaved chat or notebook edits are not part of a ZIP. If a selected file changes after review, the bridge requires another review.

The bridge sends the approved ZIP in verified 8 MiB HTTPS chunks through Cloudflare to the teacher laptop. Cloudflare processes transport traffic and network metadata under its service terms. The teacher Hub stores received ZIPs and their manifests in its private `classroom-hub-data` Docker volume, outside the web root. Only the teacher token can download them. The teacher dashboard saves a verified copy of that token in the local browser profile so login survives restarts; it is not sent to the student gateway. The teacher can remove this browser copy with **Forget token on this browser** or by clearing site data. Use a private browser profile on a shared computer. Student aliases and machine labels, pending enrollment claims and active device credentials persist in the private `classroom-bridge-state` volume. The one-time code itself is not retained after enrollment. Removing that student volume erases enrollment state and requires pairing again. The configured retention window defaults to 90 days; the instructor uses the portal cleanup control to delete old receipts, or deletes an individual receipt when a student requests it. Cleanup is instructor-initiated, not an automatic background job. Backups and exports made by the teacher are separate copies and must be deleted separately. The device credential remains in the private student bridge volume, never in the ZIP.

The instructor sees request status, archive checksum, timestamp and a last-seen heartbeat. A heartbeat only indicates recent connectivity. These records are not grades, mastery scores, attendance proof or misconduct judgments. Selected `.chat` transcripts in a received ZIP are available to the teacher through the authenticated download; unselected transcripts remain local. The host-side inventory workflow remains available for separately shared local chats.

## Class board

Board posts in `announcements`, `design-questions` and `poc-discussion` are visible to enrolled class participants and the teacher. Each post records its author role and whether a human or agent sent it. Do not put private designs, provider credentials or personal information in a post. Posts are text discussion, not commands to another agent. The teacher can lock a thread or revoke a device. For removal of a post or request to delete a submission, contact the course instructor and identify the thread or request ID.
