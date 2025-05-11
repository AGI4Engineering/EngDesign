import numpy as np 
import os 
import sys 
import math
from skimage.metrics import structural_similarity as ssim
from skimage.metrics import peak_signal_noise_ratio as psnr
from scipy.signal import convolve2d
import cv2
from scipy.ndimage import label
from skimage.measure import shannon_entropy

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))) 

def unsupervised_edge_loss_numpy(edge_map, alpha=0.1,
                                  lambda_tv=0.1, lambda_entropy=0.01, lambda_density=0.05):
    eps = 1e-8
    edge_map = np.clip(edge_map, eps, 1 - eps)
    tv_h = np.abs(edge_map[:, :-1] - edge_map[:, 1:])
    tv_v = np.abs(edge_map[:-1, :] - edge_map[1:, :])
    tv_loss = np.sum(tv_h) + np.sum(tv_v)
    entropy_loss = -np.mean(edge_map * np.log(edge_map) + (1-edge_map) * np.log(1 - edge_map))
    edge_density = np.mean(edge_map)
    density_loss = np.abs(edge_density - alpha)
    total_loss = (lambda_tv * tv_loss + lambda_entropy * entropy_loss + lambda_density * density_loss)
    return total_loss

def evaluate_image_quality(ssim_value, ssim_thresh=0.7):
    passed = ssim_value >= ssim_thresh 
    details = {
        "SSIM": ssim_value,
        "SSIM_Passed": ssim_value >= ssim_thresh,
    }
    score = ssim_value*100

    return passed, details, score
def sobel_blur(img, ksize, x_kerenel=None, y_kerenel=None):
    blurred = cv2.GaussianBlur(img, (ksize, ksize), 0)
    return sobel_basic(blurred, x_kerenel, y_kerenel)
def sobel_basic(img ,x_kerenel,y_kerenel):
    sobel_x = np.array(x_kerenel, dtype=np.float64)
    sobel_y = np.array(y_kerenel, dtype=np.float64)
    grad_x = cv2.filter2D(img, cv2.CV_64F, sobel_x)
    grad_y = cv2.filter2D(img, cv2.CV_64F, sobel_y)
    return np.hypot(grad_x, grad_y)
def apply_edge_detection(image, guassian,edge_x,edge_y, maximum, minimum):    
    edge = sobel_blur(image, guassian,edge_x,edge_y)
    norm = cv2.normalize(edge, None, 0, 1.0, cv2.NORM_MINMAX)
    binary = ((norm >= minimum) & (norm <= maximum)).astype(np.uint8) 
    edge_density = np.sum(binary > 0) / binary.size
    labeled_array, num_features = label(binary > 0)
    entropy = shannon_entropy(binary)
    return edge, (edge_density, num_features, entropy), binary

    
def evaluate_llm_response(llm_response): 
   try: 
       confidence = 100 
       gaussian = int(llm_response.config.gaussian)
       edge_x = llm_response.config.edge_x
       edge_y = llm_response.config.edge_y
       maximum = llm_response.config.maximum
       minimum = llm_response.config.minimum
       # Get absolute path to input.npy relative to this evaluate.py file
       current_dir = os.path.dirname(os.path.abspath(__file__))
       input_path = os.path.join(current_dir, "input.npy")
       input_image= np.load(input_path)
       sobel3, sobel3_metrics, sobel3_binary= apply_edge_detection(input_image , gaussian, edge_x, edge_y, maximum, minimum)
       sobel3_uint8 = cv2.convertScaleAbs(sobel3)
       cv2.imwrite("sobel3.png", sobel3_uint8)
       total_loss= unsupervised_edge_loss_numpy(sobel3/ 255.0)
       if( total_loss<70):
           passed=True
       else:
           passed=False
       details = {
            "edge_density": sobel3_metrics[0],
            "num_features": sobel3_metrics[1],
            "entropy": sobel3_metrics[2],
            "total_loss": total_loss
        }
       score = 125-total_loss 
       return passed, details, score, confidence 
       
   except Exception as e: 
       return False, {"error": str(e)}, None, None