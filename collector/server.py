#!/usr/bin/env python

import getopt
import sys
import json
import threading
import time
from coapthon.server.coap import CoAP
from coapthon.resources.resource import Resource
from coapthon.client.helperclient import HelperClient
from coapthon.messages.request import Request
from coapthon.messages.response import Response
from coapthon import defines
from coaphelper import *
from moteresource import MoteResource

moteDict = {}
mqttDict = {}
registeredUsersDict = {}

'''
MoteInfo: dict containing the following fiels:
    NodeType: both for cooja sensors, only notifier for mqtt sensors
    MoteResource: type of resource exposed by the sensor (client)
    NodeID: the identifier of a Node
    Source: ip and port of sender whenever the sensor is registered
'''
# Advanced resource: manage automatically response to registration request
class AdvancedResource(Resource):

    def __init__(self, name="Advanced"):
        super(AdvancedResource, self).__init__(name)
        self.payload = "Successful registration"

    def render_GET_advanced(self, request, response):
        print("GET server, received message:\n")
        print(request.payload)
        print("Dump some useful information")
        print("Source")
        print(request.source)
        print(request.proxy_schema)
        print(request.uri_path)
        print(request.uri_query)
        # Now, we extract the information from the json payload
        moteInfo = json.loads(request.payload)
        # Send a response with successful outcome
        response.payload = self.payload
        response.max_age = 20
        response.code = defines.Codes.CONTENT.number
        # Before exiting the function, we need to define a coapclient which will get notified and can act on the remote sensor
        # Node is a cooja mote
        # Set up observer and requesting client
        # Cooja mote expose a presence and a lock resource, through which server get presence and lock value
        moteInfo["Source"] = request.source

        moteDict[moteInfo["NodeID"]] = moteInfo

        print(moteDict)

        moteResource = MoteResource(moteInfo["Source"],moteInfo["MoteResource"],moteInfo["NodeID"],moteInfo["NodeType"])

        # moteResource.startObserver()

        return self, response

    # def render_POST_advanced(self, request, response):
    #     self.payload = request.payload
    #     print(self.payload)
    #     from coapthon.messages.response import Response
    #     assert(isinstance(response, Response))
    #     response.payload = "Response changed through POST"
    #     response.code = defines.Codes.CREATED.number
    #     return self, response
    #
    # def render_PUT_advanced(self, request, response):
    #     self.payload = request.payload
    #     from coapthon.messages.response import Response
    #     assert(isinstance(response, Response))
    #     response.payload = "Response changed through PUT"
    #     response.code = defines.Codes.CHANGED.number
    #     return self, response
    #
    # def render_DELETE_advanced(self, request, response):
    #     response.payload = "Response deleted"
    #     response.code = defines.Codes.DELETED.number
    #     return True, response

class CoAPServer(CoAP):
    def __init__(self, host, port):
        CoAP.__init__(self, (host, port), False)
        # Register resource: server behave as client in order to get the registration
        self.add_resource("registration", AdvancedResource())
