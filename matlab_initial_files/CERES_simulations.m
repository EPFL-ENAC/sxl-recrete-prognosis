% Trigger fun_CERES
clear all
clc 

delta_save=[];
delta1_save=[];
delta2_save=[];
alpha_save=[];
Select_alpha_save=[];
Select_syst_save=[];
Select_sol_save=[];
Para_save=[];
Para_L0_save=[];
Para_L1_save=[];
Para_hsreuse_save=[];
Para_year_save=[];
Para_steelprofile_type_save=[];
Para_beamposition_save=[];
Para_Q0_save=[];
Para_Q1_save=[];
Para_tpdist_beton_reuse_save=[];
Para_tpdist_metal_reuse_save=[];
impactreuse_m2_save=[];
impactnew_m2_save=[];

for hsreuse=0.14:0.02:0.22 %épaisseur de la dalle de réemploi [m] --> VARIABLE
for year=1:1:3 % year=2; %1=depuis 1989; 2=entre 1968 et 1988 ; 3=entre 1956 et 1967 --> VARIABLE
for steelprofile_type=1:2  %type acier: newsteel=1; reusedsteel=2; --> VARIABLE
for beamposition=1 %scénario receveur: ; belowconcrete=1; concreteplane=2 --> VARIABLE
for Q0=2:3 %charge utiles donneur [kN/m2] --> VARIABLE
for Q1=2:3 %charge utiles recevru [kN/m2] --> VARIABLE
for tpdist_beton_reuse=100 %0:100:100 %0:100:100 %100 %distance de tranport béton de réemploi  --> VARIABLE
for tpdist_metal_reuse=100 %0:100:100 %100 %distance de transport acier de réemploi --> VARIABLE
    
Para_save=[Para_save; hsreuse,year, steelprofile_type, beamposition, Q0, Q1, tpdist_beton_reuse, tpdist_metal_reuse];

[delta,delta1, delta2,alpha,Select_alpha,Select_syst,Select_sol,Para_L0,Para_L1,Para_hsreuse,Para_year,Para_steelprofile_type,Para_beamposition,Para_Q0,Para_Q1,Para_tpdist_beton_reuse,Para_tpdist_metal_reuse,impactreuse_m2,impactnew_m2]=fun_CERES(hsreuse, year,steelprofile_type,beamposition,Q0,Q1,tpdist_beton_reuse,tpdist_metal_reuse);
clear fun_CERES

delta_save=[delta_save; delta];
delta1_save=[delta1_save; delta1];
delta2_save=[delta2_save; delta2];
alpha_save=[alpha_save; alpha];
Select_alpha_save=[Select_alpha_save; Select_alpha];
Select_syst_save=[Select_syst_save; Select_syst];
Select_sol_save=[Select_sol_save; Select_sol];
Para_L1_save=[Para_L1_save; Para_L1];
Para_L0_save=[Para_L0_save; Para_L0];
Para_hsreuse_save=[Para_hsreuse_save; Para_hsreuse];
Para_year_save=[Para_year_save;Para_year];
Para_steelprofile_type_save=[Para_steelprofile_type_save; Para_steelprofile_type];
Para_beamposition_save=[Para_beamposition_save; Para_beamposition];
Para_Q0_save=[Para_Q0_save;Para_Q0];
Para_Q1_save=[Para_Q1_save;Para_Q1];
Para_tpdist_beton_reuse_save=[Para_tpdist_beton_reuse_save; Para_tpdist_beton_reuse];
Para_tpdist_metal_reuse_save=[Para_tpdist_metal_reuse_save; Para_tpdist_metal_reuse];
impactreuse_m2_save=[impactreuse_m2_save;impactreuse_m2];
impactnew_m2_save=[impactnew_m2_save;impactnew_m2];

titles = [num2str(cell2mat({'hsreuse = '})),num2str(hsreuse)];
dlmwrite('results.csv',titles,'-append','delimiter',' ','roffset',0)
titles = [num2str(cell2mat({'year = '})),num2str(year)];
dlmwrite('results.csv',titles,'-append','delimiter',' ','roffset',0)
titles = [num2str(cell2mat({'steelprofile_type = '})),num2str(steelprofile_type)];
dlmwrite('results.csv',titles,'-append','delimiter',' ','roffset',0)
titles = [num2str(cell2mat({'beamposition = '})),num2str(beamposition)];
dlmwrite('results.csv',titles,'-append','delimiter',' ','roffset',0)
titles = [num2str(cell2mat({'Q0= '})),num2str(Q0)];
dlmwrite('results.csv',titles,'-append','delimiter',' ','roffset',0)
titles = [num2str(cell2mat({'Q1 = '})),num2str(Q1)];
dlmwrite('results.csv',titles,'-append','delimiter',' ','roffset',0)
titles = [num2str(cell2mat({'tpdist_beton_reuse = '})),num2str(tpdist_beton_reuse)];
dlmwrite('results.csv',titles,'-append','delimiter',' ','roffset',0)
titles = [num2str(cell2mat({'tpdist_metal_reuse = '})),num2str(tpdist_metal_reuse)];
dlmwrite('results.csv',titles,'-append','delimiter',' ','roffset',0)
% titles = [num2str(cell2mat({'delta = '}))];
% dlmwrite('results.csv',titles,'-append','delimiter',' ','roffset',0)
% Continue adding data
dlmwrite('results.csv',delta,'delimiter',',','-append','roffset',-4,'coffset',1);
end 
end
end
end
end
end
end
end

D_mean=mean(mean(delta_save))
D_min=min(min(delta_save))
D_max=max(max(delta_save))
D_median=median(median(delta_save))
mean(impactreuse_m2_save);

AX=[2 2.5 3 3.5 4 4.5 5 5.5 6 6.5 7 7.5 8]