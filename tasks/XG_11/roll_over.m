function [passed, details, score] = noise_rejection(K1_num, K1_den, omega_r, beta_r)
    % Set random seed for reproducibility
    passed = false;
    details = struct();
    score = 0;

    G1 = tf(1,[1 0]);
    H = 0.5*tf(13^2,[1 2*0.01*13 13^2]);
    G = G1*H; % Plant
    wL = 1.0; % Desired bandwidth, rad/sec
    kg = 1/abs(evalfr(G, 1j*wL)); % Gain
    wb = wL; % Boost frequency, rad/sec
    betab = sqrt(10); % Boost parameter
    Kb = tf([betab wb],[1 0])/sqrt(betab^2+1); % Integral Boost
    C = kg*Kb;
    C_num_expected = C.num{1};
    C_den_expected = C.den{1};
    num_error = norm(C_num_expected - K1_num);
    den_error = norm(C_den_expected - K1_den);
    if num_error < 1e-1
        num_passed = true;
        score = score + 20;
    else
        num_passed = false;
    end
    if den_error < 1e-1
        den_passed = true;
        score = score + 20;
    else
        den_passed = false;
    end

    p = beta_r*omega_r; % Roll-off corner frequency, rad/sec
    Fr2 = tf(p^2,[1 sqrt(2)*p p^2]); % Second-order Butterworth filter
    Kr2 = Fr2/abs(evalfr(Fr2,1j*omega_r));
    K2 = Kb*kg*Kr2; % Final Controller
    L2 = G*K2; % Final loop
    results = allmargin(L2);
    gain_margin = results.GainMargin;
    phase_margin = results.PhaseMargin;
    stability = results.Stable;

    if stability
        stability_passed = true;
        score = score + 20;
        if max(phase_margin) >= 50
            phase_margin_passed = true;
            score = score + 20;
        else
            phase_margin_passed = false;
        end
        if max(gain_margin) >= 3
            gain_margin_passed = true;
            score = score + 20;
        else
            gain_margin_passed = false;
        end
        details = struct();
        details.num_passed = num_passed;
        details.den_passed = den_passed;
        details.stability_passed = stability_passed;
        details.phase_margin_passed = phase_margin_passed;
        details.gain_margin_passed = gain_margin_passed;
        details.gain_margin = gain_margin;
        details.phase_margin = phase_margin;
    else
        stability_passed = false;
        phase_margin_passed = false;
        gain_margin_passed = false;
        details = struct();
        details.num_passed = num_passed;
        details.den_passed = den_passed;
        details.stability_passed = stability_passed;
        details.phase_margin_passed = phase_margin_passed;
        details.gain_margin_passed = gain_margin_passed;
        
    end

    passed = score == 100;
    details.score = score;
    details.passed = passed;
end