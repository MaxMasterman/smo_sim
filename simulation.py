from components import Signal, Velve, Pump, Tube
from materials import Water
import pandas as pd
import numpy as np
from scipy.integrate import odeint
from scipy.signal import unit_impulse

Pr1 = 0 # reservoirdruck
Pr2 = 0 # reservoirdruck
Pc0 = 0 # startdruck in der pumpkammer
i0 = 0 # startvolumenstrom
x0 = [Pc0, i0]

f = 1/55 # signal frequency
steps = 500 # anzahl der zeitschritte
t_space = np.linspace(0, 4/f, steps, endpoint=True)# # simulation time

water = Water()
pump = Pump(medium=water)
signal = Signal(amplitude=pump.VAmp, frequency=f, offset=pump.VOff)
us = signal.rect # anregungssignal der pumpe


t1 = Tube(r=10**-3, l=0.01, medium=water) # schlauch
t2 = Tube(r=10**-3, l=0.01, medium=water) # schaluch

# velve types: foward, backward, constant
v1 = Velve(R_open=10**1, R_close=10**9, direction='forward') # ventiltyp
v2 = Velve(R_open=10**1, R_close=10**9, direction='backward') # ventiltyp

##############################################################################

#def dp_dt(x, t):
#    p = x[0]
#    ps = pump.P(us(t))
#    pv1 = -Pr1+ps-p-t1.R()*((-Pr1+ps-p)/(t1.R()+v1.R_actual))
#    pv2 = -Pr2+ps-p-t2.R()*((-Pr2+ps-p)/(t2.R()+v2.R_actual))
#    pr1 = (ps-Pr1-p)/(t1.R()+v1.R(pv1))
#    pr2 = (ps-Pr2-p)/(t2.R()+v2.R(pv2))
#    return [(pr1+pr2)/pump.C(us(t)), (pr1+pr2)]

def dx_dt(x, t): # Zustandsgrößen definieren (x1 = uc und x2 = i)
    ps = pump.P(us(t))
    
    pv1 = ps-Pr1-x[0]-t1.R()*((ps-Pr1-x[0])/(t1.R()+v1.R_actual))
    pv2 = ps-Pr2-x[0]-t2.R()*((ps-Pr2-x[0])/(t2.R()+v2.R_actual)) 
    ir1 = ((ps-Pr1-x[0])/(t1.R()+v1.R(pv1)))
    ir2 = ((ps-Pr2-x[0])/(t2.R()+v2.R(pv2)))
    
    # Zeitableitungen mit Diracpuls 
    # ...
    
    
    return [(ir1+ir2)/pump.C(us(t)), (ir1+ir2)] # Ableitungen der Zustandsgrößen x1 und x2

res = odeint(dx_dt, x0, t_space)

def volflow(p, tspace):
    
    pres = p
    for t in tspace:
        ps = pump.P(us(t))
        pv1 = ps-Pr1-pres-t1.R()*((ps-Pr1-pres)/(t1.R()+v1.R_actual))
        pv2 = ps-Pr2-pres-t2.R()*((ps-Pr2-pres)/(t2.R()+v2.R_actual))
    
        R1 = (t1.R()+v1.R(pv1))
        R2 = (t2.R()+v2.R(pv2))
    
        Rges= (R1*R2)/(R1+R2) # Parallelwiderstand
    
        Vflow = pres/Rges
    return Vflow

dVdt = volflow(res[:,0], t_space)

data = pd.DataFrame(columns = ['t', 'P_signal', 'P_chamber','dV/dt_chamber', 'P_reservoir1', 'P_reservoir2'])
data['P_chamber'] =  res[:,0] * 10**(-3) # [kPa]
data['dV/dt_chamber'] = dVdt *60*10**3 # [mL/min]
data['t'] =  t_space
data['P_signal'] = [pump.P(us(t))* 10**(-3) for t in t_space]
data['P_reservoir1'] = [Pr1* 10**(-3) for _ in t_space]
data['P_reservoir2'] = [Pr2* 10**(-3) for _ in t_space]

axes = data.plot(x='t', y=['P_signal', 'P_chamber','dV/dt_chamber', 'P_reservoir1', 'P_reservoir2'])
#axes = data.plot(x='t', y=['dV/dt_chamber'])
axes.set_title(pump)
axes.set_xlabel('Time [s]')
axes.set_ylabel('Pressure [kPa]')