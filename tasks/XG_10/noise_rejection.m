function [passed, details, score] = noise_rejection(K1_num, K1_den, omega_r, beta_r)
    % Set random seed for reproducibility
    passed = false;
    details = struct();
    score = 0;

    rng(42);  % You can change 42 to any other integer for a different seed

    % Define the plant
    G = tf(3, [1 2]);

    % ----------------------------
    % Controller 1: No roll-off
    % ----------------------------
    wL = 5.0;                        % Desired loop bandwidth (rad/s)
    kg = 1 / abs(evalfr(G, 1j*wL)); % Gain to ensure |L(jwL)| = 1
    betab = sqrt(10);               % Integral boost parameter
    Kb = tf([betab wL], [1 0]) / sqrt(betab^2 + 1);  % Integral boost component
    K1 = kg * Kb;                   % PI controller

    K1_num_expected = K1.num{1};
    K1_den_expected = K1.den{1};

    num_error = norm(K1_num - K1_num_expected);
    den_error = norm(K1_den - K1_den_expected);

    if num_error < 1e-1
        details.K1_num = "correct";
        score = score + 20;
    else
        details.K1_num = "incorrect";
    end

    if den_error < 1e-1
        details.K1_den = "correct";
        score = score + 20;
    else
        details.K1_den = "incorrect";
    end

    % ----------------------------
    % Controller 2: With roll-off
    % ----------------------------
    Kr = tf(omega_r, [1 beta_r*omega_r]) * sqrt(beta_r^2 + 1);   % First-order roll-off filter
    K2 = K1 * Kr;                   % Final controller with roll-off

    % Closed-loop transfer functions
    L2 = K2 * G;            % Open-loop transfer function
    T2 = feedback(L2, 1);   % Closed-loop transfer function
    S2 = feedback(1, L2);   % Sensitivity function
    U2 = feedback(K2, G);   % Transfer from reference to control input

    % Simulation setup
    t = 0:0.001:2;                      % Time vector
    r = 3 * ones(size(t));             % Step reference input
    n = zeros(size(t));                
    n(t >= 1) = 0.05 * randn(1, sum(t >= 1));  % Measurement noise injected at t >= 1

    % Simulate system response
    [y2, t2, ~] = lsim(T2, r + n, t);   % Output response
    [u2, ~] = lsim(U2, r + n, t);       % Control signal

    % Evaluate control signal sensitivity to noise
    u2_noise = u2(t >= 1);             % Control signal during noisy interval
    std_u2 = std(u2_noise);            % Standard deviation as noise sensitivity metric

    if std_u2 < 0.02
        noise_rejection_passed = true;
        details.noise_rejection = "fullfilled";
        score = score + 60;
    else
        noise_rejection_passed = false;
        details.noise_rejection = "not fullfilled";
    end

    passed = num_error < 1e-1 && den_error < 1e-1 && noise_rejection_passed;
end