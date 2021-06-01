from server import *
from coapthon.server.coap import CoAP
import threading
from mqtt_collector import MqttClient
import database
import logging

# Unspecified IPv6 address
ip = "::"
port = 5683


class CoAPServer(CoAP):
    def __init__(self, host, port):
        CoAP.__init__(self, (host, port), False)
        # Register resource: server behave as client in order to get the registration
        self.add_resource("registration", AdvancedResource())

def main():
    logging.getLogger("coapthon.server.coap").setLevel(logging.WARNING)
    logging.getLogger("coapthon.layers.messagelayer").setLevel(logging.WARNING)
    logging.getLogger("coapthon.client.coap").setLevel(logging.WARNING)
    # Add some random users
    registeredUsersDict["mat"] = "mat"
    registeredUsersDict["nick"] = "nick"
    registeredUsersDict["marc"] = "marc"
    registeredUsersDict["carl"] = "carl"

    print("Initializing server and MQTT client thread")
    mqttcl = MqttClient()
    # Before Initializing server, start a thread dedicated for the MQTT clients
    mqtt_thread = threading.Thread(target=mqttcl.mqtt_client,args=(),kwargs={})
    # mqtt_thread.daemon = True
    mqtt_thread.start()
    # Start server on the main thread
    server = CoAPServer(ip, port)
    try:
        server.listen(100)
    except KeyboardInterrupt:
        print("Server Shutdown")
        # mqtt_thread.kill()
        mqtt_thread.join()
        server.close()
        print("Exiting...")

if __name__ == '__main__':
    main()
