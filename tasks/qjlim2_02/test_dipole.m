% Define parameters
params = struct( ...
    'Length', 0.046, ...         % Dipole length in meters
    'Width', 0.002, ...          % Dipole width in meters
    'Fmin', 1e9, ...          % Minimum frequency (Hz)
    'Fmax', 5e9, ...          % Maximum frequency (Hz)
    'Nfreq', 201 ...            % Number of frequency points
);

%% === Setup Dipole Antenna ===
ant = dipole( ...
    'Length', params.Length, ...
    'Width', params.Width);

%% === Frequency sweep and S11 ===
freq = linspace(params.Fmin, params.Fmax, params.Nfreq);
freqGHz = freq / 1e9;

try
    sobj = sparameters(ant, freq, 'UseParallel', true);
catch
    sobj = sparameters(ant, freq);
end
s11 = rfparam(sobj, 1, 1);
s11_dB = 20 * log10(abs(s11));

% Interpolate for fine frequency resolution
freq_dense = linspace(params.Fmin, params.Fmax, 1001);
s11_fit_dB = interp1(freq, s11_dB, freq_dense, 'pchip');

%% === Resonance and bandwidth estimation ===
[~, idx_min] = min(s11_fit_dB);
f_resonant = freq_dense(idx_min);
S11_resonant = s11_fit_dB(idx_min);

bw_idx = find(s11_fit_dB < -10);
if isempty(bw_idx)
    bandwidth = 0;
else
    f_lower = freq_dense(bw_idx(1));
    f_upper = freq_dense(bw_idx(end));
    bandwidth = f_upper - f_lower;
end

%% === Gain pattern ===
[maxGain, ~, ~] = pattern(ant, f_resonant, 0, 0);

%% === Summary ===
fprintf('\n--- Dipole Antenna Summary ---\n');
fprintf('Resonant Frequency: %.3f GHz with S11 = %.2f dB\n', f_resonant / 1e9, S11_resonant);
fprintf('Bandwidth (-10 dB): %.2f MHz\n', bandwidth / 1e6);
fprintf('Max Gain: %.2f dBi\n', maxGain);

%% === Plot S11 ===
figure('Name', 'Dipole S11 Plot', 'Color', 'w');
plot(freq / 1e9, s11_dB, 'b.-', 'LineWidth', 1.2); hold on;
plot(freq_dense / 1e9, s11_fit_dB, 'r-', 'LineWidth', 1.2);
xlabel('Frequency (GHz)');
ylabel('|S_{11}| (dB)');
title('Dipole Antenna S_{11}');
legend('Simulated', 'Interpolated', 'Location', 'Best');
grid on;
