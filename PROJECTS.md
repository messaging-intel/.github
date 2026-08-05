# Project tracking

This document is the organization-local entry point for planning and delivery tracking.

## Canonical mapping

| System | Canonical resource | Authority |
| --- | --- | --- |
| GitHub organization | [`messaging-intel`](https://github.com/messaging-intel) | Repository ownership, commits, pull requests, reviews, CI, releases, and deployable artifacts |
| GitHub Project | [`messaging-intel-project`](https://github.com/orgs/messaging-intel/projects/1) | Cross-repository delivery board and merge evidence |
| Linear project | [`github.com/messaging-intel`](https://linear.app/denman/project/githubcommessaging-intel-e1358db591e8) | Planning, ownership, dependencies, milestones, and status |
| Fleet registry | [`github-linear-project-registry.tsv`](https://github.com/ORESoftware/k8s-cluster/blob/main/ops/portfolio/github-linear-project-registry.tsv) | Version-controlled organization-to-Linear identity registry |
| Linear registry document | [`GitHub organization, Linear, and GitHub Project registry`](https://linear.app/denman/document/github-organization-linear-and-github-project-registry-b4b115388b25) | Human-readable 64-organization index |

The GitHub Project title is exactly `messaging-intel-project`. Project number `1` is canonical for this organization.

## Evidence contract

Every delivery item should retain these fields when applicable:

- owning repository and Linear issue;
- pull request URL and exact candidate SHA;
- required checks and immutable workflow-run evidence;
- merge commit SHA or an explicit remaining gate;
- artifact, release, deployment, or rollback evidence;
- security and access prerequisites that remain outside source control.

GitHub is authoritative for what was built and merged. Linear is authoritative for why the work exists, who owns it, and what remains. The GitHub Project is the cross-repository execution view; it must not replace either authority.

## Current delivery evidence

| Repository | Pull request | Candidate SHA | Merge commit | Verified evidence |
| --- | --- | --- | --- | --- |
| `msgint-connectors` | [`#22`](https://github.com/messaging-intel/msgint-connectors/pull/22) | `d1475d447a2c7544f830ed02c3c49dd76989eb38` | `198ad20388616141a9ead826ed2ba78e17e85b41` | Exact 19-flag non-secret operator surface; focused operator suite 39/39; app-bound/replay delta 27/27; provider credentials and live writes remain disabled |
| `msgint-connectors` | [`#27`](https://github.com/messaging-intel/msgint-connectors/pull/27) | `cf8e8a0abdb1f2486dff3bdd97af9224f4cdf4fc` | `60956eedd9109ea6a806c1af9aa8f57182f7738c` | Strict nested provider evidence; exact read-only scope; canonical opaque references and approval windows; independent behavior suite 8/8 plus source contract 4/4; hosted jobs were zero-step DEN-977 rejections |
| `msgint-e2e` | [`#10`](https://github.com/messaging-intel/msgint-e2e/pull/10) | `e3d19d8836168487fd027f98c33693ffd684f41c` | `7d14ab1009dba7082e64f6487bef1c91c2dd071b` | Green Playwright, Puppeteer, Selenium, and API matrix on Node 22 and 24; exact eight-origin optional-permission checks |
| `msgint-e2e` | [`#19`](https://github.com/messaging-intel/msgint-e2e/pull/19) | `173deb0f9c94732e477f4aff8296232e01947c0e` | `53f15e508898b7f6a5ab839d79f680891eba17ff` | Shared browser permission policy; dependency-free negative suite 4/4; syntax checks across all three browser integrations |
| `msgint-e2e` | [`#21`](https://github.com/messaging-intel/msgint-e2e/pull/21) | `fea9661a461d5d595ef0f02bd6eea585c609b58e` | `ebc81c97116116d7cadd4ae41cb3e0a0b2a72783` | Bounded synthetic Chrome permission harness; undeclared grants denied; two idempotent removal attempts; exact shared policy suite 7/7 with 10 runtime mutations; hosted jobs were zero-step DEN-977 rejections |
| `.github` | [`#4`](https://github.com/messaging-intel/.github/pull/4) | `05bc522b17134302dc69debccb3ed09e4e966f01` | `ec8a0a81de6cae019d32fb29e1bd556a07f3e2f8` | Organization baseline policy passed; verified Linear/GitHub Project links and authority boundaries published |
| `.github` | [`#6`](https://github.com/messaging-intel/.github/pull/6) | `b2f2928cc8e0f1f56d5a4c6987bbc361e6788731` | `3ddf4a303990417e844d8be0f9dedc1949179ade` | Baseline policy passed; immutable delivery ledger and remaining gates published |

These entries record merged source and test evidence. They do not claim that private credentials were provisioned, live provider assets were registered, capture was enabled, a production cron was activated, or a Kubernetes deployment was performed.

## Remaining gates

- Resolve the organization-level GitHub Actions admission failure tracked as `DEN-977` when a job is rejected before checkout with no steps or logs.
- Rerun the real `zod@4.4.3` provider-authorization command and the real Chromium/WebDriver runtime matrix after hosted capacity is restored; independent tests do not replace those post-capacity checks.
- Provision a least-privilege GitHub App for private cross-repository canaries; use short-lived `contents:read` installation tokens rather than PATs.
- Deploy and verify the Fiducia-controlled daily health/rotation schedule only after reviewed secrets, callback reachability, idempotency, fencing, observability, and rollback evidence exist.
- Register and verify Meta assets, required scopes, app-bound token identity, callback signatures, minimized probes, and candidate promotion before enabling live provider reconciliation.
- Treat OkCupid, ColombianCupid, and other unsupported provider APIs as research-only until an official, authorized, terms-compatible interface and written approval are verified.
- Run live cluster canaries only from a reviewed Kubernetes context; repository tests and manifests are not deployment evidence.

## Repository routing

| Repository | Primary responsibility |
| --- | --- |
| [`msgint-connectors`](https://github.com/messaging-intel/msgint-connectors) | API and browser connector contracts, CLI flags, provider capability boundaries, and daily verification inputs |
| [`msgint-e2e`](https://github.com/messaging-intel/msgint-e2e) | Playwright, Puppeteer, Selenium, API, extension-permission, and browser-policy tests |
| [`msgint-docs`](https://github.com/messaging-intel/msgint-docs) | Product, architecture, operations, and compliance documentation |
| [`msgint-infra`](https://github.com/messaging-intel/msgint-infra) | Deployment, secret-delivery, scheduling, and observability infrastructure |
| [`.github`](https://github.com/messaging-intel/.github) | Organization governance, contributor policy, repository relationships, and tracking entry points |

A repository that does not exist or is not accessible must be recorded as a blocked dependency rather than represented as delivered.

## Naming and synchronization

- Linear project name: `github.com/messaging-intel`.
- GitHub Project title: `messaging-intel-project`.
- Organization governance repository: `messaging-intel/.github`.
- Managed mappings are updated from canonical default branches and reconciled semantically; unrelated prose is preserved.
- Secrets, tokens, private keys, private message content, and private repository inventories do not belong in this public repository or in project-board fields.
