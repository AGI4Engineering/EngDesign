function [passed, details, score] = evaluate_controller(A_input, B_input, beta)
    % Physical parameters
    mb = 300;    % kg
    mw = 60;     % kg
    bs = 1000;   % N/m/s
    ks = 16000 ; % N/m
    kt = 190000; % N/m

    % State matrices
    A = [ 0 1 0 0; [-ks -bs ks bs]/mb ; ...
        0 0 0 1; [ks bs -ks-kt -bs]/mw];
    B = [ 0 0; 0 1e3/mb ; 0 0 ; [kt -1e3]/mw];
    C = [1 0 0 0; 1 0 -1 0; A(2,:)];
    D = [0 0; 0 0; B(2,:)];

    % Check matrices with tolerance
    tol = 1e-1;
    A_match = all(abs(A_input - A) <= tol, 'all');
    B_match = all(abs(B_input - B) <= tol, 'all');
    
    % Initialize score and check variables
    score = 0;
    rms_correct = false;
    peak_correct = false;
    attenuation_correct = false;
    
    if A_match && B_match
        AB_correct = true;
        score = 40;
        details = struct();
        details.A_correct = A_match;
        details.B_correct = B_match;
    end

    qcar = ss(A,B,C,D);
    qcar.StateName = {'body travel (m)';'body vel (m/s)';...
            'wheel travel (m)';'wheel vel (m/s)'};
    qcar.InputName = {'r';'fs'};
    qcar.OutputName = {'xb';'sd';'ab'};

    ActNom = tf(1,[1/60 1]);
    ActNom.InputName = 'u';
    ActNom.OutputName = 'fs';
    Wroad = ss(0.07);  Wroad.u = 'd';   Wroad.y = 'r';
    Wact = 0.8*tf([1 50],[1 500]);  Wact.u = 'u';  Wact.y = 'e1';

    % Design part
    HandlingTarget = 0.04 * tf([1/8 1],[1/80 1]);
    ComfortTarget = 0.4 * tf([1/0.45 1],[1/150 1]);
    Wsd = beta/HandlingTarget;
    Wsd.u = 'sd';  Wsd.y = 'e3';
    Wab = (1-beta)/ ComfortTarget;
    Wab.u = 'ab';  Wab.y = 'e2';
    sdmeas  = sumblk('y1 = sd');
    abmeas = sumblk('y2 = ab');
    ICinputs = {'d';'u'};
    ICoutputs = {'e1';'e2';'e3';'y1';'y2'};
    qcaric = connect(qcar,ActNom,Wroad,Wact,Wab,Wsd,...
                    sdmeas,abmeas,ICinputs,ICoutputs);
    ncont = 1; % one control signal, u
    nmeas = 2; % two measurement signals, sd and ab
    K = ss(zeros(ncont,nmeas));
    [K,~,gamma] = hinfsyn(qcaric,nmeas,ncont);
    K.u = {'sd','ab'};  K.y = 'u';
    CL = connect(qcar,ActNom,K,'r',{'xb';'sd';'ab'});
    % Road disturbance
    t = 0:0.0025:1;
    roaddist = zeros(size(t));
    roaddist(1:101) = 0.025*(1-cos(8*pi*t(1:101)));

    % Simulate
    p1 = lsim(qcar(:,1),roaddist,t);
    y1 = lsim(CL,roaddist,t);
    rms_closed = rms(y1(:,1));
    peak_closed = max(abs(y1(:,1)));
    energy_open = trapz(t, p1(:,1).^2);
    energy_closed = trapz(t, y1(:,1).^2);
    attenuation_ratio = energy_closed / energy_open;

    if rms_closed <= 0.012
        score = score + 20;
        rms_correct = true;
    end
    
    if peak_closed <= 0.035
        score = score + 20;
        peak_correct = true;
    end
    
    if attenuation_ratio <= 35
        score = score + 20;
        attenuation_correct = true;
    end

    if A_match && B_match && rms_correct && peak_correct && attenuation_correct
        passed = true;
    else
        passed = false;
    end

    details.A_correct = A_match;
    details.B_correct = B_match;
    details.rms_correct = rms_correct;
    details.peak_correct = peak_correct;
    details.attenuation_correct = attenuation_correct;
    details.rms = rms_closed;
    details.peak = peak_closed;
    details.attenuation = attenuation_ratio;

end