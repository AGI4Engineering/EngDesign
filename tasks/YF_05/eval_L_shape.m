function [passed, details, score] = eval_truss_bar(A_target)
% Evaluate a 2D truss, design one member’s area, and visualize the truss & its axial forces.
% Scoring is based on the ratio of the maximum nodal displacement to an allowable threshold.
%
% Inputs:
%   A_target – cross‐sectional area of the target member (element 2) in mm^2
% Outputs:
%   passed   – true if max displacement ≤ threshold
%   details  – struct with:
%                .N            = axial force in target member (N)
%                .sigma        = stress in target member (N/mm^2)
%                .sigma_lim    = allowable stress (N/mm^2)
%                .max_disp     = maximum nodal displacement (mm)
%                .disp_thresh  = allowable displacement threshold (mm)
%   score    – 0–100 based on the displacement‐ratio rubric

    %% 1) Define geometry & topology
    nodes      = [0 0; 1 0; 1 1]*1000;        % (x,y) in mm
    elems      = [1 2; 2 3; 1 3];        % connectivity
    targetElem = 2;                      % element to design
    Nnodes     = size(nodes,1);
    Nelems     = size(elems,1);

    %% 2) Material & area
    E = 210000 * ones(Nelems,1);         % MPa (N/mm^2)
    A = [100; A_target; 100];            % only element 2 varies

    %% 3) Loads & BCs
    F = zeros(2*Nnodes,1);
    F(2*3) = -4000;                      % –1000 N at node 3 (y‐dir)
    bc = [1,1,0; 1,2,0; 2,2,0];          % [node,dir(1=x,2=y),value]

    %% 4) Assemble global stiffness matrix K
    K = zeros(2*Nnodes);
    for e = 1:Nelems
        ni = elems(e,1); nj = elems(e,2);
        xi = nodes(ni,1); yi = nodes(ni,2);
        xj = nodes(nj,1); yj = nodes(nj,2);
        dx = xj-xi; dy = yj-yi; L = hypot(dx,dy);
        c = dx/L; s = dy/L;
        ke = (E(e)*A(e)/L) * ...
             [ c*c,  c*s, -c*c, -c*s;
               c*s,  s*s, -c*s, -s*s;
              -c*c, -c*s,  c*c,  c*s;
              -c*s, -s*s,  c*s,  s*s ];
        dof = [2*ni-1,2*ni,2*nj-1,2*nj];
        K(dof,dof) = K(dof,dof) + ke;
    end

    %% 5) Apply boundary conditions
    fixed = false(2*Nnodes,1);
    U = zeros(2*Nnodes,1);
    for i = 1:size(bc,1)
        idx = 2*bc(i,1) - (2 - bc(i,2));
        fixed(idx) = true;
        U(idx)     = bc(i,3);
    end
    freeDof = find(~fixed);
    Kff = K(freeDof,freeDof);
    Ff  = F(freeDof) - K(freeDof,fixed)*U(fixed);

    %% 6) Solve nodal displacements
    U(freeDof) = Kff \ Ff;
    % convert to mm
    disp_all = sqrt(U(1:2:end).^2 + U(2:2:end).^2);
    max_disp  = max(abs(disp_all));     % max nodal displacement (mm)

    %% 7) Compute axial forces
    N_elem = zeros(Nelems,1);
    for e = 1:Nelems
        ni = elems(e,1); nj = elems(e,2);
        dx = nodes(nj,1)-nodes(ni,1);
        dy = nodes(nj,2)-nodes(ni,2);
        L  = hypot(dx,dy);
        c  = dx/L; s = dy/L;
        ui = U([2*ni-1; 2*ni]);
        uj = U([2*nj-1; 2*nj]);
        N_elem(e) = E(e)*A(e)/L * ([c; s]' * (uj - ui));
    end

    %% 8) Stress check for target element
    N_target  = N_elem(targetElem);
    sigma_lim = 250;                     % N/mm^2
    sigma     = abs(N_target) / A_target;
    passed    = (max_disp <= 0.5);      % threshold = 2 mm

    details = struct( ...
      'N',           N_target, ...
      'sigma',       sigma, ...
      'sigma_lim',   sigma_lim, ...
      'max_disp',    max_disp, ...
      'disp_thresh', 0.5 ...
    );

    %% 9) Scoring based on displacement ratio r = max_disp/threshold
    r = max_disp / details.disp_thresh;
    if     r >= 0.70 && r <= 0.90
        score = 100;
    elseif r >= 0    && r <  0.70
        score = (r / 0.70) * 100;
    elseif r >  0.90 && r <= 1.00
        score = (1 - (r - 0.90)/0.10) * 100;
    else
        score = 0;
    end
    score = max(0, min(100, score));

    % %% 10) Visualization: truss & axial forces + max displacement
    % figure('Name','2D Truss & Axial Forces'); hold on;
    % Nmax = max(abs(N_elem));
    % for e = 1:Nelems
    %     ni = elems(e,1); nj = elems(e,2);
    %     x = [nodes(ni,1), nodes(nj,1)];
    %     y = [nodes(ni,2), nodes(nj,2)];
    %     if N_elem(e) >= 0
    %         col = [0,0,1];   % tension: blue
    %     else
    %         col = [1,0,0];   % compression: red
    %     end
    %     lw = 1 + 4*abs(N_elem(e))/Nmax;
    %     plot(x, y, '-', 'Color', col, 'LineWidth', lw);
    % end
    % % Plot displaced shape scaled
    % scale = 100; % exaggeration factor
    % dispX = nodes(:,1) + scale*U(1:2:end);
    % dispY = nodes(:,2) + scale*U(2:2:end);
    % for i = 1:Nelems
    %     ni = elems(i,1); nj = elems(i,2);
    %     plot(dispX([ni,nj]), dispY([ni,nj]), 'k--');
    % end
    % scatter(nodes(:,1), nodes(:,2), 50, 'k', 'filled');
    % scatter(dispX, dispY, 50, 'g', 'filled');
    % axis equal; grid on;
    % xlabel('X (mm)'); ylabel('Y (mm)');
    % title(sprintf('Max disp = %.3f mm (thr = %.1f mm), score = %.1f', ...
    %       max_disp, details.disp_thresh, score));
    % hold off;
end

% Example call:
% A_test = 80;
% [ok, det, sc] = eval_truss_bar(A_test);
% fprintf('Max disp = %.3f mm, passed = %d, score = %.1f\n', ...
%         det.max_disp, ok, sc);
