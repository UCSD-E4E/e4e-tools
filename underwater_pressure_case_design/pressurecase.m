function [ ]= pressurecase(mat_index,len,wall,rad)
%
% Function for computing the pressure at which buckling occurs in a 
% thin-walled pressure vessel. Computes buckling for both cylindrical and
% spherical pressure vessel designs.
%
% Author: Antonella Wilby
% Last Updated: 8/20/2014
%
% PARAMETERS: 
%   mat_index: material index:
%       1 =  borosilicate glass
%       2 = 6061-T6 aluminum
%       3 = 7075-T6 aluminum
%       4 = 316 stainless steel
%       5 = delrin D100
%       6 = UHMW (Ultra-High Molecular Weight) polyethylene
%       7 = Ertalyte
%       8 = PVC (Polyvinyl chloride)
%       9 = Acrylic
%       10 = Lexan
%   len: length of pressure case cylinder in inches
%   wall: wall thickness in inches
%   rad: radius of pressure case cylinder in inches
%
% MATERIAL PROPERTIES:
%   1: young's modulus (elastic tensile modulus) in MPa
%   2: ultimate tensile strength in MPa
%   3: yield strength in MPa
%   4: Poisson's ratio
%   5: thermal conductivity in W/m K
%   6: density: density in gm/cc
%
% RETURNS:
%   Pflow: pressure for plastic flow in psi 
%   Pinf: instabilities of infinite length scale in psi 
%   Pstab: finite length instabilities in psi
%   beam: min. thickness for beam-supported flat end-cap (thousandths of an inch)
%   simple: min. thickness for simple-supported flat end-cap (thousandths of an inch)
%   hemi: min. thickness for semi-hemispherical end-cap (thousandths of an inch)
%   


% Load materials data
load 'material_properties.mat'

% Check if thin-walled assumption holds
%if( rad/wall  > 10)
    
%disp('Thin-walled assumption holds.');


% Material Properties
E = materials(1, mat_index);        % Young's modulus
yield = materials(3, mat_index);    % Yield Strength
nu = materials(4, mat_index);       % Poisson's ratio
n = 2;                              % # of circumferential lobes


% CALCULATIONS FOR CYLINDRICAL PRESSURE CASE

% Source: A.P.F. Little et al, "Inelastic Buckling of Geometrically Imperfect
% Tubes Under External Hydrostatic Pressure," J. Ocean Tech., vol. 3, no. 1, 2008.

% Buckling of an infinitely long free pipe (MPa)
P_cr_inf = ((n^2-1)*E)/(12*(1-nu^2))*(wall/rad)^3;

% Compute Von Mises critical buckling pressure (MPa)
P_cr_vm = (  (E * (wall/rad)) / (n^2 - 1 + 0.5* (pi*rad / len)^2)  )  * ...
       (  ( 1/(n^2 * (len/pi*rad)^2 + 1)^2 )  +  ( wall^2 / ( 12*rad^2 * (1-nu^2)) ) * ...
       (  n^2 - 1 + (pi*rad/len)^2 )^2    );
   
% Compute Windenburg and Trilling's buckling pressure (DTMB) (MPa)
P_cr_dtmb = ( 2.42 * E * (wall / (2 * rad))^(5/2) ) / ...
            ( (1-(nu^2))^0.75 * ( (len/(2*rad)) - 0.447*(wall/(2*rad))^0.5 ) );
        

% Convert to psi
P_cr_inf = P_cr_inf * 145.04;
P_cr_vm = P_cr_vm * 145.04;
P_cr_dtmb = P_cr_dtmb * 145.04;


% Display results
fprintf('\nCritical buckling pressures for thin-walled cylinder:\n\n');
fprintf('Critical Pressure (infinite cylinder): %f (psi)\n', P_cr_inf);
fprintf('Critical Pressure (Von Mises): %f (psi)\n', P_cr_vm);
fprintf('Critical Pressure (DTMB): %f (psi)\n', P_cr_dtmb);



% CALCULATIONS FOR SPHERICAL PRESSURE CASE

% Critical pressure for buckling of a thin-walled sphere (MPa)
%P_cr = (2*E*wall^2) / ( r^2 * sqrt(3 * (1-nu^2)) )

% TODO
