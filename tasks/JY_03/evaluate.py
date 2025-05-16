import numpy as np 
import os 
import sys 
import math
from skimage.metrics import structural_similarity as ssim
from skimage.metrics import peak_signal_noise_ratio as psnr
from scipy.signal import convolve2d
import cv2
from scipy.ndimage import label
import numpy as np
import scipy.ndimage
from scipy.ndimage import convolve

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))) 

def compute_dolp_aolp(I0, I45, I90, I135, eps=1e-8):
    
    I0, I45, I90, I135 = map(np.float32, [I0, I45, I90, I135])
    S0 = I0 + I90
    S1 = I0 - I90
    S2 = I45 - I135
    DoLP = np.sqrt(S1**2 + S2**2) / (S0 + eps)
    AoLP = 0.5 * np.arctan2(S2, S1)

    return DoLP, AoLP
def evaluate(output, gt , names):
    
    score = [] 
    detail= { }
    for i ,( output, gt) in enumerate(zip(output, gt)): 
        psnr_val = psnr(gt, output, data_range=255)
        ssim_val = ssim(gt, output, data_range=255)
        score.append( psnr_val/40*50+ ssim_val*50 )
        detail[f"{names[i]}"] = {
                "PSNR": psnr_val,
                "SSIM": ssim_val,
                "Score": score
            }
    total_score = 0 
    passed= True 
    for subscore in score: 
        if subscore < 50: 
            passed = False 
        else:
            total_score+= min(subscore, 100)

    
    return passed, detail, total_score/3  , 100
def fill_zeros_with_kernel(image, kernel):
    
   
    convolved = scipy.ndimage.convolve(image, kernel, mode='reflect')
    filled_image = np.copy(image)
    filled_image[image == 0] = convolved[image == 0]
    return filled_image

def evaluate_llm_response(llm_response): 
   try: 
       confidence = 100 
       Kernel= np.array(llm_response.config.Kernel)
       current_dir = os.path.dirname(os.path.abspath(__file__))
       gt_0_path = os.path.join(current_dir, "0.npy")
       gt_45_path = os.path.join(current_dir, "45.npy")
       gt_90_path = os.path.join(current_dir, "90.npy")
       gt_135_path = os.path.join(current_dir, "135.npy")
       input_image_path = os.path.join(current_dir, "checkerboard.npy")
       gt_0= np.load(gt_0_path)
       gt_45= np.load(gt_45_path)
       gt_90= np.load(gt_90_path)
       gt_135= np.load(gt_135_path)
       gt_0=cv2.normalize(gt_0, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
       gt_45=cv2.normalize(gt_45, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
       gt_90=cv2.normalize(gt_90, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
       gt_135=cv2.normalize(gt_135, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
       input_image = np.load(input_image_path)   
       conv_result = convolve(input_image.astype(np.float32), Kernel, mode='mirror')
       conv_result= cv2.normalize(conv_result, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
       DoLP, AoLP=compute_dolp_aolp(conv_result, gt_45, gt_90, gt_135)
       DoLP_gt, AoLP_gt = compute_dolp_aolp(gt_0, gt_45, gt_90, gt_135)
       passed, details, score, confidence = evaluate(output = [conv_result, DoLP, AoLP],  gt= [gt_0, DoLP_gt, AoLP_gt ]  , names= ["degree_0", "DoLP", "AoLP"])
       return passed, details, score, confidence
       
   except Exception as e: 
       return False, {"error": str(e)}, None, None
   