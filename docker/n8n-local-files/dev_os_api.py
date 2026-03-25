#!/usr/bin/env python3
"""
Dev-OS Log API — Standalone micro-service voor n8n workflow logging.

Draait APART van projecten (geen productie-impact).
Slaat Dev-OS log entries op in SQLite.

Usage:
    python3 docker/n8n-local-files/dev_os_api.py

Endpoints:
    POST /log              — Schrijf een log entry
    GET  /log              — Lees alle entries (optioneel ?limit=N&type=X)
    GET  /dashboard        — Genereer health dashboard JSON
    GET  /healthz          — Health check
    POST /performance      — Schrijf agent performance entry
    GET  /performance      — Query agent performance (optioneel ?agent=X&date=Y&limit=N)
    POST /pipeline-summary — Schrijf dagelijkse pipeline samenvatting
    GET  /pipeline-summary — Query pipeline summaries (optioneel ?days=N)
"""

from __future__ import annotations

import json
import os
import sqlite3
from datetime import datetime, timedelta, UTC
from pathlib import Path

from fastapi import FastAPI
from pydantic import BaseModel, Field

DB_PATH = Path(os.environ.get("DEV_OS_DB_PATH", str(Path(__file__).parent / "dev_os.db")))
SCHEMA_PATH = Path(__file__).parent / "dev_os_schema.sql"

app = FastAPI(title="Dev-OS Log API", version="0.2.0")


def _get_db() -> sqlite3.Connection:
    db = sqlite3.connect(str(DB_PATH))
    db.row_factory = sqlite3.Row
    if not _table_exists(db):
        schema = SCHEMA_PATH.read_text()
        db.executescript(schema)
    return db


def _table_exists(db: sqlite3.Connection) -> bool:
    cur = db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='dev_os_log'")
    return cur.fetchone() is not None


class PerformanceEntry(BaseModel):
    agent_name: str
    avg_duration_s: float | None = None
    p95_duration_s: float | None = None
    request_count: int = 0
    safety_red: int = 0
    safety_yellow: int = 0
    safety_green: int = 0
    ldf_levels: dict | None = None


class PipelineSummary(BaseModel):
    date: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$")
    total_queries: int = 0
    red_count: int = 0
    yellow_count: int = 0
    green_count: int = 0
    avg_duration_s: float | None = None
    hitl_queue_depth: int = 0
    health_status: str | None = None


class LogEntry(BaseModel):
    type: str = Field(
        ...,
        pattern="^(decision|code|reflection|workflow|innovation|research|coaching)$",
    )
    project: str = "devhub"
    sprint: str | None = None
    phase: str | None = None
    context: str | None = None
    content: str
    rationale: str | None = None
    tags: list[str] | None = None
    evidence_grade: str | None = None
    growth_skill_area: str | None = None
    growth_observation: str | None = None
    source: str = Field(
        ...,
        pattern="^(github|cowork|claude_code|mentor_dev|research|n8n|manual)$",
    )
    raw_data: dict | None = None


@app.get("/healthz")
def healthz():
    return {"status": "ok", "db": str(DB_PATH), "exists": DB_PATH.exists()}


@app.post("/log")
def create_log(entry: LogEntry):
    db = _get_db()
    db.execute(
        """INSERT INTO dev_os_log
           (timestamp, type, project, sprint, phase, context, content,
            rationale, tags, evidence_grade, growth_skill_area,
            growth_observation, source, raw_data)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            datetime.now(UTC).isoformat(),
            entry.type,
            entry.project,
            entry.sprint,
            entry.phase,
            entry.context,
            entry.content,
            entry.rationale,
            json.dumps(entry.tags) if entry.tags else None,
            entry.evidence_grade,
            entry.growth_skill_area,
            entry.growth_observation,
            entry.source,
            json.dumps(entry.raw_data) if entry.raw_data else None,
        ),
    )
    db.commit()
    row_id = db.execute("SELECT last_insert_rowid()").fetchone()[0]
    total = db.execute("SELECT count(*) FROM dev_os_log").fetchone()[0]
    db.close()
    return {"status": "ok", "id": row_id, "total": total}


@app.get("/log")
def read_log(
    limit: int = 50,
    type: str | None = None,
    date: str | None = None,
):
    db = _get_db()
    query = "SELECT * FROM dev_os_log"
    params: list = []
    conditions: list[str] = []
    if type:
        conditions.append("type = ?")
        params.append(type)
    if date:
        conditions.append("timestamp LIKE ?")
        params.append(f"{date}%")
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    query += " ORDER BY id DESC LIMIT ?"
    params.append(limit)
    rows = db.execute(query, params).fetchall()
    db.close()
    return {"data": [dict(r) for r in rows], "count": len(rows)}


@app.get("/dashboard")
def dashboard():
    db = _get_db()
    total = db.execute("SELECT count(*) FROM dev_os_log").fetchone()[0]

    now = datetime.now(UTC)
    day_ago = (now - timedelta(days=1)).isoformat()
    week_ago = (now - timedelta(days=7)).isoformat()

    last_24h = db.execute(
        "SELECT count(*) FROM dev_os_log WHERE timestamp > ?", (day_ago,)
    ).fetchone()[0]
    last_7d = db.execute(
        "SELECT count(*) FROM dev_os_log WHERE timestamp > ?", (week_ago,)
    ).fetchone()[0]

    by_type = dict(db.execute("SELECT type, count(*) FROM dev_os_log GROUP BY type").fetchall())
    by_source = dict(
        db.execute("SELECT source, count(*) FROM dev_os_log GROUP BY source").fetchall()
    )
    sprints = [
        r[0]
        for r in db.execute(
            "SELECT DISTINCT sprint FROM dev_os_log WHERE sprint IS NOT NULL "
            "ORDER BY id DESC LIMIT 5"
        ).fetchall()
    ]
    db.close()

    return {
        "generated": now.isoformat(),
        "summary": {
            "total_entries": total,
            "last_24h": last_24h,
            "last_7d": last_7d,
            "active_sprint": sprints[0] if sprints else "geen",
        },
        "by_type": by_type,
        "by_source": by_source,
        "recent_sprints": sprints,
        "health": {
            "n8n": "operational",
            "dev_os_log": "active" if total > 0 else "empty",
            "github_capture": "active" if by_source.get("github", 0) > 0 else "pending",
        },
    }


@app.post("/performance")
def create_performance(entry: PerformanceEntry):
    db = _get_db()
    db.execute(
        """INSERT INTO agent_performance_log
           (timestamp, agent_name, avg_duration_s, p95_duration_s, request_count,
            safety_red, safety_yellow, safety_green, ldf_levels)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            datetime.now(UTC).isoformat(),
            entry.agent_name,
            entry.avg_duration_s,
            entry.p95_duration_s,
            entry.request_count,
            entry.safety_red,
            entry.safety_yellow,
            entry.safety_green,
            json.dumps(entry.ldf_levels) if entry.ldf_levels else None,
        ),
    )
    db.commit()
    row_id = db.execute("SELECT last_insert_rowid()").fetchone()[0]
    db.close()
    return {"status": "ok", "id": row_id}


@app.get("/performance")
def read_performance(
    agent: str | None = None,
    date: str | None = None,
    limit: int = 50,
):
    db = _get_db()
    query = "SELECT * FROM agent_performance_log"
    params: list = []
    conditions: list[str] = []
    if agent:
        conditions.append("agent_name = ?")
        params.append(agent)
    if date:
        conditions.append("timestamp LIKE ?")
        params.append(f"{date}%")
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    query += " ORDER BY id DESC LIMIT ?"
    params.append(limit)
    rows = db.execute(query, params).fetchall()
    db.close()
    return {"data": [dict(r) for r in rows], "count": len(rows)}


@app.post("/pipeline-summary")
def create_pipeline_summary(entry: PipelineSummary):
    db = _get_db()
    db.execute(
        """INSERT OR REPLACE INTO daily_pipeline_summary
           (date, total_queries, red_count, yellow_count, green_count,
            avg_duration_s, hitl_queue_depth, health_status)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            entry.date,
            entry.total_queries,
            entry.red_count,
            entry.yellow_count,
            entry.green_count,
            entry.avg_duration_s,
            entry.hitl_queue_depth,
            entry.health_status,
        ),
    )
    db.commit()
    row_id = db.execute("SELECT last_insert_rowid()").fetchone()[0]
    db.close()
    return {"status": "ok", "id": row_id}


@app.get("/pipeline-summary")
def read_pipeline_summary(days: int = 7):
    db = _get_db()
    cutoff = (datetime.now(UTC) - timedelta(days=days)).strftime("%Y-%m-%d")
    rows = db.execute(
        "SELECT * FROM daily_pipeline_summary WHERE date >= ? ORDER BY date DESC",
        (cutoff,),
    ).fetchall()
    db.close()
    return {"data": [dict(r) for r in rows], "count": len(rows)}


# ── Health Check Endpoints ────────────────────────────────────────────────

REPO_PATH = Path(os.environ.get("DEVHUB_REPO_PATH", "/repo"))

_latest_health: dict | None = None


def _run_cmd(cmd: list[str], cwd: Path, timeout: int = 120) -> tuple[int, str, str]:
    """Run a command and return (exit_code, stdout, stderr)."""
    import subprocess

    try:
        result = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True, timeout=timeout)
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "timeout"
    except FileNotFoundError:
        return -1, "", f"command not found: {cmd[0]}"


@app.get("/health/run")
def run_health_check():
    global _latest_health

    if not REPO_PATH.exists():
        return {"error": "repo not mounted", "path": str(REPO_PATH)}

    ts = datetime.now(UTC).isoformat()
    checks: dict = {}

    # 1. pytest
    exit_code, stdout, stderr = _run_cmd(
        ["python3", "-m", "pytest", "--tb=no", "-q", "-p", "no:cacheprovider"], REPO_PATH
    )
    lines = stdout.strip().split("\n")
    summary = lines[-1] if lines else ""
    checks["pytest"] = {
        "exit_code": exit_code,
        "summary": summary,
    }

    # 2. ruff
    exit_code, stdout, stderr = _run_cmd(["python3", "-m", "ruff", "check", "--quiet"], REPO_PATH)
    error_count = len(stdout.strip().split("\n")) if stdout.strip() else 0
    checks["ruff"] = {
        "exit_code": exit_code,
        "error_count": error_count,
    }

    # 3. pip-audit
    exit_code, stdout, stderr = _run_cmd(
        ["python3", "-m", "pip_audit", "--format=json", "--progress-spinner=off"],
        REPO_PATH,
        timeout=180,
    )
    cve_count = 0
    if stdout.strip():
        try:
            vulns = json.loads(stdout)
            if isinstance(vulns, list):
                cve_count = len(vulns)
            elif isinstance(vulns, dict) and "dependencies" in vulns:
                cve_count = sum(
                    len(d.get("vulns", [])) for d in vulns["dependencies"] if d.get("vulns")
                )
        except json.JSONDecodeError:
            pass
    checks["pip_audit"] = {
        "exit_code": exit_code,
        "cve_count": cve_count,
    }

    # 4. outdated
    exit_code, stdout, stderr = _run_cmd(["pip", "list", "--outdated", "--format=json"], REPO_PATH)
    outdated_count = 0
    if stdout.strip():
        try:
            outdated_count = len(json.loads(stdout))
        except json.JSONDecodeError:
            pass
    checks["outdated"] = {"count": outdated_count}

    # Determine severity
    if checks["pytest"]["exit_code"] != 0 or checks["pip_audit"]["cve_count"] > 0:
        severity = "RED"
    elif checks["ruff"]["error_count"] > 0 or checks["outdated"]["count"] > 5:
        severity = "YELLOW"
    else:
        severity = "GREEN"

    report = {
        "timestamp": ts,
        "severity": severity,
        "checks": checks,
    }

    _latest_health = report
    return report


@app.get("/health/latest")
def get_latest_health():
    if _latest_health is None:
        return {"error": "no health check has been run yet"}
    return _latest_health


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)  # nosec B104 — Docker container, must bind all interfaces
