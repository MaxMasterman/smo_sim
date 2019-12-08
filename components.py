#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct  3 2019

@author: kristjan
"""

import numpy as np

class SIGNAL:
    
    def __init__(self, amplitude, frequency, offset=0):
        self.amplitude = amplitude
        self.period = 1/frequency
        self.offset = offset
        
    def rect(self, t):
        if (t % self.period) <= self.period/2:
            return self.amplitude + self.offset
        else:
            return -self.amplitude + self.offset
    
    def sin(self, t):
        return self.amplitude*(np.sin(2*np.pi*t/self.period)) + self.offset
    
class FLUID: # Klasse fürs Medium 
    
    def __init__(self):
        self.ethaD = 1*10**-3 # [Pa/s] dynamische Viskosität von Wasser @T=20°C
        self.Rgs = 1 # spezifische Gaskonstante Rgs
        self.rho = 0.9982067 # [g*cm^-3] Dichte Wasser @T=20°C
        self.T = 293 # K

class PUMP(FLUID):
    
    """ TUDOS pump from FH slides """
    def __init__(self):
        super().__init__()
        self.diameter = 5.7*10**-3 # m
        self.A = np.pi*((self.diameter)**2)/4
        
        self.Vmax = 240 # V operation voltage
        self.Vmin = -76 # V operation voltage
        self.VAmp = (abs(self.Vmax)+abs(self.Vmin))/2
        self.VOff = self.Vmax - self.VAmp
        
        
        self.zmax = 35*10**-6 # m ANNAHME
        self.zmin = -15*10**-6 # m ANNAHME
        self.zAmp = (abs(self.zmax)+abs(self.zmin))/2 # Amplituden-Berechnung
        self.zOff = self.zmax - self.zAmp # Offset-Berechnung
        
        
        self.Pmax = 50 # kPa back pressure air
        self.Pmin = -38 # kPa suction pressure air
        self.PAmp = (abs(self.Pmax)+abs(self.Pmin))/2
        self.POff = self.Pmax - self.PAmp
        
        
    def stroke(self, voltage): # Hub
        if voltage > 0:
            if voltage > self.Vmax:
                return self.zmax
            else:
                return self.zmax*voltage/self.Vmax
        if voltage < 0:
            if voltage < self.Vmin:
                return self.zmin
            else:
                return self.zmin*voltage/self.Vmin
        
    def capacity(self, voltage):
        # C = A*z/(Rgs*T)
        return self.A*self.stroke(voltage)/(self.Rgs*self.T)
    
    def pressure(self, voltage):
        if voltage > 0:
            if voltage > self.Vmax:
                return self.Pmax
            else:
                return self.Pmax*voltage/self.Vmax
        if voltage < 0:
            if voltage < self.Vmin:
                return self.Pmin
            else:
                return self.Pmin*voltage/self.Vmin
    
    
class VELVE:
    
    def __init__(self, R):
        self.R = R
    
    def const(self, u):
        return self.R*np.sqrt(abs(u))
        
    def backward(self, u):
        if u > 0: # druckhub
            return self.R*10**9 # kein leckstrom
        else: # saughub
            return self.R
        
    def forward(self, u):
        if u > 0: # druckhub
            return self.R
        else: # saughub
            return self.R*10**9 # leckstrom 

class TUBE: # Klasse Rohr 
    
    def __init__(self):
        self.D = 5.7*10**-4 # m Diameter
        self.L = 20*10**-3 # m Length

if __name__ == '__main__':
    
    import pandas as pd
    import matplotlib.pyplot as plt

    fig, (ax1, ax2) = plt.subplots(nrows=2, ncols=1)
    
    # vizualize signals amplitudes
    Signal = SIGNAL(amplitude=5, frequency=1)
    curves = pd.DataFrame(columns=['t', 'sin', 'rect'])
    curves['t'] = np.linspace(0, 3, 251)
    curves['sin']  = [signal.sin(t)  for t in curves['t']]
    curves['rect'] = [signal.rect(t) for t in curves['t']]
    curves.plot(x='t', y=['sin', 'rect'], ax=ax1, grid=True)
    ax1.set_xlabel('Time [s]')
    ax1.set_ylabel('Voltage [V]')
    
    # vizualize velve resistance
    Velve = VELVE(R=1)
    curves = pd.DataFrame(columns=['u', 'v_fw', 'v_bw'])
    curves['u'] = np.linspace(-1, 1, 251)
    curves['v_fw'] = [velve.forward(u) for u in curves['u']]
    curves['v_bw'] = [velve.backward(u) for u in curves['u']]
    curves.plot(x='u', y=['v_fw', 'v_bw'], ax=ax2, grid=True)
    ax2.set_yscale('log')
    ax2.set_xlabel('Voltage [V]')
    ax2.set_ylabel('Resistance [Ohm]')
    
    fig, (ax1, ax2) = plt.subplots(nrows=2, ncols=1)
    
    # visualize pump pressure and capacity
    Pump = PUMP()
    curves = pd.DataFrame(columns=['vcc', 'pressure'])
    curves['vcc'] = np.linspace(-100, 300, 251)
    curves['pressure']  = [pump.pressure(v)  for v in curves['vcc']]
    curves.plot(x='vcc', y='pressure', ax=ax1, grid=True)
    ax1.set_xlabel('Voltage [V]')
    ax1.set_ylabel('Pressure [kPa]')
    curves = pd.DataFrame(columns=['vcc', 'capacity'])
    curves['vcc'] = np.linspace(-100, 300, 251)
    curves['capacity']  = [pump.capacity(v)  for v in curves['vcc']]
    curves.plot(x='vcc', y='capacity', ax=ax2, grid=True)
    ax2.set_xlabel('Voltage [V]')
    ax2.set_ylabel('Pressure [m³/kPa]')
