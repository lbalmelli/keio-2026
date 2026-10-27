<table width="100%">
  <tr>
    <td align="left" valign="middle">
      <strong>Agentic Product Concept Modeling 2026</strong><br>
      Laurent Balmelli, Hidekazu Nishimura<br>
      vers 3, 27/10/26
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

The course environment does not create a separate course activity log, collect notebook or model activity, or upload chat transcripts to an instructor service. The `get-workspace-inventory.py --chat` command reads one selected chat file to display the student's messages and concise previews of agent responses. It does not edit the saved chat. OpenCode's direct file access to `.chat` files remains blocked.

## Privacy and sharing

Chats may include names, design ideas, questions, and other private information. Keep them in the local workspace and do not commit, upload, or share them without the student's consent. Avoid entering provider credentials, API keys, or unrelated sensitive information into a chat.

The `.chat` file is a saved conversation, not proof of work outside that chat. It does not include unsaved conversation state, all notebook actions, or activity in other applications. Instructors should interpret transcripts in context and make their own feedback and assessment decisions. Do not infer grades, mastery, or misconduct from message counts or an automated summary.
