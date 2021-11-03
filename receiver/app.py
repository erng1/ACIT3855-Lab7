# ACIT 3855: Lab 2 - Edge Service and Testing
# Author: Eric Ng A01086915
# Date: Sept. 22, 2021

import connexion
from connexion import NoContent
import requests
import yaml
import logging.config

import datetime
import json
from pykafka import KafkaClient

with open('app_conf.yaml', 'r') as f:
    app_config = yaml.safe_load(f.read())


with open('log_conf.yaml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')


def report_weather_forecast(body):
    """ Receives weather forecast """

    logger.info("Received event WeatherForecast request with a unique ID of " + str(body['location_id']))

    kafka_server = app_config['events']['hostname']
    kafka_port = app_config['events']['port']
    topic = app_config['events']['topic']

    client = KafkaClient(hosts=f'{kafka_server}:{kafka_port}')
    topic = client.topics[str.encode(topic)]
    producer = topic.get_sync_producer()
    msg = {"type": "wf",
           "datetime": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
           "payload": body}
    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode('utf-8'))

    logger.info("Returned event WeatherForecast response (ID: " + str(body['location_id']) + ") with status " + str(201))

    return NoContent, 201


def report_misc_weather(body):
    """ Receive misc weather information """

    logger.info("Received event MiscWeather request with a unique ID of " + str(body['location_id']))

    kafka_server = app_config['events']['hostname']
    kafka_port = app_config['events']['port']
    topic = app_config['events']['topic']

    client = KafkaClient(hosts=f'{kafka_server}:{kafka_port}')
    topic = client.topics[str.encode(topic)]
    producer = topic.get_sync_producer()
    msg = {"type": "mw",
           "datetime": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
           "payload": body}
    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode('utf-8'))

    logger.info("Returned event MiscWeather response (ID: " + str(body['location_id']) + ") with status " + str(201))

    return NoContent, 201


app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yaml",
            strict_validation=True,
            validate_responses=True)

if __name__ == "__main__":
    app.run(port=8080)
