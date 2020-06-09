#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Dec  1 18:43:13 2017

@author: ZhangYue
"""

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from scipy import stats
import sys, os, math


# provide directory as argument on command line 
data_directory = sys.argv[1]
output_dir = sys.argv[2]
sample_summary = output_dir + data_directory +'_senscal.txt'

# ensure that it exists
assert os.path.exists(data_directory)

# read in .txt files in data directory
data_file_list = sorted([i for i in os.listdir(data_directory) if i.endswith(".txt")])

# modify absolute paths 
input_paths = [os.path.join(data_directory, i) for i in data_file_list]

#record the sensitivity in lists
sample_name = []
ex_sens_list = []
rt_sens_list = []

#define a function to find the sensitivity line and calculate sensitivity number (V/nm) (updated 20190710)

def calc_sensitivity(end,intv,x,y):
    sens_x, sens_y = [], []
    for i in range(0,end,intv):
        r = lr(sens_x + x[i:i+intv],sens_y + y[i:i+intv]).rvalue
        if r*r > 0.999:#updated
            sens_x = sens_x + x[i:i+intv]
            sens_y =sens_y + y[i:i+intv]        
        else:#take out the outlier
            for j in reversed(range(intv)):
                tem_x, tem_y = x[i:i+intv], y[i:i+intv]
                del tem_x[j], tem_y[j]
                r = lr(sens_x+tem_x, sens_y+tem_y).rvalue
                if r*r > 0.999:#updated
                    sens_x = sens_x + tem_x
                    sens_y = sens_y + tem_y
                    break
                else: continue   
    if sens_x == [] or sens_y == []:
        return [sens_x,sens_y,None]
    else:
        sensitivity = (-1)*lr(sens_x,sens_y).slope #sensitivity of deflection
        return [sens_x,sens_y,sensitivity]
    

for in_file in input_paths:
    
    df = pd.read_csv(in_file,'\t')
    #create linear regression object
    lr = stats.linregress
    
    exr = df[df.columns[0]]
    exv = df[df.columns[1]]
    rtr = df[df.columns[2]]
    rtv = df[df.columns[3]]

    ##########################################################################
    #####################Analyzing the approach curve#########################
    #here I only pick the first 200 points to analyze the sensitivity to avoid the blank in the columns.
    ex_x = [float(i) for i in exr if i != '  ']
    ex_y = [float(i) for i in exv if i != '  ']
    
    #find the sensitivity line when approaching the surface
    ex_sensitivity_results = calc_sensitivity(200,4,ex_x,ex_y)

    ##########################################################################
    #####################Analyzing the retraction curve#######################
    rt_x = [i for i in rtr if i != '  ']
    rt_y = [i for i in rtv if i != '  ']

    #find the sensitivity line when leaving the surface
    rt_sensitivity_results = calc_sensitivity(200,4,rt_x,rt_y)
    
    #standardize the name
    n1 = in_file.find('/')
    sample_name.append(in_file[n1+1:-4])
    ex_sens_list.append(ex_sensitivity_results[2])
    rt_sens_list.append(rt_sensitivity_results[2])
            
with open(sample_summary, "write") as summary:
    header = 'Sample_Name' + '\t' + 'Extending_Sensitivity_V/nm' + '\t' + 'Retracting_Sensitivity_V/nm'
    summary.write(header)
    summary.write('\n')

    for i in range(len(sample_name)):
        content = sample_name[i] + '\t' + str(ex_sens_list[i]) + '\t' + str(rt_sens_list[i])
        summary.write(content)
        summary.write('\n')
print 'Finished ' + data_directory
        
        
        
            
            
            
            
