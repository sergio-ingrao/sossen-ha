# SOSSEN Microinverter

Local integration for **SOSSEN 2in1-DE** microinverters (600W / 800W / 1000W).

Direct communication over the local network — no cloud, no delays.

## Features

* **13 sensors** for real-time solar production (power, voltage, current, frequency, temperature, energy)
* **Inverter status** with 3 states: producing, alarm, off
* **Power limit control** (500-1000W) directly from HA
* **Daytime-only mode** to avoid polling at night
* **Diagnostic sensor** with all raw register values
* Updates every **10 seconds** (configurable)
* Compatible with HA **Energy Dashboard**

## Requirements

* The inverter must be on the same local network as Home Assistant
* You will need: Device ID, local IP, and Local Key (obtainable from the [Tuya IoT Platform](https://iot.tuya.com))

## Tested models

* SOSSEN 2in1-DE 600W
* SOSSEN 2in1-DE 800W
* SOSSEN 2in1-DE 1000W
