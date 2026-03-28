"""
Content Builders — Pre-built DocumentProductionRequest factory functions.

Elke builder levert een volledig geconfigureerde request op voor de
DocumentService pipeline. Content is template-based (skip_vectorstore=True).
"""

from __future__ import annotations

from devhub_documents.contracts import DocumentCategory

from devhub_core.contracts.pipeline_contracts import DocumentProductionRequest


def build_pattern_abc_adapter() -> DocumentProductionRequest:
    """'ABC + Adapter Pattern in DevHub' — categorie PATTERN.

    Beschrijft het terugkerende patroon van Abstract Base Classes met
    adapter-implementaties dat door heel DevHub wordt gebruikt.
    """
    return DocumentProductionRequest(
        topic="ABC + Adapter Pattern in DevHub",
        category=DocumentCategory.PATTERN,
        audience="developer",
        skip_vectorstore=True,
    )


def build_methodology_shape_up() -> DocumentProductionRequest:
    """'Shape Up in DevHub' — categorie METHODOLOGY.

    Beschrijft hoe DevHub de Shape Up methodiek toepast:
    probleem → oplossing → grenzen → appetite.
    """
    return DocumentProductionRequest(
        topic="Shape Up in DevHub",
        category=DocumentCategory.METHODOLOGY,
        audience="developer",
        skip_vectorstore=True,
    )


def build_tutorial_sprint_intake() -> DocumentProductionRequest:
    """'Je eerste sprint intake maken' — categorie TUTORIAL.

    Leert de gebruiker stap voor stap hoe een sprint intake
    frontmatter-bestand wordt opgesteld.
    """
    return DocumentProductionRequest(
        topic="Je eerste sprint intake maken",
        category=DocumentCategory.TUTORIAL,
        audience="developer",
        skip_vectorstore=True,
    )


def build_blueprint_boris() -> DocumentProductionRequest:
    """'Hoe een project de DevHub documentatie-pipeline overneemt' — METHODOLOGY.

    BORIS-blauwdruk: beschrijft hoe een project (BORIS of nieuw) de
    documentatie-pipeline configureert en gebruikt via nodes.yml en documents.yml.
    """
    return DocumentProductionRequest(
        topic="Hoe een project de DevHub documentatie-pipeline overneemt",
        category=DocumentCategory.METHODOLOGY,
        audience="developer",
        skip_vectorstore=True,
    )


# Registry van alle Sprint 33 builders
SPRINT_33_BUILDERS = [
    build_pattern_abc_adapter,
    build_methodology_shape_up,
    build_tutorial_sprint_intake,
    build_blueprint_boris,
]
