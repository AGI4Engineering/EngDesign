function s = helixpitch2spacing(pitch)
%HELIXPITCH2SPACING  Axial spacing between helix turns
%   s = helixpitch2spacing(pitch) returns the distance (m) between
%   successive turns of a helical wire given its pitch (m).
%
%   By default we take the spacing = pitch.  If you need a more
%   sophisticated relationship (e.g. based on geometric center-to-center
%   distance), replace this formula accordingly.

    s = pitch;
end
