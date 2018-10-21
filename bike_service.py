import osmnx as ox
import networkx as nx

import numpy as np
import pandas as pd

import os.path


def save_graph(osmnx_graph, name):
    ox.save_graphml(osmnx_graph, filename=name + '.graphml', folder='data')
    return None


def load_graph(name):
    return ox.load_graphml(name + '.graphml', folder='data')


class BikeService(object):

    def __init__(self, name, location, network_df, activity_df, load_saved_graph=True):
        """
        Class for a particular bike service
        :param network_df: pandas dataframe
            Contains station's information for a particular bike service. We expect it to have name, lat and lon
            columns, at least, named precisely as 'name','lat' and 'lon'.
        :param location: list
            Locations recognizable by osmnx from which to define a geographical region. We build a graph from names
            using osmnx.
        """

        # Related to the entire geographical space
        self.location = location
        if load_saved_graph and os.path.exists('data/' + name + '.graphml'):
            self.location_graph = ox.load_graphml(filename=name + '.graphml', folder='data')
        else:
            self.location_graph = ox.graph_from_place(location)
            ox.save_graphml(self.location_graph, filename=name + '.graphml', folder='data')
        self.graph_nodes = pd.Series(self.location_graph.nodes)

        # related to the stations
        self.network_df = network_df[['name', 'lat', 'lon']].copy()
        self.network_df['node'] = network_df[['lat', 'lon']].\
            apply(lambda site: ox.get_nearest_node(self.location_graph, tuple(site)), axis=1)
        self.size = len(network_df)

        # related to the activity
        self.activity_df = activity_df

    def map(self, c='r', s=40):
        """
        Map containing the geographic area with the stations' locations
        :param c: color code, optional
            Color for the stations
        :param s: int, optional
            Dot size for the stations
        :return: None
        """

        # selects nodes belonging or not to the stations and colors and scales them differently
        nc = np.where(self.graph_nodes.isin(self.network_df['node']), c, 'g')
        ns = np.where(self.graph_nodes.isin(self.network_df['node']), s, 0)

        ox.plot_graph(self.location_graph, fig_height=30, node_size=ns, node_color=nc, node_zorder=2)

        return None

    def stations_distances(self, distance_type, load_from_saved=True):
        """
        Computes distances between all stations.
        :param load_from_saved: bool, optional
            whether to load a previously saved graph or to produce a graph from data retrieved from OSM
        :param distance_type: string
            street: computes shortest path length
            straight: computes great circle distance
        :return: numpy square array of size given by the number of stations
        """
        network_size = self.size
        # network_size = 100
        distances = np.zeros((network_size, network_size))

        assert distance_type in ['straight', 'street'], 'Only straight or street types possible'

        if distance_type == 'straight':
            if load_from_saved and os.path.exists('data/straight_distances.npy'):
                distances = np.load('data/straight_distances.npy')
            else:
                for origin_id in range(1, network_size + 1):
                    for destination_id in range(origin_id, network_size + 1):
                        distances[origin_id - 1, destination_id - 1] = ox.utils.great_circle_vec(
                            *tuple(self.network_df.loc[origin_id][['lat', 'lon']]),
                            *tuple(self.network_df.loc[destination_id][['lat', 'lon']]))
                        distances[destination_id - 1, origin_id - 1] = distances[origin_id - 1, destination_id - 1]

                np.save('data/straight_distances.npy', distances)

        if distance_type == 'street':
            if load_from_saved and os.path.exists('data/street_distances.npy'):
                distances = np.load('data/street_distances.npy')
            else:
                for origin_id in range(1, network_size + 1):
                    for destination_id in range(1, network_size + 1):
                        origin_node = self.network_df.loc[origin_id]['node']
                        destination_node = self.network_df.loc[destination_id]['node']
                        try:
                            route = nx.shortest_path(self.location_graph, origin_node, destination_node)
                            distances[origin_id - 1, destination_id - 1] = sum([self.location_graph.get_edge_data(u, v)[0]['length']
                                                                                for u,v in zip(route, route[1:])])
                        except:
                            distances[origin_id - 1, destination_id - 1] = np.nan
                np.save('data/street_distances.npy', distances)

        return distances

    def overall_use(self, initial_date, final_date, time_window):
        """

        :param initial_date:
        :param final_date:
        :param time_window:
        :return:
        """
        initial_date = pd.Timestamp(initial_date)
        final_date = pd.Timestamp(final_date)

        take_df = self.activity_df[(self.activity_df['Fecha_Hora_Retiro'] >= initial_date)
                                   & (self.activity_df['Fecha_Hora_Retiro'] <= final_date)]
        lock_df = self.activity_df[(self.activity_df['Fecha_Hora_Arribo'] >= initial_date)
                                   & (self.activity_df['Fecha_Hora_Arribo'] <= final_date)]

        take_df['time_units'] = (take_df['Fecha_Hora_Retiro'] - initial_date).astype('timedelta64[s]') // time_window
        lock_df['time_units'] = (lock_df['Fecha_Hora_Arribo'] - initial_date).astype('timedelta64[s]') // time_window

        take_by_time_units = take_df.groupby('time_units').count()\
            .rename(columns = {'Genero_Usuario': 'viajes cada ' + str(time_window) + ' s'})
        take_by_time_units['datetime'] = pd.to_timedelta(time_window * take_by_time_units.index, unit='s') \
                                         + initial_date

        lock_by_time_units = lock_df.groupby('time_units').count()\
            .rename(columns={'Genero_Usuario': 'devoluciones cada ' + str(time_window) + ' s'})
        lock_by_time_units['datetime'] = pd.to_timedelta(time_window * lock_by_time_units.index, unit='s') \
                                         + initial_date

        return {'take': take_by_time_units[['datetime', 'viajes cada ' + str(time_window) + ' s']],
                'lock': lock_by_time_units[['datetime', 'devoluciones cada ' + str(time_window) + ' s']]}

    def station(self, station_id):
        """
        This allows me to access the outer class from the inner class Station
        :param station_id:
        :return: BikeService.Station class instance
        """
        return BikeService.Station(self, station_id)

    class Station(object):

        def __init__(self, bike_service_instance, station_id):
            """
            Class for a particular bike station
            :param bike_service_instance: the outer class. This allows me access the outer class attributes and methods.
            :param station_id:
            """
            self.bike_service_instance = bike_service_instance
            self.station_id = station_id
            self.station_node = bike_service_instance.network_df.loc[self.station_id]['node']

        def shortest_path(self, destination_id):
            """
            Shortest path FROM our station to another specified station
            :param destination_id: integer id for destination station
            :return: shortest path specified as a list of nodes
            """
            destination_node = self.bike_service_instance.network_df.loc[destination_id]['node']

            return nx.shortest_path(self.bike_service_instance.location_graph, self.station_node, destination_node)

        def plot_shortest_path(self, destination_id, truncate=True):
            """
            Plots shortest path between two stations as determined by osmnx
            :param destination_id: int
                destination id for destination station
            :param truncate: boolean
                whether to truncate the graph to the smallest box enclosing the path or keep the path
                embedded in the entire location_graph
            :return: None
            """
            path = self.shortest_path(destination_id)

            if truncate:
                path_coords_x = [self.bike_service_instance.location_graph.node[node]['x'] for node in path]
                path_coords_y = [self.bike_service_instance.location_graph.node[node]['y'] for node in path]

                north = max(path_coords_y)
                south = min(path_coords_y)
                east = max(path_coords_x)
                west = min(path_coords_x)

                temp_graph = ox.truncate_graph_bbox(self.bike_service_instance.location_graph,
                                                    north=north, south=south, east=east, west=west)

            else:
                temp_graph = self.bike_service_instance.location_graph

            ox.plot_graph_route(temp_graph, path, fig_height=30, node_size=0)

            return None

        def connections(self):
            """
            Computes a pair of pandas dataframes, one containing information of travels FROM OUR station TO OTHER
            stations and another containing information of travels FROM OTHER stations TO OUR station. The information
            contained in each pandas dataframe is:
                - id (related either to destinations or origins, respectively),
                - node (either destination or origin),
                - number of travels,
                - mean travel time,
                - distance (measured as a segment of a great circle).
            :return: a dictionary of pandas dataframes:
                1. to : travels FROM OUR station TO OTHER stations
                2. from: travels FROM OTHER stations TO OUR station
            """

            from_station = self.bike_service_instance.activity_df[
                self.bike_service_instance.activity_df['Ciclo_Estacion_Retiro'] == self.station_id].\
                groupby('Ciclo_Estacion_Arribo')
            to_station = self.bike_service_instance.activity_df[
                self.bike_service_instance.activity_df['Ciclo_Estacion_Arribo'] == self.station_id].\
                groupby('Ciclo_Estacion_Retiro')

            des_list = []
            ori_list = []

            for destination_id in range(1, self.bike_service_instance.size + 1):
                if destination_id in from_station.groups:
                    current_group = from_station.get_group(destination_id)
                    des_list.append([destination_id,
                                     self.bike_service_instance.network_df['node'].loc[destination_id],
                                     current_group['Bici'].count(),
                                     current_group['Tiempo_Transcurrido'].mean(),
                                     ox.utils.great_circle_vec(
                                         *tuple(self.bike_service_instance.network_df.loc[self.station_id][['lat', 'lon']]),
                                         *tuple(self.bike_service_instance.network_df.loc[destination_id][['lat', 'lon']]))])

            for origin_id in range(1, self.bike_service_instance.size + 1):
                if origin_id in to_station.groups:
                    current_group = to_station.get_group(origin_id)
                    ori_list.append([origin_id,
                                     self.bike_service_instance.network_df['node'].loc[origin_id],
                                     current_group['Bici'].count(),
                                     current_group['Tiempo_Transcurrido'].mean(),
                                     ox.utils.great_circle_vec(
                                         *tuple(self.bike_service_instance.network_df.loc[self.station_id][['lat', 'lon']]),
                                         *tuple(self.bike_service_instance.network_df.loc[origin_id][['lat', 'lon']]))])

            return {'to': pd.DataFrame(des_list, columns=['Destino', 'node', 'Numero de Viajes', 'Tiempo medio', 'Distancia']),
                    'from': pd.DataFrame(ori_list, columns=['Origen', 'node', 'Numero de Viajes', 'Tiempo medio', 'Distancia'])}

        def connections_subgraph(self, destination=True, origin=True):
            """
            Computes a subgraph of the entire geographical graph containing all the nodes connected to our station
            through existing travels.
            :param destination: whether to include nodes TO which a travel was made, default True
            :param origin: whether to include nodes FROM which a travel was made, default True
            :return: a osmnx graph
            """

            assert destination or origin, 'At least destination or origin connections must be chosen'

            connection_des, connection_ori = self.connections()
            if destination and origin:
                connections_nodes = pd.concat([connection_des['node'], connection_ori['node']])
            elif destination:
                connections_nodes = connection_des['node']
            elif origin:
                connections_nodes = connection_ori['node']

            if connections_nodes.shape[0] == 0:
                sub_graph = ox.truncate_graph_dist(self.bike_service_instance.location_graph, self.station_node, 1000)

            else:
                connections_data_x_coords = [self.bike_service_instance.location_graph.node[node]['x']
                                             for node in connections_nodes]
                connections_data_x_coords.append(self.bike_service_instance.location_graph.node[self.station_node]['x'])
                connections_data_y_coords = [self.bike_service_instance.location_graph.node[node]['y']
                                             for node in connections_nodes]
                connections_data_y_coords.append(self.bike_service_instance.location_graph.node[self.station_node]['y'])

                north = max(connections_data_y_coords)
                south = min(connections_data_y_coords)
                east = max(connections_data_x_coords)
                west = min(connections_data_x_coords)

                sub_graph = ox.truncate_graph_bbox(self.bike_service_instance.location_graph, north=north,
                                                   south=south, east=east, west=west, truncate_by_edge=True)

            return sub_graph

        def plot_connections(self, truncate=True, destination=True, origin=True):
            """
            Plot the nodes to which our station is connected, either as the origin or the destination of some travel.
            :param truncate: either to plot only the region containing all the connected nodes or to keep the embedding
            in the entire geographical region
            :param destination: either to show the nodes TO which a travel was made, True by default
            :param origin: either to show the nodes FROM which a travel was made, True by default
            :return: None
            """

            assert destination or origin, 'At least destination or origin connections must be chosen'

            connection_des, connection_ori = self.connections()
            if truncate:
                current_graph = self.connections_subgraph(destination, origin)
            else:
                current_graph = self.bike_service_instance.location_graph

            graph_nodes = pd.Series(current_graph.nodes)

            nc = ['gray'] * len(graph_nodes)
            ns = [0] * len(graph_nodes)

            for index, node in connection_des.iterrows():
                node_index = graph_nodes[graph_nodes == node['node']].index[0]
                nc[node_index] = 'blue'
                ns[node_index] = node['Numero de Viajes']

            for index, node in connection_ori.iterrows():
                node_index = graph_nodes[graph_nodes == node['node']].index[0]
                if nc[node_index] == 'blue':
                    nc[node_index] = 'brown'
                else:
                    nc[node_index] = 'green'
                ns[node_index] = ns[node_index] + node['Numero de Viajes']

            node_center = self.bike_service_instance.network_df['node'].loc[self.station_id]
            nc[graph_nodes[graph_nodes == node_center].index[0]] = 'orange'
            ns[graph_nodes[graph_nodes == node_center].index[0]] = 100

            ox.plot_graph(current_graph, fig_height=30, node_size=ns, node_color=nc, node_zorder=2)

            return None
