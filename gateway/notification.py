# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

import random
import time
import threading
import requests
import os

# Using the Python Device SDK for IoT Hub:
#   https://github.com/Azure/azure-iot-sdk-python
# The sample connects to a device-specific MQTT endpoint on your IoT Hub.
from azure.iot.device import IoTHubDeviceClient, Message, MethodResponse

# The device connection string to authenticate the device with your IoT hub.
# Using the Azure CLI:
# az iot hub device-identity show-connection-string --hub-name {YourIoTHubName} --device-id MyNodeDevice --output table
CONNECTION_STRING = "HostName=IoT-Hub-Daniel.azure-devices.net;DeviceId=MyPythonDevice;SharedAccessKey=tQ6bIeClkXSWvaBz8FYQ9EyzVEgBvmpFp9VBdlou1VI="

# Define the JSON message to send to IoT Hub.
MSG_TXT = '{{"sensor_name":"{sensor_name}", "location":"{location}", "value":{{"temperature": {temperature},"humidity": {humidity}, "luminance":{luminance} }} }}'


knx_gateway = None
_rooms_devices = {
    "31126" : {
        "radiators" : 
            {
                "4/1",
                "4/2"
            },
        "blinds" :
            {
                "4/1",
                "4/2"
            }

    },
    "19547" : {
        "radiators" : 
            {
                "4/10",
                "4/11"
            },
        "blinds" :
            {
                "4/10",
                "4/11"
            }

    }
}

def iothub_client_init():
    # Create an IoT Hub client
    client = IoTHubDeviceClient.create_from_connection_string(CONNECTION_STRING)
    return client

def device_method_listener(device_client):
    while True:
        method_request = device_client.receive_method_request()
        print (
            "\nMethod callback called with:\nmethodName = {method_name}\npayload = {payload}".format(
                method_name=method_request.name,
                payload=method_request.payload
            )
        )
        if method_request.name == "CloseBlinds":
            try:
                room = method_request.payload
                close_blinds(room)
            except ValueError:
                response_payload = {"Response": "Invalid parameter"}
                response_status = 400
            else:
                response_payload = {"Response": "Executed direct method {}".format(method_request.name)}
                response_status = 200

        elif method_request.name == "OpenBlinds":
            try:
                room = method_request.payload
                open_blinds(room)
            except ValueError:
                response_payload = {"Response": "Invalid parameter"}
                response_status = 400
            else:
                response_payload = {"Response": "Executed direct method {}".format(method_request.name)}
                response_status = 200

        elif method_request.name == "IncreaseTemp":
            try:
                room = method_request.payload
                increase_temp(room)
            except ValueError:
                response_payload = {"Response": "Invalid parameter"}
                response_status = 400
            else:
                response_payload = {"Response": "Executed direct method {}".format(method_request.name)}
                response_status = 200

        elif method_request.name == "DecreaseTemp":
            try:
                room = method_request.payload
                decrease_temp(room)
            except ValueError:
                response_payload = {"Response": "Invalid parameter"}
                response_status = 400
            else:
                response_payload = {"Response": "Executed direct method {}".format(method_request.name)}
                response_status = 200
        
        else:
            response_payload = {"Response": "Direct method {} not defined".format(method_request.name)}
            response_status = 404

        method_response = MethodResponse(method_request.request_id, response_status, payload=response_payload)
        device_client.send_method_response(method_response)

def close_blinds(room):
    global knx_gateway
    print("closing blinds in " + room)
    blinds = _rooms_devices[room]["blinds"]
    for blind in blinds :
        command = "./knx_client.py -i " + knx_gateway + " blind close '" + blind + "' "
        os.system(command)
    return True

def open_blinds(room):
    global knx_gateway
    threshold = 50
    print("Opening blinds in " + room)
    blinds = _rooms_devices[room]["blinds"]
    for blind in blinds :
        command = "./knx_client.py -i " + knx_gateway + " blind set '" + blind + "' " + str(threshold)
        os.system(command)

def increase_temp(room):
    global knx_gateway
    threshold = 50
    print("Increasing temperature in " + room)
    valves = _rooms_devices[room]["radiators"]
    for valve in valves :
        command = "./knx_client.py -i " + knx_gateway + " valve set '" + valve + "' " + str(threshold)
        os.system(command)
    return True

def decrease_temp(room):
    global knx_gateway
    print("Decreasing temperature in " + room)
    valves = _rooms_devices[room]["radiators"]
    for valve in valves :
        command = "./knx_client.py -i " + knx_gateway + " valve set '" + valve + "' " + str(0)
        os.system(command)
    return True

def notify(zwave_server_address, knx_gw):
    global knx_gateway 
    knx_gateway = knx_gw

    try:
        client = iothub_client_init()

        device_method_thread = threading.Thread(target=device_method_listener, args=(client,))
        device_method_thread.daemon = True
        device_method_thread.start()
        
        print ( "IoT Hub device sending periodic messages, press Ctrl-C to exit" )
        

        sensors_url = zwave_server_address + "/network/sensors"
        sensors = requests.get(url = sensors_url)
        sensors = sensors.json()
        print(sensors)

        while True:
            for sensor_key, sensor_name in sensors.items(): 
                # Build the message with simulated telemetry values.
                sensor_reading_url = zwave_server_address + "/sensor/"+sensor_key+"/readings"
                tmp = requests.get(url=sensor_reading_url).json()
                device_type="sensor"
                location = "31126" #tmp["location"]
                temperature = tmp["temperature"]
                humidity = tmp["humidity"]
                luminance = tmp["luminance"]
                msg_txt_formatted = MSG_TXT.format(type=device_type, sensor_name=sensor_name, location=location, temperature=temperature, humidity=humidity, luminance=luminance)
                message = Message(msg_txt_formatted)

                # Add a custom application property to the message.
                # An IoT hub can filter on these properties without access to the message body.
                if temperature > 30:
                    message.custom_properties["temperatureAlert"] = "true"
                else:
                    message.custom_properties["temperatureAlert"] = "false"

                # Send the message.
                print( "Sending message: {}".format(message) )
                client.send_message(message)
                print ( "Message successfully sent" )
            time.sleep(5)

    except KeyboardInterrupt:
        print ( "IoTHubClient sample stopped" )

if __name__ == '__main__':
    print ( "IoT Hub Quickstart #1 - Simulated device" )
    print ( "Press Ctrl-C to exit" )
