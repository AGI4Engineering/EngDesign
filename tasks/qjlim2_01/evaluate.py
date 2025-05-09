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
        length_mm = config.length_mm
        width_mm = config.width_mm
        height_mm = config.height_mm
        epsilon_r = config.epsilon_r
        feed_offset_x_mm = config.feed_offset_x_mm
        
        
        confidence = 0.0

        # Target specs
        target_operating_frequency_GHz = 1.537
        target_bandwidth = 50.0
        target_gain = 3.0
        target_length_mm = 100.0
        target_width_mm = 100.0
        target_height_mm = 10.0

        # Frequency sweep
        fmin_GHz = target_operating_frequency_GHz - 0.6
        fmax_GHz = target_operating_frequency_GHz + 0.6
        nfreq = 16

        ground_plane_length_mm = max(length_mm, width_mm)

        # Constraint check
        if (ground_plane_length_mm > target_length_mm or
            ground_plane_length_mm > target_width_mm or
            height_mm > target_height_mm):
            print(f"❌ Antenna size too large")
            return False, {}, 0.0, 0.0

        # Pack parameters
        params = {
            'Length': length_mm * 1e-3,
            'Width': width_mm * 1e-3,
            'GroundPlaneLength': ground_plane_length_mm * 1e-3,
            'GroundPlaneWidth': ground_plane_length_mm * 1e-3,
            'Height': height_mm * 1e-3,
            'EpsilonR': epsilon_r,
            'FeedOffset': np.array([feed_offset_x_mm * 1e-3, 0], dtype=float),
            'Fmin': fmin_GHz * 1e9,
            'Fmax': fmax_GHz * 1e9,
            'Nfreq': nfreq,
            'Polarization': 'V'
        }

        # Convert to MATLAB struct
        params_matlab = eng.struct(
            'Length', params['Length'],
            'Width', params['Width'],
            'GroundPlaneLength', params['GroundPlaneLength'],
            'GroundPlaneWidth', params['GroundPlaneWidth'],
            'Height', params['Height'],
            'EpsilonR', params['EpsilonR'],
            'FeedOffset', matlab.double(params['FeedOffset'].tolist()),
            'Fmin', params['Fmin'],
            'Fmax', params['Fmax'],
            'Nfreq', params['Nfreq'],
            'Polarization', params['Polarization']
        )

        # Run MATLAB function
        results = eng.analyze_patch_antenna_f(params_matlab)

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
        return False, {}, 0.0, 0.0

