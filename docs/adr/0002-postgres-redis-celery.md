# ADR 0002: Use PostgreSQL, Redis, and Celery for persistence and long-running execution

## Status

Accepted

## Context

The dissertation platform will run experimentation, replay, export, and evaluation workflows that can exceed normal request-response lifetimes. The repo had previously left the database and async execution posture open, but that ambiguity would push key constraints into the middle of the first vertical slice.

The user has now explicitly asked to revise the database to PostgreSQL and add Redis and Celery if needed. For this platform, they are needed.

## Decision

- Use PostgreSQL as the primary application database.
- Use Redis as the local message broker and lightweight coordination store.
- Use Celery as the asynchronous task runner for long-running workflow execution.
- Treat synchronous request handling as a trigger path only; long-running generation work should move to Celery-managed execution.

## Consequences

- Local development now expects Postgres and Redis to be available.
- The first application slice should be designed around asynchronous execution boundaries instead of retrofitting them later.
- Database models, run status tracking, and execution traces should be compatible with background task processing from the start.
- The repo needs environment variables and dependency manifests for PostgreSQL, Redis, and Celery from bootstrap onward.

## Alternatives Considered

### SQLite for initial development

Rejected because the platform is centered on workflow state, observability, and longer-running tasks. Designing around SQLite first would create misleading constraints and rework when concurrency or task orchestration appears.

### Background execution deferred until later

Rejected because long-running experiment runs are already part of the intended platform shape. Delaying the async model would push a foundational change into the middle of feature work.

### Redis without Celery

Rejected because Redis alone does not define the task execution model needed for the platform's long-running workflows.
