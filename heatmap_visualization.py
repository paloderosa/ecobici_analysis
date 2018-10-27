# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go

from bike_service import *

mapbox_access_token = 'pk.eyJ1IjoicGFsb2Rlcm9zYSIsImEiOiJjam5wajQzZXIydDBvM3Bvanh3NDR2bWR3In0.T9up8wLMrjeV4Gp0YfCSgA'

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

delegaciones = ['Cuauhtemoc, Mexico City, Mexico',
                'Benito Juárez, Mexico City, Mexico',
                'Miguel Hidalgo, Mexico City, Mexico']

network_df = pd.read_csv('data/ecobici_stations.csv', index_col=0)

activity_df = pd.read_csv('data/2018-08.csv', index_col=0)
activity_df_take = activity_df[activity_df['Fecha_Retiro']=='01/08/2018'].groupby('Ciclo_Estacion_Retiro').count()
activity_df_lock = activity_df[activity_df['Fecha_Arribo']=='01/08/2018'].groupby('Ciclo_Estacion_Arribo').count()

sizes_take = np.zeros(480)
sizes_lock = np.zeros(480)

for i in range(1,481):
    if i in activity_df_take.index:
        sizes_take[i-1] = activity_df_take.at[i,'Genero_Usuario']

    if i in activity_df_lock.index:
        sizes_lock[i-1] = activity_df_lock.at[i,'Genero_Usuario']

distances = np.load('data/street_distances.npy')


app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(children=[
    html.H1(children='Ecobici'),

    html.Div(children='''
        Datos abiertos de Ecobici.
    '''),

    html.Div([
        html.Div(
            dcc.Graph(id = "heatmap",
                      figure = go.Figure(
                          data = [go.Heatmap(z=distances,
                                             colorscale='Reds',
                                             reversescale=True,
                                             showlegend=False,
                                             showscale=False
                                             )
                                  ],
                          layout=go.Layout(autosize=False,
                                           width = 800,
                                           height = 800,
                                           xaxis=dict(ticks = '',
                                                      showticklabels = False),
                                           yaxis=dict(ticks = '',
                                                      showticklabels = False)
                                           )
                      )
                      ),
            style={'width': '43%', 'padding': '0 20', 'display': 'inline-block'}
        ),

        html.Div(
            dcc.Slider(id='crossfilter-year--slider',
                       min=1,
                       max=31,
                       value=31,
                       marks={str(day): str(day) for day in range(1, 32)},
                       vertical=True
                       ),
            style={'width': '3%', 'height': '600px', 'padding': '0 20', 'display': 'inline-block', 'z-index': '100', 'padding-bottom': '90px'}
        ),

        html.Div(
            dcc.Graph(id = 'routes',
                      figure = go.Figure(
                          data = [go.Scattermapbox(lat=network_df['lat'],
                                                   lon=network_df['lon'],
                                                   mode='markers',
                                                   marker=dict(size=sizes_take//10,
                                                               color= '#FF1A1A',
                                                               opacity = 0.3),
                                                   text=network_df['name'],
                                                   name='Préstamos'
                                                   ),
                                  go.Scattermapbox(lat=network_df['lat'],
                                                   lon=network_df['lon'],
                                                   mode='markers',
                                                   marker=dict(size=sizes_lock//10,
                                                               color= '#FF9D1A',
                                                               opacity = 0.3),
                                                   text=network_df['name'],
                                                   name='Devoluciones'
                                                   )
                                  ],
                          layout = go.Layout(autosize=False,
                                             width=1000,
                                             height=800,
                                             hovermode='closest',
                                             mapbox=dict(accesstoken=mapbox_access_token,
                                                         bearing=0,
                                                         center=dict(
                                                             lat=19.40,
                                                             lon=-99.16
                                                         ),
                                                         pitch=0,
                                                         zoom=12.1,
                                                         style='light'
                                                         ),
                                             )
                      )
            ), style={'width': '52%', 'padding': '0 20', 'display': 'inline-block'}
        )
    ], style = {'height': '800px', 'width': '100%'}
    )
], style = {'width': '100%', 'margin': 'auto', 'position': 'relative'}
)



if __name__ == '__main__':
    app.run_server(debug=True)