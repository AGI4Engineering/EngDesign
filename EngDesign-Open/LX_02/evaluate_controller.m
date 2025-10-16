function [passed, details, score] = evaluate_controller(a11, a12, a21, a22, b11, b21, k1, k2, l1, l2, s1, s2, s3, s4)
% add for Octave
details = struct();

A = [0 1; 2 0];
B = [0; -2];
K = [-2 -1];
L = [11; 32];
s = [1 0 1 0];
ss = [s1 s2 s3 s4];

score = 0;

if isequal(A, [a11 a12; a21 a22])
    score = score + 8;
    details.A = 'A is correct';
else
    details.A = 'A is wrong';
end
if isequal(B, [b11; b21])
    score = score + 8;
    details.B = 'B is correct';
else
    details.B = 'B is wrong';
end
if isequal(K, [k1 k2])
    score = score + 10;
    details.K = 'K is correct';
else
    details.K = 'K is wrong';
end
if isequal(L, [l1; l2])
    score = score + 10;
    details.L = 'L is correct';
else
    details.L = 'L is wrong';
end
details.Stability = '';
for i = 1 : 4
    if s(i) == ss(i)
        score = score + 16;
        details.Stability = [details.Stability, 'i.c.(', num2str(i), ') is correct    '];
    else
        details.Stability = [details.Stability, 'i.c.(', num2str(i), ') is wrong    '];
    end
end

if length(details.Stability) >= 4
    details.Stability = details.Stability(1 : end - 4);
end

if score == 100
    passed = true;
else
    passed = false;
end
