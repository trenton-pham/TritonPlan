# TritonPlan Agent Context

## Project Vision

TritonPlan is an AI-powered academic planning tool for UCSD students. It should behave like an academic planning engine, not just a chatbot. The product should help students understand major requirements, college GE requirements, prerequisites, and rough multi-quarter course plans.

The guiding principle is:

> Use structured logic for correctness and RAG for explanation.

LLMs may explain decisions, summarize policies, and answer advising-style questions, but they must not be the source of truth for degree progress or prerequisite satisfaction. Those decisions should come from structured data, rule logic, and graph algorithms.

## Initial MVP Scope

- University: UC San Diego only.
- Major: Data Science first.
- College: Eighth College GE requirements first.
- Planning mode: rough quarter-by-quarter planning.
- No live WebReg integration yet.
- No professor ratings, open seats, live course times, or schedule conflict optimization yet.
- Future versions can add real scheduling once UCSD course offering data is easier to scrape or ingest reliably.

## Core Product Features

### 1. Requirement Checker

Given a student's completed courses, determine:

- Which Data Science major requirements are satisfied.
- Which Eighth College GE requirements are satisfied.
- Which requirements are still missing.
- Which requirements need advisor confirmation because of ambiguity, transfer credit, AP credit, exceptions, or policy edge cases.

Requirement satisfaction should be computed with structured rules, not inferred by the LLM.

### 2. Prerequisite Checker

Model courses as a prerequisite graph:

- Each course is a node.
- Prerequisite relationships are edges.
- AND/OR logic must be represented explicitly.

Examples:

- `DSC 100` requires `DSC 80` AND `DSC 40B`.
- A course may allow `MATH 20C` OR `MATH 31BH`.

The graph layer should support:

- Finding courses the student can take now.
- Finding courses the student is blocked from taking.
- Explaining missing prerequisites.
- Showing prerequisite chains.
- Finding courses that unlock the most future options.
- Finding fastest paths toward advanced target courses.

### 3. Course Pathway Planner

Generate a rough quarter-by-quarter plan that:

- Prioritizes courses that unlock future courses.
- Avoids recommending courses before prerequisites are satisfied.
- Includes major, GE, and optional minor requirements.
- Keeps units in a reasonable range, such as 12-16 units per quarter.
- Balances workload when difficulty metadata exists.
- Uses known quarter availability when available, but does not pretend live schedule data exists.

The planner should optimize for:

- Graduation progress.
- Prerequisite unlock value.
- Interest match.
- Balanced workload.
- GE, major, and minor progress.

Subject to constraints:

- Prerequisites must be satisfied.
- Required courses should be included.
- Planned unit range should be respected.
- Course offering availability should be respected if known.
- Avoid too many difficult courses in the same quarter when difficulty labels exist.
- Future versions may add time conflicts, preferred times, professor preferences, and open seats.

### 4. RAG Academic Advisor

Use official UCSD documents as the knowledge base for natural-language advising answers.

The RAG flow should be:

1. User asks a question.
2. System retrieves relevant UCSD source documents.
3. LLM generates an answer grounded in those documents.
4. Answer cites or references the source documents used.

RAG is for explanation and policy interpretation. It should not override structured requirement checks.

### 5. Semantic Course Search

Allow students to search for courses by interest or intent, such as:

- "machine learning"
- "biology"
- "AI"
- "low writing"
- "ethics"
- "easy GE"

Use embeddings/vector search so results match meaning, not only exact keywords.

### 6. Future Schedule Builder

Later versions may add:

- Real course times.
- Professors.
- Open seats.
- Time conflicts.
- Preferred times.
- Workload and unit optimization.
- CAPE/rating-like signals if legally and technically appropriate.

This is not part of the first MVP.

## Recommended Technical Architecture

Use a hybrid architecture.

### Structured Database

Use structured storage for exact facts and rules:

- Courses.
- Units.
- Major requirements.
- GE requirements.
- Which courses satisfy which requirements.
- Prerequisites.
- Course categories.
- Quarter availability, if known.

PostgreSQL is a good default. If using Python first, clean JSON/CSV seed files are acceptable for the earliest prototype.

### Vector Database

Use vector storage for unstructured or messy academic text:

- UCSD catalog pages.
- Department advising pages.
- Four-year plans.
- FAQ pages.
- Policy explanations.
- Course descriptions.

Possible options:

- `pgvector`
- Chroma
- Pinecone
- Weaviate

### Backend

Reasonable backend options:

- FastAPI if the graph, planning, and optimization logic are primarily Python.
- Express if the project chooses a mostly TypeScript stack.

For the current project direction, FastAPI plus Python graph/planning logic is likely the simplest MVP path.

### Frontend

Reasonable frontend options:

- Next.js
- React

The UI should prioritize clarity and trust over flashy chatbot behavior. Students should see requirement status, blocked/unlocked courses, source-backed explanations, and suggested plans.

### Graph And Optimization

Good starting tools:

- NetworkX for prerequisite graph exploration.
- Python OR-Tools or a custom scoring algorithm for planning.
- Manual JSON/CSV for requirements until the data model stabilizes.

## Suggested Build Order

1. Manually create clean JSON/CSV for Data Science major requirements and Eighth College GE requirements.
2. Define a structured database schema or local structured data model.
3. Build the prerequisite graph.
4. Build the requirement checker.
5. Add RAG over official UCSD planning documents.
6. Add semantic course search.
7. Add a rough four-year or quarter-by-quarter planner.
8. Later add real schedule scraping and optimization.

## Data Modeling Notes

Agents should prefer explicit structured models over free-form text parsing wherever possible.

Recommended early entities:

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

Prerequisites should support nested boolean logic, such as:

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

Requirement rules should also support:

- Course lists.
- Minimum units.
- Category counts.
- Mutually exclusive courses.
- Overlap rules.
- Exceptions that need advisor confirmation.

## Known Shortcomings And Product Guardrails

- UCSD requirements are complicated and may not be fully machine-readable.
- GE rules differ by college, so MVP should only claim support for Eighth College.
- Prerequisites may include AP credit, transfer credit, concurrent enrollment, instructor consent, department approval, or other edge cases.
- Live course scheduling is out of scope until reliable data ingestion exists.
- Course difficulty is subjective unless based on labels, ratings, CAPE-like data, Reddit summaries, or manually curated metadata.
- RAG can hallucinate, so final academic decisions need structured rule checks.
- The system should warn users when an answer needs official advisor confirmation.
- TritonPlan should not claim to replace an official UCSD advisor.

## Agent Implementation Guidelines

- Keep MVP scope narrow: UCSD, Data Science, Eighth College.
- Prefer official UCSD sources for academic facts.
- Store exact academic rules in structured data.
- Use RAG only for grounded explanations and source-backed Q&A.
- Make uncertainty visible in the product.
- Do not silently invent requirement rules, prerequisite rules, or course availability.
- When data is incomplete, represent the unknown explicitly.
- Design APIs so additional majors, colleges, and minors can be added later without rewriting the core engine.
- Favor small, testable planning functions over opaque LLM-driven planning.
- Include tests for requirement satisfaction, prerequisite evaluation, and planner constraints as those systems are built.

## Out Of Scope For The MVP

- Full WebReg replacement.
- Live professor/time scheduler.
- Perfect graduation audit system.
- Open-seat tracking.
- Professor ratings.
- Automated enrollment.
- Claims of official academic advising authority.

