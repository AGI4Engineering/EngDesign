function [passed, details, score] = verifybounds(bar_alpha,bar_beta,underline_alpha,underline_beta)
    %% Parameters
    optimal_bar_alpha = 1;
    optimal_bar_beta = 1;
    optimal_underline_alpha = 1;
    optimal_underline_beta = 0.5;

    %% task1: Score Calculation
    score = 0;
    
    if bar_alpha == optimal_bar_alpha
        score = score + 25;
    end
    
    if bar_beta == optimal_bar_beta
        score = score + 25;
    end
    
    if underline_alpha == optimal_underline_alpha
        score = score + 25;
    end
    
    if underline_beta == optimal_underline_beta
        score = score + 25;
    end

    %% details
    details.bar_alpha = bar_alpha;
    details.bar_beta = bar_beta;
    details.underline_alpha = underline_alpha;
    details.underline_beta = underline_beta;

    %% passed
    passed = (score == 100);
end

function out = tern(cond, a, b)
    if cond, out = a; else out = b; end
end