from coapthon.server.coap import CoAP
from coapthon.resources.resource import Resource
from coapthon.client.helperclient import HelperClient
from coapthon.messages.request import Request
from coapthon.messages.response import Response
from coapthon import defines
import json
import time
import server
import threading


class MoteResource:

    def __init__(self,source_address,resource,node_id,node_type):
        self.address = source_address
        self.resource = resource
        self.id = node_id
        self.type = node_type
        self.actuator_resource = "lock"
        self.client_name = ""
        self.password = ""
        self.box_situation = "Free"
        self.startObserver()


    def presence_callback_observer(self,response):
        print("Callback called, resource arrived")
        if response.payload is not None:
            print(response.payload)
            nodeData = json.loads(response.payload)
            if not nodeData["ClientInfo"]:
                print("Credentials are empty: discard message...")
                return
            credentials = nodeData["ClientInfo"].split(" ")
            print("Client credentials are:")
            print(credentials)
            self.client_name = credentials[0]
            self.password = credentials[1]
            try:
                server_password = server.registeredUsersDict[credentials[0]]
                if server_password == self.password:
                    print("User recognized!")
                    # Need to check this nodeInfo struct
                    lockState = nodeData["BoxSituation"]
                    print(lockState)
                    self.box_situation = "Free" if lockState == 'F' else 'Busy'
                    if lockState == 'F':
                        # request = Request()
                        # request.code = defines.Codes.POST.number
                        # # request.content_type = defines
                        # request.type = defines.Types["CON"]
                        # request.destination =
                        # request.uri_path =
                        # request.uri_query = "?state=1"
                        # print(request.uri_query)
                        response = self.client.post(self.actuator_resource,"state=1")
                    else:
                        # request = Request()
                        # request.code = defines.Codes.POST.number
                        # # request.content_type = defines
                        # request.type = defines.Types["CON"]
                        # request.destination = nodeInfo["Source"]
                        # request.uri_path = "lock"
                        # request.uri_query = "?state=0"
                        # print(request.uri_query)
                        response = self.client.post(self.actuator_resource,"state=0")
            except KeyError as e:
                print("User not present")
                print(str(e))
            except Exception as e1:
                print(str(e1))



    def start_observing(self):
        self.client = HelperClient(self.address)
        self.client.observe(self.resource,self.presence_callback_observer)
        # request = Request()
        # request.code = defines.Codes.GET.number
        # request.content_type = defines.Content_types["application/json"]
        # request.type = defines.Types["CON"]
        # request.destination = self.address
        # request.uri_path = self.resource
        # request.observe = 0
        # request.block2 = (0, 0, 64)
        # try:
        #     self.client.send_request(request,self.presence_callback_observer)
        # except Exception as e:
        #     print("Exception")
        #     print(e.__class__)
        #     print(str(e))


    def startObserver(self):
        time.sleep(5)
        thr = threading.Thread(target=self.start_observing, args=(), kwargs={})
        thr.start()
        return self
