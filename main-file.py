import pandas as pd
import uploadingData, tab1, tab2, tab3
import datetime as dt
import dash
from dash import dcc, html
from dash import Input, Output
import plotly.graph_objects as go
import numpy as np

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets, suppress_callback_exceptions=True)

app.layout = html.Div([html.Div([dcc.Tabs(id='tabs',value='tab-1',
                        children=[dcc.Tab(label='Sprzedaż globalna',value='tab-1'),
                        dcc.Tab(label='Produkty',value='tab-2'),
                        dcc.Tab(label='Kanały sprzedaży', value = 'tab-3')]),
                        html.Div(id='tabs-content')],
                        style={'width':'80%','margin':'auto'})], style={'height':'100%'})

@app.callback(Output('tabs-content','children'),[Input('tabs','value')])
def render_content(tab):

    if tab == 'tab-1':
        return tab1.render_tab(datas)
    elif tab == 'tab-2':
        return tab2.render_tab(datas)
    elif tab == 'tab-3':
        return tab3.render_tab(datas)

#tab1 wykres slupkowy aktualizacja
@app.callback(Output('bar-sales','figure'),
    [Input('sales-range','start_date'),Input('sales-range','end_date')])
def tab1_bar_sales(start_date,end_date):

    truncated = datas[(datas['tran_date']>=start_date)&
                          (datas['tran_date']<=end_date)]
    grouped = truncated[truncated['total_amt']>0].groupby(
        [pd.Grouper(key='tran_date',freq='ME'),'Store_type'])['total_amt'].sum().round(2).unstack()

    traces = []
    for col in grouped.columns:
        traces.append(go.Bar(x=grouped.index,y=grouped[col],name=col,hoverinfo='text',
            hovertext=[f'{y/1e3:.2f}k' for y in grouped[col].values]))

    data_1 = traces
    fig = go.Figure(data=data_1,layout=go.Layout(title='Przychody',barmode='stack',
                                               legend=dict(x=0,y=-0.5)))

    return fig

#tab1 wykres kartograficzny aktualizacja
@app.callback(Output('choropleth-sales','figure'),
            [Input('sales-range','start_date'),Input('sales-range','end_date')])
def tab1_choropleth_sales(start_date,end_date):

    truncated = datas[(datas['tran_date']>=start_date)&(datas['tran_date']<=end_date)]
    grouped = truncated[truncated['total_amt']>0].groupby('country')['total_amt'].sum().round(2)

    trace0 = go.Choropleth(colorscale='Viridis',reversescale=True,
                            locations=grouped.index,locationmode='country names',
                            z = grouped.values, colorbar=dict(title='Sales'))
    data_1 = [trace0]
    fig = go.Figure(data=data_1,layout=go.Layout(title='Mapa',geo=dict(showframe=False,
                                                                     projection={'type':'natural earth'})))

    return fig

#tab2 wykres kolumnowy aktualizacja
@app.callback(Output('barh-prod-subcat','figure'),
            [Input('prod_dropdown','value')])
def tab2_barh_prod_subcat(chosen_cat):

    grouped = datas[(datas['total_amt']>0)&(datas['prod_cat']==chosen_cat)].pivot_table(index='prod_subcat'
                    ,columns='Gender',values='total_amt',aggfunc='sum').assign(_sum=lambda x: x['F']+x['M']).sort_values(by='_sum').round(2)

    traces = []
    for col in ['F','M']:
        traces.append(go.Bar(x=grouped[col],y=grouped.index,orientation='h',name=col))

    data_1 = traces
    fig = go.Figure(data=data_1,layout=go.Layout(barmode='stack',margin={'t':20,}))
    return fig

#wykres w tab-3
@app.callback(Output('types', 'figure'),
              [Input('store_types', 'value')])
def types(canal):

    #sortowanie w jakiej kolejnosci maja sie pojawiac dni na wykresie
    #resetujemy idex by miec dostep do kolumny day a nasteponie ustawiamy ja by miala okreslona kolejnosc i ja sortujemy
    grouped = datas[(datas['Store_type'] == canal) & (datas['total_amt'] > 0)].groupby('day')['total_amt'].sum()
    grouped = grouped.reset_index()
    grouped['day'] = pd.Categorical(grouped['day'], categories=day_order, ordered=True)
    grouped = grouped.sort_values('day')
    fig = go.Figure(data=[go.Bar(x=grouped['day'],y=grouped['total_amt'])],layout=go.Layout(title='Udział grup produktów w sprzedaży'))

    return fig

#aktyalizacja tablicy z informacjami o kupujacych
@app.callback(
    Output('table', 'data'),
    Input('store_types', 'value'),
    Input('day_select', 'value')
)
def update_table(selected_store_type, day):
    # Filtr danych na podstawie wybranego Store_type
    filtered_data = datas[(datas['Store_type'] == selected_store_type) & (datas['total_amt'] > 0) & (datas['day'] == day)]
    filtered_data['day'] = pd.Categorical(filtered_data['day'], categories=day_order, ordered=True)
    filtered_data = filtered_data.sort_values('day')
    return filtered_data.to_dict('records')


def start():
    datas = uploadingData.init()

    def convert_dates(x):
            try:
                return dt.datetime.strptime(x,'%d-%m-%Y')
            except:
                return dt.datetime.strptime(x,'%d/%m/%Y')

    datas['tran_date'] = datas['tran_date'].apply(lambda x: convert_dates(x))
    datas['day'] = datas['tran_date'].apply(lambda x: dt.datetime.strftime(x, '%A'))
    
    datas['DOB'] = datas['DOB'].apply(lambda x: dt.datetime.strptime(x,'%d-%m-%Y'))
    datas['age'] = (dt.datetime(2024, 12, 24) - datas['DOB']) // np.timedelta64(365, 'D')
    
    datas['day'] = pd.Categorical(datas['day'], categories=day_order, ordered=True)

    return datas


if __name__ == '__main__':
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    datas = start()
    app.run_server(debug=True)
