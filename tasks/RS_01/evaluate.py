import numpy as np
#import matlab.engine
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


def evaluate_llm_response(llm_response):
    try:

        from RunOpenLapSim import RunOpenLapSim

        setupFileName = "SetupFile.json"
        # TrackFile.txt
        trackFileName = "TrackFile.txt"
        # Additional Options
        bExport = 0
        bPlot = 0
        bPlotExtra = 0

        score = 0
        passed = False
        confidence = 100

            # object instantiation
        runOpenLapSim = RunOpenLapSim(setupFileName, trackFileName,
                                        bExport, bPlot, bPlotExtra)
        laptime, vcarmax = runOpenLapSim.run()

        laptimediff = laptime - llm_response.config.laptime
        vcarmaxdiff = vcarmax - llm_response.config.vcarmax
        

        details = {"laptime_sol": laptime, "vcarmax_sol": vcarmax, "Lap_time_differnce": laptimediff, "Top_speed_difference": vcarmaxdiff}

        if abs(laptimediff) <= 0.5 and abs(vcarmaxdiff) <= 1:
            score += 50
        if abs(laptimediff) <= 1 and abs(vcarmaxdiff) <= 1.5:
            score += 25
        if abs(laptimediff) <= 1.5 and abs(vcarmaxdiff) <= 2:
            score += 15
        if abs(laptimediff) <= 2 and abs(vcarmaxdiff) <= 2.5:
            score += 10

        if score == 100:
            passed = True

        return passed, details, score, confidence

    except Exception as e:
        return False, ("error: ", str(e)), None, None

