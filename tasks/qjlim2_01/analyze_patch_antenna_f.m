function results = analyze_patch_antenna_f(params)
% ANALYZE_PATCH_ANTENNA
% Analyzes patch antenna and fits |S11| using rational interpolation (Chebfun).

arguments
    params struct
end

%% === Setup antenna ===
substrate = dielectric('Name','Custom','EpsilonR',params.EpsilonR,'Thickness',params.Height);
patch = patchMicrostrip( ...
    'Length',params.Length, 'Width',params.Width, ...
    'Substrate',substrate, ...
    'GroundPlaneLength',params.GroundPlaneLength, ...
    'GroundPlaneWidth',params.GroundPlaneWidth, ...
    'Height',params.Height, ...
    'FeedOffset',params.FeedOffset );

%% === Frequency sweep and S11 ===

freq = linspace(params.Fmin, params.Fmax, params.Nfreq);
freq/1e9,

try
    sobj = sparameters(patch, freq, 'UseParallel', true);
catch
    sobj = sparameters(patch, freq);
end
s11 = rfparam(sobj, 1, 1);  % Get the complex S11 values




% Separate real and imaginary parts
s11_real = real(s11);
s11_imag = imag(s11);

s11_dB = 20 * log10(abs(s11));

% === Spline interpolation on dB magnitude ===
freq_dense = linspace(params.Fmin, params.Fmax, 1001);
s11_fit_dB = interp1(freq, s11_dB, freq_dense, 'pchip');

%% === Resonance and bandwidth estimation
[~, idx_min] = min(s11_fit_dB);
f_resonant = freq_dense(idx_min);
S11_resonant = min(s11_fit_dB); 
bw_idx = find(s11_fit_dB < -10);
if isempty(bw_idx)
    bandwidth = 0;
else
    f_lower = freq_dense(bw_idx(1));
    f_upper = freq_dense(bw_idx(end));
    bandwidth = f_upper - f_lower;
end

%% === Gain Pattern
[maxGain, ~, ~] = pattern(patch, f_resonant, 0, 90);
if isfield(params, 'Polarization')
    polType = upper(params.Polarization);
    if ~ismember(polType, {'H', 'V'})
        warning('Invalid polarization "%s", using default V.', polType);
        polType = 'V';
    end
else
    polType = 'V';
end
[maxPolGain, ~, ~] = pattern(patch, f_resonant, 0, 90, 'Polarization', polType);

%% === Store results
results = struct();
results.S11_resonant = S11_resonant;
results.f_resonant = f_resonant;
results.bandwidth = bandwidth;
results.maxGain = maxGain;

%% === Summary
fprintf('\n--- Antenna Summary ---\n');
fprintf('Resonant Frequency: %.3f GHz with S11 = %.2f dB\n', f_resonant / 1e9, S11_resonant);
fprintf('Bandwidth (-10 dB): %.2f MHz\n', bandwidth / 1e6);
fprintf('Max Gain: %.2f dBi\n', maxGain);
end
