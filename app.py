# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go

import json
import pandas as pd
import numpy as np

import base64




# TODO: show overall statistics: by sex, by weekday, by day, by month, by time.
# this on the left. on the right, a map with the dots


mapbox_access_token = 'pk.eyJ1IjoicGFsb2Rlcm9zYSIsImEiOiJjam5wajQzZXIydDBvM3Bvanh3NDR2bWR3In0.T9up8wLMrjeV4Gp0YfCSgA'

external_stylesheets = [
    'https://codepen.io/chriddyp/pen/bWLwgP.css',
]

external_scripts = [
    'https://npmcdn.com/@turf/turf/turf.min.js'
]


# we load the ecobici network data
network_df = pd.read_csv('data/ecobici_stations.csv', index_col=0)
number_of_stations = len(network_df.index)
station_names = network_df['name']
station_names = station_names.apply(lambda name: ' '.join(name.split()[1:]))
station_lats = network_df['lat']
station_lons = network_df['lon']
heatmap_text = [['de ' + station_names.loc[j] + ' a ' + station_names.loc[i]
                 for j in range(1, 481)]
                for i in range(1, 481)]

# we load the ecobici activity data
activity_df = pd.read_csv('data/2018-01.csv', index_col=0)

activity_df_by_sex = activity_df.groupby('Genero_Usuario').count()

"""
In bike_service.py we define the appropriate machinery with which we produce the data that we are going to visualize. 
Also, we produce this data and save it to disk. We prefer to produce the data offline in order to make the interactivity
 as efficient and real as possible.
"""

# distance between stations by shortest routes
street_distances = np.load('data/street_distances.npy')

# sequences of coordinates of points from one station to another through the shortest route
with open('data/shortest_routes.json') as infile:
    shortest_routes = json.load(infile)


logo_filename = 'images/ecobici_logo.jpg' # replace with your own image
encoded_logo = base64.b64encode(open(logo_filename, 'rb').read())

sex_dict = {
        'F': ['Mujeres', '#DE6D25'],
        'M': ['Hombres', '#A19F9F']
    }

app = dash.Dash(
    __name__,
    external_stylesheets=external_stylesheets,
    external_scripts=external_scripts
)

"""
We will arrange the data in several rows. The interactivity is supposed to exist over a single row.
"""
app.layout = html.Div(children=[

    # div for header
    html.Div([

        html.Span(
            'ecobicidata',
            style = {
                'width': '300px',
                'display': 'inline-block',
                'font-size': 'xx-large',
                'vertical-align': 'middle'
            }
        ),

        html.Nav(
            className = "nav nav-pills",
            children=[
                html.A(
                    'global',
                    className="nav-item nav-link",
                    href='/apps/App1',
                    style={
                        'width': '200px',
                        'display': 'inline-block'
                    }
                ),
                html.A(
                    'estaciones',
                    className="nav-item nav-link",
                    href='/apps/App1',
                    style={
                        'width': '200px',
                        'display': 'inline-block'
                    }
                ),
                html.A(
                    'actividad',
                    className="nav-item nav-link active",
                    href='/apps/App2',
                    style={
                        'width': '200px',
                        'display': 'inline-block'
                    }
                ),
                html.A(
                    'predicción',
                    className="nav-item nav-link active",
                    href='/apps/App3',
                    style={
                        'width': '200px',
                        'display': 'inline-block'
                    }
                )
            ],
            style = {
                'display': 'inline-block',
                'vertical-align': 'middle'
            }
        ),

        html.Img(
            src='data:image/jpg;base64,{}'.format(encoded_logo.decode()),
            style = {
                'display': 'inline-block',
                'height': '100px',
                'vertical-align': 'middle'
            }
        ),
    ],
        style={
            'height': '100px',
            'margin': 'auto',
            'width': '80%'
        }
    ),

    # here start the visualizations in the first row.
    html.Div([
        html.Div(
            dcc.Graph(
                id = "heatmap",
                figure = go.Figure(
                    data = [
                        go.Heatmap(
                            z=street_distances,
                            colorscale='Reds',
                            reversescale=True,
                            showlegend=False,
                            showscale=False,
                            text = heatmap_text
                        )
                    ],
                    layout=go.Layout(
                        margin=dict(t=60,l = 60, r=60, b=60),
                        autosize=False,
                        width = 800,
                        height = 800,
                        xaxis=dict(
                            ticks = '',
                            showticklabels = False
                        ),
                        yaxis=dict(
                            ticks = '',
                            showticklabels = False
                        )
                    )
                )
            ),
            style={
                'width': '42%',
                'padding': '0 20',
                'display': 'inline-block'
            }
        ),


        html.Div(
            dcc.Graph(id = 'shortest_routes'),
            style={
                'width': '57%',
                'padding': '0 20',
                'display': 'inline-block'
            },
        ),
    ],
        style = {
            'height': '800px',
            'width': '100%'
        }
    ),


    # here start the visualizations in the second row.
    html.Div([
        html.Div([
            dcc.Graph(id = 'sex-count-by-day'),

            dcc.Graph(id = 'age-sex-by-day'),
        ],
            style={
                'width': '38%',
                'padding': '0 20',
                'display': 'inline-block'
            }
        ),

        html.Div(
            dcc.Slider(
                id='crossfilter-year--slider',
                min=1,
                max=31,
                value=31,
                marks={str(day): str(day) for day in range(1, 32)},
                vertical=True
            ),
            style={
                'width': '3%',
                'height': '680px',
                'padding': '0 20',
                'display': 'inline-block',
                'z-index': '100',
                'padding-bottom': '80px'
            }
        ),

        html.Div(
            dcc.Graph(id = 'overall_activity'),
            style={
                'width': '57%',
                'padding': '0 20',
                'display': 'inline-block'
            }
        )
    ],
        style = {
            'height': '800px',
            'width': '100%'
        }
    ),


    # here start the visualizations in the third row.
    #html.Div([
        #html.Div(
        #    dcc.Graph(id = 'sex-count-by-day'),
        #),

        #html.Div(

        #),

        #html.Div(

        #)
    #])
],
    style = {
        'width': '100%',
        'margin': 'auto',
        'position': 'relative'
    }
)


# by clicking on a particular point in the heatmap corresponding to the distance from station a to point b, we display
# the corresponding route in the mapbox map.
@app.callback(
    dash.dependencies.Output('shortest_routes', 'figure'),
    [dash.dependencies.Input('heatmap', 'clickData')])
def show_shortest_path(path_info):
    if path_info is not None:
        origin_id = path_info['points'][0]['x']+1
        destination_id = path_info['points'][0]['y']+1

    else:
        origin_id, destination_id = tuple(np.random.randint(1,480,2))

    text = station_names
    lats = station_lats
    lons = station_lons
    size = [4] * number_of_stations
    color = ['#FF9D1A'] * number_of_stations
    color[origin_id-1] = '#FF9D1A'
    color[destination_id-1] = '#FF1A1A'
    size[origin_id-1] = 10
    size[destination_id-1] = 10

    return go.Figure(
        data = [
            go.Scattermapbox(
                lat = lats,
                lon = lons,
                mode='markers',
                marker=dict(
                    size=size,
                    color= color,
                    opacity = 0.9
                ),
                text=text,
                name='Ruta más corta'
            )
        ],
        layout = go.Layout(
            margin=dict(t=60,l = 60, r=60, b=60),
            autosize=False,
            width=1000,
            height=800,
            hovermode='closest',
            mapbox=dict(
                accesstoken=mapbox_access_token,
                layers =[
                    dict(
                        sourcetype = 'geojson',
                        source = shortest_routes[str(origin_id) + ' to ' + str(destination_id)],
                        color='#FF9D1A',
                        opacity = 0.5,
                        type = 'line',
                        line=dict(width=7),
                    ),
                    dict(
                        sourcetype='geojson',
                        source=shortest_routes[str(destination_id) + ' to ' + str(origin_id)],
                        color='#FF9D1A',
                        opacity=0.2,
                        type='line',
                        line=dict(width=7),
                    )
                ],
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

# by clicking on a particular day, we display in the mapbox map two circles around each station with size given the
# number of trips from and to that station for that particular day.
@app.callback(
    dash.dependencies.Output('overall_activity', 'figure'),
    [dash.dependencies.Input('crossfilter-year--slider', 'value')])
def show_activity_by_day(day_value):
    activity_df_take = activity_df[activity_df['Fecha_Retiro'] == '{:02d}'.format(day_value) + '/01/2018']\
        .groupby('Ciclo_Estacion_Retiro').count()
    activity_df_lock = activity_df[activity_df['Fecha_Arribo'] == '{:02d}'.format(day_value) + '/01/2018']\
        .groupby('Ciclo_Estacion_Arribo').count()

    sizes_take = np.zeros(480)
    sizes_lock = np.zeros(480)

    for i in range(1, 481):
        if i in activity_df_take.index:
            sizes_take[i - 1] = activity_df_take.at[i, 'Genero_Usuario']

        if i in activity_df_lock.index:
            sizes_lock[i - 1] = activity_df_lock.at[i, 'Genero_Usuario']

    return go.Figure(
        data = [
            go.Scattermapbox(
                lat=network_df['lat'],
                lon=network_df['lon'],
                mode='markers',
                marker=dict(
                    size=np.ceil(sizes_take / 10.),
                    color= '#FF1A1A',
                    opacity = 0.4
                ),
                text=network_df['name'],
                name='Préstamos'
            ),
            go.Scattermapbox(
                lat=network_df['lat'],
                lon=network_df['lon'],
                mode='markers',
                marker=dict(
                    size=np.ceil(sizes_lock / 10.),
                    color= '#FF9D1A',
                    opacity = 0.4
                ),
                    text=network_df['name'],
                    name='Devoluciones'
            )
        ],
        layout = go.Layout(
            margin=dict(t=60,l = 60, r=60, b=60),
            autosize=False,
            #width=1000,
            height=900,
            hovermode='closest',
            mapbox=dict(
                accesstoken=mapbox_access_token,
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
    dash.dependencies.Output('sex-count-by-day', 'figure'),
    [dash.dependencies.Input('crossfilter-year--slider', 'value')])
def show_sex_by_day(day_value):
    df = activity_df[['Genero_Usuario','Fecha_Retiro']][activity_df['Fecha_Retiro'] == '{:02d}'.format(day_value) + '/01/2018']
    df_by_sex = df.groupby('Genero_Usuario').count().reset_index()

    return go.Figure(
        data=[
            go.Pie(
                values = df_by_sex['Fecha_Retiro'],
                labels = [sex_dict[sex][0] for sex in df_by_sex['Genero_Usuario']],
                #name = 'Usuarios por sexo',
                hoverinfo = 'label+percent',
                hole = 0.4,
                marker=dict(
                    colors = [sex_dict[sex][1] for sex in df_by_sex['Genero_Usuario']],
                    line=dict(color='white', width=1)
                ),
            )
        ],
        layout=go.Layout(
            margin=dict(t=20, r=0, b=40),
            # title='Usuarios por sexo ' + '{:02d}'.format(day_value) + '/01/2018',
            annotations=[dict(
                font = dict(
                    size = 13,
                ),
                showarrow = False,
                text = str(df_by_sex['Fecha_Retiro'].sum()),
            )],
            #width = 500,
            #height = 300,
        )
    )

@app.callback(
    dash.dependencies.Output('age-sex-by-day', 'figure'),
    [dash.dependencies.Input('crossfilter-year--slider', 'value')])
def show_age_sex_by_day(day_value):
    df = activity_df[['Genero_Usuario','Edad_Usuario','Fecha_Retiro']][activity_df['Fecha_Retiro'] == '{:02d}'.format(day_value) + '/01/2018']
    df_f = df[df['Genero_Usuario'] == 'F']
    df_m = df[df['Genero_Usuario'] == 'M']

    tickvals = [-2000, -1750, -1500, -1250, -1000, -750, -500, -250,
                0, 250, 500, 750, 1000, 1250, 1500, 1750, 2000, 2250, 2500, 2750, 3000]
    ticktext = [np.abs(x) for x in tickvals]

    return go.Figure(
        data=[
            go.Histogram(
                y=df_m['Edad_Usuario'],
                orientation='h',
                name='Hombres',
                marker=dict(color=sex_dict['M'][1]),
                hoverinfo='skip',
                ybins=dict(
                    start=df_m['Edad_Usuario'].min(),
                    end=df_m['Edad_Usuario'].max(),
                    size=1
                ),
            ),
            go.Histogram(
                y=df_f['Edad_Usuario'],
                x=-1*np.ones(len(df_m)),
                orientation='h',
                name='Mujeres',
                marker=dict(color=sex_dict['F'][1]),
                hoverinfo='skip',
                histfunc = 'sum',
                ybins=dict(
                    start=df_f['Edad_Usuario'].min(),
                    end=df_f['Edad_Usuario'].max(),
                    size=1
                ),
            )
        ],
        layout=go.Layout(
            margin=dict(t=20, r=0, b=40),
            barmode='overlay',
            yaxis=go.layout.YAxis(
                range=[16, 80],
                #range=[df['Edad_Usuario'].min(), df['Edad_Usuario'].max()],
                title='Edad'),
            xaxis=go.layout.XAxis(
                tickvals=tickvals,
                ticktext=ticktext,
                title='Número de viajes'),
            bargap=0.1

            )
        )





if __name__ == '__main__':
    app.run_server(debug=True)