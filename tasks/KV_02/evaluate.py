def evaluate_llm_response(llm_response):
    try:
        # Get values from LLM response
        lowest_current = llm_response.config.lowest_current
        highest_current = llm_response.config.highest_current
        on_threshold = llm_response.config.on_threshold
        off_threshold = llm_response.config.off_threshold

        total_score = 0
        details = {
            "lowest_current": lowest_current,
            "highest_current": highest_current,
            "on_threshold": on_threshold,
            "off_threshold": off_threshold,
            "score_breakdown": {}
        }

        # 1. Lowest current must be >= 0
        if lowest_current >= 0 and lowest_current <= 0.1:
            total_score += 20
            details["score_breakdown"]["lowest_current_valid"] = 20
        else:
            details["score_breakdown"]["lowest_current_valid"] = 0

        # 2. Highest current must be <= 9.15
        if highest_current >= 8.00 and highest_current <= 9.15:
            total_score += 20
            details["score_breakdown"]["highest_current_safe"] = 20
        else:
            details["score_breakdown"]["highest_current_safe"] = 0

        # 3. Highest current must be greater than lowest current
        if highest_current > lowest_current:
            total_score += 20
            details["score_breakdown"]["current_ordering_valid"] = 20
        else:
            details["score_breakdown"]["current_ordering_valid"] = 0

        # 4. Thresholds must be in 0–1 range
        if 0 <= on_threshold <= 1 and 0 <= off_threshold <= 1:
            total_score += 20
            details["score_breakdown"]["threshold_range_valid"] = 20
        else:
            details["score_breakdown"]["threshold_range_valid"] = 0

        # 5. off_threshold must be < on_threshold
        if off_threshold < on_threshold:
            total_score += 20
            details["score_breakdown"]["threshold_ordering_valid"] = 20
        else:
            details["score_breakdown"]["threshold_ordering_valid"] = 0

        passed = total_score == 100
        confidence = 100  # because this is code-based judgment

        return passed, details, total_score, confidence

    except Exception as e:
        return False, {"error": str(e)}, None, None


# # Optional local test
# if __name__ == "__main__":
#     class DummyResponse:
#         class Config:
#             lowest_current = 0.0
#             highest_current = 8.0
#             on_threshold = 0.83
#             off_threshold = 0.80
#         config = Config()

#     passed, details, score, confidence = evaluate_llm_response(DummyResponse())
#     print(f"Passed: {passed}, Score: {score}, Confidence: {confidence}")
#     print(f"Details: {details}")
