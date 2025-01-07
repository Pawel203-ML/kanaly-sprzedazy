import dash
from dash import dcc, html, dash_table
import plotly.graph_objs as go
import pandas as pd


def render_tab(df):

    layout = html.Div([
        html.H1('Kanały sprzedaży',style={'text-align':'center'}),
        html.Div([
            html.Div([dcc.Graph(id = 'types')
            ], style = {'width' : '50%'}),
            html.Div([
                dcc.Dropdown(id='store_types',
                                    options=[{'label':store ,'value':store} for store in df['Store_type'].unique()],
                                    value=df['Store_type'].unique()[0], 
                                    style = {'width' : '60%'}),
                dcc.Dropdown(id = 'day_select',
                                    options = [{'label' : day, 'value' : day} for day in df['day'].unique()],
                                    value = df['day'].unique()[0],
                                    style = {'width' : '60%'}),
                html.Br(),
                dash_table.DataTable(
                    id = 'table',
                    columns = [{'name' : col, 'id' : col} for col in df[['cust_id', 'country', 'country_code', 'total_amt', 'age']]],
                    data = df.to_dict('records'),
                    style_table = {'overflowY' : 'auto', 'height' : '400px'},
                    style_cell = {'textAlign' : 'center'}
                )
            ], style = {'width' : '50%'})
        ], style={'display': 'flex', 'flex-direction': 'row'})
    ])

    return layout
    