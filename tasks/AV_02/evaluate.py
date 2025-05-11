import numpy as np
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from scipy.signal import freqz

def evaluate_llm_response(llm_response):
    try:
        # response data
        order = llm_response.config.order
        coeffs_numerator = llm_response.config.coeffs_numerator
        coeffs_denominator = llm_response.config.coeffs_denominator

        # sampling freq
        fs = 2000

        # testing frequency response
        w, h = freqz(coeffs_numerator, coeffs_denominator, worN=1000, fs=fs)

        target_freq = 120
        lower_stpbnd = 115
        upper_stpbnd= 125

        # defining freq ranges
        lower_pass_freqs = np.linspace(0, lower_stpbnd, num=lower_stpbnd)
        upper_pass_freqs = np.linspace(upper_stpbnd, 250, num=(250-upper_stpbnd))

        #trans_band_freqs = np.linspace(passband_edge, stopband_edge, num=20)

        lower_mag_db = 20 * np.log10(np.abs(np.interp(lower_pass_freqs, w, np.abs(h))))
        upper_mag_db = 20 * np.log10(np.abs(np.interp(upper_pass_freqs, w, np.abs(h))))
        target_mag_db = 20 * np.log10(np.abs(np.interp(target_freq, w, np.abs(h))))

        #trans_band_mag_db = 20 * np.log10(np.abs(np.interp(trans_band_freqs, w, np.abs(h))))

        # freq att. checks
        lower_ok = np.all(lower_mag_db[:] >= -3)
        upper_ok = np.all(upper_mag_db[:] >= -3)
        target_ok = np.all(target_mag_db <= -40)

        order_ok = order <= 50

        ord_coeff_ok = (len(coeffs_numerator) == order + 1) and (len(coeffs_denominator) == order + 1)

        out_pass = lower_ok and upper_ok and target_ok and order_ok and ord_coeff_ok
        out_confidence = 100

        score_weights = {
            'lower_ok': 0.2,
            'upper_ok': 0.2,
            'target_ok': 0.4,
            'order_ok': 0.1,
            'ord_coeff_ok': 0.1,
        }

        out_score = (
            lower_ok * score_weights['lower_ok'] +
            upper_ok * score_weights['upper_ok'] +
            target_ok * score_weights['target_ok'] +
            order_ok * score_weights['order_ok'] +
            ord_coeff_ok * score_weights['ord_coeff_ok']
        )

        out_details = {
            'order': order,
            'numerator coefficients': coeffs_numerator,
            'denominator coefficients': coeffs_denominator,
            'passband below target attenuation appropriate': lower_ok,
            'passband above target attenuation appropriate': upper_ok,
            'target frequency attenuation appropriate': target_ok,
            'order value reasonable': order_ok,
            'order and coefficient are properly related': ord_coeff_ok,
        }

        return bool(out_pass), out_details, float(out_score*100), out_confidence

    except Exception as e:
        return False, {"error": str(e)}, None, None



# if __name__ == '__main__':
#     llm_response = {'order': 8,
#                     'coeffs_denominator': [1, -7.38629070277517, 24.4025053599328, -47.0320991049601, 57.7993568733735, -46.3686717935595, 23.7189260553057, -7.07811076768760, 0.944759805909239],
#                     'coeffs_numerator': [0.971987554400379, -7.23074141988472, 24.0593587574556, -46.7018447646062, 57.8028554708087, -46.7018447646062, 24.0593587574556, -7.23074141988472, 0.971987554400379]
#     }
#
#     print(evaluate_llm_response(llm_response))