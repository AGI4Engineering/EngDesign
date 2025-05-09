function [passed, details, score] = eval_controller(Ac, Bc1, Bc2, Cc, Dc1, Dc2)
    %% Define the function crosst to simplify the calculation of rise time
    function t1 = crosst(a, t)
        n = numel(a);
        i = 0;

        for j = 0:n-1
            if a(n-j) > 0
                i = n-j;
                break;
            end
        end

        if i < 2
            t1 = 0;
            return;
        end

        pp = inv([t(i-1) 1; t(i) 1]) * [a(i-1); a(i)];
        t1 = -pp(2) / pp(1);
    end

    %% The plant model
    Ap = [-1.3046 1 -0.2142 0; 47.71 0 -104.83 0; 0 0 0 1; 0 0 -12769 -135.6];
    Bp = [0; 0; 0; 12769];
    Cp = [-1156.9 0 -189.95 0; 1 0 0 0; 0 1 0 0; 0 0 1 0; 0 0 0 1];
    Dp = [0; 0; 0; 0; 0];

    %% The closed loop system
    Z = inv(eye(size(Dc1 * Dp)) - Dc1 * Dp);
    Acl = [(Ap + Bp * Z * Dc1 * Cp), (Bp * Z * Cc);
           (Bc1 * (Cp + Dp * Z * Dc1 * Cp)), (Ac + Bc1 * Dp * Z * Cc)];
    Bcl = [Bp * Z * Dc2;
           (Bc2 + Bc1 * Dp * Z * Dc2)];
    Ccl = [(Cp + Dp * Z * Dc1 * Cp), (Dp * Z * Cc)];
    Dcl = (Dp * Z * Dc2);
    sys_cl = ss(Acl, Bcl, Ccl, Dcl);

    %% Stability check for the closed loop system
    poles = pole(sys_cl);
    stable = all(real(poles) < 0);

    %% Rise time check for the closed loop system
    [y, t] = step(sys_cl);
    az = squeeze(y(:, 1, :));  % First output channel
    aze = abs(1 - az);
    e_n = aze - 0.36;
    tr = crosst(e_n, t);

    %% Gain and Phase margins (using loop transfer function)
    Alu = [Ap, zeros(size(Bp, 1), size(Cc, 2));
           Bc1 * Cp, Ac];
    Blu = [Bp; Bc1 * Dp];
    Clu = -[Dc1 * Cp, Cc];
    Dlu = -[Dc1 * Dp];
    sys_lu = ss(Alu, Blu, Clu, Dlu);

    [GM, PM, ~, ~] = margin(sys_lu);

    %% Scoring
    score = 0;
    rise_time_pass = (tr < 0.2);
    gm_pass = (GM > 3.0);
    pm_pass = (PM > 30.0);
    if stable
        score = score + 50;
        if rise_time_pass
            score = score + 30;
        end
        if gm_pass
            score = score + 10;
        end
        if pm_pass
            score = score + 10;
        end
    else
        score = 0;
    end
    passed = (score == 100);

    %% Details output
    details = struct();
    details.stability_pass = stable;
    details.poles = poles;
    details.rise_time_value = tr;
    details.rise_time_pass = rise_time_pass;
    details.gain_margin_value = GM;
    details.gain_margin_pass = gm_pass;
    details.phase_margin_value = PM;
    details.phase_margin_pass = pm_pass;
end
