import pandas as pd
import geopandas as gpd
import numpy as np
from shapely.geometry import Point, Polygon
from datetime import date, timedelta
import csv
import os

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

gdf = gpd.read_file(os.path.join("..", "..", "data", "shapefiles", "mwi_adm3_shp"))
years = ['2020', '2021', '2022', '2023', '2024', '2025']

print('getting areas for weighting...')
region_points = {}
gdf_trim = gdf.copy()
for index, row in gdf.iterrows(): # generate a dictionary for adm3 and their relevant points
    lat_range = range(-181, -89)  # divide by ten when actually using these ranges
    lon_range = range(319, 361)
    point_list = []
    for lat_scale in lat_range:
        lat = lat_scale / 10
        for lon_scale in lon_range:
            lon = lon_scale / 10
            # define era5-land square
            square = Polygon([(lon - 0.05, lat - 0.05), (lon - 0.05, lat + 0.05), (lon + 0.05, lat + 0.05), (lon + 0.05, lat - 0.05)])
            intersect = row['geometry'].intersection(square)
            area = intersect.area
            # if there is an intersection, add info to point list
            if area > 0:
                point_info = {'lat': lat, 'lon': lon, 'area': area}
                point_list += [point_info]
    if len(point_list) > 0:
        region_points[row['ADM3_PCODE']] = point_list
    else:
        gdf_trim = gdf_trim.drop(index)
gdf_trim = gdf_trim.reset_index()

# prep output csv
filename = os.path.join('..', '..', 'data', 'adm3_summary', 'adm3_multivariable.csv')
data_output_header = [['adm3 id', 'date', 'high_temperature', 'low_temperature', 'average_temperature',
                       'high_dewpoint_temperature', 'low_dewpoint_temperature', 'average_dewpoint_temperature',
                       'max_windspeed', 'min_windspeed', 'average_windspeed',
                       'max_soil_water', 'min_soil_water', 'average_soil_water',
                       'total_precipitation', 'total_evaporation_transpiration']]
with open(filename, 'w', newline = '') as f:
    writer = csv.writer(f)
    writer.writerows(data_output_header)

# run over each year of data
for year in years:
    print("importing data from " + year + "...")
    year_df = pd.read_csv(os.path.join("..", "..", "data", "era5_export", "multivariable_export_" + year + ".csv"))
    year_df['valid_time'] = pd.to_datetime(year_df['valid_time'])
    dates = date_range(date(int(year), 1, 1), date(int(year), 12, 31))
    for day in dates: # subset over dates
        day_df = year_df[(year_df['valid_time'].dt.date == day)]
        if day.day == 1:
            print("working on " + str(day) + "...")
        for index, row in gdf_trim.iterrows(): # working over each adm region
            area = row['geometry'].area
            n_points = 0
            temp_sum = 0
            temp_max = 0
            temp_min = 1000
            d_temp_sum = 0
            d_temp_max = 0
            d_temp_min = 1000
            wind_sum = 0
            wind_max = 0
            wind_min = 10000
            vsw_sum = 0
            vsw_max = 0
            vsw_min = 1000
            total_precip = 0
            total_evavt = 0
            for point_info in region_points[row['ADM3_PCODE']]:
                # finally, we subset our day table by lat long to get summary values
                table_slice = day_df[(day_df['latitude'] < point_info['lat'] + 0.01) &
                                     (day_df['latitude'] > point_info['lat'] - 0.01) &
                                     (day_df['longitude'] < point_info['lon'] + 0.01) &
                                     (day_df['longitude'] > point_info['lon'] - 0.01)]
                if table_slice.shape[0] > 0:
                    # get maximum & minimum of intersecting grid squares; get weighted average of average temps

                    # temp
                    temp_max = max([temp_max, table_slice['t2m'].max()])
                    temp_min = min([temp_min, table_slice['t2m'].min()])
                    temp_sum += table_slice['t2m'].mean() * point_info['area']/area

                    # dewpoint_temp
                    d_temp_max = max([d_temp_max, table_slice['d2m'].max()])
                    d_temp_min = min([d_temp_min, table_slice['d2m'].min()])
                    d_temp_sum += table_slice['d2m'].mean() * point_info['area']/area

                    # windspeed - take euclidean vector distance
                    windspeeds = np.sqrt(table_slice['u10']**2 + table_slice['v10']**2)
                    wind_max = max([wind_max, max(windspeeds)])
                    wind_min = min([wind_min, min(windspeeds)])
                    wind_sum += windspeeds.mean() * point_info['area']/area

                    # volumetric soil water
                    vsw_max = max([d_temp_max, table_slice['swvl1'].max()])
                    vsw_min = min([d_temp_min, table_slice['swvl1'].min()])
                    vsw_sum += table_slice['swvl1'].mean() * point_info['area'] / area

                    # precipitation - get proportional precipitation of total
                    total_precip += table_slice['tp'].max() * point_info['area'] / area

                    # evaporation transpiration - same as precipitation
                    total_evavt += table_slice['evavt'].max() * point_info['area'] / area
            # having traversed every location, add to csv
            if temp_min < 1000:
                with open(filename, 'a', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerows([[row['ADM3_PCODE'], day, temp_max - 273.15, temp_min - 273.15, temp_sum - 273.15,
                                       d_temp_max - 273.15, d_temp_min - 273.15, d_temp_sum - 273.15,
                                       wind_max, wind_min, wind_sum, vsw_max, vsw_min, vsw_sum, total_precip, total_evavt]])



