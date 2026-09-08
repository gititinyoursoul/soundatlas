#!/usr/bin/env python3
"""Run SoundAtlas Project operations with its dedicated Project credential."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

PROJECT_ENV_PATH = "SOUNDATLAS_GITHUB_PROJECT_ENV_FILE"
PROJECT_OWNER = "gititinyoursoul"

PROJECTS_QUERY = """query { viewer { projectsV2(first: 100) {
  totalCount nodes { id number title closed shortDescription url }
} } }"""
PROJECT_QUERY = """query($number: Int!) {
  viewer { projectV2(number: $number) { id number title } }
}"""
FIELDS_QUERY = """query($number: Int!) { viewer { projectV2(number: $number) {
  fields(first: 100) { totalCount nodes {
    ... on ProjectV2Field { id name dataType }
    ... on ProjectV2IterationField { id name dataType }
    ... on ProjectV2SingleSelectField { id name dataType options { id name } }
  } }
} } }"""
ITEMS_QUERY = """query($number: Int!, $first: Int!, $after: String) {
  viewer { projectV2(number: $number) { items(first: $first, after: $after) {
    pageInfo { hasNextPage endCursor }
    nodes { id fieldValues(first: 50) { nodes {
      ... on ProjectV2ItemFieldSingleSelectValue {
        name field { ... on ProjectV2FieldCommon { name } }
      }
    } } content { __typename
      ... on Issue { number title url repository { nameWithOwner } }
      ... on PullRequest { number title url repository { nameWithOwner } }
    } }
  } } }
}"""
RESOURCE_QUERY = """query($url: URI!) { resource(url: $url) {
  ... on Issue { id }
  ... on PullRequest { id }
} }"""
ADD_ITEM_MUTATION = """mutation($project: ID!, $content: ID!) {
  addProjectV2ItemById(input: {projectId: $project, contentId: $content}) {
    item { id }
  }
}"""
EDIT_ITEM_MUTATION = """mutation(
  $project: ID!, $item: ID!, $field: ID!, $option: String!
) { updateProjectV2ItemFieldValue(input: {
  projectId: $project itemId: $item fieldId: $field
  value: {singleSelectOptionId: $option}
}) { projectV2Item { id } } }"""


class ProjectCredentialError(RuntimeError):
    """Raised when a Project credential or operation cannot be handled safely."""


def read_project_token(path: Path) -> str:
    """Read one non-empty GH_TOKEN assignment without evaluating shell code."""
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise ProjectCredentialError("Project credential file is not readable") from exc
    assignments = []
    for line in lines:
        if not line or line.startswith("#"):
            continue
        if not line.startswith("GH_TOKEN="):
            raise ProjectCredentialError(
                "Project credential file must contain only GH_TOKEN"
            )
        assignments.append(line.removeprefix("GH_TOKEN="))
    if len(assignments) != 1 or not assignments[0]:
        raise ProjectCredentialError(
            "Project credential file must contain one non-empty GH_TOKEN"
        )
    return assignments[0]


def project_environment(
    environ: Mapping[str, str], credential_path: Path | None = None
) -> dict[str, str]:
    """Replace ambient GitHub authentication with the Project-only credential."""
    configured_path = environ.get(PROJECT_ENV_PATH)
    if credential_path is None:
        if not configured_path:
            raise ProjectCredentialError(f"{PROJECT_ENV_PATH} is not configured")
        credential_path = Path(configured_path)
    project_env = dict(environ)
    project_env.pop("GH_TOKEN", None)
    project_env.pop("GITHUB_TOKEN", None)
    project_env["GH_TOKEN"] = read_project_token(credential_path)
    return project_env


def graphql(
    query: str, variables: Mapping[str, str | int], environ: Mapping[str, str]
) -> dict[str, Any]:
    """Run one GraphQL operation through gh without exposing credential material."""
    child_env = project_environment(environ)
    command = ["gh", "api", "graphql", "-f", f"query={query}"]
    for name, value in variables.items():
        command.extend(("-F", f"{name}={value}"))
    result = subprocess.run(
        command, env=child_env, capture_output=True, text=True, check=False
    )
    if result.returncode:
        detail = (
            result.stderr.strip() or result.stdout.strip() or "GitHub API error"
        ).replace(child_env["GH_TOKEN"], "[redacted]")
        raise ProjectCredentialError(f"Project operation failed: {detail}")
    try:
        response = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise ProjectCredentialError("Project operation returned invalid JSON") from exc
    if not isinstance(response, dict) or not isinstance(response.get("data"), dict):
        raise ProjectCredentialError("Project operation returned no data")
    return response["data"]


def check_owner(owner: str) -> None:
    if owner not in (PROJECT_OWNER, "@me"):
        raise ProjectCredentialError(f"Project owner must be {PROJECT_OWNER} or @me")


def project(data: dict[str, Any], number: int) -> dict[str, Any]:
    value = data.get("viewer", {}).get("projectV2")
    if not isinstance(value, dict):
        raise ProjectCredentialError(f"Project #{number} was not found")
    return value


def list_projects(environ: Mapping[str, str]) -> dict[str, Any]:
    connection = graphql(PROJECTS_QUERY, {}, environ)["viewer"]["projectsV2"]
    return {
        "projects": connection.get("nodes", []),
        "totalCount": connection.get("totalCount", 0),
    }


def list_fields(number: int, environ: Mapping[str, str]) -> dict[str, Any]:
    connection = project(graphql(FIELDS_QUERY, {"number": number}, environ), number)[
        "fields"
    ]
    return {
        "fields": [field for field in connection.get("nodes", []) if field],
        "totalCount": connection.get("totalCount", 0),
    }


def item_value(node: dict[str, Any]) -> dict[str, Any]:
    status = next(
        (
            value.get("name")
            for value in node.get("fieldValues", {}).get("nodes", [])
            if value and value.get("field", {}).get("name") == "Status"
        ),
        None,
    )
    content = node.get("content")
    value: dict[str, Any] = {"id": node["id"]}
    if status:
        value["status"] = status
    if isinstance(content, dict):
        value["content"] = {
            "number": content.get("number"),
            "title": content.get("title"),
            "type": content.get("__typename"),
            "url": content.get("url"),
            "repository": content.get("repository", {}).get("nameWithOwner"),
        }
    return value


def list_items(number: int, limit: int, environ: Mapping[str, str]) -> dict[str, Any]:
    items: list[dict[str, Any]] = []
    cursor: str | None = None
    while len(items) < limit:
        variables: dict[str, str | int] = {
            "number": number,
            "first": min(100, limit - len(items)),
        }
        if cursor:
            variables["after"] = cursor
        connection = project(graphql(ITEMS_QUERY, variables, environ), number)["items"]
        items.extend(item_value(node) for node in connection.get("nodes", []) if node)
        page = connection.get("pageInfo", {})
        if not page.get("hasNextPage"):
            break
        cursor = page.get("endCursor")
        if not cursor:
            raise ProjectCredentialError("Project item pagination returned no cursor")
    return {"items": items, "totalCount": len(items)}


def project_id(number: int, environ: Mapping[str, str]) -> str:
    value = project(graphql(PROJECT_QUERY, {"number": number}, environ), number).get(
        "id"
    )
    if not isinstance(value, str):
        raise ProjectCredentialError(f"Project #{number} returned no ID")
    return value


def add_item(number: int, url: str, environ: Mapping[str, str]) -> dict[str, str]:
    resource = graphql(RESOURCE_QUERY, {"url": url}, environ).get("resource")
    content_id = resource.get("id") if isinstance(resource, dict) else None
    if not isinstance(content_id, str):
        raise ProjectCredentialError("Issue or pull request URL was not found")
    data = graphql(
        ADD_ITEM_MUTATION,
        {"project": project_id(number, environ), "content": content_id},
        environ,
    )
    return {"id": data["addProjectV2ItemById"]["item"]["id"]}


def edit_item(
    item: str,
    project_value: str,
    field: str,
    option: str,
    environ: Mapping[str, str],
) -> dict[str, str]:
    data = graphql(
        EDIT_ITEM_MUTATION,
        {"project": project_value, "item": item, "field": field, "option": option},
        environ,
    )
    return {"id": data["updateProjectV2ItemFieldValue"]["projectV2Item"]["id"]}


def parser() -> argparse.ArgumentParser:
    command_parser = argparse.ArgumentParser(description=__doc__)
    subparsers = command_parser.add_subparsers(dest="command", required=True)
    for name in ("list", "field-list", "item-list", "item-add"):
        subparser = subparsers.add_parser(name)
        if name != "list":
            subparser.add_argument("number", type=int)
        subparser.add_argument("--owner", default=PROJECT_OWNER)
        subparser.add_argument("--format", choices=("json",), default="json")
        if name == "item-list":
            subparser.add_argument("--limit", type=int, default=30)
        if name == "item-add":
            subparser.add_argument("--url", required=True)
    edit_parser = subparsers.add_parser("item-edit")
    edit_parser.add_argument("--id", required=True)
    edit_parser.add_argument("--project-id", required=True)
    edit_parser.add_argument("--field-id", required=True)
    edit_parser.add_argument("--single-select-option-id", required=True)
    return command_parser


def run_project(
    arguments: Sequence[str], environ: Mapping[str, str] | None = None
) -> int:
    args = parser().parse_args(arguments)
    source_env = os.environ if environ is None else environ
    if hasattr(args, "owner"):
        check_owner(args.owner)
    if args.command == "list":
        output = list_projects(source_env)
    elif args.command == "field-list":
        output = list_fields(args.number, source_env)
    elif args.command == "item-list":
        if not 1 <= args.limit <= 500:
            raise ProjectCredentialError("Project item limit must be between 1 and 500")
        output = list_items(args.number, args.limit, source_env)
    elif args.command == "item-add":
        output = add_item(args.number, args.url, source_env)
    else:
        output = edit_item(
            args.id,
            args.project_id,
            args.field_id,
            args.single_select_option_id,
            source_env,
        )
    print(json.dumps(output, ensure_ascii=False))
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    try:
        return run_project(sys.argv[1:] if argv is None else argv)
    except ProjectCredentialError as exc:
        print(f"Project authentication failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
