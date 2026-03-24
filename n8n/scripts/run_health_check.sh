#!/usr/bin/env bash
# DevHub Health Check — draait 4 checks en output gestructureerd JSON
# Gebruik: /scripts/run_health_check.sh /devhub
set -euo pipefail

REPO_PATH="${1:-/devhub}"
VENV="/opt/devhub-venv/bin"

cd "$REPO_PATH"

# ── 1. pytest ────────────────────────────────────────────────────────────────
pytest_exit=0
pytest_output=$("$VENV/pytest" --tb=short -q 2>&1) || pytest_exit=$?
pytest_summary=$(echo "$pytest_output" | tail -1)

# ── 2. ruff ──────────────────────────────────────────────────────────────────
ruff_exit=0
ruff_output=$("$VENV/ruff" check . --output-format=json 2>/dev/null) || ruff_exit=$?
ruff_count=$(echo "$ruff_output" | python3 -c "import sys,json; print(len(json.load(sys.stdin)))" 2>/dev/null || echo "0")

# ── 3. pip-audit ─────────────────────────────────────────────────────────────
audit_exit=0
audit_output=$("$VENV/pip-audit" --format=json 2>/dev/null) || audit_exit=$?
cve_count=$(echo "$audit_output" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    vulns = data.get('dependencies', [])
    count = sum(len(d.get('vulns', [])) for d in vulns)
    print(count)
except:
    print(0)
" 2>/dev/null || echo "0")

# ── 4. outdated deps ────────────────────────────────────────────────────────
outdated_output=$(pip list --outdated --format=json 2>/dev/null || echo "[]")
outdated_count=$(echo "$outdated_output" | python3 -c "import sys,json; print(len(json.load(sys.stdin)))" 2>/dev/null || echo "0")

# ── Severity bepaling ────────────────────────────────────────────────────────
severity="GREEN"

if [ "$pytest_exit" -ne 0 ]; then
    severity="RED"
elif [ "$cve_count" -gt 0 ]; then
    severity="RED"
elif [ "$ruff_count" -gt 0 ]; then
    severity="YELLOW"
elif [ "$outdated_count" -gt 5 ]; then
    severity="YELLOW"
fi

# ── JSON output ──────────────────────────────────────────────────────────────
cat <<EOF
{
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "severity": "$severity",
  "checks": {
    "pytest": {
      "exit_code": $pytest_exit,
      "summary": "$(echo "$pytest_summary" | sed 's/"/\\"/g')"
    },
    "ruff": {
      "exit_code": $ruff_exit,
      "error_count": $ruff_count
    },
    "pip_audit": {
      "exit_code": $audit_exit,
      "cve_count": $cve_count
    },
    "outdated": {
      "count": $outdated_count
    }
  }
}
EOF
