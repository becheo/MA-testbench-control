import time
# import os
import numpy as np
from scipy.interpolate import interp1d


# Temperaturmessung Variante 2: Interpolation aus Lookup-Table
arr_temp = [-55,    -50,    -45,    -40,    -35,    -30,    -25,    -20,
            -15,    -10,    -5,     0,      5,      10,     15,     20,
            25,	    30,     35,     40,     45,     50,	    55,     60,
            65,	    70,     75,     80,     85,     90,     95,     100,
            105,    110,    115,	120,    125,    130,    135,    140,
            145,	150,	155
            ]
arr_ntc = [121.46,	    84.439,	    59.243,	    1.938,	    29.947,
           21.567,      15.641,     11.466,	    8.451,	    6.2927,
           4.7077,      3.5563,	    2.7119,     2.086,	    1.6204,
           1.2683,      1,	        0.7942,     0.63268,	0.5074,
           0.41026,     0.33363,	0.27243,	0.2237,     0.18459,
           0.15305,	    0.12755,	0.10677,    0.089928,	0.076068,
           0.064524,	0.054941,	0.047003,   0.040358,	0.034743,
           0.030007,    0.026006,	0.022609,   0.01972,	0.017251,
           0.015139,	0.013321,   0.011754
           ]

# ntc_ratio = 0.79
# ntc_ratio = 2.2/2.5

U_Rt = 2.0  # measured value
R1 = 1000
U_supply = 2.5
Rt = (R1*(U_Rt/U_supply))/(1-(U_Rt/U_supply))
print("Rt: {}" .format(Rt))
ntc_ratio = Rt/10000
print("ntc-ratio {}" .format(ntc_ratio))

temp = np.interp(ntc_ratio, np.flip(arr_ntc), np.flip(arr_temp))
# temp = np.interp(ntc_ratio, arr_temp, arr_ntc)
print("Temperature: {}" .format(temp))

# Temperaturmessung Variante 1: Berechnung über Formel
# Rt = 10 * 0.63268
# R1 = 1  # kOhm
# Uv = 2.5

# voltage = 2.5 * (Rt/(R1+Rt))
# print("voltage {}" .format(voltage))
# ntc_resistance = (R1*(voltage/Uv))/(1-(voltage/Uv))
# print("Resistance NTC: {}" .format(ntc_resistance))
# ntc_ratio = ntc_resistance/10
# temperature = -21.14 * np.log(ntc_ratio) + 25.705

# print("Temperature at {} Volts: {}°C" .format(voltage, temperature))


# print(10/5)

# # check anz_samples_left vielfaches von 5000

# print(20 % 5)

# print(10 % 6)
# string_output = '#'
# string_blank = ' '
# duration = 10
# start_time = time.time()
# previous_time = 0
# for i in range(0, duration+1, 1):
#     while time.time()-previous_time < 1.0:
#         time.sleep(0.001)
#     previous_time = time.time()
#     print("{:.0f} Sekunden vergangen;    |{}{}|" .format(
#         time.time()-start_time, string_output*i, string_blank*(duration-i)), end='\r')


# print(os.path.getsize(file_name)/1024+'KB / '+size+' KB downloaded!', end='\r')
