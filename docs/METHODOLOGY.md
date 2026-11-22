# Development Methodology

## 1. Software Development Lifecycle (SDLC)

- **Framework:** Agile Scrum with 2-week sprints (sprint planning, daily stand-up, sprint review with the Capital Harvest operations lead acting for the product owner, and a retrospective). This matches the hybrid plan in the Phase 1 report: phase gates for the sponsor, with Scrum for development.
- **Roles:** Product Owner - CHFB Operations Manager (proxy: Business Analyst); Scrum Master - Project Manager; Development Team - Lead Developer, ML & Data Engineer, QA & DevOps Lead.
- **Planning & Tracking:** Work items are logged as GitHub Issues (user stories, bugs, documentation tasks) and prioritized in GitHub Project Boards (Backlog -> Sprint -> In Progress -> Review -> Done). Pull requests reference their issue with `Closes #N` so issues close automatically on merge.

## 2. Version Control & Branching Strategy

- **Workflow:** GitHub Flow.
- **main:** Always contains production-ready, tested code; every merge to `main` can be built into a Docker image and deployed.
- **feature/\* | fix/\* | docs/\*:** Short-lived branches created from `main` for isolated changes (for example `feature/add-documentation`, `docs/architecture-and-methodology`), merged through a Pull Request and then deleted locally and on GitHub.
- **Commit Convention:** Conventional-Commit-style prefixes: `feat:`, `fix:`, `docs:` / `Docs:`, `refactor:`, `test:`, `chore:`, with a short summary in the imperative mood.
- **Releases:** Docker images are tagged with a semantic version (`1.0`) plus a moving `latest` tag on Docker Hub.

## 3. Code Review & Definition of Done (DoD)

1. Code compiles/runs locally without errors or regressions (`flask run` and `docker run` both start and serve `/health`).
2. Unit and integration tests pass (`pytest`; all tests green).
3. Relevant documentation (README and /docs) is updated.
4. Changes are submitted via Pull Request and reviewed prior to merging into main (at least one teammate review comment or approval, and the linked issue referenced).
5. For user-facing features: acceptance criteria in the GitHub Issue are met and demonstrated to the product owner at the sprint review.

## 4. Testing & Quality Assurance Strategy

- **Unit Testing:** pytest. Core business rules (`app/core/services.py`: FEFO order of picks, partial/backorder status, donation validation, expiry window) are tested with an in-memory repository and a fixed date. Target: at least 80% line coverage of `app/core`.
- **Integration / System Testing:** Flask test client tests exercise the HTTP API end to end (donation -> order -> stock decrement -> expiry alert, plus 400 on invalid input). Before release, the Docker image is built and run, and `/health`, `/api/lots` and the dashboard are smoke-tested against the running container. Full end-to-end user acceptance testing with staff and partner agencies is planned for the pilot phase described in the Phase 1 report.
