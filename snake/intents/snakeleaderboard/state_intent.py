"""Leaderboard state intent.

Triggered whenever a SnakeLeaderboard resource is created or updated. Reads the
SnakeScore resources out of the EDB, ranks them, republishes the top N into the
leaderboard's status, and raises an alarm when the high score changes.

Entrypoint and eda_state helpers per the EDA 25.8 state script contract:
  https://docs.eda.dev/25.8/development/apps/scripts/state/
"""

VALID_DIFFICULTIES = ("normal", "hard", "hez")
MAX_LEVEL = 20


def _score_rows(namespace):
    """Fetch every SnakeScore in the namespace from the EDB."""
    try:
        rows = eda_state.list_db(  # noqa: F821  (injected by the State Engine)
            table="snakescores",
            namespace=namespace,
        )
    except Exception as exc:  # EDB not ready, empty table, etc.
        eda_state.log("snake: could not list snakescores: %s" % exc)  # noqa: F821
        return []
    return rows or []


def _valid(spec):
    """Reject malformed or impossible entries rather than ranking them.

    The browser is not a trusted client: it can be driven by hand against the
    REST API. Validation lives here, on the server side of the boundary.
    """
    initials = str(spec.get("initials", ""))
    if len(initials) != 3 or not initials.isalpha() or not initials.isupper():
        return False

    difficulty = spec.get("difficulty")
    if difficulty not in VALID_DIFFICULTIES:
        return False

    try:
        score = int(spec.get("score", -1))
        level = int(spec.get("level", 0))
    except (TypeError, ValueError):
        return False

    if score < 0 or not (1 <= level <= MAX_LEVEL):
        return False

    # Sanity ceiling: the theoretical maximum is bounded by the scoring rules.
    # Letters cap at (10 + level) each, 5 per level, plus maneuver bonuses.
    # 2000 per level is far above any real run but still catches fabricated
    # values posted straight at the API.
    if score > level * 2000:
        return False

    return True


def _rank(rows, size, difficulty_filter):
    """Sort accepted entries and cut to the board size."""
    entries = []
    for row in rows:
        spec = row.get("spec", {}) or {}
        if not _valid(spec):
            continue
        if difficulty_filter and spec.get("difficulty") != difficulty_filter:
            continue
        entries.append(
            {
                "initials": spec.get("initials"),
                "score": int(spec.get("score", 0)),
                "level": int(spec.get("level", 1)),
                "difficulty": spec.get("difficulty", ""),
                "player": spec.get("player", ""),
                # tie-break on the earlier run so the board is stable
                "_at": spec.get("recordedAt", ""),
            }
        )

    entries.sort(key=lambda e: (-e["score"], e["_at"]))

    ranked = []
    for index, entry in enumerate(entries[:size]):
        entry.pop("_at", None)
        entry["rank"] = index + 1
        ranked.append(entry)
    return ranked, len(entries)


def process_state_cr(cr):
    """Process a SnakeLeaderboard state CR."""
    metadata = cr.get("metadata", {}) or {}
    spec = cr.get("spec", {}) or {}
    name = metadata.get("name", "leaderboard")
    namespace = metadata.get("namespace", "eda")

    size = int(spec.get("size", 10) or 10)
    difficulty_filter = spec.get("difficulty") or ""
    alarm_enabled = spec.get("highScoreAlarm", True)

    previous_top = ((cr.get("status", {}) or {}).get("topScore")) or 0

    rows = _score_rows(namespace)
    ranked, total = _rank(rows, size, difficulty_filter)
    top_score = ranked[0]["score"] if ranked else 0

    eda_state.update_db(  # noqa: F821
        table="snakeleaderboards",
        namespace=namespace,
        name=name,
        data={
            "status": {
                "entries": ranked,
                "totalRuns": total,
                "topScore": top_score,
                "lastUpdated": eda_state.now_rfc3339()  # noqa: F821
                if hasattr(eda_state, "now_rfc3339")  # noqa: F821
                else "",
            }
        },
    )

    # A new high score is a legitimate operational event: it is how the app
    # demonstrates alarm generation without inventing a fault condition.
    if alarm_enabled and ranked and top_score > previous_top:
        leader = ranked[0]
        eda_state.update_alarm(  # noqa: F821
            name="snake-high-score-%s" % name,
            namespace=namespace,
            severity="info",
            kind="SnakeLeaderboard",
            resource=name,
            description=(
                "New Snake high score: %s scored %d on level %d (%s) as %s"
                % (
                    leader["initials"],
                    leader["score"],
                    leader["level"],
                    leader["difficulty"],
                    leader["player"] or "unknown",
                )
            ),
        )
