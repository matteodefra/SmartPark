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
from database import Database
import tabulate
import logging

class MoteResource:

    def __init__(self,source_address,resource,node_id,node_type):
        # Initialize mote resource fields
        self.db = Database()
        self.connection = self.db.connect_dbs()
        self.address = source_address
        self.resource = resource
        self.id = node_id
        self.type = node_type
        self.actuator_resource = "lock"
        self.client_name = ""
        self.password = ""
        self.box_situation = "Free"
        # Start observing for updates
        self.start_observing()

    '''
    Extract the request payload containing the client name and password and the actual box situation.
    If client is registered, then a post message is sent to the mote in order to modify the state
    of the lock. Then a query is executed to update the database with the current situation
    '''
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
                    lockState = nodeData["BoxSituation"]
                    print(lockState)
                    self.box_situation = "Free" if lockState == 'F' else 'Busy'
                    if lockState == 'F':
                        response = self.client.post(self.actuator_resource,"state=1")
                        self.execute_query(1)
                    else:
                        response = self.client.post(self.actuator_resource,"state=0")
                        self.execute_query(0)
            except KeyError as e:
                print("User not present")
                print(str(e))
            except Exception as e1:
                print(str(e1))


    def show_data_log(self):

        print(self.connection)

        with self.connection.cursor() as cursor:
            sql = "SELECT * FROM `coapsensors`"
            cursor.execute(sql)
            results = cursor.fetchall()
            header = results[0].keys()
            rows = [x.values() for x in results]
            print(tabulate.tabulate(rows,header,tablefmt='grid'))

    '''
    Execute simple insert on database and call show_data_log
    '''
    def execute_query(self,value):

        print(self.connection)

        if value == 1:

            with self.connection.cursor() as cursor:
                # Create a new record
                sql = "INSERT INTO `coapsensors` (`name`, `entering`) VALUES (%s, %s)"
                cursor.execute(sql, (self.client_name, 1))

            # connection is not autocommit by default. So you must commit to save
            # your changes.
            self.connection.commit()

        else:

            with self.connection.cursor() as cursor:
                # Create a new record
                sql = "INSERT INTO `coapsensors` (`name`, `entering`) VALUES (%s, %s)"
                cursor.execute(sql, (self.client_name,0))

            # connection is not autocommit by default. So you must commit to save
            # your changes.
            self.connection.commit()

        self.show_data_log()


    '''
        Launch helper client to listen for incoming new messages
    '''
    def start_observing(self):
        logging.getLogger("coapthon.server.coap").setLevel(logging.WARNING)
        logging.getLogger("coapthon.layers.messagelayer").setLevel(logging.WARNING)
        logging.getLogger("coapthon.client.coap").setLevel(logging.WARNING)
        self.client = HelperClient(self.address)
        self.client.observe(self.resource,self.presence_callback_observer)
