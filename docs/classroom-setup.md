<table width="100%">
  <tr>
    <td align="left" valign="middle">
      <strong>Agentic Product Concept Modeling 2026</strong><br>
      Laurent Balmelli, Hidekazu Nishimura<br>
      vers 3, 28/10/26
    </td>
    <td align="right" valign="middle">
      <img src="./keio-logo.png" alt="Keio University" width="140">
    </td>
  </tr>
</table>

---

# Classroom setup and operation

The optional Classroom network keeps JupyterLab as the only student browser UI. The student bridge contacts the teacher laptop over ordinary HTTPS; students need no VPN, Tailscale account, Cloudflare software or Cloudflare login. The teacher portal is local at `http://127.0.0.1:8765`. See [privacy and consent](classroom-data-and-privacy.md) before enrollment.

## Teacher: local Hub first

Run these commands in the repository root on the teacher host (Linux shell, macOS Colima terminal, or Ubuntu WSL2 terminal):

```bash
make classroom-teacher-up
```

Without a tunnel token file this starts the Hub and ingress gateway locally. Open `http://127.0.0.1:8765`. Retrieve the generated teacher token into a private host file, then paste its contents into the portal login field:

```bash
mkdir -p .local
chmod 700 .local
docker compose -f compose.teacher.yaml exec -T classroom-hub cat /data/teacher-token > .local/classroom-teacher-token
chmod 600 .local/classroom-teacher-token
```

The portal allows creating a classroom, issuing a 15-minute one-time enrollment code, approving the pending device, requesting selected or all workspaces, viewing verified receipts and downloads, and reading the board and audit trail. Do not give students the teacher token.

## Teacher: authorize the public route

The teacher already owns `sysml.dev` through Cloudflare. Registration alone does not configure DNS, a tunnel or TLS. In the existing Cloudflare account, verify the `sysml.dev` zone is active and that no conflicting `classroom` record exists. In Cloudflare Zero Trust, create a **remotely managed** tunnel named `keio-classroom` and one published application route: `classroom.sysml.dev` to `http://classroom-ingress:8766`. The route must target the gateway in the teacher Compose network. Verify the tunnel-linked DNS record and public TLS certificate. Do not alter root `sysml.dev`, publish JupyterLab, or add an admin hostname. Follow [Cloudflare’s tunnel setup](https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/get-started/) and [token-file documentation](https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/configure-tunnels/run-parameters/).

Save the tunnel token through a private editor in `.local/cloudflare-tunnel-token` and set mode `600`; never paste it into a shell command, notebook, model, chat or Git. Then run `make classroom-teacher-up` again. The Make target detects the file and starts `cloudflared` with `--token-file`, using the host user's UID/GID so the container can read the unchanged file permissions. The connector image is pinned to `2025.7.0`, which supports its `--dns-resolver-addrs 8.8.8.8:53` argument. The service also sets Docker DNS to `8.8.8.8` and `GODEBUG=netedns0=0` for the tested Linux-host workaround. It uses outbound connections; no router port forwarding or inbound student port is required. On restrictive firewalls, permit outbound Cloudflare Tunnel connectivity according to current Cloudflare guidance.

Check from another network:

```bash
curl -i https://classroom.sysml.dev/admin
curl -i https://classroom.sysml.dev/api/v1/classrooms
curl -i https://classroom.sysml.dev/openapi.json
```

Each must return 404 from the deny-by-default gateway. Verify valid HTTPS and the tunnel-linked `classroom` DNS record, and confirm the root `sysml.dev` record/site is unchanged. A live route was not established by this repository change alone.

## Student: enroll and submit

From the student host repository root, run:

```bash
make classroom-student-up
```

The command creates an ignored local bridge secret and starts JupyterLab plus the bridge. Open `http://localhost:8888/lab`, click **Classroom**, and enter an alias, device label and teacher-issued one-time code. The default bridge address is `https://classroom.sysml.dev`; the teacher can override it for a local pilot with `CLASSROOM_HUB_URL` before running the Make target. The teacher approves the pending device in the local portal. The bridge then receives a revocable credential in its own Docker volume. Students require no Cloudflare account or VPN software.

The teacher can select a device and press **Request selected** or **Request all**. The student sees the request in Classroom, clicks **Review files**, inspects paths and sizes, and chooses **Approve and send** or **Decline**. The same path starts from **Prepare submission** or the Design Coach chat instruction “Submit my workspace to the teacher” / `/submit-workspace`. The agent only prepares a request; the student must approve in Classroom. A request ID is pending until both views show a verified receipt with SHA-256 and timestamp.

The teacher can start the local Master Agent terminal with `make classroom-master-agent` after the Hub is running. Example: “Request today's workspaces from everyone in Class A.” Its tools create consent requests, not direct file reads. The teacher agent uses the Hub volume's teacher token and a separate OpenCode state volume.

## Offline, backup and rollback

A sleeping teacher laptop or stopped tunnel prevents live exchange. The student can keep modeling locally; an already approved ZIP remains in the bridge state volume and retries when the Hub returns. A status of `Offline` is not a receipt. The instructor can revoke a device in the portal; students must pair again with a new code. For suspected tunnel-token exposure, stop the connector, revoke/rotate the token in Cloudflare and replace the local file before restarting.

The Hub SQLite database, staging chunks and received ZIPs live in the `classroom-hub-data` Docker volume. Back up that volume while the Hub is stopped for a consistent SQLite copy. The teacher portal can download receipts; deleting a receipt in the teacher portal removes its ZIP and database row. The teacher should schedule the class retention policy (90 days suggested) and delete any separate backup copy when fulfilling a deletion request.

To stop public exposure and the teacher services, run `make classroom-teacher-down`. To stop the student bridge and JupyterLab, run `make classroom-student-down`. Neither target removes Docker volumes. If the route should be retired, remove the `classroom.sysml.dev` published application and DNS record in Cloudflare after checking it is tunnel-owned; leave root `sysml.dev` untouched.

## Verification limits

The repository tests exercise both request directions, local consent, chunk resume, a >100 MiB ZIP, role checks and gateway denial without external credentials. Browser screenshots from a local demo are in [`classroom/test-artifacts/`](../classroom/test-artifacts/). They do not prove a public Cloudflare route, real laptop-to-laptop transfer, provider login, or the JupyterLab browser workflow. Run those checks on two devices after teacher authorization and tunnel provisioning. OpenCode's broad local shell access and the default Jupyter token remain residual local consent-bypass risks; do not describe MCP tool omission as an OS sandbox.
