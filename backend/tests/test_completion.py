import json
import sys
from pathlib import Path

from scripts import completion


def test_main_completes_known_script_options_with_prefix(monkeypatch, capsys) -> None:
    monkeypatch.setattr(
        sys,
        "argv",
        ["completion.py", "options", "enrich_image_links.py", "--route"],
    )

    exit_code = completion.main()

    captured = capsys.readouterr()
    assert exit_code == 0
    assert captured.out.splitlines() == ["--route-id"]
    assert captured.err == ""


def test_main_completes_event_and_route_ids_from_seed_files(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    write_seed_file(
        tmp_path / "events.json",
        "events",
        [{"id": "second-event"}, {"id": "first-event"}],
    )
    write_seed_file(
        tmp_path / "routes.json",
        "routes",
        [{"id": "other-route"}, {"id": "birth-of-hip-hop"}],
    )
    monkeypatch.setattr(completion, "SEED_DIR", tmp_path)

    monkeypatch.setattr(sys, "argv", ["completion.py", "values", "--event-id"])
    assert completion.main() == 0
    event_output = capsys.readouterr()

    monkeypatch.setattr(
        sys,
        "argv",
        ["completion.py", "values", "--route-id", "birth"],
    )
    assert completion.main() == 0
    route_output = capsys.readouterr()

    assert event_output.out.splitlines() == ["first-event", "second-event"]
    assert event_output.err == ""
    assert route_output.out.splitlines() == ["birth-of-hip-hop"]
    assert route_output.err == ""


def test_main_completes_fixed_argument_choices(monkeypatch, capsys) -> None:
    monkeypatch.setattr(sys, "argv", ["completion.py", "values", "--kind", "m"])

    exit_code = completion.main()

    captured = capsys.readouterr()
    assert exit_code == 0
    assert captured.out.splitlines() == ["media"]
    assert captured.err == ""


def test_main_rejects_invalid_usage(monkeypatch, capsys) -> None:
    monkeypatch.setattr(sys, "argv", ["completion.py", "unknown", "name"])

    exit_code = completion.main()

    captured = capsys.readouterr()
    assert exit_code == 2
    assert captured.out == ""
    assert captured.err == "usage: completion.py {options,values} name [prefix]\n"


def test_seed_ids_returns_empty_for_missing_or_invalid_seed_data(tmp_path: Path) -> None:
    assert completion.seed_ids(tmp_path / "missing.json", "events") == []

    invalid_json_path = tmp_path / "invalid.json"
    invalid_json_path.write_text("not JSON", encoding="utf-8")
    assert completion.seed_ids(invalid_json_path, "events") == []

    invalid_collection_path = tmp_path / "invalid-collection.json"
    invalid_collection_path.write_text(json.dumps({"events": {}}), encoding="utf-8")
    assert completion.seed_ids(invalid_collection_path, "events") == []


def test_seed_ids_ignores_invalid_records_and_ids(tmp_path: Path) -> None:
    path = tmp_path / "events.json"
    write_seed_file(
        path,
        "events",
        ["not-a-record", {"title": "Missing ID"}, {"id": 123}, {"id": "valid-id"}],
    )

    assert completion.seed_ids(path, "events") == ["valid-id"]


def write_seed_file(
    path: Path,
    collection_key: str,
    records: list[object],
) -> None:
    path.write_text(json.dumps({collection_key: records}), encoding="utf-8")
