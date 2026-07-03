import json
import stat
from pathlib import Path

from scripts import route_content_pipeline
from scripts.route_content_pipeline import main


ROUTE_ID = "birth-of-hip-hop"


def test_pipeline_missing_mode_creates_review_artifacts(
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
    assert (route_dir / "pipeline.json").exists()
    assert (route_dir / "event-list.md").exists()
    assert (route_dir / "event-list.json").exists()
    assert (route_dir / "route-concept.md").exists()
    assert (route_dir / "event-framing.json").exists()
    assert (route_dir / "place-framing.json").exists()
    assert (route_dir / "connection-framing.json").exists()
    assert (route_dir / "seed-transfer-report.md").exists()
    assert (route_dir / "validation-report.md").exists()

    event_list = json.loads((route_dir / "event-list.json").read_text(encoding="utf-8"))
    assert event_list["_meta"]["review_status"] == "draft"
    assert event_list["candidates"][0]["candidate_id"] == "kool-herc-sedgwick-party"
    assert event_list["candidates"][0]["status"] == "develop"


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
    assert main(["--content-root", str(content_root), "--seed-dir", str(seed_dir), "run", "--route-id", ROUTE_ID]) == 0

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


def test_promote_write_requires_reviewed_event_framing(
    tmp_path: Path,
    capsys,
) -> None:
    content_root, seed_dir = write_pipeline_fixture(tmp_path)
    assert main(["--content-root", str(content_root), "--seed-dir", str(seed_dir), "run", "--route-id", ROUTE_ID]) == 0

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

    captured = capsys.readouterr()
    assert exit_code == 2
    assert "event_framing review_status is 'reviewed'" in captured.err


def test_promote_write_adds_reviewed_draft_events_to_seed(
    tmp_path: Path,
) -> None:
    content_root, seed_dir = write_pipeline_fixture(tmp_path)
    route_dir = content_root / ROUTE_ID
    assert main(["--content-root", str(content_root), "--seed-dir", str(seed_dir), "run", "--route-id", ROUTE_ID]) == 0
    manifest = json.loads((route_dir / "pipeline.json").read_text(encoding="utf-8"))
    manifest["steps"]["event_framing"]["review_status"] = "reviewed"
    (route_dir / "pipeline.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

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
    assert main(["--content-root", str(content_root), "--seed-dir", str(seed_dir), "run", "--route-id", ROUTE_ID]) == 0
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
    assert run_metadata["review_status"] == "draft"
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


def test_agent_invokes_codex_cli_and_mark_reviewed_creates_variant(tmp_path: Path) -> None:
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
        ],
    ) == 0
    assert (route_dir / "brief_to_dossier-output.ai-draft.md").read_text(encoding="utf-8") == "agent output\n"

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
            "--mark-reviewed",
        ],
    ) == 0

    manifest = json.loads((route_dir / "pipeline.json").read_text(encoding="utf-8"))
    assert (route_dir / "research-dossier-agent-reviewed.md").read_text(encoding="utf-8") == "agent output\n"
    assert manifest["active_dossier"] == "research-dossier-agent-reviewed.md"
    assert manifest["agent_steps"]["brief_to_dossier"]["review_status"] == "reviewed"


def test_agent_blocks_draft_dependency_unless_allowed(tmp_path: Path, capsys) -> None:
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
        ],
    ) == 0

    blocked_code = main(
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
    )

    captured = capsys.readouterr()
    assert blocked_code == 2
    assert "Refusing to run dossier_to_event_review with draft agent output" in captured.err

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
            "--allow-draft-inputs",
        ],
    ) == 0
    assert (route_dir / "dossier_to_event_review-output.ai-draft.md").exists()


def test_agent_prompts_include_editorial_quality_contracts(tmp_path: Path) -> None:
    content_root, seed_dir = write_pipeline_fixture(tmp_path)
    route_dir = content_root / ROUTE_ID
    assert main(["--content-root", str(content_root), "--seed-dir", str(seed_dir), "run", "--route-id", ROUTE_ID]) == 0

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
    assert "reviewed_output=research-dossier-agent-reviewed.md" in output


def write_pipeline_fixture(tmp_path: Path) -> tuple[Path, Path]:
    content_root = tmp_path / "content" / "routes"
    content_docs = tmp_path / "content"
    content_docs.mkdir()
    (content_docs / "route-research-dossier-template.md").write_text("# Template\n", encoding="utf-8")
    (content_docs / "route-editorial-quality-standards.md").write_text("# Standards\n", encoding="utf-8")
    route_dir = content_root / ROUTE_ID
    route_dir.mkdir(parents=True)
    (route_dir / "brief.md").write_text("# Brief\n", encoding="utf-8")
    (route_dir / "research-dossier-mvp-edit.md").write_text(build_dossier(), encoding="utf-8")
    seed_dir = tmp_path / "seed"
    seed_dir.mkdir()
    write_seed_files(seed_dir)
    return content_root, seed_dir


def write_fake_codex(tmp_path: Path) -> Path:
    fake_codex = tmp_path / "fake-codex"
    fake_codex.write_text(
        """#!/bin/sh
out=""
while [ "$#" -gt 0 ]; do
  if [ "$1" = "--output-last-message" ]; then
    shift
    out="$1"
  fi
  shift
done
cat >/dev/null
printf 'agent output\\n' > "$out"
""",
        encoding="utf-8",
    )
    fake_codex.chmod(fake_codex.stat().st_mode | stat.S_IEXEC)
    return fake_codex


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
