"""
A metric visualization tool
"""

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

def send_metrics(metrics, t0 = T0, host = "localhost", port = 8086, db = 'datasource'):
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
            delta = int(m_time)
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

def start(func_metrics, metrics_url, interval=9.5, t0=T0, ds_host='localhost', ds_port=8086, ds_db = 'datasource'):
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
        send_metrics(metrics, t0, ds_host, ds_port, ds_db)
        logging.info("Wating %s for the next round ...", interval)
        time.sleep(interval)

def main(args):
    """The main function to start the program

    args -- the command line arguments
    """
    metrics_url = args[1]
    func_get_metrics = get_metrics_example if metrics_url == "TEST" else get_metrics
    interval = float(args[2]) if len(args) >= 3 else 9.5
    t0 = datetime.strptime(args[3], '%Y-%m-%d_%H-%M-%S') if len(args) >=4 else datetime.utcnow()
    ds_host = args[4] if len(args) >= 5 else 'localhost'
    ds_port = int(args[5]) if len(args) >= 6 else 8086
    ds_db = args[6] if len(args) == 7 else 'datasource'
    start(func_get_metrics, metrics_url, interval, t0, ds_host, ds_port, ds_db)

if __name__ == "__main__":
    logging.basicConfig(
        format='%(asctime)s %(levelname)s %(message)s', level=logging.DEBUG)

    # Optional: `pip3 install coloredlogs`
    try:
        import coloredlogs
        coloredlogs.install(level = 'DEBUG')
    except:
        pass

    if len(sys.argv) == 1 or len(sys.argv) > 7:
        usage = """
Usage:

python3.5 metviz.py URL [INTERVAL] [T0] [DS_HOST] [DS_PORT] [DS_DB]

        URL:        the URL from which to retrieve raw metrics data.
                    If the value 'TEST' is provided, the program runs
                    on a sample data set without using the connecting
                    to ABS remote to obtain metrics.
        INTERVAL:   the interval (seconds) between each cycle (default: 9.5)
        T0:         the time of the start of the system for data backend.
                    All the time should be in UTC time zone. If not provided,
                    UTC `now()` is used as the reference. The format to provide
                    this time is '%Y-%m-%d_%H-%M-%S'; e.g. '2001-03-05_06-12-09'.
        DS_HOST:    the host of the data backend (default: localhost)
        DS_PORT:    the port of the data backend (default: 8086)
        DS_DB:      the name of the database in the data backend (default: datasource)

        """
        logging.info("%s", usage)
        sys.exit(1)
    if sys.argv[1] == "TEST":
        DEBUG = True
        logging.warn("DEBUG mode enabled")
    main(sys.argv)
