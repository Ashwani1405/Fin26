
from fastapi import FastAPI, APIRouter

app = FastAPI(
    title="AI Personal CFO API",
    version="0.1.0",
    description="Financial Intelligence Backend"
)

from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware

# The following lines are added/modified based on the instruction
from app.api.v1.endpoints import transactions, analytics, simulation

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Allow frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

@app.on_event("startup")
async def on_startup():
    from app.core.database import engine
    from app.models.database_schema import Base
    async with engine.begin() as conn:
        # Create tables if they don't exist
        await conn.run_sync(Base.metadata.create_all)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
