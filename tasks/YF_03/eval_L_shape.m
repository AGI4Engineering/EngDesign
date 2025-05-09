function [passed, details, score] = eval_simple_beam(Th)
% Evaluate a cantilever rectangular beam under half‐area uniform load.
% One end fully fixed, free at the other end.
%
% Inputs:
%   Th      – beam thickness in Y (mm)
% Outputs:
%   passed  – true if max vertical deflection <= threshold
%   details – struct with max_displacement_y & threshold
%   score   – 0‒100 based on your rubric

    %% 1) Parameters
    L = 1000;        % span in X (mm)
    W = 40;          % width in Z (mm)
    H = Th;          % height in Y (mm)
    F_each = 1000;   % each point‐load if you wanted points (N) – unused here
    totalLoad = F_each;  % just for magnitude demonstration
    threshold = 2.0; % allowable deflection (mm)

    E  = 210000;     % Young's modulus (MPa)
    nu = 0.3;        % Poisson's ratio

    %% 2) Build 2D cross‐section as two adjacent rectangles
    model2d = createpde();
    R1 = [3 4 0   L/2  L/2   0    0 0 H H]';
    R2 = [3 4 L/2  L    L     L/2  0 0 H H]';
    gdm = [R1 R2];
    ns  = char('R1','R2')';      
    sf  = 'R1+R2';               
    [g, bt] = decsg(gdm, sf, ns);
    geometryFromEdges(model2d, g);

    beam3D = extrude(model2d.Geometry, W);

    %% 3) Create 3D structural model & mesh
    model = createpde('structural','static-solid');
    model.Geometry = beam3D;
    generateMesh(model, 'GeometricOrder','quadratic', 'Hmax', 20);

    % figure; pdegplot(model,'FaceLabels','on','FaceAlpha',0.5);
    % view(30,30); title('Face Labels: 固支面 & 半载荷面');

    %% 4) Material properties
    structuralProperties(model, 'YoungsModulus', E, 'PoissonsRatio', nu);

    %% 5) Boundary conditions

    fixedFace = 5;   %
    structuralBC(model, 'Face', fixedFace, 'Constraint', 'fixed');


    %% 6) Apply half‐area uniform load on top face

    loadedFace = 10;  

    area_half = (L/2) * W;      % mm^2
    p = totalLoad / area_half;  % N/mm^2
    structuralBoundaryLoad(model, 'Face', loadedFace, ...
        'SurfaceTraction', [0, -p, 0]);

    %% 7) Solve
    res = solve(model);

    %% 8) Evaluate max vertical displacement
    uy = res.Displacement.uy;
    max_uy = max(abs(uy));
    passed = max_uy <= threshold;
    details = struct('max_displacement_y', max_uy, 'threshold', threshold);
    figure;
    % pdeplot3D(model, ...
    %     'ColorMapData', uy, ...
    %     'Deformation', res.Displacement, ...
    %     'DeformationScaleFactor', 10);
    % title(sprintf('uy Displacement, Th=%.1f mm → Max uy=%.3f mm', Th, max_uy));
    % xlabel('X'); ylabel('Y'); zlabel('Z');
    % colorbar;

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
end

