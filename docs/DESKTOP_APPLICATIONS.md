# Desktop application allocation

Verified **2026-08-05**.

Messaging Intel uses the paired native desktop application standard:

- Rust: [`messaging-intel/msgint-desktop.rs`](https://github.com/messaging-intel/msgint-desktop.rs) — **planned**, not yet verified as a published repository.
- Flutter: [`messaging-intel/msgint-flutter-app`](https://github.com/messaging-intel/msgint-flutter-app) — **live**, with current native desktop coverage verified for macOS.

The Rust URL is an allocation target, not proof that the remote exists. Linux and Windows status must be validated per connector and browser-automation integration before it is claimed.

The live Flutter repository records the companion contract in [`COMPANION_DESKTOP.md`](https://github.com/messaging-intel/msgint-flutter-app/blob/main/COMPANION_DESKTOP.md), merged through [PR #13](https://github.com/messaging-intel/msgint-flutter-app/pull/13).

## Product boundary

Both implementations should support semantic parity for account and session state, browser/connector integration, thread and contact data, identity normalization, human-review queues, notifications, privacy controls, audit evidence, local storage, and recovery behavior.

The Rust and Flutter implementations remain independently buildable, testable, releasable applications. Shared schemas, clients, redacted fixtures, connector capabilities, platform matrices, and conformance tests should be versioned deliberately.

## Feature-delivery rule

Every desktop-facing change must inspect both implementations, define shared acceptance criteria, update both or record an explicit no-change rationale, and report Rust and Flutter status separately for macOS, Linux, and Windows. Platform support is connector-specific and must not be inferred.

## Project routing

- GitHub Project: [`messaging-intel-project` — Project 1](https://github.com/orgs/messaging-intel/projects/1)
- Linear project: `github.com/messaging-intel`
- Central registry: [`approved-private-registry`](private-registry://canonical/registry/desktop-applications.json)
- Portfolio rollout: [`DEN-2469`](https://linear.app/denman/issue/DEN-2469/roll-out-paired-rust-flutter-desktop-repositories-across-the-portfolio)

Repository creation, renames, transfers, archival, connector changes, or platform-status changes must update this document, Linear, the central registry, and both companion repositories together.
