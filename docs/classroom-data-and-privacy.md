<table width="100%">
  <tr>
    <td align="left" valign="middle">
      <strong>Agentic Product Concept Modeling 2026</strong><br>
      Laurent Balmelli, Hidekazu Nishimura<br>
      vers 5, 27/10/26
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

The normal course environment does not upload chat transcripts. The optional Classroom network records requests, transfer status, device heartbeats and board activity in a teacher-hosted database; it does not copy `.chat` files. The `get-workspace-inventory.py --chat` command reads one selected chat file to display the student's messages and concise previews of agent responses. It does not edit the saved chat. OpenCode's direct file access to `.chat` files remains blocked.

## Privacy and sharing

Chats may include names, design ideas, questions, and other private information. Keep them in the local workspace and do not commit, upload, or share them without the student's consent. Avoid entering provider credentials, API keys, or unrelated sensitive information into a chat.

The `.chat` file is a saved conversation, not proof of work outside that chat. It does not include unsaved conversation state, all notebook actions, or activity in other applications. Instructors should interpret transcripts in context and make their own feedback and assessment decisions. Do not infer grades, mastery, or misconduct from message counts or an automated summary.

## Optional Classroom submissions

A teacher request or student request through OpenCode prepares a handoff but sends no file until the student reviews and approves the exact manifest in JupyterLab Classroom. The bridge selects saved regular files only under `workspace/models/`, `workspace/notebooks/` and `workspace/reports/`. Hidden paths, `.chat`, `.env`, credentials, sample references, symlinks, caches and nested archives are excluded. Unsaved notebook edits are not part of a ZIP. If a selected file changes after review, the bridge requires another review.

The bridge sends the approved ZIP in verified 8 MiB HTTPS chunks through Cloudflare to the teacher laptop. Cloudflare processes transport traffic and network metadata under its service terms. The teacher Hub stores received ZIPs and their manifests in its private `classroom-hub-data` Docker volume, outside the web root. Only the teacher token can download them. The configured retention window defaults to 90 days; the instructor uses the portal cleanup control to delete old receipts, or deletes an individual receipt when a student requests it. Cleanup is instructor-initiated, not an automatic background job. Backups and exports made by the teacher are separate copies and must be deleted separately. The device credential remains in the private student bridge volume, never in the ZIP.

The instructor sees request status, archive checksum, timestamp and a last-seen heartbeat. A heartbeat only indicates recent connectivity. These records are not grades, mastery scores, attendance proof or misconduct judgments. `.chat` transcripts remain local and can be reviewed only through the separate explicit host-side inventory workflow already described above.

## Class board

Board posts in `announcements`, `design-questions` and `poc-discussion` are visible to enrolled class participants and the teacher. Each post records its author role and whether a human or agent sent it. Do not put private designs, provider credentials or personal information in a post. Posts are text discussion, not commands to another agent. The teacher can lock a thread or revoke a device. For removal of a post or request to delete a submission, contact the course instructor and identify the thread or request ID.
