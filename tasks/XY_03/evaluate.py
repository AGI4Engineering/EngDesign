import numpy as np
import os

def evaluate_llm_response(llm_response):
    try:
        score = 0
        details = {}
        confidence = 100

        config = llm_response.config
        counter_bits = config.counter_bits
        division_ratio = config.division_ratio
        digit_select_positions = config.digit_select_bits
        max_delay = config.max_delay_ms
        flicker_possible = config.is_flicker_possible

        # Counter bits check: must be >=17 and <=19
        if 17 <= counter_bits <= 19:
            score += 30
            details["counter_bits"] = f"{counter_bits} bits is within acceptable engineering range (17-19)"
        else:
            details["counter_bits"] = f"{counter_bits} bits is outside expected range (17-19)"

        # Division ratio check: target is 208333, allow ±1000
        expected_ratio = 50000000 / (60 * 4)
        if abs(division_ratio - expected_ratio) <= 1000:
            score += 25
            details["division_ratio"] = f"{division_ratio} is within ±1000 of 208333"
        else:
            details["division_ratio"] = f"{division_ratio} is too far from 208333"

        # Digit select bits: should be 2 consecutive bits near the top of counter
        if isinstance(digit_select_positions, list) and len(digit_select_positions) == 2:
            bits_sorted = sorted(digit_select_positions)
            if (
                bits_sorted[1] - bits_sorted[0] == 1 and
                bits_sorted[1] <= counter_bits - 1 and
                bits_sorted[0] >= counter_bits - 4
            ):
                score += 25
                details["digit_select_bits"] = f"{digit_select_positions} are valid consecutive high-order bits"
            else:
                score += 25
                details["digit_select_bits"] = f"Bits present but position range is not ideal: {digit_select_positions}"
        else:
            details["digit_select_bits"] = "Invalid or improperly formatted digit select bits"

        # Check max delay calculation
        expected_delay = (1000/60) + ((100e-6) * 50000000 * (1000/60)) + (5 * (1000/50000000))
        if abs(max_delay - expected_delay) / expected_delay <= 0.05:  # Within 5% of expected
            score += 10
            details["max_delay"] = f"Maximum delay calculation of {max_delay}ms is correct"
        else:
            details["max_delay"] = f"Maximum delay calculation of {max_delay}ms is incorrect"

        # Check flicker assessment
        expected_flicker = expected_delay > (1000/30)  # Flicker threshold around 30Hz
        if flicker_possible == expected_flicker:
            score += 10
            details["flicker_assessment"] = "Correct assessment of flicker possibility"
        else:
            details["flicker_assessment"] = "Incorrect assessment of flicker possibility"

        passed = score >= 90
        print("Score:", score)
        return passed, details, score, confidence

    except Exception as e:
        return False, {"error": str(e)}, 0, 0