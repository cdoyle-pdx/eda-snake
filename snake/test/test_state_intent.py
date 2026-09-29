"""Unit tests for the leaderboard ranking logic.

The EDA State Engine injects `eda_state` at runtime; here we exercise the pure
functions directly so validation and ranking can be tested without a cluster.
"""
import importlib.util, pathlib, sys

spec = importlib.util.spec_from_file_location(
    "state_intent",
    pathlib.Path(__file__).parent.parent / "intents" / "snakeleaderboard" / "state_intent.py",
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

def row(initials="ABC", score=100, level=3, diff="normal", player="colin", at="2026-01-01T00:00:00Z"):
    return {"spec": {"initials": initials, "score": score, "level": level,
                     "difficulty": diff, "player": player, "recordedAt": at}}

fails = []
def ok(cond, msg):
    if cond: print("ok:", msg)
    else: fails.append(msg); print("FAIL:", msg)

# --- validation ---
ok(mod._valid(row()["spec"]), "well-formed entry accepted")
ok(not mod._valid(row(initials="ab")["spec"]), "2-letter initials rejected")
ok(not mod._valid(row(initials="abc")["spec"]), "lowercase initials rejected")
ok(not mod._valid(row(initials="A1C")["spec"]), "non-alpha initials rejected")
ok(not mod._valid(row(diff="impossible")["spec"]), "unknown difficulty rejected")
ok(not mod._valid(row(level=0)["spec"]), "level 0 rejected")
ok(not mod._valid(row(level=21)["spec"]), "level 21 rejected")
ok(not mod._valid(row(score=-5)["spec"]), "negative score rejected")
ok(not mod._valid(row(score=999999, level=2)["spec"]), "impossible score rejected (anti-tamper)")
ok(mod._valid(row(score=3800, level=2)["spec"]), "high-but-plausible score accepted")
ok(not mod._valid({"initials":"ABC"}), "missing fields rejected")
ok(not mod._valid(row(score="NaN")["spec"]), "non-numeric score rejected")

# --- ranking ---
rows = [row("AAA", 500), row("BBB", 900), row("CCC", 700), row("BAD", -1)]
ranked, total = mod._rank(rows, 10, "")
ok(total == 3, "invalid entries excluded from the count")
ok([e["initials"] for e in ranked] == ["BBB","CCC","AAA"], "sorted by score descending")
ok(ranked[0]["rank"] == 1 and ranked[2]["rank"] == 3, "ranks assigned 1..n")
ok(all("_at" not in e for e in ranked), "internal tie-break field stripped from output")

# board size
AZ = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
def initials(i):
    return AZ[i // 26 % 26] + AZ[i % 26] + "Z"
ranked, _ = mod._rank([row(initials(i), i*10) for i in range(30)], 10, "")
ok(len(ranked) == 10, "board truncated to configured size")
ok(ranked[0]["score"] == 290, "top entry is the highest score")
ok(mod._valid(row(initials(5))["spec"]), "generated test initials are themselves valid")

# difficulty filter
mixed = [row("NOR", 100, diff="normal"), row("HRD", 200, diff="hard"), row("HEZ", 300, diff="hez")]
ranked, total = mod._rank(mixed, 10, "hard")
ok(len(ranked) == 1 and ranked[0]["initials"] == "HRD", "difficulty filter scopes the board")
ranked, total = mod._rank(mixed, 10, "")
ok(total == 3, "empty filter ranks all difficulties together")

# tie-break: earlier run wins
tie = [row("LAT", 500, at="2026-02-02T00:00:00Z"), row("ERL", 500, at="2026-01-01T00:00:00Z")]
ranked, _ = mod._rank(tie, 10, "")
ok(ranked[0]["initials"] == "ERL", "ties broken in favour of the earlier run")

# empty
ranked, total = mod._rank([], 10, "")
ok(ranked == [] and total == 0, "empty EDB yields an empty board")

print("ISSUES: "+"; ".join(fails) if fails else "ALL INTENT TESTS PASSED")
sys.exit(1 if fails else 0)
