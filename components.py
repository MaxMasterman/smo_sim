import numpy as np
from materials import Water

class Signal:
    
    def __init__(self, amplitude, frequency, offset):
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
    
    
class Pump:
    
    def __repr__(self):
        return " TUDOS "
    
    def __init__(self, medium, nu=0.0001):
        self.medium = medium
        self.nu = nu # mass for the slope
        self.diameter = 5.7*10**-3 # m
        self.A = np.pi*self.diameter/4
        self.z0 = 1*10**-3 # m
        self.V0 = self.A*self.z0
        ''' 
        Auslenkung realer Piezoaktor z.B.: 2um
        (https://www.physikinstrumente.de/de/produkte/piezoelektrische-wandler-transducer-piezoaktoren/pd0xx-runde-picma-chip-aktoren-100850/#specification) 
        '''
        
        self.zmax = 35*10**-6 # m ANNAHME
        self.zmin = -15*10**-6 # m ANNAHME
        self.zAmp = (self.zmax + abs(self.zmin))/2
        self.zOff = self.zmax - (self.zmax + abs(self.zmin))/2

        self.Vmax = 240 # V operation voltage
        self.Vmin = -76 # V operation voltage
        self.VAmp = (self.Vmax + abs(self.Vmin))/2
        self.VOff = self.Vmax - (self.Vmax + abs(self.Vmin))/2
            
        self.Pmax = 50*10**3 # Pa back pressure air
        self.Pmin = -38*10**3 # Pa suction pressure air
        self.PAmp = (self.Pmax + abs(self.Pmin))/2
        self.POff = self.Pmax - (self.Pmax + abs(self.Pmin))/2

    def stroke(self, voltage):
        return (self.zmin - self.zmax) / (np.exp((voltage)/self.nu) + 1) + self.zmax
        
    def C(self, voltage):
        return abs((self.V0 + self.A*self.stroke(voltage))/self.P(voltage))
    
    def P(self, voltage):
        return (self.Pmin - self.Pmax) / (np.exp((voltage)/self.nu) + 1) + self.Pmax
    
class Velve:
    
    def __init__(self, R_open, R_close, direction, nu=0.1, v_switch=0):
        self.R_open = R_open
        self.R_close = R_close
        self.R_actual = R_open
        self.direction = direction
        self.nu = nu # mass for the slope
        self.v_switch = v_switch # voltage to open
        
    def R(self, u):
        return getattr(self, self.direction)(u)
    
    def constant(self, u):
        return self.R*np.sqrt(abs(u))
        
    def backward(self, u):
        return (self.R_open - self.R_close) / (np.exp((u-self.v_switch)/self.nu) + 1) + self.R_close

    def forward(self, u):
        return (self.R_close - self.R_open) / (np.exp((u-self.v_switch)/self.nu) + 1) + self.R_open

        
class Tube:
    
    def __init__(self, r, l, medium):
        self.r = r
        self.l = l
        self.medium=medium

    def R(self):
        return (8*self.medium.ethaD*self.l)/(np.pi*(self.r)**4)
    

if __name__ == '__main__':
    
    import pandas as pd
    import matplotlib.pyplot as plt

    fig, (ax1, ax2) = plt.subplots(nrows=2, ncols=1)
    
    # vizualize signals amplitudes
    signal = Signal(amplitude=5, frequency=1, offset=2)
    curves = pd.DataFrame(columns=['t', 'sin', 'rect'])
    curves['t'] = np.linspace(0, 3, 1000)
    curves['sin']  = [signal.sin(t)  for t in curves['t']]
    curves['rect'] = [signal.rect(t) for t in curves['t']]
    curves.plot(x='t', y=['sin', 'rect'], ax=ax1)
    ax1.set_xlabel('Time [s]')
    ax1.set_ylabel('Voltage [V]')
    
    # vizualize velve resistance
    v1 = Velve(R_open=1, R_close=10**9, direction='forward', v_switch=10)
    v2 = Velve(R_open=1, R_close=10**9, direction='backward', v_switch=-10)
    curves = pd.DataFrame(columns=['u', 'v_fw', 'v_bw'])
    curves['u'] = np.linspace(-50, 150, 1000)
    curves['v_fw'] = [v1.R(u) for u in curves['u']]
    curves['v_bw'] = [v2.R(u) for u in curves['u']]
    curves.plot(x='u', y=['v_fw', 'v_bw'], ax=ax2)
    ax2.set_yscale('log')
    ax2.set_xlabel('Voltage [V]')
    ax2.set_ylabel('Resistance [Ohm]')
    
    fig, (ax1, ax2) = plt.subplots(nrows=2, ncols=1)
    
    # visualize pump pressure and capacity
    water = Water()
    pump = Pump(medium=water)
    curves = pd.DataFrame(columns=['vcc', 'stroke', 'pressure'])
    curves['vcc'] = np.linspace(-100, 300, 1000)
    curves['pressure']  = [pump.P(v)  for v in curves['vcc']]
    curves['stroke']  = [pump.stroke(v)  for v in curves['vcc']]
    curves.plot(x='vcc', y=['stroke', 'pressure'], ax=ax1)
    ax1.set_xlabel('Voltage [V]')
    ax1.set_ylabel('Pressure [kPa]')
    curves = pd.DataFrame(columns=['vcc', 'capacity'])
    curves['vcc'] = np.linspace(-100, 300, 1000)
    curves['capacity']  = [pump.C(v)  for v in curves['vcc']]
    curves.plot(x='vcc', y='capacity', ax=ax2)
    ax2.set_xlabel('Voltage [V]')
    ax2.set_ylabel('Capacity [m³/Pa]')    
    