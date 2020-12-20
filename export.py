from prometheus_client import start_http_server, Gauge, Enum
import os
import subprocess
import time
import signal
import logging


class GracefulKiller:
    kill_now = False

    def __init__(self):
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self, signum, frame):
        self.kill_now = True


statuses = ["OL", "OB", "LB", "RB", "CHRG", "DISCHRG", "ALARM", "OVER", "TRIM", "BOOST", "BYPASS", "OFF", "CAL", "TEST", "FSD"]
beeper_statuses = ["enabled", "disabled", "muted"]

# Create metrics
basic_metrics = {
    "battery.charge" : Gauge("ups_battery_charge", "Current Battery Charge"),
    "battery.charge.low" : Gauge("ups_battery_charge_low", "Battery Charge that indicates Low Battery"),
    "battery.charge.warning" : Gauge("ups_battery_charge_warning", "Battery Charge Warning Threshold"),
    "battery.runtime" : Gauge("ups_battery_runtime", "Battery Runtime"),
    "battery.runtime.low" : Gauge("ups_battery_runtime_low", "Battery Runtime that indicates Low Battery"),
    "battery.voltage" : Gauge("ups_battery_voltage", "Battery Voltage"),
    "battery.voltage.nominal" : Gauge("ups_battery_voltage_nominal", "Nominal Battery Voltage"),
    "input.voltage" : Gauge("ups_input_voltage", "Input Voltage"),
    "input.voltage.nominal" : Gauge("ups_input_voltage_nominal", "Nominal Input Voltage"),
    "output.voltage" : Gauge("ups_output_voltage", "Output Voltage"),
    "ups.delay.shutdown" : Gauge("ups_delay_shutdown", "Shutdown Delay"),
    "ups.delay.start" : Gauge("ups_delay_start", "Start Delay"),
    "ups.load" : Gauge("ups_load", "Load Percentage"),
    "ups.realpower.nominal" : Gauge("ups_realpower_nominal", "Nominal Real Power"),
    "ups.timer.shutdown" : Gauge("ups_timer_shutdown", "Shutdown Timer"),
    "ups.timer.start" : Gauge("ups_timer_start", "Start Timer"),
}

# Labeled metrics
ups_beeper_status = Gauge("ups_beeper_status", "Beeper Status", ["status"])
ups_status = Gauge("ups_status", "UPS Status Code", ["status"])


def check_stats(ups_name, ups_host, ups_port):
    # Read and clean data from UPS using upsc
    command = ["/bin/upsc", f"{ups_name}@{ups_host}:{ups_port}"]
    data = subprocess.run(command, capture_output=True).stdout.decode("utf-8").split("\n")
    clean_data = {}
    for entry in data:
        split = entry.split(": ")
        if split != [""]:
            clean_data[split[0]] = split[1]

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
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    logging.basicConfig(level=log_level, format="[%(asctime)s] [%(levelname)s] %(message)s")

    # Start up the server to expose the metrics.
    start_http_server(9120)
    logging.info("Metrics server started")
    ups_name = os.getenv("UPS_NAME", "ups")
    ups_host = os.getenv("UPS_HOST", "localhost")
    ups_port = os.getenv("UPS_PORT", "3493")
    ups_fullname = f"{ups_name}@{ups_host}:{ups_port}"
    poll_rate = int(os.getenv("POLL_RATE", "5"))
    logging.info(f"UPS to be checked: {ups_fullname}")

    # Allow loop to be killed gracefully
    killer = GracefulKiller()

    # Check UPS stats
    while not killer.kill_now:
        try:
            check_stats(ups_name, ups_host, ups_port)
            logging.debug(f"Checked {ups_fullname}")
        except Exception as e:
            logging.error(f"Failed to connect to {ups_fullname}!")
            logging.error(f"Exception: {e}!")
        time.sleep(poll_rate)

    logging.info("Shutting down...")
