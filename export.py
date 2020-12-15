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
battery_charge = Gauge("ups_battery_charge", "Current Battery Charge")
battery_charge_low = Gauge("ups_battery_charge_low", "Battery Charge that indicates Low Battery")
battery_charge_warning = Gauge("ups_battery_charge_warning", "Battery Charge Warning Threshold")
battery_runtime = Gauge("ups_battery_runtime", "Battery Runtime")
battery_runtime_low = Gauge("ups_battery_runtime_low", "Battery Runtime that indicates Low Battery")
battery_voltage = Gauge("ups_battery_voltage", "Battery Voltage")
battery_voltage_nominal = Gauge("ups_battery_voltage_nominal", "Nominal Battery Voltage")
input_voltage = Gauge("ups_input_voltage", "Input Voltage")
input_voltage_nominal = Gauge("ups_input_voltage_nominal", "Nominal Input Voltage")
output_voltage = Gauge("ups_output_voltage", "Output Voltage")
ups_beeper_status = Enum("ups_beeper_status", "Beeper Status", states=beeper_statuses)
ups_delay_shutdown = Gauge("ups_delay_shutdown", "Shutdown Delay")
ups_delay_start = Gauge("ups_delay_start", "Start Delay")
ups_load = Gauge("ups_load", "Load Percentage")
ups_realpower_nominal = Gauge("ups_realpower_nominal", "Nominal Real Power")
ups_status = Gauge("ups_status", "UPS Status Code", ["status"])
ups_timer_shutdown = Gauge("ups_timer_shutdown", "Shutdown Timer")
ups_timer_start = Gauge("ups_timer_start", "Start Timer")


def check_stats(ups_name, ups_host, ups_port, poll_rate):
    command = ["/bin/upsc", f"{ups_name}@{ups_host}:{ups_port}"]
    data = subprocess.run(command, capture_output=True).stdout.decode("utf-8").split("\n")
    clean_data = {}
    for entry in data:
        split = entry.split(": ")
        if split != [""]:
            clean_data[split[0]] = split[1]
    battery_charge.set(clean_data.get("battery.charge"))
    battery_charge_low.set(clean_data.get("battery.charge.low"))
    battery_charge_warning.set(clean_data.get("battery.charge.warning"))
    battery_runtime.set(clean_data.get("battery.runtime"))
    battery_runtime_low.set(clean_data.get("battery.runtime.low"))
    battery_voltage.set(clean_data.get("battery.voltage"))
    battery_voltage_nominal.set(clean_data.get("battery.voltage.nominal"))
    input_voltage.set(clean_data.get("input.voltage"))
    input_voltage_nominal.set(clean_data.get("input.voltage.nominal"))
    output_voltage.set(clean_data.get("output.voltage"))
    ups_beeper_status.state(clean_data.get("ups.beeper.status"))
    ups_delay_shutdown.set(clean_data.get("ups.delay.shutdown"))
    ups_delay_start.set(clean_data.get("ups.delay.start"))
    ups_load.set(clean_data.get("ups.load"))
    ups_realpower_nominal.set(clean_data.get("ups.realpower.nominal"))
    for status in statuses:
        if status in clean_data.get("ups.status"):
            ups_status.labels(status).set(1)
        else:
            ups_status.labels(status).set(0)
    ups_timer_shutdown.set(clean_data.get("ups.timer.shutdown"))
    ups_timer_start.set(clean_data.get("ups.timer.start"))
    time.sleep(poll_rate)


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
            check_stats(ups_name, ups_host, ups_port, poll_rate)
            logging.debug(f"Checked {ups_fullname}")
        except Exception as e:
            logging.error(f"Failed to connect to {ups_fullname}!")
            logging.error(f"Exception: {e}!")

    logging.info("Shutting down...")
