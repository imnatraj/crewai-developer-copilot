# CrewAI Developer Copilot

A production-grade, local-first intelligence and requirement planning platform for Node.js (JavaScript and TypeScript) codebases.

## Features

1. **Deterministic Static Analysis (Layers 1 & 2)**:
   - Walk project layout and detect dependencies.
   - Detect Express, Fastify, and NestJS routing endpoints.
   - Parse Zod, Joi, Yup, and Express-Validator validation layers.
   - Auto-detect database technology and ORMs (Prisma, Sequelize, TypeORM, Mongoose).
   - Parse table schemas, field attributes, constraints, and model relationships.
   - Map codebase imports and circular loops using `madge` and `dependency-cruiser`.
   - Read schema database migration scripts.
   - Trace API parameter validation to service and database writes.

2. **SQLite Knowledge Base (Layer 3)**:
   - Save all codebase facts in `metadata.db` as the single source of truth.

3. **Orchestrated Agent Crews (Layer 4)**:
   - Multi-agent Crews powered by **Gemini 2.5 Flash** and managed via stateful **CrewAI Flows**.
   - Generate technical documentation, API route sheets, validations matrix, dependency graphs, rules, and database schema mappings.
   - Generate impact analysis plans, risk scores, regression test blueprints, and deployment/rollback checklists.

---

## Getting Started

Refer to the [Installation Guide (INSTALL.md)](INSTALL.md) for environment configuration, and the [Developer Guide (DEVELOPER.md)](DEVELOPER.md) for architecture patterns and extensions.

---

## License

MIT
