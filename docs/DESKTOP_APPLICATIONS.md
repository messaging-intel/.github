# Desktop application allocation

Verified **2026-08-06**.

Messaging Intel uses the paired desktop application standard:

- Rust: [`messaging-intel/msgint-desktop.rs`](https://github.com/messaging-intel/msgint-desktop.rs) — **planned**, not yet verified as a published repository.
- Flutter, current: [`messaging-intel/msgint-flutter-app`](https://github.com/messaging-intel/msgint-flutter-app) — **live**, with current native desktop coverage verified for macOS.
- Flutter canonical rename target: `messaging-intel/msgint-flutter` — planned naming normalization; do not describe as published until renamed and verified.

Linux and Windows support must be validated per lawful connector and browser-automation integration rather than inferred.

## Why both Rust and Flutter remain active

The Rust and Flutter apps remain first-class side-by-side implementations so the product can compare local privacy, performance on large message/thread datasets, keyboard workflows, OS integration, mobile reuse, accessibility, release engineering, and developer velocity with the same feature set.

Every desktop-facing change must inspect both implementations, share acceptance criteria and redacted/synthetic fixtures, and normally update both. A one-sided change requires a documented no-change rationale and parity gap.

## Rust desktop kit: GPUI

**Selected strategy:** GPUI from the Zed project.

**WebView policy:** prohibited for the Rust desktop app.

Messaging Intel is a high-density, keyboard-oriented analysis application handling private local data, message/thread lists, identity review, and connector state. GPUI provides a native Rust productivity UI without embedding another browser surface. Privileged connector and session behavior remains outside the UI layer behind explicit Rust interfaces.

The Rust repository must contain `docs/DESKTOP_TOOLKIT.md` describing the GPUI version policy, platform adapters, privacy boundary, data virtualization, deep links, tests, packaging, and Flutter companion. If a target capability is blocked, changing toolkit or adding a WebView requires an ADR.

## HTTPS-first deep linking

Canonical form:

```text
https://<verified-messaging-intel-owned-host>/open/<route>?<bounded-query>
```

Fallback scheme:

```text
msgint://<route>?<bounded-query>
```

Routes belong in `msgint-interfaces` and must be shared by Rust, Flutter, clients, connectors, and the browser fallback.

Required behavior:

- support cold start and already-running/single-instance delivery;
- validate the exact host, route, thread/contact/review identifiers, action, and bounded query parameters;
- never place account sessions, cookies, credentials, message bodies, contact data, private media, or bearer tokens in URLs;
- use short-lived, one-time, audience-bound codes for sign-in and connector handoffs;
- require explicit user confirmation before opening externally referenced conversations or importing data;
- preserve pending routes safely through authentication; and
- test macOS, Windows, Linux, Android, and iOS app/universal links plus browser fallback.

GPUI receives OS URL events through narrow platform modules; the shared Rust route parser validates them before any connector or local-data operation.

## Product boundary

Both implementations should support semantic parity for account/session state, lawful browser/connector integration, thread/contact data, identity normalization, human-review queues, notifications, privacy controls, audit evidence, local storage, recovery, and deep links.

Shared schemas, clients, route fixtures, synthetic/redacted data, connector capability matrices, and conformance tests must be versioned deliberately.

## Repository-local documentation

The live Flutter repository records the companion contract in [`COMPANION_DESKTOP.md`](https://github.com/messaging-intel/msgint-flutter-app/blob/main/COMPANION_DESKTOP.md), introduced through [PR #13](https://github.com/messaging-intel/msgint-flutter-app/pull/13).

Central toolkit assignments: [`rust-desktop-strategies.md`](https://github.com/ORESoftware/project-registry/blob/main/docs/rust-desktop-strategies.md).

## Project routing

- GitHub Project: [`messaging-intel-project` — Project 1](https://github.com/orgs/messaging-intel/projects/1)
- Linear project: `github.com/messaging-intel`
- Central registry: [`approved-private-registry`](private-registry://canonical/registry/desktop-applications.json)
- Portfolio rollout: [`DEN-2469`](https://linear.app/denman/issue/DEN-2469/roll-out-paired-rust-flutter-desktop-repositories-across-the-portfolio)

Repository creation, Flutter renaming, toolkit changes, deep-link changes, connector changes, transfers, archival, or platform-status changes must update this document, Linear, the central registry/strategy, and both companion repositories together.
