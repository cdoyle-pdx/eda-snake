# Snake UI — authoring source

`nokia-snake-eda.html` is the single source of truth. Never edit the files in
`../ui/` directly; they are generated from it.

## Build

```bash
cd snake/ui-src
python3 build_split.py          # -> split/index.html snake.css snake.js callback.html callback.js
cp split/* ../ui/
```

The split exists because EDA's HttpProxy serves with `default-src 'self'`,
which blocks inline `<style>`, `<script>` and `style=""`.

## Test

```bash
python3 extract.py              # -> eda_globals.js, the harness the node suites load
for t in *test.js; do node "$t" || break; done
python3 csp_auth_test.py        # browser run under EDA's exact CSP, mock Keycloak (needs playwright)
python3 serve_test.py           # browser run with no Keycloak: must degrade to standalone
```

Every suite exits non-zero on any failure.
