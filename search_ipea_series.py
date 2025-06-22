import ipeadatapy as ipea
import pandas as pd

# Set pandas to display full text in columns
pd.set_option('display.max_colwidth', None)
pd.set_option('display.max_columns', None) # Show all columns
pd.set_option('display.width', 1000) # Wider display for console

print("Searching for available series and fetching detailed metadata...\n")

search_terms = ["homicídio", "homicidios", "homicídios", "óbito", "óbitos", "morte", "mortes", "violência", "segurança"]
# More specific terms to try if broad ones are too noisy or miss specific datasets:
# search_terms.extend(["taxa de homicídios", "homicídios dolosos", "mortes violentas intencionais"])

detailed_metadata_list = []
processed_codes = set() # To avoid fetching metadata for the same code multiple times

for term in search_terms:
    print(f"Searching for term: '{term}'")
    try:
        # Step 1: Use list_series to get CODE and NAME
        found_series_overview = ipea.list_series(term)

        if not found_series_overview.empty and 'CODE' in found_series_overview.columns:
            print(f"Found {len(found_series_overview)} potential series for '{term}'. Fetching details...")
            for code in found_series_overview['CODE']:
                if code not in processed_codes:
                    try:
                        # Step 2: Get detailed metadata for each CODE
                        meta_result = ipea.metadata(code)
                        if meta_result is not None and not meta_result.empty:
                            # ipeadatapy's metadata() returns a DataFrame, not a Series as initially assumed for some series.
                            # We convert it to a dictionary from the first row.
                            if isinstance(meta_result, pd.DataFrame):
                                meta_dict = meta_result.iloc[0].to_dict()
                                detailed_metadata_list.append(meta_dict)
                                processed_codes.add(code)
                            elif isinstance(meta_result, pd.Series): # Should ideally be this
                                detailed_metadata_list.append(meta_result.to_dict())
                                processed_codes.add(code)
                            else:
                                print(f"Metadata for {code} is not a DataFrame or Series. Type: {type(meta_result)}. Skipping.")
                        else:
                            print(f"No detailed metadata returned for CODE: {code}")
                    except Exception as e_meta:
                        print(f"Error fetching metadata for CODE '{code}': {e_meta}")
        elif found_series_overview.empty:
            print(f"No series found for '{term}'.")
        else:
            print(f"Found series for '{term}', but 'CODE' column is missing. Columns: {found_series_overview.columns.tolist()}")

    except Exception as e_list:
        print(f"Error listing series for term '{term}': {e_list}")
    print("-" * 40)

if not detailed_metadata_list:
    print("No detailed metadata collected for any of the search terms.")
else:
    combined_metadata_df = pd.DataFrame(detailed_metadata_list)

    print(f"\nCollected {len(combined_metadata_df)} unique series metadata records.")
    if not combined_metadata_df.empty:
        actual_cols = combined_metadata_df.columns.tolist()
        print("Actual columns in combined_metadata_df:", actual_cols)

        # Updated list of columns to select/display based on observed output
        # Mapping: SERCODIGO -> CODE, SERNOME -> NAME, etc.
        # BASNOME seems to correspond to 'BIG THEME'
        display_cols_map = {
            'CODE': 'CODE', # SERCODIGO
            'NAME': 'NAME', # SERNOME
            'COMMENT': 'COMMENT', # SERCOMENTARIO
            'FREQUENCY': 'FREQUENCY', # PERNOME
            'UNIT': 'UNIT', # UNINOME
            'MEASURE': 'MEASURE', # Can also be part of unit or value description
            'SOURCE ACRONYM': 'SOURCE ACRONYM', # FNTSIGLA
            'SOURCE': 'SOURCE', # FNTNOME
            'BIG THEME': 'BIG THEME', # BASNOME (Regional, Social, Macroeconomico)
            # 'THEME CODE': 'THEME CODE', # TEMNOME would be useful if available directly
            'LAST UPDATE': 'LAST UPDATE' # SERATUALIZACAO
        }

        # Select columns that are actually present in the DataFrame
        cols_to_display = [col for col in display_cols_map.keys() if col in actual_cols]

        if not cols_to_display:
            print("None of the expected columns for display are present. Saving all available data.")
            print(combined_metadata_df)
            combined_metadata_df.to_csv("found_ipea_metadata_raw.csv", index=False)
            print("\nSaved all raw series metadata to found_ipea_metadata_raw.csv")
        else:
            print(f"\nDisplaying selected columns: {cols_to_display}")
            # Filter for relevant 'BIG THEME': 'Regional' or 'Social'
            # The column 'BIG THEME' seems to hold the 'Regional', 'Social' values.
            if 'BIG THEME' in combined_metadata_df.columns:
                regional_social_series = combined_metadata_df[combined_metadata_df['BIG THEME'].isin(['Regional', 'Social'])]

                if not regional_social_series.empty:
                    print("\n--- Filtered Regional and Social Series (Selected Columns) ---")
                    print(regional_social_series[cols_to_display])
                    regional_social_series[cols_to_display].to_csv("found_ipea_regional_social_metadata.csv", index=False)
                    print("\nSaved filtered regional and social series metadata to found_ipea_regional_social_metadata.csv")
                else:
                    print("\nNo Regional or Social series found. Displaying all series with selected columns.")
                    print(combined_metadata_df[cols_to_display])
                    combined_metadata_df[cols_to_display].to_csv("found_ipea_all_metadata_selected_cols.csv", index=False)
                    print("\nSaved all series metadata (selected columns) to found_ipea_all_metadata_selected_cols.csv")
            else:
                print("\n'BIG THEME' column not found. Displaying all series with selected columns.")
                print(combined_metadata_df[cols_to_display])
                combined_metadata_df[cols_to_display].to_csv("found_ipea_all_metadata_selected_cols.csv", index=False)
                print("\nSaved all series metadata (selected columns) to found_ipea_all_metadata_selected_cols.csv")
    else:
        print("Combined metadata DataFrame is empty after processing.")

print("\nScript finished.")
