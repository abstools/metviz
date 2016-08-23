
"""
A metric visualization tool
"""

import logging
import random
import time
import statsd

def send_metric(metric, value):
    """ Sends a specific metric to StatsD server.
    The metric is assumed to be of type 'gauge'.
    The value must be an integer.

    metric - the metric name
    value - the value of the metric
    """
    client = statsd.StatsClient('localhost', 8125)
    client.gauge(metric, value)

def main():
    while True:
        delay = random.random() * 5
        time.sleep(delay)
        logging.info("Delayed: %s", delay)
        send_metric('fas.gamma.200ms', random.randint(100, 200))
        send_metric('fas.gamma.500ms', random.randint(500, 1000))


if __name__ == "__main__":
   logging.basicConfig(
        format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO)
   main()
