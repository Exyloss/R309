from paho.mqtt import client as mqtt_client

def connect_mqtt(client_id) -> mqtt_client:
    broker = 'test.mosquitto.org'
    port = 1883
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print(f"Failed to connect, return code {rc}\n")

    client = mqtt_client.Client(client_id)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client

def subscribe(client: mqtt_client, handle_fun, topic):
    data = []
    def on_message(client, userdata, msg):
        s = str(msg.payload.decode("utf-8"))
        data.append(s)
        handle_fun(msg.topic, data)
    client.subscribe(topic)
    client.on_message = on_message

def run_mqtt(fun, client_id, topic):
    client = connect_mqtt(client_id)
    subscribe(client, fun, topic)
    client.loop_forever()
