import numpy as np
import pandas as pd

def extract_trips_from_xlsx(filepath):
    """
    Main function for extracting 'trips' (i.e. direct travel between two sensors)
    from an xlsx file in the trip_chain_reports folder of this repository

    Returns: Pandas.DataFrame object where each record is a single journey
    """

    xls = pd.ExcelFile(filepath)

    # Looping over sheet names, and choosing those whose name is a number 
    # (because this will correspond to a sheet containing trip chain data)
    trips = []
    for sheet_name in xls.sheet_names:
        if not sheet_name.isdigit():
            continue

        print(f'Parsing sheet {sheet_name}')

        #  Dataframe containing data about 'trip chains' 
        # (a collection of trips made by the same vehicle that are considered to be part of the same overall journey)
        trip_chains_df = pd.read_excel(xls, 
                                    sheet_name=sheet_name,
                                    usecols='B:F', #Columns to use, 
                                    skiprows=10, #Skipping first 9 rows, 
                                    header=0, 
                                    names=['start_time', 'vehicle_class', 'trip_time', 'chain_vector', 'chain_vector_with_times'], 
                                    dtype = {'start_time': 'datetime64[ns]','vehicle_class': 'string', 'trip_time': np.float64, 'chain_vector': 'string', 'chain_vector_with_times': 'string'}
                                    )
        
        trips = trips + convert_trip_chains_to_trips(trip_chains_df)
    

    
    trips_df = pd.DataFrame.from_dict(trips)

    return trips_df


def convert_trip_chains_to_trips(trip_chains_df):
    """
    Extracts trip data from a dataframe extracted from a single xlsx sheet in the trip_chain_reports folder of this repository

    Returns:
    A list of trips of the following form:
        {
            'timestamp: '',
            'start_site': 01,
            'start_direction': 'W',
            'end_site': 02, 
            'end_direction': 'N',
            'time':
            'vehicle_type': 
        }
    """

    trip_chains = trip_chains_df.apply(parse_chain_vector, axis='columns').to_numpy()


    trips = []

    for trip_chain in trip_chains:
        trip_chain_start_time =  trip_chain[0]['timestamp']
        trip_start_time = trip_chain_start_time
        for i, trip in enumerate(trip_chain[1:], start=1):
            trips.append({
                'start_time': trip_start_time,
                'start_site': trip_chain[i-1]['site'],
                'start_direction': trip_chain[i-1]['direction'],
                'end_site': trip['site'],
                'end_direction': trip['direction'],
                'time': float(trip['time']),
                'vehicle': trip['vehicle']
            })

            trip_start_time = trip_chain_start_time + pd.DateOffset(minutes=float(trip['time']))

    return trips


    

def parse_chain_vector(row):
    """
    Given a row in the trips_chain_df, returns a list of dicts, 
    each of which represents a single trip that makes up the trip chain
    """
    vehicle = row.vehicle_class
    chain_vector_str = row.chain_vector_with_times
    timestamp = row.start_time

    chain_components = []

    initial_site = row.chain_vector.split('_')[0]
    initial_direction = row.chain_vector.split('_')[1].split('>')[0]
    chain_components.append({ 'timestamp': timestamp, 'site': initial_site, 'direction': initial_direction, 'vehicle': vehicle })
    
    for chain_component_str in chain_vector_str.split('>')[1:]:
        site = chain_component_str.split('>')[0].split('_')[0]
        direction = chain_component_str.split('_')[1].split('(')[0]
        time = chain_component_str.split('(')[1].split(')')[0]
        chain_components.append({
            'site': site,
            'direction': direction,
            'time': time,
            'vehicle': vehicle
        })
    
    return chain_components


