# nut-exporter (Deprecated)

**nut-exporter** is a Prometheus exporter for Network UPS Tools (NUT) written in Python. This project is now deprecated and no longer maintained.

## Deprecation Notice

This Python-based exporter has been superseded by a new, more efficient version written in Rust. As this project is deprecated, it will no longer receive updates or support. I recommend transitioning to the Rust-based exporter for improved performance, reliability, and ongoing maintenance.

You can find the new Rust-based exporter here:

[https://github.com/barrelmaker97/pistachio](https://github.com/barrelmaker97/pistachio)

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

Copyright (c) 2024 Nolan Cooper

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
