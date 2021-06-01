import paho.mqtt.client as mqtt
import json
from database import Database
import tabulate


class MqttClient:

    # The callback for when the client receives a CONNACK response from the server.
    def on_connect(self, client, userdata, flags, rc):
        print("Connected with result code "+str(rc))
        self.client.subscribe("weatherinfo")

    # The callback for when a PUBLISH message is received from the server.
    def on_message(self, client, userdata, msg):
        print(msg.topic+"  "+str(msg.payload))
        receivedData = json.loads(msg.payload)
        temp = receivedData["temp"]
        umidity = receivedData["umidity"]
        if receivedData["weather"] == 0:
            weather = "SUNNY"
        elif receivedData["weather"] == 1:
            weather = "CLOUDY"
        else:
            weather = "RAINY"

        with self.connection.cursor() as cursor:
            # Create a new record
            sql = "INSERT INTO `mqttsensors` (`temperature`, `umidity`,`weather`) VALUES (%s, %s, %s)"
            cursor.execute(sql, (temp,umidity,weather))

        # Commit changes
        self.connection.commit()

        # Show data log
        with self.connection.cursor() as cursor2:
            sql = "SELECT * FROM `mqttsensors`"
            cursor2.execute(sql)
            results = cursor2.fetchall()
            header = results[0].keys()
            rows = [x.values() for x in results]
            print(tabulate.tabulate(rows,header,tablefmt='grid'))



    def mqtt_client(self):
        self.db = Database()
        self.connection = self.db.connect_dbs()
        print("Mqtt client starting")
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        try:
            self.client.connect("127.0.0.1", 1883, 60)
        except Exception as e:
            print(str(e))
        self.client.loop_forever()
