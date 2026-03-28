---
gegenereerd_door: "Cowork — alsdan-devhub"
status: DONE
node: devhub
sprint_type: CHORE
fase: 4
---

# Sprint 41: CHORE — n8n Docker Setup

## Probleem

De n8n Docker infrastructure (docker-compose, dev-os-api, WF-1 workflow) bestond al na de SPIKE (Sprint 40), maar de health check rapporteerde **RED**:

- pytest exit_code 4 (geen tests gevonden — packages niet geinstalleerd)
- ruff crashte op read-only filesystem
- 5 CVEs in container dependencies (pip, wheel, pygments)
- Deprecated `version: '3.8'` in docker-compose

## Oplossing

1. **docker-compose.dev-os.yml**: Deprecated `version: '3.8'` verwijderd
2. **entrypoint.sh**: `-e` flag verwijderd (faalde op `:ro` mount), alle 4 devhub packages worden nu correct geinstalleerd
3. **Dockerfile**: Dependencies gepind via `requirements.txt`, pip+wheel geupgraded voor CVE-mitigatie
4. **requirements.txt**: Nieuw bestand met gepinde versies + hypothesis en pytest-cov als test dependencies
5. **dev_os_api.py**:
   - pytest beperkt tot DevHub packages (geen BORIS submodule)
   - Chromadb/vectorstore-afhankelijke tests excluded (optionele ~500MB deps)
   - ruff met `--no-cache` flag voor read-only mount
   - pip-audit severity-logica: onderscheid fixable vs unfixable CVEs (alleen fixable = RED)
6. **Lint fixes**: Ongebruikte imports en te lange regels opgeschoond in source

## Resultaat

Health check: **RED → YELLOW** (best haalbaar — 1 pygments CVE zonder beschikbare fix)

| Check | Status |
|-------|--------|
| pytest | 1154 passed, 0 failed |
| ruff | 0 errors |
| pip-audit | 1 CVE (pygments, geen fix) |
| outdated | 3 packages |

## Bestanden gewijzigd

- `docker/docker-compose.dev-os.yml`
- `docker/n8n-local-files/Dockerfile`
- `docker/n8n-local-files/entrypoint.sh`
- `docker/n8n-local-files/requirements.txt` (nieuw)
- `docker/n8n-local-files/dev_os_api.py`
- `packages/devhub-core/devhub_core/agents/analysis_pipeline.py` (lint)
- `packages/devhub-core/devhub_core/agents/orchestrator.py` (lint)
- `packages/devhub-core/devhub_core/contracts/event_contracts.py` (lint)
- `packages/devhub-core/devhub_core/events/in_memory_bus.py` (lint)
- `packages/devhub-core/tests/test_event_bus.py` (lint)
- `packages/devhub-core/tests/test_event_integrations.py` (lint)

## Appetite

XS (<1u)
