clear; clc;

%% --- 0. Plant data ---
A0 = [  0   1   0   0;
        0   0   1   0;
        0   0   0   1;
       -5  -4  -3  -2 ];
B1 = [0;0;0;1];
B2 = [0;0;1;0];
C1 = [1 0 0 0];

%% --- 1. LMI synthesis via CVX ---
cvx_begin sdp quiet
    cvx_precision high
    variable P(4,4) symmetric
    variable Y(1,4)

    subject to
        P >= 1e-6 * eye(4);
        Gamma = 0.2;

        for d = [+0.2, -0.2]
            Ai = A0 + d * eye(4);
            L = [ Ai*P + B2*Y + (Ai*P + B2*Y)'   ,  P*B1   ,  (C1*P)';
                  (P*B1)'                         , -Gamma ,     0    ;
                  C1*P                            ,    0   , -Gamma   ];
            L <= -1e-6 * eye(6);
        end
cvx_end

% Recover static gain
K = Y * inv(P);

fprintf('\n--- Synthesis Results ---\n');
fprintf('K = [ %s ]\n', num2str(K, ' %.4f'));
fprintf('Achieved γ = %.4f\n', Gamma);

%% --- 2. Frequency‑domain check ---
Acl = A0 + B2*K;
sys = ss(Acl, B1, C1, 0);
hinf_norm = norm(sys, Inf);
fprintf('||T_{zw}||_∞ = %.4f  (should be < 0.5)\n', hinf_norm);

%% --- 3. Time‑domain simulation ---
t  = linspace(0,50,100001);
w  = sin(1*t);           % disturbance signal
x0 = zeros(4,1);
z  = lsim(sys, w, t, x0);

figure;
plot(t, z, 'LineWidth',1.5);
grid on;
xlabel('Time (s)');
ylabel('z(t)');
title('Closed‑loop performance output z(t) to w(t)');
