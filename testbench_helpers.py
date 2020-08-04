import time
# import os
import numpy as np
from scipy.interpolate import interp1d

import mdt_custom


def running_mean(x, N):
    cumsum = np.cumsum(np.insert(x, 0, 0))
    return (cumsum[N:] - cumsum[:-N]) / float(N)


def eliminate_negative_values(data):
    for i in range(len(data)):
        if data[i] < 0:
            data[i] = 0

    return data


def calculate_temperature(data):
    """Calculate temperature out of measured voltage at NTC.

    Parameters:
        data (array): data with voltage measured at NTC.

    Returns:
        temp (array): calculated temperature
    """

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

    R1 = 1000  # [Ohm]; resistor in series
    U_supply = 2.5  # [V]

    Rt_array = [(R1*(U_Rt/U_supply))/(1-(U_Rt/U_supply)) for U_Rt in data]

    # Rt = (R1*(U_Rt/U_supply))/(1-(U_Rt/U_supply))

    ntc_ratio_array = [Rt/10000 for Rt in Rt_array]

    temp = [np.interp(ntc_ratio, np.flip(arr_ntc), np.flip(arr_temp))
            for ntc_ratio in ntc_ratio_array]

    num_of_mean_values = 2000  # 2000 Hz -> 1 mean over 1 second
    temp = running_mean(temp, num_of_mean_values)

    return temp


def calculate_current(data):
    """Calculate Current out of measured voltage at shunt."""

    shunt = 1.2  # [Ohm]
    current = [(x/shunt) for x in data]

    return current


def calculate_rpm(data):
    """Calculate rpm[1/min] out of voltage from tachometer."""
    data_positives = eliminate_negative_values(data)

    rpm_generator = [(x/4.3)*1000 for x in data_positives]

    return rpm_generator


def calculate_motor_voltage(data, current_data):
    """Calculate real voltage from motor out of voltage divider."""

    R1 = 36  # [Ohm]
    R2 = 22  # [Ohm]

    real_voltage = [x*(R1+R2)/R2 for x in data]

    voltage_motor = np.array([], dtype=np.float64)
    for i in range(len(data)):
        voltage_buffer = real_voltage[i]-current_data[i]
        voltage_motor = np.append(voltage_motor, voltage_buffer)

    return voltage_motor


def illumination(status):
    """Turn on/off light to illuminate the testbench.

    Parameters:
        status (string): possible values: 'off', 'on'
    """

    if status == 'off':
        mdt_custom.digital_output('Dev1/port0/line0', 0)
        mdt_custom.digital_output('Dev1/port0/line1', 0)
        mdt_custom.digital_output('Dev1/port0/line2', 0)

    if status == 'on':
        mdt_custom.digital_output('Dev1/port0/line0', 1)
        mdt_custom.digital_output('Dev1/port0/line1', 1)
        mdt_custom.digital_output('Dev1/port0/line2', 1)


def status_led(status):
    """Set color of status LED.

    Parameters:
        status (string): possible values: 'off', 'green', 'red', 'blue'    
    """

    if status == 'off':
        mdt_custom.digital_output('Dev1/port0/line5', 0)
        mdt_custom.digital_output('Dev1/port0/line6', 0)
        mdt_custom.digital_output('Dev1/port0/line7', 0)

    if status == 'green':
        mdt_custom.digital_output('Dev1/port0/line5', 1)
        mdt_custom.digital_output('Dev1/port0/line6', 0)
        mdt_custom.digital_output('Dev1/port0/line7', 0)

    if status == 'red':
        mdt_custom.digital_output('Dev1/port0/line5', 0)
        mdt_custom.digital_output('Dev1/port0/line6', 1)
        mdt_custom.digital_output('Dev1/port0/line7', 0)

    if status == 'blue':
        mdt_custom.digital_output('Dev1/port0/line5', 0)
        mdt_custom.digital_output('Dev1/port0/line6', 0)
        mdt_custom.digital_output('Dev1/port0/line7', 1)


def init_leds():
    """"Initialization of Leds when program is started."""

    illumination('off')
    status_led('green')
