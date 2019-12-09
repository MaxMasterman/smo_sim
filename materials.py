
    
class Water:
    
    def __init__(self):
        self.ethaD = 1*10**-3 # [Pa*s] dynamische Viskosität von Wasser @T=20°C
        self.rho = 0.9982067 # [g*cm^-3] Dichte Wasser @T=20°C
        self.T = 293.15 # K
        self.kappa = 0.5*10**-9 # [1/Pa] Kompressibilität von Wasser