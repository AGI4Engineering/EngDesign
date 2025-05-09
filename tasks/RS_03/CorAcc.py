"""
---------------------------
OpenLapSim - OLS
---------------------------

This is a steady state Lap Time Simulator for a simple point mass vehicle
with aero forces, constant tyre grip(x and y), engine torque map and gears.

Steps:
    1 - Select Files: TrackFile.txt and SetupFile.py
    2 - Calculate the Acceleration Envelope
    3 - Calculate the Lap Time Simulation (vcar)
    4 - Plot Results

---------------------------
@autor: Davide Strassera
@first release: 2019-12-21
by Python 3.7
---------------------------

"""

# ----------------------------------------------------------------------------

# import packages generic
import numpy as np
import os

# import packages (OLP)
from AccEnvCalc import AccEnvCalc
from SetupFileLoader import SetupFileLoader


class CorAcc:

    def __init__(self, setupFileName):
        # inputs
        self.setupFileName = setupFileName
        self.setupFilesPath = os.path.join(os.path.dirname(__file__), "files")
        self.head_mass = 5  #in kg
        self.helmet_mass = 2  #in kg
        # outputs
        self.cor_acc_max = None

    def run(self):

        # SetupFile obj instantiation
        s = SetupFileLoader(os.path.join(self.setupFilesPath, self.setupFileName))
        s.loadJSON()

        # Run Acceleration Envelope
        aE = AccEnvCalc(s.setupDict)
        aE.Run()

        self.cor_acc_max = max(aE.accEnvDict["ay"])
        force_on_neck = self.cor_acc_max * (self.head_mass + self.helmet_mass)
        
        return force_on_neck
# ----------------------------------------------------------------------------


if __name__ == '__main__':

    # SetupFile.json
    setupFileName = "SetupFile.json"
    # object instantiation
    corAcc = CorAcc(setupFileName)
    force_on_neck = corAcc.run()

    
