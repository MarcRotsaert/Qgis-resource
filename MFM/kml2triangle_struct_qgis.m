function [E, P] = kml2triangle_struct(kmlFile,varargin)
% [E] = kml2triangle_struct(fileName,coorsystem)
% 
% kml-checklist:
% op volgorde met oplopende curvenrs
% boundaries    counterclockwise
% internals
% holes         clockwise
% %
% INPUT          
% fileName       : filename of KML file (Google earth pad)
% coor_system    : OPTIONAL conversion from lon-lat (DEFAULT = RD , second = UTM , lonlat!!)
% checkplot     : OPTIONAL (0/1) make plot of lines
% OUTPUT is structure E of curves 
%
% BLES 2015
%% check input
%% Default values voor the variable input list

% PROCESS the varargin
var_options = struct( ...
    'coor_system','RD',...
    'utmzone',0,...
    'pointsformat','finel',...
    'checkplot',1); ...

% process the variable input options 
var_options=process_varargin(var_options,varargin);

% initialise 
E=struct('type',[],'x',[],'y',[]); % initialise

% READ KML/KMZ file
if exist(kmlFile,'file');
    P = kml2struct(kmlFile);
else
    error(['Does not exist : ' kmlFile]);
end

%% READ struct P and convert to structure to be read by triangle mesh generator
for i=1:length(P);
    % pass name to output struct
    if isfield(P(i),'name');
        E(i).name=P(i).name;
    end
    
    % pass variables in description to output struct
    if isfield(P(i),'description') && ~isempty(P(i).description);
        E(i).description=P(i).description;
        disp(E(i).name);
        line=strtrim(textscan(P(i).description,'%s', 'Delimiter', '\n'));
        for j = 1:length(line{1});
            if ~isempty(line{1}{j});
                display(['E(', num2str(i), ').' strtrim(lower(line{1}{j})) ';']);
                try
                    eval(['E(i).' strtrim(lower(line{1}{j})) ';']);
                catch
                    disp(['WRONG expression in KML file (' E(i).name ') : ' ['E(' num2str(i)  ').' strtrim(lower(line{1}{j})) ';'] ])
                end
            end
        end
    end
       
    %% coordinates
    E(i).lon = P(i).lon;
    E(i).lat = P(i).lat;
    E(i).x   = P(i).lon;
    E(i).y   = P(i).lat;
    E(i).height = P(i).height;

    % checks om te kijken of alle required fields voor een bepaald type (b,
    % i, h) aanwezig is.
    % check ook lengte >= 2;
    if isfield(E(i),'type')
        if strcmpi(E(i).type,'b') || strcmpi(E(i).type,'i') || strcmpi(E(i).type,'h');
            % lengte line moet groter zijn dan > 2
            if length(E(i).lon) < 2; 
                error(['insufficient coordinates in : ' E(i).name, ', each line should have at least two points']);
            end
            if ~isfield(E, 'cnum'); 
                error(['boundary type ''b'' or ''i'' does not include a cnum in: ', E(i).name]); 
            end
        elseif strcmpi(E(i).type,'a') || strcmpi(E(i).type,'r')
            if ~isfield(E, 'maxarea'); 
                error(['area does not include a maxarea in: ', E(i).name]); 
            end
        end
    end
    if isfield(E(i),'dep');
        if ~isempty(E(i).dep) && isnumeric(E(i).dep);
            E(i).dep=zeros(size(E(i).x))+E(i).dep;
        end
    end
        
    % remove last (connecting point) from each boundary line)
end
%% convert lon lats to utm if no zone is given
if strcmpi(var_options.coor_system,'RD');
    for i=1:length(E);
        [E(i).x,E(i).y]=wgs842rd(E(i).lon,E(i).lat);
    end
    disp('Coordinate system converted to RD (rijksdriehoek)');
elseif strcmpi(var_options.coor_system, 'UTM');
    if var_options.utmzone==0;
        zone=fix((mean([E(:).lon]) / 6 ) + 31);
    else
        zone=var_options.utmzone;
    end
    for i=1:length(E);
        if ~isempty(E(i).lat);
            [E(i).x,E(i).y,utmzonedummy,lectra]=deg2utm(E(i).lat,E(i).lon,zone);
        else
            disp(['Curve number ' num2str(i) ' is empty']);
        end
    end
    disp(['Coordinate system converted to UTM zone ' num2str(zone) ' ' lectra]);
    E(1).utmzone=[num2str(zone) ' ' lectra];
elseif strcmpi(var_options.coor_system, 'minna_badagry');
    % functions for badagry not included (special case)
    for i=1:length(E);
        [E(i).x,E(i).y]=wgs842minna_badagry(E(i).lat,E(i).lon);
    end
    disp('Coordinate system converted to minna (Badagry, Nigeria)');
elseif strcmpi(var_options.coor_system, 'Tema');
    % functions for badagry not included (special case)
    for i=1:length(E);
        [E(i).x,E(i).y]=wgs842tema(E(i).lat,E(i).lon);
    end
    disp('Coordinate system converted to TEMA ');
end

%% extract point from folder 'points' to generate finel/swan output locations
if isfield(P,'Points');
    E(1).Points=P(1).Points;      
    for ii=1:length(P(1).Points);
        if strcmpi(var_options.coor_system,'RD');
            [E(1).Points(ii).xp,E(1).Points(ii).yp]=wgs842rd(E(1).Points(ii).lon,E(1).Points(ii).lat);
        elseif strcmpi(var_options.coor_system,'minna_badagry');
            [E(1).Points(ii).xp,E(1).Points(ii).yp]=wgs842minna_badagry(E(1).Points(ii).lat,E(1).Points(ii).lon);
        elseif strcmpi(var_options.coor_system,'Tema');
            [E(1).Points(ii).xp,E(1).Points(ii).yp]=wgs842tema(E(1).Points(ii).lat,E(1).Points(ii).lon);
        elseif strcmpi(var_options.coor_system, 'UTM');
            [E(1).Points(ii).xp,E(1).Points(ii).yp]=deg2utm(E(1).Points(ii).lat,E(1).Points(ii).lon,zone);
        elseif strcmpi(var_options.coor_system, 'LATLON')
            E(1).Points(ii).xp=E(1).Points(ii).lon;
            E(1).Points(ii).yp=E(1).Points(ii).lat;
        end
        if strcmpi(var_options.pointsformat,'finel');
            fprintf(1,'hist(%4d)%%stationname='' %28s '' hist(%4d)%%x=    %12.2f       hist(%4d)%%y=   %12.2f\n',...
                ii,E(1).Points(ii).name,ii,E(1).Points(ii).xp,ii,E(1).Points(ii).yp);
        end
    end
    if strcmpi(var_options.pointsformat,'swan');
        % schrijf in 3 delen
        % POINTS Section
        for ii=1:length(P(1).Points);
            pn{ii}=strtrim(P(1).Points(ii).name);
            if length(pn{ii})>8;pn{ii}=pn{ii}(1:8);end
            if strcmpi(var_options.coor_system, 'LATLON')
                fprintf(1,'POINTS  %-10s             %12.2f   %12.2f \n',...
                    ['''' pn{ii} ''''],E(1).Points(ii).lon,E(1).Points(ii).lat);
            elseif strcmpi(var_options.coor_system, 'UTM');
                [E(1).Points(ii).xp,E(1).Points(ii).yp]=deg2utm(E(1).Points(ii).lat,E(1).Points(ii).lon,zone);
                fprintf(1,'POINTS  %-10s             %12.2f   %12.2f \n',...
                    ['''' pn{ii} ''''],E(1).Points(ii).xp,E(1).Points(ii).yp);
            end
        end
        fprintf(1,'\n');
        % Table section
        % TABle 'Europf' HEAD 'Europf.tbl' &
        for i=1:length(P(1).Points)
            fprintf(1,'TABle    %-10s    HEAD   %-12s      & \n',...
                ['''' pn{i} ''''],['''' pn{i} '.tbl' '''']);
            fprintf(1,'         TIME XP YP DEP HS DHSign TM01 DRTM01 HSWELL RTP TPS PDIR DIR PER DSPR WIND OUTPUT YYYYMMDD.0000 DT MIN \n')
        end
        fprintf(1,'\n');
        % SPEC  section
        % SPEC  'Europf' SPEC2D ABS 'Europf.sp2' &
        for i=1:length(P(1).Points)
            fprintf(1,'SPEC     %10s  SPEC2D ABS %12s       &  \n',...
                ['''' pn{i} ''''],['''' pn{i} '.sp2' '''']);
            fprintf(1,'         OUTPUT YYYYMMDD.0000 DT MIN\n');
        end
        fprintf(1,'\n');
    end
end
        
%% plotten maar
if var_options.checkplot    
    col={'g','r'};
    figure;
    for i=1:length(E);
        hold on
        plot(E(i).x,E(i).y,col{mod(i,2)+1});
        hold on;plot(E(i).x,E(i).y,['.' col{mod(i+1,2)+1}]);
        if isfield(E,'cnum');
            ucnum=unique(E(i).cnum);
            for j=1:length(ucnum);
                text(E(i).x(j),E(i).y(j),num2str(ucnum(j)));
            end
        end
        minimum_distance=5.5;
        dis=abs(hypot(diff(E(i).x),diff(E(i).y)));
        idis=find(dis<minimum_distance);
        if ~isempty(idis);
            plot(E(i).x(idis),E(i).y(idis),'bd');
        end
        if isfield(E,'Points') && ~isempty(E(1).Points(1).xp);
            plot([E(1).Points(:).xp],[E(1).Points(:).yp],'b.');
            for i=1:length(E(1).Points);
                text([E(1).Points(i).xp],[E(1).Points(i).yp],['  ' E(1).Points(i).name],'fontsize',8)
            end
        end
    end
    axis equal;
end

%% axis toevoegen

E(1).Al=[min([E(:).lon]) max([E(:).lon]) min([E(:).lat]) max([E(:).lat])];
E(1).A =[min([E(:).x])   max([E(:).x])   min([E(:).y])   max([E(:).y])  ];

% %% check order
% ib=findstr([E.type],'b');
% ii=findstr([E.type],'i');
% ih=findstr([E.type],'h');
% ir=findstr([E.type],'r');
% ia=findstr([E.type],'a');

end % function

function [X,Y]=wgs842rd(Lon,Lat)
%[X,Y]=wgs842rd(Lon,Lat) 
%Zet WGS84 coordinaten (lon-lat) om in Rijksdriehoek coordinaten.
% WAARSCHUWING: is inexact --> afwijking kan tot 100 m zijn!!!

Latv=Lat(:);
Lonv=Lon(:);

phi=Latv;
labda=Lonv;

% Zet labda,phi vectoren om in rij vectoren
phitest=size(phi);
labdatest=size(labda);

if phitest(2)==1;
    phi=phi';
end

if labdatest(2)==1;
    labda=labda';
end


X0=155000;
Y0=463000;
phi0=52.15517440;
labda0=5.38720621;

dphi=0.36*(phi-phi0);
dlabda=0.36*(labda-labda0);

tabelR= [0 1 190094.945;
         1 1 -11832.228;
         2 1 -114.221;
         0 3 -32.391;
         1 0 -0.705;
         3 1 -2.340;
         1 3 -0.608;
         0 2 -0.008;
         2 3 0.148];
     
tabelS= [1 0 309056.544;
         0 2 3638.893;
         2 0 73.077;
         1 2 -157.984;
         3 0 59.788;
         0 1 0.433;
         2 2 -6.439;
         1 1 -0.032;
         0 4 0.092;
         1 4 -0.054];
     
     
X2=zeros(length(tabelR),length(labda));
     
for i=1:length(tabelR)
    X2(i,:)=tabelR(i,3).*(dphi.^tabelR(i,1)).*(dlabda.^tabelR(i,2));
end
X=X0+sum(X2,1);

Y2=zeros(length(tabelS),length(phi));

for i=1:length(tabelS)
    Y2(i,:)=tabelS(i,3).*(dphi.^tabelS(i,1)).*(dlabda.^tabelS(i,2));
end
Y=Y0+sum(Y2,1);

X=reshape(X,size(Lat));
Y=reshape(Y,size(Lat));
end %function
function  [x,y,utmzone,Letra] = deg2utm(Lat,Lon,zone)
% -------------------------------------------------------------------------
% [x,y,utmzone] = deg2utm(Lat,Lon)
%
% Description: Function to convert lat/lon vectors into UTM coordinates (WGS84).
% Some code has been extracted from UTM.m function by Gabriel Ruiz Martinez.
%
% Inputs:
%    Lat: Latitude vector.   Degrees.  +ddd.ddddd  WGS84
%    Lon: Longitude vector.  Degrees.  +ddd.ddddd  WGS84
%BLES 
%  if nargin==3 => use only 1 zone
% e.g. [x,y,utmzone] = deg2utm(Lat,Lon,'33 T')
%
%
% Outputs:
%    x, y , utmzone.   See example
%
% Example 1:
%    Lat=[40.3154333; 46.283900; 37.577833; 28.645650; 38.855550; 25.061783];
%    Lon=[-3.4857166; 7.8012333; -119.95525; -17.759533; -94.7990166; 121.640266];
%    [x,y,utmzone] = deg2utm(Lat,Lon);
%    fprintf('%7.0f ',x)
%       458731  407653  239027  230253  343898  362850
%    fprintf('%7.0f ',y)
%      4462881 5126290 4163083 3171843 4302285 2772478
%    utmzone =
%       30 T
%       32 T
%       11 S
%       28 R
%       15 S
%       51 R
%
% Example 2: If you have Lat/Lon coordinates in Degrees, Minutes and Seconds
%    LatDMS=[40 18 55.56; 46 17 2.04];
%    LonDMS=[-3 29  8.58;  7 48 4.44];
%    Lat=dms2deg(mat2dms(LatDMS)); %convert into degrees
%    Lon=dms2deg(mat2dms(LonDMS)); %convert into degrees
%    [x,y,utmzone] = deg2utm(Lat,Lon)
%
% Author: 
%   Rafael Palacios
%   Universidad Pontificia Comillas
%   Madrid, Spain
% Version: Apr/06, Jun/06, Aug/06, Aug/06
% Aug/06: fixed a problem (found by Rodolphe Dewarrat) related to southern 
%    hemisphere coordinates. 
% Aug/06: corrected m-Lint warnings
%-------------------------------------------------------------------------

% Argument checking
%
warning off
error(nargchk(2, 3, nargin));  %2 arguments required
[mm,nn]=size(Lat);
Lat=reshape(Lat(:),length(Lat(:)),1);
Lon=reshape(Lon(:),length(Lon(:)),1);

n1=length(Lat);
n2=length(Lon);
if (n1~=n2)
   error('Lat and Lon vectors should have the same length');
end


% Memory pre-allocation
%
x=zeros(n1,1);
y=zeros(n1,1);
% Letra=zone(3);

if exist('zone', 'var');
    if ~isnumeric(zone);
        zone=str2double(zone(1:2));
    end
end

%utmzone(n1,:)='60 X';

% Main Loop
%
for i=1:n1
   la=Lat(i);
   lo=Lon(i);

   sa = 6378137.000000 ; sb = 6356752.314245;
         
   %e = ( ( ( sa ^ 2 ) - ( sb ^ 2 ) ) ^ 0.5 ) / sa;
   e2 = ( ( ( sa ^ 2 ) - ( sb ^ 2 ) ) ^ 0.5 ) / sb;
   e2cuadrada = e2 ^ 2;
   c = ( sa ^ 2 ) / sb;
   %alpha = ( sa - sb ) / sa;             %f
   %ablandamiento = 1 / alpha;   % 1/f

   lat = la * ( pi / 180 );
   lon = lo * ( pi / 180 );
   
   if nargin==2;
       Huso = fix( ( lo / 6 ) + 31);
       S = ( ( Huso * 6 ) - 183 );
       deltaS = lon - ( S * ( pi / 180 ) );
       if (la<-72), Letra='C';
       elseif (la<-64), Letra='D';
       elseif (la<-56), Letra='E';
       elseif (la<-48), Letra='F';
       elseif (la<-40), Letra='G';
       elseif (la<-32), Letra='H';
       elseif (la<-24), Letra='J';
       elseif (la<-16), Letra='K';
       elseif (la<-8), Letra='L';
       elseif (la<0), Letra='M';
       elseif (la<8), Letra='N';
       elseif (la<16), Letra='P';
       elseif (la<24), Letra='Q';
       elseif (la<32), Letra='R';
       elseif (la<40), Letra='S';
       elseif (la<48), Letra='T';
       elseif (la<56), Letra='U';
       elseif (la<64), Letra='V';
       elseif (la<72), Letra='W';
       else Letra='X';
       end
       
   else
       
       Huso = zone ;%fix( ( mean(Lon) / 6 ) + 31);
       S = ( ( Huso * 6 ) - 183 );
       deltaS = lon - ( S * ( pi / 180 ) );
       
   end
       
   a = cos(lat) * sin(deltaS);
   epsilon = 0.5 * log( ( 1 +  a) / ( 1 - a ) );
   nu = atan( tan(lat) / cos(deltaS) ) - lat;
   v = ( c / ( ( 1 + ( e2cuadrada * ( cos(lat) ) ^ 2 ) ) ) ^ 0.5 ) * 0.9996;
   ta = ( e2cuadrada / 2 ) * epsilon ^ 2 * ( cos(lat) ) ^ 2;
   a1 = sin( 2 * lat );
   a2 = a1 * ( cos(lat) ) ^ 2;
   j2 = lat + ( a1 / 2 );
   j4 = ( ( 3 * j2 ) + a2 ) / 4;
   j6 = ( ( 5 * j4 ) + ( a2 * ( cos(lat) ) ^ 2) ) / 3;
   alfa = ( 3 / 4 ) * e2cuadrada;
   beta = ( 5 / 3 ) * alfa ^ 2;
   gama = ( 35 / 27 ) * alfa ^ 3;
   Bm = 0.9996 * c * ( lat - alfa * j2 + beta * j4 - gama * j6 );
   xx = epsilon * v * ( 1 + ( ta / 3 ) ) + 500000;
   yy = nu * v * ( 1 + ta ) + Bm;

   if (yy<0)
       yy=9999999+yy;
   end

   if isnan(Huso)
       Huso=99;
   end
   
   x(i)=xx;
   y(i)=yy;
 %eval(['utmzone(i,1:2)=''',num2str(Huso),''';']);
 %eval(['utmzone(i,3:4)='' ',Letra,''';']);
    %utmzone(i,1:4)=sprintf('%02d %c',Huso,Letra);
    utmzone(1)=Huso;
end

x=reshape(x,[mm nn]);
y=reshape(y,[mm nn]);

la=mean(Lat);
if (la<-72), Letra='C';
elseif (la<-64), Letra='D';
elseif (la<-56), Letra='E';
elseif (la<-48), Letra='F';
elseif (la<-40), Letra='G';
elseif (la<-32), Letra='H';
elseif (la<-24), Letra='J';
elseif (la<-16), Letra='K';
elseif (la<-8), Letra='L';
elseif (la<0), Letra='M';
elseif (la<8), Letra='N';
elseif (la<16), Letra='P';
elseif (la<24), Letra='Q';
elseif (la<32), Letra='R';
elseif (la<40), Letra='S';
elseif (la<48), Letra='T';
elseif (la<56), Letra='U';
elseif (la<64), Letra='V';
elseif (la<72), Letra='W';
else Letra='X';
end

end % function
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
function kmlStruct = kml2struct(kmlFile)
% kmlStruct = kml2struct(kmlFile)
%
% Import a .kml file as a vector array of shapefile structs, with Geometry, Name,
% Description, Lon, Lat, and BoundaryBox fields.  Structs may contain a mix
% of points, lines, and polygons.
%
% .kml files with folder structure will not be presented as such, but will
% appear as a single vector array of structs.
%
% 
% eerst inlezen om (mogelijkerwijs) coordinate system te scoren

%% read KML file
[pathstr,fileName,ext] = fileparts(kmlFile); 
if strcmpi(lower(ext), '.kmz');
    tt = unzip([fileName, '.kmz']);
    for i=1:length(tt);
        [pathstr,fileName,ext] = fileparts(tt{i});
        if strcmpi(ext,'.kml');
            [FID msg] = fopen(tt{i},'rt');
            if FID<0;error(['ERROR : kml2struct: ' tt{i} ' does not exist']);end
            txt = fread(FID,'uint8=>char')';
            fclose(FID);
        end
        delete(tt{i});
    end
elseif strcmpi(lower(ext), '.kml');
    [FID msg] = fopen(kmlFile,'rt');
    if FID<0;error(['ERROR : kml2struct: ' kmlFile ' does not exist']);end
    txt = fread(FID,'uint8=>char')';
    fclose(FID);
end


%% read text in variable


% Make exception for the Points folder 
% Search Points folder
Points_section=[];
expr = '<Folder.+?>.+?</Folder>';
objectStrings = regexp(txt,expr,'match');
for i=1:length(objectStrings);
    bucket = regexp(objectStrings{i},'<name.*?>.+?</name>','match');
    if isempty(bucket)
        name = 'undefined';
    else
        % Clip off flags
        name = regexprep(bucket{1},'<name.*?>\s*','');
        name = regexprep(name,'\s*</name>','');
    end
    disp(strtrim(name))
    if strcmpi(strtrim(name),'Points')
        Points_section=objectStrings{i};
    end
end
% remove Points folder from txt section 
if ~isempty(Points_section)
    txt=regexprep(txt,Points_section,'');
    
    % Search for Placemarks : extract Points coordinates with names;
    expr = '<Placemark.+?>.+?</Placemark>';
    objectStrings = regexp(Points_section,expr,'match');
    
    for ii = 1:length(objectStrings);
        % Find Object Name Field
        bucket = regexp(objectStrings{ii},'<name.*?>.+?</name>','match');
        if isempty(bucket)
            name = ['undefined_point' num2str(ii)];
        else
            % Clip off flags
            name = regexprep(bucket{1},'<name.*?>\s*','');
            name = regexprep(name,'\s*</name>','');
            kmlStruct(1).Points(ii).name = name;
        end
        if ~isempty(regexp(objectStrings{ii},'<Point', 'once'))
            bucket = regexp(objectStrings{ii},'<coordinates.*?>.+?</coordinates>','match');
            % Clip off flags
            coordStr = regexprep(bucket{1},'<coordinates.*?>(\s+)*','');
            coordStr = regexprep(coordStr,'(\s+)*</coordinates>','');
            % Split coordinate string by commas or white spaces, and convert string
            % to doubles
            coordMat = str2double(regexp(coordStr,'[,\s]+','split'));
            % Rearrange coordinates to form an x-by-3 matrix
            [m,n] = size(coordMat);
            coordMat = reshape(coordMat,3,m*n/3)';
            kmlStruct(1).Points(ii).lon = coordMat(:,1);
            kmlStruct(1).Points(ii).lat = coordMat(:,2);
            kmlStruct(1).Points(ii).height= coordMat(:,3);
        end
    end
end

% Search for Placemarks (meaning sections of Points, Line or Polygon
expr = '<Placemark.+?>.+?</Placemark>';
objectStrings = regexp(txt,expr,'match');

for ii = 1:length(objectStrings);
    % Find Object Name Field
    bucket = regexp(objectStrings{ii},'<name.*?>.+?</name>','match');
    if isempty(bucket)
        name = 'undefined';
    else
        % Clip off flags
        name = regexprep(bucket{1},'<name.*?>\s*','');
        name = regexprep(name,'\s*</name>','');
    end
    
    % Find Object Description Field
    bucket = regexp(objectStrings{ii},'<description.*?>.+?</description>','match');
    if isempty(bucket)
        desc = '';
    else
        % Clip off flags
        desc = regexprep(bucket{1},'<description.*?>\s*','');
        desc = regexprep(desc,'\s*</description>','');
    end
    
    geom = 0;
    % Identify Object Type
    if ~isempty(regexp(objectStrings{ii},'<Point', 'once'))
        geom = 1;
    elseif ~isempty(regexp(objectStrings{ii},'<LineString', 'once'))
        geom = 2;
    elseif ~isempty(regexp(objectStrings{ii},'<Polygon', 'once'))
        geom = 3;
    end
    
    switch geom
        case 1
            geometry = 'Point';
        case 2
            geometry = 'Line';
        case 3
            geometry = 'Polygon';
        otherwise
            geometry = '';
    end
    
    % Find Coordinate Field
    bucket = regexp(objectStrings{ii},'<coordinates.*?>.+?</coordinates>','match');
    % Clip off flags
    coordStr = regexprep(bucket{1},'<coordinates.*?>(\s+)*','');
    coordStr = regexprep(coordStr,'(\s+)*</coordinates>','');
    numcomma=length(findstr(coordStr,','));
    % Split coordinate string by commas or white spaces, and convert string
    % to doubles
    coordMat = str2double(regexp(coordStr,'[,\s]+','split'));
	% quick solution with Sanne 
	if mod(length(coordMat)./numcomma,1) >0;
		col_shape=3;
	else mod(length(coordMat)./numcomma,1)==0; % dan istie nm 2
		col_shape=2;
	end
	          
    if ~isnan(coordMat);
        % Rearrange coordinates to form an x-by-3 matrix
        [m,n] = size(coordMat);
        coordMat = reshape(coordMat,col_shape,m*n/col_shape);
    
        % fill coordinates
        Lon = coordMat(1,:);
        Lat = coordMat(2,:);
        if col_shape==3;
            Height= coordMat(3,:);
        else
            Height= Lon.*0;
        end
    else
        Lon=[];
        Lat=[];
        Height=[];
    end
    % Create structure
    kmlStruct(ii).geometry = geometry;
    kmlStruct(ii).name = name;
    kmlStruct(ii).description = cleankmlstring(desc);
    kmlStruct(ii).lon = Lon;
    kmlStruct(ii).lat = Lat;
    kmlStruct(ii).height = Height;
    kmlStruct(ii).boundingBox = [min(Lon(:)) min(Lat(:));max(Lon(:)) max(Lat(:))];
end

   
end % function
%%%%%%%%%%%n
function clean_string=cleankmlstring(string)
% function clean_string=cleankmlstring(string)
% in KLM (or xml) files some characters need to to be replaced, see
% BLES 2015
clean_string=strrep(string, '&lt;','<');
clean_string=strrep(clean_string, '&gt;','>');
clean_string=strrep(clean_string,'&apos;','''');
clean_string=strrep(clean_string, '&quot;','"');
end % function

function options=process_varargin(options,varargin_list)
%function options=process_varargin(options)
% process the variable input list 
% list always in pairs 
% Example 
% varargin_list={'checkplot',1,'coorsystem','utm','timezone','utc'}
% options = struct( ...
%    'plot',yes',...
%    'coor_system','RD',...
%    'utmzone',0,...
%    'checkplot',1); 
% not all fieldnames in options needs to be included in the varargin_list 
%
% BLES 2015

if nargin==1 || isempty(options);
    options=struct;
end
nfound=0;
fn=fieldnames(options);
num_varargin=length(varargin_list)./2;

while ~isempty(varargin_list)
    for i=1:length(fn)
        if strcmpi(strtrim(varargin_list{1}),fn{i});
            options.(fn{i}) = varargin_list{2};
            nfound=nfound+1;
        end
    end
    varargin_list(1:2) = [];
end
if nfound<num_varargin;
    error('not all inputs processed-> check input names')
end
end %function