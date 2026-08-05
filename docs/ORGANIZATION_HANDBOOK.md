# messaging-intel organization handbook

> Shared operating defaults for repositories maintained under **messaging-intel**. Repository-local policy may strengthen these rules but should not silently weaken them.

## Mission

messaging-intel maintains software for messaging intelligence, conversation analysis, and human-reviewed contact workflows. This `.github` repository is the canonical home for organization-wide community health files, reusable templates, engineering policy, and planning links.

## Repository contract

Each active repository must document purpose, ownership, maturity, supported environments, development and test commands, authoritative schemas and integrations, release and rollback procedures, compatibility policy, and GitHub Project/Linear links. Data-processing components must also document consent and authorization boundaries, collection sources, retention, deletion, normalization, deduplication, human-review gates, rate limits, and platform-policy constraints.

## Change and review workflow

1. Anchor work in an issue, Linear item, or documented maintenance objective.
2. Keep branches and pull requests focused.
3. Explain motivation, scope, privacy and abuse risk, validation, compatibility, migration, and rollback.
4. Test permission, duplicate, parsing, deletion, opt-out, rate-limit, and partial-failure paths as relevant.
5. Resolve conflicts semantically by reconstructing both sides' intent.
6. Prefer squash merges for focused work unless commit structure materially improves auditability.

## Evidence and quality

Pull requests should include reproducible commands, synthetic or sanitized fixtures, expected and observed results, negative-path coverage, documentation updates, and CI or local-equivalent evidence. Integration changes require platform-policy and consumer impact analysis.

## Privacy, safety, and security

Never commit credentials, session tokens, personal conversations, contact details, production identities, or sensitive logs. Use synthetic or irreversibly sanitized fixtures. Preserve human review for consequential outreach or account actions; avoid unsolicited bulk behavior. Follow `SECURITY.md` for private vulnerability reporting and pin dependencies and actions where supply-chain integrity matters.

## Documentation and decisions

Keep examples sanitized and executable, links current, assumptions explicit, and data-flow boundaries clear. Record privacy, consent, retention, platform, compatibility, moderation, and operational decisions that future maintainers would otherwise have to rediscover.

## Planning ownership

GitHub owns code, reviews, checks, releases, and delivery evidence. Linear owns priority, dependencies, sequencing, and cross-project planning. The organization GitHub Project is the cross-repository execution view; see `PROJECTS.md` for routing details.

## Organization health

- [ ] Profiles, descriptions, topics, and READMEs are current.
- [ ] Contribution, security, support, governance, issue, and PR guidance is present.
- [ ] Data sources and authorization boundaries are documented and reviewed.
- [ ] Required checks reflect privacy, abuse, integration, and supply-chain risk.
- [ ] Stale repositories are archived or clearly marked.
- [ ] Project links resolve and completed work is reflected in GitHub and Linear.
