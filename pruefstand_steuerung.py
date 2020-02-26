# -*- coding: utf-8 -*-
# Revision History:
# 19/12/16 - Modi hinzugefügt
"""
Created Dec 2019
@author: Oliver Becher
Steuerung Prüfstand
Masterarbeit: Entwicklung eines vernetzten Prüftands zur web-basierten Validierung und Parametrierung von Simulationsmodellen
"""

import time  # built-in modules
import datetime
import os
import sys
import math
import decimal

import matplotlib.pyplot as plt  # third-party modules
import numpy as np

import mdt_custom  # local modules


# from os import listdir
# from os.path import isfile, join


mode = 8
# mode 1: nur lesen
# mode 2: nur schreiben - mehrere Samples
# mode 3: nur schreiben - ein sample
# mode 4: lesen und schreiben
# mode 5: TEST - verschiedenes
# mode 6: Messreihen aus Datei lesen (und anzeigen)
# mode 7: Spannungsverlauf zum testen erstellen
# mode 8: Funktion dataReadAndWrite
# mode 9: Digitalen Ausgang ansteuern


if mode == 1:
    # mode 1: nur lesen

    # data = mdt.dataRead(amplitude=5.0, samplingRate=40000.0,
    #                     duration=1.0, channels=[3], resolution=14, outType='Volt') # Beispielmessung
    start_time = time.time()
    data = mdt_custom.dataRead(amplitude=5.0, samplingRate=200.0, duration=5.0, channels=[
        0, 3], resolution=14, outType='Volt')
    print("Dauer for Schleife: ", time.time()-start_time)

    # channel 0: AI0
    # channel 1: AI1
    # channel ....
    plt.plot(data[0])
    plt.show()

    # with open("testfile.txt", "w") as f:
    #     for item in data[1]:
    #         f.write("%f\n" % item)
    #     f.close()

elif mode == 2:
    # mode 2: nur schreiben - mehrere Samples

    # data = np.ndarray([1, 0], dtype=float64)
    data = np.array([[0, 1, 2, 3, 2, 1, 0]], np.float64)
    # data1 = np.ndarray(shape=(1), dtype=np.float64)
    # data1 = [0]  # , 1, 2, 3, 2, 1, 0]
    Write_return = mdt_custom.dataWrite(data, [0, 1], 10, 1, mode)
    print(Write_return)

    # test = np.array([np.repeat([1, 0], 150), np.repeat([0, 0], 150)])
    # print(test)

elif mode == 3:
    # mode 3: nur schreiben - ein sample

    # +++ Manuelle Eingabe der Spannungswerte: +++
    while True:
        volt = float(input('Please enter voltage: '))
        voltage = volt
        Write_return = mdt_custom.dataWrite(voltage, 0, 10, 0, 3)
        # print(Write_return)
        print(volt)

    # +++ kontinuierliche Ausgabe Spannungswerte aus array: +++
    # repeat_num = 6000
    # volt = np.array([np.tile([1, 0], repeat_num)], dtype=np.float64)
    # for i in range(0, 6000, 1):
    #     voltage = volt[0, i]
    #     Write_return = mdt_custom.dataWrite(voltage, 0, 10, 0, mode)

elif mode == 4:
    print("Mode 4")
    '''
    Mode 4: Daten lesen und schreiben
        - Daten werden abhängig von den vorgegebenen Parametern gechrieben und gelesen.
        - Daten werden nach der Messung in Textdatei abgespeichert
        - Daten werden visualisiert
    '''

    # Daten schreiben und lesen:
    Dauer = 5  # [s]
    Samplerate_read = 200  # [Hz] -> Muss immer vielfaches von 'write' sein
    Samplerate_write = 100  # [Hz]
    Kanäle = [0, 3]

    # Testarray, falls Spannungsverlauf hier vorgegeben werden soll:
    # voltage = [0.0, 1.0, 1.005, 1.01, 1.015, 1.02,
    #            1.025, 1.03, 1.035, 1.04, 1.045, 0.0]

    filename_web = "Spannungsvorgabe.txt"  # Datei die ausgelesen werden soll

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
          "; Max. Value: ", max(voltage),
          "; min. Value: ", min(voltage))

    data = np.zeros((len(Kanäle), Dauer*Samplerate_read))
    read_write_ratio = int(Samplerate_read/Samplerate_write)
    timedata = []

    # Schreiben und lesen der Daten:
    start_time = time.time()
    for i in range(0, Dauer*Samplerate_write, 1):
        Write_return = mdt_custom.dataWrite(voltage[i], 0, 10, 0, 3)
        data_chunk = mdt_custom.dataRead(amplitude=5.0, samplingRate=Samplerate_read, duration=(1.0/Samplerate_write),
                                         channels=[0, 3], resolution=14, outType='Volt')
        data[:, i*read_write_ratio:i*read_write_ratio +
             read_write_ratio] = data_chunk
        # timedata.extend([format(time.time()-start_time, '.3f')])

    print("Dauer for Schleife: ", time.time()-start_time)
    # for Schleife mit Zeitmessung in der Schleife: 23.02 s
    # for Schleife ohne Zeitmessung in der Schleife: 21.97

    timedata_new = [0]
    for i in range(0, len(timedata)):
        timedata_new.append(float(timedata[i]))
        if i < (len(timedata)-1):
            timedata_new.append((float(timedata[i])+float(timedata[i+1]))/2)

    # Daten abspeichern:
    data_length = len(data[0, :])
    index = list(range(1, data_length+1))
    print("Anzahl Daten: " + str(data_length))
    print("\n Anzahl timedata: ", len(timedata_new))
    Textdatei = {"Header": "TU Berlin - Pruefstand Elektromotor ",
                 "Modul": "Modellbildung und Simulation mechatronischer Systeme",
                 "Spalteninhalt": "Index, Zeit[s], Spannung[V], ..."}

    with open("USB6009_Messung.txt", "w") as f:
        f.write(Textdatei["Header"]+"\n"+Textdatei["Modul"]+"\n")
        f.write("Created On %s\n\n" % datetime.datetime.now())
        f.write(Textdatei["Spalteninhalt"] + "\n")
        for i in range(0, data_length, 1):
            f.write("%s" % index[i])
            f.write(", %s" % timedata_new[i])
            f.write(", %s" % data[0, i])
            if len(Kanäle) == 2:
                f.write(", %s\n" % data[1, i])
            elif len(Kanäle) == 3:
                f.write(", %s" % data[1, i])
                f.write(", %s\n" % data[2, i])
            elif len(Kanäle) == 4:
                f.write(", %s" % data[1, i])
                f.write(", %s" % data[2, i])
                f.write(", %s\n" % data[3, i])
            elif len(Kanäle) == 5:
                f.write(", %s" % data[1, i])
                f.write(", %s" % data[2, i])
                f.write(", %s" % data[3, i])
                f.write(", %s\n" % data[4, i])
            else:
                f.write("\n")
        f.close()

    # Daten visualisieren:
    x_values = range(0, len(voltage))  # später mit Zeit ersetzen

    plt.subplot(2, 1, 1)
    plt.title('Spanungsverlauf Vorgabe')
    plt.plot(x_values, voltage, linestyle='--')
    plt.plot(x_values, voltage, 'ob')
    # xmin, xmax, ymin, ymax = 0, len(x_values), -0.5, 2.0
    # plt.axis([xmin, xmax, ymin, ymax])
    plt.xlabel('Zeit in s')
    plt.ylabel('Spannung in V')
    plt.grid(True)

    plt.subplot(2, 1, 2)
    plt.title('Gemessene Spannung')
    plt.plot(data[0, :])
    # ymin, ymax = -0.5, 2
    # plt.axis([0, Dauer*Samplerate_read, ymin, ymax])
    plt.xlabel('Zeit in s')
    plt.ylabel('Spannung in V')
    plt.grid(True)

    plt.tight_layout()  # damit Beschriftungen nicht überlappen
    plt.show()

elif mode == 5:
    # mode 5: TEST

    print("Testmodus")
    repeat_num = 5000
    # data = np.array([np.tile([1, 0], repeat_num), np.tile(
    #                 [0, 1], repeat_num)], dtype=np.float64)
    # data = np.array([np.tile([1, 0], repeat_num)], dtype=np.float64)
    # array aneinanderkacheln und anschließend die einzelnen Werte einzeln wiederholen
    # data = np.array([np.repeat([np.tile([0,0], repeat_num)],1), np.repeat([np.tile([0,1], repeat_num)],1)], dtype=np.float64)

    duration = 10
    timedata = [0]
    index = [0]
    start_time = time.time()
    previous_time = 0
    for i in range(0, duration, 1):
        # while loop um Ausgabe von Spannungswerten Zeitgenau steuern zu können
        while time.time()-previous_time < 1.0:
            time.sleep(0.001)
        # 0.0005: Korrekturfaktor, noch nicht optimal um die Zeit genau messen zu können
        previous_time = time.time()-0.0005
        index.extend([i+1])
        timedata.extend([format(time.time()-start_time, '.3f')])

    # Zeit am Anfang oder Ende der Schleife speichern
    # Werte dazwichen interpolieren, z.B.: range(startwert, endwert, ((endwert-startwert)/samplerate_read)) (?)

    # Zeitstempel evtl nicht über time.time() erzeugen, sondern anhand von samplingrate brechnen und dann einfach die Werte den
    # entsprechenden Zeilen zuordnen. Zeitschritt = (1/samplingrate) -Y in jeder Zeile Zeitschritt * i oder ähnlich

    # print(timedata)
    # print("--- %s seconds ---" % (time.time() - start_time))
    # print("--- %.3f seconds ---" % (time.time() - start_time))

    Dauer = 6  # [s]
    Samplerate_read = 10  # [Hz]
    Samplerate_write = 2  # [Hz]

    data = np.array([index, timedata])
    data_length = len(data[0, :])

    Textdatei = {"Header": "TU Berlin - Pruefstand Elektromotor ",
                 "Modul": "Modellbildung und Simulation mechatronischer Systeme",
                 "Spalteninhalt": "Index, Zeit[s], Spannung[V], ..."}

    with open("testfile.txt", "w") as f:
        f.write(Textdatei["Header"]+"\n"+Textdatei["Modul"]+"\n")
        f.write("Created On %s\n\n" % datetime.datetime.now())
        f.write(
            "Messparameter: Dauer [s]: %s" % Dauer + "; Frequenz [Hz]: %s" % Samplerate_read + "\n\n")
        # , "; Frequenz (Messung) [Hz]: ",
        #         Samplerate_read, "; Frequenz (Ausgabe) [Hz]: ", Samplerate_write)
        f.write(Textdatei["Spalteninhalt"] + "\n")
        for i in range(0, data_length, 1):
            f.write("%s" % data[0, i])
            f.write(", %s\n" % data[1, i])
        f.close()

    print(datetime.datetime.now())

elif mode == 6:
    # mode 6: Messreihen aus Datei lesen (und anzeigen)
    print("Mode 6")

    # TODO: Testtext
    # Daten visualisieren
    # evtl. Bestimmte Dinge der Datei überprüfen (max. Value, min. Value, länge, ...)
    # (Parameter für Messung zunächst vorgeben)

    filename_web = "USB6009_Messung_TEST.txt"
    # filename_web = "testfile.txt"

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
        f.close()

    buffer_textfile = buffer_textfile[startline_data:len(buffer_textfile)]
    # print(buffer_textfile)
    print("Anzahl an Daten: ", len(buffer_textfile))

    # Daten in listen schreiben und zu float konvertieren. 2 Spalten in der Textdatei ergeben 2 Listen
    newlist_01 = []
    newlist_02 = []
    for word in buffer_textfile:
        word = word.split(",")
        if word[1][0] == ' ':
            word[1] = word[1][1:len(word[1])]
        newlist_01.append(word[0])
        newlist_02.append(word[1])

    # print("Liste 1: ", newlist_01)
    # print("Liste 2: ", newlist_02)

    newlist_01 = [float(i) for i in newlist_01]  # Konvertierung in float
    newlist_02 = [float(i) for i in newlist_02]
    # print("Liste 1 float: ", newlist_01)

    # Daten visualisieren:

    # x_values = range(0, len(newlist_01))  # später mit Zeit ersetzen
    # plt.plot(x_values, newlist_01, linestyle='--', label='Messreiehe 1')
    # plt.plot(x_values, newlist_01, 'ob')
    # plt.plot(newlist_01, newlist_02, linestyle='--', label='Messreiehe 2')
    plt.plot(newlist_01, newlist_02)

    # plt.plot(x_values, newlist_02, 'or')
    # xmin, xmax, ymin, ymax = 0, Dauer*Samplerate_read, -0.5, 2
    # xmin, xmax, ymin, ymax = 0, len(x_values), -0.5, 2.0
    # plt.axis([xmin, xmax, ymin, ymax])
    plt.xlabel('Zeit in s')
    plt.ylabel('Spannung in V')
    plt.grid(True)
    plt.show()


elif mode == 7:
        # mode 7: Spannungsverlauf zum testen erstellen
    print("Mode 7")
    nur_erstellen = True
    # nur_erstellen = False

    if nur_erstellen:

        # Dauer = 1000
        # Array mit 50 Einträgen:
        # voltage_np = np.array([np.repeat([0.0, 1.0, 1.1, 1.2, 1.3, 1.4,
        #                                   1.5, 1.6, 1.7, 0.0], Dauer)],
        #                       dtype=np.float64)

            # Sinusverlauf
        # sample = 1000
        # x = np.arange(sample)
        # data_ao_buffer = np.sin(1 * np.pi * 2 * x / 1000) + 1
        # data_AO = np.array([np.tile(data_ao_buffer, 1000)], dtype=np.float64)

        # Array mit 500 Einträgen:
        voltage_np = np.array([], dtype=np.float64)
        value = 0
        # 10s Anstieg bis 2 V
        while value < 2.0:
            value = value + (2/(500*10))  # 2V, 500 Hz, 10 Sekunden
            voltage_np = np.append(voltage_np, value)
        # 2 V für 20 Sekunden halten
        value = np.array([np.repeat([2.0], (20*500))],
                         dtype=np.float64)  # 20 Sekunden bei 500 Hz
        voltage_np = np.append(voltage_np, value)
        # 10s Anstieg von 2V auf 3V
        value = voltage_np[-1]
        while value < 3.0:
            value = value + (1/(500*10))  # 1V, 500 Hz, 10 Sekunden
            voltage_np = np.append(voltage_np, value)
        # 3 V 20 Sekunden halten
        value = np.array([np.repeat([3.0], (20*500))],
                         dtype=np.float64)  # 20 Sekunden bei 500 Hz
        voltage_np = np.append(voltage_np, value)
        # Abnahme bis 0V in 30 Sekunden
        value = voltage_np[-1]
        while value > 0:
            value = value - (3/(500*30))
            voltage_np = np.append(voltage_np, value)

        # for i in range(0, 10000, 1):
        #     value = value + 0.002
        #     voltage_np = np.append(voltage_np, value)
        # voltage_np = np.array([np.tile(voltage_np, Dauer)])
        # voltage_np[0, -1] = 0.0

        np.savetxt("Spannungsvorgabe.txt", voltage_np,
                   fmt="%.3f", delimiter='\n')

        # print("Array erzeugt mit der Länge: ", len(voltage_np[0, :])) # numpy
        print("Array erzeugt mit der Länge: ", len(voltage_np))  # list

        plt.plot(voltage_np)
        plt.xlabel('Datenpunkte')
        plt.ylabel('Spannung in V')
        plt.grid(True)
        plt.show()

        # Variante mit Python list:
        # voltage = [0.0, 1.0, 1.1, 1.2, 1.3, 1.4,
        #            1.5, 1.6, 1.7, 0.0]
        # with open("Spannungsvorgabe.txt", "w") as f:
        #     for i in range(0, len(voltage), 1):
        #         f.write("%s\n" % str(voltage[i]))
        #     f.close()

    # Test um zu überprüfen, ob Daten richtig geschrieben wurden:
    else:
        filename_web = "Spannungsvorgabe.txt"

        # Dateien im Ordner auflisten:
        mypath = os.listdir()
        for i in range(0, len(mypath)):
            if filename_web == mypath[i]:
                filename = mypath[i]

        # Datei auslesen und nur Daten ohne Header verwenden:
        print("Folgende Datei wird geöffnet: ", filename)
        with open(filename, "r") as f:
            buffer_textfile = f.read().splitlines()
            f.close()

        print(buffer_textfile)
        voltage = [float(i) for i in buffer_textfile]  # Konvertierung in float
        print(voltage)
        print("Vorgegebene Daten: Anzahl: ", len(voltage),
              "; Max. Value: ", max(voltage), "; min. Value: ", min(voltage))

        # # Daten visualisieren:
        x_values = range(0, len(voltage))  # später mit Zeit ersetzen

        plt.subplot(2, 1, 1)
        plt.title('Spanungsverlauf Vorgabe')
        plt.plot(x_values, voltage, linestyle='--', label='Messreiehe 1')
        plt.plot(x_values, voltage, 'ob')
        xmin, xmax, ymin, ymax = 0, len(x_values), -0.5, 2.0
        plt.axis([xmin, xmax, ymin, ymax])
        plt.xlabel('Zeit in s')
        plt.ylabel('Spannung in V')
        plt.grid(True)

        plt.subplot(2, 1, 2)
        plt.title('Gemessene Spannung')
        plt.plot(x_values, voltage, 'r')
        plt.xlabel('Zeit in s')
        plt.ylabel('Spannung in V')
        plt.grid(True)

        plt.tight_layout()  # damit Beschriftungen nicht überlappen
        plt.show()

elif mode == 8:
    # mode 8: Funktion dataReadAndWrite
    print("Mode 8")
    # TODO FUnktionen usw. auf 5 Kanäle anpassen (Channels, Textdatei, plots, ...)

    # Datei die ausgelesen werden soll
    filename_web = "Spannungsvorgabe.txt"

    # Parameter
    Samplerate_read = 2000  # [Hz] -> Muss immer vielfaches von 'write' sein
    Samplerate_write = 500  # [Hz] -> muss gleich wie in 'Ersteller'-Datei sein
    Channels = [0, 1, 2, 3, 6]  # TODO mit anderen Kanälen überprüfen

    # TODO verschiedene Amplituden für verschiedene Kanäle verwenden
    # TODO verschiedene Auflösungen (resolution) für verschiedene Kanäle verwenden

    # Spannungsvorgabe
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

    data_AO = [float(i) for i in buffer_textfile]  # Konvertierung in float
    Dauer = (len(data_AO)/Samplerate_write)
    # Dauer = 20  # [s]

    SamplesPerChunk = int(Samplerate_read/Samplerate_write)
    samples = int(Samplerate_read*Dauer)
    chunks = math.ceil(samples/SamplesPerChunk)

    print("Anzahl an Chunks: ", chunks, ";    Anzahl Samples insgesamt: ",
          samples, ";    Ausgabefrequenz [Hz]: ", (chunks/Dauer), ";    Dauer [s]: ", Dauer)

    # +++++++++++++++++++++++    MAIN    ++++++++++++++++++++++++++++++++++++++
    measurement = mdt_custom.dataReadAndWrite(amplitude=10.0, samplingRate=Samplerate_read, duration=Dauer,
                                              channels=Channels, resolution=13, outType='Volt', samplesPerChunk=SamplesPerChunk, data_ao=data_AO)
    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    print("Anzahl Daten ausgelesen (pro Kanal): ", len(measurement[0]))

    # Zeit: verschiedene Methoden möglich:
    # 1: Nach Messung einfach "berechnen" anhand der eingestellten Parameter (nicht wirklich real gemessen)
    # 2: In Schleife Zeit in array schreiben (nicht für jeden Datenpunkt möglich, da immer viele Samples auf einmal gelesenw werden in einer Funktion)
    time_values = np.arange(0, Dauer, (1/Samplerate_read))

    # Daten abspeichern
    data_length = len(measurement[0, :])
    index = list(range(1, data_length+1))
    Textdatei = {"Header": "TU Berlin - Pruefstand Scheibenlaeufer",
                 "Modul": "Modellbildung und Simulation mechatronischer Systeme",
                 "Spalteninhalt": "Index, Zeit[s], Spg. Tachometer[V], Spg. Generator[V], Spg. Motor[V], Spg. Strommessung[V]"}
    num_of_chans = len(Channels)
    with open("USB6009-Messung.txt", "w") as f:
        f.write(Textdatei["Header"]+"\n"+Textdatei["Modul"]+"\n")
        f.write("Created On {}\n\n" .format(datetime.datetime.now()))
        f.write("Anzahl an Chunks: {}; Anzahl Samples insgesamt: {}; Abtastfrequenz[Hz]: {}; Ausgabefrequenz[Hz]: {}; Dauer[s]: {} \n\n" .format(
            chunks, samples, Samplerate_read, (chunks/Dauer), Dauer))
        f.write(Textdatei["Spalteninhalt"] + "\n")
        for i in range(0, data_length, 1):
            f.write("{}" .format(index[i]))
            f.write(", {:.4f}" .format(time_values[i]))
            f.write(", {:.4f}" .format(measurement[0, i]))
            if num_of_chans >= 2:
                f.write(", {:.4f}" .format(measurement[1, i]))
            if num_of_chans >= 3:
                f.write(", {:.4f}" .format(measurement[2, i]))
            if num_of_chans >= 4:
                f.write(", {:.4f}" .format(measurement[3, i]))
            if num_of_chans >= 5:
                f.write(", {:.4f}" .format(measurement[4, i]))
            f.write("\n")
        f.close()

    # Visualisierung - alle Spannungsverläufe
    plt.subplot(2, 3, 1)
    plt.title('Spannung Tachometer')
    plt.plot(time_values, measurement[0, :])
    plt.xlabel('Zeit in s')
    plt.ylabel('Spannung in V')
    plt.grid(True)
    plt.subplot(2, 3, 2)
    plt.title('Spannung Generator')
    plt.plot(time_values, measurement[1, :])
    plt.xlabel('Zeit in s')
    plt.ylabel('Spannung in V')
    plt.grid(True)
    plt.subplot(2, 3, 3)
    plt.title('Spannung Ansteuerung Motor')
    plt.plot(time_values, measurement[2, :])
    plt.xlabel('Zeit in s')
    plt.ylabel('Spannung in V')
    plt.grid(True)
    plt.subplot(2, 3, 4)
    plt.title('Spannung Strommessung')
    plt.plot(time_values, measurement[3, :])
    plt.xlabel('Zeit in s')
    plt.ylabel('Spannung in V')
    plt.grid(True)
    plt.subplot(2, 3, 5)
    plt.title('Spannung Kanal 6')
    plt.plot(time_values, measurement[4, :])
    plt.xlabel('Zeit in s')
    plt.ylabel('Spannung in V')
    plt.grid(True)
    plt.tight_layout()  # damit Beschriftungen nicht überlappen
    # plt.savefig("USB6009_Messung.pdf", bbox_inches='tight')  # pdf speichern
    plt.show()

    # Visualisierung
    # plt.subplot(2, 1, 1)
    # plt.title('Spanungsverlauf - Vorgabe')
    # plt.plot(data_AO[0, 0:(Dauer*Samplerate_write)], linestyle='--')
    # # plt.plot(data_AO[0, 0:(Dauer*Samplerate_read)], 'ob')
    # # xmin, xmax, ymin, ymax = 0, len(x_values), -0.5, 2.0
    # # plt.axis([xmin, xmax, ymin, ymax])
    # plt.xlabel('Zeit in s')
    # plt.ylabel('Spannung in V')
    # plt.grid(True)

    # plt.subplot(2, 1, 2)
    # plt.title('Gemessene Spannung')
    # plt.plot(time_values, measurement[0, :])
    # # ymin, ymax = -0.5, 2
    # # plt.axis([0, Dauer*Samplerate_read, ymin, ymax])
    # plt.xlabel('Zeit in s')
    # plt.ylabel('Spannung in V')
    # plt.grid(True)

    # plt.tight_layout()  # damit Beschriftungen nicht überlappen
    # plt.savefig("Graph.pdf", bbox_inches='tight')  # pdf speichern
    # plt.show()

elif mode == 9:
    # mode 9: Digitalen Ausgang ansteuern
    output = mdt_custom.digital_output()
    print("Output: ", output)

else:
    print("Bitte korrekten Modus auswählen")

    # Fs = 250
    # f = 2
    # sample = 250
    # x = np.arange(sample)
    # y = np.sin(1 * np.pi * f * x / Fs) + 1
    # voltage = np.array([np.tile(y,10)], dtype=np.float64)
    # print("Länge array voltage: ", len(voltage[0]), ";    Länge y: ", len(y))
    # # data_ao = np.array([np.tile([0.0, 1.0, 1.1, 1.2, 1.3, 1.4,
    #     #                             1.5, 1.6, 1.7, 0.0], 1000)],
    #     #                       dtype=np.float64)
    # plt.plot(voltage[0])
    # # plt.plot(x, y)
    # plt.xlabel('sample(n)')
    # plt.ylabel('voltage(V)')
    # plt.show()

    # test_str = ['StringZumTesten', 'ZweiterString']
    # test_str2 = ['DritterString', 'VierterString']
    # print(test_str)
    # # print('%.3s' % test_str)
    # print('{0:.2s}' .format(test_str[0]))
    # print('{0[0]:.4s}' .format(test_str))
    # print('{0[1]:.4s}' .format(test_str))
    # print('{0[1]:.6s}; {1[1]}' .format(test_str, test_str2))
    # print("Array erzeugt mit der Länge: ", len(voltage_np[0, :]))

    sample = 1000
    x = np.arange(sample)
    data_ao_buffer = np.sin(1 * np.pi * 2 * x / 1000) + 1
    data_AO = np.array([np.tile(data_ao_buffer, 1000)], dtype=np.float64)
    voltage = [0.0, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 0.0]
    print(voltage)
    print("Länge Numpy array: ", len(data_AO),
          ';    Länge list: ', len(voltage))
