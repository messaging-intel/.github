# Desktop application allocation

Verified **2026-08-06**.

Messaging Intel requires a paired, high-performance native desktop program:

- Rust: [`messaging-intel/msgint-desktop.rs`](https://github.com/messaging-intel/msgint-desktop.rs) — **planned**, not yet verified as a published repository.
- Flutter canonical target: [`messaging-intel/msgint-flutter`](https://github.com/messaging-intel/msgint-flutter) — **planned**, not yet verified as a published repository.
- Flutter current implementation: [`messaging-intel/msgint-flutter-app`](https://github.com/messaging-intel/msgint-flutter-app) — **live transitional repository**, currently with verified macOS desktop coverage.

The canonical target names are allocation and migration targets, not proof that the remotes exist. Until the Flutter rename or migration is verified, `msgint-flutter-app` remains the active Flutter implementation and must continue receiving desktop feature work and parity review.

## Why both Rust and Flutter remain active

The Rust and Flutter apps are first-class side-by-side implementations so Messaging Intel can compare native rendering performance, privacy boundaries, large message/thread datasets, keyboard workflows, Chrome integration, OS integration, mobile reuse, accessibility, release engineering, and developer velocity using the same real features.

Every desktop-facing change must inspect both implementations, share acceptance criteria, routes, schemas, Chrome protocol fixtures, and synthetic/redacted datasets, and normally update both. A one-sided change requires a documented no-change rationale, parity assessment, and follow-up issue. Completion in one repository is not full desktop completion.

Every future `msgint-desktop.rs` README, `AGENTS.md`, pull-request template, and `docs/DESKTOP_TOOLKIT.md` must state that Rust and Flutter development proceeds in parallel unless an explicit, reviewed exception applies.

## Rust desktop kit: Makepad native runtime

**Selected strategy:** Makepad native Rust UI.

**WebView policy:** prohibited.

The desktop application must use Makepad's native GPU-backed desktop targets. It must not ship through Makepad's WASM/web target and must not embed WebKit, WebView2, Chromium, or another browser renderer.

Makepad is selected for high-density native rendering, custom GPU surfaces, fast message/thread navigation, keyboard-first workflows, and a Rust-owned process boundary. Pin an exact reviewed Makepad revision or release. Upgrades require native macOS, Windows, and Linux build, rendering, input, accessibility, packaging, and deep-link evidence.

Rust owns:

- connector session and authorization state;
- local persistence, privacy controls, workspace isolation, and audit evidence;
- message/thread/contact/review models and validation;
- Chrome Native Messaging protocol handling;
- deep-link parsing, replay protection, and authorization;
- secure storage, networking, and all privileged operations.

Makepad owns native presentation, virtualized lists, GPU rendering, keyboard navigation, and windowing. Sensitive session, cookie, message, contact, or credential data must never be serialized into UI markup or logs.

The upstream framework authority is https://github.com/makepad/makepad.

## Chrome app-to-app interoperability

Messaging Intel must interoperate with Chrome through a reviewed extension bridge, not by embedding Chrome or a WebView.

### Native Messaging host

- Install an exact Chrome Native Messaging host manifest with a stable lowercase/dotted host name and an explicit `allowed_origins` list.
- Wildcard extension origins are prohibited.
- Use Chrome's length-prefixed UTF-8 JSON protocol over stdin/stdout.
- Use bounded messages, schema versions, request IDs, capability negotiation, timeouts, size limits, and audit-safe errors.
- Write diagnostics only to stderr; stdout is reserved for the native messaging protocol.
- Validate the caller extension ID, workspace, user, action, object identifiers, authorization, and explicit user intent.
- Treat content-script and extension messages as untrusted input.

The Rust Makepad application may host the protocol directly or through a small signed native-host binary in the same workspace. The Flutter application must consume the same Rust protocol crate through a signed native host and OS-protected local IPC, or use a one-time deep-link handoff for user-directed navigation. Unauthenticated loopback TCP services are prohibited.

Use native messaging for bounded structured operations. Use HTTPS or `msgint://` links for user-directed navigation. Never pass raw account sessions, cookies, browser storage, message bodies, contact exports, private media, credentials, bearer tokens, or connector secrets through either channel.

The Chrome extension, Makepad app, and Flutter app must pass the same protocol-version, authorization, replay, size-limit, malformed-message, and route fixtures. The Chrome platform reference is https://developer.chrome.com/docs/extensions/develop/concepts/native-messaging.

## HTTPS-first deep linking

Canonical form:

```text
https://<verified-messaging-intel-owned-host>/open/<route>?<bounded-query>
```

Fallback scheme:

```text
msgint://<route>?<bounded-query>
```

The production host must not be guessed. Routes belong in `msgint-interfaces` and must be shared by Rust, Flutter, generated clients, the Chrome extension, native host, connectors, and browser fallback pages.

Required behavior:

- support cold start and already-running/single-instance delivery;
- preserve only a validated pending route through authentication;
- validate the exact HTTPS host, route version, workspace/thread/contact/review identifier, action, and bounded query values;
- reject unknown routes, duplicate security-sensitive parameters, ambiguous encodings, unsafe return URLs, replay, expiry, and unauthorized workspace/object access;
- use short-lived, single-use, audience-bound codes for sign-in, browser-extension, connector, import, and share handoffs;
- require explicit confirmation before opening externally referenced conversations, importing data, changing connector state, or revealing sensitive content;
- provide a browser fallback when the app is absent; and
- test macOS, Windows, Linux, Android, and iOS app/universal links plus Chrome-to-native behavior.

Account sessions, cookies, credentials, message bodies, contact data, private media, bearer/refresh tokens, and encryption keys are prohibited in URLs.

## Product boundary

Both implementations should support semantic parity for account/session state, lawful browser and connector integration, thread/contact data, identity normalization, human-review queues, notifications, privacy controls, audit evidence, local storage, recovery, Chrome interoperability, and deep links.

Shared schemas, clients, route fixtures, native-messaging fixtures, synthetic/redacted data, connector capability matrices, and conformance tests must be versioned deliberately.

## Repository creation and migration requirements

`msgint-desktop.rs` and `msgint-flutter` must be buildable repositories, not placeholders.

The Rust repository must include:

- `docs/DESKTOP_TOOLKIT.md` with the Makepad pin, no-WebView rule, Chrome bridge, deep links, platform matrix, and Flutter companion;
- a README naming `msgint-flutter` and stating that Rust and Flutter features are developed in parallel unless explicitly exempted;
- `AGENTS.md` and a pull-request template requiring companion inspection and no-change rationale;
- native macOS/Windows/Linux CI and packaging skeletons;
- Chrome native-host manifest generation and installer tests;
- deep-link, native-messaging, privacy, replay, and synthetic-data smoke tests.

The Flutter rename or migration must preserve history, package identity, signing/release configuration, tests, and reciprocal links. Do not archive `msgint-flutter-app` or mark `msgint-flutter` live until cutover is verified.

## Project routing

- GitHub Project: [`messaging-intel-project` — Project 1](https://github.com/orgs/messaging-intel/projects/1)
- Linear project: `github.com/messaging-intel`
- Central registry: [`ORESoftware/project-registry`](https://github.com/ORESoftware/project-registry/blob/main/registry/desktop-applications.json)
- Central strategy: [`rust-desktop-strategies.md`](https://github.com/ORESoftware/project-registry/blob/main/docs/rust-desktop-strategies.md)
- Portfolio rollout: [`DEN-2469`](https://linear.app/denman/issue/DEN-2469/roll-out-paired-rust-flutter-desktop-repositories-across-the-portfolio)

Repository creation, Flutter migration, toolkit changes, Chrome protocol changes, deep-link changes, connector changes, transfers, archival, or platform-status changes must update this document, Linear, the central registry/strategy, and both companion repositories together.
