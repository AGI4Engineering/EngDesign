function [passed, details, score] = evaluate_pid(Kp, Ki, Kd)
    % Kp = 10;
    % Ki = 1.55;
    % Kd = 9.5;
    %% Build the system
    K  = 1;
    tau1 = 0.5;
    tau2 = 1.0;
    tau3 = 2.0;
    s  = tf('s');
    
    G = K / ((tau1*s + 1)*(tau2*s + 1)*(tau3*s + 1));


    %% Build the pid controller
    C = pid(Kp, Ki, Kd);
    L = C*G;
    %% Build the closed loop transfer function
    sys_cl = feedback(C*G, 1);
    %% Evaluate the system
    % ts
    t_v = [0:0.00005:30];
    [y, t]=step(sys_cl, t_v);
    y_final = y(end);
    tol = 0.05;
    upper = (1+tol)*y_final;
    lower = (1-tol)*y_final;
    outside = (y > upper) | (y < lower);
    if ~any(outside)
        Ts = 0;  
    else
        lastOutsideIdx = find(outside, 1, 'last');
        % The settling time is the next time point
        if lastOutsideIdx < length(t)
            Ts = t(lastOutsideIdx + 1);
        else
            Ts = t(end);
        end
    end
    % overshoot
    y_peak = max(y);
    Mp = 100 * (y_peak - y_final) / y_final;
    % error
    e = 1-y_final;
    % GM and PM
    [Gm, Pm, ~] = margin(C*G);
    step(sys_cl)
    %% Scoring
    poles = pole(sys_cl);
    stable = all(real(poles) < 0);
    score = 0;
    if stable
        if Ts < 5
            score = score + 30;
        end
        if Mp < 20
            score = score + 20;
        end
        if e < 1e-3
            score = score + 30;
        end
        if Gm > 10
            score = score + 10;
        end
        if Pm > 45
            score = score + 10;
        end
    end
    passed = (score == 100);
    % disp("score")
    % disp(score)
    %% Details output
    details = struct();
    details.score = score;
end
