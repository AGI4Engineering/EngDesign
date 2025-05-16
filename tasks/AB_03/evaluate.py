import cv2
import numpy as np
import importlib.util
import os
import tempfile
import sys
import types
import json
import traceback

SOLUTION_MODULE_NAME = 'solution'
SOLUTION_FUNCTION_NAME = 'get_simplified_contours'

GT_APPROX_VERTICES = np.array([[[ 505,   84]],
                               [[ 402,  165]],
                               [[ 213,  770]],
                               [[ 303,  931]],
                               [[ 272, 1342]],
                               [[ 357, 1389]],
                               [[ 572, 1327]],
                               [[ 691, 1389]],
                               [[ 760, 1256]],
                               [[ 720,  932]],
                               [[ 810,  755]],
                               [[ 729,  393]],
                               [[ 606,  142]]], dtype=np.int32)

GT_HULL_VERTICES = np.array([[[ 522,   84]], [[ 527,   85]], [[ 534,   87]],
                             [[ 540,   89]], [[ 547,   92]], [[ 555,   96]],
                             [[ 560,   99]], [[ 569,  105]], [[ 576,  110]],
                             [[ 584,  117]], [[ 592,  125]], [[ 598,  132]],
                             [[ 603,  138]], [[ 606,  142]], [[ 611,  149]],
                             [[ 615,  155]], [[ 621,  165]], [[ 625,  172]],
                             [[ 630,  182]], [[ 729,  393]], [[ 732,  400]],
                             [[ 735,  408]], [[ 744,  435]], [[ 750,  456]],
                             [[ 755,  475]], [[ 756,  479]], [[ 761,  500]],
                             [[ 766,  522]], [[ 770,  540]], [[ 775,  563]],
                             [[ 783,  603]], [[ 787,  624]], [[ 790,  640]],
                             [[ 798,  684]], [[ 808,  742]], [[ 810,  755]],
                             [[ 810,  774]], [[ 751, 1344]], [[ 750, 1348]],
                             [[ 748, 1354]], [[ 746, 1358]], [[ 742, 1364]],
                             [[ 733, 1373]], [[ 729, 1376]], [[ 724, 1379]],
                             [[ 718, 1382]], [[ 713, 1384]], [[ 707, 1386]],
                             [[ 703, 1387]], [[ 691, 1389]], [[ 333, 1389]],
                             [[ 325, 1388]], [[ 320, 1387]], [[ 316, 1386]],
                             [[ 307, 1383]], [[ 297, 1378]], [[ 294, 1376]],
                             [[ 290, 1373]], [[ 282, 1365]], [[ 279, 1361]],
                             [[ 275, 1353]], [[ 273, 1347]], [[ 272, 1342]],
                             [[ 263, 1256]], [[ 213,  770]], [[ 213,  758]],
                             [[ 215,  745]], [[ 218,  726]], [[ 222,  703]],
                             [[ 228,  669]], [[ 234,  636]], [[ 239,  609]],
                             [[ 242,  593]], [[ 245,  578]], [[ 249,  559]],
                             [[ 255,  532]], [[ 258,  519]], [[ 263,  498]],
                             [[ 270,  470]], [[ 274,  455]], [[ 277,  444]],
                             [[ 281,  430]], [[ 289,  406]], [[ 293,  396]],
                             [[ 392,  185]], [[ 402,  165]], [[ 406,  158]],
                             [[ 411,  150]], [[ 416,  143]], [[ 419,  139]],
                             [[ 423,  134]], [[ 444,  113]], [[ 449,  109]],
                             [[ 453,  106]], [[ 465,   98]], [[ 479,   91]],
                             [[ 491,   87]], [[ 499,   85]], [[ 505,   84]]], dtype=np.int32)

VERTICES_COUNT_WEIGHT = 0.4
BOUNDING_BOX_IOU_WEIGHT = 0.6
PASS_SCORE_THRESHOLD = 95.0

def calculate_iou(box1, box2):
    x1, y1, w1, h1 = box1
    x2, y2, w2, h2 = box2
    xi1 = max(x1, x2)
    yi1 = max(y1, y2)
    xi2 = min(x1 + w1, x2 + w2)
    yi2 = min(y1 + h1, y2 + h2)
    inter_width = max(0, xi2 - xi1)
    inter_height = max(0, yi2 - yi1)
    inter_area = inter_width * inter_height
    box1_area = w1 * h1
    box2_area = w2 * h2
    union_area = box1_area + box2_area - inter_area
    if union_area == 0:
        return 1.0 if inter_area == 0 else 0.0
    else:
        iou = inter_area / union_area
        return iou

def compare_vertices(gt_verts, pred_verts):
    comp_details = {}
    if gt_verts is None or pred_verts is None:
        comp_details['comparison_error'] = "Ground truth or prediction vertices are None."
        return 0.0, comp_details
    if not isinstance(pred_verts, np.ndarray):
         comp_details['comparison_error'] = f"Prediction vertices are not a NumPy array (type: {type(pred_verts)})."
         return 0.0, comp_details
    if not isinstance(gt_verts, np.ndarray):
         comp_details['comparison_error'] = f"Ground truth vertices are not a NumPy array (type: {type(gt_verts)})."
         return 0.0, comp_details

    gt_count = len(gt_verts)
    pred_count = len(pred_verts)
    count_match = (gt_count == pred_count)
    count_score = 1.0 if count_match else 0.0
    comp_details['vertex_count_match'] = count_match
    comp_details['gt_vertex_count'] = gt_count
    comp_details['pred_vertex_count'] = pred_count

    bbox_iou = 0.0
    try:
        if gt_verts.ndim < 2 or gt_verts.shape[0] == 0:
             raise ValueError("Ground truth vertices not suitable for boundingRect (ndim < 2 or empty).")
        if pred_verts.ndim < 2 or pred_verts.shape[0] == 0:
             raise ValueError("Prediction vertices not suitable for boundingRect (ndim < 2 or empty).")

        gt_bbox = cv2.boundingRect(gt_verts)
        pred_bbox = cv2.boundingRect(pred_verts)
        bbox_iou = calculate_iou(gt_bbox, pred_bbox)
        comp_details['bounding_box_iou'] = bbox_iou
        comp_details['gt_bounding_box'] = gt_bbox
        comp_details['pred_bounding_box'] = pred_bbox

    except Exception as e:
        print(f"Warning: Error calculating bounding box IoU: {e}")
        comp_details['comparison_error'] = f"Error calculating bounding box IoU: {e}"
        bbox_iou = 0.0

    combined_score = (count_score * VERTICES_COUNT_WEIGHT) + (bbox_iou * BOUNDING_BOX_IOU_WEIGHT)
    return combined_score, comp_details


def evaluate_llm_response(llm_response):
    detailed_result = {}
    score = 0.0
    passed = False
    confidence = 100.0
    temp_module_path = None

    if GT_APPROX_VERTICES is None or GT_HULL_VERTICES is None:
         detailed_result['error'] = "Ground truth vertices (GT_APPROX_VERTICES, GT_HULL_VERTICES) are not set in evaluate.py."
         return bool(passed), detailed_result, float(score), confidence
    if not hasattr(llm_response, 'config') or not hasattr(llm_response.config, 'solution_code'):
         detailed_result['error'] = "Input object 'llm_response' lacks 'config.solution_code' attribute."
         return bool(passed), detailed_result, float(score), confidence

    try:
        solution_code_str = llm_response.config.solution_code
        if not isinstance(solution_code_str, str) or not solution_code_str.strip():
            detailed_result['error'] = "Invalid or empty 'solution_code' found in llm_response.config."
            return bool(passed), detailed_result, float(score), confidence
        detailed_result['solution_code_extracted'] = True

        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as temp_f:
            temp_f.write(solution_code_str)
            temp_module_path = temp_f.name
        detailed_result['temp_file_created'] = temp_module_path

        temp_module_name = os.path.splitext(os.path.basename(temp_module_path))[0]
        spec = importlib.util.spec_from_file_location(temp_module_name, temp_module_path)
        if spec is None or spec.loader is None:
             detailed_result['error'] = f"Could not create module spec from temporary file: {temp_module_path}"
             if os.path.exists(temp_module_path): os.remove(temp_module_path)
             return bool(passed), detailed_result, float(score), confidence

        solution_module = importlib.util.module_from_spec(spec)
        temp_dir = os.path.dirname(temp_module_path)
        sys.path.insert(0, temp_dir)
        spec.loader.exec_module(solution_module)
        sys.path.pop(0)

        if not hasattr(solution_module, SOLUTION_FUNCTION_NAME):
            detailed_result['error'] = f"Function '{SOLUTION_FUNCTION_NAME}' not found in executed solution code."
            if os.path.exists(temp_module_path): os.remove(temp_module_path)
            return bool(passed), detailed_result, float(score), confidence

        get_contours_func = getattr(solution_module, SOLUTION_FUNCTION_NAME)
        detailed_result['solution_function_loaded'] = True

        pred_approx_vertices, pred_hull_vertices = get_contours_func()

        if pred_approx_vertices is None or pred_hull_vertices is None:
             detailed_result['execution_error'] = f"Solution function '{SOLUTION_FUNCTION_NAME}' returned None for one or both vertex sets."
             if os.path.exists(temp_module_path): os.remove(temp_module_path)
             return bool(passed), detailed_result, float(score), confidence

        if not isinstance(pred_approx_vertices, np.ndarray) or not isinstance(pred_hull_vertices, np.ndarray):
             detailed_result['type_error'] = f"Solution function did not return NumPy arrays. Approx type: {type(pred_approx_vertices)}, Hull type: {type(pred_hull_vertices)}."
             if os.path.exists(temp_module_path): os.remove(temp_module_path)
             return bool(passed), detailed_result, float(score), confidence

        detailed_result['prediction_vertices_generated'] = True

        approx_score, approx_details_dict = compare_vertices(GT_APPROX_VERTICES, pred_approx_vertices)
        hull_score, hull_details_dict = compare_vertices(GT_HULL_VERTICES, pred_hull_vertices)

        detailed_result['approx_comparison_details'] = approx_details_dict
        detailed_result['hull_comparison_details'] = hull_details_dict
        detailed_result['approx_comparison_score_0_to_1'] = approx_score
        detailed_result['hull_comparison_score_0_to_1'] = hull_score

        final_combined_score = (approx_score + hull_score) / 2.0
        score = final_combined_score * 100.0
        passed = score >= PASS_SCORE_THRESHOLD

        detailed_result['final_combined_score_0_to_1'] = final_combined_score
        detailed_result['final_score_0_to_100'] = score
        detailed_result['pass_threshold_0_to_100'] = PASS_SCORE_THRESHOLD
        detailed_result['passed'] = passed
        
    except Exception as e:
            return False, {"error": str(e)}, None, None
    except ImportError as e:
        detailed_result['error'] = f"Import error during evaluation: {e}. Ensure required libraries (OpenCV, NumPy) are installed in the execution environment."
        detailed_result['error_details'] = str(e)
    except FileNotFoundError as e:
         detailed_result['error'] = f"File not found during solution execution: {e}. Check image path accessibility from where the script is run."
         detailed_result['error_details'] = str(e)
    except Exception as e:
        detailed_result['error'] = f"Unexpected exception during evaluation: {type(e).__name__}"
        detailed_result['error_details'] = str(e)
        detailed_result['traceback'] = traceback.format_exc()

    finally:
        if temp_module_path and os.path.exists(temp_module_path):
            try:
                os.remove(temp_module_path)
                detailed_result['temp_file_cleaned'] = True
            except OSError as e:
                 detailed_result['cleanup_error'] = f"Error removing temp file {temp_module_path}: {e}"
                 print(f"Warning: Failed to remove temporary file {temp_module_path}")

    score = float(score)

    def make_serializable(obj):
        if isinstance(obj, dict):
            return {k: make_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, np.ndarray):
            if obj.shape == (4,) and obj.dtype == np.int32:
                 return tuple(obj.tolist())
            else:
                 return obj.tolist()
        elif isinstance(obj, (np.int_, np.intc, np.intp, np.int8, np.int16, np.int32, np.int64, np.uint8, np.uint16, np.uint32, np.uint64)):
            return int(obj)
        elif isinstance(obj, (np.float16, np.float32, np.float64, np.longdouble)):
            return float(obj)
        elif isinstance(obj, (np.bool_)):
            return bool(obj)
        elif isinstance(obj, (np.void)):
            return None
        elif isinstance(obj, types.SimpleNamespace):
            return make_serializable(vars(obj))
        try:
            json.dumps(obj)
            return obj
        except (TypeError, OverflowError):
            return str(obj)

    serializable_detailed_result = make_serializable(detailed_result)

    return bool(passed), serializable_detailed_result, score, confidence

# if __name__ == "__main__":
#     solution_file = 'solution.txt'

#     print(f"Attempting to evaluate solution from: {solution_file}")

#     try:
#         with open(solution_file, 'r', encoding='utf-8') as f:
#             solution_code = f.read()
#         print("Successfully read solution code.")

#         mock_config = types.SimpleNamespace(solution_code=solution_code)
#         mock_llm_response = types.SimpleNamespace(config=mock_config)

#         passed, details, score, confidence = evaluate_llm_response(mock_llm_response)

#         print("\n--- Evaluation Results ---")
#         print(f"Passed: {passed}")
#         print(f"Score: {score:.2f} / 100.0")

#         print("\n--- Evaluation Details ---")
#         print(json.dumps(details, indent=2))

#     except FileNotFoundError:
#         print(f"Error: Solution file '{solution_file}' not found.")
#         print("Please ensure the file exists in the same directory as evaluate.py or provide the correct path.")
#     except Exception as e:
#         print(f"An unexpected error occurred during the main execution: {type(e).__name__} - {e}")
#         print("Traceback:")
#         print(traceback.format_exc())