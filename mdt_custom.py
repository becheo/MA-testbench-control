# -*- coding: utf-8 -*-
"""
Steuerung Prüfstand Scheibenläufermotor
Masterarbeit: Entwicklung eines vernetzten Prüfstands zur web-basierten
              Validierung und Parametrierung von Simulationsmodellen

Skript 'mdt.py' modifiziert für die Verwendung des Prüfstands

Orginalskript mit "dataRead"-Funktion:
Created on Thu Feb 15 10:36:14 2018

@author: Hauke Brunken
"""

import time  # built-in modules
import math

from matplotlib.animation import FuncAnimation  # third-party modules
import matplotlib.pyplot as plt
from scipy.fftpack import fft
import sounddevice as sd
import numpy as np
import nidaqmx
import nidaqmx.stream_readers
import nidaqmx.stream_writers
import nidaqmx.system
from nidaqmx.constants import SampleTimingType
from nidaqmx.constants import TerminalConfiguration
from nidaqmx.constants import DigitalDriveType
system = nidaqmx.system.System.local()


def playSound(sound, fs):
    sd.play(sound/10, fs)


def spectrum(Messwerte, Abtastrate):
    # Berechnung des Spektrums
    N = len(Messwerte)  # Anzahl der Messwerte
    u_cmplx = fft(Messwerte)  # Berechnung der FFT
    # Berechnung der relevanten Beträge bis fs/2
    u_abs = np.abs(u_cmplx[0:N//2])/N
    u_abs[1:] *= 2
    # Erstellung des sich ergebenden Frequenzvektors
    f = np.linspace(0, Abtastrate//2, N//2)
    # Rueckgabe
    return (f, u_abs)


def dataRead(**kwargs):
    #    continues = True
    #    continues = False
    samplesPerChunk = 256
    argListMust = {'amplitude', 'samplingRate',
                   'duration', 'channels', 'resolution', 'outType'}
    argList = {'amplitude', 'samplingRate', 'duration',
               'channels', 'resolution', 'outType', 'continues'}
    for key in kwargs:
        if key not in argList:
            print(
                'Folgende Argumente müssen übergeben werden: amplitude=[V], samplingRate=[Hz], duration=[s], channels=[[,]], resolution=[bits], outType=\'volt\' oder \'codes\')')
            return None
    for key in argListMust:
        if key not in kwargs:
            print(
                'Folgende Argumente müssen übergeben werden: amplitude=[V], samplingRate=[Hz], duration=[s], channels=[[,]], resolution=[bits], outType=\'volt\' oder \'codes\')')
            return None
    amplitude = kwargs['amplitude']
    samplingRate = kwargs['samplingRate']
    duration = kwargs['duration']
    channels = kwargs['channels']
    resolution = kwargs['resolution']
    outType = kwargs['outType']
    if 'continues' not in kwargs.keys():
        continues = False
    else:
        continues = kwargs['continues']
        if type(continues) != bool:
            print('continues muss vom Typ bool sein')
            return None
    if not all(i < 4 for i in channels):
        print('Mögliche Kanäle sind 0 bis 4')
        return None
    if len(channels) > len(set(channels)):
        print('Kanäle dürfen nicht doppelt auftauchen')
        return None

    outtType = outType.capitalize()
    if outtType != 'Volt' and outtType != 'Codes':
        print(outtType)
        print('outType = \'Volt\' oder \'Codes\'')
        return None

    samples = int(samplingRate*duration)
    u_lsb = 2*amplitude/(2**resolution-1)
    bins = [-amplitude+u_lsb/2+u_lsb*i for i in range(2**resolution-1)]

    with nidaqmx.Task() as task:
        if len(system.devices) < 1:
            print('Es wurde keine Messkarte gefunden')
            return None
        dev = system.devices[0]

        if amplitude not in dev.ai_voltage_rngs:
            print('Unterstützt werden folgende Amplituden:')
            print(dev.ai_voltage_rngs[1::2])
            return None

        for channel in channels:
            ai = dev.ai_physical_chans.channel_names[channel]
            chan = task.ai_channels.add_ai_voltage_chan(
                ai, min_val=-abs(amplitude), max_val=abs(amplitude))
            if resolution < 1 or resolution > chan.ai_resolution:
                print(
                    f'Die Auflösung muss zwischen 1 und {chan.ai_resolution:1.0f} Bit liegen')
                return None

        if samplingRate > task.timing.samp_clk_max_rate:
            print(
                f'Mit dieser Kanalanzahl beträgt die höchste Abtastrate {task.timing.samp_clk_max_rate:1.0f} Hz:')
            return None
        else:
            if continues:
                task.timing.cfg_samp_clk_timing(
                    samplingRate, sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS)
            else:
                task.timing.cfg_samp_clk_timing(
                    samplingRate, samps_per_chan=samples)

        stream = task.in_stream
        chunks = math.ceil(samples/samplesPerChunk)
        analogMultiChannelReader = nidaqmx.stream_readers.AnalogMultiChannelReader(
            stream)

        if continues:
            if samplingRate > 100:
                print('In der Liveansicht ist die samplingRate auf 100 Hz begrenzt.')
                return None
            fig, ax = plt.subplots()
            closed = [False]

            def handle_close(event, closed):
                closed[0] = True
            fig.canvas.mpl_connect(
                'close_event', lambda event: handle_close(event, closed))
            xdata, ydata = np.arange(
                100)/samplingRate, np.ones((100, len(channels)))*np.nan
            lns = plt.plot(xdata, ydata, '-', animated=True)
#            pts = [plt.plot(xdata[0], ydata[0,i],marker='o', animated=True)[0] for i in range(len(channels))]
            fig.legend(['Ch: {}'.format(ch) for ch in channels])
            ax.set_xlim(0, 100/samplingRate)
            if outtType == 'Codes':
                ax.set_ylim(-1, 2**resolution)
            elif outtType == 'Volt':
                ax.set_ylim(-amplitude*1.05, amplitude*1.05)
            plt.xlabel('Zeit in s')
            plt.ylabel('Spannung in {}'.format(outType))
            fig.canvas.draw()
            fig.canvas.start_event_loop(0.1)
            bg_cache = fig.canvas.copy_from_bbox(ax.bbox)
            task.start()
            val = np.zeros((len(channels), 1))
            frame = 0
            try:
                while(not closed[0]):
                    analogMultiChannelReader.read_one_sample(val[:, 0])
                    vals = np.fmax(val, -amplitude)
                    vals = np.fmin(vals, amplitude)
                    vals = np.digitize(vals, bins)
                    if outtType == 'Volt':
                        vals = vals*u_lsb-amplitude
                    ydata[frame, :] = vals.ravel()
                    for i, ln in enumerate(lns):
                        ln.set_data(xdata, ydata[:, i])
#                    for i,pt in enumerate(pts):
#                        pt.set_data(frame, vals[i,0])
                    fig.canvas.restore_region(bg_cache)
                    for ln in lns:
                        ln.axes.draw_artist(ln)
#                    for pt in pts:
#                        pt.axes.draw_artist(pt)
                    ax.figure.canvas.blit(ax.bbox)
                    fig.canvas.start_event_loop(0.001)  # 1/samplingRate*0.5)
                    frame = (frame+1) % 100
            except KeyboardInterrupt:
                pass

            task.stop()
            plt.close(fig)
            data = True
        else:
            data = np.zeros((len(channels), samples))
            dataChunk = np.zeros((len(channels), samplesPerChunk))
            lastDataChunk = np.zeros(
                (len(channels), samples % samplesPerChunk))

            samplesLeft = samples
            for i in range(chunks):
                if samplesLeft >= samplesPerChunk:
                    analogMultiChannelReader.read_many_sample(
                        dataChunk, samplesPerChunk)
                    data[:, i*samplesPerChunk:i*samplesPerChunk +
                         samplesPerChunk] = dataChunk
                else:
                    analogMultiChannelReader.read_many_sample(
                        lastDataChunk, samplesLeft)
                    data[:, i*samplesPerChunk:i*samplesPerChunk +
                         samplesLeft] = lastDataChunk
                samplesLeft -= samplesPerChunk
            task.stop()
            data[data > amplitude] = amplitude
            data[data < -amplitude] = -amplitude
            data = np.digitize(data, bins)
            if outtType == 'Volt':
                data = data*u_lsb-amplitude

            # print(
            #     f"Die Messung wurde durchgeführt mit {dev.name:s} \n Messbereich: +/-{amplitude:1.2f} Volt\n samplingRate: {samplingRate:1.1f} Hz\n Messdauer: {duration:1.3f} s\n Auflösung: {resolution:d} bit\n Ausgabe in: {outtType:s}")

    return data


def dataWrite(voltage, channels, duration, samplingRate, mode):
    """Schreibt Daten auf einen analogen Ausgang der Messkarte.

    Auswahl zwischen einem Wert (Sprung) oder beliebigem Verlauf von Werten.
    Achtung: vorgegebener Verlauf nur soweit möglich wie von der E-Maschine umsetzbar
    Funktion zum Testen von Funktionen mit dem USB6009. Wird nur in Verbindung
    mit 'testbench_control_all.py' verwendet.
    """
    with nidaqmx.Task() as task:
        dev = system.devices[0]

        if mode == 3:
            # write one sample:

            ao = dev.ao_physical_chans.channel_names[0]
            chan_output = task.ao_channels.add_ao_voltage_chan(
                ao, min_val=0, max_val=5)
            data = voltage

            stream = task.out_stream
            analogSingleChannelWriter = nidaqmx.stream_writers.AnalogSingleChannelWriter(
                stream)
            analogSingleChannelWriter.write_one_sample(data)
        else:
            # write multiple samples:

            for channel in channels:
                ao = dev.ao_physical_chans.channel_names[channel]
                chan_output = task.ao_channels.add_ao_voltage_chan(
                    ao, min_val=0, max_val=5)

            samples = int(samplingRate*duration)
            stream = task.out_stream

            task.timing.cfg_samp_clk_timing(samplingRate)

            tile_num = 10
            repeat_num = 1000

            data = np.array([np.repeat([np.tile([0, 1], tile_num)], repeat_num),
                             np.repeat([np.tile([0, 0], tile_num)], repeat_num)], dtype=np.float64)

            task.start()
            analogMultiChannelWriter = nidaqmx.stream_writers.AnalogMultiChannelWriter(
                stream)
            analogMultiChannelWriter.write_many_sample(data)
            task.wait_until_done(timeout=30)
            task.stop()

    return chan_output


def dataReadAndWrite(**kwargs):
    """Reads and writes data with analog in- and output.

    Notice that voltage levels are bounded to capabilites of device (0 to 5V).

    Parameters:
        amplitude:        voltage amplitude to be measured.
        samplingRate:     Samplerate in Hz.
        duration:         Duration of the test that is going to be performed.
        channels:         Channels of USB6009 that should be measured during test.
        resolution:       Resolution for voltage measurement.
        outType:          Unit for output.
        samplesPerChunk:  Number of samples in one chunk of data.
        data_ao:          Data array for analog output.

    Returns:
        data: array of measured voltage data.
    """
    #    continues = True
    #    continues = False
    # samplesPerChunk = 256
    argListMust = {'amplitude', 'samplingRate',
                   'duration', 'channels', 'resolution', 'outType', 'samplesPerChunk', 'data_ao'}
    argList = {'amplitude', 'samplingRate', 'duration',
               'channels', 'resolution', 'outType', 'continues', 'samplesPerChunk', 'data_ao'}
    for key in kwargs:
        if key not in argList:
            print(
                'Folgende Argumente müssen übergeben werden: amplitude=[V], samplingRate=[Hz], duration=[s], channels=[[,]], resolution=[bits], outType=\'volt\' oder \'codes\') ,samplesPerChunk')
            return None
    for key in argListMust:
        if key not in kwargs:
            print(
                'Folgende Argumente müssen übergeben werden: amplitude=[V], samplingRate=[Hz], duration=[s], channels=[[,]], resolution=[bits], outType=\'volt\' oder \'codes\') ,samplesPerChunk')
            return None
    amplitude = kwargs['amplitude']
    samplingRate = kwargs['samplingRate']
    duration = kwargs['duration']
    channels = kwargs['channels']
    resolution = kwargs['resolution']
    outType = kwargs['outType']
    samplesPerChunk = kwargs['samplesPerChunk']
    data_ao = kwargs['data_ao']

    if 'continues' not in kwargs.keys():
        continues = False
    else:
        continues = kwargs['continues']
        if type(continues) != bool:
            print('continues muss vom Typ bool sein')
            return None

    if not all(i < 8 for i in channels):
        print('Mögliche Kanäle sind 0 bis 4')
        return None
    if len(channels) > len(set(channels)):
        print('Kanäle dürfen nicht doppelt auftauchen')
        return None

    outtType = outType.capitalize()
    if outtType != 'Volt' and outtType != 'Codes':
        print(outtType)
        print('outType = \'Volt\' oder \'Codes\'')
        return None

    samples = int(samplingRate*duration)
    u_lsb = 2*amplitude/(2**resolution-1)
    bins = [-amplitude+u_lsb/2+u_lsb*i for i in range(2**resolution-1)]

    with nidaqmx.Task() as task_ai, nidaqmx.Task() as task_ao:
        if len(system.devices) < 1:
            print('Es wurde keine Messkarte gefunden')
            return None
        dev = system.devices[0]

        if amplitude not in dev.ai_voltage_rngs:
            print('Unterstützt werden folgende Amplituden:')
            print(dev.ai_voltage_rngs[1::2])
            return None

        for channel in channels:
            ai = dev.ai_physical_chans.channel_names[channel]
            if channel == 2 or channel == 6:  # Channels that take measurements to same GND
                chan = task_ai.ai_channels.add_ai_voltage_chan(
                    ai, min_val=-abs(amplitude), max_val=abs(amplitude), terminal_config=TerminalConfiguration.RSE)
            else:
                chan = task_ai.ai_channels.add_ai_voltage_chan(
                    ai, min_val=-abs(amplitude), max_val=abs(amplitude), terminal_config=TerminalConfiguration.DIFFERENTIAL)
            # print("Kanal: {}, Einstellung Messung: {}" .format(
                # chan, chan.ai_term_cfg))
            if resolution < 1 or resolution > chan.ai_resolution:
                print(
                    f'Die Auflösung muss zwischen 1 und {chan.ai_resolution:1.0f} Bit liegen')
                return None

        if samplingRate > task_ai.timing.samp_clk_max_rate:
            print(
                f'Mit dieser Kanalanzahl beträgt die höchste Abtastrate {task_ai.timing.samp_clk_max_rate:1.0f} Hz:')
            return None
        else:
            task_ai.timing.cfg_samp_clk_timing(
                samplingRate, samps_per_chan=samples)

        stream_ai = task_ai.in_stream
        chunks = math.ceil(samples/samplesPerChunk)
        analogMultiChannelReader = nidaqmx.stream_readers.AnalogMultiChannelReader(
            stream_ai)

        data = np.zeros((len(channels), samples))
        dataChunk = np.zeros((len(channels), samplesPerChunk))
        lastDataChunk = np.zeros(
            (len(channels), samples % samplesPerChunk))

        # Prepare data output:
        # Channel 0: analog output channel
        ao = dev.ao_physical_chans.channel_names[0]
        task_ao.ao_channels.add_ao_voltage_chan(
            ao, min_val=0, max_val=5)
        stream_ao = task_ao.out_stream
        analogSingleChannelWriter = nidaqmx.stream_writers.AnalogSingleChannelWriter(
            stream_ao)

        samplesLeft = samples
        start_time = time.time()
        for i in range(chunks):
            if len(data_ao) == 1:  # for testing purposes (write one sample)
                analogSingleChannelWriter.write_one_sample(
                    data_ao[0, i])  # Numpy
            else:
                analogSingleChannelWriter.write_one_sample(
                    data_ao[i])  # analog output

            if samplesLeft >= samplesPerChunk:
                analogMultiChannelReader.read_many_sample(
                    dataChunk, samplesPerChunk)
                data[:, i*samplesPerChunk:i*samplesPerChunk +
                     samplesPerChunk] = dataChunk
            else:
                analogMultiChannelReader.read_many_sample(
                    lastDataChunk, samplesLeft)
                data[:, i*samplesPerChunk:i*samplesPerChunk +
                     samplesLeft] = lastDataChunk
            samplesLeft -= samplesPerChunk

            # Text output with 5 measurements taken:
            print("Messdauer [s]: {:.0f};  Motorspannung [V]: {:.3f};  Spannung analoger Ausgang [V]: {:.3f};  Drehzahl [1/min]: {:.0f}" .format(
                time.time()-start_time, data[2][i*samplesPerChunk], data_ao[i], ((data[0][i*samplesPerChunk])/4.3)*1000), end='\r')

        end_time = time.time() - start_time
        print("\nDauer der Messung: ", end_time)

        # After test is complete, set voltage to 0V to ensure the motor is
        # not running anymore
        analogSingleChannelWriter.write_one_sample(0.0)

        # task_ao.stop()
        task_ai.stop()
        data[data > amplitude] = amplitude
        data[data < -amplitude] = -amplitude
        data = np.digitize(data, bins)
        if outtType == 'Volt':
            data = data*u_lsb-amplitude

    return data


def digital_output(channel_name, voltage_level):
    """Control the digital output from USB6009

    Use this function to control the digital output via nidaqmx on USB6009. The
    digital outputs can be used to control LEDs. Even though high voltage is 5 V
    (open collector, inital state when connecting USB6009 via USB), when set as
    active drive the voltage is set to be 3.5 V only. For further information
    refer to USB6009 manual and specification sheet.

    Parameters:
        channel_name (str): The name of channel to set. Name depends on the port
            and line that should be used. Typically looks similar to this:
            'Dev1/port0/line0'
        voltage_level (bool): 0 (Low: 0V, 0A) or 1 (High: 3.5V, 8.5mA)

    Returns:
        dev (str): currently active system device
    """

    with nidaqmx.Task() as task:

        dev = system.devices[0]
        chan = task.do_channels.add_do_chan(channel_name)

        # configure channel as active drive to be able to power LEDs
        chan.do_output_drive_type = DigitalDriveType.ACTIVE_DRIVE

        stream = task.out_stream
        digital_single_channel_writer = nidaqmx.stream_writers.DigitalSingleChannelWriter(
            stream)

        # High: 5V (open-collector), 3,5V (active drive); Low = 0V
        digital_single_channel_writer.write_one_sample_one_line(voltage_level)
        task.stop()

    return dev
