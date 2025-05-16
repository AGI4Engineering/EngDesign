function [passed, details, score] = evaluate_converter(Fpass, Fstop, Ast, Ap, Factor_1, Factor_2)
    % Evaluate converter performance
    % Inputs:
    %   Fpass: top level parameter
    %   Fstop: top level parameter
    %   Ast: top level parameter
    %   Ap: top level parameter
    %   Factor_1: model parameter
    %   Factor_2: model parameter
    % Outputs:
    %   passed: boolean indicating if all requirements are met
    %   details: struct with detailed evaluation results
    %   score: score for the converter
    
    try
        % Top level parameters
        FsADC   = 150e6;
        FsLTERx = 30.72e6;
        Fpass   = Fpass * 1e6;
        Fstop   = Fstop * 1e6;

        Fpass_max = 10e6;
        desired_Ast = 50;
        desired_Ap = 0.1;

        Fpass_check = Fpass <= Fpass_max;
        Fstop_check = Fstop > Fpass;

        Ast_check = abs(Ast - desired_Ast) <= 10;
        Ap_check = Ap <= desired_Ap;

        
        % desired_Factor_1= 3;
        % desired_Factor_2= 4;
        % fprintf('Factor_1: %d\n', Factor_1);
        % fprintf('Factor_2: %d\n', Factor_2);

        % Define Farrow rate converter
        farrow.FsIn    = FsADC;
        farrow.FsOut   = Factor_1*Factor_2*FsLTERx;

        % Define decimating FIR filter
        FIRCoeffsDT = numerictype(1,16,15);

        % Define the intermediate FIR filter stage
        interParams.FsIn                = farrow.FsOut;
        interParams.FsOut               = farrow.FsOut/Factor_1;
        interParams.TransitionWidth     = interParams.FsOut - Factor_1*Fpass;
        interParams.StopbandAttenuation = Ast + 10;

        interSpec = fdesign.decimator(Factor_1,'nyquist', Factor_1,...
            'Tw,Ast',...
            interParams.TransitionWidth, ...
            interParams.StopbandAttenuation,...
            interParams.FsIn);

        interband = design(interSpec,'SystemObject',true);

        interband.FullPrecisionOverride = false;
        interband.CoefficientsDataType  = 'Custom';
        interband.CustomCoefficientsDataType = numerictype([],...
            FIRCoeffsDT.WordLength,FIRCoeffsDT.FractionLength);

        % Define the final FIR filter stage

        finalSpec = fdesign.decimator(Factor_2,'lowpass',...
            'Fp,Fst,Ap,Ast',Fpass,Fstop,Ap,Ast,interParams.FsOut);

        finalFilt = design(finalSpec,'equiripple','SystemObject',true);

        finalFilt.FullPrecisionOverride = false;
        finalFilt.CoefficientsDataType  = 'Custom';
        finalFilt.CustomCoefficientsDataType = numerictype([],...
            FIRCoeffsDT.WordLength,FIRCoeffsDT.FractionLength);

        % Validation and Verification
        rng(0);
        enb              = lteRMCDL('R.9');
        enb.TotSubframes = 2;
        [tx, ~, sigInfo] = lteRMCDLTool(enb,randi([0 1],1000,1));
        dataIn = resample(tx,FsADC,sigInfo.SamplingRate);
        dataIn  = 0.95 * dataIn / max(abs(dataIn));

        % Pass the signal through the designed rate converter.
        farrowFilt        = dsp.FarrowRateConverter(farrow.FsIn,farrow.FsOut);
        farrowOut         = farrowFilt(dataIn);
        interFiltOut      = interband(farrowOut);
        floatResamplerOut = finalFilt(interFiltOut);

        % Measure the EVM.
        results.floatPointSRCEVM = SRCTestUtils.MeasureEVM(sigInfo,floatResamplerOut,FsLTERx);
        fpsrEVM = results.floatPointSRCEVM.RMS*100;
        fpspEVM = results.floatPointSRCEVM.Peak*100;

        % Check the EVM and rate change of the Farrow rate filter.
        EVM_check_1 = fpsrEVM <= 0.03;
        EVM_check_2 = fpspEVM <= 0.07;

        % Compile results
        passed = Fpass_check && Fstop_check && Ast_check && Ap_check && EVM_check_1 && EVM_check_2;

        % Scoring
        score = 0;
        if Fpass_check
            score = score + 15;
        end
        if Fstop_check
            score = score + 15;
        end
        if Ast_check
            score = score + 15;
        end
        if Ap_check
            score = score + 15;
        end
        if EVM_check_1
            score = score + 20;
        end
        if EVM_check_2
            score = score + 20;
        end
        
        
        details = struct();
        details.Fpass = Fpass;
        details.Fstop = Fstop;
        details.Ast = Ast;
        details.Ap = Ap;
        details.Factor_1 = Factor_1;
        details.Factor_2 = Factor_2;
        details.fpsrEVM = fpsrEVM;
        details.fpspEVM = fpspEVM;

    catch ME
        % Handle any errors that occur during evaluation
        passed = false;
        details = struct('Error', ME.message);
        score = 0;
    end
    
end
