"""Stable, route-independent contracts for route-content agent steps."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

PROMPT_TEMPLATE_ROOT = Path(__file__).resolve().parents[1] / "prompts" / "route_pipeline"


@dataclass(frozen=True)
class PromptContract:
    step: str
    version: str
    output_format: str
    required_sections: tuple[str, ...] = ()
    required_json_keys: tuple[str, ...] = ()


CONTRACTS = {
    "brief_to_dossier": PromptContract(
        "brief_to_dossier", "1", "markdown",
        ("## Route Working Frame", "## Candidate Events", "## Risks And Open Claims"),
    ),
    "dossier_to_event_review": PromptContract(
        "dossier_to_event_review", "1", "json", required_json_keys=("_meta", "candidates"),
    ),
    "complete_draft": PromptContract(
        "complete_draft", "1", "json",
        required_json_keys=(
            "_meta", "route_concept", "candidates", "sequence", "events", "places",
            "connections", "phase_coverage", "findings", "warnings", "technical_errors",
        ),
    ),
    "event_review_to_concept": PromptContract(
        "event_review_to_concept", "1", "markdown",
        ("## Central Question", "## Route Thesis", "## Narrative Phases", "## Open Editorial Questions"),
    ),
    "concept_to_event_framing": PromptContract(
        "concept_to_event_framing", "1", "markdown", ("## Events",),
    ),
    "validation_to_revision_plan": PromptContract(
        "validation_to_revision_plan", "1", "markdown", ("## Blockers", "## Editorial Revisions"),
    ),
}


def prompt_contract(step: str) -> PromptContract:
    return CONTRACTS[step]


def load_prompt_template(step: str) -> str:
    return (PROMPT_TEMPLATE_ROOT / f"{step}.md").read_text(encoding="utf-8")


def contract_digest(step: str) -> str:
    contract = prompt_contract(step)
    content = {
        "step": contract.step,
        "version": contract.version,
        "output_format": contract.output_format,
        "required_sections": contract.required_sections,
        "required_json_keys": contract.required_json_keys,
        "template": load_prompt_template(step),
    }
    return hashlib.sha256(json.dumps(content, sort_keys=True).encode()).hexdigest()


def contract_markdown(step: str) -> str:
    contract = prompt_contract(step)
    lines = [
        "## Output Contract",
        "",
        f"- Contract version: `{contract.version}`",
        f"- Return exactly one `{contract.output_format}` artifact and no wrapper commentary.",
    ]
    if contract.required_sections:
        lines.append("- Required sections: " + ", ".join(f"`{item}`" for item in contract.required_sections) + ".")
    if contract.required_json_keys:
        lines.append("- Required top-level JSON keys: " + ", ".join(f"`{item}`" for item in contract.required_json_keys) + ".")
    return "\n".join(lines)


def validate_contract_output(step: str, value: str) -> list[str]:
    contract = prompt_contract(step)
    if not value.strip():
        return [f"{step} output must not be empty."]
    if contract.output_format == "markdown":
        return [
            f"{step} output is missing required section `{section}`."
            for section in contract.required_sections
            if section not in value
        ]
    try:
        payload: Any = json.loads(value)
    except json.JSONDecodeError as exc:
        return [f"{step} output must be valid JSON: {exc.msg}."]
    if not isinstance(payload, dict):
        return [f"{step} output must be a JSON object."]
    return [
        f"{step} output is missing required top-level key `{key}`."
        for key in contract.required_json_keys
        if key not in payload
    ]
