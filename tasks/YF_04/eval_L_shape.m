function [passed, details, score] = eval_cyl_torsion(d)
% Evaluate a cantilever solid circular shaft under an end torque.
% Inputs:
%   d       – shaft diameter (mm)
% Outputs:
%   passed  – true if twist angle ≤ threshold
%   details – struct with fields:
%              .phi       = measured twist (rad)
%              .threshold = allowable twist (rad)
%   score   – 0–100 according to the rubric

    %% 1) Given parameters
    L = 1000;                % shaft length (mm)
    T = 1e6;                 % applied torque (N·mm)
    E = 210000;              % Young's modulus (MPa)
    nu = 0.3;                % Poisson's ratio
    phi_thresh = 0.05;       % allowable twist (rad)

    %% 2) Compute shear modulus G and polar inertia J
    G = E / (2*(1 + nu));        % N/mm^2
    J = pi * d^4 / 32;           % mm^4

    %% 3) Twist angle
    phi = T * L / (G * J);       % rad

    %% 4) Passed?
    passed = (phi <= phi_thresh);

    %% 5) Package details
    details = struct( ...
      'phi',       phi, ...
      'threshold', phi_thresh ...
    );

    %% 6) Scoring rubric
    r = phi / phi_thresh;
    if     r >= 0.70 && r <= 0.90
        score = 100;
    elseif r >= 0    && r <  0.70
        score = (r / 0.70) * 100;
    elseif r >  0.90 && r <= 1.00
        score = (1 - (r - 0.90)/0.10) * 100;
    else
        score = 0;
    end
    score = max(0, min(100, score));

end


