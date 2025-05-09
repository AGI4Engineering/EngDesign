function [passed, details, score] = evaluate_controller(theta, tau, num, den)
    % Evaluate controller performance for nanopositioning stage
    % Inputs:
    %   theta: model parameter
    %   tau: model parameter
    %   num: controller numerator coefficients
    %   den: controller denominator coefficients
    % Outputs:
    %   passed: boolean indicating if all requirements are met
    %   details: struct with detailed evaluation results
    %   score: score for the controller
    
    % System state space matrices
    s = tf('s');
    Gp = pade(exp(-theta*s), 10)/(1+tau*s);  % Use Pade approximation for the delay
    desired_theta = 16.5;
    desired_tau = 19.5;
    theta_check = abs(theta - desired_theta) <= 2;
    tau_check = abs(tau - desired_tau) <= 2;
    
    % Controller transfer function
    C = tf(num, den);

    % Create closed-loop transfer function
    Tfb = feedback(Gp*C, 1);

    % Check closed-loop stability
    poles = pole(Tfb);
    is_stable = all(real(poles) < 0);
    
    if ~is_stable
        % If unstable, skip performance evaluation and return zero scores
        passed = false;
        score = 0;
        if theta_check
            score = score + 10;
        end
        if tau_check
            score = score + 10;
        end
        details = struct();
        details.theta = theta;
        details.tau = tau;
        details.overshoot = Inf;
        details.settling_time = Inf;
        details.gain_margin = -Inf;
        details.phase_margin = -Inf;
        return;
    else
        % Time domain analysis
        S = stepinfo(Tfb);
        overshoot = S.Overshoot;
        settling_time = S.SettlingTime;
        overshoot_check = overshoot <= 10;
        settling_time_check = settling_time <= 150;
            
        % Frequency analysis
        [Gm, Pm] = margin(Gp*C);
        Gm_db = 20*log10(Gm);  % Convert to dB
        gain_margin_check = (Gm_db > 7);
        phase_margin_check = (Pm > 60);
        margin_check = gain_margin_check && phase_margin_check;
        
        % Compile results
        passed = theta_check && tau_check && overshoot_check && settling_time_check && margin_check;

        % Scoring
        score = 0;
        if theta_check
            score = score + 10;
        end
        if tau_check
            score = score + 10;
        end
        if overshoot_check
            score = score + 20;
        end
        if settling_time_check
            score = score + 20;
        end
        if gain_margin_check
            score = score + 20;
        end
        if phase_margin_check
            score = score + 20;
        end
        
        details = struct();
        details.theta = theta;
        details.tau = tau;
        details.overshoot = overshoot;
        details.settling_time = settling_time;  
        details.gain_margin = Gm_db;  % Store in dB
        details.phase_margin = Pm;
    end
end