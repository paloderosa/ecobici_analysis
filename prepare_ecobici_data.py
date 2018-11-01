import pandas as pd
import seaborn as sns

import glob
import os.path

"""
We preprocess the Ecobici data in a way totally specific to it. We preprocess two types of raw files:
    1. the data in 'ecobici_stations.json', which contains information about the Ecobici stations;
    2. the data in the several 'yyyy-mm.csv' files containing the activity during the month mm in the year yyyy.
"""


def preprocess_station_data():
    """
    We retrieved this file from https://www.ecobici.cdmx.gob.mx/es/mapa-de-cicloestaciones under the name
    getJsonObject.json. It contains the information about each Ecobici stattion displayed in that website. We renamed it
    ecobici_stations.json
    :return: None
    """
    ecobici_stations = pd.read_json('raw_data/ecobici_stations.json')
    # We set the station id as the index for the dataframe
    ecobici_stations.set_index('id', inplace=True)
    # We save the dataframe to as csv file.
    ecobici_stations.to_csv('data/ecobici_stations.csv')
    # Next time we load this data, we should load ot with
    # pd.read_csv('data/ecobici_stations.csv', index_col=0)
    return None


def station_data_completeness():
    """
    Plot missing data
    :return: None
    """
    assert os.path.exists('data/ecobici_stations.csv'), 'You need to run preprocess_station_data() first'

    ecobici_stations = pd.read_csv('data/ecobici_stations.csv', index_col=0)

    sns.heatmap(ecobici_stations.isnull(), yticklabels=False, cbar=False, cmap='viridis')
    return None


def preprocess_travel_data():
    """

    :return:
    """
    assert os.path.exists('data/ecobici_stations.csv'), 'You need to run preprocess() first'

    ecobici_stations = pd.read_csv('data/ecobici_stations.csv', index_col=0)
    for name in sorted(glob.glob('raw_data/????-??.csv')):
        print('Processing ' + name)
        if not os.path.exists('data/' + name.split('/')[1]):
            travel_data = pd.read_csv(name)
            travel_data['Genero_Usuario'] = travel_data.Genero_Usuario.astype('category')
            number_stations = len(ecobici_stations)
            # We have found trips from or to stations beyond the scope of the stations' id
            travel_data.drop(travel_data[travel_data['Ciclo_Estacion_Arribo'] > number_stations].index, inplace=True)
            travel_data.drop(travel_data[travel_data['Ciclo_Estacion_Retiro'] > number_stations].index, inplace=True)
            # Set the time data in the correct format and as datetime data. Dates from the 2018 databases have the day
            # as the first element, unlike the 2010 data.
            # TODO: modify this method so that it automatically detects the datetime format from the raw databases
            travel_data['Fecha_Hora_Arribo'] = pd.to_datetime(travel_data['Fecha_Arribo'] + ' ' +
                                                              travel_data['Hora_Arribo'], dayfirst=True)
            travel_data['Fecha_Hora_Retiro'] = pd.to_datetime(travel_data['Fecha_Retiro'] + ' ' +
                                                              travel_data['Hora_Retiro'], dayfirst=True)
            travel_data['Tiempo_Transcurrido'] = (travel_data['Fecha_Hora_Arribo'] - travel_data['Fecha_Hora_Retiro'])\
                .astype('timedelta64[s]')

            # We no longer need separate date AND time columns
            #travel_data.drop(['Fecha_Retiro','Hora_Retiro','Fecha_Arribo','Hora_Arribo'], axis=1, inplace=True)
            travel_data.to_csv('data/' + name.split('/')[1])

    return None
