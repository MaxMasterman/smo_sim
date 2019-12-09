from components import Signal, Velve, Pump, Tube
from materials import Water
import pandas as pd
import numpy as np
from scipy.integrate import odeint

Pr1 = 0 # reservoirdruck
Pr2 = 0 # reservoirdruck
Pc0 = 0 # startdruck in der pumpkammer

f = 1/35 # signal frequency
steps = 500 # anzahl der zeitschritte
t_space = np.linspace(0, 4/f, steps, endpoint=True)# # simulation time

water = Water()
pump = Pump(medium=water)

uamp = pump.VAmp
uoff = pump.VOff

signal = Signal(amplitude=uamp, frequency=f, offset=uoff)
us = signal.rect # anregungssignal der pumpe
 
tube1 = Tube(r=0.5*10**-3, l=0.01, medium=water) # schlauch
tube2 = Tube(r=0.5*10**-3, l=0.01, medium=water) # schaluch

# velve types: foward, backward, constant
velve1 = Velve(R_open=1, R_close=10**9, direction='forward') # ventiltyp
velve2 = Velve(R_open=10, R_close=10**9, direction='backward') # ventiltyp

##############################################################################

def du_dt(p, t):
    p = p[0]
    ps = pump.P(us(t))
    pv1 = -Pr1+ps-p-tube1.R()*((-Pr1+ps-p)/(tube1.R()+velve1.R_actual)) # Strom über beide Widerstände berechnet
    pv2 = -Pr2+ps-p-tube2.R()*((-Pr2+ps-p)/(tube2.R()+velve2.R_actual))
    pr1 = ((ps-Pr1-p)/(tube1.R()+velve1.R(pv1)))
    pr2 = ((ps-Pr2-p)/(tube2.R()+velve2.R(pv2)))
    return (pr1+pr2)/pump.C(us(t))

pc = odeint(du_dt, Pc0, t_space)[:, 0]

data = pd.DataFrame(columns = ['t', 'V_signal', 'P_chamber', 'P_reservoir1', 'P_reservoir2'])
data['P_chamber'] =  pc/1000
data['t'] =  t_space
data['V_signal'] = [us(t) for t in t_space]
#data['P_reservoir1'] = [Pr1 for _ in t_space]
#data['P_reservoir2'] = [Pr2 for _ in t_space]

axes = data.plot(x='t', y=['V_signal', 'P_chamber', 'P_reservoir1', 'P_reservoir2'])
axes.set_title(pump)
axes.set_xlabel('Time [s]')
axes.set_ylabel('Pressure [kPa]')


