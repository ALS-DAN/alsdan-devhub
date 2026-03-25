# SPRINT_INTAKE: n8n Governance Check on Merge

| Veld | Waarde |
|------|--------|
| **Gegenereerd door** | Cowork — alsdan-devhub |
| **Status** | INBOX |
| **Fase** | 2 (Skills + Governance) |
| **Datum** | 2026-03-24 |
| **Bron** | IDEA_N8N_GOVERNANCE_CHECK_ON_MERGE_2026-03-24.md |

---

## Doel

Implementeer een n8n-workflow die bij elke push naar `main` automatisch valideert of de wijzigingen voldoen aan de DEV_CONSTITUTION — specifiek secrets-detectie (Art. 8), EVIDENCE-frontmatter (Art. 5), impact-zone labels (Art. 7), RED-zone paden-bewaking en commit message kwaliteit (Art. 4). Bij schendingen wordt een GitHub Issue aangemaakt, een commit comment gepost, en Niels gemaild.

## Probleemstelling

**Waarom nu**: De DEV_CONSTITUTION is het fundament van DevHub's governance, maar naleving is volledig afhankelijk van menselijke discipline. Niels werkt solo, vaak laat op de avond — juist dan is de kans groter dat er iets direct naar main wordt gepusht zonder PR. De PR Quality Gate (IDEA 4) bewaakt vóór merge, maar deze workflow vangt alles op dat tóch doorkomt: directe pushes, PR-merges zonder quality gate, of regels die de quality gate niet checkt.

**Fase-context**: Fase 2 (Skills + Governance). Automatiseert wat de `devhub-governance-check` skill (Fase 2.3) handmatig doet. Complementair aan PR Quality Gate: gate vóór merge, governance check ná merge.

**Probleem**: Governance-schendingen (secrets in commits, ontbrekende EVIDENCE-grading, ongelabelde RED-zone wijzigingen) worden niet automatisch gedetecteerd.
**Oplossing**: Post-merge n8n-workflow die elke push naar main toetst aan de DEV_CONSTITUTION.
**Grenzen**: Alleen DevHub-repo. Read-only checks, schrijft alleen issues/comments. Geen destructieve operaties.
**Appetite**: Klein — één sprint, hergebruikt n8n-infra + vergelijkbaar patroon als Health Check en PR Quality Gate.

## Deliverables

- [ ] n8n-workflow "Governance Check on Merge" met nodes:
  - `githubTrigger` (push naar main)
  - `github` (commit details: files changed, message, author)
  - `executeCommand` (detect-secrets scan — Art. 8)
  - `executeCommand` (frontmatter check op gewijzigde .md bestanden — Art. 5)
  - `code` (impact-zone label analyse in commit message — Art. 7)
  - `code` (RED-zone paden check — Art. 7)
  - `code` (commit message kwaliteit — Art. 4)
  - `code` (aggregatie: alle checks → compliance rapport)
  - `if` (violations.length > 0)
  - `github` (issue create met labels: governance-violation, automated)
  - `github` (commit comment met schendingsdetails)
  - `emailSend` (notificatie bij schending)
- [ ] `detect-secrets` geïnstalleerd in DevHub venv + `.secrets.baseline` aangemaakt en gecommit
- [ ] RED-zone paden definitief vastgesteld: `governance/`, `docs/compliance/DEV_CONSTITUTION.md`, `.claude/`, `config/`, `agents/`
- [ ] Governance Issue template met schendingstabel + aanbevolen acties
- [ ] Stil succes: geen actie bij compliance (geen ruis)
- [ ] Handmatige test-run: push met opzettelijke schending, verifieer issue + comment + email
- [ ] Documentatie: setup-guide in `docs/operations/n8n-governance-check.md`

## Afhankelijkheden

| Type | Detail |
|------|--------|
| **Geblokkeerd door** | SPRINT_INTAKE_N8N_HEALTH_CHECK — vereist werkende n8n Docker + credentials |
| **BORIS-impact** | Nee — draait puur op DevHub. BORIS heeft eigen governance (AI_CONSTITUTION) |
| **Tooling vereist** | n8n Docker (al opgezet), GitHub PAT, Gmail App Password, `detect-secrets` (pip) |
| **Bestaande code** | `devhub-governance-check` skill (referentie voor check-logica), DEV_CONSTITUTION.md |

## Fase-context

**Huidige fase**: Fase 2 (Skills + Governance).
**Fit**: Direct — automatiseert de governance-check skill en implementeert Art. 2, 4, 5, 7 en 8 van de DEV_CONSTITUTION. Complementair aan PR Quality Gate (vóór merge) als vangnet ná merge.

## Open vragen voor Claude Code

1. **detect-secrets installatie**: checkt of `detect-secrets` in de DevHub venv zit, voegt toe indien nodig. Moet ook in de n8n Docker container beschikbaar zijn (via volume mount of Dockerfile).
2. **`.secrets.baseline`**: eenmalig aanmaken via `detect-secrets scan > .secrets.baseline` en committen. Dit is de referentie waartegen nieuwe commits worden gecheckt.
3. **RED-zone paden verfijnen**: de voorgestelde lijst (`governance/`, `docs/compliance/DEV_CONSTITUTION.md`, `.claude/`, `config/`, `agents/`) moet worden gevalideerd tegen de actuele repo-structuur. Zijn er paden die missen of teveel zijn?
4. **Frontmatter conventie**: welke frontmatter-velden zijn verplicht voor kennisbestanden? Minimaal `evidence_grade`. Claude Code stelt een conventie vast en documenteert die.

## Prioriteit

**Hoog** — derde workflow in de implementatievolgorde. Samen met Health Check (scheduled) en PR Quality Gate (pre-merge) vormt dit de drie-punts bewaking. De governance check is het ultieme vangnet dat garandeert dat de DEV_CONSTITUTION wordt nageleefd, ook bij directe pushes.

## Technische richting

*(Claude Code mag afwijken)*

- **Trigger**: `githubTrigger` met `push` event op main branch
- **Secrets scan**: `detect-secrets scan --list-all-secrets` (Art. 8)
- **Frontmatter check**: `head -10 {file}` + parse voor `evidence_grade` (Art. 5)
- **Impact-zone**: parse commit message voor `[GREEN]`/`[YELLOW]`/`[RED]` tags (Art. 7)
- **RED-zone paden**: hardcoded lijst, vergelijken met `commit.files[].filename` (Art. 7)
- **Commit message**: minimaal 10 tekens, niet "update" (Art. 4)
- **Stil succes**: geen actie bij compliance — geen GitHub Issue, geen email

## DEV_CONSTITUTION impact

| Artikel | Impact | Toelichting |
|---------|--------|-------------|
| Art. 2 (Verificatieplicht) | Directe implementatie | Automatische verificatie van elke merge |
| Art. 4 (Transparantie) | Directe implementatie | Commit message kwaliteitscheck |
| Art. 5 (Kennisintegriteit) | Directe implementatie | EVIDENCE-frontmatter validatie |
| Art. 7 (Impact-zonering) | Directe implementatie | Impact-label + RED-zone paden check |
| Art. 8 (Dataminimalisatie) | Directe implementatie | Secrets/credentials/PII detectie |

## Cynefin-classificatie

**Gecompliceerd** → Sprint-type: **FEAT**. De individuele checks zijn simpel, maar de combinatie van 5 governance-regels in één workflow, plus de detect-secrets integratie en frontmatter-conventie, vereist zorgvuldige engineering.

## Shape Up samenvatting

| Dimensie | Waarde |
|----------|--------|
| Probleem | Governance-schendingen worden niet automatisch gedetecteerd, vooral bij directe pushes |
| Oplossing | Post-merge n8n-workflow die elke push toetst aan 5 DEV_CONSTITUTION artikelen |
| Grenzen | Alleen DevHub, read-only checks, stil bij compliance |
| Appetite | Klein (1 sprint, hergebruikt n8n-infra) |
| Risico | GREEN — read-only checks, schrijft alleen issues/comments |
