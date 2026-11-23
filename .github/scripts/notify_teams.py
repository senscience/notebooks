"""Post the published notebooks' test results to a Teams chat, through a Workflows webhook.

    python notify_teams.py <reports folder>

The folder holds one artifact per system, `published-notebooks-<system>/`, each with the
notebooks it was to run (`notebooks.txt`) and notebook-runner's reports (`report.json`). The
message says whether every notebook ran without errors on every system; if not, which ones failed,
where, and their first error. A system without reports (its job failed early, or was cancelled) is
said too. Then how long it took: the run, from its start, and each system's notebooks, from the
first one's start to the last one's end.

Environment: TEAMS_WEBHOOK, the Workflows URL ("Send webhook alerts to a chat"; without it, the
card is printed instead of posted), RUN_URL, the run's page, RUN_STARTED, when it started (ISO
8601), and SYSTEMS, the systems the run tested ("ubuntu-latest macos-latest windows-latest").
Standard library only.
"""

from __future__ import annotations

import json
import os
import sys
import urllib.request
from datetime import UTC, datetime
from pathlib import Path

ARTIFACT = "published-notebooks-"
NAMES = {"ubuntu-latest": "Linux", "macos-latest": "macOS", "windows-latest": "Windows"}
# A line per failed notebook: its first error's message, cut to this length
MESSAGE_LENGTH = 200
# The failed notebooks listed in full up to this many; the rest counted
LISTED = 15


def main(folder: Path) -> int:
    systems = os.environ.get("SYSTEMS", " ".join(NAMES)).split()
    started = os.environ.get("RUN_STARTED")
    run_seconds = (
        (datetime.now(UTC) - datetime.fromisoformat(started)).total_seconds() if started else None
    )
    card = message(folder, systems, os.environ.get("RUN_URL", ""), run_seconds)
    webhook = os.environ.get("TEAMS_WEBHOOK", "")
    if not webhook:
        print(json.dumps(card, indent=1))
        return 0
    request = urllib.request.Request(
        webhook,
        data=json.dumps(card).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        print(f"Posted: {response.status}")
    return 0


def message(
    folder: Path, systems: list[str], run_url: str, run_seconds: float | None = None
) -> dict:
    """The Adaptive Card, as a Workflows webhook takes it."""
    # Notebook → system → its report, or None when it was to run but has no report
    results: dict[str, dict[str, dict | None]] = {}
    missing: list[str] = []
    # System → its notebooks' time, from the first one's start to the last one's end
    durations: dict[str, float] = {}
    for system in systems:
        artifact = folder / f"{ARTIFACT}{system}"
        if not (artifact / "report.json").exists():
            missing.append(system)
            continue
        expected = (artifact / "notebooks.txt").read_text().split() if (
            artifact / "notebooks.txt"
        ).exists() else []
        for notebook in expected:
            results.setdefault(_key(notebook), {})[system] = None
        reports = json.loads((artifact / "report.json").read_text())
        for report in reports:
            results.setdefault(_key(report["notebook"]), {})[system] = report
        if reports:
            start = min(datetime.fromisoformat(r["started_at"]) for r in reports)
            end = max(datetime.fromisoformat(r["finished_at"]) for r in reports)
            durations[system] = (end - start).total_seconds()

    failed = {
        n: {s: r for s, r in by_system.items() if r is None or not r.get("ok")}
        for n, by_system in sorted(results.items())
    }
    failed = {n: f for n, f in failed.items() if f}
    tested = _list([NAMES.get(s, s) for s in systems if s not in missing])

    if not failed and not missing:
        title = f"✅ The {len(results)} published notebooks ran without errors on {tested}"
        lines = []
    else:
        parts = []
        if failed:
            parts.append(f"{len(failed)} of {len(results)} published notebooks failed")
        if missing:
            parts.append(f"no results from {_list([NAMES.get(s, s) for s in missing])}")
        title = "❌ " + "; ".join(parts)
        lines = [_line(n, f) for n, f in list(failed.items())[:LISTED]]
        if len(failed) > LISTED:
            lines.append(f"- and {len(failed) - LISTED} more: see the run")
        if missing:
            lines.append(
                f"- {_list([NAMES.get(s, s) for s in missing])}: no reports, the job failed "
                "or was cancelled before the notebooks ran"
            )

    body = [{"type": "TextBlock", "text": title, "weight": "Bolder", "wrap": True}]
    if lines:
        body.append({"type": "TextBlock", "text": "\n".join(lines), "wrap": True})
    took = _took(run_seconds, durations)
    if took:
        body.append({"type": "TextBlock", "text": took, "wrap": True, "isSubtle": True})
    content = {
        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
        "type": "AdaptiveCard",
        "version": "1.4",
        "body": body,
    }
    if run_url:
        content["actions"] = [{"type": "Action.OpenUrl", "title": "Open the run", "url": run_url}]
    return {
        "type": "message",
        "attachments": [
            {"contentType": "application/vnd.microsoft.card.adaptive", "content": content}
        ],
    }


def _took(run_seconds: float | None, durations: dict[str, float]) -> str:
    """"Took 18 min: the notebooks 9 min on Linux, 8 min on macOS and 17 min on Windows"."""
    systems = _list([f"{_duration(t)} on {NAMES.get(s, s)}" for s, t in durations.items()])
    if run_seconds is None:
        return f"The notebooks took {systems}" if systems else ""
    return f"Took {_duration(run_seconds)}" + (f": the notebooks {systems}" if systems else "")


def _duration(seconds: float) -> str:
    """"45 s", "9 min", "1 h 05 min"."""
    if round(seconds) < 60:
        return f"{round(seconds)} s"
    minutes = round(seconds / 60)
    return f"{minutes} min" if minutes < 60 else f"{minutes // 60} h {minutes % 60:02d} min"


def _list(names: list[str]) -> str:
    """"Linux, macOS and Windows"."""
    return " and ".join([", ".join(names[:-1]), names[-1]]) if len(names) > 1 else "".join(names)


def _key(notebook: str) -> str:
    """A notebook's path the same on every system: `10.71728/<dataset>/notebook.ipynb`."""
    return notebook.replace("\\", "/").removeprefix("./")


def _line(notebook: str, by_system: dict[str, dict | None]) -> str:
    dataset = notebook.split("/")[-2]
    systems = _list([NAMES.get(s, s) for s in by_system])
    # The first report with an error says it; the others usually say the same
    for report in by_system.values():
        if report is None:
            continue
        errors = report.get("errors") or {}
        if errors.get("runtime"):
            e = errors["runtime"][0]
            text = " ".join(f"{e['name']}: {e['message']}".split())
            if len(text) > MESSAGE_LENGTH:
                text = text[: MESSAGE_LENGTH - 1] + "…"
            return f"- **{dataset}** ({systems}): cell {e['cell']}, {text}"
        if errors.get("over_budget"):
            return f"- **{dataset}** ({systems}): over budget, {'; '.join(errors['over_budget'])}"
    return f"- **{dataset}** ({systems}): no report, it didn't run"


if __name__ == "__main__":
    raise SystemExit(main(Path(sys.argv[1])))
