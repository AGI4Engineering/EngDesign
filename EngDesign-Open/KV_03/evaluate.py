from output_structure import Response_structure

# Define acceptable aliases for each correct answer
GOLDEN_ANSWERS = {
    "A": ["max", "max block", "maximum", "maximum soc", "maximum value", "max(soc1,soc2,soc3)", "PI Controller"],
    "B": ["chargingenabled", "charging enabled", "chargingenabled input", "enable", "enable signal", "boolean enable"],
    "C": ["cellvoltage", "cell voltage input", "pack voltage", "voltage input", "voltage feedback", "measured voltage"],
    "D": ["currentwhencharging", "charging current", "charging input", "positive current", "input current when charging"],
    "E": ["currentwhendischarging", "discharging current", "discharging input", "negative current", "input current when discharging"],
    "F": ["gain","Gain","gain block", "-1 gain", "negation block", "multiply by -1", "negator", "Control Logic"],
    "G": ["constant", "constant block", "constant value", "current magnitude"],
    "I": ["max", "max block", "maximum", "maximum voltage", "max(cellvoltages)", "voltage selector"],
    "J": ["current output port", "current", "cc-cv output", "outport", "output current", "current port"]
}

def normalize(text: str) -> str:
    return text.strip().lower().replace(" ", "").replace("-", "")

def evaluate_llm_response(response: Response_structure):
    try:
        response_dict = response.config.dict()
        detailed_result = {}
        correct_count = 0
        total_labels = len(GOLDEN_ANSWERS)
        points_per_label = 10  # Flat per-label scoring

        for label in GOLDEN_ANSWERS:
            accepted_names = GOLDEN_ANSWERS[label]
            prediction = response_dict.get(label, "")
            prediction_normalized = normalize(prediction)
            accepted_normalized = [normalize(alias) for alias in accepted_names]

            match = prediction_normalized in accepted_normalized
            score = points_per_label if match else 0

            detailed_result[label] = {
                "predicted": prediction,
                "normalized": prediction_normalized,
                "accepted": accepted_names,
                "correct": match,
                "score": score
            }

            correct_count += (1 if match else 0)

        base_score = correct_count * points_per_label
        bonus = 10 if correct_count == total_labels else 0
        final_score = base_score + bonus

        passed = final_score >= 80
        confidence = final_score

        return passed, detailed_result, final_score, confidence
    except Exception as e:
        return False, {"error": str(e)}, None, None
