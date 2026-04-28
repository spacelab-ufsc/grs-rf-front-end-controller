#{
#  "status": {
#    "vhf": "rx",         // Options: "rx", "tx", "off"
#    "uhf_400": "tx",     // Options: "rx", "tx", "off"
#    "uhf_468": "rx",     // Options: "rx", "off"
#    "s_band": "off"      // Options: "rx", "off"
#  },
#  "request_telemetry": true // Options: true, false
#}

import requests
import json

# Get raspberryPi hostname
pi_hostname = 1
PI_IP_ADDRESS = pi_hostname

def send_command_to_controller(vhf, uhf_400, uhf_468, s_band, request_telemetry):
    """
    Builds the JSON command and sends it to the Raspberry Pi.
    """
    json_command = {
        "status": {
            "vhf": vhf,
            "uhf_400": uhf_400,
            "uhf_468": uhf_468,
            "s_band": s_band 
        },
        "request_telemetry": request_telemetry
    }

    try:
        response = requests.post(PI_IP_ADDRESS, json=json_command, timeout=3)
        
        if response.status_code == 200: #Success
            print("Command successfully received by the Pi!")
            return response.json() # Raspberry Pi response
        else:
            print(f"Error: Response code {response.status_code}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"Network Error: Could not find the Raspberry Pi. {e}")
        return None
    
def store_response(response):
    pass

if __name__ == "__main__":
    while True:
        reply = send_command_to_controller(vhf="tx", uhf_400="rx", uhf_468="off", s_band="rx", request_telemetry=True)
    
        if reply:
            store_response(reply)
            