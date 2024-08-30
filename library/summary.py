# -*- coding: utf-8 -*-
"""
Created on Tue Jun  9 15:35:11 2020

@author: yuezhang
"""
import pandas as pd
# provide directory as argument on command line
# provide directory as argument on command line

# Specify file paths manually
rpllen_file = "approach_rpllen/sample_reversed_extending_force_distance_curve_data_rpllen.txt"
ruplen_file = "retract_ruplen/sample_reversed_retract_data_force_distance_curve_data_ruplen_version1.txt"
rpleng_file = "approach_rpleng/sample_reversed_extending_force_distance_curve_data_rpl_eng.txt"
adheng_file = "retract_adheng/sample_reversed_retract_data_force_distance_curve_data_adh_eng.txt"
indlen_file = "sample_reversed_retract_data_adhforce_indlen_summary.txt"

# Read summary files output in previous steps
df_rpllen = pd.read_csv(rpllen_file, sep='\t')
df_rpllen.rename(columns={'Baseline_y_std_nN': 'Baseline_y_std_nN_repulsive_length'}, inplace=True)

df_ruplen = pd.read_csv(ruplen_file, sep='\t')
df_ruplen.rename(columns={'Baseline_y_std_nN': 'Baseline_y_std_nN_rupture_length'}, inplace=True)

df_rpleng = pd.read_csv(rpleng_file, sep='\t')
df_adheng = pd.read_csv(adheng_file, sep='\t')
df_indlen = pd.read_csv(indlen_file, sep='\t')

# Remove the prefix and suffix to make all dataframes have a common column named Sample_Name
# The steps involve splitting the column to identify and remove the prefixes and suffixes

df_rpllen[['prefix', 'Sample_Name']] = df_rpllen['Sample_Name'].str.split("READSTART", expand=True)
df_rpllen[['Sample_Name', 'suffix']] = df_rpllen['Sample_Name'].str.split(".out.", expand=True)

df_ruplen[['prefix', 'Sample_Name']] = df_ruplen['Sample_Name'].str.split("READSTART", expand=True)
df_ruplen[['Sample_Name', 'suffix']] = df_ruplen['Sample_Name'].str.split(".out.", expand=True)

df_rpleng[['prefix', 'Sample_Name']] = df_rpleng['Sample_Name'].str.split("READSTART", expand=True)
df_rpleng[['Sample_Name', 'suffix']] = df_rpleng['Sample_Name'].str.split(".out.", expand=True)

df_adheng[['prefix', 'Sample_Name']] = df_adheng['Sample_Name'].str.split("READSTART", expand=True)
df_adheng[['Sample_Name', 'suffix']] = df_adheng['Sample_Name'].str.split(".out.", expand=True)

df_indlen[['Sample_Name', 'suffix']] = df_indlen['Sample_Name'].str.split(".out", expand=True)

# Delete the prefix and suffix columns
del df_rpllen['prefix'], df_rpllen['suffix']
del df_ruplen['prefix'], df_ruplen['suffix']
del df_rpleng['prefix'], df_rpleng['suffix']
del df_adheng['prefix'], df_adheng['suffix']
del df_indlen['suffix']

# Merge all dataframes on the 'Sample_Name' column
df_all = pd.merge(df_rpllen, df_ruplen, on='Sample_Name', how='outer')
df_all = pd.merge(df_rpleng, df_all, on='Sample_Name', how='outer')
df_all = pd.merge(df_adheng, df_all, on='Sample_Name', how='outer')
df_all = pd.merge(df_indlen, df_all, on='Sample_Name', how='outer')

# Output the combined dataframe to a new file
df_all.to_csv("combined_summary.txt", sep="\t", index=False)
