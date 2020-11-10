from prometheus_client import start_http_server, Gauge, Enum, Info
import subprocess
import time

# Create metrics
battery_charge = Gauge('ups_battery_charge', 'Current Battery Charge')
battery_charge_low = Gauge('ups_battery_charge_low', 'Battery Charge that indicates Low Battery')
battery_charge_warning = Gauge('ups_battery_charge_warning', 'Battery Charge Warning Threshold')
battery_runtime = Gauge('ups_battery_runtime', 'Battery Runtime')
battery_runtime_low = Gauge('ups_battery_runtime_low', 'Battery Runtime that indicates Low Battery')
battery_voltage = Gauge('ups_battery_voltage', 'Battery Voltage')
battery_voltage_nominal = Gauge('ups_battery_voltage_nominal', 'Nominal Battery Voltage')
input_voltage = Gauge('ups_input_voltage', 'Input Voltage')
input_voltage_nominal = Gauge('ups_input_voltage_nominal', 'Nominal Input Voltage')
output_voltage = Gauge('ups_output_voltage', 'Output Voltage')
ups_beeper_status = Enum("ups_beeper_status", "Beeper Status", states=["enabled", "disabled", "muted"])
ups_delay_shutdown = Gauge('ups_delay_shutdown', 'Shutdown Delay')
ups_delay_start = Gauge('ups_delay_start', 'Start Delay')
ups_load = Gauge('ups_load', 'Load Percentage')
ups_realpower_nominal = Gauge('ups_realpower_nominal', 'Nominal Real Power')
ups_status = Info("ups_status", "Status Code")
ups_timer_shutdown = Gauge('ups_timer_shutdown', 'Shutdown Timer')
ups_timer_start = Gauge('ups_timer_start', 'Start Timer')


def check_stats(t):
    data = subprocess.check_output(['upsc', 'ups']).decode("utf-8").split()
    clean_data = {data[i].strip(":"): data[i + 1] for i in range(0, len(data), 2)}
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
    ups_status.info({"status": clean_data.get("ups.status")})
    ups_timer_shutdown.set(clean_data.get("ups.timer.shutdown"))
    ups_timer_start.set(clean_data.get("ups.timer.start"))
    time.sleep(t)

if __name__ == '__main__':
    # Start up the server to expose the metrics.
    start_http_server(8000)
    # Check UPS stats
    while True:
        check_stats(5)
