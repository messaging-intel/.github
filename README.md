# messaging-intel organization defaults

This public `.github` repository contains organization-wide community health files, contributor guidance, shared agent policy, an explicit repository-relationship contract, and the verified planning entry point in [`PROJECTS.md`](./PROJECTS.md).

Canonical planning identities:

- GitHub Project: [`messaging-intel-project`](https://github.com/orgs/messaging-intel/projects/1)
- Linear project: [`github.com/messaging-intel`](https://linear.app/denman/project/githubcommessaging-intel-e1358db591e8)

Repository-local policy wins when it is stricter or more specific. Existing project history must be preserved during consolidation and conflict resolution. Public governance files must not contain secrets, private keys, private message content, or unverified private-repository inventories.

<!-- ore-org-baseline:begin -->
## Organization-wide defaults

This public repository is the canonical source for GitHub-supported community-health fallbacks, organization profile content, contribution guidance, public security/support policy, issue and pull-request templates, and agent-governance declarations for [`messaging-intel`](https://github.com/messaging-intel).

## Canonical organization links

- GitHub organization: https://github.com/messaging-intel
- Public organization defaults: https://github.com/messaging-intel/.github
- Canonical Linear project: https://linear.app/denman/project/githubcommessaging-intel-e1358db591e8
- Fleet tracking issue: https://github.com/ORESoftware/k8s-cluster/issues/1222

## Safety baseline

All Git conflicts must be resolved semantically with full historical, repository-wide, organization-wide, and relevant external-organization context. Automated agents are hard-denied from destructive or history-rewriting operations, including all forms of `git stash`, `git reset`, `git clean`, `git filter-repo`, force pushing, destructive deletion, data or infrastructure teardown, credential revocation, and policy bypass.

## GitHub inheritance boundary

GitHub can use supported community-health files from a public organization `.github` repository as fallbacks and can render `profile/README.md` on the organization page. `agents.md`, `AGENTS.md`, Copilot instructions, workflows, settings, rulesets, branch protections, permissions, and secrets are not automatically inherited merely because they exist here. Each repository must carry or synchronize compatible local policy and explicitly call reusable workflows where enforcement is required.

Generated managed-policy version: `2026-08-08`.
<!-- ore-org-baseline:end -->

<!-- BEGIN MANAGED REPOSITORY RELATIONSHIPS v1 -->
## Repository relationship registry

`messaging-intel` declares repository roles, dependency edges, cross-organization capabilities, deployment ownership, and the git-submodule/Zed-package contract:

- [Human-readable map](architecture/REPOSITORY_RELATIONSHIPS.md)
- [Machine-readable manifest](architecture/repository-relationships.json)
- [JSON Schema](architecture/repository-relationships.schema.json)

The public registry withholds private repository names and edges.
<!-- END MANAGED REPOSITORY RELATIONSHIPS v1 -->
