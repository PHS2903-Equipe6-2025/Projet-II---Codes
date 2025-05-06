import pandas as pd
from pathlib import Path

# === Chemin vers le fichier CSV ===
file_path = Path(r"C:\Users\JVCot\OneDrive\Desktop\Mesures\entrée_20_mV.CSV")

# Lire le fichier CSV en sautant les premières lignes et en cherchant la ligne "Waveform Data"
with open(file_path, 'r') as file:
    lines = file.readlines()

# Trouver l'index de la ligne "Waveform Data"
waveform_data_index = lines.index('Waveform Data,\n')

# Lire les lignes suivantes (les données de temps et de tension)
waveform_data = lines[waveform_data_index + 1:]

# Nettoyer les données : enlever les lignes avec des erreurs ou des formats incorrects
cleaned_data = []
for line in waveform_data:
    line = line.strip().rstrip(',')  # Enlever la virgule de fin
    parts = line.split(',')
    if len(parts) == 2:  # Si la ligne est correctement séparée en deux
        try:
            time = float(parts[0])
            voltage = float(parts[1])
            cleaned_data.append([time, voltage])
        except ValueError:
            # Ignorer les lignes avec des valeurs mal formatées
            continue

# Créer le DataFrame avec les données nettoyées
df = pd.DataFrame(cleaned_data, columns=['Time', 'V_in'])

# Calculer la valeur moyenne de la tension en mV
moyenne_tension_mv = df['V_in'].mean() * 1000  # Conversion en mV
# Calcul de l'incertitude type (écart-type / √N)
import numpy as np
incertitude_mV = df['V_in'].std(ddof=1) / np.sqrt(len(df)) * 1000  # conversion en mV

# Afficher l'incertitude type
print(f"L'incertitude type sur la moyenne est : {incertitude_mV} mV")

# Afficher la moyenne de la tension en mV
print(f'La valeur moyenne de la tension est : {moyenne_tension_mv} mV')
