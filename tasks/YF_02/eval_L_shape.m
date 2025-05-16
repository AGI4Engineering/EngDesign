function [passed, details, score] = eval_simple_beam(Th)
% Evaluate a simply supported rectangular beam under dual point loads.
% Uses one face fully fixed (pin) and the other face “roller” (Y only).
%
% Inputs:
%   Th        - Thickness of the beam (mm) [height in Y]
% Outputs:
%   passed    - true if max vertical displacement <= 2 mm
%   details   - struct with max_displacement_y & threshold
%   score     - 100 if passed, else 0

    %% 1) Parameters
    L = 1000;           % span length in X (mm)
    W = 40;             % beam width in Z (mm)
    H = Th;             % beam height in Y (mm)
    F_each = 1000;       % each point load (N)
    totalLoad = 2*F_each;  % total vertical load (N)
    threshold = 1.0;    % allowable max displacement (mm)

    E  = 210000;          % Young's modulus (MPa)
    nu = 0.3;           % Poisson's ratio

    %% 2) Build 2D cross-section and extrude to 3D
    model2d = createpde();
    R1 = [3 4 0 L L 0 0 0 H H]';
    ns = char('R1'); ns = ns';
    g  = decsg(R1, 'R1', ns);
    geometryFromEdges(model2d, g);
    beam3D = extrude(model2d.Geometry, W);

    %% 3) Create 3D structural model
    model = createpde('structural','static-solid');
    model.Geometry = beam3D;
    generateMesh(model, 'GeometricOrder','quadratic', 'Hmax', 20);
    
    % figure;
    % pdegplot(model, 'FaceLabels', 'on', 'FaceAlpha', 0.5);
    % view(30,30);


    %% 4) Material properties
    structuralProperties(model, ...
        'YoungsModulus', E, ...
        'PoissonsRatio', nu);

    %% 5) Boundary conditions
    % Face IDs for extruded rectangle:
    %   Face 5: X = 0 (left end)
    %   Face 3: X = L (right end)
    % Pin at left: fix all DOF
    structuralBC(model, 'Face', 4, 'Constraint', 'fixed');
    % Roller at right: Y = 0 only
    structuralBC(model, 'Face', 6, 'YDisplacement', 0);

    %% 6) Apply equivalent uniform pressure on top face (face 4)
    % totalLoad N over area L*W mm^2
    p = totalLoad / (L * W);  % N/mm^2 downward
    structuralBoundaryLoad(model, 'Face', 2, ...
        'SurfaceTraction', [0, -p, 0]);

    %% 7) Solve
    res = solve(model);

    %% 8) Evaluate max vertical displacement
    uy = res.Displacement.uy;
    max_uy = max(abs(uy));
    passed = max_uy <= threshold;
    details = struct('max_displacement_y', max_uy, 'threshold', threshold);
    r = max_uy / threshold;  

    if r >= 0.7 && r <= 0.9
        score = 100;
    elseif r < 0.7 && r >= 0
        score = (r / 0.7) * 100;
    elseif r > 0.9 && r <= 1
        score = ((1 - r) / 0.1) * 100;
    else
        score = 0;
    end

    %% 9) Visualize
    % figure;
    % pdeplot3D(model, ...
    %     'ColorMapData', uy, ...
    %     'Deformation', res.Displacement, ...
    %     'DeformationScaleFactor', 10);
    % title(sprintf('uy Displacement, Th=%.1f mm → Max uy=%.3f mm', Th, max_uy));
    % xlabel('X'); ylabel('Y'); zlabel('Z');
    % colorbar;
    
end







