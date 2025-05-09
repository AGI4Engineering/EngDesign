import numpy as np
import matlab.engine
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


def evaluate_llm_response(llm_response):
    """
    Evaluates the LLM-generated design parameters for antenna modelling.

    Parameters:
    - llm_response: dict with keys (Design parameters)
    Returns:
    - (bool, dict, float, float): success, detailed_results, score, confidence
    """
    try:
    
        # Start MATLAB engine
        eng = matlab.engine.start_matlab()
        current_dir = os.path.dirname(os.path.abspath(__file__))
        eng.addpath(current_dir)

        # Access the config from the Response_structure instance
        config = llm_response.config
        print(config)
        
        # Extract design parameters
        height_mm = config.height_mm
        radius_mm = config.radius_mm
            
        confidence = 0.0

        # Target specs
        target_operating_frequency_GHz = 0.487     
        target_bandwidth = 10.0
        target_gain = 0.0

        # Frequency sweep
        fmin_GHz = target_operating_frequency_GHz - 0.3
        fmax_GHz = target_operating_frequency_GHz + 0.3
        nfreq = 80


        # Pack parameters
        params = {
            'Height': height_mm * 1e-3,
            'Radius': radius_mm * 1e-3,
            'Fmin': fmin_GHz * 1e9,
            'Fmax': fmax_GHz * 1e9,
            'Nfreq': nfreq,
        }

        # Convert to MATLAB struct
        params_matlab = eng.struct(
            'Height', params['Height'],
            'Radius', params['Radius'],
            'Fmin', params['Fmin'],
            'Fmax', params['Fmax'],
            'Nfreq', params['Nfreq'],
        )

        # Run MATLAB function
        results = eng.analyze_monopole_antenna_f(params_matlab)

        # Extract results
        results_dict = {
            'ResonantFrequencyGHz': float(results['f_resonant']) / 1e9,
            'S11_resonant_dB': float(results['S11_resonant']),
            'BandwidthMHz': float(results['bandwidth']) / 1e6,
            'MaxGaindBi': float(results['maxGain']),
        }

        # Print results
        print("\nPatch Antenna Analysis Results:")
        print("------------------------------------")
        print(f"Resonant Frequency      : {results_dict['ResonantFrequencyGHz']:.3f} GHz")
        print(f"S11 @ Resonant Frequency: {results_dict['S11_resonant_dB']:.2f} dB")
        print(f"Bandwidth (-10 dB)      : {results_dict['BandwidthMHz']:.2f} MHz")
        print(f"Max Gain                : {results_dict['MaxGaindBi']:.2f} dBi")
        print("------------------------------------")

        # Scoring
        score = 0
        freq_error_GHz = abs(results_dict['ResonantFrequencyGHz'] - target_operating_frequency_GHz)
        bandwidth_GHz = target_bandwidth / 1000.0
        penalty = min(40.0, (freq_error_GHz / bandwidth_GHz) * 40.0)
        score += max(0.0, 40.0 - penalty)

        if (results_dict['S11_resonant_dB'] <= -10.0):
            score += 20.0

        if results_dict['BandwidthMHz'] >= target_bandwidth:
            score += 20.0

        if results_dict['MaxGaindBi'] >= target_gain:
            score += 20.0

        print(f"✅ Final Score: {score:.1f} / 100")

        eng.quit()
        
        if (score < 100.0):
            return False, results_dict, score, confidence
        else:
            return True, results_dict, score, confidence
    except Exception as e:
        return False, {}, None, None


