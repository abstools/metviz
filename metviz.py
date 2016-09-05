"""
A metric visualization tool
"""

import argparse
from datetime import datetime, timedelta
import json
import logging
import random
import time
import requests
from grammar import *

# The start time of the script
T0 = datetime.utcnow()

# EPOCH: 1-1-1970
EPOCH = datetime.utcfromtimestamp(0)

# Development Mode
DEBUG = False

def get_metrics(url):
    """Makes a GET HTTP request to the specified
    URL to obtain the JSON result for the metric
    measurements.
    """
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        logging.error("GET %s -> %s", url, response.status_code)
        return "{}"

def get_metrics_example(url):
    """Returns a fixed example string
    for testing and development
    """
    return {"result" : "list[Pair(Time(2206),list[Pair(\"gamma.fas.live.200ms\", 30),Pair(\"gamma.fas.live.500ms\", 5)]),Pair(Time(1485),list[Pair(\"gamma.fas.live.200ms\", 25)])]"}

def process_metrics(values):
    """Processes metrics values as JSON
    object and if necessary parses them from 
    specific ABS format to general JSON format.

    values -- the metrics values in 'some' JSON format
    """
    if 'result' in values:
        if values['result'] == 'Nil':
            return []
        return parse(values['result'])
    else:
        # Assume this is proper JSON
        return values

def send_metrics(metrics, t0 = T0, ccf = 1.0, host = "localhost", port = 8086, db = 'datasource'):
    """Send a bag of metrics to a data backend.

    metrics -- the dict of metric values
    t0 -- the start time of the monitoring system
    host -- the host at which the data source is receiving measurements
    port -- the port of the data source
    db -- the database name in the data backend
    """
    ds_url = 'http://{0}:{1}/write?db={2}'.format(host, port, db)
    for m in metrics:
        m_time, metric_values = list(m.items())[0]
        for measurement in metric_values:
            key, value = list(measurement.items())[0]
            delta = int(float(m_time) * ccf)
            actual_time = datetime.utcnow() if DEBUG else (t0 + timedelta(milliseconds = delta))
            epoch_nanos = to_nano(actual_time - EPOCH)
            # Protocol: "METRIC[,TAGS] value=VAL TIMESTAMP"
            line_protocol = '{0} value={1} {2}'.format(key, float(value), epoch_nanos)
            logging.info("Writing metric: %s", line_protocol)
            response = requests.post(ds_url, data = line_protocol)
            logging.info("POST metric %s -> %s", key, response.status_code)
            if response.status_code >= 300:
                logging.warn("POST %s: \%s", key, response.text)

def to_nano(td):
    """Convert a datetime.timedelta object
    to nanoseconds from epoch (1-1-1970)

    td -- the timedelta object
    """
    return int(1000000000 * td.total_seconds())

def start(func_metrics, metrics_url, interval=9.5, t0=T0, ccf=1.0, ds_host='localhost', ds_port=8086, ds_db = 'datasource'):
    """Start the cycle to get metrics, process the metrics,
    and write them to the data source.

    metrics_url -- the URL from which to retrieve raw metrics
    interval -- the delay in seconds between each cycle
    t0 -- the time for the start of the system
    ds_host -- the host of the data backend for metrics
    ds_port -- the port of the data backend
    """
    while True:
        raw_metrics = func_metrics(metrics_url)
        metrics = process_metrics(raw_metrics)
        send_metrics(metrics, t0, ccf, ds_host, ds_port, ds_db)
        logging.info("Waiting %s for the next round ...", interval)
        time.sleep(interval)

def args_parser():
    """ Create a CLI argument parser
    """
    parser = argparse.ArgumentParser(prog = 'metviz.py',
        description = 'Visualize metrics. Requires Python 3.x.')
    parser.add_argument('--url', required = True,
        help = "The URL from which to retrieve raw metrics data. If the value 'TEST' is provided, the program runs on a sample data set without using the connecting to ABS remote to obtain metrics.")
    parser.add_argument('--interval', default = '9.5', required = False,
        help = "The interval (seconds) between each cycle")
    parser.add_argument('--t0', required = False,
        help = "The time of the start of the system for data backend. All the time should be in UTC time zone. If not provided, UTC `now()` is used as the reference. The format to provide this time is 'Y-m-d_H-M-S'; e.g. '2001-03-05_06-12-09'.")
    parser.add_argument('--ccf', required = False, default = "1.0",
        help = "Clock Cycle Factor. A double value in (0, 1) to denote the clock cycles factor in relation with real-time clock. A value of 1 means the same clock cycle factor as Python 'time' module sees.")
    parser.add_argument('--host', default = 'localhost', required = False,
        help = "The host of the data backend")
    parser.add_argument('--port', default = '8086', required = False,
        help = "The port of the data backend")
    parser.add_argument('--database', default = 'datasource', required = False,
        help = "The name of the database in the data backend")
    return parser

def main(args):
    """The main function to start the program

    args -- the command line arguments
    """
    metrics_url = args.url
    func_get_metrics = get_metrics_example if metrics_url == "TEST" else get_metrics
    interval = float(args.interval)
    t0 = datetime.strptime(args.t0, '%Y-%m-%d_%H-%M-%S') if args.t0 != None else datetime.utcnow()
    ccf = float(args.ccf)
    ds_host = args.host
    ds_port = int(args.port)
    ds_db = args.database
    start(func_get_metrics, metrics_url, interval, t0, ccf, ds_host, ds_port, ds_db)

if __name__ == "__main__":
    logging.basicConfig(
        format='%(asctime)s %(levelname)s %(message)s', level=logging.DEBUG)

    # Optional: `pip3 install coloredlogs`
    try:
        import coloredlogs
        coloredlogs.install(level = 'DEBUG')
    except:
        pass

    cli_parser = args_parser()
    args = cli_parser.parse_args()
    if args.url == "TEST":
        DEBUG = True
        logging.warn("DEBUG mode enabled")
    main(args)
