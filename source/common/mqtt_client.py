import paho.mqtt.client as mqtt
import uuid, random, string

class MQTT_Client(mqtt.Client):
    def __init__(self):
        # Creating a unique client id
        self.id = self.__generate_client_id()
        # Creating client object with the id
        super().__init__(self.id)

        # Binding callback functions
        self.on_connect = self.__on_connect
        self.on_disconnect = self.__on_disconnect
        self.on_message = self.__on_message
        self.msg_handler = print

    def connect(self, broker_address):
        if len(broker_address) != 0:
            self.broker_address = broker_address

        super().connect(self.broker_address)

    def __generate_client_id(self):
        # Making a client_id 23 characters long
        mac = str(hex(uuid.getnode()))[2:]
        random_str = "".join(random.choice(string.ascii_letters) for _ in range(11))
        return mac + random_str

    def __on_message(self, client, userdata, msg):
        topic = msg.topic
        m_decode = str(msg.payload.decode("utf-8", "ignore"))
        self.msg_handler(topic, m_decode)

    def __on_connect(self, client, userdata, flags, rc):
        if rc:
            print(f"A problem occured, could not connect to the broker: {self.broker_address}")
        else:
            print(f"Succesfully connected to broker: {self.broker_address}")

    def __on_disconnect(self, client, userdata, flags, rc=0):
        if rc:
            print(f"A problem occured, could not disconnect from the broker: {self.broker_address}")
        else:
            print(f"Succesfully disconnected from broker: {self.broker_address}")