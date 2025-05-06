import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
import numpy as np

# Chargement du fichier Excel
fichier = r"C:\Users\JVCot\OneDrive\Desktop\Mesures\valeurs_reg.xlsx"
df = pd.read_excel(fichier, header=None)

# Données : V_in (entrée), V_out (mesurée)
V_in = df.iloc[:, 0].values
V_out = df.iloc[:, 1].values
u_Vin = df.iloc[:, 2].values
u_Vout = df.iloc[:, 3].values


# Régression linéaire
X = V_in.reshape(-1, 1)
y = V_out
modele = LinearRegression()
modele.fit(X, y)

# Paramètres du modèle
a = modele.coef_[0]
b = modele.intercept_
N = len(V_in)

# Calcul de sigma_V (écart-type des résidus)
residus = V_out - (a * V_in + b)
sigma_V = np.sqrt(np.sum(residus**2) / (N - 2))
u_point = np.sqrt(u_Vin**2 + u_Vout**2)
u_V = np.sqrt(sigma_V + u_point**2)
V_in_mean = np.mean(V_in)
mask = (V_in != V_in_mean)
sum_term = np.sum((V_in[mask] - V_in_mean)**2) 
sum2 = np.sum(u_V**2)
delta_a = np.sqrt((sum2) / (N*sum_term))
R_out = a * (10000 + 12906.40373)
delta_R_out = R_out * np.sqrt((delta_a / a)**2 + (1 / 10000)**2)

print(delta_a)
print(R_out)
print(delta_R_out)

# Tracé
y_pred = modele.predict(X)
plt.scatter(V_in, V_out, label="Données expérimentales", color="blue")
plt.plot(V_in, y_pred, label=f"Régression : y = {a:.6f}x + {b:.6f}", color="red")
plt.xlabel("Tension en entrée (mV)")
plt.ylabel("Tension mesurée (mV)")
plt.legend()
plt.grid(True)
plt.tight_layout()
#plt.show()
