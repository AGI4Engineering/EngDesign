import numpy as np
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from scipy.signal import freqz

def evaluate_llm_response(llm_response):
    try:
        # response data
        order = llm_response.config.order
        coeffs = llm_response.config.coeffs
        stpbnd = llm_response.config.stpbnd
        decim = llm_response.config.decim

        # sampling freq
        fs = 48000

        # testing frequency response
        w, h = freqz(coeffs, worN=10000, fs=fs)

        passband_edge = 3500
        stopband_edge = 4000        # nyquist freq. = 8k/2, attenuate here to prevent aliasing

        # defining freq ranges
        passband_freqs = np.linspace(0, passband_edge, num=passband_edge)
        stopband_freqs = np.linspace(stopband_edge, 10000, num=(10000-stopband_edge))
        trans_band_freqs = np.linspace(passband_edge, stopband_edge, num=20)

        passband_mag_db = 20 * np.log10(np.abs(np.interp(passband_freqs, w, np.abs(h))))
        stopband_mag_db = 20 * np.log10(np.abs(np.interp(stopband_freqs, w, np.abs(h))))
        trans_band_mag_db = 20 * np.log10(np.abs(np.interp(trans_band_freqs, w, np.abs(h))))

        # freq att. checks
        pass_ok = np.all(passband_mag_db[:] >= -3)
        stop_ok = np.all(stopband_mag_db[1:] <= -40)
        trans_ok = np.all(trans_band_mag_db[1:] <= 0)

        order_ok = order <= 350

        ord_coeff_ok = len(coeffs) == order + 1

        stpbnd_ok = stpbnd <= stopband_edge and stpbnd >= passband_edge

        decim_ok = decim == 6       # 6 = 48k/8k

        out_pass = pass_ok and stop_ok and trans_ok and order_ok and ord_coeff_ok and stpbnd_ok and decim_ok
        out_confidence = 100

        score_weights = {
            'pass_ok': 0.2,
            'stop_ok': 0.2,
            'trans_ok': 0.1,
            'order_ok': 0.1,
            'ord_coeff_ok': 0.1,
            'stpbnd_ok': 0.2,
            'decim_ok': 0.1,
        }

        out_score = (
            pass_ok * score_weights['pass_ok'] +
            stop_ok * score_weights['stop_ok'] +
            trans_ok * score_weights['trans_ok'] +
            order_ok * score_weights['order_ok'] +
            ord_coeff_ok * score_weights['ord_coeff_ok'] +
            stpbnd_ok * score_weights['stpbnd_ok'] +
            decim_ok * score_weights['decim_ok']
        )

        out_details = {
            'order': order,
            'coefficients': coeffs,
            'passband attenuation appropriate': pass_ok,
            'stopband attenuation appropriate': stop_ok,
            'transition band attenuation appropriate': trans_ok,
            'order value reasonable': order_ok,
            'order and coefficient are properly related': ord_coeff_ok,
            'stopband placement ok': stpbnd_ok,
            'decimation value ok': decim_ok
        }

        return bool(out_pass), out_details, float(out_score*100), out_confidence

    except Exception as e:
        return False, {"error": str(e)}, None, None



# if __name__ == '__main__':
#     llm_response = {'order': 152,
#                     'coeffs': [
#  0.00232738107555552, 0.00922695722813153, 0.00773033917903762, 0.011467831400938,
#  0.0130519186698972, 0.0142389626702959, 0.0141145009286556, 0.0127583114233367,
#  0.0101950629216487, 0.00673092905298647, 0.00281708981094565, -0.000989111837913679,
#  -0.00412542696720445, -0.00613245484652375, -0.00673660822454754, -0.00591291832328676,
#  -0.0038953392590717, -0.00113926230890725, 0.00176396710143443, 0.00419786351015542,
#  0.00564840166073773, 0.00580756594621445, 0.00464445298669579, 0.00241228167119975,
#  -0.000397669974056063, -0.00315982882169413, -0.00524744854759474, -0.00616986696094999,
#  -0.00568247559741705, -0.00385592454536345, -0.00106403936072277, 0.00208332493247689,
#  0.00487403487574822, 0.00664694705563115, 0.00694721768045664, 0.00563545948236604,
#  0.0029367766419419, -0.000594710231142497, -0.00417976478398229, -0.00698840207668458,
#  -0.00831987312345981, -0.00777957197983195, -0.00537445654384982, -0.00154892311762374,
#  0.00290028621208456, 0.00697325912690389, 0.00969398673006019, 0.0103270091241112,
#  0.00857004984320211, 0.00464620894288635, -0.000701784673323982, -0.00633825404810223,
#  -0.0109688379389773, -0.0134143833101943, -0.0129019693176223, -0.00925627777003295,
#  -0.00301675399545622, 0.00463235208238579, 0.0120480796329622, 0.0174615092828941,
#  0.0193499478544405, 0.0167930690495342, 0.00976493801295727, -0.000765219115060084,
#  -0.0128992159389074, -0.0240790927115354, -0.0315059134402624, -0.0326387641547852,
#  -0.0257112150757533, -0.0101072713378632, 0.0134159322827348, 0.0427294055451825,
#  0.0746102579926494, 0.105187437495629, 0.130520665714103, 0.147243791678331,
#  0.153086920312013, 0.147243791678331, 0.130520665714103, 0.105187437495629,
#  0.0746102579926494, 0.0427294055451825, 0.0134159322827348, -0.0101072713378632,
#  -0.0257112150757533, -0.0326387641547852, -0.0315059134402624, -0.0240790927115354,
#  -0.0128992159389074, -0.000765219115060084, 0.00976493801295727, 0.0167930690495342,
#  0.0193499478544405, 0.0174615092828941, 0.0120480796329622, 0.00463235208238579,
#  -0.00301675399545622, -0.00925627777003295, -0.0129019693176223, -0.0134143833101943,
#  -0.0109688379389773, -0.00633825404810223, -0.000701784673323982, 0.00464620894288635,
#  0.00857004984320211, 0.0103270091241112, 0.00969398673006019, 0.00697325912690389,
#  0.00290028621208456, -0.00154892311762374, -0.00537445654384982, -0.00777957197983195,
#  -0.00831987312345981, -0.00698840207668458, -0.00417976478398229, -0.000594710231142497,
#  0.0029367766419419, 0.00563545948236604, 0.00694721768045664, 0.00664694705563115,
#  0.00487403487574822, 0.00208332493247689, -0.00106403936072277, -0.00385592454536345,
#  -0.00568247559741705, -0.00616986696094999, -0.00524744854759474, -0.00315982882169413,
#  -0.000397669974056063, 0.00241228167119975, 0.00464445298669579, 0.00580756594621445,
#  0.00564840166073773, 0.00419786351015542, 0.00176396710143443, -0.00113926230890725,
#  -0.0038953392590717, -0.00591291832328676, -0.00673660822454754, -0.00613245484652375,
#  -0.00412542696720445, -0.000989111837913679, 0.00281708981094565, 0.00673092905298647,
#  0.0101950629216487, 0.0127583114233367, 0.0141145009286556, 0.0142389626702959,
#  0.0130519186698972, 0.011467831400938, 0.00773033917903762, 0.00922695722813153,
#  0.00232738107555552
# ],
#                     'stpbnd': 3900,
#                     'decim': 6,}
#
#     print(evaluate_llm_response(llm_response))