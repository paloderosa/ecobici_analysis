import osmnx as ox
import networkx as nx

import numpy as np
import pandas as pd


class BikeService(object):

    def __init__(self, location, network_df, activity_df):
        """
        Class for a particular bike service
        :param df: pandas dataframe containing station's information for a particular bike service. We
        expect it to have name, lat and lon columns, at least.
        :param location: list of locations recognizable by osmnx from which to define a geographical region
        """

        # related to the entire geographical space
        self.location = location
        self.location_graph = ox.graph_from_place(location)
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
        :param c: color for the stations, default red
        :param s: size for the stations, default 40
        :return: None
        """

        nc = np.where(self.graph_nodes.isin(self.network_df['node']), c, 'g')
        ns = np.where(self.graph_nodes.isin(self.network_df['node']), s, 0)

        ox.plot_graph(self.location_graph, fig_height=30, node_size=ns, node_color=nc, node_zorder=2)

        return None

    def station(self, station_id):
        return BikeService.Station(self, station_id)

    class Station(object):

        def __init__(self, bike_service_instance, station_id):
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
            :param destination_id: destination id for destination station
            :param truncate: whether to truncate the graph to the smallest box enclosing the path or keep the path
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