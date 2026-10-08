# EDA Snake — release notes and operating guide

_As of 2026-10-02_

Snake v1.0.0 is published to `github.com/cdoyle-pdx/eda-catalog` under API group
`eda.cdoyle.dev`. Part one is what belongs in that catalog's README; part two is
what you need to remember.

---

## Part one — for the catalog README

### Installing

Three steps, and the first one is the one nobody expects. Skipping it gives
`signature trust failure: no valid signature found in registry`, which names
neither the cause nor the fix.

**1. Trust the signing key.** EDA refuses app images signed by a key it doesn't
know. Your cluster ships trusting Nokia's key only, so any third-party app needs
its key registered once per cluster.

```yaml
apiVersion: appstore.eda.nokia.com/v1
kind: SigningKey
metadata:
  name: cdoyle-pdx
  namespace: eda-system
spec:
  publicKeys:
    - title: cdoyle-pdx
      key: |
        -----BEGIN PUBLIC KEY-----
        MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEOPyd97Sd7SU9SybQkBfnA7fMc1Ib
        BMrdNVTrLuunRV2tqo/a83Wh1vJ+qkAwRpfUYeZq88EveiOUUmVg0u/6sQ==
        -----END PUBLIC KEY-----
```

Wait for `kubectl get signingkeys -A` to report `LOADED true` before going on.

**2. Add the catalog.**

```yaml
apiVersion: appstore.eda.nokia.com/v1
kind: Catalog
metadata:
  name: cdoyle-pdx
  namespace: eda-system
spec:
  enabled: true
  refreshInterval: 180
  remoteType: git
  remoteURL: https://github.com/cdoyle-pdx/eda-catalog
  skipTLSVerify: false
  title: cdoyle-pdx EDA Apps
```

Check `status.operational: true`, then **3. install Snake from the Store**
(System Administration → App Management).

After install, **Snake** appears in the left nav with **Play Snake**,
**Snake Scores** and **Snake Config** beneath it.

Requires a browser session already signed in to EDA. The game authenticates
itself with silent OIDC against the `eda` realm, so a private window or a
browser not logged in to EDA runs it in standalone mode with a synthetic
arena — by design, not an error.

### Configuring

The app works with no configuration. To change anything, create a
**SnakeConfig** under Snake in the nav — the game finds it wherever it lives,
using a namespace-agnostic query, so it doesn't matter which namespace you put
it in.

| Field | Default | Effect |
| --- | --- | --- |
| `scoreNamespace` | `eda` | Where SnakeScore CRs are written and read |
| `boardSize` | `10` | Leaderboard length, clamped to 3–50 |
| `defaultDifficulty` | `normal` | Which mode the menu opens on — `normal`, `hard` or `hez` |

Out-of-range values fall back to the default rather than being trusted, so a bad
edit degrades instead of breaking the game.

**Scores live in one namespace on purpose.** One leaderboard covers the whole
event however many fabrics the lab has, so a run against one fabric still
competes with a run against another. Two consequences worth knowing:

- The EDA UI's **namespace picker must be set to that namespace** to see scores
  in the Snake Scores browser. This is the most common "my score vanished" — the
  CR is there, the view is scoped elsewhere.
- Changing `scoreNamespace` after scores exist leaves the old ones behind in the
  previous namespace. Pick the home before an event, not during.

Appending `?scorens=<namespace>` to the game's URL overrides the CR for that
session, which is useful for pointing one dashboard tile at a demo namespace
without touching cluster config.

### What's real and what isn't

The arena is drawn from your fabric; the difficulty is not. That separation is
deliberate — if the fabric drove the skill ramp, two players on different labs
couldn't share a leaderboard.

| Element | Source |
| --- | --- |
| Arena size, levels 1–5 | Node count in the chosen namespace |
| Letter labels | Real node names |
| Some walls | Links that are actually down |
| Player name | `preferred_username` from the EDA token |
| Fabric size on each score | Node count at the time of the run |
| Speed, wall count, rival snakes, levels 6–20 | Synthetic and deterministic |

With more than one namespace holding nodes, the game picks the one with the most
and names it on the badge — `Live fabric · eda-telemetry · 6 nodes (of 2
namespaces)`. It never merges two fabrics into one arena.

#### Limitations worth stating

- **Score validation is advisory.** Ranking happens in the browser, so a
  determined player with devtools could post a fabricated score. Acceptable for
  a booth leaderboard; don't treat the data as authoritative.
- **The Snake Scores resource browser shows columns you didn't ask for** —
  annotations and four alarm counts. The `eda:ui:defaultcolumns` marker parses
  but doesn't reach the generated schema; unresolved.
- **`supportedCoreVersions: v6.0.0` is untested** beyond the one 25.8 cluster
  this was built against.

---

## Part two — for you

### Keys and secrets

- [ ] **Revoke the GitHub PAT that was pasted in plaintext.** It had `repo`
      scope, which is enough to push to any of your repositories. Generate a
      replacement and re-run `edabuilder login git`.
- [ ] **Back up `~/.config/edabuilder/keys/default.key`** somewhere that
      survives a laptop rebuild.

The signing key is load-bearing. Every person who installs Snake pins trust to
its public half through a `SigningKey` CR. Lose it and you can't sign a version
that existing users will accept — everyone has to edit their CR with a new key.

It lives outside your repos by default, which is correct. Keep it that way;
don't be tempted to commit it for convenience while files are moving between
directories.

The public half is safe to publish anywhere — it's in the README install block
above, and that's the point of it.

### Release workflow

Cutting a release is one command. `release` is `build-push --sign` and
`publish app` together, which is what we should have used from the start.

```bash
cd ~/eda-snake-scaffold/snake

# 1. bump the version in TWO places
#    manifest.yaml       image: ghcr.io/cdoyle-pdx/snake:v1.0.1
#    k8s/deployment.yaml eda-snake-ui:v1.0.1

# 2. build and push the UI image, verifying content before the push
TAG=v1.0.1
docker build --no-cache -t ghcr.io/cdoyle-pdx/eda-snake-ui:$TAG .
docker run --rm --entrypoint sh ghcr.io/cdoyle-pdx/eda-snake-ui:$TAG \
  -c 'grep -o "<title>[^<]*</title>" /usr/share/nginx/html/index.html'
docker push ghcr.io/cdoyle-pdx/eda-snake-ui:$TAG

# 3. release the app
edabuilder generate
edabuilder release https://github.com/cdoyle-pdx/eda-catalog.git \
  --app manifest=manifest.yaml --git-branch main --sign
```

The app version comes from the **image tag in `manifest.yaml`**, not from
`spec.version` (that's the API version, `v1alpha1`). `edabuilder deploy` appends
a build timestamp; `release` stamps the clean version.

**Bump the version rather than using `--force`.** Republishing the same version
rebuilds the image, which changes its digest — harmless while nobody else has
installed it, but a changed artifact under an unchanged version number is how a
catalog loses credibility.

After a release:

```bash
docker manifest inspect ghcr.io/cdoyle-pdx/snake:$TAG >/dev/null && echo ok
oras discover ghcr.io/cdoyle-pdx/snake:$TAG          # expect a sigstore referrer
gh api repos/cdoyle-pdx/eda-catalog/git/refs/tags --jq '.[].ref'
```

New ghcr packages default to **private** — make each one public or installs fail
with `ImagePullBackOff`. Two packages matter: `cdoyle-pdx/snake` (the app) and
`cdoyle-pdx/eda-snake-ui` (the nginx image the Deployment pulls).

Test a release the way a stranger would: uninstall locally, then install from
the public catalog. It's the only check that catches a private package or a
stale in-cluster registry reference.

### Traps that cost time

Each of these burned at least twenty minutes.

**Docker caches `COPY` past file changes.** A rebuild produced an identical image
digest even though `index.html` on disk had changed. Use `--no-cache`, and
verify the image contents before pushing rather than after deploying:

```bash
docker run --rm --entrypoint sh <image>:<tag> \
  -c 'grep -o "<title>[^<]*</title>" /usr/share/nginx/html/index.html'
```

**Kubernetes caches by tag.** Pushing a new image under an existing tag may not
roll the pod. Always bump the tag, and confirm what's actually running:

```bash
kubectl get pods -n eda-system -l app=snake-ui \
  -o jsonpath='{range .items[*]}{.metadata.name}{"  "}{.spec.containers[*].image}{"\n"}{end}'
```

**Zscaler breaks pushes to ghcr.** Intermittently on, silently. If a push hangs
or half-finishes, check it before debugging anything else.

**The registry path is easy to get wrong.** The Deployment wants
`eda-snake-ui`; a build tagged `snake-ui` pushes successfully, passes a registry
check, and leaves the pod in `ImagePullBackOff` asking for a tag that was never
published under that name.

**`edabuilder` owns some files — never restore your backups of them.**
`*_base_types.go`, `zz_generated.deepcopy.go` and the generated `pysrc/` are
regenerated; putting an older copy back causes `undefined: <Type>` errors that
look like your code is broken. Only `*_api_types.go` is yours.

**Deleting a kind?** Delete its `*_base_types.go` and `zz_generated.deepcopy.go`
too, or `generate` can't compile in order to regenerate them.

**Two apps can't own the same CRs.** Renaming the API group makes it a different
app to the Store, so the old one must be uninstalled first or you get
`conflicting updates` on the Deployment, Service, HttpProxy and ClusterRoles.

**`edabuilder` runs from the app directory** (where `manifest.yaml` is), not the
project root.

**`edabuilder` doesn't generate CRDs from Go types.** Use `create resource` to
scaffold a kind, then replace the generated `*_api_types.go` with yours. It
refuses to run if any target file already exists, so move yours aside first.

### EDA API facts worth keeping

All verified against the 25.8 lab. The error codes are the useful part — several
of them point away from the real cause.

| | |
| --- | --- |
| EQL endpoint | `GET /core/query/v1?query=<eql>` |
| Parameter | `query` — **not** `eql`, `filter`, `q` or `nql` |
| Response | `{"data": [ ... ]}` |
| No token | **400** `InvalidAuthHeader` — reads like a bad request, means unauthenticated |
| Wrong parameter | **404** `QueryNotSpecified` — reads like a bad path, means a missing query string |
| Wrong path | **404** `ApiNotImplemented` |
| Expired token | **401** `TokenExpired` |
| CR REST path | `/apps/<group>/<version>/namespaces/<ns>/<plural>` |
| CRD table in EQL | `.namespace.resources.cr.<group with dots as underscores>.<version>.<kind>` |

**Authentication.** There is no whoami endpoint in the core spec, and no session
cookie. The UI holds its token in memory. The game gets its own by authorization
code + PKCE with `prompt=none` in a hidden iframe, against realm `eda`, client
`auth` ("EDA UI Authentication") — a public client whose redirect URIs are `/*`,
so no Keycloak change was needed. Keycloak is reverse-proxied onto EDA's own
origin, which makes the token POST same-origin and avoids CORS entirely. Tokens
are short-lived; renewal has to update every copy of the token, not just the one
in the auth module.

**Serving a web UI at EDA's origin** is what `HttpProxy` is for:

```yaml
apiVersion: core.eda.nokia.com/v1
kind: HttpProxy
spec:
  authType: atDestination
  rootUrl: http://snake-ui.{EDA_CORE_NAMESPACE}.svc/
```

It serves under `/core/httpproxy/v1/<name>/` with CSP `default-src 'self'` — no
inline `<style>`, `<script>` or `style=""` attributes, which is why the UI ships
as separate files.

**Dashboards** are `view:` components in the manifest pointing at a JSON file.
`ui.category` becomes the left-nav header and `ui.name` the item. A
`dashletDataView` with `navigationTarget.edaRoute: external` is how you launch an
external URL from the nav.

### Open items

- [ ] Write the catalog README from part one — the `SigningKey` step above all,
      since without it installs fail opaquely.
- [ ] Decide the Store `categories` value. It still reads `uncategorised`; the
      community catalog uses `integrations`, and there's no obvious games
      category.
- [ ] Confirm what core version 25.8 maps to before leaving
      `supportedCoreVersions: v6.0.0` as a public compatibility claim.
- [ ] Ask whoever owns `edabuilder` how `eda:ui:defaultcolumns` is meant to be
      attached. The marker parses on `SnakeConfigSpec` but never reaches
      `x-eda-nokia-com` in the generated schema; it probably belongs on the root
      type in `*_base_types.go`, which `edabuilder` owns. That answer is
      reusable for every app you build after this.
- [ ] Check whether `Catalog.spec` or the `Registry` CRD offers a
      signature-verification toggle, so users could opt out per-catalog instead
      of registering a key.

#### Left alone deliberately

- **`go.mod` still says `module snake.eda.local/snake`.** It's the Go module
  path, internal to the build, and never surfaces in the API group or anything a
  user sees. Renaming it means touching every import across `go.work` for no
  outward effect.
- **`SnakeScoreStatus` is vestigial.** Its fields were written by the
  leaderboard state intent, which is gone. Kept so existing CRs stay valid;
  nothing reads them.
- **`regroup.sh`** is still in the app directory. It's a record of the group
  rename — delete it whenever.

#### If you pick this up cold

Authoring source is the single `nokia-snake-eda.html`; `build_split.py` generates
the deployable `index.html` + `snake.css` + `snake.js` + `callback.html` +
`callback.js` (split because of the CSP), and `extract.py` produces the test
harness globals. Seven test suites, ~200 checks, plus a browser run under EDA's
exact CSP against a mock Keycloak.
