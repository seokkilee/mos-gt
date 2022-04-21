import paho.mqtt.client as mqtt

client = mqtt.Client("test")

def on_connect(client, userdat, flags, rc):
    if rc == 0:
        print ("connected ok")
    else:
        print("bad connection. Returned code =", rc)

def on_disconnect(client,userdata, flags, rc=0):
    print("disconnected: ",str(rc))

def on_subscribe(client, userdata, mid, granted_qos):
    print("subscribed: " + str(mid) + " " + str(granted_qos))


def on_message(client, userdata, msg):
    print("message received")
    print(str(msg.payload.decode("utf-8")))

client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_subscribe = on_subscribe
client.on_message = on_message
# address : localhost, port: 1883 에 연결
#client.connect("test.mosquitto.org")
client.connect("143.248.36.215", 1883)
# common topic 으로 메세지 발행
client.subscribe('emotion0/drive', 1)
client.loop_forever()
