classdef SRCTestUtils
    % Class containing functions for the LTE sample rate conversion example.
    
    methods (Static)
        
        function setPlotNameAndTitle(plotName)
            title(plotName);
            set(gcf,'Name',plotName);
        end
        
        function [evm, eqSymbols] = MeasureEVM(enb,sigIn,FsIn)
            
            % Resample the input from FsIn to the rate expected 
            % by the LTE receiver functions.
            sig = resample(sigIn,enb.SamplingRate,FsIn);
            
            % EVM Measurement
            offset = lteDLFrameOffset(enb,sig);
            sig = sig(1+offset:end,:);    % remove transient
            sig = [sig; zeros(offset,1)]; % pad with zeros
            
            rxGrid = lteOFDMDemodulate(enb,sig);
            chGrid = lteDLChannelEstimate(enb,rxGrid);
            L      = size(rxGrid,2) / enb.TotSubframes;
            
            EV            = [];
            startSubframe = enb.NSubframe;
            
            for n = 0:(enb.TotSubframes-1)
                
                enb.NSubframe = mod(startSubframe + n,10);
                
                rxSubframe = rxGrid(:,(1:L) + (n*L),:);
                chSubframe = chGrid(:,(1:L) + (n*L),:);
                
                crsIndices = lteCellRSIndices(enb);
                [rxSymbols,chSymbols] = ...
                    lteExtractResources(crsIndices,rxSubframe,chSubframe);
                
                eqSymbols = lteEqualizeZF(rxSymbols,chSymbols);
                
                crsSymbols  = lteCellRS(enb);
                evmSubframe = lteEVM(eqSymbols,crsSymbols);
                EV          = [EV; evmSubframe.EV]; %#ok<AGROW>
                
            end
            
            evm = lteEVM(EV);
                        
        end
                                
    end
    
end

