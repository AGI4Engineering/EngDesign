function [passed, details, score] = edge_detection(sx, sy, wa, wb, wc, ba, bb, bc)
    % Evaluate controller performance for nanopositioning stage
    % Inputs:
    %   sx: parameter for the membership function Ix
    %   sy: parameter for the membership function Iy
    %   wa: parameter for the membership function Iout
    %   wb: parameter for the membership function Iout
    %   wc: parameter for the membership function Iout
    %   ba: parameter for the membership function Iout
    %   bb: parameter for the membership function Iout
    %   bc: parameter for the membership function Iout
    % Outputs:
    %   passed: boolean indicating if all requirements are met
    %   details: struct with detailed evaluation results
    %   score: score for the controller
    
    % Import the image.
    Irgb = imread('tasks/XG_09/image.jpg');
    % Convert to 2-D array
    Igray = rgb2gray(Irgb);
    Igray = imresize(Igray, [64 64]);  % Resize to 64x64
    % Convert image to double-precision data
    I = im2double(Igray);
    % Obtain Image gradient
    Gx = [-1 1];
    Gy = Gx';
    Ix = conv2(I,Gx,'same');
    Iy = conv2(I,Gy,'same');
    % Define Fuzzy Inference System (FIS) for Edge Detection
    edgeFIS = mamfis('Name','edgeDetection');
    edgeFIS = addInput(edgeFIS,[-1 1],'Name','Ix');
    edgeFIS = addInput(edgeFIS,[-1 1],'Name','Iy');
    edgeFIS = addMF(edgeFIS,'Ix','gaussmf',[sx 0],'Name','zero');
    edgeFIS = addMF(edgeFIS,'Iy','gaussmf',[sy 0],'Name','zero');
    % Specify the intensity of the edge-detected image as an output of edgeFIS
    edgeFIS = addOutput(edgeFIS,[0 1],'Name','Iout');
    edgeFIS = addMF(edgeFIS,'Iout','trimf',[wa wb wc],'Name','white');
    edgeFIS = addMF(edgeFIS,'Iout','trimf',[ba bb bc],'Name','black');
    % Specify FIS Rules
    r1 = "If Ix is zero and Iy is zero then Iout is white";
    r2 = "If Ix is not zero or Iy is not zero then Iout is black";
    edgeFIS = addRule(edgeFIS,[r1 r2]);
    edgeFIS.Rules;
    % Evaluate FIS 
    Ieval = zeros(size(I));
    for ii = 1:size(I,1)
        Ieval(ii,:) = evalfis(edgeFIS,[(Ix(ii,:));(Iy(ii,:))]');
    end
    Ieval_inv = 1 - mat2gray(Ieval);  % Invert: edge = high value
    % 3. Evaluation Metrics
    ref = edge(I, 'canny');  % Canny edge detector as pseudo-ground-truth
    mse_val = immse(mat2gray(Ieval_inv), double(ref));
    psnr_val = psnr(mat2gray(Ieval_inv), double(ref));
    ssim_val = ssim(mat2gray(Ieval_inv), double(ref));
    score = 0;
    passed = false;
    mse_pass = false;
    psnr_pass = false;
    ssim_pass = false;
    if mse_val < 0.5
        mse_pass = true;
        score = score + 30;
    elseif psnr_val > 3
        psnr_pass = true;
        score = score + 30;
    elseif ssim_val > 0.05
        ssim_pass = true;
        score = score + 40;
    end

    if mse_pass && psnr_pass && ssim_pass
        passed = true;
    else
        passed = false;
    end
    details = struct();
    details.mse = mse_val;
    details.psnr = psnr_val;
    details.ssim = ssim_val;
    details.mse_pass = mse_pass;
    details.psnr_pass = psnr_pass;
    details.ssim_pass = ssim_pass;
    details.score = score;
    details.passed = passed;
end