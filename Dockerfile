#base image for code
FROM python:3

COPY ./code/requirements.txt /tmp/
RUN pip install --upgrade pip
RUN pip install --requirement /tmp/requirements.txt
COPY . /tmp/

# command to execute when image loads
CMD [ "python", "/tmp/code/server.py"]

# to rm image: docker rmi --force [id]
# to build:  docker build -t naive-time-series .
# to run: docker run naive-time-series
