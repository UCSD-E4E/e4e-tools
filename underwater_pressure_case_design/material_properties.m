% For saving material properties to a mat file
% 
% PROPERTIES:
%   material: material name
%   young: young's modulus (elastic tensile modulus) in kpsi
%   yield: yield strength in kpsi
%   poisson: Poisson's ratio
%   thermal: ??????
%   density: density in gm/cc

material = cellstr(['glass',  '6061',   '7075',   '316',   'delrn',   'UHMW',   'Ertal',   'PVC' ]);
young    = [9e3      10.6e3	  10.1e3   28.0e3	4.1e2	 0.6e2	  4.9e2     490	  ];  %kpsi
yield	 = [76       40		  73.0	   81.0	    10.0	 2.4	  13.0      4500  ];  %kpsi
poisson  = [.20      .332	  .332	   .332	    .332	 .332	  .332      0.4	  ]; 
thermal  = [3.2e-6	 23e-6	  23e-6	   23e-6	81e-6	 72e-6	  59e-6	    0     ];  %degC
density  = [ 2.23	 2.70	  2.75	   7.87	    1.42	 0.94	  1.39	    1.3   ];  %gm/cc

save material_properties.mat