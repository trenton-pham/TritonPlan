# Testing FastAPI With Postgres

This file is a quick manual checklist for testing the database-backed FastAPI course endpoints.

## 1. Start the containers

From the project root, start FastAPI, Postgres, and the frontend:

```bash
docker compose up --build
```

This starts:

- The FastAPI backend at `http://localhost:8000`
- The Postgres database container
- The frontend at `http://localhost:3000`

Wait until the backend logs show that the application startup is complete.

## 2. Open a Postgres shell

In a second terminal, connect to the Postgres container:

```bash
docker compose exec postgres psql -U tritonplan -d tritonplan
```

This opens an interactive SQL shell connected to the `tritonplan` database.

## 3. Seed one test course

Paste this SQL into the Postgres shell to create a sample `DSC 80` course row:

```sql
INSERT INTO courses (
    id,
    subject,
    number,
    code,
    title,
    units,
    department,
    division,
    description,
    known_offering_terms,
    source_refs,
    data_confidence
)
VALUES (
    gen_random_uuid(),
    'DSC',
    '80',
    'DSC 80',
    'The Practice and Application of Data Science',
    4,
    'Data Science',
    'Lower Division',
    'Practice-oriented data science course.',
    '[]'::jsonb,
    '[]'::jsonb,
    'manual_seed'
);
```

If the row already exists, Postgres may reject the insert because `code` is
unique. That is expected when you have already seeded the test data.

## 4. Verify the API in FastAPI docs

Open the interactive FastAPI docs:

```text
http://localhost:8000/docs
```

Test these endpoints:

```text
GET /health
GET /courses
GET /courses/{course_code}
```

For `GET /courses/{course_code}`, use:

```text
DSC 80
```
## Expected result

The `GET /courses/DSC%2080` request should return a JSON response similar to:

```json
{
  "code": "DSC 80",
  "subject": "DSC",
  "number": "80",
  "title": "The Practice and Application of Data Science",
  "units": 4,
  "department": "Data Science",
  "division": "Lower Division",
  "description": "Practice-oriented data science course.",
  "known_offering_terms": [],
  "source_refs": [],
  "data_confidence": "manual_seed"
}
```

Results should be the same even with caps/lowercase.

The browser URL version should be:

```text
http://localhost:8000/courses/DSC%2080
```

`%20` represents the space between `DSC` and `80`.
