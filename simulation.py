#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct  3 2019

@author: kristjan
"""

import pandas as pd
import numpy as np
from scipy.integrate import odeint

from components import FLUID, SIGNAL, PUMP, VELVE, TUBE 

Pump = PUMP() 
Tube = TUBE()
Water = FLUID()

#Druckamplitude und Offset aus Pumpenparametern berechnen
VAmp = Pump.VAmp
VOff = Pump.VOff

Cp = 1 # pumpkammerkapazität
Rs = 2 # Dummy schlauchwiderstand
#Rs = (8*Water.ethaD*Tube.L)/(np.pi*(Tube.D/2)**4) # Schlauchwiderstand
Rv = 1 # ventilwiderstand

Pr = 0 # reservoirdruck
Pc0 = 0 # startdruck in der pumpkammer

T = 35*(Rs+Rv)*Cp # ladedauer | warum nicht faktor 5 !?
steps = 500 # anzahl der zeitschritte
t_space = np.linspace(0, 2*T, steps, endpoint=True)

Signal = SIGNAL(amplitude=VAmp, frequency=1/T, offset=VOff)
Vs = Signal.rect(t) # Spannungs-Anregungssignal der pumpe
Ps = Pump.stroke(Vs) # Druck-Anregungssignal der pumpe

Velve = VELVE(R=Rv)  
Rvelve = Velve.const # ventiltyp
    
i_scale = 5 # hängt auch von der anzahl der zeitschritte ab!

##############################################################################

def dp_dt(p, t):
    p = p[0]
    pv = (Pr-Ps(t)+p)*Rv/(Rv+Rs)-Ps(t)+p
    return (Ps(t)-p+Pr)/((Rs+Rvelve(pv))*Cp)
    
Pc = odeint(dp_dt, Pc0, t_space)[:,0]

data = pd.DataFrame(columns = ['t', 'Ps', 'Pc', 'Pr', 'i'])
data['Pc'] =  Pc
data['t'] =  t_space
data['Ps'] = [Ps(t) for t in t_space]
data['Pr'] = [Pr for _ in t_space]
data['i'] = np.gradient(Pc)*i_scale

axes = data.plot(x='t', y=['Ps', 'Pc', 'Pr', 'i'], grid=True)
axes.set_title('Simple Pump')
axes.set_xlabel('Time [s]')
axes.set_ylabel('Voltage [V]')

print('nettostrom:', data['i'].sum())

