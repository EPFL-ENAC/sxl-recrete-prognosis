function [delta, delta1, delta2, alpha, Select_alpha, Select_syst, Select_sol, Para_L0, Para_L1,Para_hsreuse,Para_year,Para_steelprofile_type,Para_beamposition,Para_Q0,Para_Q1,Para_tpdist_beton_reuse,Para_tpdist_metal_reuse,impactreuse_m2,impactnew_m2]=fun_CERES(hsreuse,year,steelprofile_type,beamposition,Q0,Q1,tpdist_beton_reuse,tpdist_metal_reuse)
% clear all
% clc

% % for hsreuse=0.14:0.02:0.22; %épaisseur de la dalle de réemploi [m] --> VARIABLE
% hsreuse=0.18;
% year=2; % year=2; %1=depuis 1989; 2=entre 1968 et 1988 ; 3=entre 1956 et 1967 --> VARIABLE
% steelprofile_type=2; %type acier: newsteel=1; reusedsteel=2; --> VARIABLE
% Q0=3; %charge utiles donneur [kN/m2] --> VARIABLE
% Q1=3;%charge utiles recevru [kN/m2] --> VARIABLE
% tpdist_beton_reuse=100;
% tpdist_metal_reuse=100;
% beamposition=1; %scénario receveur: ; belowconcrete=1; concreteplane=2 --> VARIABLE

%% données de bases donneur et receveur
%masses volumiques
massevol_BA=2500; %[kg/m3]
massevol_metal=7850; %masse volumique métal [kg/m3] KBOB 06.003
massevol_beton=2300; %masse volumique béton [kg/m3] KBOB 01.002
massevol_armature=7850; %masse volumique acier armature [kg/m3] KBOB 06.003
massevol_panneaux=453; %masse volumique des panneaux de coffrage [kg/m3] KBOB 07.001
massevol_mortier=1400; %masse volumique du mortier [kg/m3] KBOB 04.008
massevol_jointpoly=1600; %masse volumique du cordon de joint en mousse polyéthylène (PU) [kg/m3] KBOB 08.004
massevol_caoutchouc=1100; %masse volumique du lés en caoutchouc EPDM [kg/m3] KBOB 0.004
epaisseur_caoutchouc=0.004; %épaisseur caoutchouc [m]


%% caractérstiques du donneur
if year==1 %depuis 1989
    Fsd_armamin=435000; %[kN/m2] résistance de l'acier selon tableau 8 de la SIA 269.2
end
if year==2 %entre 1968 et 1988
    Fsd_armamin=390000;
end
if year==3 %entre 1956 et 1967
    Fsd_armamin=300000;
end
tauxarmature0=0.015; %taux d'armature dans la dalle donneuse

Gslab0=hsreuse*massevol_BA/100; %charge permanentes [kN/m2]
y_Gslab0=1.35; %coefficient de sécurité nouvelles charges permanentes
Grev0=1; %charge de nouvelle chappe [kN/m2]
y_rev0=1.35; %coefficient de sécurité nouvelles charges permanentes
y_Q0=1.5; %coefficient de sécurité charges utiles
Ebeton=15000; % Module d'elasticite fissuré env. Econc/3 [N/mm2]
Ibeton=(hsreuse*1000)^3*1000/12; %Inertie section par metre [mm4]

%% caractérstiques du receveur
y_Gslab1=1.2; %coefficient de sécurité charges permanentes existantes
y_rev1=1.35; %coefficient de sécurité charge permannentes nouvelles
Grev1=1; %charge de la nouvelle chappe [kN/m2]
y_Q1=1.5; %coefficient de sécurité charges utiles
Psi_1=0.3; %facteur psi pour la charge quasi perm pour un logement ou bureau SIA 260
profileE=205000; %module elasticité profilé [N/mm2]

if steelprofile_type==1 %recycledsteel
fyd=335/1.05; %résistance profilé [N/mm2]
end
if steelprofile_type==2 %reusedsteel
fyd=235/1.05; %Résistance profilé de réemploi (pas acier de la meilleure qualité) [N/mm2]
end

%données sur les cornières neuves pour appuyer les poutres dans le système 2
masse_lin_corn2=59.9; %[kg/m] masse linéaire d'une cornière LNP200x20

%% données sur les profilés pour système 2
% classés par W ERREUR ICI
if beamposition==1 %belowconcrete
    data=xlsread('data_beams_1.xlsx','1','B3:S29');
end
% if beamposition==2 %concreteplane
%     data=xlsread('data_beams_2.xlsx','1','B3:R30');
% end

profile_mass=data(:,3)*10^-3; %masse linéaire des profilés utilisés dans les poutres[kN/m]
profile_W=data(:,4)*10^3; %Wy des profilés utilisés dans les poutres [mm3]
profile_I=data(:,5)*10^6; %I des profilés utilisés dans les poutres [mm4]
profile_hauteur=data(:,2); %hauteur du profilé [mm]
profile_largeurtot=data(:,6); %Largeur totale du profilé [mm]
profile_degreasedsurf=data(:,12); %[m2/m] surface dégraissée et repeintre par mètre de poutre de réemploi -> PAS AUSSI LES NEUVES? VOIR Brütting et al.
beam_sol=data(:,1); %numero de poutres telles que listées dans "selection profiles.xls"
beam_vol_betonremplissage=data(:,14); %aire du profilé [m3/m]
beam_welding=data(:,13); %[m/m] mètre de soudure par mètre de poutre
beam_largeurentrepiece=data(:,15); %[mm]
beam_caoutchoucwidth=data(:,18); %[mm]

supportingplates_mass=data(:,11)*10^-3; %masse de la plaque en acier pour les profilés de moins de 200mm de large [kN/m]

if steelprofile_type==1 %recycledsteel
    profile_unwelding=data(:,16); %[m/profilé] mètre à dé-souder pour démonter un profilé
    profile_sandblastedsurf=data(:,17); %[m2/m] surface sandblastée par mètre de profilé de réemploi
end
if steelprofile_type==2 %reusedsteel
    profile_unwelding=data(:,8); %[m/profilé] mètre à dé-souder pour démonter un profilé
    profile_sandblastedsurf=data(:,9); %[m2/m] surface sandblastée par mètre de profilé de réemploi
end
if beamposition==1 %belowconcrete
   beam_selfweight=1.03; %facteur à rajouter à la charge sur les poutres liées à leur poids propre
end
if beamposition==2 %concreteplane
   beam_selfweight=1.1; %facteur à rajouter à la charge sur les poutres liées à leur poids propre
end

profile_MRd=0.7*profile_W*fyd/10^6; %MRd profilé kNm

%% schéma de découpes
%L_alpha, alpha*L0 doit grantir que Mrd_armamin0 > Med_1
Qtotsurfacique1=y_Gslab1*Gslab0+y_rev1*Grev1+y_Q1*Q1; %charge surfacique receveur [kN/m2]
Qtotsurfacique0=y_Gslab0*Gslab0+y_rev0*Grev0+y_Q0*Q0; %charge surfacique donneur [kN/m2]
alpha=(Qtotsurfacique0/Qtotsurfacique1/3)^(1/2);
%L_armamin
if hsreuse<0.18
    r_barremin=4/1000; %rayon d'une barre d'armature minimum [m]
else
    r_barremin=5/1000; %rayon d'une barre d'armature minimum [m]
end
Aire_barremin=pi*r_barremin^2; %aire d'une barre d'armature minimum[m2]
espa_barremin=0.150; %espacement entre les barres d'armature minimum [m]
n_barremin=1/espa_barremin; % nombre de barre d'armature par mètre linéaire [n/m]
Aire_armamin=Aire_barremin*n_barremin; % aire de toutes les barres d'armatures par mètre [m2/m]
Mrd_armamin=Aire_armamin*Fsd_armamin*0.81*hsreuse; %moment résistant apporté par les armatures minimums et le béton [m3]
L_armamin=(Mrd_armamin*8/Qtotsurfacique1)^(1/2)+0.15; %+0.15 ok?

%% données coffrage et étayage pour NEW (SYSTEM 0)
%panneaux
h_panneaux=0.021; %[m] épaisseur des panneaux
massesurf_panneaux=massevol_panneaux*h_panneaux; %[kg/m2] poids des panneaux horizontaux
h_coffbord=0.50; %hauteur du coffrage de bord [m]
n_coffbord=2; %nombre de coffrage de bord sur les bords long (aux appuis)
masselin_coffbord=h_coffbord*h_panneaux*n_coffbord*massevol_panneaux; %[kg/m] poids des panneaux de bord
n_uti_panneaux=20; %[n] nombre d'utilisation des panneaux de coffrage en bois
n_uti_chantier_panneaux=2; %nombre d'utilisation sur le chantier des panneaux

%poutrelles sous les panneaux
masseline_1poutrelle=4.7; %[kg/m] poids des poutrelles H20 doka
quantite_poutrelles=1/0.75+1/2.5; %[m/m2] quantité de poutrelles par m2 coffré --> A VERIFIER
massesurf_poutrelles=masseline_1poutrelle*quantite_poutrelles; %[kg/m2] poids des poutrelles par m2 coffré
n_uti_chantier_poutrelles=2; %nombre d'utilisation sur le chantier des poutrelles

%étais
poidsunit_etai=13; %[kg/étai]
portee_etai=2; %[m2/étai] surface d'influence sur un étai --> A VERIFIER
masse_lin_etais=poidsunit_etai/portee_etai; %[kg/m2]
n_uti_chantier_etais=1.5; %nombre d'utilisation sur le chantier des étais

%% données étayage pour le démontage avant REUSE (SYSTEM 1, 2A, 2B)
poidsunit_etai=13; %[kg/étai]
portee_etai_reuse=2; %[m2/étai] surface d'influence sur un étai
masse_lin_etais_reuse=poidsunit_etai/portee_etai_reuse; %[kg/m2]

%% schéma de sciage
largcamion=2.50; %largeur maximale de camion en Suisse selon l'art. 64-67 OCR

%% caractéristique NEW
tauxarmature_neuf=0.015; %taux d'armature dans béton neuf 1,5%

%% données LCA
%distances
tpdist_coffrageetayage=120; %distance de transport du matériel de coffrage et etayage [km] (pour deux trajets) --> DISTANCE A VERIFIER
tpdist_metal=60; %distance de transport des profilés métalliques [km] --> DISTANCE A VERIFIER
tpdist_beton=60; %distance de transport du béton [km] --> DISTANCE A VERIFIER
tpdist_arma=60; %distance de transport de l'acier d'armature [km] --> DISTANCE A VERIFIER

%calculs pour impact levage selon la GRAVITE
efficacitegrue=0.36; %efficacité de la grue
ener_levage1kg1m=9.8; %energie pour lever 1kg de 1m [J/m/kg]
energrue_levage1kg1m=ener_levage1kg1m/efficacitegrue; %energie utilisée par une grue pour lever 1 kg de 1m [J/m/kg]
hlevage=7; %hauteur moyenne de levage [m]
energrue_levage1kg=energrue_levage1kg1m*hlevage/1000000; %energie utilisée par une grue pour lever 1kg (inclut conversion de J à MJ) [MJ/kg]
kgco2_energiegrue=0.325; % kgco2/kwH Gasoil pour engin de chantier, sans FAP KBOB 61.001 -->> A CHANGER POUR MACHINE OPERATION (pour le moment, néglige l'usure de la grue)

%calculs pour impact sciage
surfsciable_1disque=40; %[m2] surface sciable par un disque
vitesse_sciage=40; %[m2/heure] vitesse de sciages
surfsciable_1machine=700; %[m2/machine] surface sciable par une machine
vol_1disque=0.001385442; %[m3/disque] volume d'un disque de 600 mm de diamètre et 4,9 mm d'épaisseur
kgco2_prodetelimi_acier=0.738; %[kgco2/kg] émissions pour la production et l'élimination d'un kg acier KBOB 06.012
kgco2_prodetelimi_disque=vol_1disque*massevol_metal*kgco2_prodetelimi_acier/surfsciable_1disque; %kgco2/m2 liée à l'usure du disque
kgco2_prod_machine=5.5; %[kgco2/kg] émissions pour la production de machines industrielles (ADEME)
masse_1machine=15; %[kg/machine]
facteur_elimi_machine=0.20; %coefficient pour includre l'élimination de la machine industrielle (selon obsrvation KBOB)
kgco2_prodetelimi_machine=masse_1machine*kgco2_prod_machine*(1+facteur_elimi_machine)/surfsciable_1machine; % kgco2/m2 lié à l'usure de la machine
kgco2_prodenergie_sciage=0.41; % kgco2/m2 lié à la consommation d'électricité pour la scie -> identique à Re:crete --> EVENTUELLEMENT A VERIFIER

%impacts carbone unitaires
kgco2_tp_camion3240t=0.118; % kgCO2/tkm pour tp pour camion 32-40t KBOB 62.010
kgco2_levage=energrue_levage1kg*kgco2_energiegrue; %kgCO2/kg de matériel lever à la hauteur de construction selon GRAVITE -> néglige l'usure de la grue
kgco2_prod_profilmetal=0.731; %kgCO2/kg de profilé métallique nu (production) KBOB 06.012
kgco2_prod_panneauxcoffrage=0.415; %kgCo2/kg Bois massif 3 et 5 plis KBOB 07.001
kgco2_prod_beton=0.0888; %kgCo2/kg béton non armé neuf (production) KBOB 01.002
kgco2_prod_armature=1.5*0.75; %kgco2/kg d'acier d'armature (production) KBOB 06.003 + facteur de corection KBOB 2022 KORR
kgco2_prod_revpulvacier=4.39; %kgCO2/m2 de revêtement pulverisé sur l'acier KBOB 14.006
kgco2_elimi_beton=0.0127; %kgco2/kg de béton éliminé KBOB 01.002
kgco2_elimi_armature=0.0124*0.75; %kgco2/kg d'acier d'armature éliminé KBOB 06.003 + facteur de corection KBOB 2022 KORR
kgco2_coulage_beton=1; %kgCo2/m3 de béton coulé OKOBAUDAT 9.1.02 (concrete pumping)
kgco2_sciage_beton=kgco2_prodetelimi_disque+kgco2_prodetelimi_machine+kgco2_prodenergie_sciage; % kgco2/m2 pour le sciage du beton
kgco2_elimi_profilmetal=0.00699; % kgco2/kg de profilé métallique nu (élimination) KBOB 06.012
kgco2_sandblasting=0.054055226; % kgco2/m2 de profilé métallique de réemploi à sabler E&Bpaper
kgco2_degraissage=0.0079018061; % kgco2/m2 de profilé métallique à dégraisser E&Bpaper
kgco2_welding=0.16264047; %kgco2/m de soudure sur métal E&Bpaper
kgco2_prod_mortier=0.393; %kgco2/kg  de Colle de construction/mortier d'enrobage minéral(e) KBOB 04.008
kgco2_prod_jointpoly=1.53; %kgco2/kg de joint en mousse polyéthylène KBOB 08.004
kgco2_prod_caoutchouc=2.74; %kgco2/kg de Lé d'étanchéité caoutchouc (EPDM)KBOB 09.004

%% loop

for i=1:13 %13 %tel que L0 (DONNEUR) compris entre 2 et 8
    L0=1.5+i/2;
    L_alpha=L0*alpha;
    for j=1:13 %j tel que L1 (RECEVEUR) compris entre 2 et 8
        L1=1.5+j/2;

            %% IMPACT NEW (SYSTEM 0)
            %quantité béton armé neuf
            if L1<4
                hsnew=0.18; %hauteur de la dalle neuve [m]
            elseif L1<6.5
                hsnew =0.20; %hauteur de la dalle neuve [m]
            else
                hsnew=0.22; %hauteur de la dalle neuve [m]
            end
            volbeton=L1*hsnew*(1-tauxarmature_neuf); %[m3/m]
            massebeton=volbeton*massevol_beton;%[kg/m]
            volarmature=L1*hsnew*tauxarmature_neuf;%[m3/m]
            massearmature=volarmature*massevol_armature; %[kg/m]

            %impact de la production des panneaux de coffrage (sur 20 usages)
            masse_panneaux=L1*massesurf_panneaux+masselin_coffbord; %[kg/m]
            impact_prod_coffr_new0=kgco2_prod_panneauxcoffrage*masse_panneaux/n_uti_panneaux; %[kgco2/m2]

            %impact du transport des matériaux d'étayage et de coffrage
            masse_poutrelles=L1*massesurf_poutrelles; %[kg/m] quantité de poutrelles sous étais
            masse_etais=L1*masse_lin_etais; %[kg/m] quantité d'étais
            impact_tp_coffrageetayage_new0=kgco2_tp_camion3240t*tpdist_coffrageetayage*(masse_panneaux/n_uti_chantier_panneaux+masse_poutrelles/n_uti_chantier_poutrelles+masse_etais/n_uti_chantier_etais)/1000; %[kgco2/m2]

            %impact du levage et de la dépose des matériaux d'étayage et de coffrage
            impact_levageetdepose_coffrageetetayage_new0=kgco2_levage*(masse_panneaux/n_uti_chantier_panneaux+masse_poutrelles/n_uti_chantier_poutrelles+masse_etais/n_uti_chantier_etais); %[kgco2/m]

            %impact de la production du béton
            impact_prod_betonneuf_new0=kgco2_prod_beton*massebeton; %[kgco2/m]

            %impact du transport du béton
            impact_tp_betonneuf_new0=kgco2_tp_camion3240t*massebeton/1000*tpdist_beton; %[kgco2/m]

            %impact de la production des armatures
            impact_prod_armaneuf_new0=kgco2_prod_armature*massearmature; %[kgco2/m]

            %impact du transport des armatures
            impact_tp_armaneuf_new0=kgco2_tp_camion3240t*tpdist_arma*massearmature/1000; %[kgco2/m]

            %impact du levage des armatures
            impact_levage_armaneuf_new0=kgco2_levage*massearmature; %[kgco2/m]

            %impact du levage du béton
            impact_levage_betonneuf_new0=kgco2_levage*massebeton; %[kgco2/m]

            %impact du coulage du béton
            impact_coulage_betonneuf_new0=kgco2_coulage_beton*volbeton; %[kgco2/m

            %impact new
            impactnew_prod=impact_prod_coffr_new0+impact_tp_coffrageetayage_new0+impact_levageetdepose_coffrageetetayage_new0+impact_prod_betonneuf_new0+impact_tp_betonneuf_new0+impact_prod_armaneuf_new0+impact_tp_armaneuf_new0+impact_levage_armaneuf_new0+impact_levage_betonneuf_new0+impact_coulage_betonneuf_new0; %[kgco2/m]


        %% IMPACT SYSTEM 1 - dalles simples uniquement (zones 1 et 3)
        if L1<=L_armamin && L1<=L0 || L1<=L_alpha && L1>L_armamin %conditions de la zone 1 et de la zone 3
%          if L1<=L_armamin && L1<=L0 || L1<=L_alpha %NOUVELLES conditions de la zone 1 et de la zone 3
            L_decoupeL0=L1;
            syst=0;
            Selection_beam_sol=0;

            %quantité béton armé de réemploi
            masselin_beton_reuse1=L1*hsreuse*massevol_BA; %masse BA dalle de réemploi par m [kg/m]

            %impact du transport des étais pour le donneur
            masse_etais_reuse1=masse_lin_etais_reuse*L1; %[kg/m] quantité étais pour découpe donneur par mètre linéaire receveur
            impact_tp_etai_reuse1=masse_etais_reuse1/1000*tpdist_coffrageetayage*kgco2_tp_camion3240t; %[kgco2/m]

            %impact du levage et de la dépose des étais pour le donneur
            impact_levageeetdepose_etais_reuse1=kgco2_levage*2*masse_etais_reuse1; %[kgco2/m]

            %impact du sciage du béton
            n_bloc_reuse1=1/largcamion; %nombre de bloc de béton par mètre linéaire [n/m]
            surfsciage_reuse1=((n_bloc_reuse1*L1)+1)*2*hsreuse; %surface de béton sciée par mètre linéaire [m2/m] --> ne prend pas en compte les économies possibles liées au fait que un trait de coupe puisse servir à deux blocs
            impact_sciage_betonreused_reuse1=kgco2_sciage_beton*surfsciage_reuse1; %[kgco2/m]

            %impact de la dépose du béton
            impact_depose_betonreused_reuse1=kgco2_levage*masselin_beton_reuse1; %[kgco2/m]

            %impact du transport du béton
            impact_tp_betonreused_reuse1=masselin_beton_reuse1/1000*tpdist_beton_reuse*kgco2_tp_camion3240t; %[kgco2/m]

            %impact de la production des cornières métalliques
            if hsreuse==0.14 %hauteur de la cornière = largeur de la cornière = hauteur de la dalle de réemploi
               epaisseurcorn=0.013; %épaisseur de la cornière selon la table des LNP (cornière la plus fine)
               hcorn=hsreuse;
            end
            if  hsreuse==0.16
               epaisseurcorn=0.015;
               hcorn=hsreuse;
            end
            if  hsreuse>=0.18
               epaisseurcorn=0.016;
               hcorn=hsreuse;
            end
            if  hsreuse==0.20
               epaisseurcorn=0.016;
               hcorn=hsreuse;
            end
            if  hsreuse==0.22
               epaisseurcorn=0.016;
               hcorn=0.20;
            end
            volcormetal=hcorn*2*epaisseurcorn; %volume linéaire par cornière [m3/m/corniere]
            n_cor=2;
            qcorniere=0.4; %longueur de cornière par mètre linéaire d'appui [m cornière /m] --> peut aussi être traité comme une variable
            voltotcormetal=volcormetal*n_cor*qcorniere; %volume linéaire de métal pour les cornirères [m3/m]
            massemetalcorn_reuse1=voltotcormetal*massevol_metal; %masse linéaire de métal pour les cornières [kg/m]
            impact_prod_metalneuf_corn_reuse1=massemetalcorn_reuse1*kgco2_prod_profilmetal; %[kgco2/m]

            %impact de la production des plaques métalliques
            vol_1plaque=0.25*0.15*0.008+3.14*0.008^2*hsreuse*4; %volume par plaque avec boulons [m3/plaque]
            n_plaque_reuse1=(2+ceil(L1/2))/largcamion; %nombre de plaque par mètre linéaire [plaque/m] (avec une plaque tous les 1,5 mètes min sur la longueur, et 2 plaques aux appuis de chaque plaque de chaque côté
            massemetalplaque_reuse1=vol_1plaque*n_plaque_reuse1*massevol_metal; %volume linéaire de métal pour les plaques [kg/m]
            impact_prod_metalneuf_plaque_reuse1=massemetalplaque_reuse1*kgco2_prod_profilmetal; %[kgco2/m]

            %impact du transport des cornières métalliques
            impact_tp_metalneuf_corn_reuse1=massemetalcorn_reuse1/1000*tpdist_metal*kgco2_tp_camion3240t; %[kgco2/m]

            %impact du transport des plaques métalliques
            impact_tp_metalneuf_plaque_reuse1=massemetalplaque_reuse1/1000*tpdist_metal*kgco2_tp_camion3240t; %[kgco2/m]

            %impact de la production de la peinture protectrice
            surfacepeintparcorn=hcorn; %surface à peindre par m de cornière [m2/m]
            surfacepeinttot_reuse1=surfacepeintparcorn*n_cor*qcorniere; %surface linéaire à peindre pour les cornières [m2/m]
            impact_prod_revpulvacier_reuse1=kgco2_prod_revpulvacier*surfacepeinttot_reuse1; %[kgco2/m

            %impact de la production du caoutchouc
            surfacecaoutchoucparcorn=hcorn; %surface à peindre par m de cornière = surface à doubler par caoutchouc par m de cornière [m2/m]
            volumecaoutchouctot_reuse1=surfacecaoutchoucparcorn*epaisseur_caoutchouc*n_cor*qcorniere; %volume de caoutchouc pour doubler les cornières [m3/m]
            impact_prod_caoutchouc_reuse1=massevol_caoutchouc*volumecaoutchouctot_reuse1*kgco2_prod_caoutchouc; %impact de la production du caoutchouc [kgco2/m]

            %impact du dégraissage de l'acier
            impact_degraissage_metalneuf_reuse1=kgco2_degraissage*surfacepeinttot_reuse1; %[kgco2/m]

            %impact du levage des cornières métalliques
            impact_levage_metalneuf_corn_reuse1=kgco2_levage*massemetalcorn_reuse1; %[kgco2/m]

            %impact du levage des plaques métalliques
            impact_levage_metalneuf_plaque_reuse1=kgco2_levage*massemetalplaque_reuse1; %[kgco2/m]

            %impact du levage  du béton
            impact_levage_betonreused_reuse1=kgco2_levage*masselin_beton_reuse1; %[kgco2/m]

            %impact du joint
            volumejointpoly=0.02*0.02*L1/largcamion; %[m3/m]
            impact_prod_jointpolyneuf_reuse1=kgco2_prod_jointpoly*massevol_jointpoly*volumejointpoly; %[kgco2/m]

            %impact du mortier dans les joints entre les pieces de beton
            volumemortier=(hsreuse-0.03)*0.02*L1/largcamion; %[m3/m]
            impact_prod_mortierneuf_reuse1=volumemortier*massevol_mortier*kgco2_prod_mortier; %[kgco2/m]

            %impact EVITE de l'élimination du béton réutilisé
            impact_EVITE_elimi_betonreused_reuse1=kgco2_elimi_beton*masselin_beton_reuse1; %[kgco2/m]

            %impact EVITE de l'élimination de l'acier d'armature réutilisé
            volarma0=L1*hsreuse*tauxarmature0; %volume des armatures réutilisées  [m3/m]
            massearma0=massevol_armature*volarma0; %masse des armatures réutilisées [m3/m]
            impact_EVITE_elimi_armareused_reuse1=kgco2_elimi_armature*massearma0; %[kgco2/m]

            %impact réemploi
            impactreuse1=impact_tp_etai_reuse1+impact_levageeetdepose_etais_reuse1+impact_sciage_betonreused_reuse1+impact_depose_betonreused_reuse1+impact_tp_betonreused_reuse1+impact_levage_betonreused_reuse1+impact_prod_metalneuf_corn_reuse1+impact_prod_metalneuf_plaque_reuse1+impact_tp_metalneuf_corn_reuse1+impact_tp_metalneuf_plaque_reuse1+impact_degraissage_metalneuf_reuse1+impact_prod_revpulvacier_reuse1+impact_levage_metalneuf_plaque_reuse1+impact_levage_metalneuf_corn_reuse1+impact_prod_jointpolyneuf_reuse1++impact_prod_caoutchouc_reuse1+impact_prod_mortierneuf_reuse1; %impact solution réemploi dalles simples [kgco2/m]

            %distribution des impacts (réemploi et new)
            impactreuse1_matrice=[impact_tp_etai_reuse1+impact_levageeetdepose_etais_reuse1+impact_depose_betonreused_reuse1+impact_levage_betonreused_reuse1+impact_tp_metalneuf_corn_reuse1+impact_tp_metalneuf_plaque_reuse1+impact_degraissage_metalneuf_reuse1+impact_levage_metalneuf_plaque_reuse1+impact_levage_metalneuf_corn_reuse1,impact_prod_revpulvacier_reuse1,impact_prod_jointpolyneuf_reuse1,+impact_prod_caoutchouc_reuse1,impact_prod_mortierneuf_reuse1,0,impact_prod_metalneuf_corn_reuse1,impact_prod_metalneuf_plaque_reuse1,0,0,0,impact_sciage_betonreused_reuse1,impact_tp_betonreused_reuse1,0];
            impactnew1_matrice=[impact_tp_armaneuf_new0+impact_levage_armaneuf_new0+impact_levage_betonneuf_new0+impact_coulage_betonneuf_new0+impact_prod_coffr_new0+impact_tp_coffrageetayage_new0+impact_levageetdepose_coffrageetetayage_new0+impact_EVITE_elimi_armareused_reuse1,0,0,0,0,impact_prod_armaneuf_new0,0,0,0,impact_prod_betonneuf_new0,impact_tp_betonneuf_new0,0,0,impact_EVITE_elimi_betonreused_reuse1,];
            impactreuse=impactreuse1;
            impactreuse_m2(i,j)=impactreuse/L1;
            %impact neuf
            impactnew=impactnew_prod+impact_EVITE_elimi_betonreused_reuse1+impact_EVITE_elimi_armareused_reuse1;
            impactnew_m2(i,j)=impactnew/L1;
            %% DELTA NEW/REUSE
            delta(i,j)=(impactnew-impactreuse)/impactnew;
            delta1(i,j)=(impactnew-impactreuse1)/impactnew;
            delta2(i,j)=0;



%             x1=[-impact_EVITE_elimi_betonreused_reuse1 -impact_EVITE_elimi_armareused_reuse1 impact_tp_etai_reuse1 impact_levageeetdepose_etais_reuse1 impact_sciage_betonreused_reuse1 impact_depose_betonreused_reuse1 impact_tp_betonreused_reuse1 impact_levage_betonreused_reuse1 impact_prod_metalneuf_corn_reuse1 impact_prod_metalneuf_plaque_reuse1 impact_tp_metalneuf_corn_reuse1 impact_tp_metalneuf_plaque_reuse1 impact_degraissage_metalneuf_reuse1 impact_prod_revpulvacier_reuse1 impact_levage_metalneuf_plaque_reuse1 impact_levage_metalneuf_corn_reuse1 impact_prod_jointpolyneuf_reuse1 impact_prod_mortierneuf_reuse1;impact_prod_coffr_new0 impact_tp_coffrageetayage_new0 impact_levageetdepose_coffrageetetayage_new0 impact_prod_betonneuf_new0 impact_tp_betonneuf_new0 impact_prod_armaneuf_new0 impact_tp_armaneuf_new0 impact_levage_armaneuf_new0 impact_levage_betonneuf_new0 impact_coulage_betonneuf_new0 0 0 0 0 0 0 0 0];
%             bar(x1,'stacked')
        else
        %% IMPACT SYSTEM 2 - grille de poutres avec dalles simples (zones 2,4,5)
            if L0<=L_armamin && L1>L0 %conditions de la zone 2
               L_decoupeL0=L0;
            elseif L1>L0 && L0>L_armamin || L1<=L0 && L1>L_alpha && L1>L_armamin %conditions de la zone 4 et de la zone 5
               L_decoupeL0=max(L_alpha,L_armamin);
            end
            if beamposition==1 %belowconcrete
            syst=1;
            end
%             if beamposition==2 %concreteplane
%             syst=2;
%             end
            %charge sur la cornière
            Qlin=L_decoupeL0*Qtotsurfacique1*beam_selfweight; %[kN/m]

            %% SELECTION PROFILE - SELECTIONS CARACT. A COMPLETER
            Med=Qlin*L1^2/8;%Nmm
            ind=find(profile_MRd>Med);
            Selection_I=profile_I(min(ind));
            Selection_beam_largeurentrepiece=beam_largeurentrepiece(min(ind));

            test=0;
            it=0;
            flechemax_freq=L1*1000/350; %mm
            flechemax_perm=L1*1000/300; %mm
            sel=min(ind);
            while test<2
                test=0;
                flecheBeam_freq=(L_decoupeL0+Selection_beam_largeurentrepiece/1000)*Q1*(L1*1000)^4/profileE/(Selection_I)*5/384; %mm
                flecheBeton_freq=Q1*(L_decoupeL0*1000)^4/Ebeton/Ibeton*5/384; %mm
                flechetot_freq=flecheBeam_freq+flecheBeton_freq;
                if flechetot_freq<=flechemax_freq
                    test=test+1;
                else
                    it=it+1;
                    sel=min(ind)+it;
                    Selection_I=profile_I(sel);
                    Selection_beam_largeurentrepiece=beam_largeurentrepiece(sel);
                end
                if steelprofile_type==2 %reusedsteel
                    flecheBeam_perm_reuse=(L_decoupeL0+Selection_beam_largeurentrepiece/1000)*(Gslab0+Grev1+Psi_1*Q1)*(L1*1000)^4/profileE/(Selection_I)*5/384; %mm
                    flecheBeton_perm=(Gslab0+Grev1+Psi_1*Q1)*(L_decoupeL0*1000)^4/Ebeton/Ibeton*5/384; %mm
                    flechetot_perm_reuse=flecheBeam_perm_reuse+flecheBeton_perm;
                    if flechetot_perm_reuse<=flechemax_perm
                        test=test+1;
                    else
                        it=it+1;
                        sel=min(ind)+it;
                        Selection_I=profile_I(sel);
                        Selection_beam_largeurentrepiece=beam_largeurentrepiece(sel);
                    end
                else
                    test=test+1;
                end
            end

            Selection_W=profile_W(sel);
            Selection_I=profile_I(sel);
            Selection_profile_mass=profile_mass(sel);
            Selection_profile_hauteur=profile_hauteur(sel);
            Selection_profile_largeurtot=profile_largeurtot(sel);
            Selection_profile_degreasedsurf=profile_degreasedsurf(sel);
            Selection_beam_sol=beam_sol(sel);
            Selection_beam_welding=beam_welding(sel);
            Selection_supportingplates_mass=supportingplates_mass(sel);
            Selection_profile_unwelding=profile_unwelding(sel);
            Selection_profile_sandblastedsurf=profile_sandblastedsurf(sel);
            Selection_beam_largeurentrepiece=beam_largeurentrepiece(sel);
            Selection_beam_vol_betonremplissage=beam_vol_betonremplissage(sel);
            Selection_beam_caoutchoucwidth=beam_caoutchoucwidth(sel);

            sol(i,j)=Selection_beam_sol;

            %% IMPACTS COMMUN A TOUS LES SYSTEMES 2
            %ratio dalle:poutre
            if beamposition==1 %belowconcrete
               qdalle=1;
            end
            if beamposition==2 %concrete plane
               qdalle=1/(L_decoupeL0+Selection_beam_largeurentrepiece/1000)*L_decoupeL0;
            end

            %quantité de métal pour les plaques métalliques
            vol_1plaque=0.2*0.15*0.01+3.14*0.008^2*hsreuse*4; %volume par plaque avec boulons [m3/plaque]
            n_plaque_reuse2=(2*ceil(L1/largcamion)+ceil(L_decoupeL0/1.5))/L_decoupeL0*qdalle; %nombre de plaque par mètre linéaire [plaque/m]
            massemetalplaque_reuse2=vol_1plaque*n_plaque_reuse2*massevol_metal; %masse linéaire de métal pour les plaques [kg/m]

            %surface de béton sciée
            n_bloc_reuse2=ceil(L1/largcamion); %nombre de blocs nécessaires pour couvrir L1
            surfsciage_reuse2=(L1/L_decoupeL0*2+(n_bloc_reuse2*2))*hsreuse*qdalle; %surface de béton sciée par mètre linéaire [m2/m]  --> ne prend pas en compte les économies possibles liées au fait que un trait de coupe puisse servir à deux blocs

            %impact du transport des étais pour le donneur
            masse_etais_reuse2=masse_lin_etais_reuse*L1*qdalle; %quantité étais pour découpe donneur par mètre linéaire receveur
            impact_tp_etais_reuse2=masse_etais_reuse2/1000*tpdist_coffrageetayage*kgco2_tp_camion3240t; %[kgco2/m]

            %impact du levage et de la dépose des étais
            impact_levageetdepose_etais_reuse2=kgco2_levage*masse_etais_reuse2; %[kgco2/m]

            %impact du sciage du béton
            impact_sciage_betonreused_reuse2=kgco2_sciage_beton*surfsciage_reuse2; %[kgco2/m]

            %impact du joint entre les pièces de béton
            volumejointpoly2=0.02*0.02*n_bloc_reuse2; %[m3/m]
            impact_prod_jointpolyneuf_reuse2=kgco2_prod_jointpoly*massevol_jointpoly*volumejointpoly2*qdalle; %[kgco2/m]

            %impact du mortier dans les joints entre les pieces de beton
            volumemortier2=(hsreuse-0.03)*0.02*n_bloc_reuse2; %[m3/m]
            impact_prod_mortierneuf_reuse2=volumemortier2*massevol_mortier*kgco2_prod_mortier*qdalle; %[kgco2/m]

            %quantité de métal pour les poutres
            qpoutreparmlin=1/(L_decoupeL0+(Selection_beam_largeurentrepiece/1000)); %nombre moyen de poutre par mètre (de large) de plancher
            masselin_poutre=qpoutreparmlin*Selection_profile_mass*100*L1; %masse de métal moyenne par mètre linéaire de plancher [kg/m] !! ATTENTION A LA CONVERSION

            %quantité de béton de réemploi
            lbetonparmlin=1-((Selection_beam_largeurentrepiece/1000)*qpoutreparmlin); %longueur de béton par m linéaire [m/m] A VERIFIER
            masselin_beton_reuse2=L1*hsreuse*lbetonparmlin*massevol_BA; %masse BA dalle de réemploi par m [kg/m]

            %impact pour la dépose au sol (//levage) du béton scié
            impact_depose_betonreused_reuse2=kgco2_levage*masselin_beton_reuse2; %[kgco2/m]

            %impact du transport du béton
            impact_tp_betonreused_reuse2= masselin_beton_reuse2/1000*tpdist_beton_reuse*kgco2_tp_camion3240t; %[kgco2/m]

            %impact du levage du béton
            impact_levage_betonreused_reuse2=kgco2_levage*masselin_beton_reuse2; %[kgco2/m]

            %quantité de métal pour les cornières pour appuyer les poutres A CORRIGER
            masse_corn2=masse_lin_corn2*Selection_profile_largeurtot/1000*2*qpoutreparmlin; %[kg/m]

            %impact de la production des cornièces métalliques
            impact_prod_metalneuf_corn_reuse2=masse_corn2*kgco2_prod_profilmetal;

            %impact de la production des plaques métalliques
            impact_prod_metalneuf_plaque_reuse2=massemetalplaque_reuse2*kgco2_prod_profilmetal;

            %impact du transport des plaques métalliques
            impact_tp_metalneuf_plaque_reuse2=massemetalplaque_reuse2/1000*tpdist_metal*kgco2_tp_camion3240t;

            %impact du transport des cornières métalliques
            impact_tp_metalneuf_corn_reuse2=masse_corn2/1000*tpdist_metal*kgco2_tp_camion3240t;

            %impact des soudures sur l'acier
            impact_welding_reuse2=Selection_beam_welding*L1*qpoutreparmlin*kgco2_welding;

            %impact du dégraissage de l'acier
            surface_peint_1beam=Selection_profile_degreasedsurf; %FAcTEUR 1/1000 enlevé!
            surfacepeinttot_reuse2=surface_peint_1beam*qpoutreparmlin*L1; %surface à protéger avec peinture ignifuge par mètre linéaire de plancher[m2/m]
            impact_degraissage_metalneuf_reuse2=kgco2_degraissage*surfacepeinttot_reuse2;

            %impact de la production de la peinture protectrice
            impact_prod_revpulvacier_reuse2=kgco2_prod_revpulvacier*surfacepeinttot_reuse2;

            %impact de la production du caoutchouc
            volumecaoutchouctot_reuse2=Selection_beam_caoutchoucwidth/1000*L1*qpoutreparmlin*epaisseur_caoutchouc; %volume de caoutchouc par mètre lin de plancher [m3/m]
            impact_prod_caoutchouc_reuse2=massevol_caoutchouc*volumecaoutchouctot_reuse2*kgco2_prod_caoutchouc; %impact de la production du caoutchouc [kgco2/m]

            %impact du levage de les cornières métalliques
            impact_levage_metalneuf_corn_reuse2=kgco2_levage*masse_corn2; %[kgco2/m]

            %impact du levage des plaques métalliques
            impact_levage_metalneuf_plaque_reuse2=kgco2_levage*massemetalplaque_reuse2; %[kgco2/m]

            %impact EVITE de l'élimination du béton réutilisé
            impact_EVITE_elimi_betonreused_reuse2=kgco2_elimi_beton*masselin_beton_reuse2; %[kgco2/m]

            %impact EVITE de l'élimination de l'acier d'armature réutilisé !!! A CORRIGER !!!
            volarma0=L1*hsreuse*lbetonparmlin*tauxarmature0; %volume des armatures réutilisées [m3/m]
            massearma0=massevol_armature*volarma0; %masse des armatures réutilisées [m3/m]
            impact_EVITE_elimi_armareused_reuse2=kgco2_elimi_armature*massearma0; %[kgco2/m]

            %% IMPACTS SPECIAUX POUR SYSTEMES 2 AVEC PROFILES NEUFS
            if steelprofile_type==1 %recycledsteel
                %impact de la production des profilés métalliques
                impact_prod_metalneuf_profiles_reuse2=masselin_poutre*kgco2_prod_profilmetal;

                %impact du transport des profilés métalliques
                impact_tp_metalneuf_profiles_reuse2=masselin_poutre/1000*tpdist_metal*kgco2_tp_camion3240t;

                %impact du levage des profillés métalliques
                impact_levage_metalneuf_profiles_reuse2=kgco2_levage*masselin_poutre; %[kgco2/m]
            end
            if steelprofile_type==2 %reusedsteel
                impact_prod_metalneuf_profiles_reuse2=0;
                impact_tp_metalneuf_profiles_reuse2=0;
                impact_levage_metalneuf_profiles_reuse2=0;
            end

            %% IMPACTS SPECIAUX POUR SYSTEMES 2 AVEC PROFILES REEMPLOI
            if steelprofile_type==1 %recycledsteel
                impact_unwelding_metalreuse_reuse2=0;
                impact_depose_metalreused_reuse2=0;
                impact_sablage_metalreused_reuse2=0;
                impact_tp_metalreused_reuse2=0;
                impact_EVITE_elimi_metalreused_reuse2=0;
            end
            if steelprofile_type==2 %reusedsteel
                %impact de l'ouverture/unwelding connections sur le donneur
                impact_unwelding_metalreuse_reuse2=Selection_profile_unwelding*qpoutreparmlin*kgco2_welding; %[kgco2/m]

                %impact de la dépose des profilés de réemploi
                impact_depose_metalreused_reuse2=kgco2_levage*masselin_poutre; %[kgco2/m]

                %impact du sablage des profilés
                impact_sablage_metalreused_reuse2=Selection_profile_sandblastedsurf*L1*qpoutreparmlin*kgco2_sandblasting; %[kgco2/m]

                %impact du transport des profilés de réemploi
                impact_tp_metalreused_reuse2=masselin_poutre/1000*tpdist_metal_reuse*kgco2_tp_camion3240t; %[kgco2/m]

                %impact EVITE de l'élimination des profilés métalliques réutilisés
                impact_EVITE_elimi_metalreused_reuse2=masselin_poutre*kgco2_elimi_profilmetal; %[kgco2/m
            end

            %%  IMPACTS SPECIAUX POUR SYSTEMS 2 AVEC PROFILES DANS LE PLAN DU BETON -> RAJOUTER LA PROD ET LE TP DU BETON DANS LES PROFILES!
            if beamposition==1 %belowconcrete
                impact_prod_betonnew_reuse2=0;
                impact_tp_betonnew_reuse2=0;
            end
            if beamposition==2 %concreteplan
                if Selection_profile_hauteur/1000<=hsreuse
                    masse_betonremplissage_complement=hsreuse-Selection_profile_hauteur/1000*Selection_profile_largeurtot/1000;
                end
                if Selection_profile_hauteur/1000>hsreuse
                    masse_betonremplissage_complement=(Selection_profile_hauteur/1000-hsreuse)*0.2;
                end
                masse_betonremplissage_tot=(Selection_beam_vol_betonremplissage+masse_betonremplissage_complement)*qpoutreparmlin*massevol_beton*L1; %[m3/m de poutre]*[kg/m3]*[qpoutre/m]
                impact_prod_betonnew_reuse2=masse_betonremplissage_tot*kgco2_prod_beton;
                impact_tp_betonnew_reuse2=masse_betonremplissage_tot/1000*kgco2_tp_camion3240t*tpdist_beton;
            end

            %impact réemploi
            impactreuse2=impact_tp_etais_reuse2+impact_levageetdepose_etais_reuse2+impact_sciage_betonreused_reuse2+impact_depose_betonreused_reuse2+impact_tp_betonreused_reuse2+impact_levage_betonreused_reuse2+impact_prod_jointpolyneuf_reuse2+impact_prod_caoutchouc_reuse2+impact_prod_mortierneuf_reuse2+impact_prod_metalneuf_corn_reuse2+impact_prod_metalneuf_plaque_reuse2+impact_tp_metalneuf_plaque_reuse2+impact_tp_metalneuf_corn_reuse2+impact_levage_metalneuf_corn_reuse2+impact_levage_metalneuf_plaque_reuse2+impact_welding_reuse2+impact_degraissage_metalneuf_reuse2+impact_prod_revpulvacier_reuse2+impact_prod_metalneuf_profiles_reuse2+impact_tp_metalneuf_profiles_reuse2+impact_levage_metalneuf_profiles_reuse2+impact_unwelding_metalreuse_reuse2+impact_depose_metalreused_reuse2+impact_tp_metalreused_reuse2+impact_sablage_metalreused_reuse2+impact_prod_betonnew_reuse2+impact_tp_betonnew_reuse2;
            impactreuse=impactreuse2;
            impactreuse_m2(i,j)=impactreuse/L1;

            %impact neuf
            impactnew=impactnew_prod+impact_EVITE_elimi_betonreused_reuse2+impact_EVITE_elimi_armareused_reuse2+impact_EVITE_elimi_metalreused_reuse2;
            impactnew_m2(i,j)=impactnew/L1;
            %distribution des impacts (réemploi et new)
            impactreuse2_matrice=[impact_tp_etais_reuse2+impact_levageetdepose_etais_reuse2+impact_depose_betonreused_reuse2+impact_levage_betonreused_reuse2+impact_tp_metalneuf_plaque_reuse2+impact_tp_metalneuf_corn_reuse2+impact_levage_metalneuf_corn_reuse2+impact_levage_metalneuf_plaque_reuse2+impact_welding_reuse2+impact_degraissage_metalneuf_reuse2+impact_tp_metalneuf_profiles_reuse2+impact_levage_metalneuf_profiles_reuse2+impact_unwelding_metalreuse_reuse2+impact_depose_metalreused_reuse2+impact_tp_metalreused_reuse2+impact_sablage_metalreused_reuse2+impact_prod_betonnew_reuse2+impact_tp_betonnew_reuse2,impact_prod_revpulvacier_reuse2,impact_prod_jointpolyneuf_reuse2,impact_prod_caoutchouc_reuse2, impact_prod_mortierneuf_reuse2,0,impact_prod_metalneuf_corn_reuse2,impact_prod_metalneuf_plaque_reuse2,impact_prod_metalneuf_profiles_reuse2,0,0,impact_sciage_betonreused_reuse2,impact_tp_betonreused_reuse2,0];
            impactnew2_matrice=[impact_EVITE_elimi_armareused_reuse2+impact_EVITE_elimi_metalreused_reuse2+impact_prod_coffr_new0+impact_tp_coffrageetayage_new0+impact_levageetdepose_coffrageetetayage_new0+impact_tp_armaneuf_new0+impact_levage_armaneuf_new0+impact_levage_betonneuf_new0+impact_coulage_betonneuf_new0,0,0,0,0,impact_prod_armaneuf_new0,0,0,0,impact_prod_betonneuf_new0,impact_tp_betonneuf_new0,0,0,impact_EVITE_elimi_betonreused_reuse2];
            %% DELTA NEW/REUSE
            delta(i,j)=(impactnew-impactreuse)/impactnew;
            delta1(i,j)=0;
            delta2(i,j)=(impactnew-impactreuse2)/impactnew;


             %% SELECTED SOLUTIONS
            sol(i,j)=Selection_beam_sol;
        end
        Select_syst(i,j)=syst;
        Select_alpha(i,j)=1/L0*L_decoupeL0;
        Select_sol(i,j)=Selection_beam_sol;
        Para_L0(i,j)=L0;
        Para_L1(i,j)=L1;
        Para_hsreuse(i,j)=hsreuse;
        Para_year(i,j)=year;
        Para_steelprofile_type(i,j)=steelprofile_type;
        Para_beamposition(i,j)=beamposition;
        Para_Q0(i,j)=Q0;
        Para_Q1(i,j)=Q1;
        Para_tpdist_beton_reuse(i,j)=tpdist_beton_reuse;
        Para_tpdist_metal_reuse(i,j)=tpdist_metal_reuse;


    end

%     y=[impactnew;impactreuse];
%     bar(y,'stacked')
%
%     x2=[-impact_EVITE_elimi_betonreused_reuse2 -impact_EVITE_elimi_armareused_reuse2 -impact_EVITE_elimi_metalreused_reuse2 impact_tp_etais_reuse2 impact_levageetdepose_etais_reuse2 impact_sciage_betonreused_reuse2 impact_depose_betonreused_reuse2 impact_tp_betonreused_reuse2 impact_levage_betonreused_reuse2 impact_prod_jointpolyneuf_reuse2 impact_prod_mortierneuf_reuse2 impact_prod_metalneuf_corn_reuse2 impact_prod_metalneuf_plaque_reuse2 impact_tp_metalneuf_plaque_reuse2 impact_tp_metalneuf_corn_reuse2 impact_levage_metalneuf_corn_reuse2 impact_levage_metalneuf_plaque_reuse2 impact_welding_reuse2 impact_degraissage_metalneuf_reuse2 impact_prod_revpulvacier_reuse2 impact_prod_metalneuf_profiles_reuse2 impact_tp_metalneuf_profiles_reuse2 impact_levage_metalneuf_profiles_reuse2 impact_unwelding_metalreuse_reuse2 impact_depose_metalreused_reuse2 impact_tp_metalreused_reuse2 impact_sablage_metalreused_reuse2 impact_prod_betonnew_reuse2 impact_tp_betonnew_reuse2;impact_prod_coffr_new0 impact_tp_coffrageetayage_new0 impact_levageetdepose_coffrageetetayage_new0 impact_prod_betonneuf_new0 impact_tp_betonneuf_new0 impact_prod_armaneuf_new0 impact_tp_armaneuf_new0 impact_levage_armaneuf_new0 impact_levage_betonneuf_new0 impact_coulage_betonneuf_new0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0];
%     bar(x2,'stacked')
end

% end
