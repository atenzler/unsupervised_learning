import argparse
from datetime import datetime
import pandas as pd

import paint.util.paint_mappings as mappings
from paint import PAINT_ROOT
from paint.data.stac_client import StacClient




file_path = r"C:\Users\anton\Old_Desktop\Masterthesis\Unsupervised_learning\Data\240801_Heliostate_Fokallängen_Umrüstphasen.xlsx"  # Replace with your file path
df = pd.read_excel(file_path, sheet_name="Heliostats.xml")


# Extract a specific column into a list and convert to string
all_helios = df.iloc[:, 3]
string_all_helios = [str(element) for element in all_helios]
#print(string_all_helios)

#Because script was stopped in the middle
string_all_helios = string_all_helios[1:]
print(string_all_helios)


skipped_helios = []

if __name__ == "__main__":
    # Read in arguments.
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output_dir",
        type=str,
        help="Path to save the downloaded data.",
        default=r"C:\Users\anton\Old_Desktop\Masterthesis\Unsupervised_learning\Data\Heliostats_all",
    )
    parser.add_argument(
        "--weather_data_sources",
        type=str,
        help="List of data sources to use for weather data.",
        nargs="+",
        default=["Jülich", "DWD"],
    )
    parser.add_argument(
        "--start_date",
        type=str,
        help="Start date for filtering the data.",
        default="2023-01-01Z00:00:00Z",
    )
    parser.add_argument(
        "--end_date",
        type=str,
        help="End date for filtering the data.",
        default="2023-03-01Z00:00:00Z",
    )
    parser.add_argument(
        "--collections",
        type=str,
        help="List of collections to be downloaded.",
        nargs="+",
        default=["properties", "deflectometry"],
    )
    parser.add_argument(
        "--filtered_calibration",
        type=str,
        help="List of calibration items to download.",
        nargs="+",
        default=["cropped_image", "calibration_properties"],
    )
    args = parser.parse_args()

    # Create STAC client.
    client = StacClient(output_dir=args.output_dir)

    # Download tower measurements.
    client.get_tower_measurements()

    # Download weather data between a certain time period.
    client.get_weather_data(
        data_sources=args.weather_data_sources,
        start_date=datetime.strptime(args.start_date, mappings.TIME_FORMAT),
        end_date=datetime.strptime(args.end_date, mappings.TIME_FORMAT),
    )

    # Download heliostat data.
    for heliostat in string_all_helios:
        try:
            print(f"Processing heliostat: {heliostat}")
            client.get_heliostat_data(
                heliostats=[heliostat],  # Process one heliostat at a time
                collections=args.collections,
                filtered_calibration_keys=args.filtered_calibration,
            )
        except Exception as e:
            print(f"Error occurred with heliostat {heliostat}: {e}")
            skipped_helios.append(heliostat)
            # Continue to the next heliostat
            continue


    print(f"The following heliostats were not found in the catalogue: {skipped_helios}")
