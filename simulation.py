from components import Signal, Velve, Pump, Tube
from materials import Water
import pandas as pd
import numpy as np
from scipy.integrate import odeint

Pr1 = 0 # reservoirdruck
Pr2 = 0 # reservoirdruck
Pc0 = 0 # startdruck in der pumpkammer

f = 1/20 # signal frequency
steps = 500 # anzahl der zeitschritte
t_space = np.linspace(0, 4/f, steps, endpoint=True)# # simulation time

signal = Signal(amplitude=130, frequency=f, offset=-60)
us = signal.rect # anregungssignal der pumpe
 
water = Water()
t1 = Tube(r=10**-3, l=1, medium=water) # schlauch
t2 = Tube(r=10**-3, l=1, medium=water) # schaluch

# velve types: foward, backward, constant
v1 = Velve(R_open=10**1, R_close=10**9, direction='forward') # ventiltyp
v2 = Velve(R_open=10**1, R_close=10**9, direction='backward') # ventiltyp
pump = Pump(medium=water)

##############################################################################

def du_dt(p, t):
    p = p[0]
    ps = pump.P(us(t))
    pv1 = -Pr1+ps-p-t1.R()*((-Pr1+ps-p)/(t1.R()+v1.R_actual))
    pv2 = -Pr2+ps-p-t2.R()*((-Pr2+ps-p)/(t2.R()+v2.R_actual))
    pr1 = ((ps-Pr1-p)/(t1.R()+v1.R(pv1)))
    pr2 = ((ps-Pr2-p)/(t2.R()+v2.R(pv2)))
    return (pr1+pr2)/pump.C(us(t))

pc = odeint(du_dt, Pc0, t_space)[:, 0]

data = pd.DataFrame(columns = ['t', 'P_signal', 'P_chamber', 'P_reservoir1', 'P_reservoir2'])
data['P_chamber'] =  pc
data['t'] =  t_space
data['P_signal'] = [pump.P(us(t)) for t in t_space]
data['P_reservoir1'] = [Pr1 for _ in t_space]
data['P_reservoir2'] = [Pr2 for _ in t_space]

axes = data.plot(x='t', y=['P_signal', 'P_chamber', 'P_reservoir1', 'P_reservoir2'])
#axes = data.plot(x='t', y=['P_chamber'])
axes.set_title(pump)
axes.set_xlabel('Time [s]')
axes.set_ylabel('Pressure [Pa]')

