function [passed, details, score] = evaluate_robot(theta)
%% Define the functions to calculate forward kinematics    
    function R = MatrixExp3(so3mat)
    % MatrixExp3   Matrix exponential of a 3×3 so(3) matrix
    %
    %   R = MatrixExp3(so3mat) computes expm(so3mat) for a skew-symmetric
    %   matrix so3mat using the Rodrigues formula.
    %
    %   Input:
    %     so3mat - 3×3 skew-symmetric matrix
    %   Output:
    %     R      - 3×3 rotation matrix in SO(3)
    
        % Extract the rotation vector ωθ from the skew matrix
        omegaTheta = so3ToVec(so3mat);
        
        % If the magnitude is near zero, return the identity
        if NearZero(norm(omegaTheta))
            R = eye(3);
        else
            % Compute the rotation angle θ
            [~, theta] = AxisAng3(omegaTheta);
            
            % Normalize the skew matrix
            omgmat = so3mat / theta;
            
            % Rodrigues formula
            R = eye(3) ...
                + sin(theta) * omgmat ...
                + (1 - cos(theta)) * (omgmat * omgmat);
        end
    end
    function [omghat, theta] = AxisAng3(expc3)
    % AxisAng3   Convert a 3-vector of exponential coordinates to axis-angle
    %
    %   [omghat, theta] = AxisAng3(expc3) returns the unit rotation axis omghat
    %   and rotation angle theta corresponding to the exponential coordinates
    %   expc3 = omghat * theta.
    %
    %   Input:
    %     expc3 - 3×1 vector of exponential coordinates for rotation
    %   Outputs:
    %     omghat - 3×1 unit rotation axis (undefined if theta is zero)
    %     theta  - Scalar rotation angle (norm of expc3)
    %
    %   Example:
    %     expc3 = [1; 2; 3];
    %     [omghat, theta] = AxisAng3(expc3);
    %     % omghat ≈ [0.2673; 0.5345; 0.8018], theta ≈ 3.7417
    
        theta = norm(expc3);
        if NearZero(theta)
            % If angle is near zero, axis is arbitrary; return zero vector
            omghat = [0; 0; 0];
        else
            omghat = expc3 / theta;
        end
    end
    function flag = NearZero(z)
    % NearZero  Check if a scalar is close enough to zero
    %
    %   flag = NearZero(z) returns true if |z| < 1e-6, false otherwise.
    %
    %   Input:
    %     z    - Scalar to test
    %   Output:
    %     flag - Boolean, true if abs(z) < 1e-6
    
        flag = abs(z) < 1e-6;
    end
    function v = so3ToVec(so3mat)
    % so3ToVec   Converts a 3×3 skew-symmetric matrix to a 3×1 vector
    %
    %   v = so3ToVec(so3mat) returns the vector [ω1; ω2; ω3] corresponding to
    %   the skew-symmetric matrix
    %       [  0   -ω3   ω2
    %         ω3     0  -ω1
    %        -ω2   ω1     0 ]
    %
    %   Input:
    %     so3mat - 3×3 skew-symmetric matrix
    %   Output:
    %     v      - 3×1 vector [ω1; ω2; ω3]
    
        v = [ so3mat(3,2);
              so3mat(1,3);
              so3mat(2,1) ];
    end
    function T = MatrixExp6(se3mat)
    % MatrixExp6   Matrix exponential of an se(3) matrix
    %
    %   T = MatrixExp6(se3mat) computes expm(se3mat) for a 4×4 se(3) matrix.
    %
    %   Input:
    %     se3mat - 4×4 matrix in se(3) form
    %   Output:
    %     T      - 4×4 homogeneous transformation matrix exp(se3mat)
    %
    %   This implementation uses the Rodrigues formula for SO(3) and handles
    %   the zero‐angular‐velocity case separately.
    
        % Extract the angular part ωθ from the upper‐left 3×3 block
        omgtheta = so3ToVec(se3mat(1:3,1:3));
        
        % If ‖ωθ‖ is near zero, pure translation
        if NearZero(norm(omgtheta))
            R = eye(3);
            p = se3mat(1:3,4);
            T = [R, p; 0 0 0 1];
            return
        end
        
        % Otherwise, compute axis‐angle from ωθ
        [omega, theta] = AxisAng3(omgtheta);
        
        % Normalize the skew‐matrix of ω
        omgmat = se3mat(1:3,1:3) / theta;
        
        % Compute the SO(3) part
        R = MatrixExp3(se3mat(1:3,1:3));
        
        % Compute the translation part using the V matrix
        V = eye(3)*theta ...
            + (1 - cos(theta))*omgmat ...
            + (theta - sin(theta))*(omgmat*omgmat);
        p = (V * se3mat(1:3,4)) / theta;
        
        % Assemble the homogeneous transform
        T = [R, p; 0 0 0 1];
    end
    function so3mat = VecToso3(omg)
    % VecToso3  Converts a 3×1 vector into a 3×3 skew-symmetric matrix (so(3))
    %
    %   so3mat = VecToso3(omg) returns the matrix form of the cross-product
    %   operator for the vector omg = [ω1; ω2; ω3].
    %
    %   Input:
    %     omg   - 3×1 vector [ω1; ω2; ω3]
    %   Output:
    %     so3mat - 3×3 skew-symmetric matrix
    %
    %   Example:
    %     omg = [1; 2; 3];
    %     so3 = VecToso3(omg);
    %     % so3 =
    %     %     0   -3    2
    %     %     3    0   -1
    %     %    -2    1    0
    
        so3mat = [  0      -omg(3)   omg(2);
                  omg(3)       0    -omg(1);
                 -omg(2)    omg(1)       0 ];
    end
    function se3mat = VecTose3(V)
    % VecTose3  Converts a 6-vector into a 4×4 se(3) matrix
    %   se3mat = VecTose3(V) returns the se(3) representation of the spatial
    %   velocity vector V = [omega; v], where omega is the angular part and
    %   v is the linear part.
    %
    %   Input:
    %     V      - 6×1 vector [ω1; ω2; ω3; v1; v2; v3]
    %   Output:
    %     se3mat - 4×4 matrix in se(3)
    
        omega = V(1:3);
        v     = V(4:6);
    
        % VecToso3 converts a 3-vector into a 3×3 skew-symmetric matrix
        se3mat = [ VecToso3(omega),  v;
                   0, 0, 0, 0 ];
    end
    function T = FKinSpace(M, Slist, thetalist)
    % FKinSpace Computes forward kinematics in the space frame for an open-chain robot
    %   T = FKinSpace(M, Slist, thetalist) returns the homogeneous transformation
    %   matrix of the end-effector when the joints are at the angles in thetalist.
    %
    %   Inputs:
    %     M         - 4×4 home configuration of the end-effector
    %     Slist     - 6×n matrix of joint screw axes (columns) in the space frame
    %     thetalist - n×1 vector of joint coordinates
    %
    %   Output:
    %     T         - 4×4 transformation matrix of the end-effector
    
        T = M;
        for i = numel(thetalist):-1:1
            se3mat = VecTose3( Slist(:,i) * thetalist(i) );
            T = MatrixExp6(se3mat) * T;
        end
    end
    
    %% Scoring ************************************************************
    T_1in0 = [-0.54285628 0.59396029 0.59373246 -9.39188580; 0.64992009 -0.15063728 0.74492435 -1.86561101; 0.53189373 0.79026551 -0.30425233 0.67392911; -0.00000000 0.00000000 0.00000000 1.00000000];
    M = [0.00000000 0.00000000 1.00000000 -8.00000000; 1.00000000 0.00000000 0.00000000 2.00000000; 0.00000000 1.00000000 0.00000000 0.00000000; 0.00000000 0.00000000 0.00000000 1.00000000];
    S = [0.00000000 1.00000000 0.00000000 0.00000000 -1.00000000 0.00000000; 0.00000000 0.00000000 0.00000000 1.00000000 0.00000000 1.00000000; 0.00000000 0.00000000 -1.00000000 0.00000000 0.00000000 0.00000000; 0.00000000 0.00000000 2.00000000 0.00000000 0.00000000 0.00000000; 1.00000000 0.00000000 -4.00000000 0.00000000 0.00000000 0.00000000; 0.00000000 0.00000000 0.00000000 -6.00000000 0.00000000 -8.00000000];
    T_1in0_llm = FKinSpace(M,S,theta);
    %   T_true – 4×4 target homogeneous transform
    %   T_llm  – 4×4 transform from LLM’s forward kinematics
    unit_in_mm = 1000;
    
    % 1) Position error in millimeters
    p_1in0  = T_1in0(1:3,4);
    p_1in0_llm   = T_1in0_llm(1:3,4);
    pos_err = norm(p_1in0_llm - p_1in0) * unit_in_mm;
    
    % 2) Orientation error (equivalent arc‐length in mm)
    R_err    = T_1in0(1:3,1:3)' * T_1in0_llm(1:3,1:3);
    logR     = real(logm(R_err));
    omega_th = [logR(3,2); logR(1,3); logR(2,1)];
    rot_err  = norm(omega_th) * unit_in_mm;
    
    % 3) Scoring: position 50 pts if <1 mm, orientation 50 pts if <1 mm
    if pos_err < 1
        pos_score = 50;
    else
        pos_score = 0;
    end
    
    if rot_err < 1
        rot_score = 50;
    else
        rot_score = 0;
    end
    
    % 4) Total score
    score = pos_score + rot_score;
    
    passed = (score == 100);
    %% Details output
    details = struct();
    details.score = score;
    details.T_1in0 = T_1in0_llm;
end
