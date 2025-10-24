import cdsapi
import os
from datetime import date, timedelta

# Parameter Mapping: Short variable names mapped to full ERA5 variable names
# Example: 't2m' (short name) corresponds to '2m_temperature' (full name)
param_dic = {'t2m': '2m_temperature',
             'd2m': '2m_dewpoint_temperature',
             'vsw': 'volumetric_soil_water_layer_1',
             'evt': 'evaporation_from_vegetation_transpiration',
             '10mu' : '10m_u_component_of_wind',
             '10mv' : '10m_v_component_of_wind',
             'tpr' : 'total_precipitation'}

# --------------------------- CONFIGURATION SECTION ---------------------------
# Define the date range for which data will be retrieved
start_date = date(2025, 8, 1)  # Starting date (YYYY-MM-DD)
end_date = date(2025, 8, 2)  # Ending date (YYYY-MM-DD)

# Specify the variables of interest as list (e.g., 't2m' for temperature) - keys in paramdict
dname_list = ['t2m', 'd2m', 'vsw', 'evt', '10mu', '10mv', 'tpr']

# ERA5 data retrieval times: Specify the hours of the day to fetch data for
time_slots = ['00:00', '03:00', '06:00', '09:00', '12:00', '15:00', '18:00', '21:00']

# ERA5 bounding box definition: Order is northern bound on latitude, western bound on longitude,
# southern bound on latitude, eastern bound on longitude. Include extra 0.1 to account for cutoffs
area = [-8.9, 31.9, -18.1, 36.1]

# Validate that all the chosen variables exists in the parameter dictionary
param_list = []
for dname in dname_list:
    if dname not in param_dic:
        raise ValueError(f"Invalid variable name: {dname}. Choose from {list(param_dic.keys())}")
    param_list += [param_dic[dname]]  # Full name of the variable based on the short name

# Define the output directory (generalized path without hardcoding)
output_dir = os.path.join("..", "..", "data", "net_cdf", "multivariable", "raw_era5_land_hourly")
os.makedirs(output_dir, exist_ok=True)  # Create the directory if it doesn't exist

# --------------------------- UTILITY FUNCTIONS ---------------------------

def date_range(start: date, end: date) -> list:
    """
    Generate a list of dates between the start and end dates (inclusive).

    Parameters:
    - start (date): The start date.
    - end (date): The end date.

    Returns:
    - list: List of date objects from start to end.
    """
    delta = (end - start).days + 1  # Include the end date
    return [start + timedelta(days=i) for i in range(delta)]


def era5_request_land_bounded(date_str: str, target: str, time_slots: list, area: list):
    """
    Request ERA5 land climate data for a specific date and save it to the target file.

    Parameters:
    - date_str (str): The date in 'YYYY-MM-DD' format.
    - target (str): Path to save the downloaded NetCDF file.
    - time_slots (list): List of hourly time slots for data retrieval.
    """
    try:
        client = cdsapi.Client()  # Initialize the CDS API client

        # Split date string into year, month, and day
        year, month, day = date_str.split('-')

        # Construct the data request payload
        request = {
            'variable': param_list,  # Climate variables (e.g., '2m_temperature')
            'year': year,  # Year
            'month': month,  # Month
            'day': day,  # Day
            'time': time_slots,  # List of specific hours for data retrieval
            'data_format': 'netcdf',  # File format: NetCDF
            'download_format': 'unarchived', # Specify unarchived download
            'area': area # Restrict to requested area
        }

        # Check if the file already exists to avoid redundant downloads
        if os.path.exists(target):
            print(f"File already exists: {target}")
            return

        # Submit the request and download the data
        client.retrieve('reanalysis-era5-land', request, target)
        print(f"Successfully retrieved data for {date_str}")

    except Exception as e:
        # Handle errors and log the failed downloads for later retry
        print(f"Failed to retrieve data for {date_str}: {e}")
        with open("failed_downloads.log", "a") as log_file:
            log_file.write(f"{date_str}\n")

def retrieve_era5_land_bounded(start: date, end: date, time_slots: list, area: area):
    """
    Retrieve ERA5 land climate data for all dates within the specified range.

    Parameters:
    - start (date): Start date for the retrieval process.
    - end (date): End date for the retrieval process.
    - time_slots (list): List of hours to include in each request.
    """
    for current_date in date_range(start, end):  # Loop through each date in the range
        # Create a year-specific directory to organize the downloaded files
        year_dir = os.path.join(output_dir, str(current_date.year))
        os.makedirs(year_dir, exist_ok=True)  # Ensure the directory exists

        # Format the date as a string for file naming
        date_str = current_date.strftime("%Y-%m-%d")

        # Define the target file name (generalized naming convention)
        # Currently uses final variable
        target_file = os.path.join(year_dir, f"era5_{dname}_daily_{date_str}.nc")

        # Request data for the current date
        era5_request_land_bounded(date_str, target_file, time_slots, area)

# --------------------------- MAIN EXECUTION ---------------------------
if __name__ == "__main__":
    print("Starting ERA5 land data retrieval...")
    retrieve_era5_land_bounded(start_date, end_date, time_slots, area)
    print("Data retrieval process completed.")
