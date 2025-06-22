import ipeadatapy as ipea
import pandas as pd

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)

print("Exploring ipea.territories()...\n")
try:
    all_territories = ipea.territories()
    if all_territories is not None and not all_territories.empty:
        print("ipea.territories() output:")
        print(all_territories.head())
        print(f"\nShape of territories DataFrame: {all_territories.shape}")
        print(f"\nColumns: {all_territories.columns.tolist()}")

        # Check for Pernambuco and Nordeste
        pernambuco_pe_df = all_territories[all_territories['NAME'].str.contains('Pernambuco', case=False, na=False)]
        print("\nTerritories containing 'Pernambuco':")
        print(pernambuco_pe_df)

        nordeste_ne_df = all_territories[all_territories['NAME'].str.contains('Nordeste', case=False, na=False)]
        print("\nTerritories containing 'Nordeste':")
        print(nordeste_ne_df)

        # Avoid saving all_territories if it's too large and caused issues before.
        # The print statements for Pernambuco and Nordeste should be enough.
        # all_territories.to_csv("ipea_all_territories.csv", index=False)
        # print("\nSaved all territories to ipea_all_territories.csv")
        if pernambuco_pe_df.empty:
            print("Pernambuco not found by simple string search in territories.")
        if nordeste_ne_df.empty:
            print("Nordeste not found by simple string search in territories.")
            print("Consider listing unique values in 'NIVNOME' (territorial level name) if available from ipea.territories() columns.")
            if 'NIVNOME' in all_territories.columns:
                print("Unique NIVNOME values:", all_territories['NIVNOME'].unique())


    else:
        print("ipea.territories() returned None or empty.")

except Exception as e:
    print(f"Error calling ipea.territories(): {e}")

print("\nNow trying to understand how to use territorial filtering with ipea.timeseries(code).")
print("The ipeadata API docs (http://www.ipeadata.gov.br/api/) mention OData filters like:")
print("Metadados('{SERCODIGO}')/Valores?$filter=NIVNOME eq 'Estado' and TERNOME eq 'Pernambuco'")
print("Perhaps the timeseries function needs a specific series code that already includes territory, or has no direct territory filtering.")

print("\nLet's try fetching 'HOMIC' without any territorial level and see what it returns.")
try:
    homic_data_all_levels = ipea.timeseries('HOMIC')
    if homic_data_all_levels is not None and not homic_data_all_levels.empty:
        print("\nData for 'HOMIC' (all available levels):")
        print(homic_data_all_levels.head())
        print(f"Columns: {homic_data_all_levels.columns.tolist()}")
        # If it has a territory column, that's our clue.
        # Common names could be 'TERRITORIO', 'NIVEL', 'TERCODIGO', 'TERNOME', 'TERRA', 'Territorialidades', etc.
        # Avoid saving the full CSV to prevent sandbox size errors.
        # homic_data_all_levels.to_csv("homic_data_all_levels.csv")
        # print("Saved homic_data_all_levels.csv for inspection.")
        print("Inspect the columns and head output above to understand territorial filtering for timeseries().")
        if 'TERNOME' in homic_data_all_levels.columns: # TERNOME is a common name for territory name
            print("Unique territory names in HOMIC data sample:", homic_data_all_levels['TERNOME'].unique()[:20]) # Show a few
        elif 'TERRITORIO' in homic_data_all_levels.columns:
             print("Unique territory names in HOMIC data sample:", homic_data_all_levels['TERRITORIO'].unique()[:20]) # Show a few


    else:
        print("Fetching 'HOMIC' data for all levels returned None or empty.")
except Exception as e:
    print(f"Error fetching 'HOMIC' data for all levels: {e}")

print("\nScript finished.")
