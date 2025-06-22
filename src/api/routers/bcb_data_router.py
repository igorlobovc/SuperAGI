from fastapi import APIRouter, HTTPException
import pandas as pd
import os

router = APIRouter()

# Define path to processed data.
try:
    # This assumes the script is run from the project root or PYTHONPATH is set up.
    # For FastAPI run with uvicorn from root, 'src.data_processing' should be importable.
    # When this router file is executed, __file__ is src/api/routers/bcb_data_router.py
    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
except NameError:
    # Fallback if __file__ is not available (e.g. certain testing environments)
    # This might need adjustment based on actual execution context of the agent.
    PROJECT_ROOT = "." # Assume current working directory is project root

PROCESSED_DATA_DIR = os.path.join(PROJECT_ROOT, "data", "processed", "bcb_sgs")
IBC_BR_NATIONAL_FILE = os.path.join(PROCESSED_DATA_DIR, "ibc_br_national.csv")

# Attempt to import the processing script for fallback
try:
    from src.data_processing import process_bcb_sgs
    can_process_fallback = True
except ImportError:
    process_bcb_sgs = None # type: ignore
    can_process_fallback = False
    print("Warning: Could not import process_bcb_sgs. Fallback data generation will not be available for BCB data.")


@router.get("/ibc_br_national", summary="National IBC-Br Economic Activity Index")
async def get_ibc_br_national_data():
    """
    Provides the National Economic Activity Index (IBC-Br) from BCB SGS series 24363.
    Data is typically monthly.
    """
    if not os.path.exists(IBC_BR_NATIONAL_FILE):
        print(f"Data file not found: {IBC_BR_NATIONAL_FILE}")
        if can_process_fallback and process_bcb_sgs is not None:
            print("Attempting to process BCB SGS data for national IBC-Br on-the-fly...")
            try:
                process_bcb_sgs.process_national_ibc_br() # Try to generate the file
                if not os.path.exists(IBC_BR_NATIONAL_FILE):
                    raise HTTPException(status_code=404, detail="Processed IBC-Br national data file not found and could not be generated on-the-fly.")
            except Exception as e:
                print(f"Error during on-the-fly processing for national IBC-Br: {e}")
                raise HTTPException(status_code=500, detail=f"Failed to generate national IBC-Br data on-the-fly: {str(e)}")
        else:
            raise HTTPException(status_code=404, detail="Processed IBC-Br national data file not found. Fallback processing module not available.")

    try:
        df = pd.read_csv(IBC_BR_NATIONAL_FILE, parse_dates=['date'])
        df['date'] = df['date'].dt.strftime('%Y-%m-%d') # Ensure date is string for JSON
        return df.to_dict(orient="records")
    except FileNotFoundError:
         # This case should ideally be caught by the check above, but as a safeguard:
        raise HTTPException(status_code=404, detail="Processed IBC-Br national data file not found (post-check).")
    except Exception as e:
        print(f"Error reading or processing CSV {IBC_BR_NATIONAL_FILE}: {e}")
        raise HTTPException(status_code=500, detail=f"Could not load or parse national IBC-Br data: {str(e)}")

IBCR_NE_REGIONAL_FILE = os.path.join(PROCESSED_DATA_DIR, "ibcr_ne_regional.csv")

@router.get("/ibcr_northeast", summary="Northeast Regional Economic Activity Index (IBCR-NE)")
async def get_ibcr_ne_regional_data():
    """
    Provides the Northeast Regional Economic Activity Index (IBCR-NE) from BCB SGS series 25380.
    Data is typically monthly.
    """
    if not os.path.exists(IBCR_NE_REGIONAL_FILE):
        print(f"Data file not found: {IBCR_NE_REGIONAL_FILE}")
        if can_process_fallback and process_bcb_sgs is not None:
            print("Attempting to process BCB SGS data for regional IBCR-NE on-the-fly...")
            try:
                process_bcb_sgs.process_regional_ibcr_ne() # Try to generate the file
                if not os.path.exists(IBCR_NE_REGIONAL_FILE):
                    raise HTTPException(status_code=404, detail="Processed IBCR-NE regional data file not found and could not be generated on-the-fly.")
            except Exception as e:
                print(f"Error during on-the-fly processing for regional IBCR-NE: {e}")
                raise HTTPException(status_code=500, detail=f"Failed to generate regional IBCR-NE data on-the-fly: {str(e)}")
        else:
            raise HTTPException(status_code=404, detail="Processed IBCR-NE regional data file not found. Fallback processing module not available.")

    try:
        df = pd.read_csv(IBCR_NE_REGIONAL_FILE, parse_dates=['date'])
        df['date'] = df['date'].dt.strftime('%Y-%m-%d') # Ensure date is string for JSON
        return df.to_dict(orient="records")
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Processed IBCR-NE regional data file not found (post-check).")
    except Exception as e:
        print(f"Error reading or processing CSV {IBCR_NE_REGIONAL_FILE}: {e}")
        raise HTTPException(status_code=500, detail=f"Could not load or parse regional IBCR-NE data: {str(e)}")
