import requests
import json
import os
from datetime import datetime, timedelta

def fetch_sgs_data(series_code, years_to_fetch=5):
    """
    Fetches time series data from BCB SGS API for a given series code.
    Fetches data for the last 'years_to_fetch' full years plus current year to date.
    """
    base_url = f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.{series_code}/dados"

    today = datetime.today()
    # Ensure end_date is not in the future if today is used for file naming
    # For API query, BCB handles future dates gracefully (returns up to latest available)
    query_end_date_str = today.strftime("%d/%m/%Y")

    # Go back N full years from the beginning of the current year for a consistent period
    current_year_start = datetime(today.year, 1, 1)
    start_date = datetime(today.year - years_to_fetch, 1, 1)
    query_start_date_str = start_date.strftime("%d/%m/%Y")

    params = {
        "formato": "json",
        "dataInicial": query_start_date_str,
        "dataFinal": query_end_date_str
    }

    # Use a fixed reference for file naming if needed, or make it dynamic
    # For simplicity in the agent, using dynamic dates for file name.
    file_name_start_date = start_date.strftime('%Y%m%d')
    file_name_end_date = today.strftime('%Y%m%d') # Use actual today for file name end date

    # Define save path relative to the project root
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) if "__file__" in globals() else "."
    raw_data_dir = os.path.join(project_root, "data", "raw", "bcb_sgs")

    try:
        os.makedirs(raw_data_dir, exist_ok=True)
    except OSError as e:
        print(f"Error creating directory {raw_data_dir}: {e}")
        return None, None

    file_path_json = os.path.join(raw_data_dir, f"sgs_{series_code}_{file_name_start_date}_{file_name_end_date}.json")

    print(f"Fetching data for series {series_code} from {query_start_date_str} to {query_end_date_str}...")
    api_url_with_params = f"{base_url}?formato=json&dataInicial={query_start_date_str}&dataFinal={query_end_date_str}"
    print(f"API URL: {api_url_with_params}")

    response = None # Initialize response to None
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()

        with open(file_path_json, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"Successfully downloaded and saved data to {file_path_json}")

        if isinstance(data, list) and len(data) > 0:
            print(f"\nSample of fetched data for series {series_code} (first 3 records):")
            for record in data[:3]:
                print(record)
            if len(data) > 3:
                print("...")
                print(data[-1]) # Also print last record
        elif isinstance(data, dict):
             print(f"\nAPI for series {series_code} returned a dictionary: {data}")
        else:
            print(f"\nFetched data for series {series_code} is not in the expected list format or is empty.")

        return data, file_path_json
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data for series {series_code} from BCB SGS API: {e}")
        if response is not None:
            print(f"Response status code: {response.status_code}")
            print(f"Response content: {response.text[:500]}...") # Print first 500 chars of error
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON response for series {series_code}: {e}")
        if response is not None:
            print(f"Response content: {response.text[:500]}...")
    except Exception as e:
        print(f"An unexpected error occurred for series {series_code}: {e}")
    return None, None

if __name__ == "__main__":
    # IBC-Br (Índice de Atividade Econômica do Banco Central) - Nacional
    # This is an index, seasonally adjusted.
    ibc_br_code = 24363

    print(f"--- Fetching IBC-Br (National) - Code: {ibc_br_code} ---")
    fetch_sgs_data(ibc_br_code, years_to_fetch=5)

    # Example: Selic rate (daily) - code 11
    # selic_code = 11
    # print(f"\n--- Fetching Selic (National) - Code: {selic_code} ---")
    # fetch_sgs_data(selic_code, years_to_fetch=1) # Fetch 1 year for daily series to keep it small

    # Example: IPCA (monthly) - code 433 (Índice nacional de preços ao consumidor-amplo (IPCA))
    # ipca_code = 433
    # print(f"\n--- Fetching IPCA (National) - Code: {ipca_code} ---")
    # fetch_sgs_data(ipca_code, years_to_fetch=5)

    # Placeholder for a known regional series if one is found later
    # For example, IBCR-NE (Índice de Atividade Econômica Regional - Nordeste dessazonalizado)
    # Code for IBCR-NE is 25380 (found via external search as internal search is blocked)
    ibcr_ne_code = 25380
    print(f"\n--- Fetching IBCR-NE (Northeast Regional Economic Activity) - Code: {ibcr_ne_code} ---")
    fetch_sgs_data(ibcr_ne_code, years_to_fetch=5)
