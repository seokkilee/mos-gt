from config import *
from vehicle_commands import *
import paho.mqtt.client as mqtt
import json

class VehicleController:

    def __init__(self):
        #self.topic = "{}/drive".format(topic)
        self.client = mqtt.Client()
        self.client.on_connect = VehicleController.on_connect
        self.client.on_disconnect = VehicleController.on_disconnect
        self.client.on_publish = VehicleController.on_publish
        self.client.on_subscribe = VehicleController.on_subscribe
        self.client.username_pw_set(mqtt_username, mqtt_passwd)
        self.client.connect(host=mqtt_broker_host, port=mqtt_broker_port, keepalive=mqtt_keepalive)

    def get_client(self):
        return self.client

    def drive_ctrl(self, vehicle, dri_key, angle):
        self.publish_cmd(self.build_cmd_msg(dri_key, angle), VEHICLE[vehicle], DRI_CMD)

    def aux_ctrl(self, vehicle, aux_key, value):
        self.publish_cmd(self.build_cmd_msg(aux_key, value), VEHICLE[vehicle], AUX_CMD)

    def publish_cmd(self, cmd, vehicle_name, cmd_type):
        if cmd_type == DRI_CMD:
            topic = "{}/{}".format(vehicle_name, "drive")
        else:
            topic = "{}/{}".format(vehicle_name, "aux")

        self.client.loop_start()
        self.client.publish(topic, cmd, 2)
        self.client.loop_stop()

    def build_cmd_msg(self, key, val):
        built_cmd = ""
        built_cmd = str([key, val])

        return built_cmd

    def disconnect(self):
        self.client.disconnect()
        
    @staticmethod
    def on_connect(client, userdata, flags, rc):
        if rc == mqtt.CONNACK_ACCEPTED:
            print("connected OK")

        else:
            print("Bad connection Returned code=", rc)

    @staticmethod
    def on_disconnect(client, userdata, flags, rc=0):
        print(str(rc))

    @staticmethod
    def on_publish(client, userdata, mid):
        print("In on_pub callback mid= ", mid)

    @staticmethod
    def on_subscribe(client, userdata, mid, granted_qos):
        print("Subscribed with")

"""
if __name__ == "__main__":
    vc = VehicleController()
    vc.drive_ctrl(0, -1, 2)
    vc.drive_ctrl(0, 2, 3)
"""
"""
client.loop_start()
client.publish('common1', json.dumps({"success": "ok"}), 2)
client.loop_stop()
client.disconnect()
"""
