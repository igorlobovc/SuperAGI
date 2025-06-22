import ipeadatapy as ipea
import pandas as pd

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)

print("Fetching available territories...\n")

try:
    # Fetch all territories. This might be a large list.
    # The ipeadatapy documentation for get_serie mentions using territorial_level like 'Estados' or 'Regioes'
    # It does not explicitly show a function to list all territories and their specific codes for filtering,
    # but the get_serie function itself might accept names directly or we might need to find codes from the website.
    # Let's try fetching a known series for all states and all regions to see the territory names/codes used.

    print("Attempting to list states by fetching a sample series (e.g., POPULAÇÃO TOTAL for 'Estados')...")
    # Using a common series like population (e.g., 'POPT') to see state names/codes
    # From previous search, 'HOMIC' is a regional series. Let's try with it for states.
    # If ipea.timeseries('HOMIC', territorial_level='Estado') works, it will list all states.
    try:
        # Correct function is ipea.timeseries() based on dir(ipea)
        states_data = ipea.timeseries('HOMIC', territorial_level='Estado')
        if not states_data.empty:
            # The data is returned in a wide format usually, with states as columns or in a MultiIndex.
            # Let's see the structure.
            print("\nSample data with 'Estados' level:")
            print(states_data.head())

            # If territories are in columns:
            if isinstance(states_data.columns, pd.MultiIndex):
                state_names = states_data.columns.get_level_values(0).unique().tolist()
            else: # if in index or a single column
                if 'TERRITORIO' in states_data.columns: # Example column name
                    state_names = states_data['TERRITORIO'].unique().tolist()
                elif states_data.index.name == 'TERRITORIO':
                    state_names = states_data.index.unique().tolist()
                else: # Try to infer from column names if they are the territories
                    state_names = states_data.columns.tolist()

            print("\nPotential State Names/Codes found:")
            print(state_names)
            if 'Pernambuco' in state_names or 'PE' in state_names:
                print("Found 'Pernambuco' or 'PE'.")
            else:
                # Save to CSV to inspect all state names
                states_data.to_csv("debug_states_data.csv")
                print("Could not immediately confirm Pernambuco. Saved to debug_states_data.csv")

        else:
            print("Could not fetch sample data for states.")
    except Exception as e:
        print(f"Error fetching data for 'Estados': {e}")

    print("\n" + "-"*50 + "\n")

    print("Attempting to list regions by fetching a sample series (e.g., HOMIC for 'Regiões')...")
    try:
        # Correct function is ipea.timeseries() based on dir(ipea)
        regions_data = ipea.timeseries('HOMIC', territorial_level='Região')
        if not regions_data.empty:
            print("\nSample data with 'Regiões' level:")
            print(regions_data.head())

            if isinstance(regions_data.columns, pd.MultiIndex):
                region_names = regions_data.columns.get_level_values(0).unique().tolist()
            else: # if in index or a single column
                if 'TERRITORIO' in regions_data.columns: # Example column name
                    region_names = regions_data['TERRITORIO'].unique().tolist()
                elif regions_data.index.name == 'TERRITORIO':
                    region_names = regions_data.index.unique().tolist()
                else: # Try to infer from column names if they are the territories
                    region_names = regions_data.columns.tolist()

            print("\nPotential Region Names/Codes found:")
            print(region_names)
            if 'Nordeste' in region_names or 'NE' in region_names:
                print("Found 'Nordeste' or 'NE'.")
            else:
                regions_data.to_csv("debug_regions_data.csv")
                print("Could not immediately confirm Nordeste. Saved to debug_regions_data.csv")
        else:
            print("Could not fetch sample data for regions.")
    except Exception as e:
        print(f"Error fetching data for 'Regiões': {e}")

except Exception as e:
    print(f"An error occurred: {e}")

print("\nScript finished.")
