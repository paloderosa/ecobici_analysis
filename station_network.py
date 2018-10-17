import osmnx as ox


class Station(object):
    """
    Custom network class around each bike station
    """

    def __init__(self, station_id, network_dataframe):
        """
        Initialize
        :param network_dataframe: bike network dataframe
        :param station_id: integer id number for each station
        """
        dataframe = network_dataframe
        self.station_id = station_id
        self.station_node = dataframe.loc[self.station_id]['node']


    def shortest_path(self, destination_id):
        """
        Shortest path FROM our station to another specified station
        :param destination_id: integer id for destination station
        :return: shortest path specified as a list of nodes
        """
        destination_node = dataframe.loc[destination_id]['node']
        return nx.shortest_path(ecobici_zone, self.station_node, destination_node)


    def plot_shortest_path(self, destination_id, truncate=True):
        destination_node = ecobici_stations.loc[destination_id]['node']
        path = self.shortest_path(destination_id)

        if truncate:
            path_coords_x = [ecobici_zone.node[node]['x'] for node in some_station.shortest_path(destination_id)]
            path_coords_y = [ecobici_zone.node[node]['y'] for node in some_station.shortest_path(destination_id)]

            north = max(path_coords_y)
            south = min(path_coords_y)
            east = max(path_coords_x)
            west = min(path_coords_x)

            temp_graph = ox.truncate_graph_bbox(ecobici_zone, north=north, south=south, east=east, west=west)

        else:
            temp_graph = ecobici_zone

        ox.plot_graph_route(temp_graph, path, fig_height=30, node_size=0)

        return None

    def connections(self):
        """
        DataFrame containing data of all stations to which a travel has been made
        """
        des_list = []
        ori_list = []

        for destination_id in range(1, no_stations + 1):
            if (self.station_id, destination_id) in travels_by_origin_destination.groups:
                current_group = travels_by_origin_destination.get_group((self.station_id, destination_id))
                des_list.append([destination_id,
                                 ecobici_stations['node'].loc[destination_id],
                                 current_group['Bici'].count(),
                                 current_group['Tiempo_Transcurrido'].mean(),
                                 ox.utils.great_circle_vec(
                                     *tuple(ecobici_stations.loc[self.station_id][['lat', 'lon']]),
                                     *tuple(ecobici_stations.loc[destination_id][['lat', 'lon']]))])

        for origin_id in range(1, no_stations + 1):
            if (self.station_id, origin_id) in travels_by_destination_origin.groups:
                current_group = travels_by_destination_origin.get_group((self.station_id, origin_id))
                ori_list.append([origin_id,
                                 ecobici_stations['node'].loc[origin_id],
                                 current_group['Bici'].count(),
                                 current_group['Tiempo_Transcurrido'].mean(),
                                 ox.utils.great_circle_vec(
                                     *tuple(ecobici_stations.loc[self.station_id][['lat', 'lon']]),
                                     *tuple(ecobici_stations.loc[origin_id][['lat', 'lon']]))])

        return (pd.DataFrame(des_list, columns=['Destino', 'node', 'Numero de Viajes', 'Tiempo medio', 'Distancia']),
                pd.DataFrame(ori_list, columns=['Origen', 'node', 'Numero de Viajes', 'Tiempo medio', 'Distancia']))

    def connections_subgraph(self, destination=True, origin=True):
        connection_des, connection_ori = self.connections()
        if destination and origin:
            connections_nodes = pd.concat([connection_des['node'], connection_ori['node']])
        elif destination:
            connections_nodes = connection_des['node']
        elif origin:
            connections_nodes = connection_ori['node']

        if connections_nodes.shape[0] == 0:
            temp_graph = ox.truncate_graph_dist(ecobici_zone, self.station_node, 1000)

        else:
            connections_data_x_coords = [ecobici_zone.node[node]['x'] for node in connections_nodes]
            connections_data_x_coords.append(ecobici_zone.node[self.station_node]['x'])
            connections_data_y_coords = [ecobici_zone.node[node]['y'] for node in connections_nodes]
            connections_data_y_coords.append(ecobici_zone.node[self.station_node]['y'])

            north = max(connections_data_y_coords)
            south = min(connections_data_y_coords)
            east = max(connections_data_x_coords)
            west = min(connections_data_x_coords)

            temp_graph = ox.truncate_graph_bbox(ecobici_zone, north=north, south=south, east=east, west=west,
                                                truncate_by_edge=True)

        return temp_graph

    def plot_connections(self, truncate=True, destination=True, origin=True):
        connection_des, connection_ori = self.connections()
        if truncate:
            current_graph = self.connections_subgraph(destination, origin)
        else:
            current_graph = ecobici_zone

        graph_nodes = pd.Series(current_graph.nodes)
        # print(graph_nodes)

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

        node_center = ecobici_stations['node'].loc[self.station_id]
        nc[graph_nodes[graph_nodes == node_center].index[0]] = 'orange'
        ns[graph_nodes[graph_nodes == node_center].index[0]] = 100

        ox.plot_graph(current_graph, fig_height=30, node_size=ns, node_color=nc, node_zorder=2)
        return None

   # def activity(interval='day')