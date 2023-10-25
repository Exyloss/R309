#!/usr/bin/env python3

from tkinter import *
from tkinter import filedialog
from tkinter import ttk
import _thread
from paho.mqtt import client as mqtt_client
import json
from datetime import datetime

default_broker = 'test.mosquitto.org'
default_port = 1883

def subscribe(client: mqtt_client, handle_fun, topic):
    print(topic+" : up")
    def on_message(client, userdata, msg):
        s = str(msg.payload.decode("utf-8"))
        print(msg.topic+" : "+s)
        handle_fun(client, msg.topic, s)

    client.subscribe(topic)
    client.on_message = on_message

def run_mqtt(fun, client_id, topic, broker, port):
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
    l3 = Label(win, text="Topic : ", height=2)
    l3.grid(row=3, column=1)

    broker = Entry(win, width=20)
    broker.grid(row=1, column=2, padx=(0, 20))
    broker.insert(END, "test.mosquitto.org")

    port = Entry(win, width=20)
    port.grid(row=2, column=2, padx=(0, 20))
    port.insert(END, "1883")

    topic = Entry(win, width=20)
    topic.grid(row=3, column=2, padx=(0, 20))

    create = Button(win, text="Créer", width=10, command=lambda topic_entry=topic, broker_entry=broker, port_entry=port, win=win : append_tab(topic_entry, broker_entry, port_entry, win))
    create.grid(row=4, column=1, padx=(30, 0))

    cancel = Button(win, text="Annuler", width=10, command=win.destroy)
    cancel.grid(row=4, column=2)

def append_tab(topic_entry, broker_entry, port_entry, win=None):
    global tabs
    topic = topic_entry.get()
    port = int(port_entry.get())
    broker = broker_entry.get()
    entry.delete(0, END)
    tabs[topic] = { "win": ttk.Frame(tabControl) }
    tabControl.add(tabs[topic]["win"], text=topic)

    tabs[topic]["result"] = Text(tabs[topic]["win"])
    tabs[topic]["result"].pack()
    tabs[topic]["result"].config(state=DISABLED)

    tabs[topic]["username"] = "exylos1"
    tabs[topic]["port"] = port
    tabs[topic]["broker"] = broker

    tabs[topic]["entry"] = Entry(tabs[topic]["win"], width=40)
    tabs[topic]["entry"].pack()

    tabs[topic]["submit"] = Button(tabs[topic]["win"], text="Envoyer", width=40, command=lambda topic=topic : publish(topic))
    tabs[topic]["submit"].pack()

    tabs[topic]["export"] = Button(tabs[topic]["win"], text="Exporter les données", width=40, command=lambda topic=topic : export_logs(topic))
    tabs[topic]["export"].pack()

    tabs[topic]["closed"] = False
    tabs[topic]["logs"] = []

    client_id = "exylos1"
    tabs[topic]["thread"] = _thread.start_new_thread(run_mqtt, (handle_fun, client_id, topic, broker, port))
    if win != None:
        win.destroy()

def destroy_tab(event):
    global tabs
    topic = tabControl.tab(tabControl.select(), "text")
    tabControl.forget(tabControl.select())
    if topic != "Accueil":
        tabs[topic]["closed"] = True
    else:
        root.destroy()

def handle_fun(client, topic, data):
    global tabs
    if tabs[topic]["closed"]:
        client.disconnect()
        tabs.pop(topic)
        _thread.exit()
    recept = ""
    now = datetime.now()
    current_time = now.strftime("Le %d/%m/%y à %H:%M:%S : ")
    tabs[topic]["logs"].append(data)
    tabs[topic]["result"].config(state=NORMAL)
    tabs[topic]["result"].insert(END, current_time+data+"\n")
    tabs[topic]["result"].config(state=DISABLED)

def publish(topic):
    text = tabs[topic]["entry"].get()
    print(topic+" : "+text)
    client= mqtt_client.Client(tabs[topic]["username"]+"1")
    client.connect(tabs[topic]["broker"], tabs[topic]["port"])
    client.publish(topic, text)
    client.disconnect()

def export_logs(topic):
    name = filedialog.asksaveasfilename(filetypes=[("Format JSON", "*.json"),("Texte brut", "*.txt")])
    data = tabs[topic]["logs"]
    f = open(name, "w")
    if name.split(".")[-1] == "txt":
        for i in data:
            f.write(i)
    elif name.split(".")[-1] == "json":
        f.write(json.dumps(data))
    f.close()


root = Tk()
root.title("Tkinter")
root.geometry("400x600")

tabControl = ttk.Notebook(root)
tabControl.pack(expand=1, fill="both")
tabs = {}

fen = ttk.Frame(root, width=1000)
fen.pack(side="bottom", fill="x")

tabControl.add(fen, text="Accueil")

submit = Button(fen, text="Créer le topic", width=40)
submit.pack(side="bottom")

entry = Entry(fen, width=40)
entry.pack(side="bottom")

submit["command"] = lambda entry=entry : append_tab(entry)


root.bind("<Control-t>", new_tab)
root.bind("<Control-w>", destroy_tab)
root.mainloop()
