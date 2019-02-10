# -*- coding: utf-8 -*-
# this model simulates the work of a database as well as creating other core functionality for the endpoints:
# trains model, trains model, create visuals, and generate metrics

## import libraries
import pandas as pd
from fbprophet import Prophet
from fbprophet.diagnostics import cross_validation, performance_metrics
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import json
import csv
import plotly.offline as py
import plotly.graph_objs as go
import plotly.io as pio
import plotly.tools as tls
import os

## Import data
raw_data_df = pd.read_csv("/tmp/data/initial_data.csv", header = 0, names = ['ds', 'y'], parse_dates = True)
model = Prophet() # Prophet(yearly_seasonality=True)
fit = model.fit(raw_data_df)
#fig_initial = py.plot([go.Scatter(x=raw_data_df['ds'], y=raw_data_df['y'], name='initial')], filename='/tmp/data/visuals/initial_graph.html', auto_open=False)

# predict function
def predict(p, fit=fit):
    # extend periods for forecast
    future = fit.make_future_dataframe(periods=p, freq = 'W-FRI')
    # forecast
    forecast = fit.predict(future)

    return forecast[['ds','yhat']]

#function to save score (actual) data as csv file
def save_score_data(actual_data):
    #grab forecast name
    forecast_name = actual_data['forecast_name']
    # grab values as list
    values = actual_data['values']

    #save csv with actual values
    #with open('%s.csv' % forecast_name, 'w') as file:
        #for k in values:
            #file.write("%s,%d\n" % (k['date'],k['value']))

    #save actual values as csv
    with open('/tmp/data/actual/actual_data_%s.csv' % forecast_name, 'w') as file:
        writer=csv.writer(file, delimiter=',',lineterminator='\n',)
        writer.writerow(["ds","y"])
        for k in values:
            row = k['date'],k['value']
            writer.writerow(row)

    return 'data saved successfully'

# function to obtain metrics, sciki-learn way
def get_metrics(forecast_name):
    #read data from csv files
    actual_data = pd.read_csv('/tmp/data/actual/actual_data_%s.csv' % forecast_name, index_col=0, parse_dates=True)
    forecast = pd.read_csv('/tmp/data/forecasts/forecast_%s.csv' % forecast_name, index_col=0, parse_dates=True)
    initial_data = pd.read_csv('/tmp/data/initial_data.csv', parse_dates=True) #for visual
    #join actual data with forecast (yhat)
    metrics_df = pd.merge(forecast, actual_data, on='ds', how='inner')

    # calculate metrics
    r2 = r2_score(metrics_df.y, metrics_df.yhat)
    mse = mean_squared_error(metrics_df.y, metrics_df.yhat)
    mae = mean_absolute_error(metrics_df.y, metrics_df.yhat)

    #create graphs with all points integrated
    initial_trace = go.Scatter(x=initial_data['ds'], y=initial_data['y'], name='initial')
    actual_trace = go.Scatter(x=metrics_df.index, y=metrics_df['y'], name='actual')
    forecast_trace = go.Scatter(x=metrics_df.index, y=metrics_df['yhat'], name='forecast', mode='markers')
    graph_data = [initial_trace, actual_trace, forecast_trace]
    #layout = go.Layout(title="Actual vs $s Graph" % forecast_name, showlegend=True)
    #figure = go.Figure(data=graph_data, layout=layout)
    fig_complete = py.plot(graph_data, filename='/tmp/data/visuals/%s_graph.html' % forecast_name, auto_open=False)

    #save metrics as csv
    with open('/tmp/data/metrics/metrics_%s.csv' % forecast_name, 'w') as file:
        writer=csv.writer(file, delimiter=',',lineterminator='\n',)
        writer.writerow(["metric","score"])
        writer.writerow(["r2",r2])
        writer.writerow(["mse",mse])
        writer.writerow(["mae",mae])

    #these are not used yet, future-proofing our api
    return r2, mse, mae
