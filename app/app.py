# Import packages
from dash import Dash, html, dash_table, dcc, callback, Output, Input
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import logging 

# Incorporate data
hotel_df = pd.read_csv('hotel_bookings.csv')
di = {0:'Kept',1:'Canceled'}
hotel_df = hotel_df.replace({"is_canceled": di})
hotel_df['len_of_stay'] = hotel_df['stays_in_weekend_nights'] + hotel_df['stays_in_week_nights']
Q1 = hotel_df['adr'].quantile(0.25)
Q3 = hotel_df['adr'].quantile(0.75)
IQR = Q3 - Q1

# Define outliers
is_outlier = (hotel_df['adr'] < (Q1 - 1.5 * IQR)) | (hotel_df['adr'] > (Q3 + 1.5 * IQR))

# Remove outliers
cleaned_df = hotel_df[~is_outlier]

logging.basicConfig(filename='app.log', level=logging.DEBUG)

# Initialize the app
app = Dash()
server = app.server

# App layout
app.layout = [
    html.Div(children='Hotel Booking Analysis'),
    html.Hr(),
    dcc.RadioItems(options=['distribution_channel', 'market_segment','deposit_type'], value='distribution_channel', id='controls-and-radio-item'),
    dcc.Graph(figure={}, id='controls-and-graph'),
    dcc.Graph(figure={},id = 'box-and-whiskers'),
    dcc.Graph(figure = {}, id = 'test')
]

# Callback for both the bar and box plots
@callback(
    [Output('controls-and-graph', 'figure'), Output('box-and-whiskers', 'figure'), Output('test', 'figure')],
    Input('controls-and-radio-item', 'value')
)
def update_graph(col_chosen):
    # Bar chart data
    hotel_df_chart = hotel_df[['is_canceled', col_chosen]]
    plot_df_agg1 = hotel_df_chart.groupby(['is_canceled', col_chosen]).agg(count=('is_canceled', 'count')).reset_index()
    bar_fig = px.bar(plot_df_agg1, x=col_chosen, y='count', color='is_canceled', title="Bookings and Cancellations")

    # Box plot data
    box_fig = px.violin(hotel_df, y=col_chosen, x='lead_time', title="Lead Time Distributions")

    #dist fig
    dist_fig = px.violin(cleaned_df, y='adr', x=col_chosen, title = 'Revenue Distributions')
    return bar_fig, box_fig, dist_fig

# Run the app
if __name__ == '__main__':
    app.run(debug=True)

