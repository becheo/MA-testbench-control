# -*- coding: utf-8 -*-
"""
Created on Thu Feb 15 17:59:51 2018

@author: Hauke Brunken
"""

import matplotlib.pyplot as plt
import numpy as np
import mdt


data = mdt.dataRead(amplitude=5.0, samplingRate=40000.0,
                    duration=1.0, channels=[3], resolution=14, outType='Volt')  # Beispielmessung


plt.plot(data[0])
mdt.playSound(data[0], 40000)
