# 0001. Record architecture decisions

- **Status:** Accepted
- **Date:** 2026-10-29

## Context

The `colivmanager-backend` service is in its early stages. As it grows, the
reasoning behind foundational choices — the web framework, how the service is
packaged, where and how it is deployed — will become harder to reconstruct from
the code alone. New contributors need a durable record of *why* the system is
built the way it is, not just *how*.

We have no lightweight, version-controlled way to capture these decisions
today.

## Decision

We will keep Architecture Decision Records (ADRs) in this repository, under
`docs/adr/`, following the format popularised by Michael Nygard.

- Each significant architectural decision gets its own numbered Markdown file.
- ADRs live alongside the code and evolve through the same pull-request review
  process.
- An accepted ADR is immutable; a decision is changed by writing a new ADR that
  supersedes the previous one.

## Consequences

- The context and trade-offs behind architectural choices stay discoverable and
  reviewable.
- Contributors incur a small, deliberate overhead: significant decisions should
  be accompanied by an ADR.
- The `docs/adr/README.md` index and `template.md` provide the entry point and
  starting structure for new records.

## Alternatives considered

- **A wiki or external document store** – decouples the rationale from the code
  and its review process, and tends to drift out of date.
- **No formal record** – lowest effort, but institutional knowledge is lost as
  contributors change.
