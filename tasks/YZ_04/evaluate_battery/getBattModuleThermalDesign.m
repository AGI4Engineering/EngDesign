%% Run all design scenarios

% Copyright 2023 The MathWorks, Inc.

function simResults = getBattModuleThermalDesign(designOptions, operationalParams, thermalMassPercentDevValues)
    numChannelOptions = designOptions.NumChannelOptions;
    flowrateOptions = designOptions.FlowrateOptions;
    channelDiaOptions = designOptions.ChannelDiaOptions;
    designParams.Options = findFullFactorial(length(numChannelOptions),length(flowrateOptions),length(channelDiaOptions));
    totalNumOptions = size(designParams.Options,1);
    simData = zeros(totalNumOptions,6);
    % Run
    disp(strcat('Total number of simulations = ',num2str(totalNumOptions)));
    for itr = 1:totalNumOptions
        load_system('BattModuleThermalMgmtLFP');
        run('setBattModuleParameters');
        chargingParams.SOC = operationalParams.SOC;     % Initial battery state of charge
        chargingParams.T = operationalParams.T;         % Initial battery temperature, K
        chargingParams.I = operationalParams.I;         % Charging current, A
        chargingParams.time = operationalParams.time;   % Charging time, s
        chargingParams.CoolT = operationalParams.CoolT; % Coolant inlet temperature, K
        chargingParams.Flow = operationalParams.Flow;   % Flowrate, lpm
        Detailed.thermal_massCellPercentDeviation = thermalMassPercentDevValues;
        idx1 = designParams.Options(itr,1);
        idx2 = designParams.Options(itr,2);
        idx3 = designParams.Options(itr,3);
        CP.Design.NumCh = numChannelOptions(1,idx1);
        CP.Design.Dc = channelDiaOptions(1,idx3);
        chargingParams.Flow = flowrateOptions(1,idx2);
        % Display message of progress
        strNumCh = num2str(numChannelOptions(1,idx1));
        strFlow  = num2str(flowrateOptions(1,idx2));
        strChDia = num2str(channelDiaOptions(1,idx3)*1000);
        disp(strcat('Simulating case # ',num2str(itr),' : flow = ',strFlow,...
            ' lpm, Channel Dia = ',strChDia,' mm and Num. of Channels = ',strNumCh));
        simRes = sim('BattModuleThermalMgmtLFP','SrcWorkspace','Current');
        battRes.Tvec = simRes.simlog_batteryModuleLFP.Detailed.temperatureCell.series.values;
        battRes.Tmax = max(battRes.Tvec');
        battRes.Tmin = min(battRes.Tvec');
        deltaT = max(battRes.Tmax-battRes.Tmin);
        maxT   = max(battRes.Tmax');
        deltaP = max(abs(simRes.simlog_batteryModuleLFP.Parallel_Channels.presSensor.series.values));
        simData(itr,:) = [deltaT, maxT, deltaP, numChannelOptions(1,idx1), ...
                          flowrateOptions(1,idx2), channelDiaOptions(1,idx3)];
    end
    % Save data in a Table
    simResults = array2table(simData,...
        'VariableNames',{'Max. Gradient Tcell','Max. Tcell','Pressure Drop',...
        'Num. Channels','Flowrate','Channel Diameter'});
end

function mat = findFullFactorial(prm1,prm2,prm3)
    totData = prm1*prm2*prm3;
    mat     = zeros(totData,3);
    count = 0;
    for k = 1:prm3
        for j = 1:prm2
            for i = 1:prm1
                count = count + 1;
                mat(count,1) = i;
                mat(count,2) = j;
                mat(count,3) = k;
            end
        end
    end
end