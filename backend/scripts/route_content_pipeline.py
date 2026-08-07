import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.route_review import ROUTE_REVIEW_FILENAME, RouteReviewRepository
from app.schemas import Connection, Event, Place, Route

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONTENT_ROOT = REPO_ROOT / "docs" / "content" / "routes"
DEFAULT_SEED_DIR = REPO_ROOT / "data" / "seed"
SCRIPT_NAME = "route_content_pipeline.py"
PIPELINE_FILENAME = "pipeline.json"
PIPELINE_STEPS = (
    "event_list",
    "accepted_events",
    "route_concept",
    "event_framing",
    "seed_preview",
    "validation",
)
ACCEPTED_EVENT_DECISIONS = {"keep", "merge"}
CANDIDATE_DECISIONS = {"keep", "maybe", "merge", "reject"}
REVIEW_STATES = {"pending", "approved", "rejected"}
CLUSTER_RECOMMENDED_ACTIONS = {"keep_separate", "merge", "use_as_context"}
QUALITY_GATE_FIELDS = (
    "route_fit_confirmed",
    "place_and_year_specificity_confirmed",
    "source_risks_visible",
    "seed_draft_ready",
)
AGENT_STEPS = (
    "brief_to_dossier",
    "dossier_to_event_review",
    "complete_draft",
    "event_review_to_concept",
    "concept_to_event_framing",
    "validation_to_revision_plan",
)


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        if args.command == "init":
            route_dir = route_dir_for(args.content_root, args.route_id)
            manifest = init_pipeline(
                route_dir=route_dir,
                route_id=args.route_id,
                active_dossier=args.dossier,
                renew=args.renew,
            )
            print(format_init_summary(route_dir, manifest))
        elif args.command == "run":
            result = run_pipeline(
                content_root=args.content_root,
                seed_dir=args.seed_dir,
                route_id=args.route_id,
                step=args.step,
                renew=args.renew,
                variant=args.variant,
            )
            print(format_run_summary(result))
        elif args.command == "agent":
            result = run_agent_pipeline(
                content_root=args.content_root,
                seed_dir=args.seed_dir,
                route_id=args.route_id,
                step=args.step,
                renew=args.renew,
                dry_run=args.dry_run,
                codex_command=args.codex_command,
                model=args.model,
                variant=args.variant,
                revision_request=args.revision_request,
            )
            print(format_agent_summary(result))
        elif args.command == "status":
            route_dir = route_dir_for(args.content_root, args.route_id)
            manifest = load_or_create_manifest(route_dir, args.route_id)
            print(
                format_status(
                    route_dir,
                    manifest,
                    review_repository=RouteReviewRepository(args.content_root),
                )
            )
        elif args.command == "review":
            review_repository = RouteReviewRepository(args.content_root)
            if args.migrate_legacy:
                report = review_repository.migrate_legacy(args.route_id)
                print(format_review_migration_summary(report.model_dump()))
            else:
                result = review_repository.refresh(args.route_id)
                print(format_review_summary(result.model_dump()))
        elif args.command == "promote":
            if not args.to_seed:
                raise ValueError("promote currently requires --to-seed.")
            result = promote_to_seed(
                content_root=args.content_root,
                seed_dir=args.seed_dir,
                route_id=args.route_id,
                write=args.write,
                variant=args.variant,
            )
            print(result)
        else:
            parser.print_help()
            return 2
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Manage SoundAtlas route content from brief to seed-ready drafts.",
    )
    parser.add_argument(
        "--content-root",
        type=Path,
        default=DEFAULT_CONTENT_ROOT,
        help="Directory containing per-route content folders.",
    )
    parser.add_argument(
        "--seed-dir",
        type=Path,
        default=DEFAULT_SEED_DIR,
        help="Directory containing seed JSON files.",
    )
    subparsers = parser.add_subparsers(dest="command")

    init_parser = subparsers.add_parser("init", help="Create a route pipeline manifest.")
    init_parser.add_argument("--route-id", required=True)
    init_parser.add_argument("--dossier", help="Active dossier filename.")
    init_parser.add_argument(
        "--renew",
        action="store_true",
        help="Rewrite pipeline.json even when it already exists.",
    )

    run_parser = subparsers.add_parser("run", help="Run route pipeline steps.")
    run_parser.add_argument("--route-id", required=True)
    run_parser.add_argument("--step", choices=PIPELINE_STEPS)
    run_parser.add_argument(
        "--all",
        action="store_true",
        help="Run all steps. This is the default when --step is omitted.",
    )
    run_parser.add_argument(
        "--missing",
        action="store_true",
        help="Create only missing outputs. This is the default mode.",
    )
    run_parser.add_argument(
        "--renew",
        action="store_true",
        help="Regenerate selected outputs and save .bak copies of overwritten files.",
    )
    run_parser.add_argument(
        "--variant",
        help="Write/read named route-local variants, for example 'alternate-draft'.",
    )

    agent_parser = subparsers.add_parser(
        "agent",
        help="Generate prompts or invoke Codex CLI for editorial agent steps.",
    )
    agent_parser.add_argument("--route-id", required=True)
    agent_parser.add_argument("--step", choices=AGENT_STEPS)
    agent_parser.add_argument(
        "--all",
        action="store_true",
        help="Run all agent steps. This is the default when --step is omitted.",
    )
    agent_parser.add_argument(
        "--missing",
        action="store_true",
        help="Create only missing agent outputs. This is the default mode.",
    )
    agent_parser.add_argument(
        "--renew",
        action="store_true",
        help="Regenerate selected agent outputs and save .bak copies.",
    )
    agent_parser.add_argument(
        "--variant",
        help="Write/read named route-local variants, for example 'alternate-draft'.",
    )
    agent_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Write prompt and run metadata without invoking Codex CLI.",
    )
    agent_parser.add_argument(
        "--codex-command",
        default="codex",
        help="Codex CLI executable to invoke.",
    )
    agent_parser.add_argument(
        "--model",
        help="Optional Codex model name passed to codex exec.",
    )
    agent_parser.add_argument(
        "--revision-request",
        type=Path,
        help="Route-local JSON request for selective or full complete-draft regeneration.",
    )
    status_parser = subparsers.add_parser("status", help="Report route pipeline state.")
    status_parser.add_argument("--route-id", required=True)

    review_parser = subparsers.add_parser(
        "review",
        help="Create or refresh the private active route-review result.",
    )
    review_parser.add_argument("--route-id", required=True)
    review_parser.add_argument(
        "--migrate-legacy",
        action="store_true",
        help="Create the first route review from legacy event-list review_state values.",
    )

    promote_parser = subparsers.add_parser(
        "promote",
        help="Preview or write reviewed route drafts into seed JSON.",
    )
    promote_parser.add_argument("--route-id", required=True)
    promote_parser.add_argument("--to-seed", action="store_true")
    promote_parser.add_argument(
        "--write",
        action="store_true",
        help="Write seed files. Omit for dry-run preview.",
    )
    promote_parser.add_argument(
        "--variant",
        help="Preview or write seed data from named route-local variants.",
    )
    return parser


def route_dir_for(content_root: Path, route_id: str) -> Path:
    return content_root / route_id


def active_complete_draft_path(route_dir: Path, manifest: dict[str, Any]) -> Path:
    filename = manifest.get("agent_steps", {}).get("complete_draft", {}).get(
        "active_output", manifest["steps"]["complete_draft"]["json"]
    )
    return route_dir / filename


def init_pipeline(
    *,
    route_dir: Path,
    route_id: str,
    active_dossier: str | None,
    renew: bool = False,
) -> dict[str, Any]:
    route_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = route_dir / PIPELINE_FILENAME
    if manifest_path.exists() and not renew:
        manifest = read_json(manifest_path)
        return merge_manifest_defaults(route_dir, route_id, manifest)

    manifest = default_manifest(route_dir, route_id, active_dossier)
    write_json(manifest_path, manifest)
    return manifest


def load_or_create_manifest(route_dir: Path, route_id: str) -> dict[str, Any]:
    manifest_path = route_dir / PIPELINE_FILENAME
    if manifest_path.exists():
        manifest = read_json(manifest_path)
        merged = merge_manifest_defaults(route_dir, route_id, manifest)
        if merged != manifest:
            write_json(manifest_path, merged)
        return merged
    return init_pipeline(route_dir=route_dir, route_id=route_id, active_dossier=None)


def default_manifest(
    route_dir: Path,
    route_id: str,
    active_dossier: str | None,
) -> dict[str, Any]:
    dossier = active_dossier or choose_active_dossier(route_dir)
    return {
        "route_id": route_id,
        "active_dossier": dossier,
        "steps": {
            "event_list": {
                "input": dossier,
                "markdown": "event-list.md",
                "json": "event-list.json",
            },
            "accepted_events": {
                "input": "event-list.json",
                "json": "accepted-events.json",
                "markdown": "accepted-events.md",
            },
            "complete_draft": {
                "input": "candidate-outline.json",
                "json": "complete-draft.json",
                "markdown": "complete-draft.md",
            },
            "route_concept": {
                "input": "accepted-events.json",
                "markdown": "route-concept.md",
            },
            "event_framing": {
                "input": "accepted-events.json",
                "markdown": "event-framing.md",
                "events": "event-framing.json",
                "places": "place-framing.json",
                "connections": "connection-framing.json",
            },
            "seed_preview": {
                "input": "event-framing.json",
                "markdown": "seed-transfer-report.md",
            },
            "validation": {
                "markdown": "validation-report.md",
            },
        },
        "agent_steps": default_agent_steps(dossier),
    }


def default_agent_steps(active_dossier: str) -> dict[str, dict[str, Any]]:
    return {
        "brief_to_dossier": {
            "inputs": [
                "brief.md",
                "../../route-research-dossier-template.md",
                "../../route-editorial-quality-standards.md",
            ],
            "prompt": "brief_to_dossier-prompt.ai-draft.md",
            "output": "research-dossier.md",
            "run": "brief_to_dossier-run.ai-draft.json",
        },
        "dossier_to_event_review": {
            "inputs": [active_dossier],
            "prompt": "dossier_to_event_review-prompt.ai-draft.md",
            "output": "event-list.json",
            "outline": "candidate-outline.json",
            "run": "dossier_to_event_review-run.ai-draft.json",
        },
        "complete_draft": {
            "inputs": [
                "candidate-outline.json",
                active_dossier,
                "../../route-editorial-quality-standards.md",
            ],
            "prompt": "complete_draft-prompt.ai-draft.md",
            "output": "complete-draft-output.ai-draft.json",
            "active_output": "complete-draft.json",
            "run": "complete_draft-run.ai-draft.json",
        },
        "event_review_to_concept": {
            "inputs": ["event-list.json"],
            "prompt": "event_review_to_concept-prompt.ai-draft.md",
            "output": "route-concept.md",
            "run": "event_review_to_concept-run.ai-draft.json",
        },
        "concept_to_event_framing": {
            "inputs": ["route-concept.md", "event-list.json"],
            "prompt": "concept_to_event_framing-prompt.ai-draft.md",
            "output": "event-framing.md",
            "run": "concept_to_event_framing-run.ai-draft.json",
        },
        "validation_to_revision_plan": {
            "inputs": ["seed-transfer-report.md", "validation-report.md"],
            "prompt": "validation_to_revision_plan-prompt.ai-draft.md",
            "output": "revision-plan.md",
            "run": "validation_to_revision_plan-run.ai-draft.json",
        },
    }


def merge_manifest_defaults(
    route_dir: Path,
    route_id: str,
    manifest: dict[str, Any],
) -> dict[str, Any]:
    defaults = default_manifest(
        route_dir,
        route_id,
        manifest.get("active_dossier") if isinstance(manifest.get("active_dossier"), str) else None,
    )
    merged = {**defaults, **manifest}
    merged["steps"] = {
        step: {**defaults["steps"][step], **manifest.get("steps", {}).get(step, {})}
        for step in defaults["steps"]
    }
    merged["agent_steps"] = {
        step: {**defaults["agent_steps"][step], **manifest.get("agent_steps", {}).get(step, {})}
        for step in AGENT_STEPS
    }
    normalize_manifest_inputs(merged)
    return merged


def normalize_manifest_inputs(manifest: dict[str, Any]) -> None:
    # Existing manifests retain their accepted-events configuration as a
    # compatibility path. The active complete-draft step uses the candidate
    # outline and does not inherit the legacy gate.
    if "complete_draft" not in manifest["steps"]:
        manifest["steps"]["complete_draft"] = {
            "input": "candidate-outline.json",
            "json": "complete-draft.json",
            "markdown": "complete-draft.md",
        }
    manifest["agent_steps"]["complete_draft"]["inputs"] = [
        manifest["agent_steps"]["dossier_to_event_review"].get(
            "outline", "candidate-outline.json"
        ),
        manifest["active_dossier"],
        "../../route-editorial-quality-standards.md",
    ]
    manifest["steps"]["complete_draft"]["input"] = manifest["agent_steps"][
        "complete_draft"
    ]["inputs"][0]
    manifest["agent_steps"]["event_review_to_concept"]["inputs"] = [
        manifest["steps"]["event_list"]["json"]
    ]
    manifest["agent_steps"]["concept_to_event_framing"]["inputs"] = [
        manifest["steps"]["route_concept"]["markdown"],
        manifest["steps"]["event_list"]["json"],
    ]


def choose_active_dossier(route_dir: Path) -> str:
    preferred = route_dir / "research-dossier.md"
    if preferred.exists():
        return preferred.name
    dossiers = sorted(route_dir.glob("research-dossier*.md"))
    if dossiers:
        return dossiers[0].name
    return "research-dossier.md"


def manifest_for_variant(
    *,
    route_dir: Path,
    manifest: dict[str, Any],
    variant: str | None = None,
) -> dict[str, Any]:
    if not variant:
        return manifest
    validate_variant_name(variant)
    variant_manifest = json.loads(json.dumps(manifest))
    active_dossier = variant_manifest["active_dossier"]
    variant_dossier = variant_filename(active_dossier, variant)
    variant_manifest["active_dossier"] = variant_dossier
    variant_manifest["steps"]["event_list"]["input"] = variant_dossier
    variant_manifest["steps"]["event_list"]["markdown"] = variant_filename("event-list.md", variant)
    variant_manifest["steps"]["event_list"]["json"] = variant_filename("event-list.json", variant)
    variant_manifest["steps"]["complete_draft"]["input"] = variant_filename(
        "candidate-outline.json", variant
    )
    variant_manifest["steps"]["complete_draft"]["json"] = variant_filename(
        "complete-draft.json", variant
    )
    variant_manifest["steps"]["complete_draft"]["markdown"] = variant_filename(
        "complete-draft.md", variant
    )
    variant_manifest["steps"]["accepted_events"]["input"] = variant_manifest["steps"]["event_list"][
        "json"
    ]
    variant_manifest["steps"]["accepted_events"]["json"] = variant_filename(
        "accepted-events.json", variant
    )
    variant_manifest["steps"]["accepted_events"]["markdown"] = variant_filename(
        "accepted-events.md", variant
    )
    variant_manifest["steps"]["route_concept"]["input"] = variant_manifest["steps"][
        "accepted_events"
    ]["json"]
    variant_manifest["steps"]["route_concept"]["markdown"] = variant_filename(
        "route-concept.md", variant
    )
    variant_manifest["steps"]["event_framing"]["input"] = variant_manifest["steps"][
        "accepted_events"
    ]["json"]
    variant_manifest["steps"]["event_framing"]["markdown"] = variant_filename(
        "event-framing.md", variant
    )
    variant_manifest["steps"]["event_framing"]["events"] = variant_filename(
        "event-framing.json", variant
    )
    variant_manifest["steps"]["event_framing"]["places"] = variant_filename(
        "place-framing.json", variant
    )
    variant_manifest["steps"]["event_framing"]["connections"] = variant_filename(
        "connection-framing.json", variant
    )
    variant_manifest["steps"]["seed_preview"]["input"] = variant_manifest["steps"]["event_framing"][
        "events"
    ]
    variant_manifest["steps"]["seed_preview"]["markdown"] = variant_filename(
        "seed-transfer-report.md", variant
    )
    variant_manifest["steps"]["validation"]["markdown"] = variant_filename(
        "validation-report.md", variant
    )
    variant_manifest["agent_steps"]["brief_to_dossier"]["output"] = variant_dossier
    variant_manifest["agent_steps"]["dossier_to_event_review"]["inputs"] = [variant_dossier]
    variant_manifest["agent_steps"]["dossier_to_event_review"]["output"] = variant_manifest[
        "steps"
    ]["event_list"]["json"]
    variant_manifest["agent_steps"]["dossier_to_event_review"]["outline"] = variant_filename(
        "candidate-outline.json", variant
    )
    variant_manifest["agent_steps"]["complete_draft"]["inputs"] = [
        variant_filename("candidate-outline.json", variant),
        variant_dossier,
        "../../route-editorial-quality-standards.md",
    ]
    variant_manifest["agent_steps"]["complete_draft"]["output"] = variant_filename(
        "complete-draft-output.ai-draft.json", variant
    )
    variant_manifest["agent_steps"]["complete_draft"]["active_output"] = variant_manifest[
        "steps"
    ]["complete_draft"]["json"]
    variant_manifest["agent_steps"]["event_review_to_concept"]["inputs"] = [
        variant_manifest["steps"]["event_list"]["json"]
    ]
    variant_manifest["agent_steps"]["event_review_to_concept"]["output"] = variant_manifest[
        "steps"
    ]["route_concept"]["markdown"]
    variant_manifest["agent_steps"]["concept_to_event_framing"]["inputs"] = [
        variant_manifest["steps"]["route_concept"]["markdown"],
        variant_manifest["steps"]["event_list"]["json"],
    ]
    variant_manifest["agent_steps"]["concept_to_event_framing"]["output"] = variant_manifest[
        "steps"
    ]["event_framing"]["markdown"]
    variant_manifest["agent_steps"]["validation_to_revision_plan"]["inputs"] = [
        variant_manifest["steps"]["seed_preview"]["markdown"],
        variant_manifest["steps"]["validation"]["markdown"],
    ]
    variant_manifest["agent_steps"]["validation_to_revision_plan"]["output"] = variant_filename(
        "revision-plan.md", variant
    )
    return variant_manifest


def validate_variant_name(variant: str) -> None:
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", variant):
        raise ValueError("Variant names must use lowercase letters, numbers, and hyphens.")


def variant_filename(filename: str, variant: str) -> str:
    path = Path(filename)
    return f"{path.stem}.{variant}{path.suffix}"


def run_pipeline(
    *,
    content_root: Path,
    seed_dir: Path,
    route_id: str,
    step: str | None,
    renew: bool,
    variant: str | None = None,
) -> list[dict[str, Any]]:
    route_dir = route_dir_for(content_root, route_id)
    manifest = load_or_create_manifest(route_dir, route_id)
    manifest = manifest_for_variant(route_dir=route_dir, manifest=manifest, variant=variant)
    selected_steps = [step] if step else list(PIPELINE_STEPS)
    results = []
    for selected_step in selected_steps:
        results.append(
            run_step(
                route_dir=route_dir,
                seed_dir=seed_dir,
                manifest=manifest,
                step=selected_step,
                renew=renew,
            ),
        )
    if not variant:
        write_json(route_dir / PIPELINE_FILENAME, manifest)
    return results


def run_step(
    *,
    route_dir: Path,
    seed_dir: Path,
    manifest: dict[str, Any],
    step: str,
    renew: bool,
) -> dict[str, Any]:
    if step in {"route_concept", "event_framing"} and active_complete_draft_path(
        route_dir, manifest
    ).exists():
        return {
            "step": step,
            "status": "blocked",
            "outputs": [],
            "errors": [
                "Active complete draft is the content authority; use its generated views instead."
            ],
        }
    if step == "event_list":
        return generate_event_list(route_dir=route_dir, manifest=manifest, renew=renew)
    if step == "accepted_events":
        return generate_accepted_events(route_dir=route_dir, manifest=manifest, renew=renew)
    if step == "route_concept":
        return generate_route_concept(route_dir=route_dir, manifest=manifest, renew=renew)
    if step == "event_framing":
        return generate_event_framing(
            route_dir=route_dir,
            seed_dir=seed_dir,
            manifest=manifest,
            renew=renew,
        )
    if step == "seed_preview":
        return generate_seed_preview(
            route_dir=route_dir,
            seed_dir=seed_dir,
            manifest=manifest,
            renew=renew,
        )
    if step == "validation":
        return generate_validation_report(
            route_dir=route_dir,
            seed_dir=seed_dir,
            manifest=manifest,
            renew=renew,
        )
    raise ValueError(f"Unknown pipeline step '{step}'.")


def run_agent_pipeline(
    *,
    content_root: Path,
    seed_dir: Path,
    route_id: str,
    step: str | None,
    renew: bool,
    dry_run: bool,
    codex_command: str,
    model: str | None,
    variant: str | None = None,
    revision_request: Path | None = None,
) -> list[dict[str, Any]]:
    route_dir = route_dir_for(content_root, route_id)
    manifest = load_or_create_manifest(route_dir, route_id)
    manifest = manifest_for_variant(route_dir=route_dir, manifest=manifest, variant=variant)
    selected_steps = [step] if step else list(AGENT_STEPS)

    results = []
    for selected_step in selected_steps:
        results.append(
            run_agent_step(
                route_dir=route_dir,
                seed_dir=seed_dir,
                manifest=manifest,
                step=selected_step,
                renew=renew,
                dry_run=dry_run,
                codex_command=codex_command,
                model=model,
                revision_request=revision_request,
            )
        )
    if not variant:
        write_json(route_dir / PIPELINE_FILENAME, manifest)
    return results


def run_agent_step(
    *,
    route_dir: Path,
    seed_dir: Path,
    manifest: dict[str, Any],
    step: str,
    renew: bool,
    dry_run: bool,
    codex_command: str,
    model: str | None,
    revision_request: Path | None = None,
) -> dict[str, Any]:
    if (
        step in {"event_review_to_concept", "concept_to_event_framing"}
        and active_complete_draft_path(route_dir, manifest).exists()
        and not dry_run
    ):
        raise ValueError(
            "Active complete draft is the content authority; secondary agent steps cannot overwrite its views."
        )
    agent_step = manifest["agent_steps"][step]
    prompt_path = route_dir / agent_step["prompt"]
    output_path = route_dir / agent_step["output"]
    run_path = route_dir / agent_step["run"]
    expected_outputs = [prompt_path, run_path] if dry_run else [prompt_path, output_path, run_path]
    skipped = maybe_skip_outputs(expected_outputs, renew)
    if skipped:
        return {"step": step, "status": "skipped", "outputs": skipped}

    request = None
    if revision_request is not None:
        if step != "complete_draft":
            raise ValueError("Revision requests are supported only by complete_draft.")
        request = load_revision_request(
            route_dir=route_dir,
            request_path=revision_request,
            current_revision=RouteReviewRepository(route_dir.parent, seed_dir=seed_dir)
            .get(manifest["route_id"])
            .revision_id,
        )
    prompt = build_agent_prompt(
        route_dir=route_dir,
        manifest=manifest,
        step=step,
        revision_request=request,
    )
    write_text(prompt_path, prompt, renew=renew)
    metadata = build_agent_run_metadata(
        route_dir=route_dir,
        step=step,
        agent_step=agent_step,
        dry_run=dry_run,
        codex_command=codex_command,
        model=model,
    )
    if dry_run:
        metadata["status"] = "dry_run"
        write_json(run_path, metadata, renew=renew)
        return {"step": step, "status": "dry_run", "outputs": [prompt_path.name, run_path.name]}

    if output_path.exists() and renew:
        backup_file(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    command = build_codex_exec_command(
        codex_command=codex_command,
        model=model,
        output_path=output_path,
    )
    print(f"Running Codex CLI for {step}; writing {relative_repo_path(output_path)}...", flush=True)
    completed = subprocess.run(
        command,
        input=prompt,
        text=True,
        capture_output=True,
        cwd=REPO_ROOT,
        check=False,
    )
    metadata.update(
        {
            "status": "completed" if completed.returncode == 0 else "failed",
            "returncode": completed.returncode,
            "stdout": completed.stdout,
            "stderr": completed.stderr,
        },
    )
    if completed.returncode != 0:
        write_json(run_path, metadata, renew=renew)
        raise ValueError(
            "Codex CLI agent step failed:\n"
            + (completed.stderr.strip() or completed.stdout.strip() or "no output"),
        )
    if not output_path.exists():
        write_text(output_path, completed.stdout, renew=False)
    raw_output = output_path.read_text(encoding="utf-8")
    metadata["raw_output_sha256"] = sha256_text(raw_output)
    activation_output = output_path
    repair_outputs: list[str] = []
    if step == "complete_draft":
        try:
            json.loads(raw_output)
            metadata["repair"] = {"attempted": False}
        except json.JSONDecodeError:
            repaired = normalize_json_envelope(raw_output)
            if repaired is None:
                metadata.update(
                    {
                        "status": "failed",
                        "validation": "raw output is not a repairable JSON envelope",
                        "repair": {"attempted": True, "succeeded": False},
                    }
                )
                write_json(run_path, metadata, renew=renew)
                raise ValueError("Complete draft output is not a repairable JSON envelope.")
            activation_output = output_path.with_name(
                f"{output_path.stem}-repair{output_path.suffix}"
            )
            write_text(activation_output, repaired, renew=renew)
            repair_outputs.append(activation_output.name)
            metadata["repair"] = {
                "attempted": True,
                "succeeded": True,
                "operation": "unwrap_single_json_code_fence",
                "repaired_output_sha256": sha256_text(repaired),
            }
    try:
        extra_outputs = sync_agent_sidecar_outputs(
            route_dir=route_dir,
            seed_dir=seed_dir,
            manifest=manifest,
            step=step,
            output_path=activation_output,
            renew=renew,
            revision_request=request,
        )
    except Exception as exc:
        metadata.update({"status": "failed", "validation": str(exc)})
        write_json(run_path, metadata, renew=renew)
        raise
    metadata["validation"] = "passed"
    active_path = route_dir / agent_step.get("active_output", agent_step["output"])
    if active_path.exists():
        metadata["active_output_sha256"] = sha256_text(
            active_path.read_text(encoding="utf-8")
        )
    write_json(run_path, metadata, renew=renew)
    return {
        "step": step,
        "status": "written",
        "outputs": [
            prompt_path.name,
            output_path.name,
            *repair_outputs,
            run_path.name,
            *extra_outputs,
        ],
    }


def sync_agent_sidecar_outputs(
    *,
    route_dir: Path,
    seed_dir: Path,
    manifest: dict[str, Any],
    step: str,
    output_path: Path,
    renew: bool,
    revision_request: dict[str, Any] | None = None,
) -> list[str]:
    if step == "complete_draft":
        return activate_complete_draft(
            route_dir=route_dir,
            seed_dir=seed_dir,
            manifest=manifest,
            output_path=output_path,
            renew=renew,
            revision_request=revision_request,
        )
    if step != "dossier_to_event_review":
        return []
    event_list = read_json(output_path)
    markdown_path = route_dir / manifest["steps"]["event_list"]["markdown"]
    write_text(markdown_path, format_event_list_markdown(event_list), renew=renew)
    outline_path = route_dir / manifest["agent_steps"][step].get(
        "outline", "candidate-outline.json"
    )
    write_json(outline_path, event_list, renew=renew)
    return [markdown_path.name, outline_path.name]


def activate_complete_draft(
    *,
    route_dir: Path,
    seed_dir: Path,
    manifest: dict[str, Any],
    output_path: Path,
    renew: bool,
    revision_request: dict[str, Any] | None = None,
) -> list[str]:
    payload = read_json(output_path)
    source_outline = read_json(
        route_dir / manifest["agent_steps"]["complete_draft"]["inputs"][0]
    )
    errors = validate_complete_draft(
        payload=payload,
        route_id=manifest["route_id"],
        seed_dir=seed_dir,
        source_outline=manifest["agent_steps"]["complete_draft"]["inputs"][0],
        source_outline_payload=source_outline,
    )
    if revision_request is not None:
        errors.extend(
            validate_regeneration(
                route_dir=route_dir,
                manifest=manifest,
                payload=payload,
                request=revision_request,
            )
        )
    if errors:
        raise ValueError("Complete draft validation failed:\n" + "\n".join(errors))

    active_step = manifest["steps"]["complete_draft"]
    event_step = manifest["steps"]["event_framing"]
    candidates = order_complete_draft_candidates(payload)
    source = active_step["json"]
    event_list = {
        "_meta": {
            "route_id": manifest["route_id"],
            "target_output": manifest["steps"]["event_list"]["json"],
            "review_status": "draft",
            "source_basis": [payload["_meta"]["source_outline"], source],
            "generated_by": SCRIPT_NAME,
        },
        "candidates": candidates,
        "warnings": payload["warnings"],
    }
    event_framing = {
        "_meta": {
            "route_id": manifest["route_id"],
            "source": source,
            "generated_by": SCRIPT_NAME,
            "review_status": "draft",
        },
        "events": payload["events"],
    }
    place_framing = {
        "_meta": {
            "route_id": manifest["route_id"],
            "source": source,
            "generated_by": SCRIPT_NAME,
            "review_status": "draft",
        },
        "places": payload["places"],
    }
    connection_framing = {
        "_meta": {
            "route_id": manifest["route_id"],
            "source": source,
            "generated_by": SCRIPT_NAME,
            "review_status": "draft",
        },
        "connections": payload["connections"],
    }
    complete_draft = dict(payload)
    complete_draft["_meta"] = {
        **payload["_meta"],
        "generated_by": SCRIPT_NAME,
        "active_output": source,
        "review_status": "draft",
    }
    review_repository = RouteReviewRepository(route_dir.parent, seed_dir=seed_dir)
    review = review_repository.build_from_complete_draft(
        manifest["route_id"], complete_draft
    )
    files: dict[str, str] = {
        active_step["json"]: json.dumps(complete_draft, indent=2, ensure_ascii=False) + "\n",
        active_step["markdown"]: format_complete_draft_markdown(complete_draft),
        manifest["steps"]["event_list"]["json"]: json.dumps(
            event_list, indent=2, ensure_ascii=False
        )
        + "\n",
        manifest["steps"]["event_list"]["markdown"]: format_event_list_markdown(event_list),
        manifest["steps"]["route_concept"]["markdown"]: payload["route_concept"],
        event_step["markdown"]: format_event_framing_markdown(
            payload["events"], payload["places"], payload["connections"]
        ),
        event_step["events"]: json.dumps(event_framing, indent=2, ensure_ascii=False) + "\n",
        event_step["places"]: json.dumps(place_framing, indent=2, ensure_ascii=False) + "\n",
        event_step["connections"]: json.dumps(
            connection_framing, indent=2, ensure_ascii=False
        )
        + "\n",
        ROUTE_REVIEW_FILENAME: json.dumps(
            review.model_dump(), indent=2, ensure_ascii=False
        )
        + "\n",
    }
    replace_route_files(route_dir=route_dir, files=files, renew=renew)
    return [
        active_step["json"],
        active_step["markdown"],
        manifest["steps"]["event_list"]["json"],
        manifest["steps"]["event_list"]["markdown"],
        manifest["steps"]["route_concept"]["markdown"],
        event_step["markdown"],
        event_step["events"],
        event_step["places"],
        event_step["connections"],
        ROUTE_REVIEW_FILENAME,
        f"review:{review.revision_id}",
    ]


def validate_complete_draft(
    *,
    payload: dict[str, Any],
    route_id: str,
    seed_dir: Path,
    source_outline: str,
    source_outline_payload: dict[str, Any] | None = None,
) -> list[str]:
    errors: list[str] = []
    metadata = payload.get("_meta")
    if not isinstance(metadata, dict):
        errors.append("Complete draft is missing `_meta`.")
        metadata = {}
    if metadata.get("route_id") != route_id:
        errors.append(f"Complete draft route_id must be `{route_id}`.")
    if metadata.get("source_outline") != source_outline:
        errors.append(f"Complete draft source_outline must be `{source_outline}`.")
    if metadata.get("review_status") != "draft":
        errors.append("Complete draft `_meta.review_status` must be `draft`.")
    for field in (
        "route_concept",
        "candidates",
        "sequence",
        "events",
        "places",
        "connections",
        "phase_coverage",
        "findings",
        "warnings",
        "technical_errors",
    ):
        if field not in payload:
            errors.append(f"Complete draft is missing `{field}`.")
    if not isinstance(payload.get("route_concept"), str) or not payload.get("route_concept", "").strip():
        errors.append("Complete draft route_concept must be non-empty Markdown.")
    warnings = payload.get("warnings", [])
    technical_errors = payload.get("technical_errors", [])
    if not isinstance(warnings, list) or any(not isinstance(item, str) for item in warnings):
        errors.append("Complete draft warnings must be a list of strings.")
    if not isinstance(technical_errors, list) or any(not isinstance(item, str) for item in technical_errors):
        errors.append("Complete draft technical_errors must be a list of strings.")
    if technical_errors:
        errors.extend(f"Complete draft technical error: {item}" for item in technical_errors)

    candidates = payload.get("candidates", [])
    sequence = payload.get("sequence", [])
    events = payload.get("events", [])
    places = payload.get("places", [])
    connections = payload.get("connections", [])
    if not isinstance(candidates, list) or not candidates:
        errors.append("Complete draft candidates must be a non-empty list.")
        candidates = []
    if not isinstance(sequence, list):
        errors.append("Complete draft sequence must be a list.")
        sequence = []
    if not isinstance(events, list):
        errors.append("Complete draft events must be a list.")
        events = []
    if not isinstance(places, list):
        errors.append("Complete draft places must be a list.")
        places = []
    if not isinstance(connections, list):
        errors.append("Complete draft connections must be a list.")
        connections = []

    candidate_ids: list[str] = []
    active_candidate_ids: list[str] = []
    candidate_by_id: dict[str, dict[str, Any]] = {}
    for candidate in candidates:
        if not isinstance(candidate, dict):
            errors.append("Complete draft contains a non-object candidate.")
            continue
        candidate_id = candidate.get("candidate_id")
        if not isinstance(candidate_id, str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", candidate_id):
            errors.append(f"Complete draft candidate has invalid candidate_id `{candidate_id}`.")
            continue
        if candidate_id in candidate_ids:
            errors.append(f"Complete draft contains duplicate candidate `{candidate_id}`.")
        candidate_ids.append(candidate_id)
        candidate_by_id[candidate_id] = candidate
        if candidate.get("status") not in CANDIDATE_DECISIONS:
            errors.append(f"Complete draft candidate `{candidate_id}` has unsupported status.")
        if candidate.get("review_state") != "pending":
            errors.append(f"Complete draft candidate `{candidate_id}` must remain pending.")
        for field in ("years", "place", "working_title", "route_function"):
            if not isinstance(candidate.get(field), str) or not candidate[field].strip():
                errors.append(f"Complete draft candidate `{candidate_id}` is missing `{field}`.")
        composition = candidate.get("composition")
        if not isinstance(composition, dict):
            errors.append(f"Complete draft candidate `{candidate_id}` is missing composition.")
            continue
        outcome = composition.get("outcome")
        if outcome not in {"active", "omitted", "merged_into", "split_into", "added"}:
            errors.append(f"Complete draft candidate `{candidate_id}` has unsupported composition outcome.")
            continue
        if not isinstance(composition.get("reason"), str) or not composition["reason"].strip():
            errors.append(f"Complete draft candidate `{candidate_id}` composition has no reason.")
        related = composition.get("related_candidate_ids", [])
        if not isinstance(related, list) or any(not isinstance(item, str) or not item for item in related):
            errors.append(f"Complete draft candidate `{candidate_id}` has invalid composition relationships.")
        if outcome in {"merged_into", "split_into"} and not related:
            errors.append(f"Complete draft candidate `{candidate_id}` {outcome} has no target.")
        if outcome in {"omitted", "merged_into", "split_into"}:
            preview = candidate.get("preview")
            if not isinstance(preview, dict) or any(
                not isinstance(preview.get(field), str) or not preview[field].strip()
                for field in ("summary", "significance")
            ):
                errors.append(
                    f"Complete draft inactive candidate `{candidate_id}` has incomplete preview content."
                )
        if outcome in {"active", "added"}:
            active_candidate_ids.append(candidate_id)

    for candidate_id, candidate in candidate_by_id.items():
        composition = candidate.get("composition")
        if not isinstance(composition, dict):
            continue
        for related_id in composition.get("related_candidate_ids", []):
            if related_id == candidate_id or related_id not in candidate_by_id:
                errors.append(
                    f"Complete draft candidate `{candidate_id}` has unresolved composition target `{related_id}`."
                )
    if sequence != active_candidate_ids:
        errors.append("Complete draft sequence must contain each active or added candidate exactly once in route order.")

    outline_ids = _outline_candidate_ids(source_outline_payload)
    if source_outline_payload is not None:
        missing_outline = sorted(outline_ids - set(candidate_ids))
        if missing_outline:
            errors.append("Complete draft does not account for outline candidates: " + ", ".join(missing_outline))
        unexpected = sorted(set(candidate_ids) - outline_ids)
        for candidate_id in unexpected:
            composition = candidate_by_id[candidate_id].get("composition")
            if not isinstance(composition, dict) or composition.get("outcome") != "added":
                errors.append(f"Complete draft new candidate `{candidate_id}` must use added composition outcome.")

    phase_coverage = payload.get("phase_coverage", [])
    if not isinstance(phase_coverage, list) or not phase_coverage:
        errors.append("Complete draft phase_coverage must be a non-empty list.")
    else:
        for item in phase_coverage:
            if not isinstance(item, dict) or not isinstance(item.get("phase"), str) or not item["phase"].strip():
                errors.append("Complete draft phase coverage requires a phase.")
                continue
            candidate_refs = item.get("candidate_ids", [])
            if not isinstance(candidate_refs, list) or any(item not in candidate_by_id for item in candidate_refs):
                errors.append(f"Complete draft phase `{item['phase']}` has unresolved candidates.")
            if item.get("status") not in {"covered", "narrowed", "gap"}:
                errors.append(f"Complete draft phase `{item['phase']}` has invalid status.")

    findings = payload.get("findings", [])
    if not isinstance(findings, list):
        errors.append("Complete draft findings must be a list.")
    else:
        for finding in findings:
            if not isinstance(finding, dict) or finding.get("owner") not in {
                "candidate_composition",
                "active_event",
                "active_route",
                "source_media",
                "technical",
            } or not isinstance(finding.get("message"), str) or not finding["message"].strip():
                errors.append("Complete draft contains an invalid owned finding.")
                continue
            candidate_id = finding.get("candidate_id")
            if candidate_id is not None and candidate_id not in candidate_by_id:
                errors.append(f"Complete draft finding has unknown candidate `{candidate_id}`.")

    event_ids = [event.get("id") for event in events if isinstance(event, dict)]
    if len(event_ids) != len(events) or len(set(event_ids)) != len(event_ids):
        errors.append("Complete draft events must have unique IDs.")
    if set(event_ids) != set(active_candidate_ids):
        errors.append("Complete draft event IDs must match active or added candidate IDs.")

    seed = load_seed_payloads(seed_dir)
    new_places = drafted_places({"places": {"places": places}})
    merged = {
        "routes": seed["routes"],
        "places": upsert_records(seed["places"], "places", new_places),
        "events": upsert_records(seed["events"], "events", events),
        "connections": upsert_records(seed["connections"], "connections", connections),
    }
    errors.extend(validate_seed_payloads(merged))
    place_ids = {place.get("id") for place in merged["places"].get("places", [])}
    for place in places:
        if not isinstance(place, dict) or place.get("decision") not in {"reuse", "new"}:
            errors.append("Complete draft places must use reuse or new decisions.")
            continue
        if place.get("place_id") not in place_ids:
            errors.append(f"Complete draft place `{place.get('place_id')}` is unresolved.")
        if place.get("decision") == "new" and not isinstance(place.get("place"), dict):
            errors.append(f"Complete draft new place `{place.get('place_id')}` has no place record.")
    connection_ids = [item.get("id") for item in connections if isinstance(item, dict)]
    if len(connection_ids) != len(set(connection_ids)):
        errors.append("Complete draft connections must have unique IDs.")
    return errors


def _outline_candidate_ids(payload: dict[str, Any] | None) -> set[str]:
    if not isinstance(payload, dict):
        return set()
    candidates = payload.get("candidates")
    if not isinstance(candidates, list):
        return set()
    return {
        item["candidate_id"]
        for item in candidates
        if isinstance(item, dict) and isinstance(item.get("candidate_id"), str)
    }


def load_revision_request(
    *,
    route_dir: Path,
    request_path: Path,
    current_revision: str,
) -> dict[str, Any]:
    path = request_path if request_path.is_absolute() else route_dir / request_path
    if path.parent.resolve() != route_dir.resolve() or not path.exists():
        raise ValueError("Revision request must be an existing route-local JSON file.")
    request = read_json(path)
    if request.get("base_revision_id") != current_revision:
        raise ValueError("Revision request is stale; reload the current route review first.")
    if request.get("scope") not in {"selective", "full"}:
        raise ValueError("Revision request scope must be selective or full.")
    if not isinstance(request.get("correction"), str) or not request["correction"].strip():
        raise ValueError("Revision request needs a correction.")
    candidate_ids = request.get("candidate_ids")
    if not isinstance(candidate_ids, list) or not candidate_ids or any(
        not isinstance(item, str) or not item for item in candidate_ids
    ):
        raise ValueError("Revision request needs one or more candidate IDs.")
    kind = request.get("change_kind", "local")
    if kind not in {
        "local",
        "brief",
        "thesis",
        "dossier",
        "source_invalidation",
        "whole_route",
        "non_local",
    }:
        raise ValueError("Revision request has an unsupported change_kind.")
    if kind != "local" and request["scope"] != "full":
        raise ValueError("Broad revision requests must use full regeneration.")
    return request


def validate_regeneration(
    *,
    route_dir: Path,
    manifest: dict[str, Any],
    payload: dict[str, Any],
    request: dict[str, Any],
) -> list[str]:
    if request["scope"] == "full":
        return []
    errors: list[str] = []
    metadata = payload.get("_meta")
    regenerated = metadata.get("regenerated_candidate_ids") if isinstance(metadata, dict) else None
    if not isinstance(regenerated, list) or not regenerated or any(
        not isinstance(item, str) or not item for item in regenerated
    ):
        return ["Selective regeneration must identify regenerated_candidate_ids."]
    if not set(request["candidate_ids"]).issubset(set(regenerated)):
        errors.append("Selective regeneration must include every requested candidate ID.")
    active_path = route_dir / manifest["steps"]["complete_draft"]["json"]
    if not active_path.exists():
        return ["Selective regeneration requires an active complete draft."]
    prior = read_json(active_path)
    prior_events = {
        item.get("id"): item
        for item in prior.get("events", [])
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }
    next_events = {
        item.get("id"): item
        for item in payload.get("events", [])
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }
    for event_id, event in prior_events.items():
        if event_id in regenerated:
            continue
        if event_id not in next_events or _canonical_json(event) != _canonical_json(next_events[event_id]):
            errors.append(
                f"Selective regeneration changed unaffected event `{event_id}`."
            )
    return errors


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def replace_route_files(
    *,
    route_dir: Path,
    files: dict[str, str],
    renew: bool,
) -> None:
    """Replace one activated route revision or restore every prior target."""
    targets = [route_dir / filename for filename in files]
    previous = {
        target: target.read_bytes() if target.exists() else None
        for target in targets
    }
    replaced: list[Path] = []
    with tempfile.TemporaryDirectory(prefix=".complete-draft-", dir=route_dir) as stage_name:
        stage_dir = Path(stage_name)
        try:
            for filename, content in files.items():
                staged_path = stage_dir / filename
                staged_path.parent.mkdir(parents=True, exist_ok=True)
                staged_path.write_text(content, encoding="utf-8")
            for target in targets:
                if renew and target.exists():
                    backup_file(target)
                os.replace(stage_dir / target.relative_to(route_dir), target)
                replaced.append(target)
        except OSError as exc:
            for target in replaced:
                original = previous[target]
                if original is None:
                    target.unlink(missing_ok=True)
                else:
                    target.write_bytes(original)
            raise ValueError(
                f"Complete draft activation failed; previous revision was preserved: {exc}"
            ) from exc


def order_complete_draft_candidates(payload: dict[str, Any]) -> list[dict[str, Any]]:
    candidates_by_id = {
        candidate["candidate_id"]: candidate for candidate in payload["candidates"]
    }
    return [candidates_by_id[candidate_id] for candidate_id in payload["sequence"]]


def format_complete_draft_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Complete Route Draft",
        "",
        f"Source outline: `{payload['_meta']['source_outline']}`",
        "",
        "This complete draft is generated content for private editorial review. It is not approved or publication-ready.",
        "",
        "## Sequence",
        "",
    ]
    lines.extend(f"{index}. `{candidate_id}`" for index, candidate_id in enumerate(payload["sequence"], 1))
    lines.extend(["", "## Warnings", ""])
    lines.extend(f"- {warning}" for warning in payload.get("warnings", []))
    if not payload.get("warnings"):
        lines.append("- None")
    lines.extend(["", "## Technical Errors", ""])
    lines.extend(f"- {error}" for error in payload.get("technical_errors", []))
    if not payload.get("technical_errors"):
        lines.append("- None")
    lines.append("")
    return "\n".join(lines)


def build_agent_prompt(
    *,
    route_dir: Path,
    manifest: dict[str, Any],
    step: str,
    revision_request: dict[str, Any] | None = None,
) -> str:
    agent_step = manifest["agent_steps"][step]
    input_blocks = []
    for input_file in agent_step.get("inputs", []):
        input_path = route_dir / input_file
        if not input_path.exists():
            raise ValueError(f"Missing input for {step}: {input_path}")
        input_blocks.append(
            format_prompt_file_block(input_file, input_path.read_text(encoding="utf-8"))
        )

    revision_blocks: list[str] = []
    if revision_request is not None:
        active_output = manifest["agent_steps"]["complete_draft"].get(
            "active_output", "complete-draft.json"
        )
        revision_blocks = [
            "## Revision request",
            json.dumps(revision_request, indent=2, ensure_ascii=False),
            "",
            "## Current complete draft",
            (route_dir / active_output).read_text(encoding="utf-8"),
            "",
        ]
    return "\n".join(
        [
            f"# SoundAtlas Agent Step: {step}",
            "",
            "You are running inside the SoundAtlas route editorial workflow.",
            "Return only the requested artifact content. Do not edit files.",
            "Do not include wrapping commentary before or after the artifact.",
            "Keep all historical claims cautious and source-aware.",
            "Mark unresolved claims, weak source leads, and rights risks explicitly.",
            "Your job is to improve editorial quality, not merely reformat the input.",
            "Preserve useful detail, sharpen route logic, and mark unresolved review needs.",
            "",
            f"Route ID: `{manifest['route_id']}`",
            f"Target output: `{agent_step.get('active_output', agent_step['output'])}`",
            "",
            "## Task",
            "",
            agent_step_instructions(step),
            "",
            "## Inputs",
            "",
            "\n\n".join(input_blocks),
            "",
            *revision_blocks,
        ],
    )


def agent_step_instructions(step: str) -> str:
    instructions = {
        "brief_to_dossier": (
            "Create a route research dossier draft that follows the provided "
            "template and quality standards. Start from the route brief only; "
            "do not narrow the research direction beyond what the brief supports."
        ),
        "dossier_to_event_review": "\n".join(
            [
                "Improve the event selection quality in the active dossier.",
                "Use only the dossier input. Do not invent new events or close source risks.",
                "Separate strong route events from context-only or weak candidates.",
                "Every candidate kept for development must explain its role in the route thesis.",
                "Preserve candidate IDs, years, places, working titles, inclusion rationale, source leads, and risk notes.",
                "Return only an event-list JSON draft with `_meta` and `candidates`.",
                'Use `_meta.review_status: "draft"` and keep every candidate decision draft.',
                "Each candidate must include `candidate_id`, `status`, `review_state`, `years`, `place`, `working_title`, `route_function`, `decision_rationale`, `review_question`, `source_leads`, `risk_notes`, and `next_action`.",
                "Use only `keep`, `maybe`, `merge`, or `reject` as candidate statuses. Treat `status` as the agent-proposed decision, not human approval.",
                "Use only `pending`, `approved`, or `rejected` as `review_state`. New agent drafts should normally use `pending` until human review.",
                "For every `merge` candidate, include machine-readable `merge_target_id` and `merge_rationale`; do not hide merge targets only in prose.",
                "When candidates overlap, align, duplicate, or form a context cluster, include top-level `review_clusters` with `cluster_id`, `title`, `member_candidate_ids`, `recommended_anchor_id`, `recommended_action`, `rationale`, and `review_guidance`.",
                "Use only `keep_separate`, `merge`, or `use_as_context` as cluster `recommended_action`.",
                "Do not call candidates final seed events.",
            ],
        ),
        "complete_draft": "\n".join(
            [
                "Create one complete route draft from the candidate outline and active dossier.",
                "The candidate outline is agent planning input, not a frozen human-approved roster.",
                "You may add, omit, merge, split, or reorder candidates when the route argument and evidence support it.",
                "Return only JSON with `_meta`, `route_concept`, `candidates`, `sequence`, `events`, `places`, `connections`, `phase_coverage`, `findings`, `warnings`, and `technical_errors`.",
                "Set `_meta.review_status` to `draft`, `_meta.source_outline` to the candidate-outline input filename, and `_meta.route_id` to the route ID.",
                "Every candidate must include `candidate_id`, `status`, `review_state`, `years`, `place`, `working_title`, `route_function`, `decision_rationale`, `review_question`, `source_leads`, `risk_notes`, `next_action`, and `composition` with `outcome`, `reason`, and `related_candidate_ids`.",
                "Use `keep`, `maybe`, `merge`, or `reject` only for agent recommendations; every generated candidate must use `review_state: pending`.",
                "Account for every source-outline candidate exactly once. Use `active`, `omitted`, `merged_into`, `split_into`, or `added` composition outcomes. Only active and added candidates appear in `sequence` and have seed-shaped events; inactive candidates need `preview.summary` and `preview.significance` for review.",
                "Every event must be a complete current-schema framing draft with seed-shaped fields, source and media arrays, and at least one relevant item-level source URL. Its `id` must match an active or added candidate ID.",
                "Every place and connection must use the current route pipeline framing shape and reference the generated event IDs.",
                "Include phase coverage records with `phase`, `status` (`covered`, `narrowed`, or `gap`), and candidate IDs. Include owned findings with owner `candidate_composition`, `active_event`, `active_route`, `source_media`, or `technical`; do not put inactive-candidate findings in active-route findings.",
                "Acquire and compare relevant sources before drafting reader-facing prose. Never invent source support. Keep unresolved source, historical, place, media, and wording risks in owned findings; keep structural or reference failures in `technical_errors`.",
                "Do not approve events, publish seed data, or claim the route is publication-ready.",
            ],
        ),
        "event_review_to_concept": "\n".join(
            [
                "Improve the route argument quality from the generated event-list draft.",
                "Use the event-list input as the boundary and keep additions clearly marked as proposed additions requiring review.",
                "Return only a route concept Markdown draft.",
                "The concept must include story-serving headings, a central question, a route thesis, narrative phases, place logic, candidate sequence, source-risk notes, and open editorial questions.",
                "Turn event candidates into a coherent editorial argument, not a chronology or checklist.",
                "Make the route's development over time and across places legible.",
                "Mark weak transitions, missing source support, and claims that need cautious wording.",
                "Keep the concept draft status clear; do not claim the route is seed-ready.",
            ],
        ),
        "concept_to_event_framing": "\n".join(
            [
                "Improve event-level story quality from the route concept and generated event-list draft.",
                "Return only event framing Markdown; do not return seed JSON.",
                "Use story-serving event headings. Do not use `summary` or `significance` as editorial Markdown headers.",
                "For each event, include a product-facing event title, one-sentence what-happens prose for later seed `summary`, and one-sentence why-this-matters-here prose for later seed `significance`.",
                "Event titles should be concise and product-facing, usually under 90 characters.",
                "What-happens prose should focus on what happened.",
                "Why-this-matters-here prose should focus on why the event matters to this route.",
                "The combined what-happens and why-this-matters-here prose should usually stay under 70 words.",
                "Also include place decision, connection rationale, source needs, and wording risks for each event.",
                "Avoid `first`, `birthplace`, or sole-origin claims unless the source basis is explicit.",
                "Do not claim event framing or seed JSON is publication-ready.",
            ],
        ),
        "validation_to_revision_plan": "\n".join(
            [
                "Improve publication readiness by turning preview and validation findings into an editorial revision plan.",
                "Use only the seed preview and validation report inputs.",
                "Return only a Markdown revision plan.",
                "Prioritize blockers before polish.",
                "Group fixes by route, place, event, connection, source, and wording risk.",
                "Separate schema/reference problems from editorial quality problems.",
                "Call out missing source URLs, unresolved coordinates, weak event prose, unsupported claims, and connection logic gaps.",
                "Do not edit seed data.",
            ],
        ),
    }
    return instructions[step]


def format_prompt_file_block(label: str, content: str) -> str:
    return "\n".join([f"### `{label}`", "", "```md", content.rstrip(), "```"])


def build_agent_run_metadata(
    *,
    route_dir: Path,
    step: str,
    agent_step: dict[str, Any],
    dry_run: bool,
    codex_command: str,
    model: str | None,
) -> dict[str, Any]:
    return {
        "step": step,
        "provider": "codex_cli",
        "dry_run": dry_run,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "inputs": agent_step.get("inputs", []),
        "input_sha256": {
            item: sha256_text((route_dir / item).read_text(encoding="utf-8"))
            for item in agent_step.get("inputs", [])
            if (route_dir / item).exists()
        },
        "prompt": agent_step["prompt"],
        "output": agent_step["output"],
        "command": build_codex_exec_command(
            codex_command=codex_command,
            model=model,
            output_path=route_dir / agent_step["output"],
        ),
    }


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def normalize_json_envelope(value: str) -> str | None:
    """Perform the one allowed value-preserving repair for fenced JSON."""
    match = re.fullmatch(r"\s*```(?:json)?\s*\n(?P<body>\{.*\})\s*\n```\s*", value, re.DOTALL)
    return match.group("body") if match else None


def build_codex_exec_command(
    *,
    codex_command: str,
    model: str | None,
    output_path: Path,
) -> list[str]:
    command = [
        codex_command,
        "exec",
        "--cd",
        str(REPO_ROOT),
        "--sandbox",
        "read-only",
        "--output-last-message",
        str(output_path),
    ]
    if model:
        command.extend(["--model", model])
    command.append("-")
    return command


def generate_event_list(
    *,
    route_dir: Path,
    manifest: dict[str, Any],
    renew: bool,
) -> dict[str, Any]:
    step = manifest["steps"]["event_list"]
    dossier_path = route_dir / step["input"]
    if not dossier_path.exists():
        raise ValueError(f"Missing active dossier: {dossier_path}")

    markdown_path = route_dir / step["markdown"]
    json_path = route_dir / step["json"]
    skipped = maybe_skip_outputs([markdown_path, json_path], renew)
    if skipped:
        return {"step": "event_list", "status": "skipped", "outputs": skipped}

    candidates = extract_candidate_events(dossier_path.read_text(encoding="utf-8"))
    payload = {
        "_meta": {
            "route_id": manifest["route_id"],
            "source": step["input"],
            "generated_by": SCRIPT_NAME,
            "review_status": "draft",
        },
        "candidates": [
            {
                **candidate,
                "status": "maybe",
                "review_state": "pending",
                "decision_rationale": "",
                "review_question": "Approve this proposed candidate decision?",
                "next_action": "review candidate",
            }
            for candidate in candidates
        ],
    }
    write_text(markdown_path, format_event_list_markdown(payload), renew=renew)
    write_json(json_path, payload, renew=renew)
    return {
        "step": "event_list",
        "status": "written",
        "outputs": [markdown_path.name, json_path.name],
        "candidates": len(candidates),
    }


def generate_accepted_events(
    *,
    route_dir: Path,
    manifest: dict[str, Any],
    renew: bool,
) -> dict[str, Any]:
    step = manifest["steps"]["accepted_events"]
    event_list_path = route_dir / step["input"]
    json_path = route_dir / step["json"]
    markdown_path = route_dir / step["markdown"]
    if not event_list_path.exists():
        raise ValueError(f"Missing event list JSON: {event_list_path}")

    if json_path.exists() and not renew:
        payload = read_json(json_path)
        json_written = False
    else:
        event_list = read_json(event_list_path)
        event_list_errors = validate_event_list_decisions(event_list)
        if event_list_errors:
            return {
                "step": "accepted_events",
                "status": "blocked",
                "outputs": [],
                "errors": event_list_errors,
            }
        payload = build_accepted_events_payload(
            route_id=manifest["route_id"],
            source=event_list_path.name,
            event_list=event_list,
        )
        write_json(json_path, payload, renew=renew)
        json_written = True

    markdown_written = False
    if renew or not markdown_path.exists():
        write_text(markdown_path, format_accepted_events_markdown(payload), renew=renew)
        markdown_written = True

    outputs = []
    if json_written:
        outputs.append(json_path.name)
    if markdown_written:
        outputs.append(markdown_path.name)
    if not outputs:
        return {
            "step": "accepted_events",
            "status": "skipped",
            "outputs": [json_path.name, markdown_path.name],
        }
    return {
        "step": "accepted_events",
        "status": "written",
        "outputs": outputs,
        "accepted_events": len(payload.get("accepted_events", [])),
    }


def validate_event_list_decisions(event_list: dict[str, Any]) -> list[str]:
    errors = []
    candidates = event_list.get("candidates", [])
    candidate_ids = {
        candidate.get("candidate_id") for candidate in candidates if candidate.get("candidate_id")
    }
    for candidate in candidates:
        candidate_id = candidate.get("candidate_id", "<missing>")
        status = candidate.get("status")
        review_state = candidate.get("review_state")
        if status not in CANDIDATE_DECISIONS:
            errors.append(
                f"Candidate `{candidate_id}` has unsupported decision `{status}`; "
                "use keep, maybe, merge, or reject.",
            )
        if review_state not in REVIEW_STATES:
            errors.append(
                f"Candidate `{candidate_id}` has unsupported review_state `{review_state}`; "
                "use pending, approved, or rejected.",
            )
        if status in ACCEPTED_EVENT_DECISIONS and review_state != "approved":
            errors.append(
                f"Candidate `{candidate_id}` is `{status}` but review_state is not approved.",
            )
        if status == "merge" and not candidate.get("merge_target_id"):
            errors.append(f"Candidate `{candidate_id}` is merge but has no merge_target_id.")
        if status == "merge" and not candidate.get("merge_rationale"):
            errors.append(f"Candidate `{candidate_id}` is merge but has no merge_rationale.")
        merge_target_id = candidate.get("merge_target_id")
        if status == "merge" and merge_target_id:
            if merge_target_id == candidate_id:
                errors.append(
                    f"Candidate `{candidate_id}` merge_target_id must reference another candidate."
                )
            elif merge_target_id not in candidate_ids:
                errors.append(
                    f"Candidate `{candidate_id}` merge_target_id `{merge_target_id}` "
                    "does not reference another candidate.",
                )
    for cluster in event_list.get("review_clusters", []):
        cluster_id = cluster.get("cluster_id", "<missing>")
        recommended_action = cluster.get("recommended_action")
        if recommended_action not in CLUSTER_RECOMMENDED_ACTIONS:
            errors.append(
                f"Review cluster `{cluster_id}` has unsupported recommended_action `{recommended_action}`; "
                "use keep_separate, merge, or use_as_context.",
            )
        recommended_anchor_id = cluster.get("recommended_anchor_id")
        if recommended_anchor_id not in candidate_ids:
            errors.append(
                f"Review cluster `{cluster_id}` recommended_anchor_id `{recommended_anchor_id}` "
                "does not reference a candidate.",
            )
        for member_id in cluster.get("member_candidate_ids", []):
            if member_id not in candidate_ids:
                errors.append(
                    f"Review cluster `{cluster_id}` member_candidate_id `{member_id}` "
                    "does not reference a candidate.",
                )
    return errors


def build_accepted_events_payload(
    *,
    route_id: str,
    source: str,
    event_list: dict[str, Any],
) -> dict[str, Any]:
    accepted_events = []
    for candidate in event_list.get("candidates", []):
        decision = candidate.get("status")
        if decision not in ACCEPTED_EVENT_DECISIONS:
            continue
        accepted_events.append(
            {
                "event_id": candidate["candidate_id"],
                "decision": decision,
                "review_state": candidate.get("review_state"),
                "merge_target_id": candidate.get("merge_target_id")
                if decision == "merge"
                else None,
                "source_candidate_id": candidate["candidate_id"],
                "working_title": candidate.get("working_title", ""),
                "years": candidate.get("years", ""),
                "place": candidate.get("place", ""),
                "route_rationale": candidate.get("inclusion_rationale")
                or candidate.get("route_function", ""),
                "quality_check": {field: False for field in QUALITY_GATE_FIELDS},
                "source_leads": list_from_review_value(candidate.get("source_leads")),
                "media_image_leads": [],
                "risk_notes": list_from_review_value(candidate.get("risk_notes")),
            },
        )
    return {
        "_meta": {
            "route_id": route_id,
            "source": source,
            "generated_by": SCRIPT_NAME,
            "review_status": "draft",
            "handoff_status": "draft",
        },
        "accepted_events": accepted_events,
    }


def list_from_review_value(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value if str(item).strip()]
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    return []


def accepted_events_gate_errors(route_dir: Path, manifest: dict[str, Any]) -> list[str]:
    step = manifest["steps"]["accepted_events"]
    path = route_dir / step["json"]
    if not path.exists():
        return [f"Missing accepted-events gate file `{step['json']}`."]
    return validate_accepted_events_payload(read_json(path))


def validate_accepted_events_payload(payload: dict[str, Any]) -> list[str]:
    errors = []
    accepted_events = payload.get("accepted_events")
    if not isinstance(accepted_events, list) or not accepted_events:
        return ["Accepted-events gate has no accepted events."]

    event_ids = {
        event.get("event_id")
        for event in accepted_events
        if isinstance(event, dict) and isinstance(event.get("event_id"), str)
    }
    for event in accepted_events:
        if not isinstance(event, dict):
            errors.append("Accepted-events gate contains a non-object event entry.")
            continue
        event_id = event.get("event_id", "<missing>")
        decision = event.get("decision")
        if decision not in ACCEPTED_EVENT_DECISIONS:
            errors.append(f"Accepted event `{event_id}` has unsupported decision `{decision}`.")
        merge_target_id = event.get("merge_target_id")
        if decision == "merge":
            if not merge_target_id:
                errors.append(f"Accepted event `{event_id}` is merge but has no merge_target_id.")
            elif merge_target_id == event_id:
                errors.append(
                    f"Accepted event `{event_id}` merge_target_id must reference another accepted event."
                )
            elif merge_target_id not in event_ids:
                errors.append(
                    f"Accepted event `{event_id}` merge_target_id `{merge_target_id}` "
                    "does not reference another accepted event.",
                )
        if decision == "keep" and merge_target_id:
            errors.append(
                f"Accepted event `{event_id}` is keep but has merge_target_id `{merge_target_id}`."
            )

        for field in ("source_candidate_id", "working_title", "years", "place", "route_rationale"):
            if not event.get(field):
                errors.append(f"Accepted event `{event_id}` is missing `{field}`.")

        quality_check = event.get("quality_check")
        if not isinstance(quality_check, dict):
            errors.append(f"Accepted event `{event_id}` is missing `quality_check`.")
            continue
        for field in QUALITY_GATE_FIELDS:
            if quality_check.get(field) is not True:
                errors.append(
                    f"Accepted event `{event_id}` has unconfirmed quality flag `{field}`."
                )
    return errors


def generate_route_concept(
    *,
    route_dir: Path,
    manifest: dict[str, Any],
    renew: bool,
) -> dict[str, Any]:
    step = manifest["steps"]["route_concept"]
    accepted_events_path = route_dir / step["input"]
    output_path = route_dir / step["markdown"]
    gate_errors = accepted_events_gate_errors(route_dir, manifest)
    if gate_errors:
        return {"step": "route_concept", "status": "blocked", "outputs": [], "errors": gate_errors}
    skipped = maybe_skip_outputs([output_path], renew)
    if skipped:
        return {"step": "route_concept", "status": "skipped", "outputs": skipped}

    accepted_events = read_json(accepted_events_path)
    content = format_route_concept_markdown(manifest["route_id"], accepted_events)
    write_text(output_path, content, renew=renew)
    return {"step": "route_concept", "status": "written", "outputs": [output_path.name]}


def generate_event_framing(
    *,
    route_dir: Path,
    seed_dir: Path,
    manifest: dict[str, Any],
    renew: bool,
) -> dict[str, Any]:
    step = manifest["steps"]["event_framing"]
    accepted_events_path = route_dir / step["input"]
    dossier_path = route_dir / manifest["active_dossier"]
    outputs = [
        route_dir / step["markdown"],
        route_dir / step["events"],
        route_dir / step["places"],
        route_dir / step["connections"],
    ]
    gate_errors = accepted_events_gate_errors(route_dir, manifest)
    if gate_errors:
        return {"step": "event_framing", "status": "blocked", "outputs": [], "errors": gate_errors}
    if not dossier_path.exists():
        raise ValueError(f"Missing active dossier: {dossier_path}")
    skipped = maybe_skip_outputs(outputs, renew)
    if skipped:
        return {"step": "event_framing", "status": "skipped", "outputs": skipped}

    accepted_events = read_json(accepted_events_path)
    seed_places = load_seed_collection(seed_dir, "places")
    seed_place_index = build_place_index(seed_places)
    events, places = build_event_and_place_drafts(
        route_id=manifest["route_id"],
        accepted_events=accepted_events,
        seed_place_index=seed_place_index,
    )
    connections = build_connection_drafts(
        manifest["route_id"],
        dossier_path.read_text(encoding="utf-8"),
        {event["id"] for event in events},
    )
    events_payload = {
        "_meta": {
            "route_id": manifest["route_id"],
            "source": accepted_events_path.name,
            "generated_by": SCRIPT_NAME,
            "review_status": "draft",
        },
        "events": events,
    }
    places_payload = {
        "_meta": {
            "route_id": manifest["route_id"],
            "source": accepted_events_path.name,
            "generated_by": SCRIPT_NAME,
            "review_status": "draft",
        },
        "places": places,
    }
    connections_payload = {
        "_meta": {
            "route_id": manifest["route_id"],
            "source": manifest["active_dossier"],
            "generated_by": SCRIPT_NAME,
            "review_status": "draft",
        },
        "connections": connections,
    }
    write_text(outputs[0], format_event_framing_markdown(events, places, connections), renew=renew)
    write_json(outputs[1], events_payload, renew=renew)
    write_json(outputs[2], places_payload, renew=renew)
    write_json(outputs[3], connections_payload, renew=renew)
    return {
        "step": "event_framing",
        "status": "written",
        "outputs": [path.name for path in outputs],
    }


def generate_seed_preview(
    *,
    route_dir: Path,
    seed_dir: Path,
    manifest: dict[str, Any],
    renew: bool,
) -> dict[str, Any]:
    step = manifest["steps"]["seed_preview"]
    output_path = route_dir / step["markdown"]
    gate_errors = accepted_events_gate_errors(route_dir, manifest)
    if gate_errors:
        return {"step": "seed_preview", "status": "blocked", "outputs": [], "errors": gate_errors}
    skipped = maybe_skip_outputs([output_path], renew)
    if skipped:
        return {"step": "seed_preview", "status": "skipped", "outputs": skipped}

    report = build_seed_preview_report(route_dir=route_dir, seed_dir=seed_dir, manifest=manifest)
    write_text(output_path, report, renew=renew)
    return {"step": "seed_preview", "status": "written", "outputs": [output_path.name]}


def generate_validation_report(
    *,
    route_dir: Path,
    seed_dir: Path,
    manifest: dict[str, Any],
    renew: bool,
) -> dict[str, Any]:
    step = manifest["steps"]["validation"]
    output_path = route_dir / step["markdown"]
    skipped = maybe_skip_outputs([output_path], renew)
    if skipped:
        return {"step": "validation", "status": "skipped", "outputs": skipped}

    gate_errors = accepted_events_gate_errors(route_dir, manifest)
    errors = list(gate_errors)
    if not gate_errors:
        merged = build_merged_seed_payloads(
            route_dir=route_dir, seed_dir=seed_dir, manifest=manifest
        )
        errors.extend(validate_seed_payloads(merged))
    report = format_validation_report(errors)
    write_text(output_path, report, renew=renew)
    return {"step": "validation", "status": "written", "outputs": [output_path.name]}


def maybe_skip_outputs(paths: list[Path], renew: bool) -> list[str]:
    if renew:
        return []
    existing = [path.name for path in paths if path.exists()]
    if len(existing) == len(paths):
        return existing
    return []


def extract_candidate_events(markdown: str) -> list[dict[str, str]]:
    rows = parse_section_table(markdown, "Candidate Events")
    candidates = []
    for row in rows:
        candidate_id = clean_id(row.get("candidate id", ""))
        if not candidate_id:
            continue
        candidates.append(
            {
                "candidate_id": candidate_id,
                "years": clean_cell(row.get("years", "")),
                "place": clean_cell(row.get("place", "")),
                "working_title": clean_cell(row.get("working title", "")),
                "inclusion_rationale": clean_cell(row.get("inclusion rationale", "")),
                "source_leads": clean_cell(row.get("source leads", "")),
                "risk_notes": clean_cell(row.get("risk notes", "")),
            },
        )
    return candidates


def extract_candidate_connections(markdown: str) -> list[dict[str, str]]:
    rows = parse_section_table(markdown, "Candidate Connections")
    connections = []
    for row in rows:
        from_event = clean_id(row.get("from event", ""))
        to_event = clean_id(row.get("to event", ""))
        relationship_type = slugify(clean_cell(row.get("relationship type", "")))
        if not from_event or not to_event or not relationship_type:
            continue
        connections.append(
            {
                "from_event_id": from_event,
                "to_event_id": to_event,
                "type": relationship_type,
                "summary": clean_cell(row.get("narrative purpose", "")),
                "source_leads": clean_cell(row.get("source leads", "")),
                "risk_notes": clean_cell(row.get("risk notes", "")),
            },
        )
    return connections


def parse_section_table(markdown: str, section_title: str) -> list[dict[str, str]]:
    lines = markdown.splitlines()
    section_lines: list[str] = []
    in_section = False
    for line in lines:
        if line.strip() == f"## {section_title}":
            in_section = True
            continue
        if in_section and line.startswith("## "):
            break
        if in_section:
            section_lines.append(line)

    table_lines = [line for line in section_lines if line.strip().startswith("|")]
    if len(table_lines) < 2:
        return []
    headers = [normalize_header(cell) for cell in split_markdown_row(table_lines[0])]
    rows = []
    for line in table_lines[2:]:
        cells = split_markdown_row(line)
        if len(cells) != len(headers):
            continue
        rows.append(dict(zip(headers, cells, strict=True)))
    return rows


def split_markdown_row(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def normalize_header(value: str) -> str:
    return clean_cell(value).lower()


def clean_cell(value: str) -> str:
    value = value.strip()
    if value.startswith("`") and value.endswith("`"):
        value = value[1:-1]
    return value.strip()


def clean_id(value: str) -> str:
    return slugify(clean_cell(value))


def slugify(value: str) -> str:
    value = value.lower().replace("&", " and ")
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-")


def parse_year_range(value: str) -> tuple[int, int]:
    years = [int(year) for year in re.findall(r"(?<!\d)(1[6-9]\d{2}|20\d{2})(?!\d)", value)]
    if not years:
        decade_match = re.search(r"(1[6-9]\d0|20\d0)s", value)
        if decade_match:
            decade = int(decade_match.group(1))
            return decade, decade + 9
        return 0, 0
    return min(years), max(years)


def format_event_list_markdown(payload: dict[str, Any]) -> str:
    route_id = payload["_meta"]["route_id"]
    source = (
        payload["_meta"].get("source")
        or payload["_meta"].get("basis")
        or payload["_meta"].get("target_output", "")
    )
    candidates = payload.get("candidates", [])
    lines = [
        f"# {route_id} Event List",
        "",
        f"Source: `{source}`",
        "",
        "## How To Review",
        "",
        "This is a decision-first review artifact. `Decision` is the agent-proposed",
        "candidate status; `Review state` records human confirmation. Accepted-event",
        "handoff only includes `keep` and resolved `merge` candidates after their",
        "`review_state` is `approved`.",
        "",
        "## Decision Summary",
        "",
        "| Decision | Count | Pending | Approved | Rejected |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for decision in ["keep", "maybe", "merge", "reject"]:
        decision_candidates = [
            candidate for candidate in candidates if candidate.get("status") == decision
        ]
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{decision}`",
                    str(len(decision_candidates)),
                    str(count_by_review_state(decision_candidates, "pending")),
                    str(count_by_review_state(decision_candidates, "approved")),
                    str(count_by_review_state(decision_candidates, "rejected")),
                ],
            )
            + " |",
        )

    lines.extend(["", "## Overlap Clusters", ""])
    review_clusters = payload.get("review_clusters", [])
    if review_clusters:
        lines.extend(
            [
                "| Cluster | Recommended action | Anchor | Members | Rationale | Review guidance |",
                "| --- | --- | --- | --- | --- | --- |",
            ],
        )
        for cluster in review_clusters:
            lines.append(
                "| "
                + " | ".join(
                    [
                        f"`{cluster.get('cluster_id', '')}`",
                        stringify_markdown_cell(cluster.get("recommended_action", "")),
                        f"`{cluster.get('recommended_anchor_id', '')}`",
                        stringify_markdown_cell(
                            format_id_list(cluster.get("member_candidate_ids", []))
                        ),
                        stringify_markdown_cell(cluster.get("rationale", "")),
                        stringify_markdown_cell(cluster.get("review_guidance", "")),
                    ],
                )
                + " |",
            )
    else:
        lines.append("No overlap clusters recorded.")

    lines.extend(["", "## Merge Decisions", ""])
    merge_candidates = [candidate for candidate in candidates if candidate.get("status") == "merge"]
    if merge_candidates:
        lines.extend(
            [
                "| Candidate ID | Review state | Merge target | Merge rationale | Review question |",
                "| --- | --- | --- | --- | --- |",
            ],
        )
        for candidate in merge_candidates:
            lines.append(
                "| "
                + " | ".join(
                    [
                        f"`{candidate.get('candidate_id', '')}`",
                        stringify_markdown_cell(candidate.get("review_state", "")),
                        f"`{candidate.get('merge_target_id', '')}`",
                        stringify_markdown_cell(candidate.get("merge_rationale", "")),
                        stringify_markdown_cell(candidate.get("review_question", "")),
                    ],
                )
                + " |",
            )
    else:
        lines.append("No merge decisions recorded.")

    lines.extend(["", "## Maybe Items", ""])
    maybe_candidates = [candidate for candidate in candidates if candidate.get("status") == "maybe"]
    if maybe_candidates:
        lines.extend(
            [
                "| Candidate ID | Review state | Working title | Review question | Decision rationale |",
                "| --- | --- | --- | --- | --- |",
            ],
        )
        for candidate in maybe_candidates:
            lines.append(
                "| "
                + " | ".join(
                    [
                        f"`{candidate.get('candidate_id', '')}`",
                        stringify_markdown_cell(candidate.get("review_state", "")),
                        stringify_markdown_cell(candidate.get("working_title", "")),
                        stringify_markdown_cell(candidate.get("review_question", "")),
                        stringify_markdown_cell(candidate.get("decision_rationale", "")),
                    ],
                )
                + " |",
            )
    else:
        lines.append("No maybe items recorded.")

    lines.extend(
        [
            "",
            "## Candidate Appendix",
            "",
            "| Candidate ID | Decision | Review state | Years | Place | Working title | Route function | Decision rationale | Source leads | Risk notes | Next action |",
            "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
        ],
    )
    for candidate in candidates:
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{candidate.get('candidate_id', '')}`",
                    stringify_markdown_cell(candidate.get("status", "")),
                    stringify_markdown_cell(candidate.get("review_state", "")),
                    stringify_markdown_cell(candidate.get("years", "")),
                    stringify_markdown_cell(candidate.get("place", "")),
                    stringify_markdown_cell(candidate.get("working_title", "")),
                    stringify_markdown_cell(
                        candidate.get("inclusion_rationale", candidate.get("route_function", "")),
                    ),
                    stringify_markdown_cell(candidate.get("decision_rationale", "")),
                    stringify_markdown_cell(candidate.get("source_leads", "")),
                    stringify_markdown_cell(candidate.get("risk_notes", "")),
                    stringify_markdown_cell(candidate.get("next_action", "")),
                ],
            )
            + " |",
        )
    lines.append("")
    return "\n".join(lines)


def count_by_review_state(candidates: list[dict[str, Any]], review_state: str) -> int:
    return len(
        [candidate for candidate in candidates if candidate.get("review_state") == review_state],
    )


def format_id_list(value: Any) -> str:
    if isinstance(value, list):
        return "<br>".join(f"`{item}`" for item in value)
    return stringify_markdown_cell(value)


def stringify_markdown_cell(value: Any) -> str:
    if isinstance(value, list):
        return "<br>".join(str(item) for item in value)
    if value is None:
        return ""
    return str(value).replace("\n", "<br>")


def format_route_concept_markdown(route_id: str, event_list: dict[str, Any]) -> str:
    accepted_events = [
        event for event in event_list.get("accepted_events", []) if event.get("decision") == "keep"
    ]
    lines = [
        f"# {route_id} Route Concept Draft",
        "",
        "Source: `accepted-events.json`",
        "",
        "This scaffold turns accepted-event handoff entries into a route concept",
        "draft. Replace scaffold text with source-reviewed narrative before seed transfer.",
        "",
        "## Route Argument",
        "",
        "- Central question: TODO",
        "- Thesis: TODO",
        "",
        "## Candidate Sequence",
        "",
        "| Candidate ID | Years | Place | Working title | Route function |",
        "| --- | --- | --- | --- | --- |",
    ]
    for event in accepted_events:
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{event.get('event_id', '')}`",
                    str(event.get("years", "")),
                    str(event.get("place", "")),
                    str(event.get("working_title", "")),
                    str(event.get("route_rationale", "")),
                ],
            )
            + " |",
        )
    lines.extend(
        [
            "",
            "## Open Questions",
            "",
            "- Which places need exact coordinates or a justified regional strategy?",
            "- Which claims need source comparison before final wording?",
            "",
        ],
    )
    return "\n".join(lines)


def format_accepted_events_markdown(payload: dict[str, Any]) -> str:
    route_id = payload["_meta"]["route_id"]
    source = payload["_meta"]["source"]
    lines = [
        f"# Accepted Events: {route_id}",
        "",
        "Status: Draft accepted-event dossier for enrichment planning. Not seed-ready or publication-ready.",
        f"Route: `{route_id}`",
        f"Source candidate list: `{source}`",
        "",
        "## Review Boundary",
        "",
        "This file is generated from `accepted-events.json`. It includes only `keep` candidates",
        "and resolved `merge` outcomes. Source approval, media approval, and publication",
        "readiness remain human-reviewed.",
        "",
        "## Accepted Event Index",
        "",
        "| Event ID | Decision | Merge target | Working title | Years | Place | Seed draft ready? | Notes |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for event in payload.get("accepted_events", []):
        quality_check = event.get("quality_check", {})
        seed_ready = "yes" if quality_check.get("seed_draft_ready") is True else "no"
        notes = "; ".join(event.get("risk_notes", []))
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{event.get('event_id', '')}`",
                    f"`{event.get('decision', '')}`",
                    f"`{event.get('merge_target_id') or ''}`",
                    str(event.get("working_title", "")),
                    str(event.get("years", "")),
                    str(event.get("place", "")),
                    f"`{seed_ready}`",
                    notes,
                ],
            )
            + " |",
        )
    lines.extend(["", "## Event Dossiers", ""])
    for event in payload.get("accepted_events", []):
        lines.extend(
            [
                f"### `{event.get('event_id', '')}`: {event.get('working_title', '')}",
                "",
                f"Candidate decision: `{event.get('decision', '')}`",
                f"Merge target: `{event.get('merge_target_id') or ''}`",
                "",
                "#### Core Framing",
                "",
                f"- Working title: {event.get('working_title', '')}",
                f"- Year range: {event.get('years', '')}",
                f"- Place: {event.get('place', '')}",
                f"- Route rationale: {event.get('route_rationale', '')}",
                "",
                "#### Quality Gate",
                "",
            ],
        )
        quality_check = event.get("quality_check", {})
        for field in QUALITY_GATE_FIELDS:
            lines.append(f"- {field}: `{str(quality_check.get(field) is True).lower()}`")
        lines.extend(
            [
                "",
                "#### Source Leads",
                "",
            ],
        )
        source_leads = event.get("source_leads", [])
        if source_leads:
            lines.extend(f"- {lead}" for lead in source_leads)
        else:
            lines.append("- None recorded.")
        lines.extend(["", "#### Risk Notes", ""])
        risk_notes = event.get("risk_notes", [])
        if risk_notes:
            lines.extend(f"- {note}" for note in risk_notes)
        else:
            lines.append("- None recorded.")
        lines.append("")
    return "\n".join(lines)


def build_event_and_place_drafts(
    *,
    route_id: str,
    accepted_events: dict[str, Any],
    seed_place_index: dict[str, dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    events = []
    place_records_by_id: dict[str, dict[str, Any]] = {}
    for accepted_event in accepted_events.get("accepted_events", []):
        if accepted_event.get("decision") != "keep":
            continue
        place_text = str(accepted_event.get("place") or "review-place")
        place_decision = build_place_decision(place_text, seed_place_index)
        place_records_by_id[place_decision["place_id"]] = place_decision
        year_start, year_end = parse_year_range(str(accepted_event.get("years") or ""))
        events.append(
            {
                "id": accepted_event["event_id"],
                "route_id": route_id,
                "place_id": place_decision["place_id"],
                "title": accepted_event.get("working_title")
                or accepted_event["event_id"].replace("-", " ").title(),
                "year_start": year_start,
                "year_end": year_end,
                "summary": "Draft summary pending source-reviewed event framing.",
                "significance": accepted_event.get("route_rationale")
                or "Draft significance pending review.",
                "tags": [],
                "review_status": "draft",
                "source_urls": [],
                "media_links": [],
                "image_links": [],
            },
        )
    return events, list(place_records_by_id.values())


def build_place_decision(
    place_text: str,
    seed_place_index: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    place_id = slugify(place_text) or "review-place"
    existing = seed_place_index.get(place_id) or seed_place_index.get(slugify(place_text))
    if existing:
        return {
            "decision": "reuse",
            "source_place_text": place_text,
            "place_id": existing["id"],
        }
    return {
        "decision": "new",
        "source_place_text": place_text,
        "place_id": place_id,
        "place": {
            "id": place_id,
            "name": place_text,
            "borough": "review",
            "place_type": "review",
            "latitude": 0.0,
            "longitude": 0.0,
            "summary": "Draft place generated from route pipeline; review before seed promotion.",
            "review_status": "draft",
            "source_urls": [],
        },
    }


def build_place_index(seed_places: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    index = {}
    for place in seed_places:
        if isinstance(place.get("id"), str):
            index[place["id"]] = place
        if isinstance(place.get("name"), str):
            index[slugify(place["name"])] = place
    return index


def build_connection_drafts(
    route_id: str,
    dossier_markdown: str,
    selected_event_ids: set[str],
) -> list[dict[str, Any]]:
    connections = []
    for candidate in extract_candidate_connections(dossier_markdown):
        if candidate["from_event_id"] not in selected_event_ids:
            continue
        if candidate["to_event_id"] not in selected_event_ids:
            continue
        connection_id = slugify(
            f"{candidate['from_event_id']}-to-{candidate['to_event_id']}-{candidate['type']}",
        )
        connections.append(
            {
                "id": connection_id,
                "from_event_id": candidate["from_event_id"],
                "to_event_id": candidate["to_event_id"],
                "type": candidate["type"],
                "summary": candidate["summary"] or f"Draft {route_id} connection pending review.",
                "review_status": "draft",
            },
        )
    return connections


def format_event_framing_markdown(
    events: list[dict[str, Any]],
    places: list[dict[str, Any]],
    connections: list[dict[str, Any]],
) -> str:
    lines = [
        "# Event Framing Draft",
        "",
        "This is a review artifact generated from the event list. Edit the JSON",
        "drafts before seed promotion.",
        "",
        "## Events",
        "",
        "| Event ID | Year range | Place ID | Title |",
        "| --- | --- | --- | --- |",
    ]
    for event in events:
        lines.append(
            f"| `{event['id']}` | {event['year_start']}-{event['year_end']} | "
            f"`{event['place_id']}` | {event['title']} |",
        )
    lines.extend(
        ["", "## Places", "", "| Place ID | Decision | Source place |", "| --- | --- | --- |"]
    )
    for place in places:
        lines.append(
            f"| `{place['place_id']}` | {place['decision']} | {place['source_place_text']} |",
        )
    lines.extend(
        [
            "",
            "## Connections",
            "",
            "| Connection ID | From | To | Type |",
            "| --- | --- | --- | --- |",
        ],
    )
    for connection in connections:
        lines.append(
            f"| `{connection['id']}` | `{connection['from_event_id']}` | "
            f"`{connection['to_event_id']}` | {connection['type']} |",
        )
    lines.append("")
    return "\n".join(lines)


def build_seed_preview_report(
    *,
    route_dir: Path,
    seed_dir: Path,
    manifest: dict[str, Any],
) -> str:
    seed = load_seed_payloads(seed_dir)
    drafts = load_draft_payloads(route_dir, manifest)
    gate_errors = accepted_events_gate_errors(route_dir, manifest)
    if gate_errors:
        warnings = list(gate_errors)
        validation_errors = list(gate_errors)
    else:
        merged = build_merged_seed_payloads(
            route_dir=route_dir, seed_dir=seed_dir, manifest=manifest
        )
        warnings = preview_warnings(manifest["route_id"], seed, drafts, merged)
        validation_errors = validate_seed_payloads(merged)
    lines = [
        "# Seed Transfer Preview",
        "",
        f"Route: `{manifest['route_id']}`",
        "",
        "## Proposed Changes",
        "",
        f"- Routes: {count_new_records(seed['routes'], [], 'routes')}",
        f"- Places: {count_new_records(seed['places'], drafted_places(drafts), 'places')}",
        f"- Events: {count_new_records(seed['events'], drafts['events'].get('events', []), 'events')}",
        f"- Connections: {count_new_records(seed['connections'], drafts['connections'].get('connections', []), 'connections')}",
        "",
        "## Warnings",
        "",
    ]
    if warnings:
        lines.extend(f"- {warning}" for warning in warnings)
    else:
        lines.append("- None")
    lines.extend(["", "## Validation", ""])
    if validation_errors:
        lines.extend(f"- {error}" for error in validation_errors)
    else:
        lines.append("- Seed preview validates against current schemas and references.")
    lines.append("")
    return "\n".join(lines)


def preview_warnings(
    route_id: str,
    seed: dict[str, dict[str, Any]],
    drafts: dict[str, dict[str, Any]],
    merged: dict[str, dict[str, Any]],
) -> list[str]:
    warnings = []
    if not any(route.get("id") == route_id for route in seed["routes"].get("routes", [])):
        warnings.append(f"Route `{route_id}` does not exist in seed routes.")
    for event in drafts["events"].get("events", []):
        if not event.get("source_urls"):
            warnings.append(f"Event `{event.get('id')}` has no source URLs.")
        if event.get("year_start") == 0 or event.get("year_end") == 0:
            warnings.append(f"Event `{event.get('id')}` needs a reviewed year range.")
    for place in drafted_places(drafts):
        if place.get("latitude") == 0.0 and place.get("longitude") == 0.0:
            warnings.append(f"Place `{place.get('id')}` needs reviewed coordinates.")
        if place.get("place_type") == "review" or place.get("borough") == "review":
            warnings.append(f"Place `{place.get('id')}` needs reviewed place metadata.")
    warnings.extend(validate_seed_payloads(merged))
    return warnings


def count_new_records(
    seed_payload: dict[str, Any],
    draft_records: list[dict[str, Any]],
    collection_key: str,
) -> str:
    seed_ids = {
        item.get("id") for item in seed_payload.get(collection_key, []) if isinstance(item, dict)
    }
    new_count = sum(1 for item in draft_records if item.get("id") not in seed_ids)
    update_count = sum(1 for item in draft_records if item.get("id") in seed_ids)
    return f"{new_count} new, {update_count} update"


def promote_to_seed(
    *,
    content_root: Path,
    seed_dir: Path,
    route_id: str,
    write: bool,
    variant: str | None,
) -> str:
    route_dir = route_dir_for(content_root, route_id)
    manifest = load_or_create_manifest(route_dir, route_id)
    manifest = manifest_for_variant(route_dir=route_dir, manifest=manifest, variant=variant)
    report = build_seed_preview_report(route_dir=route_dir, seed_dir=seed_dir, manifest=manifest)
    if not write:
        return report

    gate_errors = accepted_events_gate_errors(route_dir, manifest)
    if gate_errors:
        raise ValueError(
            "Refusing to write before accepted-events gate passes:\n" + "\n".join(gate_errors)
        )

    merged = build_merged_seed_payloads(route_dir=route_dir, seed_dir=seed_dir, manifest=manifest)
    errors = validate_seed_payloads(merged)
    if errors:
        raise ValueError("Refusing to write invalid seed data:\n" + "\n".join(errors))

    write_json(seed_dir / "places.json", merged["places"])
    write_json(seed_dir / "events.json", merged["events"])
    write_json(seed_dir / "connections.json", merged["connections"])
    return report + "\nSeed files written.\n"


def build_merged_seed_payloads(
    *,
    route_dir: Path,
    seed_dir: Path,
    manifest: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    seed = load_seed_payloads(seed_dir)
    drafts = load_draft_payloads(route_dir, manifest)
    draft_events = normalize_event_records(drafts["events"].get("events", []))
    return {
        "routes": seed["routes"],
        "places": upsert_records(seed["places"], "places", drafted_places(drafts)),
        "events": upsert_records(seed["events"], "events", draft_events),
        "connections": upsert_records(
            seed["connections"],
            "connections",
            drafts["connections"].get("connections", []),
        ),
    }


def normalize_event_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    normalized = []
    for record in records:
        if not isinstance(record, dict):
            normalized.append(record)
            continue
        try:
            normalized.append(
                Event.model_validate(record).model_dump(mode="json", exclude_none=True)
            )
        except Exception:
            normalized.append(record)
    return normalized


def load_seed_payloads(seed_dir: Path) -> dict[str, dict[str, Any]]:
    return {
        "routes": read_json(seed_dir / "routes.json"),
        "places": read_json(seed_dir / "places.json"),
        "events": read_json(seed_dir / "events.json"),
        "connections": read_json(seed_dir / "connections.json"),
    }


def load_draft_payloads(route_dir: Path, manifest: dict[str, Any]) -> dict[str, dict[str, Any]]:
    framing_step = manifest["steps"]["event_framing"]
    return {
        "events": read_optional_json(route_dir / framing_step["events"], {"events": []}),
        "places": read_optional_json(route_dir / framing_step["places"], {"places": []}),
        "connections": read_optional_json(
            route_dir / framing_step["connections"], {"connections": []}
        ),
    }


def drafted_places(drafts: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    places = []
    for decision in drafts["places"].get("places", []):
        if decision.get("decision") == "new" and isinstance(decision.get("place"), dict):
            places.append(decision["place"])
    return places


def upsert_records(
    payload: dict[str, Any],
    collection_key: str,
    draft_records: list[dict[str, Any]],
) -> dict[str, Any]:
    next_payload = json.loads(json.dumps(payload))
    records = [
        record for record in next_payload.get(collection_key, []) if isinstance(record, dict)
    ]
    draft_by_id = {
        record["id"]: record
        for record in draft_records
        if isinstance(record, dict) and isinstance(record.get("id"), str)
    }
    next_records = []
    seen_ids = set()
    for record in records:
        record_id = record.get("id")
        if record_id in draft_by_id:
            next_records.append(draft_by_id[record_id])
            seen_ids.add(record_id)
        else:
            next_records.append(record)
    for record_id, draft in draft_by_id.items():
        if record_id not in seen_ids:
            next_records.append(draft)
    next_payload[collection_key] = next_records
    return next_payload


def validate_seed_payloads(payloads: dict[str, dict[str, Any]]) -> list[str]:
    errors = []
    routes = validate_collection(payloads["routes"], "routes", Route, errors)
    places = validate_collection(payloads["places"], "places", Place, errors)
    events = validate_collection(payloads["events"], "events", Event, errors)
    connections = validate_collection(payloads["connections"], "connections", Connection, errors)
    route_ids = {route.id for route in routes}
    place_ids = {place.id for place in places}
    event_ids = {event.id for event in events}
    for event in events:
        if event.route_id not in route_ids:
            errors.append(f"Event `{event.id}` references unknown route `{event.route_id}`.")
        for place_id in event.place_ids:
            if place_id not in place_ids:
                errors.append(f"Event `{event.id}` references unknown place `{place_id}`.")
        for relationship in event.place_relationships:
            for endpoint_name, place_id in (
                ("from_place_id", relationship.from_place_id),
                ("to_place_id", relationship.to_place_id),
            ):
                if place_id not in place_ids:
                    errors.append(
                        f"Event `{event.id}` relationship {endpoint_name} "
                        f"references unknown place `{place_id}`.",
                    )
                if place_id not in event.place_ids:
                    errors.append(
                        f"Event `{event.id}` relationship {endpoint_name} "
                        "must appear in event place_ids.",
                    )
    for connection in connections:
        if connection.from_event_id not in event_ids:
            errors.append(
                f"Connection `{connection.id}` references unknown source event "
                f"`{connection.from_event_id}`.",
            )
        if connection.to_event_id not in event_ids:
            errors.append(
                f"Connection `{connection.id}` references unknown target event "
                f"`{connection.to_event_id}`.",
            )
    return errors


def validate_collection(
    payload: dict[str, Any],
    collection_key: str,
    model: type[Route] | type[Place] | type[Event] | type[Connection],
    errors: list[str],
) -> list[Any]:
    valid = []
    for item in payload.get(collection_key, []):
        try:
            valid.append(model(**item))
        except Exception as exc:
            errors.append(
                f"{collection_key} `{item.get('id', '<missing>')}` failed schema validation: {exc}"
            )
    return valid


def format_validation_report(errors: list[str]) -> str:
    lines = ["# Route Pipeline Validation", ""]
    if errors:
        lines.append("Validation failed:")
        lines.extend(f"- {error}" for error in errors)
    else:
        lines.append("Validation passed.")
    lines.append("")
    return "\n".join(lines)


def format_init_summary(route_dir: Path, manifest: dict[str, Any]) -> str:
    return "\n".join(
        [
            "Route content pipeline initialized",
            f"Route: {manifest['route_id']}",
            f"Directory: {relative_repo_path(route_dir)}",
            f"Active dossier: {manifest['active_dossier']}",
        ],
    )


def format_run_summary(results: list[dict[str, Any]]) -> str:
    lines = ["Route content pipeline run"]
    for result in results:
        outputs = ", ".join(result.get("outputs", [])) or "no outputs"
        detail = ""
        if "candidates" in result:
            detail = f" ({result['candidates']} candidate event(s))"
        if "accepted_events" in result:
            detail = f" ({result['accepted_events']} accepted event(s))"
        lines.append(f"- {result['step']}: {result['status']} {outputs}{detail}")
        for error in result.get("errors", []):
            lines.append(f"  - {error}")
    return "\n".join(lines)


def format_agent_summary(results: list[dict[str, Any]]) -> str:
    lines = ["Route content agent run"]
    for result in results:
        outputs = ", ".join(result.get("outputs", [])) or "no outputs"
        lines.append(f"- {result['step']}: {result['status']} {outputs}")
        for error in result.get("errors", []):
            lines.append(f"  - {error}")
        if result.get("next"):
            lines.append(f"  next: {result['next']}")
    return "\n".join(lines)


def format_status(
    route_dir: Path,
    manifest: dict[str, Any],
    review_repository: RouteReviewRepository | None = None,
) -> str:
    lines = [
        "Route content pipeline status",
        f"Route: {manifest['route_id']}",
        f"Directory: {relative_repo_path(route_dir)}",
        f"Active dossier: {manifest['active_dossier']}",
        "",
        "Steps",
    ]
    for step_name, step in manifest["steps"].items():
        outputs = step_outputs(route_dir, step)
        output_status = ", ".join(
            f"{route_relative_path(route_dir, path)}:{'present' if path.exists() else 'missing'}"
            for path in outputs
        )
        input_name = step.get("input")
        input_detail = f" input={input_name}" if input_name else ""
        lines.append(f"- {step_name}:{input_detail} outputs={output_status or 'none'}")
    complete_step = manifest.get("agent_steps", {}).get("complete_draft", {})
    active_complete_output = complete_step.get("active_output", "complete-draft.json")
    lines.extend(["", "Active complete draft"])
    if (route_dir / active_complete_output).exists():
        lines.append(f"- present: {active_complete_output}")
        lines.append(
            "- accepted-events gate does not block the active complete-draft path"
        )
    else:
        lines.append(f"- missing: {active_complete_output}")
    gate_errors = accepted_events_gate_errors(route_dir, manifest)
    lines.extend(["", "Accepted-events gate (legacy compatibility)"])
    if gate_errors:
        lines.append("- blocked")
        for error in gate_errors:
            lines.append(f"  - {error}")
        if not (route_dir / active_complete_output).exists():
            stale_outputs = downstream_outputs_present(route_dir, manifest)
            if stale_outputs:
                lines.append("- stale downstream artifacts: " + ", ".join(stale_outputs))
    else:
        lines.append("- passed")
    lines.extend(["", "Private route review"])
    if review_repository is None:
        review_repository = RouteReviewRepository(route_dir.parent)
    try:
        review = review_repository.get(manifest["route_id"])
    except ValueError as exc:
        lines.append(f"- unavailable: {exc}")
    else:
        counts = {state: 0 for state in ("draft", "approved", "dont_use")}
        for proposal in review.proposals:
            counts[proposal.editorial_state] += 1
        included = sum(proposal.included for proposal in review.proposals)
        warnings = len(review.warnings) + sum(
            len(proposal.warnings) for proposal in review.proposals
        )
        errors = sum(len(proposal.technical_errors) for proposal in review.proposals)
        lines.extend(
            [
                f"- revision: {review.revision_id}",
                f"- generated proposals: {len(review.proposals)}",
                f"- states: draft={counts['draft']}, approved={counts['approved']}, "
                f"dont_use={counts['dont_use']}",
                f"- reviewed content: included={included}, "
                f"excluded={len(review.proposals) - included}",
                f"- dormant decisions: {len(review.dormant_proposals)}",
                f"- editorial warnings: {warnings}",
                f"- technical errors: {errors}",
                f"- technical readiness: {'ready' if review.technical_ready else 'blocked'}",
            ]
        )
    lines.extend(["", "Agent steps"])
    for step_name, step in manifest.get("agent_steps", {}).items():
        outputs = step_outputs(route_dir, step)
        output_status = ", ".join(
            f"{route_relative_path(route_dir, path)}:{'present' if path.exists() else 'missing'}"
            for path in outputs
        )
        inputs = ", ".join(step.get("inputs", [])) or "none"
        lines.append(f"- {step_name}: inputs={inputs} outputs={output_status or 'none'}")
    return "\n".join(lines)


def format_review_summary(result: dict[str, Any]) -> str:
    proposals = result["proposals"]
    included = sum(proposal["included"] for proposal in proposals)
    errors = sum(len(proposal["technical_errors"]) for proposal in proposals)
    warnings = len(result["warnings"]) + sum(
        len(proposal["warnings"]) for proposal in proposals
    )
    return "\n".join(
        [
            "Private route review refreshed",
            f"Route: {result['route_id']}",
            f"Revision: {result['revision_id']}",
            f"Generated proposals: {len(proposals)}",
            f"Reviewed content: {included} included, {len(proposals) - included} excluded",
            f"Dormant decisions: {len(result['dormant_proposals'])}",
            f"Editorial warnings: {warnings}",
            f"Technical errors: {errors}",
            f"Technical readiness: {'ready' if result['technical_ready'] else 'blocked'}",
        ]
    )


def format_review_migration_summary(report: dict[str, Any]) -> str:
    migrated = report["migrated"]
    return "\n".join(
        [
            "Legacy route-review states migrated",
            f"Route: {report['route_id']}",
            f"Revision: {report['revision_id']}",
            f"Proposals: {report['proposals']}",
            "Mapped states: "
            f"pending={migrated['pending']}, approved={migrated['approved']}, "
            f"rejected={migrated['rejected']}",
            "Agent recommendations and accepted-events membership were not migrated.",
        ]
    )


def downstream_outputs_present(route_dir: Path, manifest: dict[str, Any]) -> list[str]:
    outputs = []
    for step_name in ("route_concept", "event_framing", "seed_preview"):
        for path in step_outputs(route_dir, manifest["steps"][step_name]):
            if path.exists():
                outputs.append(route_relative_path(route_dir, path))
    return outputs


def step_outputs(route_dir: Path, step: dict[str, Any]) -> list[Path]:
    outputs = []
    for key in (
        "markdown",
        "json",
        "events",
        "places",
        "connections",
        "prompt",
        "output",
        "active_output",
        "run",
    ):
        if isinstance(step.get(key), str):
            outputs.append(route_dir / step[key])
    return outputs


def load_seed_collection(seed_dir: Path, collection_key: str) -> list[dict[str, Any]]:
    path = seed_dir / f"{collection_key}.json"
    if not path.exists():
        return []
    payload = read_json(path)
    return [item for item in payload.get(collection_key, []) if isinstance(item, dict)]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def read_optional_json(path: Path, default: dict[str, Any]) -> dict[str, Any]:
    if not path.exists():
        return default
    return read_json(path)


def write_json(path: Path, payload: dict[str, Any], renew: bool = False) -> None:
    if path.exists() and renew:
        backup_file(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_text(path: Path, content: str, renew: bool = False) -> None:
    if path.exists() and renew:
        backup_file(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def backup_file(path: Path) -> None:
    backup_path = path.with_name(path.name + ".bak")
    shutil.copy2(path, backup_path)


def relative_repo_path(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def route_relative_path(route_dir: Path, path: Path) -> str:
    try:
        return str(path.relative_to(route_dir))
    except ValueError:
        return path.name


if __name__ == "__main__":
    raise SystemExit(main())
