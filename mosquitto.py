from paho.mqtt import client as mqtt_client

def subscribe(client: mqtt_client, handle_fun, topic):
    print(topic+" : up")
    def on_message(client, userdata, msg):
        """
        Lorsqu'un message MQTT est reçu par le thread:
        """
        s = str(msg.payload.decode("utf-8"))
        print("received -> "+msg.topic+" : "+s)
        # On envoi le client, le topic et le contenu du message dans
        # la fonction handle_fun
        handle_fun(client, msg.topic, s)

    client.subscribe(topic)
    # on définit la fonction à exécuter en cas de réception d'un message:
    client.on_message = on_message

def run_mqtt(fun, client_id, topic, broker, port):
    """
    Fonction configurant le client MQTT au lancement du thread
    """
    client = mqtt_client.Client(client_id)
    client.connect(broker, port)
    subscribe(client, fun, topic)
    client.loop_forever()

