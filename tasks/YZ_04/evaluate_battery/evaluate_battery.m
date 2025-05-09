function [passed, details, score] = evaluate_battery(numCells_p, numCells_s, NumChannel, Flowrate, ChannelDia)
    % Evaluate converter performance
    % Inputs:
    %   numCells_p: number of cells in parallel
    %   numCells_s: number of cells in series
    %   NumChannel: number of cooling channels
    %   Flowrate: flow rate of the coolant
    %   ChannelDia: diameter of the cooling channels

    % Outputs:
    %   passed: boolean indicating if all requirements are met
    %   details: struct with detailed evaluation results
    %   score: score for the converter
    
    try
        check_1 = numCells_p >= 3;
        check_2 = numCells_s >= 5;

        % load a pre-generated battery module library. 
        batteryLFP = load('BattDetailedModuleLFP.mat');

        % Specify the maximum acceptable temperature gradient in the battery module
        requirements.MaxModuleTgrad  = 5;
        % Specify the maximum acceptable temperature rise within the battery module
        requirements.MaxCellTempInc  = 10;
        % Specify the maximum acceptable pressure drop for the module cooling system
        requirements.MaxPressureDrop = 20000;

        % thermal mass variation of the battery cell
        thermalMassPercentDev.cellToCell = ...
        [0.104874716016494
        0.722254032225002
        2.58549125261624
        -0.666890670701386
        0.187331024578940
        -0.0824944253709554
        -1.93302291785099
        -0.438966153934773
        -1.79467884145512
        0.840375529753905
        -0.888032082329010
        0.100092833139322
        -0.544528929990548
        0.303520794649354
        -0.600326562133734];

        run('setBattModuleCoolingPlate_param');
        
        % Set the operating parameters
        chargingParams.SOC = 0.05;  % Initial battery state of charge
        chargingParams.T = 300;     % Initial battery temperature, K
        chargingParams.I = 100;     % Charging current, A
        chargingParams.time = 1200; % Charging time, s
        chargingParams.CoolT = 300; % Coolant inlet temperature, K
        chargingParams.Flow = 3;    % Flowrate, lpm

        % Specify the design parameters
        designParams.NumChannelOptions = NumChannel;
        designParams.FlowrateOptions = Flowrate;
        designParams.ChannelDiaOptions = ChannelDia;

        % Simulate the test
        simResults = getBattModuleThermalDesign(designParams, chargingParams, thermalMassPercentDev.cellToCell);

        % Check the conditions
        check_3 = simResults.("Max. Gradient Tcell") <= requirements.MaxModuleTgrad;
        check_4 = simResults.("Max. Tcell") - chargingParams.T <= requirements.MaxCellTempInc;
        check_5 = simResults.("Pressure Drop") <= requirements.MaxPressureDrop;

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
        details.numCells_p = numCells_p;
        details.numCells_s = numCells_s;
        details.NumChannel = NumChannel;
        details.Flowrate = Flowrate;
        details.ChannelDia = ChannelDia;
        details.MaxModuleTgrad = simResults.("Max. Gradient Tcell");
        details.MaxCellTempInc = simResults.("Max. Tcell") - chargingParams.T;
        details.MaxPressureDrop = simResults.("Pressure Drop");
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
