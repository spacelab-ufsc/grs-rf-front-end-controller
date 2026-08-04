# RF Front-End Controller

Controls the ground station's RF front-end controller (VHF/UHF/S-band LNAs and PAs) and reports telemetry from it, via a small client/server pair communicating over ZeroMQ.

## Architecture
- **`command_dispatcher.py`** runs on the lab server and sends control commands to the Pi.
- **`pi_command_handler.py`** runs on the Raspberry Pi attached to the RF front-end. It receives commands, toggles the appropriate GPIO pins, and optionally reads back telemetry.
- **`read_sensor.py`** runs on the Pi and reads power/current/voltage/temperature from six INA238 sensors (one per LNA/PA on each band) over I2C.

## Message protocol

Requests (dispatcher → Pi) and replies (Pi → dispatcher) are JSON, sent via `zmq`'s `send_json`/`recv_json`.

**Request:**

```json
{
  "status": {
    "vhf": "rx",
    "uhf_400": "tx",
    "uhf_468": "rx",
    "s_band": "off"
  },
  "request_telemetry": "true"
}
```

- Each band's value is one of `"rx"`, `"tx"`, or any other value (treated as "off" when both LNA and PA are disabled). `uhf_468` and `s_band` only support `"rx"` / off, since they have no PA/switch pins.
- A band key can be omitted from `status` to leave that band's pins untouched.

**Reply:**

```json
{
  "telemetry": {
    "vhf":     { "LNA": { "power": 0.12, "current": 0.045, "voltage": 5.01, "temperature": 27.3 },
                 "PA":  { "power": 1.8,  "current": 0.6,   "voltage": 5.02, "temperature": 31.1 } },
    "uhf_400": { "LNA": {...}, "PA": {...} },
    "uhf_468": { "LNA": {...} },
    "s_band":  { "LNA": {...} }
  }
}
```

`telemetry` is only present in the reply if `request_telemetry` was `True`. Units: power in watts, current in amps, voltage in volts, temperature in °C, each rounded (power/current/voltage to 3 decimals, temperature to 2).

## Module reference

### `read_sensor.py` (runs on the Pi)

Reads all six front-end power monitors (Adafruit INA23x driver, I2C) and returns a nested telemetry dict.

| Band | Amplifier | I2C address |
|---|---|---|
| VHF | LNA | `0x41` |
| VHF | PA | `0x40` |
| UHF 400 MHz | LNA | `0x43` |
| UHF 400 MHz | PA | `0x42` |
| UHF 468 MHz | LNA | `0x44` |
| S-band | LNA | `0x45` |

- `read_sensor_object(sensor_object) -> dict` — reads `current`, `bus_voltage`, `power`, `die_temperature` off one sensor and returns them as a rounded `{power, current, voltage, temperature}` dict.
- `return_telemetry() -> dict` — reads all six sensors and assembles the nested `{band: {amp: readings}}` structure shown in the module docstring and the reply schema above.

Requires the [Adafruit CircuitPython INA23x](https://github.com/adafruit/Adafruit_CircuitPython_INA23x) library.

### `pi_command_handler.py` (runs on the Pi)

ZMQ `REP` server bound to `tcp://0.0.0.0:5555`. For each request received:

1. Toggles GPIO pins for any band present in `status` via `toggle_vhf`/`toggle_uhf_400`/`toggle_uhf_468`/`toggle_s_band`.
2. If `request_telemetry == "true"`, calls `return_telemetry()` and includes it in the reply.
3. Sends the JSON reply.

| Band | Switch pin (BCM) | LNA pin (BCM) | PA pin (BCM) |
|---|---|---|---|
| VHF | 18 | 4 | 17 |
| UHF 400 MHz | 27 | 22 | 23 |
| UHF 468 MHz | — | 24 | — |
| S-band | — | 25 | — |

- `toggle_vhf` / `toggle_uhf_400` (`state: str`) — for `"rx"`: PA off, switch to RX, LNA on. For `"tx"`: LNA off, switch to TX, PA on. Any other value: both LNA and PA off.
- `toggle_uhf_468` / `toggle_s_band` (`state: str`) — `"rx"` turns the LNA on, anything else turns it off (no switch/PA on these bands).
- `interpret_command()` — the main server loop. Runs until `KeyboardInterrupt`, or returns `1` if an empty/falsy JSON message is received.

### `command_dispatcher.py` (runs on the lab server)

ZMQ `REQ` client. `send_command_to_controller(vhf, uhf_400, uhf_468, s_band, request_telemetry)` builds the request JSON shown above, sends it, and passes the reply to `store_response()`.

`store_response()` is currently a stub (`pass`) — see **Known issues**.

## Known issues

- **`PI_IP_ADDRESS` is a placeholder.**
- **`store_response()` is currently unimplemented.**
