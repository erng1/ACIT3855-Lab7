# ACIT 3855: Lab 3 - Data Storage & Synchronous Communication
# Author: Eric Ng A01086915
# Date: Oct. 7, 2021

import connexion
from connexion import NoContent

from sqlalchemy import create_engine, and_
from sqlalchemy.orm import sessionmaker
from base import Base
from weather_forecast import WeatherForecast
from misc_weather import MiscWeather

import yaml
import logging.config
import datetime

import json
from pykafka import KafkaClient
from pykafka.common import OffsetType
from threading import Thread

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


# setting variables from app_conf.yaml
user = app_config['datastore']['user']
password = app_config['datastore']['password']
hostname = app_config['datastore']['hostname']
port = app_config['datastore']['port']
db = app_config['datastore']['db']

DB_ENGINE = create_engine(f"mysql+pymysql://{user}:{password}@{hostname}:{port}/{db}")
Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)


def get_weather_forecast(start_timestamp, end_timestamp):
    """ Gets new weather forecasts after the timestamp """

    session = DB_SESSION()

    start_timestamp_datetime = datetime.datetime.strptime(start_timestamp, "%Y-%m-%dT%H:%M:%SZ")
    end_timestamp_datetime = datetime.datetime.strptime(end_timestamp, "%Y-%m-%dT%H:%M:%SZ")
    forecasts = session.query(WeatherForecast).filter(and_(WeatherForecast.date_created >= start_timestamp_datetime, WeatherForecast.date_created < end_timestamp_datetime))

    results_list = []
    for forecast in forecasts:
        results_list.append(forecast.to_dict())

    print(results_list)

    session.close()
    logger.info("Query for Weather Forecast after %s returns %d results" % (start_timestamp, len(results_list)))

    return results_list, 200


def get_misc_weather(start_timestamp, end_timestamp):
    """ Gets new misc weather info after the timestamp """

    session = DB_SESSION()

    start_timestamp_datetime = datetime.datetime.strptime(start_timestamp, "%Y-%m-%dT%H:%M:%SZ")
    end_timestamp_datetime = datetime.datetime.strptime(end_timestamp, "%Y-%m-%dT%H:%M:%SZ")
    misc_info = session.query(MiscWeather).filter(and_(MiscWeather.date_created >= start_timestamp_datetime, MiscWeather.date_created < end_timestamp_datetime))

    results_list = []
    for info in misc_info:
        results_list.append(info.to_dict())

    print(results_list)

    session.close()
    logger.info("Query for Weather Forecast after %s returns %d results" % (start_timestamp, len(results_list)))

    return results_list, 200


def process_messages():
    """ Process event messages """

    hostname2 = "%s:%d" % (app_config["events"]["hostname"], app_config["events"]["port"])

#    client = KafkaClient(hosts=hostname2)
#    topic = client.topics[str.encode(app_config["events"]["topic"])]

    retry_count = 0
    max_retries = app_config["connection"]["max_retries"]
    while retry_count < max_retries:
        try:
            logger.info("Attempting to connect to Kafka... Retry count: %s" % retry_count)
            client = KafkaClient(hosts=hostname2)
            topic = client.topics[str.encode(app_config["events"]["topic"])]
        except Exception:
            logger.error("Kafka connection failed.")
            time.sleep(app_config["connection"]["sleep_time"])
            retry_count += 1
            continue
        logger.info("Successfully connected to Kafka.")
        break

    # Create a consume on a consumer group, that only reads new messages
    # (uncommitted messages) when the service re-starts (i.e., it doesn't
    # read all the old messages from the history in the message queue).
    consumer = topic.get_simple_consumer(consumer_group=b'event_group',
                                         reset_offset_on_start=False,
                                         auto_offset_reset=OffsetType.LATEST)

    # This is blocking - it will wait for a new message
    for msg in consumer:
        msg_str = msg.value.decode('utf-8')
        msg = json.loads(msg_str)
        logger.info("Message: %s" % msg)

        payload = msg["payload"]

        if msg["type"] == "wf": # Change this to your event type
            # Store the event1 (i.e., the payload) to the DB
            session = DB_SESSION()

            wf = WeatherForecast(payload['location_id'],
                                 payload['location_name'],
                                 payload['weather'],
                                 payload['temperature'],
                                 payload['timestamp'])

            session.add(wf)

            session.commit()
            session.close()

            logger.debug("Stored event WeatherForecast request with a unique id of " + str(payload['location_id']))
        elif msg["type"] == "mw": # Change this to your event type
            # Store the event2 (i.e., the payload) to the DB
            session = DB_SESSION()

            mw = MiscWeather(payload['location_id'],
                             payload['location_name'],
                             payload['precipitation'],
                             payload['humidity'],
                             payload['wind'],
                             payload['air_quality'],
                             payload['timestamp'])

            session.add(mw)

            session.commit()
            session.close()

            logger.debug("Stored event MiscWeather request with a unique id of " + str(payload['location_id']))

        # Commit the new message as being read
        consumer.commit_offsets()


app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yaml",
            base_path="/storage",
            strict_validation=True,
            validate_responses=True)

if __name__ == "__main__":
    logger.info(f"Connecting to DB. Hostname:{hostname} Port:{port}")
    t1 = Thread(target=process_messages)
    t1.setDaemon(True)
    t1.start()
    app.run(port=8090)
