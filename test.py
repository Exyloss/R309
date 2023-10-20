import tkinter as tk

# Créer la fenêtre principale
fenetre = tk.Tk()
fenetre.title("Alignement horizontal en bas de page")

# Créer un cadre pour contenir les widgets en bas de la fenêtre
cadre_bas = tk.Frame(fenetre)
cadre_bas.pack(side="bottom", fill="x")  # "side" en bas et "fill" en largeur

# Créer deux widgets (par exemple, des boutons) à aligner horizontalement en bas
bouton1 = tk.Button(cadre_bas, text="Bouton 1")
bouton1.pack(side="left")

bouton2 = tk.Button(cadre_bas, text="Bouton 2")
bouton2.pack(side="left")

# Démarrer la boucle principale de l'application
fenetre.mainloop()
