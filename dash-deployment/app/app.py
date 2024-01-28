from dash.dependencies import Output, Input
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
from flask import Flask
import pandas as pd
import dash
import numpy as np


server = Flask(__name__)
app = dash.Dash(server=server, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = 'Dashboard'

# Dataframe
dfCombined = pd.concat([pd.read_csv('./prim_semana_gener.csv'), pd.read_csv('./semana_sanvalentin.csv')], ignore_index=True)
dfCombined['tpep_pickup_datetime'] = pd.to_datetime(dfCombined['tpep_pickup_datetime'])
dfCombined['pickup_hour'] = dfCombined['tpep_pickup_datetime'].dt.hour

dfCombined['pickup_weekday'] = dfCombined['tpep_pickup_datetime'].dt.weekday

# Listas y diccionarios usados
# Dropdown options para los dias de la semana
days_of_week = ['Lunes', 'Martes', 'Miercoles', 'Jueves', 'Viernes', 'Sabado', 'Domingo']

graph2_options = ['Pasajeros', 'Metodo de Pago']

# RadioItems options para seleccionar la semana a visualizar
week_options = [
    {'label': 'Primera Semana de Enero', 'value': 'January'},
    {'label': "Semana de San Valentin", 'value': 'Valentine'},
]

# Metodos de pago para la leyenda del Pie Chart
payment_labels = {
    1: 'Tarjeta de Credito',
    2: 'Efectivo',
    3: 'Gratuito',
    4: 'Disputa'
}
# Dropdown options para eleccion de kilometros
graph3_options = ['Kilometros Totales',  'Kilometros Mediana']

# Callback para los cambios de graficas
@app.callback(
    [Output("line_chart", "figure"),
     Output("pie_chart", "figure"),
     Output("bar_chart", "figure"),],
    [Input("day-selector", "value"),
     Input("pas-pay-selector", "value"),
     Input("km-selector", "value"),
     Input("week-switch", "value")]
)
def update_charts(day, pas_pay, km, selected_week):
    print(day, pas_pay, selected_week)

    # Filtrar DataFrame según la semana seleccionada
    if selected_week == 'January':
        selected_df = dfCombined[dfCombined['tpep_pickup_datetime'].dt.month == 1]
        day_filter = int(day) + 2
    elif selected_week == 'Valentine':
        selected_df = dfCombined[dfCombined['tpep_pickup_datetime'].dt.month == 2]
        day_filter = int(day) + 8
    else:
        # Si no hay una selección válida, usa el DataFrame original
        selected_df = dfCombined

    # Filtrar DataFrame según el día seleccionado
    dfDiaFiltrat = selected_df[selected_df['tpep_pickup_datetime'].dt.day == day_filter]

    # Gráfico de línea
    mitjana_hora = dfDiaFiltrat.groupby('pickup_hour')['total_amount'].mean()
    fig_line = px.line(mitjana_hora,
                       x=np.arange(1, 25),
                       y="total_amount",
                       labels={"x": "Hora del dia", "total_amount": "Total ($)"},
                       title='Pagos')


    # Gráfico de pastel
    if pas_pay == 'Pasajeros':
        dfPasPay = selected_df['passenger_count']
        title = 'Distribucion de pasajeros'
    elif pas_pay == 'Metodo de Pago':
        dfPasPay = selected_df['payment_type'].map(payment_labels)
        title = 'Distribucion de metodos de pago'
    else:
        # Por defecto, mostrará la distribución de pasajeros
        dfPasPay = dfDiaFiltrat['passenger_count']
        title = 'Distribucion de pasajeros'

    fig_pie = px.pie(dfPasPay, names=dfPasPay.name, title=title)
    fig_pie.update_layout(legend=dict(traceorder='normal'))


    # Grafico de barras
    day_mapping = {i: day for i, day in enumerate(days_of_week)} # Mapeo de los dias de la semana
    selected_df['pickup_weekday_name'] = selected_df['pickup_weekday'].map(day_mapping)
    selected_df['pickup_weekday_name'] = pd.Categorical(selected_df['pickup_weekday_name'], 
                                        categories=days_of_week, ordered=True) # Lo ordenamos segun los dias de la semana (teniendo en cuenta los numeros 0-6)
    if km == 'Kilometros Totales':
        kms = selected_df.groupby('pickup_weekday_name')['trip_distance'].sum().reset_index()
        r1 = 900000
        r2 = 1250000
        nombre_y = 'Kilometros Recorridos'
        title = 'Kilometros Recorridos por Dia'

    elif km == 'Kilometros Mediana':
        kms = selected_df.groupby('pickup_weekday_name')['trip_distance'].mean().reset_index()
        r1 = 2
        r2 = 3.5
        nombre_y = 'Media de Kilómetros Recorridos'
        title = 'Media de Kilómetros Recorridos por Día'


    fig_bar = px.bar(kms,
                 x='pickup_weekday_name', y='trip_distance',
                 labels={'pickup_weekday_name': 'Dia de la Semana', 'trip_distance': nombre_y},
                 title=title)
        # Ajustar el rango del eje y
    fig_bar.update_layout(
        yaxis=dict(
            range=[r1, r2],  # Para visualizar mejor el grafico
        )
    )

    return fig_line, fig_pie, fig_bar

# Sample Graphs
graph1 = dcc.Graph(id="line_chart") # Grafico lineal
graph2 = dcc.Graph(id="pie_chart") # Grafico de pastel
graph3 = dcc.Graph(id="bar_chart") # Grafico de barras

# Define each dbc.Col as a separate variable
col1 = dbc.Col(
    dbc.Alert(
        [
            html.H4("Dinero Pagado por Hora", className="alert-heading"),
            dcc.Dropdown(
                id='day-selector',
                options=[{'label': day, 'value': str(index)}
                        for index, day in enumerate(days_of_week)],
                value='0',
                style={"marginTop": "20px"},
                className="",  # Remove Bootstrap styling
            ),
            graph1
        ],
        color="success",
        style={"margin": "20px"}  # Add margin to the borders
    ),
    width=4,
)

col2 = dbc.Col(
    dbc.Alert(
        [
            html.H4("Numero de Pasajeros / Metodos de pago", className="alert-heading"),
            dcc.Dropdown(
                id='pas-pay-selector',
                options=[{'label': option, 'value': option}
                        for option in graph2_options],
                value='Pasajeros',
                style={"marginTop": "20px"},
                className="",  # Remove Bootstrap styling
            ),
            graph2
        ],
        color="success",
        style={"margin": "20px"}  # Add margin to the borders
    ),
    width=4,
)

col3 = dbc.Col(
    dbc.Alert(
        [
            html.H4("Kilometros Totales / Mediana por Dia", className="alert-heading"),
            dcc.Dropdown(
                id='km-selector',
                options=[{'label': km, 'value': km}
                        for km in graph3_options],
                value='Kilometros Totales',
                style={"marginTop": "20px"},
                className="",  # Remove Bootstrap styling
            ),
            graph3
        ],
        color="success",
        style={"margin": "20px"}  # Add margin to the borders
    ),
    width=4,
)

app.layout = html.Div(
    style={"backgroundColor": "#f0f8ff", "minHeight": "100vh",
           "margin": "0", "padding": "0", "overflowX": "hidden"},
    children=[
        dbc.Row(
            dbc.Col(html.H1("Taxis de Nueva York", className="text-center",
                    style={"paddingTop": "60px"}), width={"size": 6, "offset": 3}),
            className="mb-4",
        ),
        dbc.Row([col1, col2, col3], className="justify-content-center",
                style={"marginTop": "60px"}),  # Add marginTop for spacing
        dbc.Row(
            [
                dbc.Col(
                    dcc.RadioItems(
                        id='week-switch',
                        options=week_options,
                        value='January',
                        style={"marginTop": "14px", 'font-size': '16px', 'whiteSpace': 'nowrap'},
                        className="",  # Remove Bootstrap styling
                    ),
                    width=1,
                ),
            ],
            className="justify-content-center",
        ),
    ]
)

if __name__=='__main__':
    app.run_server()