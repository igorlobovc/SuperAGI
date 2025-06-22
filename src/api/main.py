from fastapi import FastAPI

app = FastAPI(
    title="Pernambuco Economic Dashboard API",
    description="API to serve data for the Pernambuco economic, political, and financial overview dashboard.",
    version="0.1.0"
)

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Pernambuco Economic Dashboard API"}

@app.get("/health", tags=["General"])
async def health_check():
    """
    Simple health check endpoint.
    Returns the operational status of the API.
    """
    return {"status": "ok", "message": "API is healthy"}

# Import and include routers
from .routers import bcb_data_router
# Potentially other routers in the future
# from .routers import siconfi_data_router
# from .routers import sefaz_data_router

app.include_router(bcb_data_router.router, prefix="/api/v1/bcb", tags=["BCB SGS Data"])
# app.include_router(siconfi_data_router.router, prefix="/api/v1/siconfi", tags=["SICONFI Data"])
# app.include_router(sefaz_data_router.router, prefix="/api/v1/sefaz", tags=["SEFAZ PE Data"])


# To run this application locally (for development):
# Ensure you are in the project root directory (the one containing 'src')
# Command: uvicorn src.api.main:app --reload --port 8000
#
# The __main__ block below is an alternative way to run for simple local testing,
# but using the uvicorn command directly is more standard for FastAPI development.
if __name__ == "__main__":
    import uvicorn
    # Note: Running directly like this might have issues with relative imports if routers are in subdirectories
    # depending on how PYTHONPATH is configured. The uvicorn command from project root is preferred.
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, app_dir=os.path.dirname(__file__))

# Create an __init__.py in src/api to make it a package
# Create a subdirectory src/api/routers for organizing route files.
# Example router file: src/api/routers/bcb_data_router.py
"""
from fastapi import APIRouter
import pandas as pd
import os

router = APIRouter()

# Conceptual path, adjust based on actual project structure
PROCESSED_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data", "processed", "bcb_sgs")


@router.get("/ibc_br_national")
async def get_ibc_br_national_data():
    file_path = os.path.join(PROCESSED_DATA_DIR, "ibc_br_national.csv")
    if not os.path.exists(file_path):
        return {"error": "Processed data not found."}
    try:
        df = pd.read_csv(file_path)
        return df.to_dict(orient="records")
    except Exception as e:
        return {"error": f"Could not load or parse data: {str(e)}"}
"""
