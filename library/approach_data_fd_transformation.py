#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Dec  1 18:43:13 2017

@author: ZhangYue
"""
matplotlib.use('Agg') #to let it work under windows environment. if its running under linux (mac or linux), no need to include this line
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from scipy import stats
import sys, os, math

# provide directory as argument on command line 
data_directory, output_dir = sys.argv[1], sys.argv[2]
ex_true_sensitivity_value, spr_con = float(sys.argv[3]), float(sys.argv[4])


#make directories for plot and corrected data output
output_directory = output_dir + data_directory + '_extending_force_distance_curve_plots'
corrected_data_directory = output_dir + data_directory + '_extending_force_distance_curve_data'
os.mkdir(output_directory), os.mkdir(corrected_data_directory)

# ensure that it exists
assert os.path.exists(data_directory)
assert os.path.exists(output_directory)
assert os.path.exists(corrected_data_directory)

# read in .txt files in data directory
data_file_list = sorted([i for i in os.listdir(data_directory) if i.endswith(".txt")])

# modify names of output and corrected_data files
output_file_list = [a[:-3]+"plt.png" for a in data_file_list]
corrected_data_file_list = ["READSTART" + a[:-3]+"corrected.txt" for a in data_file_list]

# modify absolute paths 
input_paths = [os.path.join(data_directory, i) for i in data_file_list]
output_paths = [os.path.join(output_directory, i) for i in output_file_list]
corrected_data_paths = [os.path.join(corrected_data_directory, i) for i in corrected_data_file_list]

#define a function to find the sensitivity line and calculate sensitivity number (V/nm) (updated 20190710)

def calc_sensitivity(end,intv,x,y):
    sens_x, sens_y = [], []
    for i in range(0,end,intv):
        r = lr(sens_x + x[i:i+intv],sens_y + y[i:i+intv]).rvalue
        if r > 0.99:
            sens_x = sens_x + x[i:i+intv]
            sens_y =sens_y + y[i:i+intv]        
        else:#take out the outlier
            for j in reversed(range(intv)):
                tem_x, tem_y = x[i:i+intv], y[i:i+intv]
                del tem_x[j], tem_y[j]
                r = lr(sens_x+tem_x, sens_y+tem_y).rvalue
                if abs(r) > 0.99:
                    sens_x = sens_x + tem_x
                    sens_y = sens_y + tem_y
                    break
                else: continue   
    if sens_x == [] or sens_y == []:
        return [sens_x,sens_y,None]
    else:
        sensitivity = (-1)*lr(sens_x,sens_y).slope #sensitivity of deflection
        return [sens_x,sens_y,sensitivity]

#define a function to find the baseline 
#least_length is the least length of the baseline you set

def find_baseline2(least_length,sensitivity,x,y):
    y_sens_crct = [i/sensitivity for i in y]
    base_x, base_y = [], [] 
    window_x = x[len(x)-least_length-1:len(x)-1]
    window_y = y_sens_crct[len(x)-least_length-1:len(x)-1]
    slp = lr(window_x,window_y).slope
    std = lr(window_x,window_y).stderr
    if abs(slp) < 0.001 and std < 0.005:
        base_x = window_x
        base_y = [item*sensitivity for item in window_y]
        baseline_start_position = len(x)-least_length
    if base_y == []:
        return [None,None]
    else:
        #baseline is the value on y axis, which is the average of the list we've just found
        baseline = sum(base_y)/len(base_y)
        return [baseline,baseline_start_position]


for in_file, out_file, corrected_data_file in zip(input_paths, output_paths, corrected_data_paths):
    
    df = pd.read_csv(in_file,'\t')

    #create linear regression object
    lr = stats.linregress
    
    exr = df[df.columns[0]]
    exv = df[df.columns[1]]

    ##########################################################################
    #####################Analyzing the approach curve#########################
    ex_x = [float(i) for i in exr if i != '  ']
    ex_y = [float(i) for i in exv if i != '  ']

    undulating_baseline = False
    
    ex_sensitivity_results = calc_sensitivity(200,4,ex_x,ex_y)
    if ex_sensitivity_results[2] == None: #if no sensitivity line was found, that presents the failure of this retracting measurement
        pass
    else:
        ex_baseline_results = find_baseline2(150,ex_true_sensitivity_value,ex_x,ex_y)
        if ex_baseline_results[0] == None:
            undulating_baseline = True #no baseline found represents the failure of this measurement
            pass
        else:
            #assign variables
            x = ex_x
            y = ex_y
            baseline = ex_baseline_results[0]
            baseline_start_position = ex_baseline_results[1]
            sensitivity = ex_sensitivity_results[2]

            #calculation on y axis
            new_defl_v = [i - baseline for i in y]
            new_defl_length_nm = [i/ex_true_sensitivity_value for i in new_defl_v]
            force_nN = [i*spr_con for i in new_defl_length_nm]

            #calculation on x axis
            x_of_zero_position_nm = lr(ex_sensitivity_results[0],[(i-baseline)/sensitivity for i in ex_sensitivity_results[1]]).intercept
            new_z_nm = [i - x_of_zero_position_nm for i in x]

            separation_distance_nm = []
            for i in range(len(new_z_nm)):
                sd = new_z_nm[i] + new_defl_v[i]/sensitivity
                separation_distance_nm.append(sd)
            

            #record the corrected data individually
            with open(corrected_data_file, "w") as corrected_data_file_handle:
                corrected_data_file_handle.write('separation_distance_nm' + '\t' + 'force_nN')
                corrected_data_file_handle.write('\n')
                for distance_item, force_item in zip(separation_distance_nm, force_nN):
                    linetowrite = str(distance_item) + '\t' + str(force_item)
                    corrected_data_file_handle.write(linetowrite)
                    corrected_data_file_handle.write('\n')


            with open(out_file, "w") as out_file_handle:
                plt.figure()
                plt.scatter(separation_distance_nm, force_nN, s=0.5, color='black')
                plt.axhline(0, color='blue')
                plt.axvline(0, color='blue')
                axes = plt.gca()
                axes.set_xlim([min(separation_distance_nm)-100, max(separation_distance_nm)+100])
                axes.set_ylim([min(force_nN)-1.5,max(force_nN)+0.5])
                plt.ylabel('Interaction Force (nN)')
                plt.xlabel('Separation Distance (nm)')
                plt.savefig(out_file)
                plt.close()

print 'Finished' + data_directory
    
    
    
        
                
                
                
