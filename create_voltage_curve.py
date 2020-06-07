"""
Script zum Erstellen eines Spannungsverlaufs für den Prüfstand
@author: Oliver Becher
Masterarbeit: Entwicklung eines vernetzten Prüftands zur web-basierten Validierung und Parametrierung von Simulationsmodellen
"""

import time
import numpy as np
import matplotlib.pyplot as plt


samplerate_write = 250  # Ausgabefrequenz [Hz]
voltage_np = np.array([0], dtype=np.float64)
dateiname = "Spannungsvorgabe.txt"


def voltage_hold(array, duration):
    '''create voltage holding curve'''
    holdvalue = array[-1]
    value = np.array([np.repeat([holdvalue], (duration*samplerate_write))],
                     dtype=np.float64)  # 20 Sekunden bei 500 Hz
    array = np.append(array, value)
    return array


def voltage_alter(array, duration, endvalue):
    '''Create voltage curve appending the array'''
    value = array[-1]
    startvalue = value
    if value < endvalue:
        while value < endvalue:
            value = value + ((endvalue-startvalue)/(samplerate_write*duration))
            array = np.append(array, value)
        return array
    elif value > endvalue:
        while value > endvalue:
            value = value - ((startvalue-endvalue)/(samplerate_write*duration))
            array = np.append(array, value)
        return array
    else:
        voltage_hold(array, duration)
        return array


def voltage_step(array, endvalue):
    array = np.append(array, endvalue)
    return array


# def voltage_rise(array, duration, endvalue, value, startvalue):
#     '''create rising voltage curve'''
#     while value < endvalue:
#         value = value + ((endvalue-startvalue)/(samplerate_write*duration))
#         array = np.append(array, value)
#     return array


# def voltage_hold(array, duration):
#     '''create voltage holding curve'''
#     holdvalue = array[-1]
#     value = np.array([np.repeat([holdvalue], (duration*samplerate_write))],
#                      dtype=np.float64)  # 20 Sekunden bei 500 Hz
#     array = np.append(array, value)
#     return array


# def voltage_reduction(array, duration, endvalue, value, startvalue):
#     '''create voltage reduction curve'''
#     while value > endvalue:
#         value = value - ((startvalue-endvalue)/(samplerate_write*duration))
#         array = np.append(array, value)
#     return array


# def voltage_alter(array, duration, endvalue):
#     value = array[-1]
#     startvalue = value
#     if value < endvalue:
#         return_array = voltage_rise(
#             array, duration, endvalue, value, startvalue)
#         return return_array
#     elif value > endvalue:
#         return_array = voltage_reduction(
#             array, duration, endvalue, value, startvalue)
#         return return_array
#     else:
#         return_array = voltage_hold(array, duration)
#         return return_array


# ++++++++++++++++++++++++    Array creation    +++++++++++++++++++++++++++++++
# # 't' s Anstieg bis 'x' V
# voltage_np = voltage_rise(voltage_np, 10, 1.5)

# # 'x' V für 't' Sekunden halten
# voltage_np = voltage_hold(voltage_np, 20)

# # 't' s Anstieg von 'x' V auf 'y' V
# voltage_np = voltage_rise(voltage_np, 10, 2)

# # 'x' V 't' Sekunden halten
# voltage_np = voltage_hold(voltage_np, 20)

# # Abnahme bis 'x' V in 't' Sekunden
# voltage_np = voltage_reduction(voltage_np, 10, 0)


start_time = time.time()

voltage_np = voltage_alter(voltage_np, 5, 1.5)
voltage_np = voltage_hold(voltage_np, 20)
# voltage_np = voltage_step(voltage_np, 3.0)
# voltage_np = voltage_alter(voltage_np, 10, 3.0)
# voltage_np = voltage_hold(voltage_np, 10)
voltage_np = voltage_alter(voltage_np, 5, 0.0)

# ++++++++++++++++++++++    Array creation end    +++++++++++++++++++++++++++++
print("Dauer Erstellung: ", time.time()-start_time)


# TODO array auf Werte überprüfen (nur positive Werte erlaubt, evtl auch nach Amplitude überprüfen)

start_time = time.time()
# Abspeichern in Textdatei

# np.savetxt(dateiname, voltage_np,
#            fmt="%.3f", delimiter='\n')
np.savetxt(dateiname, voltage_np,
           delimiter='\n')
print("Array erzeugt mit der Länge: ", len(voltage_np))  # list
print("Datei abgespeichert: ", dateiname)

print("Dauer Abspeichern: ", time.time()-start_time)

time_buffer = range(0, len(voltage_np))
time = [(x/samplerate_write) for x in time_buffer]

# Visualisierung
plt.plot(time, voltage_np)
plt.xlabel('Zeit in s')
plt.ylabel('Spannung in V')
plt.grid(True)
plt.show()
