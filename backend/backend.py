"""
backend.py
Auteurs : Daniel Oliveira et Edin Mujkanovic
Description : backend permettant de gérer les évenements dans les pièces. Il est basé sur un script disponible dans le tutoriel Microsoft Azure.
"""

import asyncio
from azure.eventhub import TransportType
from azure.eventhub.aio import EventHubConsumerClient
from azure.iot.hub import IoTHubRegistryManager
from azure.iot.hub.models import CloudToDeviceMethod, CloudToDeviceMethodResult
import json
import time
import datetime as dt

# Event Hub-compatible endpoint
# az iot hub show --query properties.eventHubEndpoints.events.endpoint --name {your IoT Hub name}
EVENTHUB_COMPATIBLE_ENDPOINT = "sb://iothub-ns-iot-hub-da-6187715-646edab406.servicebus.windows.net/"

# Event Hub-compatible name
# az iot hub show --query properties.eventHubEndpoints.events.path --name {your IoT Hub name}
EVENTHUB_COMPATIBLE_PATH = "iot-hub-daniel"

# Primary key for the "service" policy to read messages
# az iot hub policy show --name service --query primaryKey --hub-name {your IoT Hub name}
IOTHUB_SAS_KEY = "F1vOY2cq5GX25rtOxK10VH8UpBYCKwydmFWAi3AQsS8="

# If you have access to the Event Hub-compatible connection string from the Azure portal, then
# you can skip the Azure CLI commands above, and assign the connection string directly here.
CONNECTION_STR = f'Endpoint={EVENTHUB_COMPATIBLE_ENDPOINT}/;SharedAccessKeyName=service;SharedAccessKey={IOTHUB_SAS_KEY};EntityPath={EVENTHUB_COMPATIBLE_PATH}'

CONNECTION_STRING = "HostName=IoT-Hub-Daniel.azure-devices.net;SharedAccessKeyName=service;SharedAccessKey=F1vOY2cq5GX25rtOxK10VH8UpBYCKwydmFWAi3AQsS8="
DEVICE_ID = "MyPythonDevice"
ANDROID_ID = "MyAndroidDevice"

HIGH_HUMIDITY = 40
LOW_LUMINANCE = 10

rooms = {}

# Define callbacks to process events
async def on_event_batch(partition_context, events):
    for event in events:
        print("Received event from partition: {}.".format(partition_context.partition_id))
        print("Telemetry received: ", event.body_as_str())
        print("Properties (set by device): ", event.properties)
        print("System properties (set by IoT Hub): ", event.system_properties)
        parse_message(event.body_as_str(), event.system_properties[b"iothub-connection-device-id"])
        print()
    await partition_context.update_checkpoint()

async def on_error(partition_context, error):
    # Put your code here. partition_context can be None in the on_error callback.
    if partition_context:
        print("An exception: {} occurred during receiving from Partition: {}.".format(
            partition_context.partition_id,
            error
        ))
    else:
        print("An exception: {} occurred during the load balance process.".format(error))


'''
Methode permettant de parser le message reçu depuis IoT Hub
'''
def parse_message(message, device_id):
    global rooms
    message = json.loads(message)
    device_id = device_id.decode("UTF-8")
    if device_id == DEVICE_ID :
        humidity = message["value"]["humidity"]
        luminance = message["value"]["luminance"]
        room = message["location"]
        now = dt.datetime.now()

        # Si l'humidité est trop haute, fermer les stores
        if humidity > HIGH_HUMIDITY:
            call_method("CloseBlinds", room)
        
        # Si la pièce est coccupé + journée + lumière basse, ouvrir les stores
        elif rooms.get(room) != None and rooms[room]["person"] >= 1 \
            and luminance < LOW_LUMINANCE and now.hour >= 8 and now.hour < 20:
            call_method("OpenBlinds", room)

    else :
        update_room(message)

'''
Methode permettant de mettre à jour les valeurs des radiateurs et des stores de la chambre
'''
def update_room(message):
    global rooms
    room_name = message["room"]
    previous_room = message["previousRoom"]
    if room_name != "":
        if not room_name in rooms:
            rooms[message["room"]] = {"person":0, "time": time.time()}
        
        rooms[room_name]["person"] += 1
        rooms[room_name]["time"] = time.time()
        # si la pièce était vide, augmenter la température
        if rooms[room_name]["person"] == 1:
            call_method("IncreaseTemp", room_name)

        print("TEST")

    if previous_room != "":
        rooms[previous_room]["person"] -= 1
        rooms[previous_room]["time"] = time.time()

        # si la pièce est vide, baisser la température
        if rooms[previous_room]["person"] == 0:
            call_method("DecreaseTemp", previous_room)
    
    print(rooms)


def call_method(method_name, param):
    # Create IoTHubRegistryManager
    registry_manager = IoTHubRegistryManager(CONNECTION_STRING)

    # Call the direct method.
    deviceMethod = CloudToDeviceMethod(method_name=method_name, payload=param)
    response = registry_manager.invoke_device_method(DEVICE_ID, deviceMethod)

def main():
    loop = asyncio.get_event_loop()
    client = EventHubConsumerClient.from_connection_string(
        conn_str=CONNECTION_STR,
        consumer_group="$default",
    )
    try:
        loop.run_until_complete(client.receive_batch(on_event_batch=on_event_batch, on_error=on_error))
    except KeyboardInterrupt:
        print("Receiving has stopped.")
    finally:
        loop.run_until_complete(client.close())
        loop.stop()
    

if __name__ == '__main__':
    main()
