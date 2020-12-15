[![CodeFactor](https://www.codefactor.io/repository/github/barrelmaker97/nut-exporter/badge)](https://www.codefactor.io/repository/github/barrelmaker97/nut-exporter)
# nut-exporter
Prometheus Exporter for Network UPS Tools

## Configuration
All config is done via environment variables, listed below:

* `UPS_NAME`: _Optional_. Name of the UPS to monitor (*Default:* `ups`)
* `UPS_HOST` _Optional_. Hostname of the NUT server to monitor. (*Default:* `localhost`)
* `UPS_PORT` _Optional_. Port of the NUT server to monitor. (*Default:* `3493`)
* `LOG_LEVEL`: _Optional_. Logging level of the exporter. (*Options:* `debug`, `info`, `warning`, `error`, `critical`) (*Default:* `info`)
* `POLL_RATE` _Optional_. Amount of time, in seconds, this exporter will wait between requests to the NUT server for data. (*Default:* `5`)
