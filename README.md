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

# License

Copyright (c) 2021 Nolan Cooper

This exporter is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This exporter is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this exporter.  If not, see <https://www.gnu.org/licenses/>.
