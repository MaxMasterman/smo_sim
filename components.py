import numpy as np
from materials import Water
water = Water()


class Signal:
    
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
    
    
class Pump:
    
    def __repr__(self):
        return " TUDOS "
    
    def __init__(self, medium):
        self.medium = medium
        self.diameter = 5.7*10**-3 # m
        self.A = np.pi*self.diameter/4
        
        self.zmax = 35*10**-6 # m ANNAHME
        self.zmin = -15*10**-6 # m ANNAHME
        
        self.Vmax = 240 # V operation voltage
        self.Vmin = -76 # V operation voltage
        self.VAmp = (abs(self.Vmax)+abs(self.Vmin))/2
        self.VOff = self.Vmax - self.VAmp
        
        self.Pmax = 50*10**3 # Pa back pressure air
        self.Pmin = -38*10**3 # Pa suction pressure air

        
    def stroke(self, voltage):
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
        
    def C(self, voltage):
        # Cf = z*A*kappa # hydraulische Kapazität des Fluids (Option 1)
        # Ck = # Kapazität des Kammermaterials (Option 2)
        # Cm = # Kapazität der Kammermembran (Option 3)
        return self.A*self.stroke(voltage)*self.medium.kappa # (Option 1)
        # return 1
    
    def P(self, voltage):
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
    
    
class Velve:
    
    def __init__(self, R_open, R_close, direction):
        self.R_open = R_open
        self.R_close = R_close
        self.R_actual = R_open
        self.direction = direction
        
    def R(self, u):
        return getattr(self, self.direction)(u)
    
    def constant(self, u):
        return self.R*np.sqrt(abs(u))
        
    def backward(self, u):
        if u > 0: # druckhub
            self.R_actual = self.R_close
        else: # saughub
            self.R_actual = self.R_open
        return self.R_actual
        
    def forward(self, u):
        if u > 0: # druckhub
            self.R_actual = self.R_open
        else: # saughub
            self.R_actual = self.R_close
        return self.R_actual
        
class Tube:
    
    def __init__(self, r, l, medium):
        self.r = r
        self.l = l
        self.medium=medium

    def R(self):
        return (8*self.medium.ethaD*self.l)/(np.pi*(self.r)**4)
        # return 1
    

if __name__ == '__main__':
    
    import pandas as pd
    import matplotlib.pyplot as plt

    fig, (ax1, ax2) = plt.subplots(nrows=2, ncols=1)
    
    # vizualize signals amplitudes
    signal = Signal(amplitude=5, frequency=1)
    curves = pd.DataFrame(columns=['t', 'sin', 'rect'])
    curves['t'] = np.linspace(0, 3, 251)
    curves['sin']  = [signal.sin(t)  for t in curves['t']]
    curves['rect'] = [signal.rect(t) for t in curves['t']]
    curves.plot(x='t', y=['sin', 'rect'], ax=ax1)
    ax1.set_xlabel('Time [s]')
    ax1.set_ylabel('Voltage [V]')
    
    # vizualize velve resistance
    velve1 = Velve(R_open=1, R_close=10**9, direction='forward')
    velve2 = Velve(R_open=1, R_close=10**9, direction='backward')
    curves = pd.DataFrame(columns=['u', 'v_fw', 'v_bw'])
    curves['u'] = np.linspace(-1, 1, 251)
    curves['v_fw'] = [velve1.R(u) for u in curves['u']]
    curves['v_bw'] = [velve2.R(u) for u in curves['u']]
    curves.plot(x='u', y=['v_fw', 'v_bw'], ax=ax2)
    ax2.set_yscale('log')
    ax2.set_xlabel('Voltage [V]')
    ax2.set_ylabel('Resistance [Ohm]')
    
    fig, (ax1, ax2) = plt.subplots(nrows=2, ncols=1)
    
    # visualize pump pressure and capacity
    pump = Pump(medium=water)
    curves = pd.DataFrame(columns=['vcc', 'pressure'])
    curves['vcc'] = np.linspace(-100, 300, 251)
    curves['pressure']  = [pump.P(v)  for v in curves['vcc']]
    curves.plot(x='vcc', y='pressure', ax=ax1)
    ax1.set_xlabel('Voltage [V]')
    ax1.set_ylabel('Pressure [Pa]')
    curves = pd.DataFrame(columns=['vcc', 'capacity'])
    curves['vcc'] = np.linspace(-100, 300, 251)
    curves['capacity']  = [pump.C(v)  for v in curves['vcc']]
    curves.plot(x='vcc', y='capacity', ax=ax2)
    ax2.set_xlabel('Voltage [V]')
    ax2.set_ylabel('Pressure [m³/Pa]')    
