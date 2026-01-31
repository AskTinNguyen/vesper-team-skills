# Enrichment Checklist

Use this checklist when enriching a skill from its source repository. Check each category and note gaps.

## 1. Installation & Setup

- [ ] Dependencies listed (packages, tools, runtimes)
- [ ] Version requirements specified (Node >=18, Python >=3.10, etc.)
- [ ] Install commands provided (exact, copy-pasteable)
- [ ] Post-install steps documented (migrations, config generation, etc.)
- [ ] System requirements noted (OS, architecture, disk space)

## 2. Configuration

- [ ] All config files identified (paths, formats)
- [ ] All config keys documented with defaults
- [ ] Environment variables listed with descriptions
- [ ] `.env.example` or equivalent included in assets/
- [ ] Sensitive values identified (API keys, secrets) with placeholder guidance

## 3. CLI Commands

- [ ] All commands documented with exact syntax
- [ ] All flags and options listed
- [ ] Exit codes documented
- [ ] Common error messages and their meanings
- [ ] Shell completion setup (if available)

## 4. Scripts

- [ ] All scripts have correct shebangs (`#!/usr/bin/env bash` or `#!/usr/bin/env python3`)
- [ ] Scripts use real commands from the source (verified, not hypothetical)
- [ ] Scripts handle errors with proper exit codes
- [ ] Scripts document their usage in comments or `--help`
- [ ] Scripts use portable syntax (no bash-isms if targeting sh)

## 5. API / Integration

- [ ] API endpoints documented (method, path, params, response)
- [ ] Authentication method documented
- [ ] Rate limits noted
- [ ] Webhook/event formats documented
- [ ] SDK usage examples (if applicable)

## 6. File Formats

- [ ] Input file formats documented with examples
- [ ] Output file formats documented with examples
- [ ] Configuration file formats documented
- [ ] Template syntax documented (if applicable)

## 7. Error Handling

- [ ] Common errors listed with causes and fixes
- [ ] Troubleshooting section covers real issues (from source's issue tracker)
- [ ] Recovery procedures for data loss or corruption
- [ ] Logging configuration documented

## 8. Testing

- [ ] How to run tests documented
- [ ] Test environment setup documented
- [ ] Test data/fixtures described
- [ ] CI/CD pipeline configuration referenced

## 9. Examples

- [ ] At least one complete end-to-end example
- [ ] Examples use real data structures (not `foo`/`bar`)
- [ ] Examples show common use cases
- [ ] Examples show error handling
- [ ] Examples match current API version (not deprecated)

## 10. Architecture

- [ ] Project structure overview (key directories and their purposes)
- [ ] Key abstractions explained (models, services, handlers)
- [ ] Data flow documented (request lifecycle, event processing)
- [ ] Extension points identified (plugins, hooks, middleware)

## 11. References

- [ ] External documentation linked (official docs, tutorials)
- [ ] Related tools and alternatives mentioned
- [ ] Migration guides (if upgrading from previous versions)
- [ ] Changelog highlights for recent versions

## 12. Skill-Specific

- [ ] SKILL.md frontmatter is valid (name, description)
- [ ] Trigger phrases match real use cases
- [ ] All file references in SKILL.md resolve to real files
- [ ] Progressive disclosure: essentials in SKILL.md, details in references/
- [ ] No placeholder TODOs remain
- [ ] Scripts are executable (`chmod +x`)

## Gap Severity Levels

| Level | Description | Action |
|-------|-------------|--------|
| **Critical** | Skill will fail without this | Fix immediately |
| **Important** | Skill works but poorly without this | Fix in this enrichment pass |
| **Nice-to-have** | Improves skill quality | Fix if time permits |
| **Cosmetic** | Style or formatting | Fix in a future pass |
