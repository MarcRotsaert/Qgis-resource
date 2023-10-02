addpath('Z:\MatlabToolbox\Sva$TRI')


E1=kml2triangle_struct_qgis('$PAD/$KML.kml','coor_system','$CRS');
[T,E2]=make_triangle_grid(E1,'$PAD/$MESH' $ARG $VARARGIN);
cd $PAD
triangle2sepran4$IMP_EXP($E2 '$MESH.1','$PAD/$MESH.out')



