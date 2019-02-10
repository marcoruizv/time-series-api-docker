# -*- coding: utf-8 -*-
# This script creates a flask server for the time series api and its endpoints

import os
from flask import Flask, jsonify, request, make_response, send_from_directory
import json
from model import predict, save_score_data, get_metrics

HEADERS = {'Content-type': 'application/json', 'Accept': 'text/plain'}

# define api
def flask_app():
    app = Flask(__name__)

    #defining sample forecasts dictionary
    #this is here simply so we can get some sample data when we call this endpoint
    forecasts = [{ 'name': 'sample','length': 5}]

    #define models (only one for now)
    models = [{ 'id': 1, 'model_type': 'time series model with fbprophet'}]

    #define error handler for unexisting endpoints
    @app.errorhandler(404)
    def not_found(error):
        return make_response(jsonify({'error': 'Not found'}), 404)

    #define home endpoint
    @app.route('/', methods=['GET'])
    def home():
        return '<h1> This is a prototype for an API</h1><p>Server is up and running</p>'

    #retrieve models
    @app.route('/models', methods=['GET'])
    def get_models():
        return jsonify(models)

    #define how to get created forecasts
    @app.route('/forecasts', methods=['GET'])
    def get_forecasts():
        return jsonify(forecasts)

    #define how to post forecasts
    @app.route('/forecasts', methods=['POST'])
    def create_forecast():
        # store forecast name and length for future reference
        forecasts.append(request.get_json())

        # create prediction of specified length (in weeks)
        pred = predict(request.json.get('length'))

        # save forecast to file
        file_name = request.json.get('name')
        pred.to_csv(r'/tmp/data/forecasts/forecast_{}.csv'.format(file_name), index=False)
        return '', 'Success'

    #post actual data to create model score
    @app.route('/metrics', methods=['POST'])
    def post_scores():
        #get name of forecast
        forecast_name = request.json.get('forecast_name')
        #save score data as csv
        save_score_data(request.get_json())
        #execute function that compares forecast data to actual
        get_metrics(forecast_name)

        return 'Success'

    #retrieve list of reports available
    @app.route('/graphs/all', methods=['GET'])
    def get_reports():
        #show list of all reports that can be generated
        ls_dir=os.listdir('/tmp/data/metrics')
        ls_files=[x.split('.')[0] for x in ls_dir if not x.startswith('.')]
        report_list = [x.split("metrics_")[1] for x in ls_files]

        return jsonify(report_list)

    #retrieve report by name
    @app.route('/graphs/<string:name>', methods=['GET'])
    def get_report(name):
        #get list of all reports that can be created
        ls_dir=os.listdir('/tmp/data/metrics')
        ls_files=[x.split('.')[0] for x in ls_dir if not x.startswith('.')]
        report_list = [x.split("metrics_")[1] for x in ls_files]

        # Check if a name was provided as part of the URL.
        # If name is provided/exists in our list, generate visuals and return report.
        # If no name is provided, display an error in the browser.
        if name in report_list:
            return send_from_directory('/tmp/data/visuals/', '%s_graph.html' % name, as_attachment=True)
            #return "report is good"
        else:
            return "Error: No forecast name provided. Please specify one."

    return app

# start the app!
if __name__ == '__main__':
    app = flask_app()
    app.run(debug=True, host='0.0.0.0')