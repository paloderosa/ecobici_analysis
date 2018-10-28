# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go

from bike_service import *


# TODo: first row: heatmap with particular routes. on hover in the heatmap, show the particular route
# TODO: clarify the FROM - TO problem

# TODO: show overall statistics: by sex, by weekday, by day, by month, by time. this on the left. on the right, a map with the dots


mapbox_access_token = 'pk.eyJ1IjoicGFsb2Rlcm9zYSIsImEiOiJjam5wajQzZXIydDBvM3Bvanh3NDR2bWR3In0.T9up8wLMrjeV4Gp0YfCSgA'

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css',
                        #'https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap.min.css',
                        #'/static/reset.css'
                        ]


# we load the ecobici network data
network_df = pd.read_csv('data/ecobici_stations.csv', index_col=0)
station_names = network_df['name']
station_names = station_names.apply(lambda name: ' '.join(name.split()[1:]))
heatmap_text = [['de ' + station_names.loc[j] + ' a ' + station_names.loc[i] for j in range(1,481)] for i in range(1,481)]


# we load the ecobici activity data
activity_df = pd.read_csv('data/2018-08.csv', index_col=0)


"""
In bike_service.py we define the appropiate machinery with which we produce the data that we are going to visualize. 
Also, we produce this data and save it to disk. We prefer to produce the data offline in order to make the interactivity
 as efficient and real as possible.
"""

street_distances = np.load('data/street_distances.npy')


app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

"""
We will arrange the data in several rows. The interactivity is supposed to exist over a single row.
"""
app.layout = html.Div(children=[

    html.Nav(className = "nav nav-pills",
             children=[html.Span('ecobicidata',
                                 style = {'width': '300px', 'display': 'inline-block', 'font-size': 'xx-large'}),
                       html.A('global', className="nav-item nav-link", href='/apps/App1',
                              style={'width': '200px', 'display': 'inline-block'}),
                       html.A('estaciones', className="nav-item nav-link", href='/apps/App1',
                              style={'width': '200px', 'display': 'inline-block'}),
                       html.A('actividad', className="nav-item nav-link active", href='/apps/App2',
                              style={'width': '200px', 'display': 'inline-block'}),
                       html.A('predicción', className="nav-item nav-link active", href='/apps/App3',
                              style={'width': '200px', 'display': 'inline-block'})
                       ]
             ),


    # Here start the visualizations in the first row.


    html.Div([
        html.Div(
            dcc.Graph(id = "heatmap",
                      figure = go.Figure(
                          data = [go.Heatmap(z=street_distances,
                                             colorscale='Reds',
                                             reversescale=True,
                                             showlegend=False,
                                             showscale=False,
                                             text = heatmap_text
                                             )
                                  ],
                          layout=go.Layout(margin=dict(t=60,l = 60, r=60, b=60),
                                           autosize=False,
                                           width = 800,
                                           height = 800,
                                           xaxis=dict(ticks = '',
                                                      showticklabels = False),
                                           yaxis=dict(ticks = '',
                                                      showticklabels = False)
                                           )
                      )
                      ),
            style={'width': '42%', 'padding': '0 20', 'display': 'inline-block'}
        ),

    #html.Div(id = 'test',
    #         style={'width': '52%', 'padding': '0 20', 'display': 'inline-block'},
    #         ),

        html.Div([
            dcc.Graph(id = 'shortest_routes',
                      )
        ], style={'width': '57%', 'padding': '0 20', 'display': 'inline-block'},
        ),

    ], style = {'height': '800px', 'width': '100%'}
    ),


    # Here start the visualizations in the second row.

    html.Div([

        html.Div(
            style={'width': '38%', 'padding': '0 20', 'display': 'inline-block'}
        ),

        html.Div(
            dcc.Slider(id='crossfilter-year--slider',
                       min=1,
                       max=31,
                       value=31,
                       marks={str(day): str(day) for day in range(1, 32)},
                       vertical=True
                       ),
            style={'width': '3%', 'height': '680px', 'padding': '0 20', 'display': 'inline-block', 'z-index': '100', 'padding-bottom': '80px'}
        ),

        html.Div(
            dcc.Graph(id = 'overall_activity'
            ),
            style={'width': '57%', 'padding': '0 20', 'display': 'inline-block'}
        )
    ], style = {'height': '800px', 'width': '100%'}
    )
], style = {'width': '100%', 'margin': 'auto', 'position': 'relative'}
)


@app.callback(
    dash.dependencies.Output('overall_activity', 'figure'),
    [dash.dependencies.Input('crossfilter-year--slider', 'value')])
def show_activity(day_value):
    activity_df_take = activity_df[activity_df['Fecha_Retiro'] == '{:02d}'.format(day_value) + '/08/2018'].groupby('Ciclo_Estacion_Retiro').count()
    activity_df_lock = activity_df[activity_df['Fecha_Arribo'] == '{:02d}'.format(day_value) + '/08/2018'].groupby('Ciclo_Estacion_Arribo').count()

    sizes_take = np.zeros(480)
    sizes_lock = np.zeros(480)

    for i in range(1, 481):
        if i in activity_df_take.index:
            sizes_take[i - 1] = activity_df_take.at[i, 'Genero_Usuario']

        if i in activity_df_lock.index:
            sizes_lock[i - 1] = activity_df_lock.at[i, 'Genero_Usuario']

    return go.Figure(
        data = [go.Scattermapbox(lat=network_df['lat'],
                                 lon=network_df['lon'],
                                 mode='markers',
                                 marker=dict(size=np.ceil(sizes_take / 10.),
                                             color= '#FF1A1A',
                                             opacity = 0.4),
                                 text=network_df['name'],
                                 name='Préstamos'
                                 ),
                go.Scattermapbox(lat=network_df['lat'],
                                 lon=network_df['lon'],
                                 mode='markers',
                                 marker=dict(size=np.ceil(sizes_lock / 10.),
                                             color= '#FF9D1A',
                                             opacity = 0.4),
                                 text=network_df['name'],
                                 name='Devoluciones'
                                 )
                ],
        layout = go.Layout(margin=dict(t=60,l = 60, r=60, b=60),
                           autosize=False,
                           width=1000,
                           height=800,
                           hovermode='closest',
                           mapbox=dict(accesstoken=mapbox_access_token,
                                       bearing=0,
                                       center=dict(
                                           lat=19.404,
                                           lon=-99.17
                                       ),
                                       pitch=0,
                                       zoom=12.2,
                                       style='light'
                                       ),
                           )
    )

@app.callback(
    dash.dependencies.Output('shortest_routes', 'figure'),
    #dash.dependencies.Output('test', 'children'),
    [dash.dependencies.Input('heatmap', 'clickData')])
def show_shortest_path(path_info):
    if path_info is not None:
        origin_id = path_info['points'][0]['x']+1
        destination_id = path_info['points'][0]['y']+1

        opacitys = 0.5

        sizes = 10

        lats = network_df.loc[[origin_id,destination_id], 'lat']
        lons = network_df.loc[[origin_id,destination_id], 'lon']

    else:
        origin_id, destination_id = tuple(np.random.randint(1,480,2))

        opacitys = 0.5

        sizes = 10

        lats = network_df.loc[[origin_id, destination_id], 'lat']
        lons = network_df.loc[[origin_id, destination_id], 'lon']

    return go.Figure(
        data = [go.Scattermapbox(lat = lats,
                                 #lat=network_df['lat'],
                                 lon = lons,
                                 #lon=network_df['lon'],
                                 mode='markers',
                                 marker=dict(size=sizes,
                                             color= '#FF9D1A',
                                             opacity = opacitys),
                                 text=network_df['name'],
                                 name='Préstamos'
                                 )
                ],
        layout = go.Layout(margin=dict(t=60,l = 60, r=60, b=60),
                           autosize=False,
                           width=1000,
                           height=800,
                           hovermode='closest',
                           mapbox=dict(accesstoken=mapbox_access_token,
                                       #layers =[dict(sourcetype = 'geojson',
                                       #              source = route_dict,
                                       #              color='rgb(0,0,230)',
                                       #              type = 'line',
                                       #              line=dict(width=1.5),
                                       #              )
                                       #         ],
                                       bearing=0,
                                       center=dict(
                                           lat=19.404,
                                           lon=-99.17
                                       ),
                                       pitch=0,
                                       zoom=12.2,
                                       style='light'
                                       ),
                           )
    )


if __name__ == '__main__':
    app.run_server(debug=True)