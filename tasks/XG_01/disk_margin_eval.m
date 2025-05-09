function [passed, details, score] = disk_margin_eval(num, den, alpha)
    % Evaluate controller performance for aircraft model
    % Inputs:
    %   num: controller numerator coefficients
    %   den: controller denominator coefficients
    %   alpha: alpha value for loopsyn
    % Outputs:
    %   passed: boolean indicating if all requirements are met
    %   details: struct with detailed evaluation results
    
    % System state space matrices
    A = [ -2.2567e-02  -3.6617e+01  -1.8897e+01  -3.2090e+01   3.2509e+00  -7.6257e-01;
       9.2572e-05  -1.8997e+00   9.8312e-01  -7.2562e-04  -1.7080e-01  -4.9652e-03;
       1.2338e-02   1.1720e+01  -2.6316e+00   8.7582e-04  -3.1604e+01   2.2396e+01;
       0            0            1.0000e+00   0            0            0;
       0            0            0            0           -3.0000e+01   0;
       0            0            0            0            0           -3.0000e+01];
    B = [0     0;
        0     0;
        0     0;
        0     0;
        30     0;
        0    30];
    C = [0     1     0     0     0     0;
        0     0     0     1     0     0];
    D = [0     0;
        0     0];

    G = ss(A,B,C,D);
    
    % Desired loop shape
    expected_num = 8;
    expected_den = [1,0];
    Gd = tf(num, den);
    Gder = tf(expected_num, expected_den);
    tf_passed = isequal(Gd, Gder);
    
    % Design controller
    [K,CL,gamma,info] = loopsyn(G,Gd,alpha);
    DM = diskmargin(G,K);
    disk_margin = DM.DiskMargin;

    % Compute Score
    score = 0;
    if tf_passed
        score = score + 20;
    end
    if disk_margin > 0.05
        score = score + 40;
    end
    if gamma < 1
        score = score + 40;
    end

    % Compile results
    passed = score == 100;

    details = struct();
    details.diskmargin = disk_margin;
    details.gamma = gamma;
    details.info = info;
    
end