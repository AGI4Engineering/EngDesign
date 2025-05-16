%% Battery parameters

%% Detailed
Detailed.SOC_vecCell = [0, .1, .25, .5, .75, .9, 1]; % Vector of state-of-charge values, SOC
Detailed.SOC_vecCellPercentDeviation = zeros([15, 1]); % Percent deviation for SOC_vecCell
Detailed.T_vecCell = [278, 293, 313]; % Vector of temperatures, T, K
Detailed.T_vecCellPercentDeviation = zeros([15, 1]); % Percent deviation for T_vecCell
Detailed.V0_matCell = [3.49, 3.5, 3.51; 3.55, 3.57, 3.56; 3.62, 3.63, 3.64; 3.71, 3.71, 3.72; 3.91, 3.93, 3.94; 4.07, 4.08, 4.08; 4.19, 4.19, 4.19]; % Open-circuit voltage, V0(SOC,T), V
Detailed.V0_matCellPercentDeviation = zeros([15, 1]); % Percent deviation for V0_matCell
Detailed.V_rangeCell = [0, inf]; % Terminal voltage operating range [Min Max], V
Detailed.V_rangeCellPercentDeviation = zeros([15, 1]); % Percent deviation for V_rangeCell
Detailed.R0_dis_matCell = [.0117, .0085, .009; .011, .0085, .009; .0114, .0087, .0092; .0107, .0082, .0088; .0107, .0083, .0091; .0113, .0085, .0089; .0116, .0085, .0089]; % Terminal resistance during discharging, R0(SOC,T), Ohm
Detailed.R0_dis_matCellPercentDeviation = zeros([15, 1]); % Percent deviation for R0_dis_matCell
Detailed.R0_ch_matCell = [.0117, .0085, .009; .011, .0085, .009; .0114, .0087, .0092; .0107, .0082, .0088; .0107, .0083, .0091; .0113, .0085, .0089; .0116, .0085, .0089]; % Terminal resistance during charging, R0(SOC,T), Ohm
Detailed.R0_ch_matCellPercentDeviation = zeros([15, 1]); % Percent deviation for R0_ch_matCell
Detailed.AHCell = 27; % Cell capacity, AH, A*hr
Detailed.AHCellPercentDeviation = zeros([15, 1]); % Percent deviation for AHCell
Detailed.R1_matCell = [.0109, .0029, .0013; .0069, .0024, .0012; .0047, .0026, .0013; .0034, .0016, .001; .0033, .0023, .0014; .0033, .0018, .0011; .0028, .0017, .0011]; % First polarization resistance, R1(SOC,T), Ohm
Detailed.R1_matCellPercentDeviation = zeros([15, 1]); % Percent deviation for R1_matCell
Detailed.tau1_matCell = [20, 36, 39; 31, 45, 39; 109, 105, 61; 36, 29, 26; 59, 77, 67; 40, 33, 29; 25, 39, 33]; % First time constant, tau1(SOC,T), s
Detailed.tau1_matCellPercentDeviation = zeros([15, 1]); % Percent deviation for tau1_matCell
Detailed.R2_matCell = [.0109, .0029, .0013; .0069, .0024, .0012; .0047, .0026, .0013; .0034, .0016, .001; .0033, .0023, .0014; .0033, .0018, .0011; .0028, .0017, .0011]; % Second polarization resistance, R2(SOC,T), Ohm
Detailed.R2_matCellPercentDeviation = zeros([15, 1]); % Percent deviation for R2_matCell
Detailed.tau2_matCell = [20, 36, 39; 31, 45, 39; 109, 105, 61; 36, 29, 26; 59, 77, 67; 40, 33, 29; 25, 39, 33]; % Second time constant, tau2(SOC,T), s
Detailed.tau2_matCellPercentDeviation = zeros([15, 1]); % Percent deviation for tau2_matCell
Detailed.thermal_massCell = 100; % Thermal mass, J/K
Detailed.thermal_massCellPercentDeviation = zeros([15, 1]); % Percent deviation for thermal_massCell
Detailed.InterCellThermalResistance = 1; % Inter-cell thermal path resistance, K/W
Detailed.InterParallelAssemblyThermalResistance = 1; % Inter-parallel assembly thermal path resistance, K/W

%% ParallelAssemblyType1
ParallelAssemblyType1.SOC_vecCell = [0, .1, .25, .5, .75, .9, 1]; % Vector of state-of-charge values, SOC
ParallelAssemblyType1.SOC_vecCellPercentDeviation = zeros([3, 1]); % Percent deviation for SOC_vecCell
ParallelAssemblyType1.T_vecCell = [278, 293, 313]; % Vector of temperatures, T, K
ParallelAssemblyType1.T_vecCellPercentDeviation = zeros([3, 1]); % Percent deviation for T_vecCell
ParallelAssemblyType1.V0_matCell = [3.49, 3.5, 3.51; 3.55, 3.57, 3.56; 3.62, 3.63, 3.64; 3.71, 3.71, 3.72; 3.91, 3.93, 3.94; 4.07, 4.08, 4.08; 4.19, 4.19, 4.19]; % Open-circuit voltage, V0(SOC,T), V
ParallelAssemblyType1.V0_matCellPercentDeviation = zeros([3, 1]); % Percent deviation for V0_matCell
ParallelAssemblyType1.V_rangeCell = [0, inf]; % Terminal voltage operating range [Min Max], V
ParallelAssemblyType1.V_rangeCellPercentDeviation = zeros([3, 1]); % Percent deviation for V_rangeCell
ParallelAssemblyType1.R0_dis_matCell = [.0117, .0085, .009; .011, .0085, .009; .0114, .0087, .0092; .0107, .0082, .0088; .0107, .0083, .0091; .0113, .0085, .0089; .0116, .0085, .0089]; % Terminal resistance during discharging, R0(SOC,T), Ohm
ParallelAssemblyType1.R0_dis_matCellPercentDeviation = zeros([3, 1]); % Percent deviation for R0_dis_matCell
ParallelAssemblyType1.R0_ch_matCell = [.0117, .0085, .009; .011, .0085, .009; .0114, .0087, .0092; .0107, .0082, .0088; .0107, .0083, .0091; .0113, .0085, .0089; .0116, .0085, .0089]; % Terminal resistance during charging, R0(SOC,T), Ohm
ParallelAssemblyType1.R0_ch_matCellPercentDeviation = zeros([3, 1]); % Percent deviation for R0_ch_matCell
ParallelAssemblyType1.AHCell = 27; % Cell capacity, AH, A*hr
ParallelAssemblyType1.AHCellPercentDeviation = zeros([3, 1]); % Percent deviation for AHCell
ParallelAssemblyType1.R1_matCell = [.0109, .0029, .0013; .0069, .0024, .0012; .0047, .0026, .0013; .0034, .0016, .001; .0033, .0023, .0014; .0033, .0018, .0011; .0028, .0017, .0011]; % First polarization resistance, R1(SOC,T), Ohm
ParallelAssemblyType1.R1_matCellPercentDeviation = zeros([3, 1]); % Percent deviation for R1_matCell
ParallelAssemblyType1.tau1_matCell = [20, 36, 39; 31, 45, 39; 109, 105, 61; 36, 29, 26; 59, 77, 67; 40, 33, 29; 25, 39, 33]; % First time constant, tau1(SOC,T), s
ParallelAssemblyType1.tau1_matCellPercentDeviation = zeros([3, 1]); % Percent deviation for tau1_matCell
ParallelAssemblyType1.R2_matCell = [.0109, .0029, .0013; .0069, .0024, .0012; .0047, .0026, .0013; .0034, .0016, .001; .0033, .0023, .0014; .0033, .0018, .0011; .0028, .0017, .0011]; % Second polarization resistance, R2(SOC,T), Ohm
ParallelAssemblyType1.R2_matCellPercentDeviation = zeros([3, 1]); % Percent deviation for R2_matCell
ParallelAssemblyType1.tau2_matCell = [20, 36, 39; 31, 45, 39; 109, 105, 61; 36, 29, 26; 59, 77, 67; 40, 33, 29; 25, 39, 33]; % Second time constant, tau2(SOC,T), s
ParallelAssemblyType1.tau2_matCellPercentDeviation = zeros([3, 1]); % Percent deviation for tau2_matCell
ParallelAssemblyType1.thermal_massCell = 100; % Thermal mass, J/K
ParallelAssemblyType1.thermal_massCellPercentDeviation = zeros([3, 1]); % Percent deviation for thermal_massCell
ParallelAssemblyType1.InterCellThermalResistance = 1; % Inter-cell thermal path resistance, K/W
