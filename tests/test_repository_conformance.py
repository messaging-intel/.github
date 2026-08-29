from __future__ import annotations

import copy
import datetime as dt
import importlib.util
import os
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "audit_repository_conformance.py"
SPEC = importlib.util.spec_from_file_location("repository_conformance", MODULE_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("cannot load repository conformance module")
audit = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(audit)


class FakeGitHubClient:
    def __init__(self, repositories: list[str], missing: set[tuple[str, str]]) -> None:
        self.repositories = repositories
        self.missing = missing

    def active_repositories(self, organization: str, prefix: str) -> dict[str, str]:
        self.organization = organization
        self.prefix = prefix
        return {repository: "main" for repository in self.repositories}

    def path_exists(self, organization: str, repository: str, branch: str, path: str) -> bool:
        return (repository, path) not in self.missing


class RepositoryConformanceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.policy = audit.load_policy(ROOT / "policies" / "repository-conformance.v1.json")
        self.today = dt.date(2026, 8, 24)

    def test_checked_in_policy_is_valid(self) -> None:
        audit.validate_policy(self.policy, self.today)
        self.assertEqual(14, len(self.policy["repositories"]))
        self.assertEqual(29, len(self.policy["exceptions"]))

    def test_missing_or_empty_live_authority_fails_closed(self) -> None:
        with (
            mock.patch.dict(os.environ, {}, clear=True),
            self.assertRaisesRegex(audit.AuditError, "requires non-empty GitHub read authority"),
        ):
            audit.GitHubClient.from_environment("https://api.github.test", "TEST_TOKEN")
        with (
            mock.patch.dict(os.environ, {"TEST_TOKEN": "   "}, clear=True),
            self.assertRaisesRegex(audit.AuditError, "requires non-empty GitHub read authority"),
        ):
            audit.GitHubClient.from_environment("https://api.github.test", "TEST_TOKEN")

    def test_exception_must_be_ticketed(self) -> None:
        policy = copy.deepcopy(self.policy)
        policy["exceptions"][0]["ticket"] = "not-a-ticket"
        with self.assertRaisesRegex(audit.AuditError, "DEN issue identifier"):
            audit.validate_policy(policy, self.today)

    def test_exception_expiration_is_enforced(self) -> None:
        policy = copy.deepcopy(self.policy)
        policy["exceptions"][0]["expiresOn"] = "2026-08-23"
        with self.assertRaisesRegex(audit.AuditError, "expired exception"):
            audit.validate_policy(policy, self.today)

    def test_new_prefixed_repository_is_inventory_drift(self) -> None:
        expected = set(self.policy["repositories"])
        with self.assertRaisesRegex(audit.AuditError, "unexpected=.*msgint-new-component"):
            audit.compare_inventory(expected, expected | {"msgint-new-component"})

    def test_missing_requirement_uses_only_matching_exception(self) -> None:
        repositories = self.policy["repositories"]
        repository = repositories[0]
        policy = {
            "organization": "messaging-intel",
            "repositoryPrefix": "msgint-",
            "repositories": repositories,
            "requirements": [{"id": "guard", "paths": [".github/workflows/guard.yml"]}],
            "exceptions": [
                {
                    "repository": repository,
                    "requirement": "guard",
                    "ticket": "DEN-3896",
                    "expiresOn": "2026-09-30",
                    "reason": "A separately reviewed propagation change is still required."
                }
            ],
        }
        client = FakeGitHubClient(
            repositories,
            {(repository, ".github/workflows/guard.yml")},
        )
        used, findings = audit.audit_live(policy, client)
        self.assertEqual(1, used)
        self.assertTrue(any(line.startswith(f"EXCEPTION {repository}/guard") for line in findings))

    def test_unexcepted_missing_requirement_fails(self) -> None:
        repositories = self.policy["repositories"]
        repository = repositories[0]
        policy = {
            "organization": "messaging-intel",
            "repositoryPrefix": "msgint-",
            "repositories": repositories,
            "requirements": [{"id": "guard", "paths": [".github/workflows/guard.yml"]}],
            "exceptions": [],
        }
        client = FakeGitHubClient(
            repositories,
            {(repository, ".github/workflows/guard.yml")},
        )
        with self.assertRaisesRegex(audit.AuditError, f"{repository} is missing guard"):
            audit.audit_live(policy, client)


if __name__ == "__main__":
    unittest.main()
