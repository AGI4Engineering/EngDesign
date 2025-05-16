function [passed, details, score] = verifyK(K)

    A0 = [0 1 0 0;
          0 0 1 0;
          0 0 0 1;
         -5 -4 -3 -2];
    B1 = [0; 0; 0; 1];
    B2 = [0; 0; 1; 0];
    C1 = [1 0 0 0];

    %% task1
    deltas = [0.2, -0.2];
    isStable = false;
    for d = deltas
        Acl = (A0 + d*eye(4)) + B2*K;
        if any(real(eig(Acl)) < 0)
            isStable = true;
            break;
        end
    end

    if isStable
        %% task2
        sysNom   = ss(A0 + B2*K, B1, C1, 0);
        HinfNorm = norm(sysNom, inf);
        meetsHinf = (HinfNorm < 0.5);
    end

    %% details
    details.isStable  = isStable;
    details.HinfNorm  = HinfNorm;
    details.meetsHinf = meetsHinf;

    %% score and passed
    if isStable
        score = 70 + 30 * double(meetsHinf);
    else
        score = 0;
    end
    passed = (isStable && meetsHinf);
end

function out = tern(cond, a, b)
    if cond, out = a; else out = b; end
end
