function w = cylinder2strip(r)
%CYLINDER2STRIP   Equivalent strip width for a cylindrical wire
%   w = cylinder2strip(r) returns a flat‐wire width w (m) that
%   approximates a round wire of radius r (m). Here we take
%   w = 2*r (i.e. strip width = wire diameter).
%
%   You can adjust this to another equivalence (e.g. equal
%   cross‐sectional area) if you know the strip thickness.

    w = 2*r;
end
