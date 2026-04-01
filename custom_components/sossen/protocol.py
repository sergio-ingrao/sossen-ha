"""SOSSEN proprietary protocol encoder/decoder."""

import base64

from .const import (
    DP_AC_FREQUENCY,
    DP_AC_POWER,
    DP_AC_VOLTAGE,
    DP_DC_CURRENT_1,
    DP_DC_CURRENT_2,
    DP_DC_POWER_1,
    DP_DC_POWER_2,
    DP_DC_POWER_TOTAL,
    DP_DC_VOLTAGE_1,
    DP_DC_VOLTAGE_2,
    DP_ENERGY_TOTAL,
    DP_SET_FLAG,
    DP_SET_POWER_LIMIT,
    DP_STATUS,
    DP_TEMPERATURE,
    DP_WIFI_SIGNAL,
)


def decode_records(payload_b64: str) -> dict:
    """Decode a Base64 payload into raw DP records (id -> value)."""
    try:
        data = base64.b64decode(payload_b64)
    except Exception:
        return {}

    records = {}
    i = 2
    while i + 6 <= len(data):
        if data[i] == 0x01 and data[i + 1] == 0x01:
            dp_id = (data[i + 2] << 8) | data[i + 3]
            value = (data[i + 4] << 8) | data[i + 5]
            records[dp_id] = value
            i += 6
        else:
            i += 1
    return records


def decode_payload(payload_b64: str) -> dict | None:
    """Decode a SOSSEN proprietary Base64 payload into sensor values.

    Payload format:
    - Header: 2 bytes (0x03 0x01)
    - Records: 6 bytes each (0x01 0x01 DPH DPL VH VL)
    """
    records = decode_records(payload_b64)

    if not records or DP_AC_VOLTAGE not in records:
        return None

    result = {
        "status": records.get(DP_STATUS, 0),
        "dc_power_total_w": round(records.get(DP_DC_POWER_TOTAL, 0) * 1.0, 1),
        "ac_power_w": round(records.get(DP_AC_POWER, 0) * 1.0, 1),
        "ac_voltage_v": round(records.get(DP_AC_VOLTAGE, 0) * 0.1, 1),
        "ac_frequency_hz": round(records.get(DP_AC_FREQUENCY, 0) * 0.01, 2),
        "dc_voltage_1_v": round(records.get(DP_DC_VOLTAGE_1, 0) * 0.1, 1),
        "dc_current_1_a": round(records.get(DP_DC_CURRENT_1, 0) * 0.03125, 2),
        "dc_power_1_w": round(records.get(DP_DC_POWER_1, 0) * 0.33, 1),
        "dc_voltage_2_v": round(records.get(DP_DC_VOLTAGE_2, 0) * 0.1, 1),
        "dc_current_2_a": round(records.get(DP_DC_CURRENT_2, 0) * 0.03125, 2),
        "dc_power_2_w": round(records.get(DP_DC_POWER_2, 0) * 0.33, 1),
        "energy_total_kwh": round(records.get(DP_ENERGY_TOTAL, 0) * 0.1, 1),
        "temperature_c": round(records.get(DP_TEMPERATURE, 0) * 0.1, 1),
        "wifi_signal": records.get(DP_WIFI_SIGNAL, 0),
    }

    # Include all raw DP values for debugging
    result["_raw"] = {str(k): v for k, v in sorted(records.items())}

    return result


def build_set_power_payload(watts: int) -> str:
    """Build a Base64 payload to set the inverter power limit.

    Uses Tuya DP 24 with proprietary records:
    - DP 32770 (0x8002) = 0 (flag)
    - DP 32771 (0x8003) = watts
    """
    vh = (watts >> 8) & 0xFF
    vl = watts & 0xFF
    payload = bytes(
        [
            0x03, 0x01,
            0x01, 0x01, (DP_SET_FLAG >> 8) & 0xFF, DP_SET_FLAG & 0xFF, 0x00, 0x00,
            0x01, 0x01, (DP_SET_POWER_LIMIT >> 8) & 0xFF, DP_SET_POWER_LIMIT & 0xFF, vh, vl,
        ]
    )
    return base64.b64encode(payload).decode()
