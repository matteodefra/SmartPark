from coapthon.server.coap import CoAP
from coapthon.resources.resource import Resource
from coapthon.client.helperclient import HelperClient
from coapthon.messages.request import Request
from coapthon.messages.response import Response
from coapthon import defines
import json
import time
import server

global client
nodeInfo = {};

def presence_callback_observer(response):
    print("Callback called, resource arrived")
    if response.payload is not None:
        print(response.payload)
        nodeData = json.loads(response.payload)
        credentials = nodeData["ClientInfo"].split(" ")
        print("Client credentials are:")
        print(credentials)
        try:
            password = server.registeredUsersDict[credentials[0]]
            if password == credentials[1]:
                print("User recognized!")
                # Need to check this nodeInfo struct
                lockState = nodeInfo["BoxSituation"]
                if lockState == 'F':
                    request = Request()
                    request.code = defines.Codes.POST.number
                    # request.content_type = defines
                    request.type = defines.Types["CON"]
                    request.destination = nodeInfo["Source"]
                    request.uri_path = "lock"
                    request.uri_query = "?state=1"
                    print(request.uri_query)
                    response = client.send_request(request)
                else:
                    request = Request()
                    request.code = defines.Codes.POST.number
                    # request.content_type = defines
                    request.type = defines.Types["CON"]
                    request.destination = nodeInfo["Source"]
                    request.uri_path = "lock"
                    request.uri_query = "?state=0"
                    print(request.uri_query)
                    response = client.send_request(request)
        except KeyError as e:
            print("User not present")




def set_up_client(moteInfo):
    time.sleep(5)
    nodeInfo = server.moteDict[moteInfo["NodeID"]]
    client = HelperClient(server=moteInfo["Source"])
    request = Request()
    request.code = defines.Codes.GET.number
    request.content_type = defines.Content_types["application/json"]
    request.type = defines.Types["CON"]
    request.destination = moteInfo["Source"]
    request.uri_path = moteInfo["MoteResource"]
    request.observe = 0
    try:
        client.send_request(request,presence_callback_observer)
    except Exception as e:
        print("Exception")
        print(e.__class__)
        print(str(e))
