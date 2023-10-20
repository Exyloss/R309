#!/usr/bin/env python3

from tkinter import *
from tkinter import ttk
import _thread
from mqtt_fun import run_mqtt

def new_tab(event=None):
    def append_tab():
        global tabs
        topic = entry.get()
        tabs[topic] = ttk.Frame(tabControl)
        tabControl.add(tabs[topic], text=topic)
        print(tabs)
        win.destroy()

    win = Toplevel(root)
    entry = Entry(win, width=20)
    entry.pack()
    create = Button(win, text="Créer", width=10, command=append_tab)
    create.pack(side=LEFT)
    cancel = Button(win, text="Annuler", width=10, command=win.destroy)
    cancel.pack(side=RIGHT)

def destroy_tab(event):
    global tabs
    tabControl.forget(tabControl.select())

def handle_fun(topic, data):
    recept = ""
    for i in data:
        recept += i+"\n"
    result.config(text=recept)

def publish():
    text = entry.get()


topic = "/exylos"
client_id = "exylos1"
data = []

root = Tk()
root.title("Tkinter")
root.geometry("400x400")

tabControl = ttk.Notebook(root)
tabControl.pack(expand=1, fill="both")
tabs = {}

fen = ttk.Frame(root, width=1000)
fen.pack(side="bottom", fill="x")

result = Label(root, background="lightblue")
result.pack()

entry = Entry(fen, width=40)
entry.pack(side="left")

submit = Button(fen, text="Envoyer", width=5, command=publish)
submit.pack(side="left")

_thread.start_new_thread(run_mqtt, (handle_fun, client_id, topic))

root.bind("<Control-t>", new_tab)
root.bind("<Control-w>", destroy_tab)
root.mainloop()
