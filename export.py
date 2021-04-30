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

basic_metrics = {}

# Labeled metrics
ups_beeper_status = Gauge("ups_beeper_status", "Beeper Status", ["status"])
ups_status = Gauge("ups_status", "UPS Status Code", ["status"])


# Resets all stats to 0
def clear_stats():
    # Clear basic metrics
    for metric in basic_metrics:
        basic_metrics.get(metric).set(0)

    # Clear metrics with labels
    for status in beeper_statuses:
        ups_beeper_status.labels(status).set(0)
    for status in statuses:
        ups_status.labels(status).set(0)


# Read and clean data from UPS using upsc
def check_stats(ups_name, ups_host, ups_port):
    clean_data = PyNUTClient(host=ups_host, port=ups_port).list_vars(ups_name)

    # Set basic metrics
    for metric in basic_metrics:
        basic_metrics.get(metric).set(clean_data.get(metric))

    # Set metrics with labels
    for status in beeper_statuses:
        if status in clean_data.get("ups.beeper.status"):
            ups_beeper_status.labels(status).set(1)
        else:
            ups_beeper_status.labels(status).set(0)
    for status in statuses:
        if status in clean_data.get("ups.status"):
            ups_status.labels(status).set(1)
        else:
            ups_status.labels(status).set(0)


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

    ups_fullname = f"{ups_name}@{ups_host}:{ups_port}"
    ups_ip = socket.gethostbyname(ups_host)
    logger.info(f"UPS to be checked: {ups_fullname}")
    logger.info(f"UPS IP Address: {ups_ip}")
    logger.info(f"Poll Rate: Every {poll_rate} seconds")
    logger.info(f"DNS Lookup Rate: Every {lookup_rate} seconds")

    # Start up the server to expose the metrics.
    logger.info("Starting metrics server...")
    start_http_server(9120)
    logger.info("Metrics server started")

    # Allow loop to be killed gracefully
    killer = GracefulKiller()

    # Get list of available stats
    client = PyNUTClient(host=ups_host, port=ups_port)
    client_vars = client.list_vars(ups_name)
    for var in client_vars:
        desc = client.var_description(ups_name, var)
        var_split = var.split(".")
        if var_split[0] != "ups":
            var_split.insert(0, "ups")
        name = "_".join(var_split)
        try:
            float(client_vars.get(var))
            metric = {var: Gauge(name, desc)}
            basic_metrics.update(metric)
        except Exception as e:
            logger.debug(f"Exception: {e}!")

    # Check UPS stats
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
                check_stats(ups_name, ups_ip, ups_port)
                logger.debug(f"Checked {ups_fullname}")
        except Exception as e:
            logger.error(f"Failed to connect to {ups_fullname}!")
            logger.debug(f"Exception: {e}!")
            clear_stats()
            logger.debug("Reset stats to 0 because UPS was unreachable")
        time.sleep(1)

    logger.info("Shutting down...")
