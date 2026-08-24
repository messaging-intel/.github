#!/usr/bin/env python3
"""Audit the live Messaging Intel repository baseline through the GitHub API."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

DEFAULT_POLICY = Path("policies/repository-conformance.v1.json")
DEFAULT_API_URL = "https://api.github.com"
DEFAULT_TOKEN_ENV = "MSGINT_CONFORMANCE_READ_TOKEN"
TICKET_PATTERN = re.compile(r"^DEN-[1-9][0-9]*$")


class AuditError(RuntimeError):
    """A bounded policy, authority, or live-conformance failure."""


def load_policy(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as error:
        raise AuditError(f"policy file is missing: {path}") from error
    except json.JSONDecodeError as error:
        raise AuditError(f"policy is not valid JSON: {error}") from error
    if not isinstance(value, dict):
        raise AuditError("policy root must be a JSON object")
    return value


def parse_date(value: object, label: str) -> dt.date:
    if not isinstance(value, str):
        raise AuditError(f"{label} must be an ISO date")
    try:
        return dt.date.fromisoformat(value)
    except ValueError as error:
        raise AuditError(f"{label} must be an ISO date") from error


def validate_policy(policy: dict[str, Any], today: dt.date) -> None:
    if policy.get("schemaVersion") != 1:
        raise AuditError("schemaVersion must be 1")

    organization = policy.get("organization")
    prefix = policy.get("repositoryPrefix")
    if not isinstance(organization, str) or not organization:
        raise AuditError("organization must be a non-empty string")
    if not isinstance(prefix, str) or not prefix:
        raise AuditError("repositoryPrefix must be a non-empty string")

    repositories = policy.get("repositories")
    if not isinstance(repositories, list) or not repositories:
        raise AuditError("repositories must be a non-empty array")
    if len(repositories) != 14:
        raise AuditError(f"policy must enumerate exactly 14 production repositories, got {len(repositories)}")
    if any(not isinstance(name, str) or not name.startswith(prefix) for name in repositories):
        raise AuditError("every repository must be a prefixed non-empty string")
    if repositories != sorted(set(repositories)):
        raise AuditError("repositories must be unique and sorted")
    repository_set = set(repositories)

    requirements = policy.get("requirements")
    if not isinstance(requirements, list) or not requirements:
        raise AuditError("requirements must be a non-empty array")
    requirement_by_id: dict[str, dict[str, Any]] = {}
    for index, requirement in enumerate(requirements):
        label = f"requirements[{index}]"
        if not isinstance(requirement, dict):
            raise AuditError(f"{label} must be an object")
        requirement_id = requirement.get("id")
        paths = requirement.get("paths")
        if not isinstance(requirement_id, str) or not requirement_id:
            raise AuditError(f"{label}.id must be a non-empty string")
        if requirement_id in requirement_by_id:
            raise AuditError(f"duplicate requirement id: {requirement_id}")
        if not isinstance(paths, list) or not paths or any(not isinstance(path, str) or not path for path in paths):
            raise AuditError(f"{label}.paths must contain non-empty strings")
        scoped = requirement.get("repositories", repositories)
        if not isinstance(scoped, list) or not scoped:
            raise AuditError(f"{label}.repositories must be a non-empty array when provided")
        if len(scoped) != len(set(scoped)) or not set(scoped).issubset(repository_set):
            raise AuditError(f"{label}.repositories must be unique policy repositories")
        requirement_by_id[requirement_id] = requirement

    exceptions = policy.get("exceptions")
    if not isinstance(exceptions, list):
        raise AuditError("exceptions must be an array")
    seen_exceptions: set[tuple[str, str]] = set()
    for index, exception in enumerate(exceptions):
        label = f"exceptions[{index}]"
        if not isinstance(exception, dict):
            raise AuditError(f"{label} must be an object")
        repository = exception.get("repository")
        requirement_id = exception.get("requirement")
        ticket = exception.get("ticket")
        reason = exception.get("reason")
        if repository not in repository_set:
            raise AuditError(f"{label}.repository is not in the production inventory")
        requirement = requirement_by_id.get(requirement_id)
        if requirement is None:
            raise AuditError(f"{label}.requirement is unknown")
        scoped = requirement.get("repositories", repositories)
        if repository not in scoped:
            raise AuditError(f"{label} targets a repository outside the requirement scope")
        key = (repository, requirement_id)
        if key in seen_exceptions:
            raise AuditError(f"duplicate exception for {repository}/{requirement_id}")
        seen_exceptions.add(key)
        if not isinstance(ticket, str) or not TICKET_PATTERN.fullmatch(ticket):
            raise AuditError(f"{label}.ticket must be a DEN issue identifier")
        if not isinstance(reason, str) or len(reason.strip()) < 20:
            raise AuditError(f"{label}.reason must explain the temporary gap")
        expires_on = parse_date(exception.get("expiresOn"), f"{label}.expiresOn")
        if expires_on < today:
            raise AuditError(f"expired exception for {repository}/{requirement_id}: {expires_on}")


class GitHubClient:
    def __init__(self, api_url: str, token: str) -> None:
        if not token.strip():
            raise AuditError("GitHub read authority is empty")
        self.api_url = api_url.rstrip("/")
        self.token = token

    @classmethod
    def from_environment(cls, api_url: str, token_env: str) -> GitHubClient:
        token = os.environ.get(token_env)
        if token is None or not token.strip():
            raise AuditError(
                f"live audit requires non-empty GitHub read authority in {token_env}"
            )
        return cls(api_url, token)

    def request_json(self, route: str, *, missing_ok: bool = False) -> Any | None:
        request = urllib.request.Request(
            f"{self.api_url}{route}",
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {self.token}",
                "User-Agent": "messaging-intel-repository-conformance/1",
                "X-GitHub-Api-Version": "2022-11-28",
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                return json.load(response)
        except urllib.error.HTTPError as error:
            if missing_ok and error.code == 404:
                return None
            raise AuditError(f"GitHub API rejected {route} with HTTP {error.code}") from error
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as error:
            raise AuditError(f"GitHub API request failed for {route}: {type(error).__name__}") from error

    def active_repositories(self, organization: str, prefix: str) -> dict[str, str]:
        result: dict[str, str] = {}
        for page in range(1, 101):
            route = (
                f"/orgs/{urllib.parse.quote(organization, safe='')}/repos"
                f"?type=all&per_page=100&page={page}"
            )
            payload = self.request_json(route)
            if not isinstance(payload, list):
                raise AuditError("GitHub repository inventory response must be an array")
            for item in payload:
                if not isinstance(item, dict):
                    raise AuditError("GitHub repository inventory contains a non-object entry")
                name = item.get("name")
                archived = item.get("archived")
                default_branch = item.get("default_branch")
                if isinstance(name, str) and name.startswith(prefix) and archived is False:
                    if not isinstance(default_branch, str) or not default_branch:
                        raise AuditError(f"active repository {name} has no default branch")
                    result[name] = default_branch
            if len(payload) < 100:
                return result
        raise AuditError("GitHub repository inventory exceeded 10,000 entries")

    def path_exists(self, organization: str, repository: str, branch: str, path: str) -> bool:
        route = (
            f"/repos/{urllib.parse.quote(organization, safe='')}/"
            f"{urllib.parse.quote(repository, safe='')}/contents/"
            f"{urllib.parse.quote(path, safe='/')}?ref={urllib.parse.quote(branch, safe='')}"
        )
        payload = self.request_json(route, missing_ok=True)
        if payload is None:
            return False
        if not isinstance(payload, dict) or payload.get("type") != "file":
            raise AuditError(f"expected a file response for {repository}:{path}")
        return True


def exception_index(policy: dict[str, Any]) -> dict[tuple[str, str], dict[str, Any]]:
    return {
        (item["repository"], item["requirement"]): item
        for item in policy["exceptions"]
    }


def compare_inventory(expected: set[str], discovered: set[str]) -> None:
    missing = sorted(expected - discovered)
    unexpected = sorted(discovered - expected)
    if missing or unexpected:
        raise AuditError(
            "production repository inventory drift: "
            f"missing={missing or 'none'}, unexpected={unexpected or 'none'}"
        )


def audit_live(policy: dict[str, Any], client: GitHubClient) -> tuple[int, list[str]]:
    organization = policy["organization"]
    repositories = policy["repositories"]
    live = client.active_repositories(organization, policy["repositoryPrefix"])
    compare_inventory(set(repositories), set(live))
    exceptions = exception_index(policy)
    findings: list[str] = []
    used_exceptions = 0

    for requirement in policy["requirements"]:
        requirement_id = requirement["id"]
        scoped = requirement.get("repositories", repositories)
        for repository in scoped:
            matched_path = next(
                (
                    path
                    for path in requirement["paths"]
                    if client.path_exists(
                        organization,
                        repository,
                        live[repository],
                        path,
                    )
                ),
                None,
            )
            exception = exceptions.get((repository, requirement_id))
            if matched_path is not None:
                findings.append(f"PASS {repository}/{requirement_id}: {matched_path}")
                if exception is not None:
                    findings.append(
                        f"NOTICE {repository}/{requirement_id}: exception {exception['ticket']} is now unused"
                    )
                continue
            if exception is None:
                raise AuditError(
                    f"{repository} is missing {requirement_id}; expected one of {requirement['paths']}"
                )
            used_exceptions += 1
            findings.append(
                f"EXCEPTION {repository}/{requirement_id}: "
                f"{exception['ticket']} through {exception['expiresOn']} - {exception['reason']}"
            )

    return used_exceptions, findings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--policy", type=Path, default=DEFAULT_POLICY)
    parser.add_argument("--api-url", default=os.environ.get("GITHUB_API_URL", DEFAULT_API_URL))
    parser.add_argument("--token-env", default=DEFAULT_TOKEN_ENV)
    parser.add_argument("--validate-policy-only", action="store_true")
    arguments = parser.parse_args()

    try:
        policy = load_policy(arguments.policy)
        validate_policy(policy, dt.datetime.now(tz=dt.UTC).date())
        if arguments.validate_policy_only:
            print(
                f"repository-conformance: policy ok - "
                f"{len(policy['repositories'])} repositories, "
                f"{len(policy['requirements'])} requirements, "
                f"{len(policy['exceptions'])} expiring exceptions"
            )
            return 0

        client = GitHubClient.from_environment(arguments.api_url, arguments.token_env)
        used_exceptions, findings = audit_live(policy, client)
        for finding in findings:
            print(finding)
        print(
            f"repository-conformance: PASS - audited {len(policy['repositories'])}/"
            f"{len(policy['repositories'])} production repositories; "
            f"{used_exceptions} active exceptions"
        )
        return 0
    except AuditError as error:
        print(f"repository-conformance: ERROR: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
