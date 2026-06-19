# GitHub Visibility Policy

Use this policy for satellite repos unless a project-specific exception is
explicitly approved.

## Default rule

- New satellite repos are private by default.
- Public visibility is allowed only with explicit authorization.

## Required record

If a repo is public, record the exception in `docs/supervision/GITHUB_HOME.md`
with:

- remote
- branch
- visibility
- authorization
- confirmed_by
- confirmed_at_utc

## Review rule

- Treat public visibility as an explicit exception, not an implicit default.
- Do not promote a visibility exception upstream as a generic rule unless the
  pattern is proven reusable across multiple repos.
