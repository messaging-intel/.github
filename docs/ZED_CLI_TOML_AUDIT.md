# Zed and CLI TOML audit

- **Tracking:** Linear `DEN-604`, `DEN-3903`, and Messaging Intel `.github#25`
- **Owner:** Messaging Intel interface and package governance
- **Status:** reusable static and compiler-backed admission tooling

## Purpose

This repository publishes a reusable, fail-closed audit for repositories that use
Zed package metadata, flags-2-env command contracts, generated Cargo packages,
or Nix-pinned flags-2-env source.

The audit complements, rather than replaces, the canonical upstream tools:

- `zed-pkg/zed-interfaces` parses and packs `.zpkg.toml` and `.zpkg.lock`;
- `flags-2-env/flags-2-env` performs the canonical `.cli-flags.toml` audit;
- `scripts/audit_zed_cli_toml.py` checks repository-level relationships that a
  parser for one file cannot establish by itself.

## Repository relationships checked

The bounded Python audit parses every in-scope `*.toml` file plus `.zpkg.lock`
and rejects, among other things:

- a missing or unsupported Zed lockfile;
- direct Zed dependencies absent from the lock;
- incomplete, mutable, duplicate, or malformed locked-package identities;
- a missing canonical `[targets.repository]` root target;
- a root target name that differs from `package.name`;
- a non-repository target using `dir = "."`;
- missing or unsafe target, lifecycle, binary, or flags-2-env paths;
- a package smoke test that references a path excluded from the package;
- malformed flag scopes, duplicate aliases/shorts/envs, unsupported types, or
  a non-HTTPS/broken repository help anchor;
- optional strict-mode failures for dotenv discovery and missing parse channels;
- generated Cargo packages that are publishable or version-drifted from Zed;
- new Nix references to the retired `ORESoftware/flags-2-env` source.

The workflow then runs the exact pinned flags-2-env parser over the command
contract and, when requested, the exact pinned Zed package validator and packer.
A Python pass alone is not a Zed package certification.

## Reusable workflow

Call the workflow by an immutable commit SHA:

```yaml
jobs:
  toml-contracts:
    uses: messaging-intel/.github/.github/workflows/reusable-zed-cli-toml-audit.yml@<40-character-sha>
    with:
      tooling_ref: <same-40-character-sha>
      flags2env_ref: 333c2ace93c362d274171ab0e0edf613d96a8e59
      require_cli_flags: true
      require_zpkg: true
      require_no_dotenv: true
      require_strict_cli_channels: true
      enforce_canonical_flags_source: true
      enforce_generated_cargo_version: true
```

`tooling_ref` and `flags2env_ref` must both be full immutable lowercase commit
SHAs. A consumer must update the workflow reference and `tooling_ref` together.

## Evidence boundary

The retained receipt contains paths and bounded finding messages, not TOML file
contents, environment values, dependency credentials, registry tokens, or
participant data. A missing runner, skipped required job, unavailable private
dependency, or failed upstream validator remains blocked evidence rather than a
pass.
