function [passed, details, score] = eval_plate_deflection(thickness)
% Evaluate a 3D rectangular plate (1000×500×thickness mm) under transverse pressure
% with all four side faces fixed.
% Inputs:
%   thickness – plate thickness (mm)
% Outputs:
%   passed  – true if max deflection ≤ threshold
%   details – struct with fields:
%               .max_disp   (mm), .disp_thresh (mm), .max_stress (N/mm^2)
%   score   – 0–100 based on deflection ratio

    %% 1) Geometry & material parameters
    L = 1000;             % length in X (mm)
    W =  500;             % width  in Y (mm)
    E = 210000;           % Young's modulus (N/mm^2)
    nu = 0.3;             % Poisson's ratio
    rho = 7850;           % density (kg/m^3)
    pressure = 2;         % transverse pressure (N/mm^2)
    disp_thresh = 0.5;    % allowable deflection (mm)

    %% 2) Create 3D structural model
    model = createpde('structural','static-solid');
    
    
    %% 3) Define plate geometry as a block
    gm = multicuboid(L, W, thickness);
    model.Geometry = gm;
    % figure
    % pdegplot(model,'FaceLabels','on')
    % axis equal
    %% 4) Assign material properties
    structuralProperties(model, ...
        'YoungsModulus', E, ...
        'PoissonsRatio', nu, ...
        'MassDensity', rho);

    %% 5) Fix all four side faces (Face IDs 1-4)
    structuralBC(model,'Face',3:6,'Constraint','fixed');

    %% 6) Apply uniform pressure on top face (Face ID 6)
    structuralBoundaryLoad(model,'Face',2,'Pressure',pressure);

    %% 7) Mesh and solve
    % Use a mesh size proportional to thickness
    hmax = min([L, W]) / 10;
    generateMesh(model,'GeometricOrder','linear','Hmax',hmax);
    result = solve(model);

    %% 8) Post-process: displacement and stress
    u = result.Displacement;
    ux = u.ux;    
    uy = u.uy;    
    uz = u.uz;    
    Umag = sqrt(ux.^2 + uy.^2 + uz.^2);
    max_disp = max(Umag);  % mm

    stress = result.VonMisesStress;
    max_stress = max(stress);

    passed = (max_disp <= disp_thresh);
    details = struct('max_disp',max_disp, 'disp_thresh',disp_thresh, 'max_stress',max_stress);

    %% 9) Scoring (deflection ratio r)
    r = max_disp / disp_thresh;
    if r >= 0.70 && r <= 0.90
        score = 100;
    elseif r >= 0 && r < 0.70
        score = (r / 0.70) * 100;
    elseif r > 0.90 && r <= 1.00
        score = (1 - (r - 0.90) / 0.10) * 100;
    else
        score = 0;
    end
    score = max(0, min(100, score));

    % 10) Visualization: 3D deformation and stress
    % figure('Name','3D Plate Deformation','NumberTitle','off');
    % pdeplot3D(model, ...
    %     'ColorMapData',Umag, ...
    %     'Deformation',[ux, uy, uz], ...
    %     'DeformationScaleFactor',1);
    % title(sprintf('Max Deflection = %.3f mm', max_disp));
    % xlabel('X (mm)'); ylabel('Y (mm)'); zlabel('Z (mm)');
    % 
    % figure('Name','3D Plate Stress','NumberTitle','off');
    % pdeplot3D(model,'ColorMapData',stress);
    % title(sprintf('Max von Mises Stress = %.1f N/mm^2', max_stress));
    % xlabel('X (mm)'); ylabel('Y (mm)'); zlabel('Z (mm)');
end

% % Example call:
% thickness_test = 10; % mm
% [ok, det, sc] = eval_plate_deflection(thickness_test);
% fprintf('Thickness=%.1f mm → Max disp=%.3f mm, Passed=%d, Score=%.1f\n', ...
%        thickness_test, det.max_disp, ok, sc);
