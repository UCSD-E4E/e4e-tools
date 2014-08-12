function [ stats ]= pcase(index,len,wall,od,display)
%function [ Pflow Pinf Pstab beam simple hemi] = 
%                pcase(index,length,wall,od,display)
% PARAMETERS: 
%   index: material index:
%       1 =  borosilicate glass
%       2 = 6061-T6 aluminum
%       3 = 7075-T6 aluminum
%       4 = 316 stainless
%       5 = delrin
%       6 = UHMW polyethylene
%       7 = Ertalyte
%       8 = PVC (Polyvinyl chloride)
%   len: length of pressure case in inches
%   wall: wall thickness in inches
%   od: outer diameter of pressure case in inches
%   display: 1 will display the results in a readable format
%
% MATERIAL PROPERTIES:
%   material: material name
%   young: young's modulus (elastic tensile modulus) in kpsi
%   yield: yield strength in kpsi
%   poisson: Poisson's ratio
%   thermal: ??????
%   density: density in gm/cc
%
% RETURNS:
%   Pflow: pressure for plastic flow in psi 
%   Pinf: instabilities of infinite length scale in psi 
%   Pstab: finite length instabilities in psi
%   beam: min. thickness for beam-supported flat end-cap (thousandths of an inch)
%   simple: min. thickness for simple-supported flat end-cap (thousandths of an inch)
%   hemi: min. thickness for semi-hemispherical end-cap (thousandths of an inch)
%   
% input is in inches
% output is in psi and 1000*inches



% Load materials data
load 'material_properties.mat'


pcase_properties = ['Plastic flow    (psi)'; 
        'infinite Length (psi)';
		'Finite Length   (psi)';
		'Beam EndCap     (mil)';
		'Simple EndCap   (mil)';
		'Semi-Hemisphere (mil)';
		];

    
% Calculations for cylinderical pressure case follow.
E = 1000.0 * young(index);
SY = 1000.0 * yield(index);
nu = poisson(index);
a = od/2;  % = radius

Pflow = wall .* SY ./ a;
Pinf = E .* (wall ./ a).^3 ./ ( 4*(1-nu.*nu) );
Pstab = 0.807 * E .* (wall ./ len) .* (wall./a).^1.5 ./ ((1-nu.*nu).^0.75);
      
% Pflow is pressure for plastic flow. 
% Pinf is for instabilities of infinite length scale. 
% Pstab is for finite length instabilities.
pressure = [ Pflow; Pinf; Pstab ];
pressure = floor(pressure);
Pfail = min(pressure);  % max pressure before fails in one of the modes
    
% now compute minimum end-cap thicknesses
beam = (a - wall) .* sqrt(0.75 * Pfail ./ SY);
simple = (a - wall) .* sqrt(0.375 * (3+nu) .* Pfail ./ SY);
hemi = a .* Pfail ./ (2*SY);
thickness = [ beam; simple; hemi] * 1000;
thickness = floor(thickness);

stats = [ pressure; thickness;];
n = length(wall);  % # of unique pts

if (display==1)
  disp('Failure Pressures and minimum End Cap thicknesses Reqd:')
  
  for i = 1 : size(pcase_properties, 1)
    t = pcase_properties(i,:);  %initialize output string
    
    for j = 1 : n
	  s = sprintf('%6.0f',stats(i,j) );
	  t = [t  s ];
    end
    
	disp(t)
  end
end