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
