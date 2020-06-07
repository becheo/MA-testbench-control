"""
Auswerten von Daten aus einer Textdatei.
@author: Oliver Becher
Masterarbeit: Entwicklung eines vernetzten Prüftands zur web-basierten Validierung und Parametrierung von Simulationsmodellen

Anzeigen und Auswerten der gespeicherten Messdaten sowie gleitende Mittelwertbildung
"""
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure
import numpy as np
import os


# evtl. Bestimmte Dinge der Datei überprüfen (max. Value, min. Value, länge, ...)
# TODO Temperatur mit hinzugügen zu Daten die visualisiert werden

# TODO plots anpassen auf Anzahl an Messreihen der Datei

#  +++++++++++++++    Einstellungen    ++++++++++++++++++++++++++++++++++++++++
filename_web = "USB6009-Messung.txt"

show_specific_time_range = False
time_start = 30.0
time_end = 40.0

running_mean_rpm = False
running_mean_current = True
current_measurement = False
plot_all = False
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

# Dateien im Ordner auflisten:
mypath = os.listdir()
for i in range(0, len(mypath)):
    if filename_web == mypath[i]:
        filename = mypath[i]

# Datei auslesen und nur Daten ohne Header verwenden:
print("Folgende Datei wird geöffnet: ", filename)
with open(filename, "r") as f:
    buffer_textfile = f.read().splitlines()
    for i in range(len(buffer_textfile)):
        if buffer_textfile[i][0:5] == "Index":
            startline_data = i+1
            break
    f.close()

number_of_dataseries = buffer_textfile[startline_data].count(',') + 1
print("Anzahl verschiedener Datenreihen in dieser Datei (inklusive Index und Zeit): ",
      number_of_dataseries)
buffer_textfile = buffer_textfile[startline_data:len(buffer_textfile)]
print("Anzahl an Daten pro Datenreihe: ", len(buffer_textfile))

# list of lists erstellen und Daten in jeweils eine Liste schreiben
data_str = [[] for i in range(number_of_dataseries)]
data = data_str
for word in buffer_textfile:
    word = word.split(", ")
    for i in range(len(word)):
        data_str[i].append(word[i])

# Von String zu float
for i in range(len(data_str)):
    data[i] = [float(i) for i in data_str[i]]

# Aufbau der Daten:
# data[0]: Index
# data[1]: Zeit [s]
# data[2]: Spannung Tachometer [V]
# data[3]: Spannung Generator [V]
# data[4]: Spannung Ansteuerung Motor [V]
# data[5]: Spannung Strommessung [V]

if current_measurement == True:
    plt.title('Sannung der Strommessung')
    plt.plot(data[1], data[2])
    plt.xlabel('Zeit in s')
    plt.ylabel('Spannung in V')
    plt.grid(True)
    plt.tight_layout()
    plt.show()

# Daten visualisieren:
plot_title = {1: "Spannung Tachometer [V]",
              2: "Spannung Generator [V]",
              3: "Spannung Ansteuerug Motor (Motor + Shunt) [V]",
              4: "Spannung Strommessung [V]"}

# for i in range(1, (len(plot_title)+1)):
#     plt.subplot(2, 2, i)
#     plt.title(plot_title[i])
#     plt.plot(data[1], data[i+1])
#     plt.xlabel('Zeit in s')
#     plt.ylabel('Spannung in V')
#     plt.grid(True)
#     if show_specific_time_range == True:
#         plt.axis(xmin=time_start, xmax=time_end)
# plt.tight_layout()
# plt.show()

# Konvertierung der Spanungen

# Konvertierung der Spannung von Tachogenerator in Drehzahl [1/min]
# Spannung bei 1000rpm: 4,3 V
# -> Drehzahl = Spannung/4,3 * 1000
rpm_generator = [(x/4.3)*1000 for x in data[2]]

# Konvertierung Spannung Ansteuerung Motor in Motorspannung
voltage_motor = np.array([], dtype=np.float64)
for i in range(len(data[4])):
    voltage_buffer = data[4][i]-data[5][i]
    voltage_motor = np.append(voltage_motor, voltage_buffer)
# so auch möglich: voltage_motor = [x-data[5][x] for x in data[4]] ?

# Konvertierung der Spannungsmessung des Stromes in Strom
# Widerstand (gemessen): 1,8 Ohm, I = U/R
shunt = 1.8  # [Ohm]
current = [(x/shunt) for x in data[5]]

# Visualisieurung Konvertierte Werte
if plot_all == True:
    plt.subplot(2, 3, 4)
    plt.title('Tachometer')
    plt.plot(data[1], rpm_generator)
    plt.xlabel('Zeit in s')
    plt.ylabel('Drehzahl in 1/min')
    plt.grid(True)
    plt.subplot(2, 3, 5)
    plt.title('Generator')
    plt.plot(data[1], data[3])
    plt.xlabel('Zeit in s')
    plt.ylabel('Spannung in V')
    plt.grid(True)
    plt.subplot(2, 3, 1)
    plt.title('Ansteuerung Motor')
    plt.plot(data[1], data[4])
    plt.xlabel('Zeit in s')
    plt.ylabel('Spannung in V')
    plt.grid(True)
    plt.subplot(2, 3, 3)
    plt.title('Strom')
    plt.plot(data[1], current)
    plt.xlabel('Zeit in s')
    plt.ylabel('Strom in A')
    plt.grid(True)
    plt.subplot(2, 3, 2)
    plt.title('Sannung am Motor')
    plt.plot(data[1], voltage_motor)
    plt.xlabel('Zeit in s')
    plt.ylabel('Spannung in V')
    plt.grid(True)
    plt.tight_layout()
    plt.show()


def running_mean(x, N):
    cumsum = np.cumsum(np.insert(x, 0, 0))
    return (cumsum[N:] - cumsum[:-N]) / float(N)


if running_mean_rpm == True:
    # Graph Vgl. Drehzahl mit und ohne running mean
    for i in range(1, 2):
        figure(figsize=(15, 5))
        num_of_mean_values = i*500
        rpm_generator_filtered = running_mean(
            rpm_generator, num_of_mean_values)
        plt.subplot(1, 2, 1)
        plt.title('Messwerte unverändert')
        plt.plot(data[1], rpm_generator)
        plt.xlabel('Zeit in s')
        plt.ylabel('Drehzahl in 1/min')
        plt.grid(True)
        plt.subplot(1, 2, 2)
        plt.title('Messwerte mit Mittelwertbildung: {}' .format(
            num_of_mean_values))
        plt.plot(data[1][(num_of_mean_values-1):],
                 rpm_generator_filtered)
        plt.xlabel('Zeit in s')
        plt.ylabel('Drehzahl in 1/min')
        plt.grid(True)
        plt.tight_layout()
        plt.show()

if running_mean_current == True:
    for i in range(1, 2):
        figure(figsize=(15, 5))
        num_of_mean_values = i*3500
        rpm_generator_filtered = running_mean(current, num_of_mean_values)
        plt.subplot(1, 2, 1)
        plt.title('Messwerte unverändert')
        plt.plot(data[1], current)
        plt.xlabel('Zeit in s')
        plt.ylabel('Strom in A')
        plt.grid(True)
        plt.subplot(1, 2, 2)
        plt.title('Messwerte mit Mittelwertbildung: {}' .format(
            num_of_mean_values))
        plt.plot(data[1][(num_of_mean_values-1):],
                 rpm_generator_filtered)
        plt.xlabel('Zeit in s')
        plt.ylabel('Strom in A')
        plt.grid(True)
        plt.tight_layout()
        plt.savefig("Strommessung-ohne-AI6-4V_3.pdf",
                    bbox_inches='tight')  # pdf speichern
        plt.show()
