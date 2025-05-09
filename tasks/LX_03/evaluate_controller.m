function [passed, details, score] = evaluate_controller(p1, p2, ts, N, pm, k1, k2, k3, k4)
score = 0;

if p1 == 0.5
    score = score + 4;
    details.p1 = 'p1 is correct';
else
    details.p1 = 'p1 is wrong';
end
if p2 < -0.19 && p2 > -0.21
    score = score + 4;
    details.p2 = 'p2 is correct';
else
    details.p2 = 'p2 is wrong';
end
if ts < 2.66 && ts > 2.6
    score = score + 4;
    details.ts = 'ts is correct';
else
    details.ts = 'ts is wrong';
end
if N == 3
    score = score + 4;
    details.N = 'N is correct';
else
    details.N = 'N is wrong';
end
if pm < 0.4 && pm > 0.36
    score = score + 4;
    details.pm = 'pm is correct';
else
    details.pm = 'pm is wrong';
end
if abs(k1 + k2) < 0.05 * abs(k1)
    score = score + 20;
    details.dcgain = 'DC gain is met';
else
    details.dcgain = 'DC gain is not met';
end

A = [0 0 1 0; 0 0 0 1; -10 10 -2 2; 60 -660 12 -12];
B1 = [0; 0; 3.34; -20];
B2 = [0; 0; 0; 600];
C = [1 -1 0 0];
D = 0;
A1 = A - B1 * [k1 k2 k3 k4];
eigval = eig(A1);
[~, idx] = sort(real(eigval), 'descend');
eigval_sorted = eigval(idx);
if abs(eigval_sorted(1) - eigval_sorted(2)) < 0.05 * abs(eigval_sorted(1))
    score = score + 20;
    details.critical = 'critically damped closed-loop response is met';
else
    details.critical = 'critically damped closed-loop response is not met';
end
if eigval_sorted(1) < -2.25
    score = score + 20;
    details.settlingTime = 'settling time is met';
else
    details.settlingTime = 'settling time is not met';
end
sys = ss(A1, B2, C, D);
[y, ~] = step(0.5 * sys);
miny = min(y);
if miny > -0.5
    score = score + 20;
    details.bottomOut = 'no bottom out is met';
else
    details.bottomOut = 'no bottom out is not met';
end
if score == 100
    passed = true;
else
    passed = false;
end
