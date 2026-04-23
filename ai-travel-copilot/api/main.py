from fastapi import FastAPI
from api.routes_plan import router as plan_router

app = FastAPI(title="Travel Planner Agent", version="0.2.0")
app.include_router(plan_router)


@app.get("/health")
def health_check() -> dict:
    return {"status": "ok", "service": "travel-planner"}
