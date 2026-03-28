"""
DocsAgent — Parallelle documentatie-generatie volgens Diátaxis+ framework.

Ontvangt DocGenRequests van de DevOrchestrator en genereert/updatet
documentatie parallel aan development werk. Raakt nooit code, alleen docs.

Diátaxis+ categorieën in drie lagen:
- Laag 1 (Product): Tutorial, How-to, Reference, Explanation
- Laag 2 (Proces): Pattern, Analysis, Decision, Retrospective
- Laag 3 (Kennisbank): Methodology, Best Practice, SOTA Review, Playbook
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal

from devhub_core.contracts.dev_contracts import DocGenRequest

logger = logging.getLogger(__name__)


# Diátaxis templates per categorie
DIATAXIS_TEMPLATES: dict[str, str] = {
    "tutorial": """# {title}

> **Type:** Tutorial (leren door doen)
> **Doelgroep:** {audience}
> **Gegenereerd:** {timestamp}

## Wat je gaat leren

<!-- Beschrijf het leerdoel -->

## Vereisten

<!-- Wat moet de lezer al weten/hebben -->

## Stappen

### Stap 1: {step_1}

<!-- Instructies -->

### Stap 2: {step_2}

<!-- Instructies -->

## Samenvatting

<!-- Wat heeft de lezer geleerd -->
""",
    "howto": """# {title}

> **Type:** How-to guide (taak uitvoeren)
> **Doelgroep:** {audience}
> **Gegenereerd:** {timestamp}

## Probleem

<!-- Welk probleem lost dit op -->

## Oplossing

### Stap 1

<!-- Instructies -->

### Stap 2

<!-- Instructies -->

## Veelvoorkomende problemen

<!-- Troubleshooting -->
""",
    "reference": """# {title}

> **Type:** Reference (informatie opzoeken)
> **Doelgroep:** {audience}
> **Gegenereerd:** {timestamp}

## Overzicht

<!-- Korte beschrijving -->

## API / Interface

<!-- Technische details -->

## Parameters

| Parameter | Type | Beschrijving |
|-----------|------|-------------|
| | | |

## Voorbeelden

```python
# Voorbeeld
```
""",
    "explanation": """# {title}

> **Type:** Explanation (achtergrond en context)
> **Doelgroep:** {audience}
> **Gegenereerd:** {timestamp}

## Context

<!-- Waarom bestaat dit -->

## Hoe het werkt

<!-- Uitleg van het mechanisme -->

## Design beslissingen

<!-- Waarom deze aanpak -->

## Gerelateerd

<!-- Links naar gerelateerde docs -->
""",
    # --- Laag 2: Proces ---
    "pattern": """# {title}

> **Type:** Pattern (gevonden patroon)
> **Doelgroep:** {audience}
> **Gegenereerd:** {timestamp}

## Context

<!-- In welke situatie doet dit patroon zich voor -->

## Probleem

<!-- Welk terugkerend probleem lost dit patroon op -->

## Oplossing

<!-- Beschrijving van het patroon -->

## Krachten en afwegingen

<!-- Welke krachten spelen mee, welke trade-offs -->

## Consequenties

<!-- Wat zijn de gevolgen van dit patroon -->

## Gerelateerde patronen

<!-- Vergelijking met alternatieve patronen -->
""",
    "analysis": """# {title}

> **Type:** Analysis (onderzoek en bevindingen)
> **Doelgroep:** {audience}
> **Gegenereerd:** {timestamp}

## Onderzoeksvraag

<!-- Wat willen we weten -->

## Methode

<!-- Hoe is dit onderzocht -->

## Bevindingen

<!-- Wat is gevonden -->

## Conclusie

<!-- Wat betekent dit -->

## Aanbevelingen

<!-- Wat adviseren we op basis van de bevindingen -->
""",
    "decision": """# {title}

> **Type:** Decision (architectuur/ontwerp-beslissing)
> **Doelgroep:** {audience}
> **Gegenereerd:** {timestamp}

## Context

<!-- Welke situatie leidde tot deze beslissing -->

## Beslissing

<!-- Wat is besloten -->

## Argumenten voor

<!-- Waarom deze keuze -->

## Argumenten tegen

<!-- Welke nadelen zijn er -->

## Consequenties

<!-- Wat zijn de gevolgen -->

## Status

<!-- Voorstel / Geaccepteerd / Herzien / Vervangen -->
""",
    "retrospective": """# {title}

> **Type:** Retrospective (terugblik)
> **Doelgroep:** {audience}
> **Gegenereerd:** {timestamp}

## Sprint / Periode

<!-- Welke sprint of periode betreft dit -->

## Wat ging goed

<!-- Successen en positieve observaties -->

## Wat kan beter

<!-- Verbeterpunten en geleerde lessen -->

## Actiepunten

<!-- Concrete vervolgacties -->

## Metrics

<!-- Relevante cijfers: tests, velocity, cycle time -->
""",
    # --- Laag 3: Kennisbank ---
    "methodology": """# {title}

> **Type:** Methodology (werkwijze/methodiek)
> **Doelgroep:** {audience}
> **Gegenereerd:** {timestamp}

## Doel

<!-- Wat bereik je met deze methodiek -->

## Principes

<!-- Kernprincipes van de methodiek -->

## Proces / Stappen

<!-- Hoe pas je de methodiek toe -->

## Rollen

<!-- Wie is betrokken en in welke rol -->

## Wanneer toepassen

<!-- In welke situatie is deze methodiek geschikt -->

## Bronnen

<!-- Referenties en verdere lezing -->
""",
    "best_practice": """# {title}

> **Type:** Best Practice (bewezen werkwijze)
> **Doelgroep:** {audience}
> **Gegenereerd:** {timestamp}

## Principe

<!-- Wat is de best practice -->

## Waarom

<!-- Waarom is dit een best practice, welk bewijs -->

## Hoe toepassen

<!-- Concrete stappen om toe te passen -->

## Valkuilen

<!-- Veelgemaakte fouten bij toepassing -->

## Voorbeelden

<!-- Concrete voorbeelden uit de praktijk -->
""",
    "sota_review": """# {title}

> **Type:** SOTA Review (state of the art)
> **Doelgroep:** {audience}
> **Gegenereerd:** {timestamp}

## Onderwerp

<!-- Welk vakgebied of technologie -->

## Huidige stand

<!-- Wat is de huidige state of the art -->

## Belangrijke spelers

<!-- Wie zijn de belangrijkste partijen/tools -->

## Trends

<!-- Welke ontwikkelingen tekenen zich af -->

## Bronnen

<!-- Primaire bronnen en referenties -->

## Beoordeling

<!-- Relevantie voor DevHub en projecten -->
""",
    "playbook": """# {title}

> **Type:** Playbook (draaiboek)
> **Doelgroep:** {audience}
> **Gegenereerd:** {timestamp}

## Situatie

<!-- Wanneer gebruik je dit playbook -->

## Voorbereidingschecklist

<!-- Wat moet klaarstaan voordat je begint -->

## Stappen

### Stap 1

<!-- Eerste actie -->

### Stap 2

<!-- Tweede actie -->

## Escalatiepunten

<!-- Wanneer en naar wie escaleren -->

## Afronding

<!-- Hoe sluit je het af en wat documenteer je -->
""",
}


@dataclass
class DocResult:
    """Resultaat van een documentatie-generatie actie."""

    task_id: str
    files_generated: list[str]
    files_updated: list[str]
    diataxis_category: str
    status: Literal["generated", "updated", "skipped", "error"]
    message: str = ""


class DocsAgent:
    """Agent voor parallelle documentatie-generatie.

    Ontvangt DocGenRequests en produceert Diátaxis-conforme markdown bestanden.
    Schrijft alleen naar docs/, raakt nooit code.
    """

    def __init__(self, docs_root: Path | None = None) -> None:
        self._docs_root = docs_root or Path("docs")

    def process_request(self, request: DocGenRequest) -> DocResult:
        """Verwerk een documentatie-opdracht.

        Args:
            request: DocGenRequest van de DevOrchestrator

        Returns:
            DocResult met status en gegenereerde/bijgewerkte bestanden
        """
        generated: list[str] = []
        updated: list[str] = []

        for target in request.target_files:
            target_p = Path(target)
            target_path = target_p if target_p.is_absolute() else self._docs_root / target

            if target_path.exists():
                # Update bestaand bestand — voeg metadata header toe als die ontbreekt
                self._update_doc(target_path, request)
                updated.append(str(target_path))
            else:
                # Genereer nieuw bestand vanuit Diátaxis template
                self._generate_doc(target_path, request)
                generated.append(str(target_path))

        status: Literal["generated", "updated", "skipped", "error"] = "generated"
        if updated and not generated:
            status = "updated"
        elif not generated and not updated:
            status = "skipped"

        result = DocResult(
            task_id=request.task_id,
            files_generated=generated,
            files_updated=updated,
            diataxis_category=request.diataxis_category,
            status=status,
            message=f"{len(generated)} generated, {len(updated)} updated",
        )

        logger.info(
            "DocsAgent: %s — %s (%s)",
            request.task_id,
            result.message,
            request.diataxis_category,
        )
        return result

    def analyze_coverage(self, docs_path: Path | None = None) -> dict[str, list[str]]:
        """Analyseer Diátaxis-dekking van bestaande documentatie.

        Returns:
            Dict met per categorie een lijst van gevonden docs.
        """
        root = docs_path or self._docs_root
        coverage: dict[str, list[str]] = {
            "tutorial": [],
            "howto": [],
            "reference": [],
            "explanation": [],
            "pattern": [],
            "analysis": [],
            "decision": [],
            "retrospective": [],
            "methodology": [],
            "best_practice": [],
            "sota_review": [],
            "playbook": [],
            "uncategorized": [],
        }

        if not root.exists():
            return coverage

        for md_file in root.rglob("*.md"):
            category = self._detect_category(md_file)
            coverage[category].append(str(md_file.relative_to(root)))

        return coverage

    def suggest_docs(
        self,
        source_files: list[str],
        existing_coverage: dict[str, list[str]] | None = None,
    ) -> list[DocGenRequest]:
        """Suggereer documentatie-opdrachten op basis van bronbestanden.

        Analyseert welke Diátaxis-categorieën ontbreken voor de gegeven bestanden.
        """
        suggestions: list[DocGenRequest] = []
        coverage = existing_coverage or self.analyze_coverage()

        for source in source_files:
            source_name = Path(source).stem

            # Check of er al reference docs zijn voor dit bestand
            has_reference = any(source_name in doc for doc in coverage.get("reference", []))
            if not has_reference:
                suggestions.append(
                    DocGenRequest(
                        task_id=f"AUTO-REF-{source_name}",
                        target_files=[f"reference/{source_name}.md"],
                        diataxis_category="reference",
                        audience="developer",
                        source_code_files=[source],
                    )
                )

        return suggestions

    # --- Privé helpers ---

    def _generate_doc(self, target_path: Path, request: DocGenRequest) -> None:
        """Genereer een nieuw document vanuit Diátaxis template."""
        fallback = DIATAXIS_TEMPLATES["reference"]
        template = DIATAXIS_TEMPLATES.get(request.diataxis_category, fallback)

        title = self._derive_title(target_path, request)
        content = template.format(
            title=title,
            audience=request.audience,
            timestamp=datetime.now(UTC).strftime("%Y-%m-%d"),
            step_1="Eerste stap",
            step_2="Tweede stap",
        )

        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_text(content)

    def _update_doc(self, target_path: Path, request: DocGenRequest) -> None:
        """Update een bestaand document met metadata als die ontbreekt."""
        content = target_path.read_text()

        # Check of er al een Diátaxis type header is
        if "> **Type:**" not in content:
            header = (
                f"\n> **Type:** {request.diataxis_category.capitalize()}\n"
                f"> **Doelgroep:** {request.audience}\n"
                f"> **Laatst bijgewerkt:** {datetime.now(UTC).strftime('%Y-%m-%d')}\n\n"
            )
            # Voeg header toe na de eerste heading
            lines = content.split("\n")
            insert_idx = 1  # Na eerste regel
            for i, line in enumerate(lines):
                if line.startswith("# "):
                    insert_idx = i + 1
                    break
            lines.insert(insert_idx, header)
            target_path.write_text("\n".join(lines))

    def _detect_category(self, md_file: Path) -> str:
        """Detecteer Diátaxis categorie van een bestaand markdown bestand."""
        try:
            content = md_file.read_text(errors="ignore")[:500]
        except OSError:
            return "uncategorized"

        content_lower = content.lower()

        # Laag 1: Product (Diátaxis standaard)
        if "tutorial" in content_lower or "leren" in content_lower:
            return "tutorial"
        if "how-to" in content_lower or "howto" in content_lower or "stappen" in content_lower:
            return "howto"
        if "reference" in content_lower or "api" in content_lower:
            return "reference"
        explanation_kw = "explanation" in content_lower or "achtergrond" in content_lower
        if explanation_kw or "context" in content_lower:
            return "explanation"

        # Laag 2: Proces
        if "pattern" in content_lower or "patroon" in content_lower:
            return "pattern"
        analysis_kw = "analysis" in content_lower or "analyse" in content_lower
        if analysis_kw or "bevindingen" in content_lower:
            return "analysis"
        decision_kw = "decision" in content_lower or "beslissing" in content_lower
        if decision_kw or "adr" in content_lower:
            return "decision"
        retro_kw = "retrospective" in content_lower or "retro" in content_lower
        if retro_kw or "terugblik" in content_lower:
            return "retrospective"

        # Laag 3: Kennisbank
        if "methodology" in content_lower or "methodiek" in content_lower:
            return "methodology"
        if "best practice" in content_lower or "best_practice" in content_lower:
            return "best_practice"
        if "sota" in content_lower or "state of the art" in content_lower:
            return "sota_review"
        if "playbook" in content_lower or "draaiboek" in content_lower:
            return "playbook"

        # Check pad-gebaseerd
        path_str = str(md_file).lower()
        all_cats = [
            "tutorial",
            "howto",
            "reference",
            "explanation",
            "pattern",
            "analysis",
            "decision",
            "retrospective",
            "methodology",
            "best_practice",
            "sota_review",
            "playbook",
        ]
        for cat in all_cats:
            if cat in path_str:
                return cat

        return "uncategorized"

    def _derive_title(self, target_path: Path, request: DocGenRequest) -> str:
        """Leid een titel af uit het pad en de request."""
        stem = target_path.stem.replace("_", " ").replace("-", " ").title()
        return stem
