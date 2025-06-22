import pandas as pd
import json
import os
import requests # Added for fallback fetching
from datetime import datetime, timedelta # Added for fallback fetching

# Define project root dynamically for better path handling
try:
    # Assuming this script is in src/data_processing/
    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
except NameError: # __file__ is not defined, e.g. in an interactive environment
    # Fallback for environments where __file__ is not available
    PROJECT_ROOT = os.path.abspath(os.path.join(os.getcwd(), os.pardir, os.pardir)) if os.path.basename(os.getcwd()) == "data_processing" else os.path.abspath(".")


RAW_DATA_DIR = os.path.join(PROJECT_ROOT, "data", "raw", "bcb_sgs")
PROCESSED_DATA_DIR = os.path.join(PROJECT_ROOT, "data", "processed", "bcb_sgs")

def fetch_sgs_data_fallback(series_code, years_to_fetch=5):
    """
    Fallback: Fetches time series data directly if local file is not found.
    """
    base_url = f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.{series_code}/dados"
    today = datetime.today()
    start_date = datetime(today.year - years_to_fetch, 1, 1)
    query_start_date_str = start_date.strftime("%d/%m/%Y")
    query_end_date_str = today.strftime("%d/%m/%Y")

    params = {
        "formato": "json",
        "dataInicial": query_start_date_str,
        "dataFinal": query_end_date_str
    }
    print(f"Fallback: Fetching data for series {series_code} from API ({query_start_date_str} to {query_end_date_str})...")
    response = None
    try:
        response = requests.get(base_url, params=params, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Fallback fetch error for series {series_code}: {e}")
        if response is not None:
            print(f"Response status: {response.status_code}, content: {response.text[:200]}")
        return None
    except Exception as e:
        print(f"Unexpected error during fallback fetch for series {series_code}: {e}")
        return None


def find_raw_data_file(series_code):
    """Finds the most recent raw data file for a given series code."""
    if not os.path.exists(RAW_DATA_DIR):
        print(f"Raw data directory not found: {RAW_DATA_DIR}")
        return None

    relevant_files = [f for f in os.listdir(RAW_DATA_DIR) if f.startswith(f"sgs_{series_code}_") and f.endswith(".json")]
    if not relevant_files:
        print(f"No raw data files found for series {series_code} in {RAW_DATA_DIR}")
        return None

    latest_file = ""
    latest_end_date = None

    for f_name in relevant_files:
        try:
            parts = f_name.replace(".json", "").split("_")
            end_date_str_from_file = parts[-1]
            current_file_end_date = datetime.strptime(end_date_str_from_file, '%Y%m%d')
            if latest_end_date is None or current_file_end_date > latest_end_date:
                latest_end_date = current_file_end_date
                latest_file = f_name
        except Exception: # Catch broader exceptions for file name parsing
            # print(f"Warning: Could not parse date from filename {f_name}: {e}")
            continue

    return os.path.join(RAW_DATA_DIR, latest_file) if latest_file else None


def process_national_ibc_br():
    """Processes the national IBC-Br data (SGS Code 24363)."""
    series_code = 24363
    print(f"\n--- Processing National IBC-Br (SGS: {series_code}) ---")

    raw_file_path = find_raw_data_file(series_code)
    data = None

    if raw_file_path and os.path.exists(raw_file_path):
        print(f"Loading raw data from: {raw_file_path}")
        try:
            with open(raw_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            print(f"Error loading JSON from {raw_file_path}: {e}")
            data = None # Ensure data is None if loading fails

    if not data: # If file not found, or failed to load, attempt fallback
        print(f"Raw data file for series {series_code} not found or failed to load. Attempting fallback API fetch.")
        data = fetch_sgs_data_fallback(series_code, years_to_fetch=10) # Fetch more years for fallback

    if not data or not isinstance(data, list) or not data: # Check if data is empty list
        print(f"No data loaded or data is not in list format for series {series_code}. Skipping processing.")
        return

    df = pd.DataFrame(data)
    if df.empty:
        print(f"DataFrame is empty for series {series_code} after loading. Skipping processing.")
        return

    # print(f"Raw data columns for series {series_code}: {df.columns.tolist()}")
    # print(f"First few rows of raw data for series {series_code}:\n{df.head()}")

    if 'data' not in df.columns or 'valor' not in df.columns:
        print(f"Error: Expected columns 'data' and 'valor' not found in series {series_code}.")
        return

    try:
        df['date'] = pd.to_datetime(df['data'], format='%d/%m/%Y')
        df['ibc_br_index_national'] = pd.to_numeric(df['valor'], errors='coerce')
    except Exception as e:
        print(f"Error converting data types for series {series_code}: {e}")
        return

    processed_df = df[['date', 'ibc_br_index_national']].copy()
    processed_df.dropna(subset=['ibc_br_index_national'], inplace=True)
    processed_df.sort_values(by='date', inplace=True)

    try:
        os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)
    except OSError as e:
        print(f"Error creating processed data directory {PROCESSED_DATA_DIR}: {e}")
        return

    output_path = os.path.join(PROCESSED_DATA_DIR, "ibc_br_national.csv")
    try:
        processed_df.to_csv(output_path, index=False, date_format='%Y-%m-%d')
        print(f"Processed national IBC-Br data saved to: {output_path}")
        # print(f"Processed DataFrame head:\n{processed_df.head()}")
    except Exception as e:
        print(f"Error saving processed data for series {series_code} to {output_path}: {e}")

def process_regional_ibcr_ne():
    """Processes the Northeast IBCR-NE data (SGS Code 25380)."""
    series_code = 25380
    print(f"\n--- Processing Northeast IBCR-NE (SGS: {series_code}) ---")

    raw_file_path = find_raw_data_file(series_code)
    data = None

    if raw_file_path and os.path.exists(raw_file_path):
        print(f"Loading raw data from: {raw_file_path}")
        try:
            with open(raw_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            print(f"Error loading JSON from {raw_file_path}: {e}")
            data = None

    if not data:
        print(f"Raw data file for series {series_code} not found or failed to load. Attempting fallback API fetch.")
        data = fetch_sgs_data_fallback(series_code, years_to_fetch=10)

    if not data or not isinstance(data, list) or not data:
        print(f"No data loaded or data is not in list format for series {series_code}. Skipping processing.")
        return

    df = pd.DataFrame(data)
    if df.empty:
        print(f"DataFrame is empty for series {series_code} after loading. Skipping processing.")
        return

    if 'data' not in df.columns or 'valor' not in df.columns:
        print(f"Error: Expected columns 'data' and 'valor' not found in series {series_code}.")
        return

    try:
        df['date'] = pd.to_datetime(df['data'], format='%d/%m/%Y')
        df['ibcr_index_northeast'] = pd.to_numeric(df['valor'], errors='coerce')
    except Exception as e:
        print(f"Error converting data types for series {series_code}: {e}")
        return

    processed_df = df[['date', 'ibcr_index_northeast']].copy()
    processed_df.dropna(subset=['ibcr_index_northeast'], inplace=True)
    processed_df.sort_values(by='date', inplace=True)

    try:
        os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)
    except OSError as e:
        print(f"Error creating processed data directory {PROCESSED_DATA_DIR}: {e}")
        return

    output_path = os.path.join(PROCESSED_DATA_DIR, "ibcr_ne_regional.csv")
    try:
        processed_df.to_csv(output_path, index=False, date_format='%Y-%m-%d')
        print(f"Processed Northeast IBCR-NE data saved to: {output_path}")
        # print(f"Processed DataFrame head:\n{processed_df.head()}")
    except Exception as e:
        print(f"Error saving processed data for series {series_code} to {output_path}: {e}")


if __name__ == "__main__":
    # Create dummy project root for local testing if needed
    if PROJECT_ROOT == ".": # Simple check if fallback was used
        # This block is for local testing convenience if script is run directly
        # and not from the assumed project structure during agent execution.
        if not os.path.exists(os.path.join("data", "raw", "bcb_sgs")):
            os.makedirs(os.path.join("data", "raw", "bcb_sgs"), exist_ok=True)
        if not os.path.exists(os.path.join("data", "processed", "bcb_sgs")):
            os.makedirs(os.path.join("data", "processed", "bcb_sgs"), exist_ok=True)

    process_national_ibc_br()
    process_regional_ibcr_ne()
