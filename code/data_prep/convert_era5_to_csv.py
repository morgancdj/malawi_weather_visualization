import xarray as xr
import pandas as pd
import os
import glob

def file_to_table(path, lat_bounds, lon_bounds):
    """
    Args:
        path: File path for target file
        lat_bounds: latitude slice for bounding box
        lon_bounds: longitude slice for bounding box

    Returns:
        Dataframe with identifying info (lat, long, time) moved from index to regular column
    """

    data = xr.open_dataset(path, engine = "netcdf4")
    df = data.sel(longitude = lon_bounds, latitude = lat_bounds).to_dataframe()
    df = df.reset_index()
    return df

def concatenate_all(lat_bounds, lon_bounds, year):
    """

    Args:
        lat_bounds: latitude slice for bounding box
        lon_bounds: longitude slice for bounding box
        year: Year that we are compressing to a table

    Returns:
        A single dataframe with all the data for that year in a single table

    """
    input_dir = os.path.join("..", "..", "data", "net_cdf", "multivariable", "raw_era5_land_hourly", year)
    nc_files = sorted(glob.glob(os.path.join(input_dir, "*.nc")))
    all_data = []
    for nc_file in nc_files:
        try:
            this_day = file_to_table(nc_file, lat_bounds, lon_bounds)
            all_data += [this_day]
            if str(this_day.at[0, 'valid_time'])[-11:-9] == "01":
                print("Started month beginning at " + str(this_day.at[0, 'valid_time']))
        except:
            print("Failed day " + nc_file[-13:-3])
    full_year = pd.concat(all_data, ignore_index = True)
    full_year.to_csv(os.path.join("..", "..", "data", "era5_export", "multivariable_export_" + year + ".csv"), index = False)
    return full_year

dname = ['t2m', 'd2m', 'vsw', 'evt', '10mu', '10mv', 'tpr']
lat_bounds = slice(-8.9, -18.1)
lon_bounds = slice(31.9, 36.1)

years = ['2020', '2021', '2022', '2023', '2024','2025']
yearly_data = []
for year in years:
    yearly_data += [concatenate_all(lat_bounds, lon_bounds, year)]
