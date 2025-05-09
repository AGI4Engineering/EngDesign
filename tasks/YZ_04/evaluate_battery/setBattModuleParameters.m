%% All parameters for the module

% Copyright 2023 The MathWorks, Inc.

batteryLFP = load('BattDetailedModuleLFP.mat');
run('BattDetailedModuleLFP_param');
run('setBattModuleCoolingPlate_param');
chargingParams.SOC   = 0.05; % Initial battery state of charge
chargingParams.T     = 300;  % Initial battery temperature, K
chargingParams.I     = 100;  % Charging current, A
chargingParams.time  = 1200; % Charging time, s
chargingParams.CoolT = 300;  % Coolant inlet temperature, K
chargingParams.Flow  = 3;    % Flowrate, lpm
