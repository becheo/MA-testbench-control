# -*- coding: utf-8 -*-
"""
Created on Thu Feb 15 10:36:14 2018

@author: Hauke Brunken
"""

import nidaqmx
import nidaqmx.stream_readers
import nidaqmx.system
system = nidaqmx.system.System.local()
import numpy as np
import math
import sounddevice as sd
from scipy.fftpack import fft
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

def playSound(sound, fs):
    sd.play(sound/10, fs)

def spectrum(Messwerte, Abtastrate): 
	#Berechnung des Spektrums
	N=len(Messwerte)# Anzahl der Messwerte
	u_cmplx=fft(Messwerte) #Berechnung der FFT
	u_abs=np.abs(u_cmplx[0:N//2])/N #Berechnung der relevanten Beträge bis fs/2
	u_abs[1:] *= 2
	f=np.linspace(0,Abtastrate//2,N//2)# Erstellung des sich ergebenden Frequenzvektors
	#Rueckgabe
	return (f,u_abs)

def dataRead(**kwargs):
#    continues = True
#    continues = False
    samplesPerChunk = 256
    argListMust = {'amplitude', 'samplingRate', 'duration', 'channels', 'resolution', 'outType'}
    argList = {'amplitude', 'samplingRate', 'duration', 'channels', 'resolution', 'outType', 'continues'}
    for key in kwargs:
        if key not in argList:
            print('Folgende Argumente müssen übergeben werden: amplitude=[V], samplingRate=[Hz], duration=[s], channels=[[,]], resolution=[bits], outType=\'volt\' oder \'codes\')')
            return None
    for key in argListMust:
        if key not in kwargs:
            print('Folgende Argumente müssen übergeben werden: amplitude=[V], samplingRate=[Hz], duration=[s], channels=[[,]], resolution=[bits], outType=\'volt\' oder \'codes\')')
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
            chan = task.ai_channels.add_ai_voltage_chan(ai, min_val=-abs(amplitude), max_val=abs(amplitude))
            if resolution < 1 or resolution > chan.ai_resolution:
                print(f'Die Auflösung muss zwischen 1 und {chan.ai_resolution:1.0f} Bit liegen')
                return None
        
        if samplingRate > task.timing.samp_clk_max_rate:
            print(f'Mit dieser Kanalanzahl beträgt die höchste Abtastrate {task.timing.samp_clk_max_rate:1.0f} Hz:')
            return None
        else:
            if continues:
                task.timing.cfg_samp_clk_timing(samplingRate, sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS)
            else:
                task.timing.cfg_samp_clk_timing(samplingRate, samps_per_chan=samples)
        
        stream = task.in_stream
        chunks = math.ceil(samples/samplesPerChunk)
        analogMultiChannelReader = nidaqmx.stream_readers.AnalogMultiChannelReader(stream)
        
        if continues:
            if samplingRate > 100:
                print('In der Liveansicht ist die samplingRate auf 100 Hz begrenzt.')
                return None
            fig, ax = plt.subplots()
            closed = [False]
            def handle_close(event,closed):
                closed[0] = True
            fig.canvas.mpl_connect('close_event', lambda event: handle_close(event, closed))
            xdata, ydata = np.arange(100)/samplingRate, np.ones( (100,len(channels)))*np.nan
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
            val = np.zeros((len(channels),1))
            frame = 0
            try:
                while(not closed[0]):
                    analogMultiChannelReader.read_one_sample(val[:,0])
                    vals = np.fmax(val,-amplitude)
                    vals = np.fmin(vals,amplitude)
                    vals = np.digitize(vals,bins)
                    if outtType == 'Volt':
                        vals = vals*u_lsb-amplitude
                    ydata[frame,:] = vals.ravel()
                    for i,ln in enumerate(lns):
                        ln.set_data(xdata, ydata[:,i])
#                    for i,pt in enumerate(pts):
#                        pt.set_data(frame, vals[i,0])
                    fig.canvas.restore_region(bg_cache)
                    for ln in lns:
                        ln.axes.draw_artist(ln)
#                    for pt in pts:
#                        pt.axes.draw_artist(pt)
                    ax.figure.canvas.blit(ax.bbox)
                    fig.canvas.start_event_loop(0.001)#1/samplingRate*0.5)
                    frame = (frame+1)%100
            except KeyboardInterrupt:
                pass
            

            task.stop()
            plt.close(fig)
            data = True
        else:
            data = np.zeros( (len(channels),samples))
            dataChunk = np.zeros( (len(channels),samplesPerChunk))
            lastDataChunk = np.zeros( (len(channels),samples%samplesPerChunk))
            
            samplesLeft = samples
            for i in range(chunks):
                if samplesLeft >= samplesPerChunk:
                    analogMultiChannelReader.read_many_sample(dataChunk, samplesPerChunk)
                    data[:,i*samplesPerChunk:i*samplesPerChunk+samplesPerChunk] = dataChunk
                else:
                    analogMultiChannelReader.read_many_sample(lastDataChunk, samplesLeft)
                    data[:,i*samplesPerChunk:i*samplesPerChunk+samplesLeft] = lastDataChunk
                samplesLeft -= samplesPerChunk
            task.stop()
            data[data>amplitude] = amplitude
            data[data<-amplitude] = -amplitude
            data = np.digitize(data,bins)
            if outtType == 'Volt':
                data = data*u_lsb-amplitude
    
            print(f"Die Messung wurde durchgeführt mit {dev.name:s} \n Messbereich: +/-{amplitude:1.2f} Volt\n samplingRate: {samplingRate:1.1f} Hz\n Messdauer: {duration:1.3f} s\n Auflösung: {resolution:d} bit\n Ausgabe in: {outtType:s}")

    return data