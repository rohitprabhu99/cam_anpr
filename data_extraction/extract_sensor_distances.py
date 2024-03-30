import numpy as np
import pandas as pd
import geopandas as gpd
import fiona


def extract_sensor_data_from_kml():
    """
    Main function for creating a GeoPandas Dataframe from the kml file in 
    the sensor_location_data folder of this repository

    Returns: GeoPandas.GeoDatafeame object where each record corresponds to a particular sensor
    """

    fiona.drvsupport.supported_drivers['KML'] = 'rw'
    sensors_data = gpd.read_file('./sensor_location_data/sensor_map.kml')
    sensors_data = sensors_data.to_crs(epsg=3310)

    return sensors_data


def extract_sensor_distances_from_kml():
    """
    Main function for extracting the distances between all pairs of sensors
    from a kml file in the sensor_location_data folder of this repository

    Returns: Pandas.Dataframe object where each record corresponds to a particular pair of sensors
    """

    sensors_data = extract_sensor_data_from_kml()

    # Getting distance between each pair of sensors
    sensor_distances = []

    for start_sensor,  start_point in sensors_data[['Name', 'geometry']].to_numpy():
        for end_sensor, end_point in sensors_data[['Name', 'geometry']].to_numpy():
            distance = start_point.distance(end_point)
            sensor_distances.append({
                'start': start_sensor,
                'end': end_sensor,
                'distance': distance
            })

    sensor_distances_df = pd.DataFrame.from_records(sensor_distances)

    return sensor_distances_df

    

    