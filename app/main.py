
from fastapi import FastAPI, APIRouter

app = FastAPI(
    title="AI Personal CFO API",
    version="0.1.0",
    description="Financial Intelligence Backend"
)

from fastapi.responses import RedirectResponse

# The following lines are added/modified based on the instruction
from app.api.v1.endpoints import transactions, analytics, simulation

# Define api_router here instead of importing it from app.api.v1.api
api_router = APIRouter()
api_router.include_router(transactions.router, prefix="/transactions", tags=["Transactions"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
api_router.include_router(simulation.router, prefix="/simulation", tags=["Simulation"])

app.include_router(api_router, prefix="/api/v1")

@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/docs")

@app.get("/health")
async def health_check():
    return {"status": "ok", "version": "0.1.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
