% Properties of materials that can be used for underwater pressure cases
%
% Saves the materials properties to a mat file for use in the pressure case
% calculations script
%
% IMPORTANT NOTE: If you have a particular material datasheet available, 
% it would be best to replace the current values for the material with
% those from your datasheet. The values in this script are approximate
% values only.
% 
% Author: Antonella Wilby
% Last Updated: 8/20/14
% 
% PROPERTIES:
%   1: young's modulus (elastic tensile modulus) in MPa
%   2: ultimate tensile strength in MPa
%   3: yield strength in MPa
%   4: Poisson's ratio
%   5: thermal conductivity at 77-degF in W/m K
%   6: density in gm/cc
 

% Material Index:

% 1: Borosilicate Glass
% Source: http://www.matweb.com/search/datasheet.aspx?matguid=5bb651ca58524e79a503011b2cd8083d
glass = [62750;  100;  35;  0.20;  1.2;  2.23];

% 2: 6061-T6 Aluminum (properties listed for T6 temper)
% Source: http://asm.matweb.com/search/SpecificMaterial.asp?bassnum=MA6061t6
al_6061_t6 = [68900;  310;  276;  0.33;   167;  2.70];

% 3: 7075-T6 Aluminum (properties listed for T6 temper)
% Source: http://asm.matweb.com/search/SpecificMaterial.asp?bassnum=MA7075T6
al_7075_t6 = [71700;  572;  503;  0.33;  130;  2.81];

% 4: 316 Stainless Steel 
% Source: http://asm.matweb.com/search/SpecificMaterial.asp?bassnum=MQ316A
ss_316 = [193000;  580;  290;  0.265;  16.3;  8.0];

% 5: Delrin D100
% Source: http://plastics.dupont.com/plastics/pdflit/americas/delrin/H76836.pdf
delrin = [3120;  69;  69;  0.332;  0.33;  1.42];

% 6: UHMW (Ultra-High Molecular Weight) Polyethylene
% Source: http://www.boedeker.com/polye_p.htm
uhmw = [552;  40;  40;  0.332;  72e-6;   0.93];

% 7: Ertalyte
% Source: http://www.matweb.com/search/datasheettext.aspx?matguid=281e3a595e624a06bf49d9c6138092e5
ertalyte = [3170;  85.5;  85.5;  0.332;  0.288; 1.41];

% 8: PVC - Polyvinyl chloride (rigid)
% Source: https://www.plasticsintl.com/datasheets/PVC.pdf
pvc = [2834;  51.7;  31;  0.4;  0.16;  1.3];

% 9: Acrylic - Poly(methyl methacrylate)
% Source: http://www.associatedplastics.com/forms/acrylic_plastics_data.pdf
acrylic = [3100;  72.4;  72.4;  0.35;  0.17;  1.18]; % metric

% 10: Lexan 9030 Polycarbonate
% Source: http://www.associatedplastics.com/forms/pc_lexan_9034.pdf
lexan = [2379; 65.5; 62.1; 0.37; 0; 0];

materials = [glass al_6061_t6 al_7075_t6 ss_316 delrin uhmw ertalyte pvc acrylic];

save('material_properties.mat', 'materials');
