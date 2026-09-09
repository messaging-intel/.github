# QA / research post-parity certification roadmap

- **Tracking:** Linear `DEN-604`, `DEN-3903`, `DEN-389`, and completed baseline `DEN-3975`
- **Cross-organization dependencies:** Elenkos `DEN-3837` and `DEN-3824`
- **Status:** implementation and synthetic certification only; production recruitment and collection remain disabled
- **Last reviewed:** 2026-09-09

## Decision

The same person may independently be an Elenkos QA engineer and a Messaging Intel research participant. The person is the intersection; the systems and records are not.

The following remain separate:

- identity and subject namespaces;
- authentication sessions and audiences;
- authorization and operator roles;
- application state and local persistence;
- databases, schemas, service principals, object stores, queues, caches, and backups;
- encryption and key-management contexts;
- logs, traces, analytics, crash reports, support evidence, and exports;
- compensation, data-rights, and incident-response paths;
- manager-visible and customer-visible state.

The only currently admitted cross-organization object is a neutral `public_information_card` with `activationStatus = disabled_pending_approval`. It carries no invitation, participation state, research credential, response, reminder, reproductive-health value, QA identity, work record, device signal, or telemetry correlation.

## Completed baseline

The roadmap starts after these completed or merged controls:

1. `messaging-intel/msgint-docs#3` defines the QA/research noninterference boundary, observation-error mechanisms, separately analyzed QA-outreach stratum, and fail-closed activation posture.
2. `messaging-intel/msgint-interfaces#50` defines independently authored TypeSpec and JSON Schema Draft 2020-12 peer authorities for the workplace public-information boundary.
3. `elenkos-systems/elenkos-rykshaw-flutter#13` removes QA-owned research routes, configuration, controller state, persistence, actions, and telemetry, leaving an information-only surface.
4. `elenkos-systems/elenkos-interfaces#5` removes the stale research route from the canonical Elenkos interface authority and generated projections.
5. `messaging-intel/msgint-interfaces#61` proposes the next evidence layer: pinned TJSV parity, Contract IR, current-input consumer verification, generated Rust/Dart/TypeScript validators, runtime evidence, and a negative drift canary.

These changes do not authorize recruitment, consent, collection, compensation, analysis export, or country activation.

## Current blocker: real workflow admission

`messaging-intel/msgint-interfaces#61` currently has exact head:

```text
4b4138e5acc6a29b9d287413e454d2ff93f3bae5
```

Workflow run `34315550474`, job `102350883785`, completed with:

```text
steps: []
runner_id: 0
runner_name: ""
runner_group_id: 0
```

No checkout, dependency install, TypeSpec compilation, JSON Schema comparison, TJSV execution, runtime adapter, drift canary, repository test, or artifact upload ran. This is a zero-step Actions-admission result tracked by `DEN-3903` and [organization issue #22](../issues/22). It is neither a source pass nor a source failure.

PR #61 must remain draft and unmerged until its exact current head—or a semantically reconciled successor current with `main`—executes real steps and all required gates pass.

## Authority and evidence graph

```text
independently authored TypeSpec ------------------.
                                                    +--> TJSV parity receipt
independently authored JSON Schema Draft 2020-12 -'          |
                                                               +--> verified Contract IR
TypeSpec-generated JSON Schema witness -----------------------'          |
                                                                          +--> consumer verification
trusted positive/negative corpus ----------------------------------------'          |
                                                                                     +--> runtime evidence
operation/projection metadata + pinned emitters + output digests -------------------'          |
                                                                                                +--> projection admission
                                                                                                |
                                                                                                +--> exact-source external consumers
```

### Authority rules

- TypeSpec and the authored JSON Schema are independent human-maintained peer authorities.
- The TypeSpec-generated JSON Schema is comparison evidence only.
- Contract IR, generated language packages, Protobuf, SQL, ORM models, clients, runtime receipts, and projection manifests are derived evidence, never a third authority.
- A copied `passed` flag, stale receipt, generated symbol, old output digest, or partial declaration list is not admission evidence.
- Every consumer recomputes verification against current checked-out sources immediately before use.

## Task graph

### P0: complete TJSV evidence and downstream admission

[Issue #25 — certify TJSV Contract IR, runtime evidence, and projection admission](../issues/25)

Required outcomes:

- pin one reviewed 40-character `ORESoftware/typespec-json-schema-validator` commit at every execution edge;
- retain the parity receipt, generated comparison witness, Contract IR, consumer-verification receipt, runtime evidence, and projection manifests with exact source/tool/output digests;
- require the complete qualified declaration scope for `MessagingIntel.WorkplaceParticipantBoundary.PublicInformationCard`;
- verify current TypeSpec, generated witness, authored JSON Schema, parity receipt, and Contract IR immediately before every consumer;
- execute the same trusted corpus through Rust/Serde, Dart/Flutter, and TypeScript validators, adding Gleam and Go when those projections are introduced;
- bind Protobuf/gRPC, OpenAPI, SQL, Diesel, SeaORM, SDK, and client outputs through projection admission;
- stop on missing adapters, skipped cases, validator crashes, stale inputs, unknown outputs, or unreviewed representation loss.

### P0: independent paired test organizations

[Issue #26 — certify cross-org noninterference in paired test organizations](../issues/26)

`messaging-intel-test` and `elenkos-systems-test` must consume immutable production SHAs through governed read-only materialization or certified Zed packages. They must not copy production sources or define their own expected contract.

Required negative families include:

- QA account, tenant, team, manager, assignment, finding, schedule, performance, compensation, location/BLE, device/network, auth subject, trace/session, support, and analytics identifiers entering research;
- invitation, eligibility, participation, consent/refusal, pause/withdrawal, response, reminder, reproductive-health, research compensation, data-rights, cohort, or pseudonym state entering QA;
- manager inference through URL opens, application switching, installed-app inventory, network destination, notifications, timing, crash reports, support evidence, exports, or small aggregates;
- test, demo, emulator, automation, and fixture records entering authoritative research storage;
- duplicate/reordered retries, withdrawal during queued transfer, stale sessions, restore without deletion replay, and locale/timezone drift.

Every test run records exact source SHAs, TJSV revision, package and corpus digests, toolchains, commands, and explicit passed/failed/skipped/blocked states.

### P0: cloud and data-plane noninterference

[Issue #27 — prove Supabase, Neon, Cloudflare, AWS, and R2 separation](../issues/27)

The inventory must reconcile the one-to-one organization mapping across GitHub, Linear, GitHub Projects, Slack, Cloudflare, GCP, Supabase, Neon, AWS, and R2 while respecting the documented temporary Supabase exception.

Required invariants:

- Elenkos and Messaging Intel have distinct RuntimeConfig paths, schemas, service roles, RLS policies, migration ownership, object stores, queues, encryption contexts, telemetry, backups, and operators;
- no broad service role, credential, admin group, backup set, queue, telemetry stream, or support export can read both sensitive planes;
- R2 bucket names are globally collision-safe and organization-prefixed;
- per-customer buckets include the unique organization prefix and use independently scoped credentials and policies;
- object-key prefixes inside one broadly accessible bucket are not accepted as the sole isolation boundary for sensitive research or legal evidence;
- a runtime in one organization cannot resolve the other organization’s database, schema, queue, bucket, key, endpoint, or telemetry sink;
- backup restore replays withdrawal and deletion obligations.

Provider access that cannot be independently verified is recorded as `blocked`, never as a pass.

### P0: Elenkos manager non-inference

[Elenkos issue #33 — prove manager blindness across privileged surfaces](https://github.com/elenkos-systems/.github/issues/33)

Elenkos must prove that owners, administrators, managers, schedulers, reviewers, payout operators, support staff, and analytics users cannot learn or infer individual research state. The absence must hold across normal/admin APIs and web applications, database projections, search/filter/export paths, notifications, logs/traces/metrics, crashes, screenshots, support tooling, caches, backups, and repeated small-cell queries.

Break-glass cannot expose research data because the Elenkos plane must not possess it.

### P0: Rykshaw verified consumer

[Elenkos issue #34 — consume only TJSV-verified public-information projections](https://github.com/elenkos-systems/.github/issues/34)

Rykshaw may consume only an immutable, admitted public-information projection. It must:

- verify the current peer-authority closure, parity receipt, Contract IR, complete declaration scope, and Dart runtime evidence before projection use;
- reject stale package pins, unknown fields, unsupported locales, unsafe URLs, bearer/invitation material, hypothesis-bearing content, and any activation literal other than `disabled_pending_approval`;
- retain no research API origin, credential, participant identifier, callback, controller state, queue, secure-storage entry, or manager-visible event;
- fail to a static unavailable state rather than a generic remote renderer or enrollment fallback.

### P1: observation clocks and immutable analysis provenance

[Issue #29 — bind observation-error clocks and analysis provenance](../issues/29)

Every approved research observation must keep event, client capture, reminder, server receipt, correction, and missingness clocks separate. It must bind protocol, consent, instrument, locale, app/build, schema, reminder policy, algorithm, and collection-method versions.

The analysis manifest must bind:

- preregistered hypotheses, estimands, endpoints, windows, exclusions, clustering, missingness, multiplicity, and negative controls;
- country/site/locale and the separately identified QA-outreach stratum;
- null simulations that preserve observed cycle variability, repeated measures, finite windows, and reminder/report timing;
- exact dataset, transformation code, toolchain/model, and output digests;
- confirmatory versus exploratory status.

Temporal overlap, convergence, or correlated reporting is not automatically biological synchronization or causation.

### P1: independent country activation receipts

[Issue #28 — signed four-country activation receipts and rollback](../issues/28)

Colombia, Venezuela, Ecuador, and Brazil are independent activation lanes. No country inherits approval from another.

A passed activation receipt binds the exact:

- country, site/recruiting entity, sponsor, and responsible operator;
- protocol, preregistration, ethics/site review, privacy, employment-power, jurisdiction, transfer, residency, and security evidence;
- approved participant information, consent, withdrawal, complaint, and data-rights materials in the required language;
- instrument, reminder policy, observation-error register, and negative-control versions;
- TypeSpec and authored JSON Schema digests, TJSV `runId`, Contract IR ID, complete runtime evidence, and projection manifests;
- app, web, server, container, package, image, and GitOps revisions;
- data-plane ownership and latest successful rollback/kill-switch drill.

A branch, environment variable, deployed binary, copied approval boolean, stale receipt, or another country’s receipt cannot activate production.

### P1: incident containment and deletion replay

[Issue #30 — exercise leak kill switch, queue cancellation, and restore/delete replay](../issues/30)

A suspected boundary leak must stop affected recruitment, invitations, collection, reminders, provider egress, analysis export, and callbacks. The workflow must cancel or tombstone queued and offline transfers, deny stale sessions, retain non-sensitive incident provenance, enumerate affected sinks using sanitized identifiers, and replay withdrawal/deletion obligations after restoring a backup.

Automation may not revoke unrelated credentials. Credential/session actions require an explicitly approved, scoped human-controlled procedure. Reactivation requires a new passed country/build receipt.

## Dependency order

```text
DEN-3903 / .github#22: real runner admission
    |
    v
.github#25: TJSV parity -> Contract IR -> runtime -> projection admission
    |------> Elenkos #34: verified Rykshaw consumer
    |------> .github#26: paired test organizations
    |------> Elenkos #33: manager non-inference
    |------> .github#27: cloud/data-plane noninterference
    `------> .github#29: observation/analysis provenance

DEN-411 consent/data rights -----.
DEN-412 ethics governance --------+--> .github#28 country activation receipt
DEN-413 jurisdiction review ------'              |
#25 + #26 + #27 + #29 ---------------------------'
                                                     |
                                                     `--> .github#30 containment/restore drill
```

## Existing ownership that must not be duplicated

The following remain authoritative unless a verified residual gap is demonstrated:

- `DEN-411`: consent, pause, withdrawal, correction, export, and deletion approval;
- `DEN-412`: ethics/IRB or equivalent governance determination;
- `DEN-413`: jurisdiction, privacy, and interception-law review;
- `DEN-389`: release-gate evidence pack and immutable activation plan;
- `DEN-3903`: Actions admission and CI cost/burn controls;
- `DEN-604`: repository-family conformance;
- `DEN-3837` and `DEN-3824`: Rykshaw and Elenkos workforce/admin architecture;
- [organization issue #22](../issues/22): runner admission;
- [organization issue #23](../issues/23): future `msgint-pub-lib-core`;
- [organization issue #24](../issues/24): fleet readiness and PR reconciliation;
- Elenkos `.github#14`, `#15`, and `#18`–`#31`.

## Program completion criteria

The post-parity program is complete only when:

1. every lane names an owning repository and exact source SHA;
2. every executable gate runs on a real runner and retains a non-sensitive receipt;
3. every result is explicitly `passed`, `failed`, `skipped`, or `blocked`;
4. every consumer verifies current source inputs and complete declaration scope;
5. runtime and projection evidence is deterministic, compile-tested, and bound to exact tool/output digests;
6. no manager or QA operator can learn or infer individual research participation;
7. no QA identity or operational event enters research, and no research state enters QA;
8. the four country lanes remain independently disabled until exact receipts pass;
9. the leak kill switch, queue cancellation, withdrawal, restore/delete replay, and rollback are exercised using synthetic data;
10. no production participant, credential, recruitment, consent, collection, compensation, analysis export, or activation is introduced as test material.

## Linear mirror

The Linear project document is:

[Cross-org contract certification task graph — 2026-09-09](https://linear.app/denman/document/cross-org-contract-certification-task-graph-2026-09-09-e695809e011c)

Creating a new Linear umbrella issue was attempted and rejected because the workspace free-issue limit is exceeded. GitHub issues are therefore the executable records, while the Linear project document and comments on existing umbrellas provide the planning mirror. No fabricated Linear identifiers are used.
