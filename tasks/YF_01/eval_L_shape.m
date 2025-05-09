function [passed, details, score] = eval_L_shape(Th)
% One-file evaluation of an L-shaped steel beam under load
% Inputs:
%   Lh, Lv, Th, Rf, Height     - Geometry parameters (in mm)
%   FixFaceID, LoadFaceID     - Boundary condition face IDs
%   traction                  - Applied surface traction [tx, ty, tz]
%   E, nu                     - Material properties
% Outputs:
%   passed  - Whether max displacement <= threshold
%   details - Struct with max displacement and threshold
%   score   - 100 if passed, 0 if not
    %% Parameters
    threshold = 0.1;  % mm displacement limit
    [Lh, Lv, Rf, Height] = deal(50, 80, 20, 50);
    FixFaceID = 4;
    LoadFaceID = 5;
    traction = [10, -20, 0];  % N/mm²
    E = 21000;               % MPa
    nu = 0.3;

    %% --- Build Geometry ---
    model2d = createpde;
    R1 = [3 4 0 Lh Lh 0 0 0 Lv Lv]';
    R2 = [3 4 Th+Rf Lh Lh Th+Rf Th Th Lv Lv]';
    R3 = [3 4 Th Th+Rf Th+Rf Th Th+Rf Th+Rf Lv Lv]';
    xC = Th + Rf;
    yC = Th + Rf;
    radius = Rf;
    C1 = [1, xC, yC, radius, zeros(1,6)]';

    gdm = [R1 R2 R3 C1];
    ns  = char('R1','R2','R3','C1');
    ns  = ns';
    sf = 'R1 - R2 - R3 - C1';
    g = decsg(gdm, sf, ns);

    geometryFromEdges(model2d, g);
    shape3D = extrude(model2d.Geometry, Height);

    %% --- Create Model & Mesh ---
    model3d = createpde("structural", "static-solid");
    model3d.Geometry = shape3D;
    generateMesh(model3d, "GeometricOrder", "quadratic", "Hmax", 2);

    %% --- Material Properties ---
    structuralProperties(model3d, "YoungsModulus", E, "PoissonsRatio", nu);

    %% --- Boundary Conditions & Loads ---
    structuralBC(model3d, "Face", FixFaceID, "Constraint", "fixed");
    structuralBoundaryLoad(model3d, "Face", LoadFaceID, "SurfaceTraction", traction);

    %% --- Solve ---
    R = solve(model3d);

    %% --- Evaluate Maximum uz Displacement ---
    uz = R.Displacement.z;
    max_uz = max(abs(uz));
    passed = max_uz <= threshold;

    %% --- Output Struct ---
    details = struct();
    details.max_displacement_z = max_uz;
    details.threshold = threshold;
    r = max_uz / threshold;  

    if r >= 0.7 && r <= 0.9
        score = 100;
    elseif r < 0.7 && r >= 0
        score = (r / 0.7) * 100;
    elseif r > 0.9 && r <= 1
        score = ((1 - r) / 0.1) * 100;
    else
        score = 0;
    end
end
