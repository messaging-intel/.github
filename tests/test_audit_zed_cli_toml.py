from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "audit_zed_cli_toml.py"
SPEC = importlib.util.spec_from_file_location("audit_zed_cli_toml", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)
Auditor = MODULE.Auditor


VALID_ZPKG = '''
[package]
org = "example"
name = "contracts"
version = "1.2.3"

[package.repository]
vcs = "git"
url = "https://github.com/example/contracts"

[publish]
smoke_test = 'test -f "$ZED_PKG_TEST_TARGET/schema/domain.json"'
exclude = [".github/**", "tmp/**"]

[targets.repository]
dir = "."

[targets.schema]
dir = "schema"
adapter = "none"
'''.strip() + "\n"

VALID_CLI = '''
[help]
url = "https://github.com/example/contracts#command-line-configuration"

[env]
files = []

[parse]
positionals_env = "EXAMPLE_POSITIONALS"
unknown_options_env = "EXAMPLE_UNKNOWN_OPTIONS"
errors_env = "EXAMPLE_PARSE_ERRORS"
allow_unknown = false

[flags.contract]
env = "EXAMPLE_CONTRACT"
aliases = ["contract"]
short = "c"
type = "string"
default = "all"
help = "Contract family."
'''.strip() + "\n"

README = """# Contracts\n\n## Command-line configuration\n\nDocumented.\n"""


class AuditTests(unittest.TestCase):
    def fixture(self) -> tuple[tempfile.TemporaryDirectory[str], Path]:
        temp = tempfile.TemporaryDirectory()
        root = Path(temp.name)
        (root / "schema").mkdir()
        (root / "generated" / "rust").mkdir(parents=True)
        (root / ".zpkg.toml").write_text(VALID_ZPKG, encoding="utf-8")
        (root / ".zpkg.lock").write_text("version = 1\n", encoding="utf-8")
        (root / ".cli-flags.toml").write_text(VALID_CLI, encoding="utf-8")
        (root / "README.md").write_text(README, encoding="utf-8")
        (root / "generated" / "rust" / "Cargo.toml").write_text(
            '''[package]\nname = "contracts"\nversion = "1.2.3"\nedition = "2024"\npublish = false\n''',
            encoding="utf-8",
        )
        return temp, root

    def run_audit(self, root: Path):
        return Auditor(
            root,
            repository="example/contracts",
            require_cli_flags=True,
            require_zpkg=True,
            enforce_canonical_flags_source=True,
            enforce_generated_cargo_version=True,
            require_no_dotenv=True,
            require_strict_cli_channels=True,
        ).run()

    @staticmethod
    def messages(report):
        return [item["message"] for item in report["findings"]]

    def test_valid_fixture_passes(self):
        temp, root = self.fixture()
        self.addCleanup(temp.cleanup)
        report = self.run_audit(root)
        self.assertEqual(report["status"], "passed", report)
        self.assertEqual(report["finding_count"], 0)

    def test_missing_lock_fails(self):
        temp, root = self.fixture()
        self.addCleanup(temp.cleanup)
        (root / ".zpkg.lock").unlink()
        report = self.run_audit(root)
        self.assertIn(
            "Zed package manifest requires a parsed .zpkg.lock",
            self.messages(report),
        )

    def test_divergent_root_target_name_fails(self):
        temp, root = self.fixture()
        self.addCleanup(temp.cleanup)
        manifest = (root / ".zpkg.toml").read_text(encoding="utf-8")
        manifest = manifest.replace(
            '[targets.repository]\ndir = "."',
            '[targets.repository]\ndir = "."\nname = "contracts-repository"',
        )
        (root / ".zpkg.toml").write_text(manifest, encoding="utf-8")
        report = self.run_audit(root)
        self.assertIn(
            "root repository target name must be omitted or equal package.name",
            self.messages(report),
        )

    def test_non_repository_root_target_fails(self):
        temp, root = self.fixture()
        self.addCleanup(temp.cleanup)
        manifest = (root / ".zpkg.toml").read_text(encoding="utf-8")
        manifest = manifest.replace("[targets.repository]", "[targets.flutter]")
        (root / ".zpkg.toml").write_text(manifest, encoding="utf-8")
        report = self.run_audit(root)
        joined = "\n".join(self.messages(report))
        self.assertIn("targets.repository", joined)
        self.assertIn("only targets.repository may use", joined)

    def test_dependency_without_locked_package_fails(self):
        temp, root = self.fixture()
        self.addCleanup(temp.cleanup)
        manifest = (root / ".zpkg.toml").read_text(encoding="utf-8")
        manifest += '\n[dependencies]\n"example/helper" = "=1.0.0"\n'
        (root / ".zpkg.toml").write_text(manifest, encoding="utf-8")
        report = self.run_audit(root)
        self.assertIn(
            "direct dependency example/helper is absent from .zpkg.lock",
            self.messages(report),
        )

    def test_smoke_test_cannot_reference_excluded_file(self):
        temp, root = self.fixture()
        self.addCleanup(temp.cleanup)
        manifest = (root / ".zpkg.toml").read_text(encoding="utf-8")
        manifest = manifest.replace(
            'test -f "$ZED_PKG_TEST_TARGET/schema/domain.json"',
            'sh "$ZED_PKG_TEST_TARGET/.github/smoke.sh"',
        )
        (root / ".zpkg.toml").write_text(manifest, encoding="utf-8")
        report = self.run_audit(root)
        self.assertTrue(
            any(
                "smoke test references excluded path" in message
                for message in self.messages(report)
            ),
            report,
        )

    def test_retired_flags_source_fails(self):
        temp, root = self.fixture()
        self.addCleanup(temp.cleanup)
        (root / "flake.nix").write_text(
            'url = "github:ORESoftware/flags-2-env/abc";\n', encoding="utf-8"
        )
        (root / "flake.lock").write_text(
            json.dumps(
                {
                    "nodes": {
                        "flags": {
                            "locked": {
                                "owner": "ORESoftware",
                                "repo": "flags-2-env",
                            },
                            "original": {
                                "owner": "ORESoftware",
                                "repo": "flags-2-env",
                            },
                        }
                    }
                }
            ),
            encoding="utf-8",
        )
        report = self.run_audit(root)
        joined = "\n".join(self.messages(report))
        self.assertIn("github:flags-2-env/flags-2-env", joined)
        self.assertIn("must use owner flags-2-env", joined)

    def test_missing_readme_help_anchor_fails(self):
        temp, root = self.fixture()
        self.addCleanup(temp.cleanup)
        (root / "README.md").write_text("# Contracts\n", encoding="utf-8")
        report = self.run_audit(root)
        self.assertIn(
            "help URL fragment #command-line-configuration is absent from README.md",
            self.messages(report),
        )

    def test_generated_cargo_version_and_publish_are_enforced(self):
        temp, root = self.fixture()
        self.addCleanup(temp.cleanup)
        cargo = root / "generated" / "rust" / "Cargo.toml"
        cargo.write_text(
            '''[package]\nname = "contracts"\nversion = "0.1.0"\nedition = "2024"\npublish = true\n''',
            encoding="utf-8",
        )
        report = self.run_audit(root)
        joined = "\n".join(self.messages(report))
        self.assertIn("generated Cargo package must set publish = false", joined)
        self.assertIn(
            "generated Cargo version must equal Zed package version 1.2.3",
            joined,
        )

    def test_strict_dotenv_boundary_fails_without_explicit_opt_out(self):
        temp, root = self.fixture()
        self.addCleanup(temp.cleanup)
        cli = (root / ".cli-flags.toml").read_text(encoding="utf-8")
        cli = cli.replace("[env]\nfiles = []\n\n", "")
        (root / ".cli-flags.toml").write_text(cli, encoding="utf-8")
        report = self.run_audit(root)
        self.assertIn(
            "strict secret boundary requires an [env] table",
            self.messages(report),
        )

    def test_strict_cli_channels_are_required(self):
        temp, root = self.fixture()
        self.addCleanup(temp.cleanup)
        cli = (root / ".cli-flags.toml").read_text(encoding="utf-8")
        cli = cli.replace('errors_env = "EXAMPLE_PARSE_ERRORS"\n', "")
        (root / ".cli-flags.toml").write_text(cli, encoding="utf-8")
        report = self.run_audit(root)
        self.assertIn(
            "parse.errors_env must be an uppercase env key",
            self.messages(report),
        )

    def test_locked_dependency_requires_complete_immutable_metadata(self):
        temp, root = self.fixture()
        self.addCleanup(temp.cleanup)
        manifest = (root / ".zpkg.toml").read_text(encoding="utf-8")
        manifest += '\n[dependencies]\n"example/helper" = "=1.0.0"\n'
        (root / ".zpkg.toml").write_text(manifest, encoding="utf-8")
        (root / ".zpkg.lock").write_text(
            'version = 1\n\n[[package]]\norg = "example"\nname = "helper"\nversion = "1.0.0"\n',
            encoding="utf-8",
        )
        report = self.run_audit(root)
        joined = "\n".join(self.messages(report))
        self.assertIn("requires canonical sha256", joined)
        self.assertIn("requires non-empty vcs_commit", joined)
        self.assertIn("size must be a positive integer", joined)

    def test_all_toml_files_are_parsed(self):
        temp, root = self.fixture()
        self.addCleanup(temp.cleanup)
        (root / "broken.toml").write_text("[broken\n", encoding="utf-8")
        report = self.run_audit(root)
        self.assertTrue(
            any("cannot parse TOML" in message for message in self.messages(report))
        )


if __name__ == "__main__":
    unittest.main()
