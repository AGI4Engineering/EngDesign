function [passed, details, score] = evaluate_controller(num, den)
    % Evaluate controller performance for nanopositioning stage
    % Inputs:
    %   num: controller numerator coefficients
    %   den: controller denominator coefficients
    % Outputs:
    %   passed: boolean indicating if all requirements are met
    %   details: struct with detailed evaluation results
    
    % System state space matrices
    A = [-3360.27884342382, 24650.4407238876, -24650.4407238876, 24650.4407238876, -24650.4407238876, 24650.4407238876, -6162.61018097190;
         -3270.26403683917, 10278.7248098086, -7476.39347226054, 7476.39347226054, -7476.39347226054, 7476.39347226054, -1869.09836806513;
         -2657.10970968037, 10628.4388387215, -13430.7701762696, 16233.1015138177, -16233.1015138177, 16233.1015138177, -4058.27537845441;
         -3954.03177459846, 15816.1270983939, -15816.1270983939, 13013.7957608458, -10211.4644232977, 10211.4644232977, -2552.86610582443;
         -2325.45756017668, 9301.83024070671, -9301.83024070671, 9301.83024070671, -12104.1615782548, 14906.4929158029, -3726.62322895072;
         -1665.81075466004, 6663.24301864017, -6663.24301864017, 6663.24301864017, -6663.24301864017, 3860.91168109210, -264.645085886005;
         -1596.51916299641, 6386.07665198562, -6386.07665198562, 6386.07665198562, -6386.07665198562, 6386.07665198562, -4398.85050054448];
    
    B = [33.1501; 29.2147; 49.7430; 55.4071; 43.2351; 22.8726; 24.9153];
    C = [41.1585, -164.6342, 164.6342, -164.6342, 164.6342, -164.6342, 41.1585];
    D = 0;
    
    % Create state space and transfer function models
    sys_ss = ss(A, B, C, D);
    sys_tf = tf(sys_ss);
    
    % Controller transfer function
    controller = tf(num, den);
    
    % Open-loop transfer function
    L = sys_tf * controller;
    
    % Create closed-loop transfer function
    Tfb = feedback(L, 1);
    % Check closed-loop stability
    poles = pole(Tfb);
    is_stable = all(real(poles) < 0);
    if ~is_stable
        % If unstable, skip performance evaluation and return zero scores
        passed = false;
        score = 0;
        details = struct();
        details.bandwidth_hz = Inf;
        details.bandwidth_passed = false;
        details.gain_margin_db = -Inf;
        details.phase_margin_deg = -Inf;
        details.margins_passed = false;
        return;
    else
        % Frequency analysis
        w = logspace(0, 4, 1000);  % Create logarithmically spaced points from 10^0 to 10^4
        [mag, phase, wout] = bode(L, w);
        mag = squeeze(mag);
        phase = squeeze(phase);
        
        % 1. Find bandwidth (0 dB crossing frequency)
        mag_db = 20*log10(mag);
        % Find where magnitude crosses 0 dB
        crossover_idx = find(diff(sign(mag_db)) ~= 0, 1);
        if ~isempty(crossover_idx)
            % Linear interpolation to find more precise crossing frequency
            w1 = w(crossover_idx);
            w2 = w(crossover_idx + 1);
            m1 = mag_db(crossover_idx);
            m2 = mag_db(crossover_idx + 1);
            bw_rad = w1 + (w2 - w1) * (-m1)/(m2 - m1);
            bw_hz = bw_rad / (2 * pi);
            bw_check = abs(bw_hz - 85) <= 10; % Allow ±10 Hz tolerance
        else
            bw_hz = 0;
            bw_check = false;
        end
        
        % 2. Check margins
        [Gm, Pm] = margin(L);
        Gm_db = Gm;
        margin_check = (Gm_db > 1.5) && (Pm > 60);
        
        % Compile results
        passed = bw_check && margin_check;

        % Scoring
        score = 0;
        if bw_check
            score = score + 40;
        end
        if Gm_db > 1.5
            score = score + 30;
        end
        if Pm > 60
            score = score + 30;
        end
        
        details = struct();
        details.bandwidth_hz = bw_hz;
        details.bandwidth_passed = bw_check;
        details.gain_margin_db = Gm_db;
        details.phase_margin_deg = Pm;
        details.margins_passed = margin_check;
    end
    
end