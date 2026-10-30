# Stack policy

Treat `project-defaults.json` as the machine-readable source of greenfield preferences. Apply the resolved personal, machine, project, and task choices before these defaults. Preserve coherent repository choices. Qualitative overrides, such as preferring Django or allowing LangChain, belong in the approved local working-agreement delta.

## Selection rules

1. Preserve a coherent existing stack and its lockfiles.
2. Ask when detected tools conflict, a choice changes deployment or data architecture, or the default adds a service.
3. Prefer local-first and self-hostable components for solo and small-team work.
4. Let an organization-selected platform win in team-owned data science and LLM projects.
5. Add infrastructure only when the project has the operational need it solves.

## Boundaries

| Boundary | Default | Ask when |
|---|---|---|
| Python | uv, Ruff, pytest, Pyright standard | Poetry or another manager is required; research code makes static checking noisy |
| API | FastAPI, Pydantic v2, HTTPX, OpenAPI | Protocol, latency, streaming, or deployment constraints point elsewhere |
| Frontend | React and TypeScript; Vite behind FastAPI | SSR, SEO, React Server Components, or a Node full-stack layer matters |
| UI | Tailwind and shadcn/ui | The interface is tiny, has an established design system, or needs specialized components |
| JavaScript | Node Active LTS, pnpm, strict TypeScript, Biome, Vitest | Existing tooling or required plugins provide a better fit |
| Browser verification | Playwright | The project has no browser behavior |
| Tabular processing | Polars for new pipelines; pandas for compatibility | Library integration, team convention, or workload shape decides it |
| Dataset format | Parquet for larger analytical data | Exchange, streaming, appendability, readability, or an external contract favors CSV, JSON, JSONL, or another format |
| Relational storage | PostgreSQL in production; SQLite for local prototypes | The workload is analytical, embedded, serverless, or externally constrained |
| Vector storage | Qdrant for a dedicated vector subsystem; pgvector when co-location is enough | Retrieval scale, hybrid search, filtering, operations, and another service must be weighed |
| LLM integration | Official or OpenAI-compatible clients behind small typed adapters | Routing, fallback, rate, or budget control justifies a proxy |
| Agent layer | Pydantic AI when the workflow is genuinely agentic | Direct calls and functions are sufficient |
| Model runtime | Project-specific local or hosted endpoint | Hardware, quantization, concurrency, privacy, licensing, and latency are unresolved |
| Notebook | marimo as a soft preference; Jupyter for compatibility | A notebook is actually useful; otherwise use Python modules |
| Experiment tracking | MLflow when durable tracking is useful | A tiny run needs only versioned artifacts or a team mandates another platform |
| Formal LLM eval | Inspect AI | A small typed application harness answers the question more directly |
| LLM tracing | Structured logs first; self-hosted Opik when traces need a UI | MLflow already covers the need or the operational cost is not justified |
| Deployment | Docker and Compose; GitHub Actions | The real target requires serverless, Kubernetes, cloud, or on-premises integration |

Pydantic validates and serializes boundary data at runtime. Pyright checks annotated program behavior without executing it. Use both where the project benefits, and keep Pyright at `standard` for exploratory code unless a stricter stable boundary is worth the annotation cost.

Use native structured outputs and Pydantic schemas where supported. The default new-project stack excludes LangChain and LlamaIndex; an explicit override or coherent existing project can use them. Use LiteLLM only when its routing capabilities earn the abstraction. Use W&B or Trackio only for a project or team requirement that MLflow or local artifacts do not meet.

## Operational questions

Always resolve project maturity, deployment target, exposure and authentication, data sensitivity, external-provider permissions, expected workload, and the experiment or evaluation budget before those answers affect implementation.
