# TritonPlan Architecture

## Project Principle

TritonPlan is an AI-powered academic planning tool for UCSD students. It should behave like an academic planning engine, not a chatbot that happens to know about classes.

The core principle is:

> Use structured logic for correctness and RAG for explanation.

LLMs may explain requirement status, summarize policy, and answer advising-style questions from retrieved UCSD sources. They must not be the source of truth for degree progress, prerequisite eligibility, or planner constraints. Those decisions belong to structured data, deterministic rule evaluation, prerequisite graph logic, and tested planning code.

This document separates the architecture into:

1. **MVP Architecture**: the smallest useful academic planning engine.
2. **Phase 2 Architecture**: hardening, richer data, better retrieval, and optional graph projection.
3. **Final Architecture**: the long-term platform with broader UCSD coverage and real schedule optimization.

---

## Phase Summary

| Phase | Goal | Include | Avoid |
|---|---|---|---|
| MVP | Prove reliable academic planning for one narrow UCSD slice | Data Science major, Eighth College GE, prerequisite checker, requirement checker, rough quarter planner, source-backed RAG, semantic course search | Neo4j, OR-Tools, live WebReg, exact meeting times, professor ratings, open-seat tracking |
| Phase 2 | Improve data depth, explainability, and planning quality | More robust ingestion, richer requirement model, planner scoring, auth, saved plans, optional Neo4j graph projection | Replacing structured logic with LLM decisions, over-broad major/college support before data quality is solid |
| Final | Mature academic planning and schedule optimization platform | Multiple majors/colleges/minors, real schedule data, constraint optimization, production graph layer, operational monitoring | Claims of official advising authority, unsupported policy guesses |

---

## MVP Architecture

### MVP Scope

The MVP should support:

- University: UC San Diego only.
- Major: Data Science first.
- College: Eighth College GE requirements first.
- Planning mode: rough quarter-by-quarter planning.
- Academic logic: deterministic structured checks.
- Explanations: RAG over official UCSD sources.

The MVP should not support:

- Live WebReg integration.
- Exact meeting-time schedule generation.
- Open-seat tracking.
- Professor ratings.
- Automated enrollment.
- Full graduation audit claims.
- Broad multi-major or multi-college coverage.

### MVP System Shape

```text
Next.js Frontend
        |
FastAPI Backend
        |
PostgreSQL + pgvector
```

PostgreSQL is the source of truth. `pgvector` stores embeddings for RAG and semantic course search. The backend runs prerequisite evaluation, requirement evaluation, recommendation scoring, and rough planning in Python.

Neo4j and OR-Tools are intentionally deferred. They are useful later, but they should not block the first working planning engine.

### MVP Local Services

Local development should start with:

```text
frontend
backend
postgres with pgvector
```

The PostgreSQL image should support the `vector` extension, such as `pgvector/pgvector`, once semantic search or RAG is implemented.

Neo4j should not be required for MVP local development. If a Neo4j service is added early for experimentation, it should be optional and not part of the core MVP path.

### MVP Backend Responsibilities

The FastAPI backend should own:

- Course catalog APIs.
- Student completed-course APIs.
- Prerequisite eligibility checks.
- Requirement satisfaction checks.
- Missing requirement summaries.
- Rough quarter-by-quarter plan generation.
- RAG retrieval and answer generation.
- Semantic course search.

The backend should expose results in a way the frontend can audit. For example, a requirement response should include satisfied courses, missing requirements, ambiguous items, and source references where available.

### MVP Frontend Responsibilities

The frontend should prioritize clarity and trust:

- Show completed, missing, and uncertain requirements.
- Show courses the student can take now.
- Show blocked courses and missing prerequisites.
- Show a rough future plan by quarter.
- Show source-backed explanations with citations.
- Make uncertainty visible instead of hiding it.

The UI should not feel like a standalone chatbot. Chat can exist, but the product should center structured planning views.

---

## MVP Data Model

The first data model should be explicit and easy to test. It can start with seed JSON/CSV files loaded into PostgreSQL, but the runtime source of truth should be structured tables.

### Core Entities

Recommended MVP entities:

- `Course`
- `Requirement`
- `RequirementGroup`
- `RequirementOption`
- `PrerequisiteExpression`
- `StudentRecord`
- `CompletedCourse`
- `PlannedCourse`
- `QuarterPlan`
- `SourceDocument`
- `DocumentChunk`

### Course Data

Courses should include:

- Stable ID.
- Subject code, such as `DSC`.
- Course number, such as `80`.
- Canonical course code, such as `DSC 80`.
- Title.
- Units.
- Description.
- Department.
- Lower or upper division.
- Known offering terms, if available.
- Source document reference.
- Data confidence status.

Unknown values should be stored as unknown, not guessed.

### Prerequisite Data

Prerequisites should support nested boolean logic. For the MVP, storing expressions as structured JSON is acceptable if validation and tests are strong.

Example:

```json
{
  "type": "AND",
  "requirements": [
    { "type": "COURSE", "course": "DSC 80" },
    {
      "type": "OR",
      "requirements": [
        { "type": "COURSE", "course": "MATH 20C" },
        { "type": "COURSE", "course": "MATH 31BH" }
      ]
    }
  ]
}
```

The evaluator should return:

- Eligible or blocked.
- Missing prerequisite branches.
- Satisfied prerequisite branches.
- Ambiguous prerequisites needing advisor confirmation.
- A human-readable explanation generated from structured evaluation results.

The LLM may phrase the explanation, but it should not decide whether the prerequisite is satisfied.

### Requirement Data

Requirement rules should support:

- Required courses.
- Course lists where a student must choose a subset.
- Minimum units.
- Category counts.
- Course overlap rules.
- Mutually exclusive courses.
- Exceptions requiring advisor confirmation.
- Source references.

Requirement evaluation should return:

- `satisfied`
- `missing`
- `partially_satisfied`
- `unknown`
- `needs_advisor_confirmation`

This status model matters because UCSD policies can include AP credit, transfer credit, substitutions, department approval, exceptions, and catalog-year differences.

### Source Documents

RAG source documents should include:

- Official source title.
- Source URL or local source path.
- UCSD department or college owner.
- Last ingested date.
- Effective academic year if known.
- Chunk text.
- Embedding vector.
- Citation metadata.

RAG answers should cite retrieved source documents and state when the answer depends on official advisor confirmation.

---

## MVP Academic Engines

### Requirement Checker

Given completed courses, the requirement checker should determine:

- Which Data Science major requirements are satisfied.
- Which Eighth College GE requirements are satisfied.
- Which requirements are missing.
- Which requirements are ambiguous.
- Which requirements require advisor confirmation.

This should be implemented as small, testable rule functions. Avoid embedding requirement logic directly in prompts.

### Prerequisite Checker

Given completed courses and a target course, the prerequisite checker should:

- Evaluate nested AND/OR prerequisite expressions.
- Identify courses the student can take now.
- Identify blocked courses.
- Explain missing prerequisites.
- Show prerequisite chains from available structured data.

For the MVP, NetworkX or simple recursive Python evaluation is enough. Neo4j is not required.

### Course Pathway Planner

The first planner should generate a rough quarter-by-quarter plan. It should:

- Never place a course before prerequisites are satisfied.
- Prioritize required courses that unlock future courses.
- Include major and GE progress.
- Keep units in a reasonable range, such as 12-16 units per quarter.
- Respect known course offering terms when available.
- Mark assumptions and unknowns clearly.

A simple greedy or scoring-based planner is enough for MVP.

Example scoring inputs:

```text
score =
+ satisfies required requirement
+ unlocks future required courses
+ matches stated interest
+ offered in target quarter
- high workload concentration
- uncertain availability
- advisor-confirmation dependency
```

### RAG Academic Advisor

RAG should answer natural-language academic questions using retrieved UCSD sources.

Flow:

```text
User question
        |
Embed question
        |
Search document chunks in PostgreSQL/pgvector
        |
Retrieve relevant UCSD source chunks
        |
Generate answer with citations
```

RAG should explain policies and context. It should not override structured requirement or prerequisite results.

### Semantic Course Search

Semantic course search should help students search by intent, such as:

- `machine learning`
- `AI`
- `biology`
- `ethics`
- `low writing`
- `easy GE`

The first version should combine vector similarity with structured filters, such as department, units, level, requirement category, and prerequisite eligibility.

---

## MVP API Surface

Suggested first endpoints:

```text
GET  /health
GET  /courses
GET  /courses/{course_code}
POST /students/{student_id}/completed-courses
GET  /students/{student_id}/requirements
GET  /students/{student_id}/eligible-courses
GET  /students/{student_id}/blocked-courses
POST /students/{student_id}/plans
POST /search/courses
POST /advisor/questions
```

The exact routes can change, but the API should preserve the separation between deterministic academic checks and RAG explanations.

---

## MVP Testing Priorities

Add tests as the engines are built:

- Prerequisite expression evaluation.
- Requirement satisfaction and missing requirement detection.
- Ambiguous or advisor-confirmation cases.
- Planner prerequisite ordering.
- Planner unit bounds.
- Planner handling of unknown course availability.
- RAG retrieval returns cited source chunks.
- LLM answers do not claim unsupported certainty.

Academic correctness should be tested before the UI becomes elaborate.

---

## MVP Development Order

Recommended implementation order:

1. Define seed data format for Data Science major requirements, Eighth College GE requirements, courses, and prerequisites.
2. Set up PostgreSQL with pgvector-capable local development.
3. Create the core course, prerequisite, requirement, student, and source-document tables.
4. Build and test prerequisite expression evaluation.
5. Build and test requirement evaluation.
6. Build basic student completed-course input.
7. Build rough planner with prerequisite ordering and unit bounds.
8. Add semantic course search over course descriptions.
9. Add RAG over official UCSD documents.
10. Build frontend views for requirements, eligible/blocked courses, plan output, and source-backed Q&A.

This order keeps the academic engine ahead of the conversational layer.

---

## Phase 2 Architecture

Phase 2 begins after the MVP can reliably evaluate requirements, evaluate prerequisites, and produce a rough plan for Data Science plus Eighth College.

### Phase 2 Goals

Phase 2 should improve quality, maintainability, and explainability:

- Harden official data ingestion.
- Improve source provenance and academic-year handling.
- Add saved plans and user accounts if needed.
- Add richer planner scoring.
- Add better prerequisite-chain visualization.
- Add more majors, colleges, or minors only when data modeling is stable.
- Consider Neo4j as a graph projection if graph queries become painful in Python or SQL.

### Optional Neo4j Graph Projection

Neo4j should be introduced only as a projection of trusted PostgreSQL data.

```text
FastAPI Backend
 ├── PostgreSQL + pgvector
 │    ├── source of truth
 │    ├── courses
 │    ├── prerequisites
 │    ├── requirements
 │    ├── student records
 │    ├── documents
 │    └── embeddings
 │
 └── Neo4j
      ├── prerequisite graph projection
      ├── course unlock graph
      ├── pathway queries
      └── visualization support
```

The key rule:

> PostgreSQL remains the source of truth. Neo4j is a synchronized graph projection.

Neo4j can help answer:

- What courses does `DSC 30` unlock?
- What path gets a student from `DSC 30` to `DSC 148`?
- Which required courses are bottlenecks?
- Which eligible courses unlock the most future options?
- Which courses connect a student to machine learning topics?

### Neo4j Sync Strategy

Start with a manual sync script:

```bash
python backend/app/scripts/sync_neo4j.py
```

The script should:

1. Read trusted course and prerequisite data from PostgreSQL.
2. Upsert `Course` nodes into Neo4j.
3. Upsert prerequisite relationships into Neo4j.
4. Store stable PostgreSQL IDs on Neo4j nodes.
5. Avoid treating Neo4j as editable source data.

Example Neo4j node:

```cypher
(:Course {
  postgres_id: 42,
  code: "DSC 80",
  department: "DSC",
  course_number: "80",
  title: "The Practice and Application of Data Science"
})
```

Progression:

```text
Phase 2a: Manual graph rebuild
Phase 2b: Scheduled graph sync
Phase 2c: Sync-on-write only if the product needs it
```

Sync-on-write is more complex and should wait until there is a real operational need.

### Phase 2 Planner Improvements

Planner improvements can include:

- Better unlock-value scoring.
- Workload labels.
- Interest weighting.
- Catalog-year awareness.
- Minor or specialization support.
- Alternative plan comparison.
- "Why this course now?" explanations.
- Warnings when data is incomplete.

Continue using a scoring or greedy planner until constraints become complex enough to justify OR-Tools.

### Phase 2 RAG Improvements

RAG improvements can include:

- Better document chunking.
- Source freshness checks.
- Academic-year filtering.
- Department or college source ownership.
- Citation quality scoring.
- Refusal behavior when sources are insufficient.
- Retrieval evaluation tests.

RAG should remain an explanation layer, not the authority for requirement satisfaction.

---

## Final Architecture

The final architecture can support a broader academic planning and schedule optimization platform.

### Final System Shape

```text
Next.js Frontend
        |
FastAPI Backend
        |
PostgreSQL + pgvector
        |
Optional Neo4j Graph Projection
        |
Optional Optimization Services
```

A more complete final backend view:

```text
FastAPI Backend
 ├── PostgreSQL + pgvector
 │    ├── courses
 │    ├── prerequisites
 │    ├── degree requirements
 │    ├── college requirements
 │    ├── student profiles
 │    ├── completed courses
 │    ├── planned courses
 │    ├── saved plans
 │    ├── academic documents
 │    ├── document chunks
 │    ├── embeddings
 │    └── audit logs
 │
 ├── Neo4j
 │    ├── prerequisite graph
 │    ├── course unlock graph
 │    ├── requirement graph
 │    └── pathway queries
 │
 └── Optimization Layer
      ├── rough academic plan generation
      ├── real schedule constraints
      ├── meeting-time conflict checks
      └── OR-Tools models when needed
```

### Final Capabilities

Long-term capabilities may include:

- More UCSD majors.
- More UCSD colleges.
- Minors and specializations.
- Catalog-year specific requirement sets.
- Transfer/AP credit modeling.
- Advisor-confirmation workflows.
- Real course offering ingestion.
- Meeting times and section combinations.
- Schedule conflict optimization.
- Student preference optimization.
- Better plan comparison and what-if analysis.

### OR-Tools Role

Google OR-Tools should be introduced when the problem becomes a real constraint optimization problem.

Good OR-Tools use cases:

- Meeting-time conflicts.
- Lab/discussion section combinations.
- Preferred time windows.
- Maximum daily course load.
- No-Friday or no-early-class preferences.
- Multiple valid plan alternatives.
- Tradeoffs between graduation speed, workload, and preferences.

For the MVP and much of Phase 2, a deterministic scoring planner is simpler and easier to debug.

### Production Architecture

Possible production setup:

```text
Frontend:
Vercel

Backend:
AWS ECS Fargate, Render, Railway, or similar

Primary Database:
AWS RDS PostgreSQL or AWS Aurora PostgreSQL with pgvector

Graph Database:
Neo4j AuraDB, only if graph projection is in use

File/Object Storage:
AWS S3 or equivalent

AI Provider:
OpenAI API or another supported model provider
```

For an early student-facing deployment, keep production simple:

```text
Frontend: Vercel
Backend: Render or Railway
Database: Managed PostgreSQL with pgvector
Graph Database: defer unless Phase 2 proves it is needed
```

---

## Data Ownership

| Data Type | MVP Location | Phase 2 / Final Location | Notes |
|---|---|---|---|
| Course metadata | PostgreSQL | PostgreSQL | Structured source-of-truth records |
| Prerequisite expressions | PostgreSQL | PostgreSQL, optionally projected to Neo4j | Store nested AND/OR logic explicitly |
| Requirement rules | PostgreSQL | PostgreSQL, optionally projected to Neo4j | Do not rely on prompts for rule checks |
| Student profile | PostgreSQL | PostgreSQL | Transactional user data |
| Completed courses | PostgreSQL | PostgreSQL, optionally projected to Neo4j | Needed for eligibility and planning |
| Planned courses | PostgreSQL | PostgreSQL | Saved outputs should be auditable |
| Source documents | PostgreSQL | PostgreSQL plus object storage if needed | Official UCSD sources preferred |
| Document chunks | PostgreSQL | PostgreSQL | RAG retrieval corpus |
| Embeddings | PostgreSQL with pgvector | PostgreSQL with pgvector | Avoid separate vector DB until needed |
| Chat/advisor answers | PostgreSQL | PostgreSQL | Useful for history and audit |
| Graph paths | Not required | Neo4j projection if useful | Derived data, not source of truth |

---

## Example End-to-End MVP Request

User asks:

```text
What path gets me from DSC 30 to machine learning courses?
```

MVP backend flow:

1. PostgreSQL retrieves the student's completed courses.
2. The prerequisite engine evaluates what the student can take now.
3. Semantic search finds course descriptions related to machine learning.
4. The planner or pathway module checks prerequisite chains using structured data.
5. PostgreSQL retrieves course metadata and requirement mappings.
6. The recommendation scorer ranks possible next courses.
7. RAG retrieves relevant UCSD source chunks.
8. The LLM explains the result with citations, using the structured engine output as facts.
9. The frontend displays eligible next steps, blocked paths, missing prerequisites, and source-backed explanation.

Phase 2 may replace step 4 with Neo4j path queries if that becomes useful.

---

## Guardrails

TritonPlan should:

- Prefer official UCSD sources for academic facts.
- Store exact academic rules in structured data.
- Use RAG only for grounded explanations and source-backed Q&A.
- Make uncertainty visible.
- Mark transfer credit, AP credit, exceptions, and substitutions as advisor-confirmation cases when rules are incomplete.
- Avoid silently inventing requirement rules, prerequisite rules, or course availability.
- Keep MVP scope narrow until the data model proves itself.

TritonPlan should not:

- Claim to replace an official UCSD advisor.
- Use LLM output as the source of truth for degree progress.
- Pretend live schedule, seat, or professor data exists before it is ingested.
- Expand to many majors or colleges before the first structured rules are reliable.

---

## Final Design Principle

TritonPlan should be built as an academic planning system where:

- PostgreSQL stores trusted academic and student data.
- Deterministic backend logic handles eligibility, requirement checks, and planning constraints.
- `pgvector` retrieves relevant academic context for RAG and semantic search.
- Neo4j is added later only if graph projection earns its complexity.
- OR-Tools is added later only when real scheduling constraints require it.
- The LLM explains results using retrieved context and structured engine outputs.
- The frontend presents planning decisions clearly enough for students to trust and question them.

The first successful version is not the one with the most infrastructure. It is the one that can correctly say: "You can take these courses now, these are blocked for these reasons, these requirements remain, and here is a source-backed explanation."
