function [passed, details, score] = evaluate_antenna(relativeBW, r, D, turns, pitch, side)
    % Evaluate converter performance
    % Inputs:
    %   relativeBW: relative bandwidth of the antenna
    %   r: radius of the cylinder
    %   D: diameter of the antenna
    %   turns: number of helical turns
    %   pitch: pitch of the helix
    %   side: side length of the square ground plane

    % Outputs:
    %   passed: boolean indicating if all requirements are met
    %   details: struct with detailed evaluation results
    %   score: score for the converter
    
    try
        % check the relative bandwidth
        check_1 = abs(relativeBW - 0.45) <= 0.05;

        % design helix antenna
        width = cylinder2strip(r);
        feedheight = 3*r;
        radius = D/2;
        spacing = helixpitch2spacing(pitch,radius);
        radiusGP = side/2;
        hx = helix(Radius=radius,Width=width,Turns=turns,...
                Spacing=spacing,GroundPlaneRadius=radiusGP,...
                FeedStubHeight=feedheight);
        
        % directivity as a function of frequency
        freq = [1.3e9, 1.65e9, 2.0e9];  
        Nf = length(freq);
        Direc = nan(1, Nf);
        for i = 1:Nf
            Direc(i) = pattern(hx, freq(i), 0, 90);
        end

        % check the directivity at 1.3 GHz
        target_freq = 1.3e9;
        [~, idx] = min(abs(freq - target_freq));
        Direc_at_low = Direc(idx);
        check_2 = abs(Direc_at_low - 13) <= 1.5;

        % check the directivity at 1.65 GHz
        target_freq = 1.65e9;
        [~, idx] = min(abs(freq - target_freq));
        Direc_at_center = Direc(idx);
        check_3 = abs(Direc_at_center - 13) <= 1.5;
        
        % check the directivity at 2.0 GHz
        target_freq = 2.0e9;
        [~, idx] = min(abs(freq - target_freq));
        Direc_at_high = Direc(idx);
        check_4 = abs(Direc_at_high - 13) <= 1.5;

        % axial ratio at center frequency
        center_freq = 1.65e9;
        ar_dB = axialRatio(hx, center_freq, 0, 90);

        % check the axial ratio at center frequency
        check_5 = ar_dB < 1.5;

        % Compile results
        passed = check_1 && check_2 && check_3 && check_4 && check_5;

        % Scoring
        score = 0;
        if check_1
            score = score + 20;
        end
        if check_2
            score = score + 20;
        end
        if check_3
            score = score + 20;
        end
        if check_4
            score = score + 20;
        end
        if check_5
            score = score + 20;
        end
        
        
        details = struct();
        details.relativeBW = relativeBW;
        details.r = r;
        details.D = D;
        details.turns = turns;
        details.pitch = pitch;
        details.side = side;
        details.Direc_at_low = Direc_at_low;
        details.Direc_at_center = Direc_at_center;
        details.Direc_at_high = Direc_at_high;
        details.ar_dB = ar_dB;
        details.check_1 = check_1;
        details.check_2 = check_2;
        details.check_3 = check_3;
        details.check_4 = check_4;
        details.check_5 = check_5;
        
    catch ME
        % Handle any errors that occur during evaluation
        passed = false;
        details = struct('Error', ME.message);
        score = 0;
    end
    
end
