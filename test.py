# -*- coding: utf-8 -*-
"""
Created on Sat Dec 21 12:31:16 2019

@author: timo.stubler
"""

f = 1/35 # signal frequency
steps = 500 # anzahl der zeitschritte
t_space = np.linspace(0, 4/f, steps, endpoint=True)# # simulation time


x0 = [uc0, i0]


def dp_dt(x, t):

    return 

res = odeint(dp_dt, x0, t_space)