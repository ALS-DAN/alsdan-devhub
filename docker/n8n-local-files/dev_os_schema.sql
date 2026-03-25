CREATE TABLE IF NOT EXISTS dev_os_log (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp   TEXT NOT NULL,  -- ISO8601
    type        TEXT NOT NULL CHECK(type IN (
                  'decision','code','reflection','workflow',
                  'innovation','research','coaching')),
    project     TEXT DEFAULT 'devhub',
    sprint      TEXT,           -- SPRINT_NAME of NULL
    phase       TEXT CHECK(phase IN ('ORIENTEREN','BOUWEN','BEHEERSEN')),
    context     TEXT,
    content     TEXT NOT NULL,
    rationale   TEXT,
    tags        TEXT,           -- JSON array
    evidence_grade TEXT CHECK(evidence_grade IN (
                  'GOLD','SILVER','BRONZE','SPECULATIVE')),
    growth_skill_area  TEXT,
    growth_observation TEXT,
    source      TEXT NOT NULL CHECK(source IN (
                  'github','cowork','claude_code','mentor_dev',
                  'research','n8n','manual')),
    raw_data    TEXT            -- originele JSON voor auditing
);

CREATE INDEX IF NOT EXISTS idx_log_date ON dev_os_log(timestamp);
CREATE INDEX IF NOT EXISTS idx_log_type ON dev_os_log(type);
CREATE INDEX IF NOT EXISTS idx_log_sprint ON dev_os_log(sprint);

-- ── Observability tabellen (FASE 4) ─────────────────────────────────────

CREATE TABLE IF NOT EXISTS agent_performance_log (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp       TEXT NOT NULL,  -- ISO8601
    agent_name      TEXT NOT NULL,
    avg_duration_s  REAL,
    p95_duration_s  REAL,
    request_count   INTEGER DEFAULT 0,
    safety_red      INTEGER DEFAULT 0,
    safety_yellow   INTEGER DEFAULT 0,
    safety_green    INTEGER DEFAULT 0,
    ldf_levels      TEXT   -- JSON: {"0": N, "1": N, "2": N, "3": N}
);

CREATE INDEX IF NOT EXISTS idx_perf_timestamp ON agent_performance_log(timestamp);
CREATE INDEX IF NOT EXISTS idx_perf_agent ON agent_performance_log(agent_name);

CREATE TABLE IF NOT EXISTS daily_pipeline_summary (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    date             TEXT NOT NULL UNIQUE,  -- YYYY-MM-DD
    total_queries    INTEGER DEFAULT 0,
    red_count        INTEGER DEFAULT 0,
    yellow_count     INTEGER DEFAULT 0,
    green_count      INTEGER DEFAULT 0,
    avg_duration_s   REAL,
    hitl_queue_depth INTEGER DEFAULT 0,
    health_status    TEXT   -- healthy|degraded|critical
);

CREATE INDEX IF NOT EXISTS idx_summary_date ON daily_pipeline_summary(date);
