from fastapi import FastAPI

app = FastAPI(title="TritonPlan API")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "tritonplan-backend"}
