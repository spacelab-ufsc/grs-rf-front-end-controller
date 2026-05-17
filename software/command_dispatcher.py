import zmq
import json

# Fill in with raspberryPi IP adress
PI_IP_ADDRESS = "1"

context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.connect(PI_IP_ADDRESS)

def send_command_to_controller(vhf, uhf_400, uhf_468, s_band, request_telemetry):
    """
    Builds the JSON command and sends it to the Raspberry Pi.
    """
    status = {
        "status": {
            "vhf": vhf,
            "uhf_400": uhf_400,
            "uhf_468": uhf_468,
            "s_band": s_band 
        },
        "request_telemetry": request_telemetry
    }
    
    socket.send_json(status)
    
    reply = socket.recv_json()
    store_response(reply)
    
def store_response(response):
    pass

            
            