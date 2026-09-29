# eda-snake

Nokia Snake as an installable Nokia EDA application, built with `edabuilder`
against the EDA **25.8** app development workflow.

Admins play it in the same browser they already use for EDA, from the app's
entry in the UI menu tree. The leaderboard is shared across everyone on the
cluster because it lives in the EDB as custom resources.

---

## What kind of app this is

EDA has two classes of app: intent apps written in MicroPython, and
**controller-based apps** which can be written in any language. Snake is both:

| Part | Class | Why |
|---|---|---|
| `SnakeScore`, `SnakeLeaderboard` CRDs | API resources | Leaderboard state lives in the EDB, so it is transactional, git-backed and revertible |
| `intents/snakeleaderboard/state_intent.py` | State intent | Ranks scores server-side and raises the new-high-score alarm |
| `k8s/deployment.yaml` + `service.yaml` | Controller-based | The game is a browser UI, so it needs something serving it |

No **config** intent exists, deliberately: Snake does not generate device
configuration, so there is nothing for a config script to push.

## Build and install

`build.sh` runs the real `edabuilder` sequence end to end:

```bash
./build.sh
```

It performs:

```bash
edabuilder init --vendor nokia-gtm eda-snake     # project scaffold
edabuilder create app snake                       # app scaffold + manifest
edabuilder create resource SnakeScore             # CRD only
edabuilder create resource SnakeLeaderboard --scaffold-state
edabuilder generate                               # CRDs, OpenAPI, python SDK, manifest
edabuilder generate appsettings                   # collects '# app-set:' annotations
edabuilder generate appsettings-openapi
docker build -t ghcr.io/nokia-gtm/eda-snake-ui:v0.1.0 .
edabuilder deploy                                 # build, publish, install (in-cluster target)
```

`edabuilder deploy` uses the `in-cluster` deploy target by default — the dev
registry and catalog that edabuilder itself deploys into the EDA cluster. To
publish to your own registry + git catalog instead, add a deploy target to
`~/.config/edabuilder/config.yaml` and `edabuilder deploy use-target <name>`.

### Installing from a catalog (the three-step user flow)

Once published to a git catalog:

1. **Add the catalog** — point EDA at the catalog repo.
2. **Install from the EDA Store**, or apply an `AppInstaller` workflow:

```yaml
apiVersion: appstore.eda.nokia.com/v1
kind: AppInstaller
metadata:
  name: snake-install
  namespace: eda-system
spec:
  operation: install
  apps:
    - appId: snake
      catalog: <your-catalog>
      version:
        value: v0.1.0
      appSettings:
        uiCpuLimit: "1"
```

3. **Open it** — installing registers the CRDs, so a **Snake** group appears in
   the EDA UI menu tree. Selecting it lands on the leaderboard with
   Play / How it's built / Reset.

## App settings

Annotated in `k8s/deployment.yaml` with `# app-set: ${...}` and collected into
`settings/appsettings_types.go` by `edabuilder generate appsettings`:

| Setting | Default | Purpose |
|---|---|---|
| `uiCpuLimit` | `500m` | CPU ceiling for the UI pod |
| `uiMemoryLimit` | `128Mi` | Memory ceiling for the UI pod |

## RBAC

Two ClusterRoles in `rbac/roles.yaml`:

- `eda-snake-player` — read the board, create scores. Enough to play.
- `eda-snake-admin` — adds update/delete, which is what resetting the board needs.

The UI hides the reset control for users without the admin role, but that is
convenience, not security. Enforcement is EDA's access control on the CR; the
browser is never the boundary. The state intent independently re-validates every
score, since the REST API can be driven by hand.

## The same-origin proxy

`nginx.conf` proxies `/core/` and `/apps/` to the EDA API from the same origin
that serves the game. That means no CORS exception, and the admin's existing EDA
session is reused as-is.

## Design rule

**Fabric state seeds the game. It never drives difficulty.**

Levels 1–5 size to the real topology, letters spawn on named nodes, and
down links become walls. Levels 6–20 scale out synthetically. But `levelConfig()`
is always synthetic and deterministic — otherwise a run played while someone was
load-testing the lab would not be comparable to any other run, and the
leaderboard would be meaningless.

If EDA is unreachable the UI degrades to localStorage and synthetic generation,
and the game still plays.

## Tests

```bash
python3 snake/test/test_state_intent.py   # ranking, validation, anti-tamper
```

The browser-side logic has its own suites (fabric seeding, RBAC gating, prefill,
offline parity) — see the development notes.

## EQL queries (verified)

`EDA.readFabric()` in `snake/ui/index.html` runs exactly two queries. The field
names below were checked against a live 25.8 lab.

```
.namespace.node fields [name, operating-system, status]
.namespace.node.<srl|sros>.interface fields [.namespace.node.name, name, admin-state, oper-state, oper-down-reason]
```

**Response envelope.** The EDA API follows the Kubernetes Resource Model, so
list responses are normally enveloped. The EQL endpoint's exact envelope is not
pinned down in the docs, so `EDA.rows()` accepts any of: a bare array,
`{items:[]}`, `{rows:[]}`, `{results:[]}`, `{data:[]}`, `{entries:[]}`, or a
single KRM object — and `EDA.field()` reads each field from the row itself or
from `.spec` / `.status` / `.metadata.name`. Whichever shape arrives, parsing
works.

The shape that actually arrived is recorded in `EDA.lastShape`, logged once to
the browser console on the first query, and shown as the last row of the
in-game "How this game was built" panel. Read it there to confirm.

Notes:

- `.namespace.node` has **no `type` field**, so leaf/spine role is inferred from
  the node name only. It is cosmetic — no game mechanic depends on it.
- Interfaces live under a per-OS table. The OS reported by the node query
  decides which of `srl` / `sros` to read; a missing table is skipped, so a
  mixed-vendor lab still works.
- Only `ethernet-*`, `lag*` and `irb*` ports count as fabric links. mgmt,
  loopback and system interfaces are excluded, otherwise they would show up as
  permanently-healthy "links" and skew the wall count.

## Still to verify on your cluster

**`eda_state` helper signatures** (`list_db`, `update_db`, `update_alarm`) are
used as documented, but the exact keyword arguments should be confirmed against
an `edabuilder deploy` run and the State Engine logs.
