#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Jun  9 15:35:11 2020

@author: yuezhang
"""

import pandas as pd

#read summary files output in previous steps
rpllen_file = "approach_rpllen/sample_reversed_extending_force_distance_curve_data_rpllen.txt"
ruplen_file = "retract_ruplen/sample_reversed_retract_data_force_distance_curve_data_ruplen_version1.txt"
rpleng_file = "approach_rpleng/sample_reversed_extending_force_distance_curve_data_rpl_eng.txt"
adheng_file = "retract_adheng/sample_reversed_retract_data_force_distance_curve_data_adh_eng.txt"
indlen_file = "sample_reversed_retract_data_adhforce_indlen_summary.txt"

df_rpllen = pd.read_csv(rpllen_file,'\t')
df_rpllen.rename(columns={'Baseline_y_std_nN':'Baseline_y_std_nN_repulsive_length'},inplace = True) #the standard deviation of baseline y-values of the force distance curves that used for determining repulsive length

df_ruplen = pd.read_csv(ruplen_file,'\t')
df_ruplen.rename(columns={'Baseline_y_std_nN':'Baseline_y_std_nN_rupture_length'},inplace = True) #the standard deviation of baseline y-values of the force distance curves that used for determining rupture length

df_rpleng = pd.read_csv(rpleng_file,'\t')
df_adheng = pd.read_csv(adheng_file,'\t')
df_indlen = pd.read_csv(indlen_file,'\t')

#remove the prefix and suffix to make all dataframes have a common column named Sample_Name，
#here i use two steps to 1)separate prefix and suffix first and 2)delete them, in order to make
#it clear to see what prefix or suffix that the program automatically appended onto the sample name
 
df_rpllen[['prefix','Sample_Name']] = df_rpllen.Sample_Name.str.split("READSTART",expand = True)
df_rpllen[['Sample_Name','suffix']] = df_rpllen.Sample_Name.str.split(".out.",expand = True)


df_ruplen[['prefix','Sample_Name']] = df_ruplen.Sample_Name.str.split("READSTART",expand = True)
df_ruplen[['Sample_Name','suffix']] = df_ruplen.Sample_Name.str.split(".out.",expand = True)

df_rpleng[['prefix','Sample_Name']] = df_rpleng.Sample_Name.str.split("READSTART",expand = True)
df_rpleng[['Sample_Name','suffix']] = df_rpleng.Sample_Name.str.split(".out.",expand = True)

df_adheng[['prefix','Sample_Name']] = df_adheng.Sample_Name.str.split("READSTART",expand = True)
df_adheng[['Sample_Name','suffix']] = df_adheng.Sample_Name.str.split(".out.",expand = True)

df_indlen[['Sample_Name','suffix']] = df_indlen.Sample_Name.str.split(".out",expand = True)

del df_rpllen['prefix'],df_rpllen['suffix']
del df_ruplen['prefix'],df_ruplen['suffix']
del df_rpleng['prefix'],df_rpleng['suffix']
del df_adheng['prefix'],df_adheng['suffix']
del df_indlen['suffix']
#merge all dataframes

df_all = pd.merge(df_rpllen, df_ruplen, on='Sample_Name', how='outer')
df_all = pd.merge(df_rpleng, df_all, on='Sample_Name', how='outer')
df_all = pd.merge(df_adheng, df_all, on='Sample_Name', how='outer')
df_all = pd.merge(df_indlen, df_all, on='Sample_Name', how='outer')

df_all.to_csv("combined_summary.txt",sep="\t")