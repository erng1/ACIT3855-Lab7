# ACIT 3855: Lab 5 - Processing Service
# Author: Eric Ng A01086915
# Date: Oct. 21, 2021

import connexion

import yaml
import logging.config
import datetime
from apscheduler.schedulers.background import BackgroundScheduler
import json
import os
import requests

from flask_cors import CORS, cross_origin


<<<<<<< Updated upstream
=======
if "TARGET_ENV" not in os.environ or os.environ["TARGET_ENV"] != "test":
    CORS(app.app)
    app.app.config['CORS_HEADERS'] = 'Content-Type'

>>>>>>> Stashed changes
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


def get_stats():
    """ Gets Weather Forecast and Misc Weather processed stats """

    logger.info("Statistics retrieval started.")

    if os.path.isfile('/data/data.json'):
        with open('/data/data.json', 'r') as f:
            data = json.loads(f.read())
    else:
        logger.error("File does not exist. Failed to retrieve statistics.")
        err_message = "Statistics do not exist."
        return err_message, 404

    logger.debug("Contents:", data)
    logger.info("get_stats request complete.")

    return data, 200


def populate_stats():
    """ Periodically update stats """

    logger.info("Periodic processing started.")

    if os.path.isfile('/data/data.json'):
        with open('/data/data.json', 'r') as f:
            data = json.loads(f.read())
    else:
        data = {
            "num_wf_reports": 0,
            "max_temperature": 0,
            "min_temperature": 0,
            "num_mw_reports": 0,
            "last_updated": "2021-02-05T12:39:16Z"
        }

    # get current timestamp
    current_timestamp = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")

    last_updated = data['last_updated']

    # get rows from weather_forecast table
    url1 = app_config['eventstore1']['url'] + "?start_timestamp=" + last_updated + "&end_timestamp=" + current_timestamp
    response1 = requests.get(url1)
    events1 = json.loads(response1.content)
    logger.info("Received " + str(len(events1)) + " events")
    #print("Events1:", events1)
    print("Current timestamp:", current_timestamp)
    print("Events dates:", end=" ")
    print(events['date_created'] for events in events1)
    if response1.status_code != 200:
        logger.error("Invalid Weather Forecast get request")

    # get rows from misc_weather table
    url2 = app_config['eventstore2']['url'] + "?start_timestamp=" + last_updated + "&end_timestamp=" + current_timestamp
    response2 = requests.get(url2)
    events2 = json.loads(response2.content)
    #print("Events2:", events2)
    print("Current timestamp:", current_timestamp)
    print("Events dates:", end=" ")
    print(events['date_created'] for events in events2)
    logger.info("Received " + str(len(events2)) + " events")
    if response2.status_code != 200:
        logger.error("Invalid Misc Weather get request")

    # cumulatively calculate new stats
    if events1:
        data['num_wf_reports'] += len(events1)
        max_temp = max(events['temperature'] for events in events1)
        min_temp = min(events['temperature'] for events in events1)
        if max_temp > data['max_temperature']:
            data['max_temperature'] = max_temp
        if min_temp < data['min_temperature']:
            data['min_temperature'] = min_temp
    if events2:
        data['num_mw_reports'] += len(events2)
    data['last_updated'] = current_timestamp

    with open('/data/data.json', 'w+') as f:
        f.write(json.dumps(data, indent=4))


def init_scheduler():
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(populate_stats, 'interval', seconds=app_config['scheduler']['period_sec'])
    sched.start()


app = connexion.FlaskApp(__name__, specification_dir='')
CORS(app.app)
app.app.config['CORS_HEADERS'] = 'Content-Type'
app.add_api("openapi.yaml",
            base_path="/processing",
            strict_validation=True,
            validate_responses=True)

if __name__ == "__main__":
    init_scheduler()
    app.run(port=8100, use_reloader=False)
