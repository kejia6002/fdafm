#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed May  8 14:51:16 2019

@author: yuezhang
"""

import matplotlib
matplotlib.use('Agg') #to let it work under windows environment. if its running under linux (mac or linux), no need to include this line
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from scipy import stats
import sys, os, math


# provide directory as argument on command line 
data_directory = sys.argv[1]
output_dir = sys.argv[2]

#create a .txt file to store the summary
sample_summary = output_dir + data_directory + '_rpllen.txt'
#make directories for plot and corrected data output

output_directory = output_dir + data_directory + '_rpllen_plots'

os.mkdir(output_dir)
os.mkdir(output_directory)

# ensure that it exists
assert os.path.exists(data_directory)
assert os.path.exists(output_directory)

# read in .txt files in data directory
data_file_list = sorted([i for i in os.listdir(data_directory) if i.endswith(".txt")])

# modify names of output and corrected_data files
output_file_list = [a[:-3]+"rpllen_plt.png" for a in data_file_list]

# modify absolute paths 
input_paths = [os.path.join(data_directory, i) for i in data_file_list]
output_paths = [os.path.join(output_directory, i) for i in output_file_list]


sample_name_list, rpl_len_list = [],[]
baseline_std_list = []

def rpllen(x,y): #this algorithm automatically find the position the first dot
    #has y value lower than mean(y[-150:]) + 3*std(y[-150:])
    baseline_y = np.mean(y[-150:])
    baseline_y_std = np.std(y[-150:])
    counter = 0
    
    for i in range(len(x)):
        if counter < 1:        
            if y[i] <= baseline_y+3*baseline_y_std:
               counter= counter +1
            else:
                counter = 0
        else: break
    if counter == 1:
        rpl_len_x = x[i-1]
        rpl_len_y = y[i-1]
    else:
        rpl_len_x = False
        rpl_len_y = False
        
    return rpl_len_x, rpl_len_y, baseline_y_std

for in_file, out_file in zip(input_paths, output_paths):
    
    df = pd.read_csv(in_file,'\t')
    distance = df[df.columns[0]]
    force = df[df.columns[1]]

    rpl_len_x, rpl_len_y, baseline_y_std = rpllen(distance,force)
    
    
    if rpl_len_x == False:
        pass
    else:
        sample_name_list.append(in_file)
        rpl_len_list.append(rpl_len_x)
        baseline_std_list.append(baseline_y_std)

        with open(out_file, "w") as out_file_handle:
            print_rpl_len = 'repulsion length = ' + str(round(rpl_len_x,2)) + ' nm'
            plt.figure()
            plt.scatter(distance, force, s=0.5, color='black')
            plt.annotate(print_rpl_len, xy=(rpl_len_x, rpl_len_y
                        ), xytext=(100, 2),
                        arrowprops=dict(arrowstyle="->", color='red'),
                        horizontalalignment='left',verticalalignment='bottom')
            plt.axhline(0, color='blue')
            plt.axvline(0, color='blue')
            axes = plt.gca()
            axes.set_xlim([min(distance)-100, max(distance)+100])
            axes.set_ylim([min(force)-1.5,max(force)+0.5])
            plt.ylabel('Interaction Force (nN)')
            plt.xlabel('Separation Distance (nm)')
            plt.savefig(out_file)
            plt.close()
            
        rpl_len_x, rpl_len_y = False, False

with open(sample_summary, "w") as summary:
    header = 'Sample_Name' + '\t' + 'repulsion_Length_nm' + '\t' + 'Baseline_y_std_nN'
    summary.write(header)
    summary.write('\n')

    for i in range(len(sample_name_list)):
        content = sample_name_list[i] + '\t' + str(rpl_len_list[i]) + '\t' + str(baseline_std_list[i])
        summary.write(content)
        summary.write('\n')
    print 'Finished with apporach_rpllen'
    