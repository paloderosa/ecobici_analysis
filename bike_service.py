import osmnx as ox
import numpy as np
import pandas as pd
#from station_network import *


class BikeService(object):

    def __init__(self, location, df):
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
        self.dataframe = df[['name', 'lat', 'lon']].copy()
        self.dataframe['node'] = df[['lat', 'lon']].\
            apply(lambda site: ox.get_nearest_node(self.location_graph, tuple(site)), axis=1)
        self.size = len(df)

    def map(self, c='r', s=40):
        """
        Map containing the geographic area with the stations' locations
        :param c: color for the stations, default red
        :param s: size for the stations, default 40
        :return: None
        """

        nc = np.where(self.graph_nodes.isin(self.dataframe['node']), c, 'g')
        ns = np.where(self.graph_nodes.isin(self.dataframe['node']), s, 0)

        ox.plot_graph(self.location_graph, fig_height=30, node_size=ns, node_color=nc, node_zorder=2)

        return None
