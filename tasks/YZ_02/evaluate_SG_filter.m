function [passed, details, score] = evaluate_SG_filter(coeff_1, coeff_2)
    % Evaluate converter performance
    % Inputs:
    %   coeff_1: list of coefficients for analytical expression (1)
    %   coeff_2: list of coefficients for analytical expression (2)
    % Outputs:
    %   passed: boolean indicating if all requirements are met
    %   details: struct with detailed evaluation results
    %   score: score for the converter
    
    try
        % Design an SG filter using 6th-order polynomials and with the half width of 50 samples
        m = 6;
        nh = 50;

        % Compute the cutoff frequency for the SG filter using analytical expression (1).
        Fs = 1000;
        F3dB = Fs/(coeff_1(1)*(nh+1/2)/(m+coeff_1(2)) - (coeff_1(3)+coeff_1(4)*m)/(nh+1/2));
        
        % Cheek the cutoff frequency
        desired_F3dB = 0.023;
        check_1 = abs(F3dB/Fs - desired_F3dB) <= 0.003;

        % Compute the half-magnitude interval for the SG filter with weighting using analytical expression (2).
        nhW = round((coeff_2(1)+coeff_2(2)*m+coeff_2(3)*m^2)/(F3dB/Fs)-1);
        check_2 = nhW > nh;

        % Design an SG filter using squared Hann weights
        flW = 2*nhW+1;
        weightsSqHann = hann(flW+2).^2;
        weightsSqHann([1 end]) = [];
        [~,gSGwSqHann] = sgolay(m,flW,weightsSqHann);
        gSGwSqHann = gSGwSqHann(:,1);

        % Design a SG filter with optimal weighting
        Tn = toeplitz([2 -1 zeros(1,flW-2)]);
        v = ones(flW,1);
        weightsOptimal = Tn\v;
        [~,gSGwOptimal] = sgolay(m,flW,weightsOptimal);
        gSGwOptimal = gSGwOptimal(:,1);

        % Design a SG filter with triangular weighting
        weightsTriang = triang(flW);
        [~,gSGwTriang] = sgolay(m,flW,weightsTriang);
        gSGwTriang = gSGwTriang(:,1);

        % Design a SG filter with no weighting
        [~,gSGwNone] = sgolay(m,flW);
        gSGwNone = gSGwNone(:,1);

        % Compute the output vs. input noise ratio, and smoothness for SG filters
        rSGwNone = gSGwNone'*gSGwNone;
        sSGwNone = diff([0;gSGwNone;0]);
        sSGwNone = sum(abs(sSGwNone).^2)/2;

        rSGwSqHann = gSGwSqHann'*gSGwSqHann;
        sSGwSqHann = diff([0;gSGwSqHann;0]);
        sSGwSqHann = sum(abs(sSGwSqHann).^2)/2;

        rSGwTriang = gSGwTriang'*gSGwTriang;
        sSGwTriang = diff([0;gSGwTriang;0]); 
        sSGwTriang = sum(abs(sSGwTriang).^2)/2;

        rSGwOptimal = gSGwOptimal'*gSGwOptimal;
        sSGwOptimal = diff([0;gSGwOptimal;0]); 
        sSGwOptimal = sum(abs(sSGwOptimal).^2)/2;

        temp = num2cell(db([rSGwNone; rSGwSqHann; rSGwTriang; rSGwOptimal]));
        [rSGwNone, rSGwSqHann, rSGwTriang, rSGwOptimal] = temp{:};
        temp = num2cell(db([sSGwNone; sSGwSqHann; sSGwTriang; sSGwOptimal]));
        [sSGwNone, sSGwSqHann, sSGwTriang, sSGwOptimal] = temp{:};

        % Check the output vs. input noise ratio and smoothness for SG filters
        check_3 = max([rSGwNone, rSGwSqHann, rSGwTriang, rSGwOptimal]) < -25.0;
        check_4 = max([sSGwNone, sSGwSqHann, sSGwTriang, sSGwOptimal]) < -69.0;

        % Check the relation of output vs. input noise and smoothness of the SG filter
        check_5 = max([sSGwSqHann, sSGwTriang, sSGwOptimal]) < sSGwNone;
        check_6 = min([rSGwSqHann, rSGwTriang, rSGwOptimal]) > rSGwNone;

        % Check the SG filter with optimal weighting
        check_7 = sSGwOptimal < min([sSGwNone, sSGwSqHann, sSGwTriang]);

        % Compile results
        passed = check_1 && check_2 && check_3 && check_4 && check_5 && check_6 && check_7;

        % Scoring
        score = 0;
        if check_1
            score = score + 25;
        end
        if check_2
            score = score + 25;
        end
        if check_3
            score = score + 10;
        end
        if check_4
            score = score + 10;
        end
        if check_5
            score = score + 10;
        end
        if check_6
            score = score + 10;
        end
        if check_7
            score = score + 10;
        end
        
        
        details = struct();
        details.coeff_1 = coeff_1;
        details.coeff_2 = coeff_2;
        details.F3dB = F3dB/Fs;
        details.nhW = nhW;
        details.rSGwNone = rSGwNone;
        details.rSGwSqHann = rSGwSqHann;
        details.rSGwTriang = rSGwTriang;
        details.rSGwOptimal = rSGwOptimal;
        details.sSGwNone = sSGwNone;
        details.sSGwSqHann = sSGwSqHann;
        details.sSGwTriang = sSGwTriang;
        details.sSGwOptimal = sSGwOptimal;
        details.check_1 = check_1;
        details.check_2 = check_2;
        details.check_3 = check_3;
        details.check_4 = check_4;
        details.check_5 = check_5;
        details.check_6 = check_6;
        details.check_7 = check_7;
        
    catch ME
        % Handle any errors that occur during evaluation
        passed = false;
        details = struct('Error', ME.message);
        score = 0;
    end
    
end
