#!/usr/bin/env python3
"""Fail-closed audit for Zed, flags-2-env, Cargo, and repository TOML contracts."""

from __future__ import annotations

import argparse
import fnmatch
import json
import os
import re
import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any, Iterable
from urllib.parse import urlparse

MAX_TOML_BYTES = 2 * 1024 * 1024
IGNORED_PARTS = {
    ".git",
    ".dart_tool",
    ".zed",
    ".zpkg-staging",
    "build",
    "node_modules",
    "target",
    "temp",
    "tmp",
    "zed_modules",
}
ALLOWED_FLAG_TYPES = {
    "array",
    "bool",
    "boolean",
    "decimal",
    "double",
    "float",
    "int",
    "integer",
    "json",
    "json-array",
    "json-object",
    "list",
    "map",
    "number",
    "object",
    "string",
}


@dataclass(frozen=True)
class Finding:
    path: str
    message: str


class Auditor:
    def __init__(
        self,
        root: Path,
        *,
        repository: str | None,
        require_cli_flags: bool,
        require_zpkg: bool,
        enforce_canonical_flags_source: bool,
        enforce_generated_cargo_version: bool,
        require_no_dotenv: bool,
        require_strict_cli_channels: bool,
    ) -> None:
        self.root = root.resolve()
        self.repository = repository
        self.require_cli_flags = require_cli_flags
        self.require_zpkg = require_zpkg
        self.enforce_canonical_flags_source = enforce_canonical_flags_source
        self.enforce_generated_cargo_version = enforce_generated_cargo_version
        self.require_no_dotenv = require_no_dotenv
        self.require_strict_cli_channels = require_strict_cli_channels
        self.findings: list[Finding] = []
        self.documents: dict[Path, dict[str, Any]] = {}

    def fail(self, path: Path | str, message: str) -> None:
        candidate = Path(path) if not isinstance(path, Path) else path
        try:
            display = candidate.resolve().relative_to(self.root).as_posix()
        except (OSError, ValueError):
            display = str(path)
        self.findings.append(Finding(display or ".", message))

    def run(self) -> dict[str, Any]:
        if not self.root.is_dir():
            self.fail(self.root, "audit root is not a directory")
            return self.report()

        paths = list(self._toml_paths())
        for path in paths:
            document = self._load_toml(path)
            if document is not None:
                self.documents[path] = document

        zpkg_path = self.root / ".zpkg.toml"
        cli_path = self.root / ".cli-flags.toml"
        if self.require_zpkg and zpkg_path not in self.documents:
            self.fail(zpkg_path, "required .zpkg.toml is missing or invalid")
        if self.require_cli_flags and cli_path not in self.documents:
            self.fail(cli_path, "required .cli-flags.toml is missing or invalid")

        zpkg = self.documents.get(zpkg_path)
        if zpkg is not None:
            self._audit_zpkg(zpkg_path, zpkg)
        cli = self.documents.get(cli_path)
        if cli is not None:
            self._audit_cli_flags(cli_path, cli)
        self._audit_cargo_manifests(zpkg)
        if self.enforce_canonical_flags_source:
            self._audit_flags_source()
        return self.report()

    def report(self) -> dict[str, Any]:
        ordered = sorted(self.findings, key=lambda item: (item.path, item.message))
        return {
            "status": "passed" if not ordered else "failed",
            "root": str(self.root),
            "toml_files": len(self.documents),
            "finding_count": len(ordered),
            "findings": [item.__dict__ for item in ordered],
        }

    def _toml_paths(self) -> Iterable[Path]:
        seen: set[Path] = set()
        for path in self.root.rglob("*.toml"):
            if any(part in IGNORED_PARTS for part in path.relative_to(self.root).parts):
                continue
            seen.add(path)
        lock = self.root / ".zpkg.lock"
        if lock.exists() or lock.is_symlink():
            seen.add(lock)
        yield from sorted(seen)

    def _load_toml(self, path: Path) -> dict[str, Any] | None:
        if path.is_symlink():
            self.fail(path, "TOML contract must not be a symbolic link")
            return None
        if not path.is_file():
            self.fail(path, "TOML contract is not a regular file")
            return None
        try:
            size = path.stat().st_size
        except OSError as error:
            self.fail(path, f"cannot stat TOML contract: {error.__class__.__name__}")
            return None
        if size > MAX_TOML_BYTES:
            self.fail(path, f"TOML contract exceeds {MAX_TOML_BYTES} bytes")
            return None
        try:
            with path.open("rb") as handle:
                value = tomllib.load(handle)
        except (OSError, tomllib.TOMLDecodeError) as error:
            self.fail(path, f"cannot parse TOML: {error}")
            return None
        if not isinstance(value, dict):
            self.fail(path, "top-level TOML value must be a table")
            return None
        return value

    def _audit_zpkg(self, path: Path, document: dict[str, Any]) -> None:
        package = document.get("package")
        if not isinstance(package, dict):
            self.fail(path, "missing [package] table")
            return
        org = self._required_string(path, package, "org", "[package]")
        name = self._required_string(path, package, "name", "[package]")
        self._required_string(path, package, "version", "[package]")
        repository_table = package.get("repository")
        if not isinstance(repository_table, dict):
            self.fail(path, "missing [package.repository] table")
        else:
            repository_url = self._required_string(
                path, repository_table, "url", "[package.repository]"
            )
            if repository_url and self.repository:
                expected = f"https://github.com/{self.repository}".lower()
                actual = repository_url.rstrip("/")
                if actual.endswith(".git"):
                    actual = actual[:-4]
                if actual.lower() != expected:
                    self.fail(
                        path,
                        f"package repository URL must be {expected}, found {actual}",
                    )
        if self.repository and org and name:
            expected_org, separator, expected_name = self.repository.partition("/")
            if not separator:
                self.fail(path, "repository identity must be owner/name")
            else:
                if org != expected_org:
                    self.fail(path, f"package.org must be {expected_org}")
                if name != expected_name:
                    self.fail(path, f"package.name must be {expected_name}")

        lock_path = self.root / ".zpkg.lock"
        lock = self.documents.get(lock_path)
        if lock is None:
            self.fail(lock_path, "Zed package manifest requires a parsed .zpkg.lock")
        else:
            if lock.get("version") != 1:
                self.fail(lock_path, "lockfile version must be exactly 1")
            dependencies = document.get("dependencies", {})
            if not isinstance(dependencies, dict):
                self.fail(path, "[dependencies] must be a table")
                dependencies = {}
            packages = lock.get("package", [])
            if packages is None:
                packages = []
            if not isinstance(packages, list):
                self.fail(lock_path, "[[package]] entries must be an array of tables")
                packages = []
            locked: set[str] = set()
            for index, item in enumerate(packages):
                if not isinstance(item, dict):
                    self.fail(lock_path, f"package entry {index} is not a table")
                    continue
                item_org = item.get("org")
                item_name = item.get("name")
                identity = f"package[{index}]"
                if isinstance(item_org, str) and isinstance(item_name, str):
                    identity = f"{item_org}/{item_name}"
                    if identity in locked:
                        self.fail(lock_path, f"duplicate locked package {identity}")
                    locked.add(identity)
                self._audit_locked_package(lock_path, item, identity)
            for dependency in dependencies:
                if not isinstance(dependency, str) or "/" not in dependency:
                    self.fail(path, f"invalid Zed dependency key {dependency!r}")
                elif dependency not in locked:
                    self.fail(
                        lock_path,
                        f"direct dependency {dependency} is absent from .zpkg.lock",
                    )

        targets = document.get("targets", {})
        if not isinstance(targets, dict):
            self.fail(path, "[targets.*] entries must form a table")
            targets = {}
        if targets:
            repository_target = targets.get("repository")
            if not isinstance(repository_target, dict):
                self.fail(
                    path,
                    'targeted package must declare [targets.repository] with dir = "."',
                )
            else:
                if repository_target.get("dir") != ".":
                    self.fail(path, '[targets.repository].dir must be "."')
                root_name = repository_target.get("name")
                if root_name not in (None, name):
                    self.fail(
                        path,
                        "root repository target name must be omitted or equal package.name",
                    )
            for target_name, target in targets.items():
                if not isinstance(target, dict):
                    self.fail(path, f"target {target_name} must be a table")
                    continue
                directory = target.get("dir")
                if not isinstance(directory, str) or not self._safe_relative(directory):
                    self.fail(path, f"target {target_name} has unsafe dir {directory!r}")
                    continue
                if directory == "." and target_name != "repository":
                    self.fail(
                        path,
                        "only targets.repository may use the whole-repository dir",
                    )
                target_path = self.root if directory == "." else self.root / directory
                if not target_path.is_dir():
                    self.fail(path, f"target {target_name} directory is missing: {directory}")

        self._audit_smoke_test(path, document)
        self._audit_lifecycle_paths(path, document)
        self._audit_zed_interop(path, document)

    def _audit_locked_package(
        self, path: Path, item: dict[str, Any], identity: str
    ) -> None:
        for key in ("org", "name", "version", "format", "vcs_tag", "vcs_commit", "source"):
            value = item.get(key)
            if not isinstance(value, str) or not value.strip():
                self.fail(path, f"locked package {identity} requires non-empty {key}")
        digest = item.get("sha256")
        if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
            self.fail(path, f"locked package {identity} requires canonical sha256")
        elif set(digest) == {"0"}:
            self.fail(path, f"locked package {identity} sha256 must not be all zeroes")
        size = item.get("size")
        if not isinstance(size, int) or isinstance(size, bool) or size < 1:
            self.fail(path, f"locked package {identity} size must be a positive integer")
        commit = item.get("vcs_commit")
        if isinstance(commit, str) and commit.strip():
            immutable = bool(
                re.fullmatch(r"[0-9a-f]{40}", commit)
                or re.fullmatch(r"artifact-sha256:[0-9a-f]{64}", commit)
            )
            if not immutable:
                self.fail(
                    path,
                    f"locked package {identity} vcs_commit must be a full commit or artifact digest",
                )

    def _audit_smoke_test(self, path: Path, document: dict[str, Any]) -> None:
        publish = document.get("publish", {})
        if not isinstance(publish, dict):
            self.fail(path, "[publish] must be a table")
            return
        smoke = publish.get("smoke_test")
        excludes = publish.get("exclude", [])
        if smoke is None:
            return
        if not isinstance(smoke, str) or not smoke.strip():
            self.fail(path, "publish.smoke_test must be a non-empty string")
            return
        if not isinstance(excludes, list) or not all(isinstance(item, str) for item in excludes):
            self.fail(path, "publish.exclude must be an array of strings")
            return
        references = re.findall(r"\$\{?ZED_PKG_TEST_TARGET\}?/([A-Za-z0-9._/+-]+)", smoke)
        for reference in references:
            for pattern in excludes:
                if self._matches_exclude(reference, pattern):
                    self.fail(
                        path,
                        f"publish smoke test references excluded path {reference!r} via {pattern!r}",
                    )

    @staticmethod
    def _matches_exclude(path: str, pattern: str) -> bool:
        normalized = pattern.removeprefix("./")
        if fnmatch.fnmatch(path, normalized):
            return True
        if normalized.endswith("/**"):
            prefix = normalized[:-3].rstrip("/")
            return path == prefix or path.startswith(prefix + "/")
        return False

    def _audit_lifecycle_paths(self, path: Path, document: dict[str, Any]) -> None:
        lifecycle = document.get("lifecycle", {})
        if lifecycle is None:
            return
        if not isinstance(lifecycle, dict):
            self.fail(path, "[lifecycle.*] entries must form a table")
            return
        for phase, config in lifecycle.items():
            if not isinstance(config, dict):
                self.fail(path, f"lifecycle phase {phase} must be a table")
                continue
            command = config.get("command")
            if not isinstance(command, str) or not command.strip():
                self.fail(path, f"lifecycle phase {phase} needs a command")
                continue
            match = re.search(r"(?:^|\s)(?:sh|bash)\s+['\"]?(\./[^'\"\s]+)", command)
            if not match:
                continue
            relative = match.group(1).removeprefix("./")
            if not self._safe_relative(relative):
                self.fail(path, f"lifecycle phase {phase} uses unsafe path {relative!r}")
                continue
            candidate = self.root / relative
            if candidate.is_symlink() or not candidate.is_file():
                self.fail(path, f"lifecycle phase {phase} references missing regular file {relative}")

    def _audit_zed_interop(self, path: Path, document: dict[str, Any]) -> None:
        bins = document.get("bin", {})
        if bins is None:
            bins = {}
        if not isinstance(bins, dict):
            self.fail(path, "[bin] must be a table")
            bins = {}
        for name, value in bins.items():
            if not isinstance(value, str) or not self._safe_relative(value):
                self.fail(path, f"bin {name} has unsafe path {value!r}")
                continue
            candidate = self.root / value
            if candidate.is_symlink() or not candidate.is_file():
                self.fail(path, f"bin {name} references missing regular file {value}")

        interop = document.get("interop", {})
        if not isinstance(interop, dict):
            return
        flags = interop.get("flags-2-env")
        if flags is None:
            flags = interop.get("flags2env")
        if flags is None:
            return
        if not isinstance(flags, dict):
            self.fail(path, "[interop.flags-2-env] must be a table")
            return
        config = flags.get("config")
        declared_bins = flags.get("bins", [])
        if not isinstance(config, str) or not self._safe_relative(config):
            self.fail(path, "flags-2-env interop config must be a safe relative path")
        elif not (self.root / config).is_file():
            self.fail(path, f"flags-2-env interop config is missing: {config}")
        if not isinstance(declared_bins, list) or not all(
            isinstance(item, str) for item in declared_bins
        ):
            self.fail(path, "flags-2-env interop bins must be an array of strings")
        else:
            for name in declared_bins:
                if name not in bins:
                    self.fail(path, f"flags-2-env interop names undeclared bin {name}")

    def _audit_cli_flags(self, path: Path, document: dict[str, Any]) -> None:
        parse = document.get("parse", {})
        if not isinstance(parse, dict):
            self.fail(path, "[parse] must be a table")
        elif parse.get("allow_unknown") is not False:
            self.fail(path, "parse.allow_unknown must be false")

        help_table = document.get("help", {})
        if not isinstance(help_table, dict):
            self.fail(path, "[help] must be a table")
        else:
            help_url = help_table.get("url")
            if not isinstance(help_url, str) or urlparse(help_url).scheme != "https":
                self.fail(path, "help.url must be an HTTPS URL")
            elif self.repository:
                expected_prefix = f"https://github.com/{self.repository}".lower()
                parsed = urlparse(help_url)
                base = f"{parsed.scheme}://{parsed.netloc}{parsed.path}".rstrip("/").lower()
                if base == expected_prefix and parsed.fragment:
                    readme = self.root / "README.md"
                    if not readme.is_file():
                        self.fail(path, "local help URL fragment requires README.md")
                    else:
                        headings = self._readme_anchors(readme)
                        if parsed.fragment.lower() not in headings:
                            self.fail(
                                path,
                                f"help URL fragment #{parsed.fragment} is absent from README.md",
                            )

        envs: dict[str, str] = {}
        self._audit_flag_scope(path, document.get("flags", {}), "flags", envs)
        commands = document.get("commands", {})
        if commands is not None:
            if not isinstance(commands, dict):
                self.fail(path, "[commands.*] entries must form a table")
            else:
                self._audit_commands(path, commands, "commands", envs)

        env_table = document.get("env")
        if env_table is not None:
            if not isinstance(env_table, dict):
                self.fail(path, "[env] must be a table")
            else:
                files = env_table.get("files")
                if files is not None:
                    if not isinstance(files, list) or not all(
                        isinstance(item, str) and self._safe_relative(item)
                        for item in files
                    ):
                        self.fail(path, "env.files must contain only safe relative paths")
        if self.require_no_dotenv:
            if not isinstance(env_table, dict):
                self.fail(path, "strict secret boundary requires an [env] table")
            else:
                files = env_table.get("files")
                load = env_table.get("load")
                if files != [] and load is not False:
                    self.fail(
                        path,
                        "strict secret boundary requires env.files = [] or env.load = false",
                    )

        if self.require_strict_cli_channels:
            if not isinstance(parse, dict):
                return
            channel_envs: set[str] = set()
            for key in ("positionals_env", "unknown_options_env", "errors_env"):
                value = parse.get(key)
                if not isinstance(value, str) or not re.fullmatch(r"[A-Z][A-Z0-9_]*", value):
                    self.fail(path, f"parse.{key} must be an uppercase env key")
                    continue
                if value in channel_envs or value in envs:
                    self.fail(path, f"parse.{key} env {value} is not unique")
                channel_envs.add(value)

    def _audit_commands(
        self,
        path: Path,
        commands: dict[str, Any],
        prefix: str,
        envs: dict[str, str],
    ) -> None:
        names: set[str] = set()
        aliases: set[str] = set()
        for command_name, command in commands.items():
            if not isinstance(command, dict):
                self.fail(path, f"{prefix}.{command_name} must be a table")
                continue
            if command_name in names:
                self.fail(path, f"duplicate command {prefix}.{command_name}")
            names.add(command_name)
            command_aliases = command.get("aliases", [])
            if command_aliases is not None:
                if not isinstance(command_aliases, list) or not all(
                    isinstance(item, str) and item for item in command_aliases
                ):
                    self.fail(path, f"{prefix}.{command_name}.aliases must be strings")
                else:
                    for alias in command_aliases:
                        if alias in names or alias in aliases:
                            self.fail(path, f"duplicate command alias {alias} in {prefix}")
                        aliases.add(alias)
            self._audit_flag_scope(
                path,
                command.get("flags", {}),
                f"{prefix}.{command_name}.flags",
                envs,
            )
            children = command.get("commands")
            if children is not None:
                if not isinstance(children, dict):
                    self.fail(path, f"{prefix}.{command_name}.commands must be a table")
                else:
                    self._audit_commands(
                        path,
                        children,
                        f"{prefix}.{command_name}.commands",
                        envs,
                    )

    def _audit_flag_scope(
        self,
        path: Path,
        flags: Any,
        prefix: str,
        envs: dict[str, str],
    ) -> None:
        if flags is None:
            return
        if not isinstance(flags, dict):
            self.fail(path, f"[{prefix}.*] entries must form a table")
            return
        aliases: set[str] = set()
        shorts: set[str] = set()
        for flag_name, flag in flags.items():
            if not isinstance(flag, dict):
                self.fail(path, f"{prefix}.{flag_name} must be a table")
                continue
            env = flag.get("env")
            if not isinstance(env, str) or not re.fullmatch(r"[A-Z][A-Z0-9_]*", env):
                self.fail(path, f"{prefix}.{flag_name}.env must be an uppercase env key")
            elif env in envs:
                self.fail(
                    path,
                    f"env {env} is shared by {envs[env]} and {prefix}.{flag_name}",
                )
            else:
                envs[env] = f"{prefix}.{flag_name}"
            kind = flag.get("type")
            if not isinstance(kind, str) or kind.lower() not in ALLOWED_FLAG_TYPES:
                self.fail(path, f"{prefix}.{flag_name}.type is unsupported: {kind!r}")
            values = flag.get("aliases", [])
            if not isinstance(values, list) or not values or not all(
                isinstance(item, str) and item for item in values
            ):
                self.fail(path, f"{prefix}.{flag_name}.aliases must be non-empty strings")
            else:
                for alias in values:
                    if alias in aliases:
                        self.fail(path, f"duplicate flag alias {alias} in {prefix}")
                    aliases.add(alias)
            short = flag.get("short")
            if short is not None:
                if not isinstance(short, str) or len(short) != 1:
                    self.fail(path, f"{prefix}.{flag_name}.short must be one character")
                elif short in shorts:
                    self.fail(path, f"duplicate short flag {short} in {prefix}")
                else:
                    shorts.add(short)

    def _audit_cargo_manifests(self, zpkg: dict[str, Any] | None) -> None:
        zpkg_version = None
        if isinstance(zpkg, dict):
            package = zpkg.get("package")
            if isinstance(package, dict) and isinstance(package.get("version"), str):
                zpkg_version = package["version"]
        for path, document in self.documents.items():
            if path.name != "Cargo.toml":
                continue
            package = document.get("package")
            if not isinstance(package, dict):
                continue
            if "generated" in path.relative_to(self.root).parts:
                if package.get("publish") is not False:
                    self.fail(path, "generated Cargo package must set publish = false")
                if self.enforce_generated_cargo_version and zpkg_version:
                    if package.get("version") != zpkg_version:
                        self.fail(
                            path,
                            f"generated Cargo version must equal Zed package version {zpkg_version}",
                        )

    def _audit_flags_source(self) -> None:
        flake = self.root / "flake.nix"
        if flake.is_file():
            text = flake.read_text(encoding="utf-8", errors="replace")
            if re.search(r"github:ORESoftware/flags-2-env(?:/|\")", text, re.I):
                self.fail(
                    flake,
                    "new source references must use github:flags-2-env/flags-2-env",
                )
        lock = self.root / "flake.lock"
        if lock.is_file():
            try:
                value = json.loads(lock.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as error:
                self.fail(lock, f"cannot parse flake.lock JSON: {error}")
                return
            nodes = value.get("nodes", {}) if isinstance(value, dict) else {}
            if isinstance(nodes, dict):
                for node_name, node in nodes.items():
                    if not isinstance(node, dict):
                        continue
                    for section_name in ("locked", "original"):
                        section = node.get(section_name)
                        if not isinstance(section, dict):
                            continue
                        if str(section.get("repo", "")).lower() == "flags-2-env":
                            owner = str(section.get("owner", ""))
                            if owner.lower() != "flags-2-env":
                                self.fail(
                                    lock,
                                    f"node {node_name}.{section_name} must use owner flags-2-env",
                                )

    def _required_string(
        self, path: Path, table: dict[str, Any], key: str, table_name: str
    ) -> str | None:
        value = table.get(key)
        if not isinstance(value, str) or not value.strip():
            self.fail(path, f"{table_name}.{key} must be a non-empty string")
            return None
        return value.strip()

    @staticmethod
    def _safe_relative(value: str) -> bool:
        if not value or "\\" in value or value.startswith("/"):
            return False
        if value == ".":
            return True
        path = PurePosixPath(value)
        return not path.is_absolute() and ".." not in path.parts and "." not in path.parts

    @staticmethod
    def _readme_anchors(path: Path) -> set[str]:
        anchors: set[str] = set()
        counts: dict[str, int] = {}
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            match = re.match(r"^#{1,6}\s+(.+?)\s*#*\s*$", line)
            if not match:
                continue
            text = re.sub(r"<[^>]+>", "", match.group(1)).strip().lower()
            text = re.sub(r"[^\w\- ]", "", text, flags=re.UNICODE)
            slug = re.sub(r"[\s-]+", "-", text).strip("-")
            count = counts.get(slug, 0)
            counts[slug] = count + 1
            anchors.add(slug if count == 0 else f"{slug}-{count}")
        return anchors


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--repository", default=os.environ.get("GITHUB_REPOSITORY"))
    parser.add_argument("--require-cli-flags", action="store_true")
    parser.add_argument("--require-zpkg", action="store_true")
    parser.add_argument("--enforce-canonical-flags-source", action="store_true")
    parser.add_argument("--enforce-generated-cargo-version", action="store_true")
    parser.add_argument("--require-no-dotenv", action="store_true")
    parser.add_argument("--require-strict-cli-channels", action="store_true")
    parser.add_argument("--json", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    auditor = Auditor(
        Path(args.root),
        repository=args.repository,
        require_cli_flags=args.require_cli_flags,
        require_zpkg=args.require_zpkg,
        enforce_canonical_flags_source=args.enforce_canonical_flags_source,
        enforce_generated_cargo_version=args.enforce_generated_cargo_version,
        require_no_dotenv=args.require_no_dotenv,
        require_strict_cli_channels=args.require_strict_cli_channels,
    )
    report = auditor.run()
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    elif report["status"] == "passed":
        print(f"toml-contract-audit: passed ({report['toml_files']} TOML files)")
    else:
        for finding in report["findings"]:
            print(
                f"toml-contract-audit: {finding['path']}: {finding['message']}",
                file=sys.stderr,
            )
        print(
            f"toml-contract-audit: failed with {report['finding_count']} finding(s)",
            file=sys.stderr,
        )
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
