def evaluate_answer(reference: float, response: float, abs_tolerance: float) -> int:
    """
    Evaluate whether the given response is within the acceptable absolute error range of the reference answer.

    Parameters:
    - reference (float): the correct or standard answer.
    - response (float): the value provided by the user.
    - abs_tolerance (float): allowed absolute error (tolerance).

    Returns:
    - int: 1 if response is within [reference - abs_tolerance, reference + abs_tolerance], otherwise 0.
    """
    if abs(response - reference) <= abs_tolerance:
        return 1
    else:
        return 0


def evaluate_llm_response(llm_response):
    try:
        total_score = 0
        detailed_info = ""

        # LLM predicted output
        config = llm_response.config

        if evaluate_answer(18.32, config.SNRatRm, config.tor1):
            total_score += 5
            detailed_info += "The available SNR calculated in Task 1 is correct.\n"
        else:
            detailed_info += "The available SNR calculated in Task 1 is wrong.\n"

        if evaluate_answer(13.12, config.D0, config.tor2):
            total_score += 5
            detailed_info += "The required SNR for a single pulse received from a steady target calculated in Task 2 is correct.\n"
        else:
            detailed_info += "The required SNR for a single pulse received from a steady target calculated in Task 2 is wrong.\n"

        if evaluate_answer(21.14, config.D1, config.tor3):
            total_score += 5
            detailed_info += "The required SNR for a single pulse received from a fluctuating target calculated in Task 3 is correct.\n"
        else:
            detailed_info += "The required SNR for a single pulse received from a fluctuating target calculated in Task 3 is wrong.\n"

        if evaluate_answer(13.50, config.DN, config.tor4):
            total_score += 5
            detailed_info += "The required SNR for 10 noncoherently integrated pulses received from a fluctuating target calculated in Task 4 is correct.\n"
        else:
            detailed_info += "The required SNR for 10 noncoherently integrated pulses received from a fluctuating target calculated in Task 4 is wrong.\n"

        if evaluate_answer(7.79, config.Gi, config.tor5):
            total_score += 5
            detailed_info += "The integration gain calculated in Task 5 is correct.\n"
        else:
            detailed_info += "The integration gain calculated in Task 5 is wrong.\n"

        if evaluate_answer(8.17, config.Lf, config.tor6):
            total_score += 5
            detailed_info += "The fluctuation loss calculated in Task 6 is correct.\n"
        else:
            detailed_info += "The fluctuation loss calculated in Task 6 is wrong.\n"

        if evaluate_answer(131.93, config.actual_Rm, config.tor7):
            total_score += 5
            detailed_info += "The actual maximum range of the system calculated in Task 7 is correct.\n"
        else:
            detailed_info += "The actual maximum range of the system calculated in Task 7 is wrong.\n"

        if evaluate_answer(1.65, config.Rmin, config.tor8):
            total_score += 5
            detailed_info += "The closest range from which a full pulse can be received calculated in Task 8 is correct.\n"
        else:
            detailed_info += "The closest range from which a full pulse can be received calculated in Task 8 is wrong.\n"

        if evaluate_answer(111.03, config.Rua, config.tor9):
            total_score += 5
            detailed_info += "The unambiguous range of the system calculated in Task 9 is correct.\n"
        else:
            detailed_info += "The unambiguous range of the system calculated in Task 9 is wrong.\n"

        if evaluate_answer(2.7745, config.scan_sector_loss, config.tor10):
            total_score += 10
            detailed_info += "The scan sector loss calculated in Task 10 is correct.\n"
        else:
            detailed_info += "The scan sector loss calculated in Task 10 is wrong.\n"

        if evaluate_answer(1.4468, config.Lmti_a, config.tor11_a):
            total_score += 5
            detailed_info += "The MTI noise correlation loss calculated in Task 11 is correct.\n"
        else:
            detailed_info += "The MTI noise correlation loss calculated in Task 11 is wrong.\n"

        if evaluate_answer(8.1562, config.Lmti_b, config.tor11_b):
            total_score += 5
            detailed_info += "The MTI velocity response loss calculated in Task 11 is correct.\n"
        else:
            detailed_info += "The MTI velocity response loss calculated in Task 11 is wrong.\n"

        if evaluate_answer(1.0549, config.binary_integration_loss, config.tor12):
            total_score += 10
            detailed_info += "The binary integration loss calculated in Task 12 is correct.\n"
        else:
            detailed_info += "The binary integration loss calculated in Task 12 is wrong.\n"

        if evaluate_answer(0.2500, config.cfar_loss, config.tor13):
            total_score += 10
            detailed_info += "The CFAR loss calculated in Task 13 is correct.\n"
        else:
            detailed_info += "The CFAR loss calculated in Task 13 is wrong.\n"

        if evaluate_answer(28.42, config.effective_df, config.tor14):
            total_score += 10
            detailed_info += "The effective detectability factor gained from Task 14 is correct.\n"
        else:
            detailed_info += "The effective detectability factor gained from Task 14 is wrong.\n"

        if config.evaluate_system_feasibility == 0:
            total_score += 5
            detailed_info += "The evaluation of whether or not this radar system can satisfy the performance requirement is correct.\n"
        else:
            detailed_info += "The evaluation of whether or not this radar system can satisfy the performance requirement is wrong.\n"

        passed = total_score == 100

        details = {
            "detailed information": detailed_info,
            "total_score": total_score
        }

        return passed, details, total_score, 100

    except Exception as e:
        return False, {"error": str(e)}, None, None
