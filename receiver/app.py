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

import time

import os


if "TARGET_ENV" in os.environ and os.environ["TARGET_ENV"] == "test":
    print("In Test Environment")
    app_conf_file = "/config/app_conf.yaml"
    log_conf_file = "/config/log_conf.yaml"
else:
    print("In Dev Environment")
    app_conf_file = "app_conf.yaml"
    log_conf_file = "log_conf.yaml"

with open(app_conf_file, 'r') as f:
    app_config = yaml.safe_load(f.read())

# External Logging Configuration
with open(log_conf_file, 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')

logger.info("App Conf File: %s" % app_conf_file)
logger.info("Log Conf File: %s" % log_conf_file)


kafka_server = app_config['events']['hostname']
kafka_port = app_config['events']['port']
kafka_topic = app_config['events']['topic']

retry_count = 0
max_retries = app_config["connection"]["max_retries"]
while retry_count < max_retries:
    logger.info("Attempting to connect to Kafka... Retry count: %s" % retry_count)
    try:
        client = KafkaClient(hosts=f'{kafka_server}:{kafka_port}')
        topic = client.topics[str.encode(kafka_topic)]
    except Exception:
        logger.error("Kafka connection failed.")
        time.sleep(app_config["connection"]["sleep_time"])
        retry_count += 1
        continue
    logger.info("Successfully connected to Kafka.")
    break


def report_weather_forecast(body):
    """ Receives weather forecast """

    logger.info("Received event WeatherForecast request with a unique ID of " + str(body['location_id']))

    topic = client.topics[str.encode(kafka_topic)]

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
            base_path="/receiver",
            strict_validation=True,
            validate_responses=True)

if __name__ == "__main__":
    app.run(port=8080)
