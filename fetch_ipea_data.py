import ipeadatapy as ipea
import pandas as pd

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)

# Series codes identified as relevant
SERIES_CODES = {
    "HOMIC": "Homicídios (Número Absoluto)",
    "THOMIC": "Taxa de Homicídios (por 100.000 hab.)"
}

# Territory information from previous exploration
TERRITORIES_INFO = {
    "Pernambuco": {"ID": "26", "LEVEL_NAME": "Estados"}, # From ipea.territories(), LEVEL was 'Estados'
    "Nordeste": {"ID": "2", "LEVEL_NAME": "Regiões"}    # From ipea.territories(), LEVEL was 'Regiões'
}

# The timeseries output had NIVNOME as the level name column
# and TERCODIGO as the territory ID column.

def fetch_and_filter_data(series_code, series_name, territory_label, tercodigo, nivnome):
    print(f"\nFetching data for series: {series_name} ({series_code}) for {territory_label}...")
    try:
        # Fetch the full timeseries for all territories/levels
        full_data = ipea.timeseries(series_code)

        if full_data is None or full_data.empty:
            print(f"No data returned for series {series_code}.")
            return None

        # Ensure required columns are present
        required_cols = ['TERCODIGO', 'NIVNOME', 'YEAR', 'VALUE (Unidade)'] # Assuming 'YEAR' and 'VALUE (Unidade)' exist
        if not all(col in full_data.columns for col in required_cols):
            print(f"Missing one or more required columns in data for {series_code}. Available: {full_data.columns.tolist()}")
            # Try to find value column if it's dynamic (e.g. VALUE (some_unit) or just VALUE)
            value_col_found = None
            for col in full_data.columns:
                if "VALUE" in col.upper(): # Generic check for value column
                    value_col_found = col
                    break
            if not value_col_found:
                 print("Could not identify a VALUE column.")
                 return None
            else:
                print(f"Using identified value column: {value_col_found}")
                # Adjust required_cols if needed, or handle it in selection. For now, focus on filtering.
                # This script will assume 'VALUE (Unidade)' or a similar single value column from previous observation.
                # If value column name is different, the selection part needs to be robust.

        # Filter for the specific territory
        # Comparing TERCODIGO as string, as it appeared like that in sample output.
        filtered_df = full_data[
            (full_data['TERCODIGO'] == tercodigo) &
            (full_data['NIVNOME'] == nivnome)
        ]

        if filtered_df.empty:
            print(f"No data found for {territory_label} ({nivnome} ID {tercodigo}) in series {series_code} after filtering.")
            print("This might be because the series is not available for this specific territory/level combination.")
            print("Full data columns were:", full_data.columns.tolist())
            print("Unique TERCODIGOs in full_data:", full_data['TERCODIGO'].unique()[:10])
            print("Unique NIVNOMEs in full_data:", full_data['NIVNOME'].unique()[:10])
            return None

        print(f"Successfully fetched and filtered data for {series_name} - {territory_label}.")

        # Select relevant columns for the sample: YEAR, VALUE
        # The value column name might vary, e.g., 'VALUE (Unidade)', 'VALUE (%)'
        # Let's try to find it dynamically or use the one observed for HOMIC
        value_column_name = 'VALUE (Unidade)' # Default based on HOMIC output
        if value_column_name not in filtered_df.columns:
            # Try to find a column that starts with 'VALUE'
            for col in filtered_df.columns:
                if col.startswith('VALUE'):
                    value_column_name = col
                    break

        if value_column_name not in filtered_df.columns:
            print(f"Could not determine the value column for {series_code}. Available: {filtered_df.columns.tolist()}")
            return filtered_df # Return filtered but without specific column selection

        # Ensure DATE is the index for time series consistency, or YEAR is present
        if 'YEAR' in filtered_df.columns:
            final_df = filtered_df[['YEAR', value_column_name]].copy()
            final_df.rename(columns={value_column_name: series_name}, inplace=True)
            final_df.sort_values(by='YEAR', inplace=True)
        elif 'DATE' in filtered_df.index.name: # If DATE is already index
             final_df = filtered_df[[value_column_name]].copy()
             final_df.rename(columns={value_column_name: series_name}, inplace=True)
        else: # Fallback if neither YEAR column nor DATE index is straightforward
            print("YEAR column not found, and DATE not index. Saving available relevant columns.")
            # Attempt to keep TERCODIGO, NIVNOME, RAW DATE, and the value column
            display_cols = [col for col in ['RAW DATE', 'TERCODIGO', 'NIVNOME', value_column_name] if col in filtered_df.columns]
            final_df = filtered_df[display_cols]

        return final_df

    except Exception as e:
        print(f"Error processing series {series_code} for {territory_label}: {e}")
        return None

# --- Main script execution ---
all_final_data = {}

for terr_label, terr_info in TERRITORIES_INFO.items():
    tercod = terr_info["ID"]
    nivnome_filter = terr_info["LEVEL_NAME"] # This should match NIVNOME in the data

    datasets_for_territory = []
    for series_code, series_desc_name in SERIES_CODES.items():
        df = fetch_and_filter_data(series_code, series_desc_name, terr_label, tercod, nivnome_filter)
        if df is not None and not df.empty:
            datasets_for_territory.append(df.set_index('YEAR') if 'YEAR' in df.columns else df)
            # YEAR as index for potential merge

    # Merge datasets for the current territory if multiple series were fetched
    if len(datasets_for_territory) > 1:
        # Assuming 'YEAR' was made the index for all
        merged_df = pd.concat(datasets_for_territory, axis=1)
        all_final_data[terr_label] = merged_df.reset_index()
    elif len(datasets_for_territory) == 1:
        all_final_data[terr_label] = datasets_for_territory[0].reset_index()
    else:
        print(f"No datasets successfully fetched for {terr_label}.")


# Save the sample data
for territory_label, df_sample in all_final_data.items():
    if df_sample is not None and not df_sample.empty:
        sample_filename = f"{territory_label.lower().replace(' ', '_')}_homicides_sample.csv"
        df_sample.to_csv(sample_filename, index=False)
        print(f"\nSaved sample data for {territory_label} to {sample_filename}")
        print(df_sample.head())
    else:
        print(f"\nNo data to save for {territory_label}.")

print("\nScript finished.")
