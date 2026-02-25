# Changelog

All notable changes to this testing suite will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Visual regression testing with AI-powered comparison
- Mobile app testing (Appium integration)
- Load testing support (k6 integration)
- Security testing (OWASP ZAP)
- Performance benchmarking

## [1.0.0] - 2024-02-01

### Added
- **test-orchestrator**: Main orchestrator with 7-step collaborative workflow
  - Input clarification with AskUserQuestion
  - Parallel research (repo, best-practices, framework-docs)
  - Test planning (MINIMAL/MORE/ALOT levels)
  - Test case generation with spec-flow-analyzer
  - Parallel test execution across all test types
  - Bug classification (P1/P2/P3) with todo tracking
  - User decision checkpoints before creating PRs

- **test-frontend**: Component testing for Frontend frameworks
  - React Testing Library support
  - Vue Test Utils support
  - Svelte testing support
  - Angular testing support
  - Auto-detection of framework and test runner
  - Coverage requirements (80%+)

- **test-backend**: Unit and integration testing for Backend
  - Node.js (Express, Fastify, NestJS) support
  - Python (FastAPI, Flask, Django) support
  - Ruby (Rails, Sinatra) support
  - Go (Gin, Echo, Fiber) support
  - Testcontainers for database testing
  - Factory pattern for test data

- **test-e2e**: End-to-end testing with Playwright
  - Page Object Model (POM) pattern
  - Cross-browser testing (Chromium, Firefox, WebKit)
  - Mobile viewport emulation
  - Visual regression testing
  - Trace and screenshot on failure
  - CI/CD integration

- **test-api**: API testing for REST and GraphQL
  - REST endpoint testing with pytest
  - GraphQL query/mutation testing
  - OpenAPI contract testing (schemathesis)
  - Authentication testing (JWT, API Key, OAuth)
  - Performance testing
  - Parallel execution support

### Features
- Parallel test execution across all test types
- Comprehensive bug tracking with todo files
- User approval checkpoints before actions
- Coverage reporting (HTML, JSON, LCOV)
- Integration with GitHub issues and PRs
- Risk-based test prioritization (P0/P1/P2/P3)

## [0.9.0] - 2024-01-15

### Added
- Initial beta release of testing suite
- Basic test orchestration workflow
- Frontend component testing support
- Backend API testing support
- E2E testing with Playwright

### Changed
- Refactored workflow to 7-step collaborative process

### Fixed
- Race conditions in parallel test execution
- Test data cleanup issues

## [0.8.0] - 2024-01-01

### Added
- Alpha release for internal testing
- Basic command structure
- Proof of concept for parallel agents

---

## Release Notes Template

```markdown
## [X.Y.Z] - YYYY-MM-DD

### Added
- New features

### Changed
- Changes in existing functionality

### Deprecated
- Soon-to-be removed features

### Removed
- Now removed features

### Fixed
- Bug fixes

### Security
- Security improvements
```
