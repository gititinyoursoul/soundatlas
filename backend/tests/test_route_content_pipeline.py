import json
import stat
from pathlib import Path

from scripts import route_content_pipeline
from scripts.route_content_pipeline import main


ROUTE_ID = "birth-of-hip-hop"


def test_pipeline_missing_mode_creates_accepted_events_and_blocks_downstream(
    tmp_path: Path,
    capsys,
) -> None:
    content_root, seed_dir = write_pipeline_fixture(tmp_path)

    exit_code = main(
        [
            "--content-root",
            str(content_root),
            "--seed-dir",
            str(seed_dir),
            "run",
            "--route-id",
            ROUTE_ID,
            "--missing",
        ],
    )

    output = capsys.readouterr().out
    route_dir = content_root / ROUTE_ID
    assert exit_code == 0
    assert "event_list: written" in output
    assert "accepted_events: written" in output
    assert "route_concept: blocked" in output
    assert (route_dir / "pipeline.json").exists()
    assert (route_dir / "event-list.md").exists()
    assert (route_dir / "event-list.json").exists()
    assert (route_dir / "accepted-events.json").exists()
    assert (route_dir / "accepted-events.md").exists()
    assert not (route_dir / "route-concept.md").exists()
    assert not (route_dir / "event-framing.json").exists()
    assert not (route_dir / "place-framing.json").exists()
    assert not (route_dir / "connection-framing.json").exists()
    assert not (route_dir / "seed-transfer-report.md").exists()
    assert (route_dir / "validation-report.md").exists()

    event_list = json.loads((route_dir / "event-list.json").read_text(encoding="utf-8"))
    assert event_list["_meta"]["review_status"] == "draft"
    assert event_list["candidates"][0]["candidate_id"] == "kool-herc-sedgwick-party"
    assert event_list["candidates"][0]["status"] == "maybe"
    accepted_events = json.loads((route_dir / "accepted-events.json").read_text(encoding="utf-8"))
    assert accepted_events["accepted_events"] == []


def test_pipeline_missing_mode_does_not_overwrite_existing_artifacts(
    tmp_path: Path,
) -> None:
    content_root, seed_dir = write_pipeline_fixture(tmp_path)
    assert main(["--content-root", str(content_root), "--seed-dir", str(seed_dir), "run", "--route-id", ROUTE_ID]) == 0
    event_list_path = content_root / ROUTE_ID / "event-list.md"
    event_list_path.write_text("manual review\n", encoding="utf-8")

    assert main(["--content-root", str(content_root), "--seed-dir", str(seed_dir), "run", "--route-id", ROUTE_ID, "--missing"]) == 0

    assert event_list_path.read_text(encoding="utf-8") == "manual review\n"


def test_pipeline_renew_regenerates_artifacts_and_writes_backup(
    tmp_path: Path,
) -> None:
    content_root, seed_dir = write_pipeline_fixture(tmp_path)
    route_dir = content_root / ROUTE_ID
    assert main(["--content-root", str(content_root), "--seed-dir", str(seed_dir), "run", "--route-id", ROUTE_ID]) == 0
    event_list_path = route_dir / "event-list.md"
    event_list_path.write_text("manual review\n", encoding="utf-8")

    assert main(
        [
            "--content-root",
            str(content_root),
            "--seed-dir",
            str(seed_dir),
            "run",
            "--route-id",
            ROUTE_ID,
            "--step",
            "event_list",
            "--renew",
        ],
    ) == 0

    assert (route_dir / "event-list.md.bak").read_text(encoding="utf-8") == "manual review\n"
    assert "kool-herc-sedgwick-party" in event_list_path.read_text(encoding="utf-8")


def test_promote_dry_run_previews_seed_changes_without_writing(
    tmp_path: Path,
    capsys,
) -> None:
    content_root, seed_dir = write_pipeline_fixture(tmp_path)
    prepare_reviewed_accepted_events(content_root, seed_dir)

    exit_code = main(
        [
            "--content-root",
            str(content_root),
            "--seed-dir",
            str(seed_dir),
            "promote",
            "--route-id",
            ROUTE_ID,
            "--to-seed",
        ],
    )

    output = capsys.readouterr().out
    events_payload = json.loads((seed_dir / "events.json").read_text(encoding="utf-8"))
    assert exit_code == 0
    assert "# Seed Transfer Preview" in output
    assert "Events: 1 new, 0 update" in output
    assert events_payload["events"] == []


def test_promote_write_adds_draft_events_to_seed(
    tmp_path: Path,
) -> None:
    content_root, seed_dir = write_pipeline_fixture(tmp_path)
    prepare_reviewed_accepted_events(content_root, seed_dir)

    exit_code = main(
        [
            "--content-root",
            str(content_root),
            "--seed-dir",
            str(seed_dir),
            "promote",
            "--route-id",
            ROUTE_ID,
            "--to-seed",
            "--write",
        ],
    )

    events_payload = json.loads((seed_dir / "events.json").read_text(encoding="utf-8"))
    assert exit_code == 0
    assert events_payload["events"][0]["id"] == "kool-herc-sedgwick-party"
    assert events_payload["events"][0]["place_id"] == "1520-sedgwick-avenue"


def test_validation_report_flags_unknown_route_reference(tmp_path: Path) -> None:
    content_root, seed_dir = write_pipeline_fixture(tmp_path)
    route_dir = content_root / ROUTE_ID
    prepare_reviewed_accepted_events(content_root, seed_dir)
    event_payload = json.loads((route_dir / "event-framing.json").read_text(encoding="utf-8"))
    event_payload["events"][0]["route_id"] = "missing-route"
    (route_dir / "event-framing.json").write_text(json.dumps(event_payload, indent=2) + "\n", encoding="utf-8")

    result = route_content_pipeline.run_pipeline(
        content_root=content_root,
        seed_dir=seed_dir,
        route_id=ROUTE_ID,
        step="validation",
        renew=True,
    )

    report = (route_dir / "validation-report.md").read_text(encoding="utf-8")
    assert result[0]["status"] == "written"
    assert "references unknown route `missing-route`" in report


def test_agent_dry_run_writes_prompt_and_metadata_without_output(
    tmp_path: Path,
    capsys,
) -> None:
    content_root, seed_dir = write_pipeline_fixture(tmp_path)

    exit_code = main(
        [
            "--content-root",
            str(content_root),
            "--seed-dir",
            str(seed_dir),
            "agent",
            "--route-id",
            ROUTE_ID,
            "--step",
            "brief_to_dossier",
            "--dry-run",
        ],
    )

    output = capsys.readouterr().out
    route_dir = content_root / ROUTE_ID
    run_metadata = json.loads((route_dir / "brief_to_dossier-run.ai-draft.json").read_text(encoding="utf-8"))
    assert exit_code == 0
    assert "brief_to_dossier: dry_run" in output
    assert (route_dir / "brief_to_dossier-prompt.ai-draft.md").exists()
    assert not (route_dir / "brief_to_dossier-output.ai-draft.md").exists()
    assert run_metadata["provider"] == "codex_cli"
    assert run_metadata["output"] == "research-dossier.md"
    assert run_metadata["dry_run"] is True


def test_agent_renew_writes_prompt_backup(tmp_path: Path) -> None:
    content_root, seed_dir = write_pipeline_fixture(tmp_path)
    route_dir = content_root / ROUTE_ID
    assert main(
        [
            "--content-root",
            str(content_root),
            "--seed-dir",
            str(seed_dir),
            "agent",
            "--route-id",
            ROUTE_ID,
            "--step",
            "brief_to_dossier",
            "--dry-run",
        ],
    ) == 0
    prompt_path = route_dir / "brief_to_dossier-prompt.ai-draft.md"
    prompt_path.write_text("manual prompt\n", encoding="utf-8")

    assert main(
        [
            "--content-root",
            str(content_root),
            "--seed-dir",
            str(seed_dir),
            "agent",
            "--route-id",
            ROUTE_ID,
            "--step",
            "brief_to_dossier",
            "--dry-run",
            "--renew",
        ],
    ) == 0

    assert (prompt_path.with_name("brief_to_dossier-prompt.ai-draft.md.bak")).read_text(encoding="utf-8") == "manual prompt\n"
    assert "SoundAtlas Agent Step" in prompt_path.read_text(encoding="utf-8")


def test_agent_invokes_codex_cli_and_writes_direct_output(tmp_path: Path, capsys) -> None:
    content_root, seed_dir = write_pipeline_fixture(tmp_path)
    fake_codex = write_fake_codex(tmp_path)
    route_dir = content_root / ROUTE_ID

    assert main(
        [
            "--content-root",
            str(content_root),
            "--seed-dir",
            str(seed_dir),
            "agent",
            "--route-id",
            ROUTE_ID,
            "--step",
            "brief_to_dossier",
            "--codex-command",
            str(fake_codex),
            "--renew",
        ],
    ) == 0
    output = capsys.readouterr().out
    assert "Running Codex CLI for brief_to_dossier; writing" in output
    assert (route_dir / "research-dossier.md").read_text(encoding="utf-8") == "agent output\n"
    manifest = json.loads((route_dir / "pipeline.json").read_text(encoding="utf-8"))
    assert manifest["agent_steps"]["brief_to_dossier"]["output"] == "research-dossier.md"


def test_agent_variant_writes_named_output_without_changing_manifest(tmp_path: Path, capsys) -> None:
    content_root, seed_dir = write_pipeline_fixture(tmp_path)
    fake_codex = write_fake_codex(tmp_path)
    route_dir = content_root / ROUTE_ID
    manifest_path = route_dir / "pipeline.json"

    assert main(
        [
            "--content-root",
            str(content_root),
            "--seed-dir",
            str(seed_dir),
            "agent",
            "--route-id",
            ROUTE_ID,
            "--step",
            "brief_to_dossier",
            "--codex-command",
            str(fake_codex),
            "--variant",
            "mvp-edit",
        ],
    ) == 0

    output = capsys.readouterr().out
    assert "research-dossier.mvp-edit.md" in output
    assert (route_dir / "research-dossier.mvp-edit.md").read_text(encoding="utf-8") == "agent output\n"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["agent_steps"]["brief_to_dossier"]["output"] == "research-dossier.md"


def test_run_variant_writes_named_outputs_without_changing_manifest(tmp_path: Path) -> None:
    content_root, seed_dir = write_pipeline_fixture(tmp_path)
    route_dir = content_root / ROUTE_ID
    (route_dir / "research-dossier.mvp-edit.md").write_text(build_dossier(), encoding="utf-8")
    manifest_path = route_dir / "pipeline.json"

    assert main(
        [
            "--content-root",
            str(content_root),
            "--seed-dir",
            str(seed_dir),
            "run",
            "--route-id",
            ROUTE_ID,
            "--step",
            "event_list",
            "--variant",
            "mvp-edit",
        ],
    ) == 0

    assert (route_dir / "event-list.mvp-edit.md").exists()
    assert (route_dir / "event-list.mvp-edit.json").exists()
    assert not (route_dir / "event-list.json").exists()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["steps"]["event_list"]["json"] == "event-list.json"


def test_agent_steps_can_run_without_review_gate(tmp_path: Path) -> None:
    content_root, seed_dir = write_pipeline_fixture(tmp_path)
    fake_codex = write_fake_codex(tmp_path, output=build_agent_event_list_json())
    route_dir = content_root / ROUTE_ID

    assert main(
        [
            "--content-root",
            str(content_root),
            "--seed-dir",
            str(seed_dir),
            "agent",
            "--route-id",
            ROUTE_ID,
            "--step",
            "dossier_to_event_review",
            "--codex-command",
            str(fake_codex),
        ],
    ) == 0
    assert "agent-reviewed-event" in (route_dir / "event-list.json").read_text(encoding="utf-8")
    assert "agent-reviewed-event" in (route_dir / "event-list.md").read_text(encoding="utf-8")
    assert "Agent reviewed event" in (route_dir / "event-list.md").read_text(encoding="utf-8")


def test_agent_prompts_include_editorial_quality_contracts(tmp_path: Path) -> None:
    content_root, seed_dir = write_pipeline_fixture(tmp_path)
    route_dir = content_root / ROUTE_ID
    prepare_reviewed_accepted_events(content_root, seed_dir)

    for step in [
        "dossier_to_event_review",
        "event_review_to_concept",
        "concept_to_event_framing",
        "validation_to_revision_plan",
    ]:
        assert main(
            [
                "--content-root",
                str(content_root),
                "--seed-dir",
                str(seed_dir),
                "agent",
                "--route-id",
                ROUTE_ID,
                "--step",
                step,
                "--dry-run",
                "--renew",
            ],
        ) == 0

    dossier_prompt = (route_dir / "dossier_to_event_review-prompt.ai-draft.md").read_text(encoding="utf-8")
    concept_prompt = (route_dir / "event_review_to_concept-prompt.ai-draft.md").read_text(encoding="utf-8")
    framing_prompt = (route_dir / "concept_to_event_framing-prompt.ai-draft.md").read_text(encoding="utf-8")
    revision_prompt = (route_dir / "validation_to_revision_plan-prompt.ai-draft.md").read_text(encoding="utf-8")

    for prompt in [dossier_prompt, concept_prompt, framing_prompt, revision_prompt]:
        assert "improve editorial quality, not merely reformat the input" in prompt
        assert "mark unresolved review needs" in prompt

    assert "Separate strong route events from context-only or weak candidates" in dossier_prompt
    assert "`route_function`" in dossier_prompt
    assert "Do not call candidates final seed events" in dossier_prompt
    assert "Use only `keep`, `maybe`, `merge`, or `reject` as candidate statuses." in dossier_prompt

    assert "coherent editorial argument, not a chronology or checklist" in concept_prompt
    assert "story-serving headings" in concept_prompt
    assert "place logic" in concept_prompt

    assert "Do not use `summary` or `significance` as editorial Markdown headers" in framing_prompt
    assert "what-happens prose" in framing_prompt
    assert "why-this-matters-here prose" in framing_prompt
    assert "usually stay under 70 words" in framing_prompt
    assert "usually under 90 characters" in framing_prompt

    assert "publication readiness" in revision_prompt
    assert "Prioritize blockers before polish" in revision_prompt
    assert "schema/reference problems from editorial quality problems" in revision_prompt


def test_codex_exec_command_uses_supported_noninteractive_flags(tmp_path: Path) -> None:
    command = route_content_pipeline.build_codex_exec_command(
        codex_command="codex",
        model=None,
        output_path=tmp_path / "agent-output.md",
    )

    assert command[:2] == ["codex", "exec"]
    assert "--sandbox" in command
    assert "read-only" in command
    assert "--output-last-message" in command
    assert "--ask-for-approval" not in command
    assert "-a" not in command


def test_status_reports_agent_steps(tmp_path: Path, capsys) -> None:
    content_root, seed_dir = write_pipeline_fixture(tmp_path)

    exit_code = main(
        [
            "--content-root",
            str(content_root),
            "--seed-dir",
            str(seed_dir),
            "status",
            "--route-id",
            ROUTE_ID,
        ],
    )

    output = capsys.readouterr().out
    assert exit_code == 0
    assert "Agent steps" in output
    assert "brief_to_dossier" in output
    assert "research-dossier.md:present" in output


def test_accepted_events_step_generates_draft_from_keep_candidates(tmp_path: Path) -> None:
    content_root, seed_dir = write_pipeline_fixture(tmp_path)
    route_dir = content_root / ROUTE_ID
    write_event_list_decisions(content_root, seed_dir, route_dir, {"kool-herc-sedgwick-party": "keep"})

    assert main(
        [
            "--content-root",
            str(content_root),
            "--seed-dir",
            str(seed_dir),
            "run",
            "--route-id",
            ROUTE_ID,
            "--step",
            "accepted_events",
        ],
    ) == 0

    accepted_events = json.loads((route_dir / "accepted-events.json").read_text(encoding="utf-8"))
    assert accepted_events["accepted_events"][0]["event_id"] == "kool-herc-sedgwick-party"
    assert accepted_events["accepted_events"][0]["decision"] == "keep"
    assert accepted_events["accepted_events"][0]["quality_check"]["seed_draft_ready"] is False
    assert "Accepted Event Index" in (route_dir / "accepted-events.md").read_text(encoding="utf-8")


def test_downstream_steps_block_until_quality_flags_are_confirmed(tmp_path: Path) -> None:
    content_root, seed_dir = write_pipeline_fixture(tmp_path)
    route_dir = content_root / ROUTE_ID
    write_event_list_decisions(content_root, seed_dir, route_dir, {"kool-herc-sedgwick-party": "keep"})
    assert main(
        [
            "--content-root",
            str(content_root),
            "--seed-dir",
            str(seed_dir),
            "run",
            "--route-id",
            ROUTE_ID,
            "--step",
            "accepted_events",
        ],
    ) == 0

    result = route_content_pipeline.run_pipeline(
        content_root=content_root,
        seed_dir=seed_dir,
        route_id=ROUTE_ID,
        step="route_concept",
        renew=False,
    )

    assert result[0]["status"] == "blocked"
    assert "unconfirmed quality flag `seed_draft_ready`" in "\n".join(result[0]["errors"])


def test_downstream_steps_run_after_accepted_events_gate_passes(tmp_path: Path) -> None:
    content_root, seed_dir = write_pipeline_fixture(tmp_path)
    route_dir = content_root / ROUTE_ID
    prepare_reviewed_accepted_events(content_root, seed_dir)

    assert (route_dir / "route-concept.md").exists()
    assert (route_dir / "event-framing.json").exists()
    events_payload = json.loads((route_dir / "event-framing.json").read_text(encoding="utf-8"))
    assert events_payload["_meta"]["source"] == "accepted-events.json"
    assert events_payload["events"][0]["id"] == "kool-herc-sedgwick-party"


def test_unresolved_merge_candidate_blocks_accepted_events_generation(tmp_path: Path) -> None:
    content_root, seed_dir = write_pipeline_fixture(tmp_path)
    route_dir = content_root / ROUTE_ID
    write_event_list_decisions(content_root, seed_dir, route_dir, {"kool-herc-sedgwick-party": "merge"})

    result = route_content_pipeline.run_pipeline(
        content_root=content_root,
        seed_dir=seed_dir,
        route_id=ROUTE_ID,
        step="accepted_events",
        renew=False,
    )

    assert result[0]["status"] == "blocked"
    assert "has no merge_target_id" in "\n".join(result[0]["errors"])


def test_resolved_merge_requires_another_accepted_event_target(tmp_path: Path) -> None:
    payload = {
        "accepted_events": [
            {
                "event_id": "source-event",
                "decision": "merge",
                "merge_target_id": "target-event",
                "source_candidate_id": "source-event",
                "working_title": "Source event",
                "years": "1973",
                "place": "Bronx",
                "route_rationale": "Merge trail.",
                "quality_check": {field: True for field in route_content_pipeline.QUALITY_GATE_FIELDS},
            },
            {
                "event_id": "target-event",
                "decision": "keep",
                "merge_target_id": None,
                "source_candidate_id": "target-event",
                "working_title": "Target event",
                "years": "1973",
                "place": "Bronx",
                "route_rationale": "Accepted target.",
                "quality_check": {field: True for field in route_content_pipeline.QUALITY_GATE_FIELDS},
            },
        ],
    }

    assert route_content_pipeline.validate_accepted_events_payload(payload) == []

    payload["accepted_events"][0]["merge_target_id"] = "source-event"
    assert "must reference another accepted event" in "\n".join(
        route_content_pipeline.validate_accepted_events_payload(payload),
    )


def test_accepted_events_markdown_is_not_overwritten_without_renew(tmp_path: Path) -> None:
    content_root, seed_dir = write_pipeline_fixture(tmp_path)
    route_dir = content_root / ROUTE_ID
    write_event_list_decisions(content_root, seed_dir, route_dir, {"kool-herc-sedgwick-party": "keep"})
    assert main(
        [
            "--content-root",
            str(content_root),
            "--seed-dir",
            str(seed_dir),
            "run",
            "--route-id",
            ROUTE_ID,
            "--step",
            "accepted_events",
        ],
    ) == 0
    markdown_path = route_dir / "accepted-events.md"
    markdown_path.write_text("manual dossier notes\n", encoding="utf-8")

    assert main(
        [
            "--content-root",
            str(content_root),
            "--seed-dir",
            str(seed_dir),
            "run",
            "--route-id",
            ROUTE_ID,
            "--step",
            "accepted_events",
            "--missing",
        ],
    ) == 0

    assert markdown_path.read_text(encoding="utf-8") == "manual dossier notes\n"


def test_status_marks_existing_downstream_artifacts_stale_when_gate_is_missing(
    tmp_path: Path,
    capsys,
) -> None:
    content_root, seed_dir = write_pipeline_fixture(tmp_path)
    route_dir = content_root / ROUTE_ID
    (route_dir / "route-concept.md").write_text("old concept\n", encoding="utf-8")

    assert main(
        [
            "--content-root",
            str(content_root),
            "--seed-dir",
            str(seed_dir),
            "status",
            "--route-id",
            ROUTE_ID,
        ],
    ) == 0

    output = capsys.readouterr().out
    assert "Accepted-events gate" in output
    assert "blocked" in output
    assert "stale downstream artifacts: route-concept.md" in output


def prepare_reviewed_accepted_events(content_root: Path, seed_dir: Path) -> None:
    route_dir = content_root / ROUTE_ID
    write_event_list_decisions(content_root, seed_dir, route_dir, {"kool-herc-sedgwick-party": "keep"})
    assert main(
        [
            "--content-root",
            str(content_root),
            "--seed-dir",
            str(seed_dir),
            "run",
            "--route-id",
            ROUTE_ID,
            "--step",
            "accepted_events",
        ],
    ) == 0
    accepted_path = route_dir / "accepted-events.json"
    accepted_events = json.loads(accepted_path.read_text(encoding="utf-8"))
    for accepted_event in accepted_events["accepted_events"]:
        for field in route_content_pipeline.QUALITY_GATE_FIELDS:
            accepted_event["quality_check"][field] = True
    accepted_path.write_text(json.dumps(accepted_events, indent=2) + "\n", encoding="utf-8")
    assert main(
        [
            "--content-root",
            str(content_root),
            "--seed-dir",
            str(seed_dir),
            "run",
            "--route-id",
            ROUTE_ID,
        ],
    ) == 0


def write_event_list_decisions(
    content_root: Path,
    seed_dir: Path,
    route_dir: Path,
    decisions: dict[str, str],
) -> None:
    assert main(
        [
            "--content-root",
            str(content_root),
            "--seed-dir",
            str(seed_dir),
            "run",
            "--route-id",
            ROUTE_ID,
            "--step",
            "event_list",
        ],
    ) == 0
    event_list_path = route_dir / "event-list.json"
    event_list = json.loads(event_list_path.read_text(encoding="utf-8"))
    for candidate in event_list["candidates"]:
        if candidate["candidate_id"] in decisions:
            candidate["status"] = decisions[candidate["candidate_id"]]
    event_list_path.write_text(json.dumps(event_list, indent=2) + "\n", encoding="utf-8")


def write_pipeline_fixture(tmp_path: Path) -> tuple[Path, Path]:
    content_root = tmp_path / "content" / "routes"
    content_docs = tmp_path / "content"
    content_docs.mkdir()
    (content_docs / "route-research-dossier-template.md").write_text("# Template\n", encoding="utf-8")
    (content_docs / "route-editorial-quality-standards.md").write_text("# Standards\n", encoding="utf-8")
    route_dir = content_root / ROUTE_ID
    route_dir.mkdir(parents=True)
    (route_dir / "brief.md").write_text("# Brief\n", encoding="utf-8")
    (route_dir / "research-dossier.md").write_text(build_dossier(), encoding="utf-8")
    seed_dir = tmp_path / "seed"
    seed_dir.mkdir()
    write_seed_files(seed_dir)
    return content_root, seed_dir


def write_fake_codex(tmp_path: Path, output: str = "agent output\n") -> Path:
    fake_codex = tmp_path / "fake-codex"
    fake_codex.write_text(
        f"""#!/bin/sh
out=""
while [ "$#" -gt 0 ]; do
  if [ "$1" = "--output-last-message" ]; then
    shift
    out="$1"
  fi
  shift
done
cat >/dev/null
cat > "$out" <<'FAKE_CODEX_OUTPUT'
{output.rstrip()}
FAKE_CODEX_OUTPUT
""",
        encoding="utf-8",
    )
    fake_codex.chmod(fake_codex.stat().st_mode | stat.S_IEXEC)
    return fake_codex


def build_agent_event_list_json() -> str:
    return json.dumps(
        {
            "_meta": {
                "route_id": ROUTE_ID,
                "target_output": "event-list.json",
                "review_status": "draft",
            },
            "candidates": [
                {
                    "candidate_id": "agent-reviewed-event",
                    "status": "keep",
                    "years": "1973",
                    "place": "1520 Sedgwick Avenue",
                    "working_title": "Agent reviewed event",
                    "route_function": "Shows the agent-authored route function.",
                    "source_leads": ["Interviews", "Archives"],
                    "risk_notes": ["Needs source comparison."],
                    "next_action": "Review accepted-event quality flags.",
                },
            ],
        },
        indent=2,
    ) + "\n"


def build_dossier() -> str:
    return """# Dossier

## Candidate Events

| Candidate ID | Years | Place | Working title | Inclusion rationale | Source leads | Risk notes |
| --- | --- | --- | --- | --- | --- | --- |
| `kool-herc-sedgwick-party` | 1973 | 1520 Sedgwick Avenue | Kool Herc and Cindy Campbell's Sedgwick party | Shows a symbolic origin story in a specific place. | Interviews and public history. | Avoid sole-birthplace wording. |

## Candidate Connections

| From event | To event | Relationship type | Narrative purpose | Source leads | Risk notes |
| --- | --- | --- | --- | --- | --- |
| `kool-herc-sedgwick-party` | `missing-event` | context | This row is ignored because one endpoint is missing. | Source leads. | Risk notes. |
"""


def write_seed_files(seed_dir: Path) -> None:
    (seed_dir / "routes.json").write_text(
        json.dumps(
            {
                "_meta": {"description": "routes", "schema_version": 1},
                "routes": [
                    {
                        "id": ROUTE_ID,
                        "title": "Birth of Hip-Hop",
                        "color": "#e4572e",
                        "creator": "test",
                        "year_start": 1970,
                        "year_end": 1985,
                        "summary": "Test route",
                        "thesis": "Test thesis",
                        "tags": ["hip-hop"],
                        "review_status": "draft",
                        "source_urls": [],
                    },
                ],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (seed_dir / "places.json").write_text(
        json.dumps(
            {
                "_meta": {"description": "places", "schema_version": 1},
                "places": [
                    {
                        "id": "1520-sedgwick-avenue",
                        "name": "1520 Sedgwick Avenue",
                        "borough": "Bronx",
                        "place_type": "building",
                        "latitude": 40.8459,
                        "longitude": -73.9230,
                        "summary": "Test place",
                        "review_status": "draft",
                        "source_urls": [],
                    },
                ],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    for filename, collection in [
        ("events.json", "events"),
        ("connections.json", "connections"),
    ]:
        (seed_dir / filename).write_text(
            json.dumps(
                {
                    "_meta": {"description": collection, "schema_version": 1},
                    collection: [],
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
