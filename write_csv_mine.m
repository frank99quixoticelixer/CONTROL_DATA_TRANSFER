%% Export Simulink outputs to CSV
% Handles data shaped as 3 x 1 x N

% -----------------------------
% Time
% -----------------------------
t = out.timee(:);   % 1001 x 1

% -----------------------------
% Position & angles
% -----------------------------
pos = squeeze(out.position);   % 3 x N
ang = squeeze(out.angles);     % 3 x N

% Transpose to N x 3
pos = pos.';
ang = ang.';

% -----------------------------
% Sanity checks
% -----------------------------
assert(size(pos,2) == 3, 'Position must be Nx3');
assert(size(ang,2) == 3, 'Angles must be Nx3');
assert(size(pos,1) == length(t), 'Time/position mismatch');

% -----------------------------
% Split
% -----------------------------
x = pos(:,1);
y = pos(:,2);
z = pos(:,3);

phi   = ang(:,1);
theta = ang(:,2);
psi   = ang(:,3);

% -----------------------------
% Create table
% -----------------------------
T = table( ...
    t, x, y, z, phi, theta, psi, ...
    'VariableNames', ...
    {'time','x','y','z','phi','theta','psi'} ...
);

% -----------------------------
% Write CSV
% -----------------------------
filename = 'quadcopter_sim_log.csv';
writetable(T, filename);

fprintf('Exported %d samples to %s\n', length(t), filename);
