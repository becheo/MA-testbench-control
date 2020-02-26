import os
import matplotlib.pyplot as plt
import numpy as np


# Datei die ausgelesen werden soll
filename_web = "Spannungsvorgabe.txt"
frequency = 500

# Dateien im Ordner auflisten:
mypath = os.listdir()
for i in range(0, len(mypath)):
    if filename_web == mypath[i]:
        filename = mypath[i]

# Datei auslesen:
print("Folgende Datei wird geöffnet: ", filename)
with open(filename, "r") as f:
    buffer_textfile = f.read().splitlines()
    f.close()

voltage = [float(i) for i in buffer_textfile]  # Konvertierung in float
print("Vorgegebene Daten: Anzahl: ", len(voltage),
      ";    max. Value: ", max(voltage),
      ";    min. Value: ", min(voltage),
      ";    Dauer: ", (len(voltage)/frequency))

time_buffer = range(0, len(voltage))
time = [(x/500) for x in time_buffer]

plt.plot(time, voltage)
plt.title('Eingelesener Spannugsverlauf')
plt.xlabel('Zeit in s')
plt.ylabel('Spannung in V')
plt.grid(True)
plt.show()
