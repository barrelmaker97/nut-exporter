#!/usr/bin/env python3
from prometheus_client import start_http_server, Gauge
import os
import time
import signal
import logging
import socket
import itertools
from nut2 import PyNUTClient


class GracefulKiller:
    kill_now = False

    def __init__(self):
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self, signum, frame):
        self.kill_now = True


# Lists of possible UPS states, to be used by label-based metrics
statuses = ["OL", "OB", "LB", "RB", "CHRG", "DISCHRG", "ALARM", "OVER", "TRIM", "BOOST", "BYPASS", "OFF", "CAL", "TEST", "FSD"]
beeper_statuses = ["enabled", "disabled", "muted"]

# Labeled metrics
ups_beeper_status = Gauge("ups_beeper_status", "Beeper Status", ["status"])
ups_status = Gauge("ups_status", "UPS Status Code", ["status"])


# Resets all metrics to 0
def clear_metrics(metrics):
    # Clear basic metrics
    for metric in metrics:
        metrics.get(metric).set(0)

def clear_label_metrics():
    # Clear metrics with labels
    for status in beeper_statuses:
        ups_beeper_status.labels(status).set(0)
    for status in statuses:
        ups_status.labels(status).set(0)


# Read data from UPS
def check_metrics(data, metrics):
    # Set basic metrics
    for metric in metrics:
        metrics.get(metric).set(data.get(metric))

def check_label_metrics(data):
    # Set metrics with labels
    for status in beeper_statuses:
        if status in data.get("ups.beeper.status"):
            ups_beeper_status.labels(status).set(1)
        else:
            ups_beeper_status.labels(status).set(0)
    for status in statuses:
        if status in data.get("ups.status"):
            ups_status.labels(status).set(1)
        else:
            ups_status.labels(status).set(0)


# Create dict of UPS variables with Prometheus Gauges
def get_metrics(ups_name, ups_host, ups_port):
    client = PyNUTClient(ups_host, ups_port)
    client_vars = client.list_vars(ups_name)
    metrics = {}
    for var in client_vars:
        try:
            float(client_vars.get(var))
            desc = client.var_description(ups_name, var)
            var_split = var.split(".")
            if var_split[0] != "ups":
                var_split.insert(0, "ups")
            name = "_".join(var_split)
            metrics.update({var: Gauge(name, desc)})
        except Exception as e:
            logger.debug(f"Exception: {e}!")
    return metrics


if __name__ == "__main__":
    # Set up logging
    logger = logging.getLogger("exporter")
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    logger.setLevel(log_level)
    stream_handler = logging.StreamHandler()
    formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s")
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)
    logger.propagate = False

    # Read environment variables
    logger.info("Reading configuration from environment...")
    ups_name = os.getenv("UPS_NAME", "ups")
    ups_host = os.getenv("UPS_HOST", "localhost")
    ups_port = os.getenv("UPS_PORT", "3493")
    poll_rate = int(os.getenv("POLL_RATE", "5"))
    lookup_rate = int(os.getenv("LOOKUP_RATE", "100"))

    # Print configuration info
    ups_fullname = f"{ups_name}@{ups_host}:{ups_port}"
    ups_ip = socket.gethostbyname(ups_host)
    logger.info(f"UPS to be checked: {ups_fullname}")
    logger.info(f"UPS IP Address: {ups_ip}")
    logger.info(f"Poll Rate: Every {poll_rate} seconds")
    logger.info(f"DNS Lookup Rate: Every {lookup_rate} seconds")

    # Get list of available metrics
    logger.info("Determining list of available metrics...")
    basic_metrics = get_metrics(ups_name, ups_ip, ups_port)
    metrics_count = len(basic_metrics.keys())
    logger.info(f"{metrics_count} metrics available to be exported")

    # Start up the server to expose the metrics.
    logger.info("Starting metrics server...")
    start_http_server(9120)
    logger.info("Metrics server started")

    # Allow loop to be killed gracefully
    killer = GracefulKiller()

    # Check UPS metrics
    for loop_counter in itertools.count():
        if killer.kill_now:
            logger.debug("Recieved SIGINT or SIGTERM")
            break
        try:
            if loop_counter % lookup_rate == 0:
                logger.debug("Resolving UPS IP Address...")
                ups_ip = socket.gethostbyname(ups_host)
                logger.debug(f"UPS IP Address is {ups_ip}")
            if loop_counter % poll_rate == 0:
                data = PyNUTClient(ups_ip, ups_port).list_vars(ups_name)
                check_metrics(data, basic_metrics)
                check_label_metrics(data)
                logger.debug(f"Checked {ups_fullname}")
        except Exception as e:
            logger.error(f"Failed to connect to {ups_fullname}!")
            logger.debug(f"Exception: {e}!")
            clear_metrics(basic_metrics)
            clear_label_metrics()
            logger.debug("Reset metrics to 0 because UPS was unreachable")
        time.sleep(1)

    logger.info("Shutting down...")
