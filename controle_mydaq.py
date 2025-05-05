import nidaqmx
from nidaqmx.constants import TerminalConfiguration, AcquisitionType, READ_ALL_AVAILABLE
import numpy as np
import time
import matplotlib.pyplot as plt
from multiprocessing import Process
import keyboard

def tension2(volt, canal): #Envoie une tension analogique dans la range +-2V
    with nidaqmx.Task() as task:
        # Créer un canal de sortie analogique (exemple avec 'ao0')
        task.ao_channels.add_ao_voltage_chan(f"myDAQ1/{canal}",  # Canal de sortie
                                            min_val=-2.0,  # Tension minimale
                                            max_val=2.0)   # Tension maximale 
        task.write(volt)  # Envoi de la tension sur le canal

def tension10(volt, canal): #Envoie une tension analogique dans la range +-10V
    with nidaqmx.Task() as task:
        # Créer un canal de sortie analogique (exemple avec 'ao0')
        task.ao_channels.add_ao_voltage_chan(f"myDAQ1/{canal}",  # Canal de sortie
                                            min_val=-10.0,  # Tension minimale (par exemple -10V)
                                            max_val=10.0)   # Tension maximale (par exemple 10V)
        task.write(volt)  # Envoi de la tension sur le canal

def mesure_tension(canal, n): #mesure n valeurs de tension dans un pin d'entrée analogique
    with nidaqmx.Task() as task:
        task.ai_channels.add_ai_voltage_chan(f"myDAQ1/{canal}", min_val=-10.0, max_val=10.0)
        task.timing.cfg_samp_clk_timing(120000, sample_mode=AcquisitionType.FINITE, samps_per_chan=n)
        mesure = task.read(READ_ALL_AVAILABLE)
        return mesure
    
def mesure_1_tension(canal): #mesure une valeur de tension dans un pin d'entrée analogique
    with nidaqmx.Task() as task:
        task.ai_channels.add_ai_voltage_chan(f"myDAQ1/{canal}", min_val=-10.0, max_val=10.0)
        task.timing.cfg_samp_clk_timing(1000, sample_mode=AcquisitionType.FINITE, samps_per_chan=1000)
        mesure = task.read()
        return mesure

def digital_high(ligne): #envoie un high dans un canala digital
    line_name = f"myDAQ1/port0/line{str(ligne)}"  # Choisir la ligne à contrôler
    # Créer une tâche pour la sortie numérique
    with nidaqmx.Task() as task:
        task.do_channels.add_do_chan(line_name)  # Ajouter une ligne numérique
        task.write(True)  # HIGH (5V)

def digital_low(ligne): #ENvoie un low dans un canal digital
    line_name = f"myDAQ1/port0/line{str(ligne)}"  # Choisir la ligne à contrôler
    # Créer une tâche pour la sortie numérique
    with nidaqmx.Task() as task:
        task.do_channels.add_do_chan(line_name)  # Ajouter une ligne numérique
        task.write(False)  # LOW (0 V)

def digital_read(ligne): #Lit l'état d'un canal digital
    line_name = f"myDAQ1/port0/line{str(ligne)}"  # Choisir la ligne à contrôler
    # Créer une tâche pour la sortie numérique
    with nidaqmx.Task() as task:
        task.di_channels.add_di_chan(line_name)  # Ajouter une ligne numérique
        state = task.read()
        return state

def digital_tuple(x): #convertit le tuple binaire en tension dans les digital pins
    for j,i in enumerate(x):
        if i == 0:
            digital_low(j+1)
        if i == 1:
            digital_high(j+1)

def afficher_tension(canal):
    while True:
        print(mesure_1_tension(canal))

def variation_tension(duree, valeur_depart, valeur_fin, canal, frequence=100): #Code réalisé par ChatGPT (n'a pas fonctionné)
    """
    Fait varier la tension de `valeur_depart` à `valeur_fin` sur le `canal`
    durant `duree` secondes.
    
    Arguments :
    - duree : durée de la montée/descente en secondes.
    - valeur_depart : tension initiale (en volts).
    - valeur_fin : tension finale (en volts).
    - canal : nom du canal (ex : "ao0").
    - frequence : nombre de pas par seconde.
    """
    nb_points = int(duree * frequence)
    valeurs = np.linspace(valeur_depart, valeur_fin, nb_points)

    for v in valeurs:
        tension2(v, canal)
        time.sleep(1 / frequence)

def approche_manuelle(): #Approche manuelle/Mode de debug
    while True:
        action = input("0 off, 1-7 fwd, 9-14 bwd, pass (P), ai0, ai1, piezo (pz), slow piezo (s): ")
        if action == "P":
            break
        if action == "ai0":
            process = Process(target = afficher_tension("ai0"))
            process.start()
            while process.is_alive():
                if keyboard.is_pressed('q'):
                    process.terminate()
                    break
        if action == "ai1":
            process = Process(target = afficher_tension("ai1"))
            process.start()
            while process.is_alive():
                if keyboard.is_pressed('q'):
                    process.terminate()
                    break
        if action == "pz":
            vpiezo = 0
            while True:
                print(f"Tension actuelle dans le piezo: {vpiezo} V")
                vpiezo = input("Nouvelle tension dans le piezo (<2): ")
                if vpiezo == "P":
                    break
                else:
                    try:
                        float(vpiezo)
                        tension2(vpiezo, "ao1")
                    except:
                        pass
        if action == "s":
            duree = float(input("Duree de la variation: "))
            depart = float(input("Valeur de départ (<2V): "))
            fin = float(input("Valeur de fin (<2V): "))
            variation_tension(duree, depart, fin, "ao1", 1000)
        else:
            try: 
                int(action)
                if int(action)>=0 and int(action) <= 14:
                    print(*tuple([int(i) for i in bin(int(action))[2:].zfill(4)[::-1]]))
                    while digital_read(0) == True: 
                        digital_tuple(tuple([int(i) for i in bin(int(action))[2:].zfill(4)[::-1]]))
                    digital_tuple((0,0,0,0))
            except:
                pass

def piezotest(): #Vérifie que le piezo est à distance
    tension2(0,"ao1")
    time.sleep(0.3)
    if mesure_1_tension("ai0")> 0.002:
        tension2(2,"ao1")
        time.sleep(0.3)
        if mesure_1_tension("ai0")< 0.002:
            return True
    return False

def approche_piezo(): #Approche plus fine couplant piezo + moteur
    fwd_mod = 3
    bwd_mod = 10
    is_piezoclose = False
    while not is_piezoclose:
        print(f"Avancer en mode {fwd_mod}")
        while mesure_1_tension("ai0") < 0.01:
            is_piezoclose = piezotest()
            if is_piezoclose:
                break
            tension2(2, "ao1")
            if digital_read(0)==True:
                while digital_read(0) == True: 
                    digital_tuple(tuple([int(i) for i in bin(fwd_mod)[2:].zfill(4)[::-1]]))
                digital_tuple((0,0,0,0))
                tension2(0, "ao1")
                is_piezoclose = piezotest()
                if is_piezoclose:
                    break
        fwd_mod = 2
        time.sleep(5)
        print(f"Reculer en mode {bwd_mod}")
        while mesure_1_tension("ai0") > 0.01: # à voir s'il faut mettre un intervalle de valeur
            is_piezoclose = piezotest()
            if is_piezoclose:
                break
            tension2(0, "ao1")
            if digital_read(0)==True:
                while digital_read(0) == True: 
                    digital_tuple(tuple([int(i) for i in bin(bwd_mod)[2:].zfill(4)[::-1]]))
                digital_tuple((0,0,0,0))
                tension2(2, "ao1")
                is_piezoclose = piezotest()
                if is_piezoclose:
                    break
        bwd_mod = 9
        time.sleep(5)

def approche_automatique():
    fwd_mod = 7
    bwd_mod = 14

    # Approche grossière #1 - approche de 1000 à 20 stps
    while fwd_mod > 3:
        print(f"Avancer en mode {fwd_mod}")
        while mesure_1_tension("ai0") < 0.01: # à ajuster l'intervalle de valeur
            if digital_read(0)==True:
                while digital_read(0) == True: 
                    digital_tuple(tuple([int(i) for i in bin(fwd_mod)[2:].zfill(4)[::-1]]))
                digital_tuple((0,0,0,0))
        fwd_mod -= 1
        time.sleep(3)
        print(f"Reculer en mode bwd {bwd_mod}")
        while mesure_1_tension("ai0") > 0.01: # à ajuster l'intervalle de valeur
            if digital_read(0)==True:
                while digital_read(0) == True: 
                    digital_tuple(tuple([int(i) for i in bin(bwd_mod)[2:].zfill(4)[::-1]]))
                digital_tuple((0,0,0,0))
        bwd_mod-=1
        time.sleep(3)

    # Approche grossière #2 - approche <10 stp + piezo
    approche_piezo()

    print("Fin de l'approche automatique!")

def approche_loop():
    fwd_mod = 2
    bwd_mod = 8
    while fwd_mod == 2:
        print(f"Avancer en mode {fwd_mod}")
        while mesure_1_tension("ai0") < 0.005: # à ajuster l'intervalle de valeur
            if digital_read(0)==True:
                while digital_read(0) == True: 
                    digital_tuple(tuple([int(i) for i in bin(fwd_mod)[2:].zfill(4)[::-1]]))
                digital_tuple((0,0,0,0))
        time.sleep(3)
        print(f"Reculer en mode bwd {bwd_mod}")
        while mesure_1_tension("ai0") > 0.005: # à ajuster l'intervalle de valeur
            if digital_read(0)==True:
                while digital_read(0) == True: 
                    digital_tuple(tuple([int(i) for i in bin(bwd_mod)[2:].zfill(4)[::-1]]))
                digital_tuple((0,0,0,0))
        time.sleep(3)

if __name__=='__main__': #Environnement principal
    tension2(0.1,"ao0")
    tension2(0,"ao1")
    digital_tuple((0,0,0,0))
    mode = input("Automatique (A)/ Auto-piezo (P)/ Manuel (M)/ Loop (L): ")
    if mode == "A":
        approche_automatique()
        approche_manuelle()
    if mode == "P":
        approche_piezo()
        approche_manuelle()
    if mode == "M":
        approche_manuelle()
    if mode == "L":
        approche_loop()