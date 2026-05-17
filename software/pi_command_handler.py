import zmq
import RPi.GPIO as GPIO
from read_sensor import *

GPIO.setmode(GPIO.BCM)

# VHF ------------------------------------------
pin_switch_vhf = 18
pin_lna_vhf = 4
pin_pa_vhf = 17
#-----------------------------------------------

# UHF 400  MHz ---------------------------------
pin_switch_uhf_400 = 27
pin_lna_uhf_400 = 22
pin_pa_uhf_400 = 23
#-----------------------------------------------

# UHF 468 --------------------------------------
pin_lna_uhf_468 = 24
#-----------------------------------------------

# S Band ---------------------------------------
pin_lna_s_band = 25
#-----------------------------------------------

context = zmq.Context()
socket = context.socket(zmq.REP)


def toggle_vhf(state):
    if state == "rx":
        GPIO.output(pin_pa_vhf, GPIO.LOW) # Turn off PA
        GPIO.output(pin_switch_vhf, GPIO.HIGH) # Flip switch
        GPIO.output(pin_lna_vhf, GPIO.HIGH) # Turn on LNA
    elif state == "tx":
        GPIO.output(pin_lna_vhf, GPIO.LOW)
        GPIO.output(pin_switch_vhf, GPIO.LOW)
        GPIO.output(pin_pa_vhf, GPIO.HIGH)
    else:
        GPIO.output(pin_lna_vhf, GPIO.LOW)
        GPIO.output(pin_pa_vhf, GPIO.LOW)

def toggle_uhf_400(state):
    if state == "rx":
        GPIO.output(pin_pa_uhf_400, GPIO.LOW)
        GPIO.output(pin_switch_uhf_400, GPIO.HIGH)
        GPIO.output(pin_lna_uhf_400, GPIO.HIGH)
    elif state == "tx":
        GPIO.output(pin_lna_uhf_400, GPIO.LOW)
        GPIO.output(pin_switch_uhf_400, GPIO.LOW)
        GPIO.output(pin_pa_uhf_400, GPIO.HIGH)
    else:
        GPIO.output(pin_lna_uhf_400, GPIO.LOW)
        GPIO.output(pin_pa_uhf_400, GPIO.LOW)

def toggle_uhf_468(state):
    if state == "rx":
        GPIO.output(pin_lna_uhf_468, GPIO.HIGH)
    else:
        GPIO.output(pin_lna_uhf_468, GPIO.LOW)

def toggle_s_band(state):
    if state == "rx":
        GPIO.output(pin_lna_s_band, GPIO.HIGH)
    else:
        GPIO.output(pin_lna_s_band, GPIO.LOW)

def get_telemetry():
    return read_sensors()

def interpret_command():
    """
    Receives the JSON file from the lab Server, interprets the dictionary
    and toggles the GPIO pins associated with the required hardware.
    """
    with socket.bind("tcp://0.0.0.0:5555"):
        try:
            while True:
                rcv_json = socket.recv_json()
                
                if not rcv_json:
                    return 1
                
                status = rcv_json.get('status', {})
                
                # Toggle the GPIO pins
                if "vhf" in status:
                    toggle_vhf(status['vhf'])
                    
                if "uhf_400"in status:
                    toggle_uhf_400(status['uhf_400'])
                    
                if "uhf_468" in status:
                    toggle_uhf_468(status["uhf_468"])
                    
                if "s_band" in status:
                    toggle_s_band(status["s_band"])
                
                response_data = {}

                # Telemetry
                if rcv_json.get('request_telemetry') == "true":
                    response_data["telemetry"] = get_telemetry()
                    
                socket.send_json(response_data)
        except KeyboardInterrupt:
            pass
        
if __name__ == "__main__":
    interpret_command()
