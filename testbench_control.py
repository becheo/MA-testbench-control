"""
@author: Oliver Becher
Steuerung Prüfstand
Masterarbeit: Entwicklung eines vernetzten Prüftands zur web-basierten
              Validierung und Parametrierung von Simulationsmodellen
"""

import time  # built-in modules
import datetime
import os
import sys
import math
import decimal

import matplotlib.pyplot as plt  # third-party modules
import numpy as np
import pandas

import mdt_custom  # local modules
import config as cfg
import testbench_helpers as hlp


def run_testbench(filename):
    """
    Function to perform a test while taking measurements. The results are stored
    in a csv file which will be shown on the website.
    """

    # Parameter
    Samplerate_read = 2000  # [Hz] -> Muss immer vielfaches von 'write' sein
    Samplerate_write = 250  # [Hz] -> muss gleich wie in 'Ersteller'-Datei sein
    Channels = [0, 1, 2, 3, 6]

    filepath = cfg.folder_upload + '/' + filename

    # read out csv file
    data = pandas.read_csv(filepath)
    data_AO = data['voltage'].tolist()

    duration = (len(data_AO)/Samplerate_write)

    SamplesPerChunk = int(Samplerate_read/Samplerate_write)
    samples = int(Samplerate_read*duration)
    chunks = math.ceil(samples/SamplesPerChunk)

    print("Anzahl an Chunks: ", chunks, ";    Anzahl Samples insgesamt: ",
          samples, ";    Ausgabefrequenz [Hz]: ", (chunks/duration), ";    Dauer [s]: ", duration)

    for i in range(10):
        hlp.status_led('blue')
        time.sleep(0.5)
        hlp.status_led('off')
        time.sleep(0.5)

    hlp.status_led('red')

    # +++++++++++++++++++++++    MAIN    ++++++++++++++++++++++++++++++++++++++
    measurement = mdt_custom.dataReadAndWrite(amplitude=10.0, samplingRate=Samplerate_read, duration=duration,
                                              channels=Channels, resolution=13, outType='Volt', samplesPerChunk=SamplesPerChunk, data_ao=data_AO)
    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    print("Anzahl Daten ausgelesen (pro Kanal): ", len(measurement[0]))

    time_values = np.arange(0, duration, (1/Samplerate_read))

    # Calculation of data out of voltage values
    rpm = hlp.calculate_rpm(measurement[0])
    current = hlp.calculate_current(measurement[3])
    temp = hlp.calculate_temperature(measurement[4])
    motor_voltage = hlp.calculate_motor_voltage(measurement[2], measurement[3])

    # save results to file
    result_path = cfg.folder_results + '/' + 'results-' + filename

    data_length = len(measurement[0, :])
    index = list(range(1, data_length+1))
    Textdatei = {"Header": "TU Berlin - Pruefstand Scheibenlaeufer",
                 "Modul": "Modellbildung und Simulation mechatronischer Systeme",
                 "Spalteninhalt": "Index,Zeit[s],Drehzahl[1/min],Generatorspannung[V],Motorspannung[V],Strommessung[A],Temperatur[C]"}
    num_of_chans = len(Channels)

    with open(result_path, "w") as f:
        f.write(Textdatei["Spalteninhalt"] + "\n")
        for i in range(0, data_length, 1):
            f.write("{}" .format(index[i]))
            f.write(", {:.4f}" .format(time_values[i]))
            f.write(", {:.4f}" .format(rpm[i]))
            if num_of_chans >= 2:
                f.write(", {:.4f}" .format(measurement[1, i]))
            if num_of_chans >= 3:
                f.write(", {:.4f}" .format(motor_voltage[i]))
            if num_of_chans >= 4:
                f.write(", {:.4f}" .format(current[i]))
            if num_of_chans >= 5:
                f.write(", {:.4f}" .format(temp[i]))
            f.write("\n")
        f.close()

        hlp.status_led('green')

    # Visualisierung - alle Spannungsverläufe
    if __name__ == "__main__":
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
        plt.title('Spannung Temperaturmessung')
        plt.plot(time_values, measurement[4, :])
        plt.axis([0, duration, 0, 5])
        plt.xlabel('Zeit in s')
        plt.ylabel('Spannung in V')
        plt.grid(True)
        plt.tight_layout()  # damit Beschriftungen nicht überlappen
        # plt.savefig("USB6009_Messung.pdf", bbox_inches='tight')  # pdf speichern
        plt.show()
