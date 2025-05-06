import csv
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path


# === Chemin vers le fichier CSV ===
file_path = Path(r"C:\Users\JVCot\OneDrive\Desktop\Mesures\mesures_20_mV.CSV")

# === Étape 1 : Lecture du fichier CSV ===
metadonnees = {}
donnees_brutes = []

with file_path.open(newline='') as csvfile:
    reader = csv.reader(csvfile)
    lecture_donnees = False

    for row in reader:
        if not row:
            continue
        if row[0].strip() == "Waveform Data":
            lecture_donnees = True
            continue
        if lecture_donnees:
            donnees_brutes.extend([int(val.strip()) for val in row if val.strip()])
        else:
            if len(row) >= 2:
                metadonnees[row[0].strip()] = row[1].strip()

# === Étape 2 : Extraction des paramètres ===
sampling_period = float(metadonnees.get("Sampling Period", 1e-4))
vertical_scale = float(metadonnees.get("Vertical Scale", 1.0))
vertical_position = float(metadonnees.get("Vertical Position", 0.0))

# Nettoyage du champ 'Probe' pour retirer le "X"
probe_str = metadonnees.get("Probe", "1.0")
probe = float(probe_str.replace("X", ""))


# === Étape 3 : Conversion des données brutes en tension ===
valeurs_volts = [
    -(val * vertical_scale / 25.0) + 0.0
    for val in donnees_brutes
]
temps = np.arange(len(valeurs_volts)) * sampling_period


# === Étape 4 : Affichage ===

# 1. Nuage de points
plt.figure(figsize=(12, 4))
plt.plot(temps * 1e6, valeurs_volts, marker='.', linestyle='none', markersize=2, color='blue')
plt.xlabel("Temps (µs)", fontsize=14)
plt.ylabel("Tension (V)", fontsize=14)
plt.grid(True)
plt.tight_layout()

# 2. Histogramme
plt.figure(figsize=(6, 4))
plt.hist(valeurs_volts, bins=50, color='orange', edgecolor='black')
plt.xlabel("Tension (V)")
plt.ylabel("Occurrences")

# Lignes pointillées rouges aux tensions spécifiques
valeurs_marquees = [0.17462]
for val in valeurs_marquees:
    plt.axvline(x=val, color='red', linestyle='--', linewidth=1)

plt.tight_layout()

plt.show()

from scipy.stats import norm

from scipy.stats import norm

# === Étape 5 : Sélection d'une plage temporelle et ajustement gaussien ===

# Définir les bornes de la plage (en secondes)
t_min = 200 *10**(-6)# début de la plage
t_max = 245 * 10**(-6)  # fin de la plage

# Sélectionner les indices correspondant à cette plage
indices = np.where((temps >= t_min) & (temps <= t_max))[0]
valeurs_selectionnees = np.array(valeurs_volts)[indices]


# Extraire les sous-ensembles de données
temps_selectionnes = temps[indices]
valeurs_selectionnees = np.array(valeurs_volts)[indices]

résolution = 8*(vertical_scale)/256
print(f"La résolution est : {résolution}")
print(f"La gaussienne contient {len(valeurs_selectionnees)} mesures")

# Ajustement d'une gaussienne
mu, sigma = norm.fit(valeurs_selectionnees)

# Affichage de l'histogramme + fit
plt.figure(figsize=(6, 4))
count, bins, _ = plt.hist(valeurs_selectionnees, bins=50, color='lightblue', edgecolor='black', label='Histogramme')

# Courbe de la gaussienne ajustée
x = np.linspace(bins[0], bins[-1], 1000)
y = norm.pdf(x, mu, sigma)
plt.plot(x, y, 'r--', label=f'Fit Gaussien\nμ = {mu:.4f} V\nσ = {sigma:.4f} V')

plt.xlabel("Tension (V)")
plt.ylabel("Occurences")
plt.legend()
plt.tight_layout()
plt.grid(True)

plt.show()




