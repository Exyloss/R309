#!/usr/bin/env python3

from tkinter import *
from tkinter import filedialog, ttk
import _thread
from paho.mqtt import client as mqtt_client
import json
from datetime import datetime

default_broker = 'test.mosquitto.org'
default_port = 1883
default_user = "tkclient"
n = 0

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

def new_tab(event=None):
    win = Toplevel(root)

    l1 = Label(win, text="Broker : ", height=2)
    l1.grid(row=1, column=1)
    l2 = Label(win, text="Port : ", height=2)
    l2.grid(row=2, column=1)
    l3 = Label(win, text="Username : ", height=2)
    l3.grid(row=3, column=1)
    l4 = Label(win, text="Topic : ", height=2)
    l4.grid(row=4, column=1)

    broker = Entry(win, width=20)
    broker.grid(row=1, column=2, padx=(0, 20))
    broker.insert(END, "test.mosquitto.org")

    port = Entry(win, width=20)
    port.grid(row=2, column=2, padx=(0, 20))
    port.insert(END, "1883")

    user = Entry(win, width=20)
    user.grid(row=3, column=2, padx=(0, 20))
    user.insert(END, default_user+str(n))

    topic = Entry(win, width=20)
    topic.grid(row=4, column=2, padx=(0, 20))

    # L'action de ce bouton sera l'execution de la fonction append_tab
    # avec les paramètres adéquat
    create = Button(win, text="Créer", width=10, command=
                    lambda
                        topic_entry=topic,
                        broker_entry=broker,
                        port_entry=port,
                        user_entry=user,
                        win=win :
                        append_tab(topic_entry, broker_entry, port_entry, user_entry, win)
                    )
    create.grid(row=5, column=1, padx=(30, 0))

    cancel = Button(win, text="Annuler", width=10, command=win.destroy)
    cancel.grid(row=5, column=2)

def append_tab(topic_entry, broker_entry, port_entry, user_entry, win=None):
    """
    Fonction permettant de créer un nouvel onglet et un nouveau thread MQTT
    *_entry: Entrée contenant la valeur du *
    """
    global tabs, n
    topic = topic_entry.get()
    port = int(port_entry.get())
    broker = broker_entry.get()
    user = user_entry.get()
    print((topic, port, broker, user))
    tabs[topic] = { "win": Frame(tabControl) }
    tabControl.add(tabs[topic]["win"], text=topic)

    # result sera le champ texte dans lequel il y aura les messages reçus
    tabs[topic]["result"] = Text(tabs[topic]["win"], width=70)
    tabs[topic]["result"].grid(row=1, column=0, columnspan=2, padx=(0, 0))
    tabs[topic]["result"].config(state=DISABLED)

    tabs[topic]["user"] = user
    if user == default_user+str(n):
        n += 1
        user_entry.delete(0, END)
        user_entry.insert(END, default_user+str(n))

    tabs[topic]["port"] = port
    tabs[topic]["broker"] = broker

    # Entrée contenant le message que l'utilisateur souhaite envoyer
    tabs[topic]["entry"] = Entry(tabs[topic]["win"], width=40)
    tabs[topic]["entry"].grid(row=2, column=0, padx=(0, 0))

    submit_button = Button(tabs[topic]["win"], text="Envoyer", width=10, command=lambda topic=topic : publish(topic))
    submit_button.grid(row=2, column=1, padx=(0, 0))

    export_button = Button(tabs[topic]["win"], text="Exporter les données", width=55, command=lambda topic=topic : export_logs(topic))
    export_button.grid(row=3, column=0, columnspan=2)

    tabs[topic]["closed"] = False

    exit_button = Button(tabs[topic]["win"], text="Quitter", width=55, command=destroy_tab)
    exit_button.grid(row=4, column=0, columnspan=2)

    # Variable contenant les logs MQTT pour le topic créé
    tabs[topic]["logs"] = []

    # On stocke l'identifiant du thread dans un variable et on le lance
    tabs[topic]["thread"] = _thread.start_new_thread(run_mqtt, (handle_fun, user, topic, broker, port))
    if win != None:
        win.destroy()
    else:
        topic_entry.delete(0, END)

def destroy_tab(event=None):
    global tabs
    topic = tabControl.tab(tabControl.select(), "text")
    tabControl.forget(tabControl.select())
    if topic != "Accueil":
        tabs[topic]["closed"] = True

def handle_fun(client, topic, data):
    """
    Fonction traitant les données reçues par le client MQTT
    """
    global tabs
    if tabs[topic]["closed"]:
        # Si le topic est marqué comme étant fermé,
        # on ferme le client et le thread associé
        client.disconnect()
        tabs.pop(topic)
        _thread.exit()
    recept = ""
    now = datetime.now()
    # On formate la date
    current_time = now.strftime("Le %d/%m/%y à %H:%M:%S : ")
    now = datetime.now()
    log_time = now.strftime("%y-%m-%d;%H:%M:%S")
    # On ajoute aux logs le message reçu
    tabs[topic]["logs"].append({"topic": topic, "data": data, "time": log_time})
    tabs[topic]["result"].config(state=NORMAL)
    # On insère au champ de texte le message et la date
    tabs[topic]["result"].insert(END, current_time+data+"\n")
    tabs[topic]["result"].config(state=DISABLED)

def publish(topic):
    """
    Publier un message sur un topic
    """
    text = tabs[topic]["entry"].get()
    print("published -> "+topic+" : "+text)
    client = mqtt_client.Client(tabs[topic]["user"]+"_publish")
    client.connect(tabs[topic]["broker"], tabs[topic]["port"])
    client.publish(topic, text)
    tabs[topic]["entry"].delete(0, END)
    client.disconnect()

def export_logs(topic):
    # Fonction Tkinter permettant de demander à l'utilisateur de créer
    # un nouveau fichier
    name = filedialog.asksaveasfilename(filetypes=[
            ("Format JSON", "*.json"),
            ("Texte brut", "*.txt")
        ]
    )
    data = tabs[topic]["logs"]
    f = open(name, "w")
    if name.split(".")[-1] == "txt": # Si l'utilisateur a sélectionné texte brut
        for i in data:
            f.write(topic+";"+i["time"]+";"+i["data"]+"\n")
    elif name.split(".")[-1] == "json": # Si l'utilisateur a sélectionné JSON
        f.write(json.dumps(data))
    f.close()


root = Tk()
root.title("Tkinter")
root.geometry("500x540")

tabControl = ttk.Notebook(root)
tabControl.pack(expand=1, fill="both")
# tabs est un dictionnaire contenant les différents widgets créés pour chaque
# topic, ainsi que les informations supplémentaires.
tabs = {}

fen = Frame(root, width=1000)
fen.pack(side="bottom", fill="x")

tabControl.add(fen, text="Accueil")

aide = Text(fen, width=70, height=15)
aide.grid(row=0, column=0, rowspan=2, columnspan=2, pady=(0, 50))

help_file = open("help.txt", "r")
for i in help_file.readlines():
    aide.insert(END, i)
help_file.close()
aide.config(state=DISABLED)

l1 = Label(fen, text="Broker :", width=10)
l1.grid(row=2, column=0, pady=(0, 10))
l2 = Label(fen, text="Port :", width=10)
l2.grid(row=3, column=0, pady=(0, 10))
l3 = Label(fen, text="Username :", width=10)
l3.grid(row=4, column=0, pady=(0, 10))
l4 = Label(fen, text="Topic :", width=10)
l4.grid(row=5, column=0, pady=(0, 10))

broker = Entry(fen, width=45)
broker.grid(row=2, column=1)
broker.insert(END, "test.mosquitto.org")

port = Entry(fen, width=45)
port.grid(row=3, column=1)
port.insert(END, "1883")

user = Entry(fen, width=45)
user.grid(row=4, column=1)
user.insert(END, default_user+str(n))

topic = Entry(fen, width=45)
topic.grid(row=5, column=1)

create = Button(fen, text="Créer le topic", width=55, command=lambda
                        topic_entry=topic,
                        broker_entry=broker,
                        port_entry=port,
                        user_entry=user,
                        :
                        append_tab(topic_entry, broker_entry, port_entry, user_entry)
                    )

create.grid(row=6, column=0, columnspan=2)

exit_button = Button(fen, text="Quitter", width=55, command=quit)
exit_button.grid(row=7, column=0, columnspan=2)

root.bind("<Control-t>", new_tab)
root.bind("<Control-w>", destroy_tab)
root.mainloop()
