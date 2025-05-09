%% Cooling plate parameters for the module

% Copyright 2023 The MathWorks, Inc.


CP.Interface.Num  = batteryLFP.Detailed.ThermalNodes.Bottom.NumNodes;
CP.Interface.Dim  = batteryLFP.Detailed.ThermalNodes.Bottom.Dimensions;
CP.Interface.Loc  = batteryLFP.Detailed.ThermalNodes.Bottom.Locations;
CP.Interface.DimX = 1;
CP.Interface.DimY = 10;

CP.Plate.Thk      = 2e-3;
CP.Plate.K        = 80;
CP.Plate.Den      = 2500;
CP.Plate.Cp       = 447;
CP.Plate.T        = 300;

CP.Design.NumCh   = 4;
CP.Design.Dc      = 1.5e-3;
CP.Design.Dd      = 5e-3;
CP.Design.Rgh     = 1.5e-5;
