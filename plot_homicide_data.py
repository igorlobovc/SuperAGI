import pandas as pd
import matplotlib.pyplot as plt
import os

def generate_plot(csv_filepath, year_column, value_columns_map, title_prefix, output_dir="plots"):
    """
    Generates and saves a line plot from a CSV file.

    Args:
        csv_filepath (str): Path to the input CSV file.
        year_column (str): Name of the column containing year data.
        value_columns_map (dict): A dictionary where keys are column names to plot
                                  and values are their desired legend labels.
        title_prefix (str): Prefix for the plot title and output filename.
        output_dir (str): Directory to save the plot images.
    """
    try:
        df = pd.read_csv(csv_filepath)
    except FileNotFoundError:
        print(f"Error: CSV file not found at {csv_filepath}")
        return

    if year_column not in df.columns:
        print(f"Error: Year column '{year_column}' not found in {csv_filepath}")
        return

    plt.figure(figsize=(12, 6))

    plot_title_suffix_parts = []
    for value_column, legend_label in value_columns_map.items():
        if value_column not in df.columns:
            print(f"Warning: Value column '{value_column}' not found in {csv_filepath}. Skipping this column.")
            continue
        plt.plot(df[year_column], df[value_column], label=legend_label, marker='o', linestyle='-')
        plot_title_suffix_parts.append(legend_label)

    if not plot_title_suffix_parts:
        print(f"No valid value columns found to plot for {csv_filepath}.")
        plt.close() # Close the empty figure
        return

    plot_title_suffix = " & ".join(plot_title_suffix_parts)
    plt.title(f"{title_prefix}: {plot_title_suffix} Over Time")
    plt.xlabel("Year")
    plt.ylabel("Value (Count / Rate per 100k)")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created directory: {output_dir}")

    # Sanitize title_prefix and plot_title_suffix for filename
    filename_prefix = title_prefix.lower().replace(" ", "_").replace("(", "").replace(")", "")
    filename_suffix = plot_title_suffix.lower().replace(" ", "_").replace("/", "_").replace("&", "and").replace("(", "").replace(")", "")
    output_filename = os.path.join(output_dir, f"{filename_prefix}_{filename_suffix}.png")

    plt.savefig(output_filename)
    print(f"Plot saved to {output_filename}")
    plt.close() # Close the figure to free memory

if __name__ == "__main__":
    # Define data files and columns to plot
    data_files_info = {
        "pernambuco": {
            "filepath": "pernambuco_homicides_sample.csv",
            "plots": [
                {"cols_map": {"Homicídios (Número Absoluto)": "Absolute Homicides"}, "suffix": "Absolute Numbers"},
                {"cols_map": {"Taxa de Homicídios (por 100.000 hab.)": "Homicide Rate (per 100k)"}, "suffix": "Rates"}
            ]
        },
        "nordeste": {
            "filepath": "nordeste_homicides_sample.csv",
            "plots": [
                {"cols_map": {"Homicídios (Número Absoluto)": "Absolute Homicides"}, "suffix": "Absolute Numbers"},
                {"cols_map": {"Taxa de Homicídios (por 100.000 hab.)": "Homicide Rate (per 100k)"}, "suffix": "Rates"}
            ]
        }
    }

    # Generate plots
    for territory_name, info in data_files_info.items():
        csv_file = info["filepath"]
        for plot_def in info["plots"]:
            # The title prefix will be like "Pernambuco Homicides" or "Nordeste Homicide Rates"
            # The actual series name is used in the legend and plot title by the function.
            generate_plot(
                csv_filepath=csv_file,
                year_column="YEAR",
                value_columns_map=plot_def["cols_map"],
                title_prefix=f"{territory_name.capitalize()} Homicide Data"
            )

    print("\nAll plotting tasks complete.")
    print(f"Please check the '{os.getcwd()}/plots' directory for the generated PNG images.")
    print("Ensure you have pandas and matplotlib installed: pip install pandas matplotlib")
