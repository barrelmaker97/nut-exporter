[![CodeFactor](https://www.codefactor.io/repository/github/barrelmaker97/nut-exporter/badge)](https://www.codefactor.io/repository/github/barrelmaker97/nut-exporter)
# nut-exporter
Prometheus Exporter for Network UPS Tools

## Configuration
All config is done via environment variables, listed below:
| Parameter     | Description                                                                                      | Default     |
|---------------|--------------------------------------------------------------------------------------------------|-------------|
| `UPS_NAME`    | Name of the UPS to monitor                                                                       | `ups`       |
| `UPS_HOST`    | Hostname of the NUT server to monitor                                                            | `localhost` |
| `UPS_PORT`    | Port of the NUT server to monitor                                                                | `3493`      |
| `LOG_LEVEL`   | Logging level of the exporter                                                                    | `info`      |
| `POLL_RATE`   | Amount of time, in seconds, this exporter will wait between requests to the NUT server for data  | `5`         |
| `LOOKUP_RATE` | Amount of time, in seconds, this exporter will wait between looking up the NUT server IP address | `100`       |
