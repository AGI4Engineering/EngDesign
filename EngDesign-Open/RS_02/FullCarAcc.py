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


class FullCarAcc:

    def __init__(self, setupFileName):
        # inputs
        self.setupFileName = setupFileName
        self.setupFilesPath = os.path.join(os.path.dirname(__file__), "files")
        # outputs
        self.max_acc = None
        self.max_dec = None

    def run(self):

        # SetupFile obj instantiation
        s = SetupFileLoader(os.path.join(self.setupFilesPath, self.setupFileName))
        s.loadJSON()

        # Run Acceleration Envelope
        aE = AccEnvCalc(s.setupDict)
        aE.Run()

        self.max_acc = np.max(aE.accEnvDict["axacc"])
        self.max_dec = abs(np.min(aE.accEnvDict["axdec"]))

        return self.max_acc, self.max_dec
# ----------------------------------------------------------------------------


if __name__ == '__main__':

    # SetupFile.json
    setupFileName = "SetupFile.json"

    # object instantiation
    fullCarAcc = FullCarAcc(setupFileName)
    max_acc, max_dec = fullCarAcc.run()

    
