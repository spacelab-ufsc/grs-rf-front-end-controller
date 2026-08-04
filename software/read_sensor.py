"""
Format of the returned string:
{
    "vhf" : {
        "LNA" : {
            "power" : power_lna_vhf,
            "current" : current_lna_vhf,
            "voltage" : voltage_lna_vhf,
            "temperature" : temperature_lna_vhf
        },
        "PA"  : {
            "power" : power_pa_vhf,
            "current" : current_pa_vhf,
            "voltage" : voltage_pa_vhf,
            "temperature" : temperature_pa_vhf
        }
        },
    "uhf_400" : {
        "LNA" : {
            "power" : power_lna_uhf400,
            "current" : current_lna_uhf400,
            "voltage" : voltage_lna_uhf400,
            "temperature" : temperature_lna_uhf400
        },
        "PA" : {
            "power" : power_pa_uhf400,
            "current" : current_pa_uhf400,
            "voltage" : voltage_pa_uhf400,
            "temperature" : temperature_pa_uhf400
        }
    },
    "uhf_468" : {
        "LNA" : {
            "power" : power_lna_uhf468,
            "current" : current_lna_uhf468,
            "voltage" : voltage_lna_uhf468,
            "temperature" : temperature_lna_uhf468
        } 
    },
    "s_band" : {
        "LNA" : {
            "power" : power_lna_sband,
            "current" : current_lna_sband,
            "voltage" : voltage_lna_sband,
            "temperature" : temperature_lna_sband
        } 
    }
}"""
# Check the sensor's (INA 238) repository to install dependencies: https://github.com/adafruit/Adafruit_CircuitPython_INA23x

import sys
import board
import adafruit_ina23x

i2c = board.I2C()

sensor_vhf_pa = adafruit_ina23x.INA23X(i2c, address = 0x40)
sensor_vhf_lna = adafruit_ina23x.INA23X(i2c, address = 0x41)
sensor_uhf400_pa = adafruit_ina23x.INA23X(i2c, address = 0x42)
sensor_uhf400_lna =adafruit_ina23x.INA23X(i2c, address = 0x43)
sensor_uhf468_lna = adafruit_ina23x.INA23X(i2c, address = 0x44)
sensor_sband_lna = adafruit_ina23x.INA23X(i2c, address = 0x45)

list_sensors = [sensor_vhf_lna, sensor_vhf_pa, sensor_uhf400_lna, sensor_uhf400_pa, sensor_uhf468_lna, sensor_sband_lna]

def read_sensor_object(sensor_object):
    current = sensor_object.current # Amps
    voltage = sensor_object.bus_voltage # Volts
    power = sensor_object.power # Watts
    temperature = sensor_object.die_temperature # Celsius
    
    current = round(current, 3)
    voltage = round(voltage, 3)
    power = round(power, 3)
    temperature = round(temperature, 2)
    
    readings = {}
    readings["power"] = power
    readings["current"] = current
    readings["voltage"] = voltage
    readings["temperature"] = temperature
    
    return readings

def return_telemetry():
    readings = []
    for sensor in list_sensors:
        try:
            readings.append(read_sensor_object(sensor))
        except Exception as e:
            print(f"Error: {e}")
            readings.append({"power": None, "current": None, "voltage": None, "temperature": None})

    json_readings = {"vhf" : {"LNA" : readings[0], "PA" : readings[1]},
                     "uhf_400" : {"LNA" : readings[2], "PA" : readings[3]},
                     "uhf_468" : {"LNA" : readings[4]},
                     "s_band" : {"LNA" : readings[5]}
                     }

    return json_readings