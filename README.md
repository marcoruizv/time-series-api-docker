# PoC - Dockerized Time Series API

This is a proof of concept api meant to showcase how a time series model can be exposed via an API and containerized for deployment.

The dummy training data and the model itself are not tuned for accuracy, they were simply used to show how quickly and easy it is to get set up and running with Dockerized apps.

## Usage

In order to use this api, you need to have Docker installed.
For more on how to do that for your system, please refer to the official [Docker documentation](https://docs.docker.com/).

Once you have Docker installed, you can then run the following command to build an image from the Dockerfile:
``` bash
docker build -t [TAGNAME] [DOCKERFILEPATH]

# if this command returns an access error, try running with admin prviledeges/root (e.g. sudo docker)
# [TAGNAME] can be anything you want, this is jsut a tag for your container (e.g. time-series)
# [DOCKERFILEPATH] provide the path to the directory that contains the Dockerfile for this api (e.g. /Users/mruiz/projects/time-series-api-docker/)
```

And then run the following to run your new container:
``` bash
docker run -p 5000:5000 [TAGNAME]
# -p 5000:5000 the p flag exposes a HOST:CONTAINER port
# [TAGNAME] name tag of image you want to run
```

That's it! You can test that the API is running via curl:
`curl http://0.0.0.0:5000`
Or simply open up your browser and navigate to `http://0.0.0.0:5000`

## Using the sample Time Series Model API

For this PoC, there are 6 endpoints that showcase both GET and POST methods.
When the server is initiated (when you run the Docker container), a simple time series model is trained with the following data:

| ds            |  y  |
| ------------- |:---:|
| 2018-01-05    | 10  |
| 2018-01-12    | 20  |
| 2018-01-19    | 30  |
| ...           | ... |

Where:
- `ds` is the date with weekly frequency on Fridays for the first 40 weeks of 2018
- `y` is the value cycling from 10-90-10 in intervals of 10 (10,20,...90,80,70,...)

**Endpoints and their usage:**

To use the sample time series API, you need to be aware of the following endpoints, their accepted methods, and data value formats:

`publicurl:5000/` [GET]
This is the APIs "home" address, you should simply see a message stating that the server is up and running.

`/models` [GET]
This will return all the models available to use. In our case, only the sample model is available.

`/forecasts` [GET/POST]
GET - will return all the forecasts that have been created. Initially, it should return sample data.
POST - receives forecast name as a string and an integer that equals the length of the forecast we want to create.
For this sample model, we'd want to create a forecast based on number of weeks into the future (obviously, given that this is a sample, we'd want data points that fit our training model)

`/metrics` [POST]
Will receive forecast name (has to be an existing forecast) and data values (ds, y) to create metrics for the model.

`/graphs/all` [GET]
Show a list of viewable forecast graphs.

`/graphs/<forecast_name>` [GET]
Automatically download forecast graph (must provide existing forecast name).


The following python script can be used to create a forecast (`/forecasts` [POST]):
``` python
import requests

url = "[URL_timeSeriesAPI]/forecasts"
data = {"name": "twelve-week", "length": 12}
headers = {"Content-type": "application/json", "Accept": "text/plain"}

r = requests.post(url, json=data, headers=headers)
```

The following python script can be used to post actual data and create metrics for our forecast (`/metrics` [POST]):
``` python
import requests

url = "[jupyterURL]/metrics"
data = {"forecast_name": "twelve-week", "values": [{"date": "2018-10-05", "value":80},{"date": "2018-10-12", "value":90},{"date": "2018-10-19", "value":80},{"date": "2018-10-26", "value":70},{"date": "2018-11-02", "value":60},{"date": "2018-11-09", "value":50},{"date": "2018-11-16", "value":40},{"date": "2018-11-23", "value":30},{"date": "2018-11-30", "value":20},{"date": "2018-12-07", "value":10},{"date": "2018-12-14", "value":20},{"date": "2018-12-21", "value":30}]}
headers = {"Content-type": "application/json", "Accept": "text/plain"}

r = requests.post(url, json=data, headers=headers)
```