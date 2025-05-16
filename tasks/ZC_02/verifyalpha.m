function [passed, details, score] = verifyalpha(alpha)
    %% Parameters
    optimalAlpha = 0.651;
    maxAlpha = 1.087;

    %% task1: Score Calculation
    if alpha > maxAlpha
        score = 0;
    elseif alpha >= optimalAlpha
        score = 95;
    else
        ratio = alpha / optimalAlpha;
        if ratio >= 0.90
            score = 90;
        elseif ratio >= 0.80
            score = 80;
        elseif ratio >= 0.70
            score = 70;
        elseif ratio >= 0.60
            score = 60;
        elseif ratio >= 0.50
            score = 50;
        else
            score = 0;
        end
    end

    %% details
    details.alpha = alpha;

    %% passed
    passed = (score >= 90);
end

function out = tern(cond, a, b)
    if cond, out = a; else out = b; end
end