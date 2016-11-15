# metviz

A tool that relays metrics (as time-series) from an HTTP endpoint in an ABS model to InfluxDB for visualization.

## Installation

* Install Python 3+
```bash
$ sudo apt-get install python3
```
* Install Python 3 pip
```bash
$ sudo apt-get install python3-pip
```
* Install Python Requests
```bash
$ (sudo) pip3 install requests
```
* Install modgrammar
```bash
$ (sudo) pip3 install modgrammar
```
* Install docker
```bash
$ sudo apt-get install docker-engine
```

## Configuration

* Start the monitoring backend. For more information refer to [here][mon]:
```bash
$ ./run-monitoring.sh
```
* Go to InfluxDB admin at http://localhost:3004
* Use *Query Templates* to create a database `datasource` if it does not exist.
* Go to Grafana at http://localhost:3003
* Use `root/root` to log in
* From top-left menu, go to *Data Sources* to configure one
    * Name: `default` and also check *Default* option
    * Type: `InfluxDB`
    * URL: `http://localhost:8086`
    * Access: `direct`
    * Database: `datasource`
    * User/Pass: `datasource/datasource`
* From top-left menu, go to *Dashboards* to *Import* one
    * Use the file in the root of this repository `Metric-Viz.json`.
    * Use the above `default` data source for the dashboard.
    * Save and open the dashboard

## Running

### Debug mode

If the backend for metrics data from ABS is not available, run the following to 
use the tool in a sample test data mode:

```bash
$ python metviz.py TEST
```

### Production mode

To use the tool against a running ABS metric endpoint:

```bash
$ python metviz.py http://localhost:9999/X/Y/Z
```

The above endpoint should be accessible with HTTP `GET` method with the specified
JSON format.

[mon]: https://github.com/advantageous/docker-grafana-statsd/
