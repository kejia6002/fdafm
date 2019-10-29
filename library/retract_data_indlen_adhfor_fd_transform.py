#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Dec  1 18:43:13 2017

@author: ZhangYue
"""

import matplotlib
matplotlib.use('Agg') #to let it work under windows environment. if its running under linux (mac or linux), no need to include this line
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from scipy import stats
import sys, os, math

# provide directory as argument on command line 
data_directory, output_dir = sys.argv[1], sys.argv[2]
ex_true_sensitivity_value, rt_true_sensitivity_value, spr_con = float(sys.argv[3]), float(sys.argv[4]), float(sys.argv[5])

#create a .txt file to store the summary
sample_summary = output_dir + data_directory + '_retract_data_adhforce_indlen_summary.txt'
#make directories for plot and corrected data output

output_directory = output_dir + data_directory + '_retract_data_force_distance_curve_plots'
corrected_data_directory = output_dir + data_directory + '_retract_data_force_distance_curve_data'

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



#record the attractive force in a list
sample_name = []
attractive_force_list = []
indentation_length_list = []


for in_file, out_file, corrected_data_file in zip(input_paths, output_paths, corrected_data_paths):
    
    df = pd.read_csv(in_file,'\t')

    #create linear regression object
    lr = stats.linregress
    
    exr = df[df.columns[0]]
    exv = df[df.columns[1]]
    rtr = df[df.columns[2]]
    rtv = df[df.columns[3]]

    ##########################################################################
    #####################Analyzing the approach curve#########################
    ex_x = [float(i) for i in exr if i != '  ']
    ex_y = [float(i) for i in exv if i != '  ']
    
    #find the sensitivity line when approaching the surface
    ex_sensitivity_results = calc_sensitivity(200,4,ex_x,ex_y)
    if ex_sensitivity_results[2] == None:
        pass #none sensitivity value means the failure in this calculation
    else: 
        #calculate the total distance traveled by piezo after contact between probe and sample
        ex_piezo_distance = abs(ex_sensitivity_results[0][0] - ex_sensitivity_results[0][-1])
        #calculate the deflection length of cantilever after contact between probe and sample
        ex_deflection_length = abs(ex_sensitivity_results[1][0] - ex_sensitivity_results[1][-1])/ex_true_sensitivity_value
        #indentation length (deformation on surface) + probe deflection distance = piezo traveled distance
        indentation_length_nm = ex_piezo_distance - ex_deflection_length
    
    
        ##########################################################################
        #####################Analyzing the retraction curve#######################
        undulating_baseline = False
        
        rt_x = [i for i in rtr if i != '  ']
        rt_y = [i for i in rtv if i != '  ']
        
        rt_sensitivity_results = calc_sensitivity(200,4,rt_x,rt_y)
        if rt_sensitivity_results[2] == None: #if no sensitivity line was found, that presents the failure of this retracting measurement
            pass
        else:
            rt_baseline_results = find_baseline2(150,rt_true_sensitivity_value,rt_x,rt_y)
            if rt_baseline_results[0] == None:
                undulating_baseline = True
                pass #no baseline found represents the failure of this measurement
            else:

                #assign variables
                x = rt_x
                y = rt_y
                baseline = rt_baseline_results[0]
                baseline_start_position = rt_baseline_results[1]
                sensitivity = rt_sensitivity_results[2]

                #calculation on y axis
                new_defl_v = [i - baseline for i in y]
                new_defl_length_nm = [i/rt_true_sensitivity_value for i in new_defl_v]
                force_nN = [i*spr_con for i in new_defl_length_nm]

                #calculation on x axis
                x_of_zero_position_nm = lr(rt_sensitivity_results[0],[(i-baseline)/sensitivity for i in rt_sensitivity_results[1]]).intercept
                new_z_nm = [i - x_of_zero_position_nm for i in x]
                separation_distance_nm = []
                for i in range(len(new_z_nm)):
                    sd = new_z_nm[i] + new_defl_v[i]/sensitivity
                    separation_distance_nm.append(sd)
                
                #########################################
                #Attractive Force (most negative force)#
                #########################################
                no_attractive_force = False
                attractive_force_nn = min(force_nN[0:baseline_start_position]) #attractive force is negative now
                if attractive_force_nn >= 0:
                    attractive_force_nn = 0
                    no_attractive_force = True
                
                for i in range(len(force_nN)):
                    if force_nN[i] == attractive_force_nn:
                        attractive_force_position_number = i
                        break
                    else:
                        continue
                for i in range(attractive_force_position_number,baseline_start_position):
                    if force_nN[i] > 0.3:
                        undulating_baseline = True #if interation force goes above 0.3 (empirical value), there is too much noise.
                        break
                    else:
                        continue


                #start to output scatter plot
                if undulating_baseline == True:
                    pass
                else:
                    #record the corrected data individually
                    with open(corrected_data_file, "w") as corrected_data_file_handle:
                        corrected_data_file_handle.write('separation_distance_nm' + '\t' + 'force_nN')
                        corrected_data_file_handle.write('\n')
                        for distance_item, force_item in zip(separation_distance_nm, force_nN): 
                            linetowrite = str(distance_item) + '\t' + str(force_item)
                            corrected_data_file_handle.write(linetowrite)
                            corrected_data_file_handle.write('\n')
                    
                    attractive_force_nn = attractive_force_nn * (-1) #make the force to be a positive value
                    #standardize the name
                    if '/' not in in_file:
                        n1 = -1
                    else:
                        n1 = in_file.find('/')
                    sample_name.append(in_file[n1+1:-4])
                    attractive_force_list.append(attractive_force_nn)
                    indentation_length_list.append(indentation_length_nm)

                    #export a summary file which records the indentation length and attractive force. note that 
                    #if the attractive force is not detected, then zero is recorded  
                    with open(sample_summary, "write") as summary:
                        header = 'Sample_Name' + '\t' + 'Indentation_Length_nm' + '\t' + 'Attractive_Force_nN'
                        summary.write(header)
                        summary.write('\n')

                        for i in range(len(sample_name)):
                            content = sample_name[i] + '\t' + str(indentation_length_list[i]) + '\t' + str(attractive_force_list[i])
                            summary.write(content)
                            summary.write('\n')

                    if no_attractive_force == True:

                        with open(out_file, "w") as out_file_handle:
                            print_attractive_force = 'No attractive force detected, recorded as 0 nN'
                            plt.figure()
                            plt.scatter(separation_distance_nm, force_nN, s=0.5, color='black')
                            plt.text(max(force_nN)/2,max(separation_distance_nm)/2,'no attractive force')
                            plt.axhline(0, color='blue')
                            plt.axvline(0, color='blue')
                            axes = plt.gca()
                            axes.set_xlim([min(separation_distance_nm)-100, max(separation_distance_nm)+100])
                            axes.set_ylim([min(force_nN)-1.5,max(force_nN)+0.5])
                            plt.ylabel('Interaction Force (nN)')
                            plt.xlabel('Separation Distance (nm)')
                            plt.savefig(out_file)
                            plt.close()
                    
                    else:  
                        for i in range(len(force_nN)):
                            if force_nN[i] == (-1)*attractive_force_nn:
                                attractive_force_position_nm = separation_distance_nm[i]
                                break
                            else: continue
                        with open(out_file, "w") as out_file_handle:
                            print_attractive_force = 'attractive force = ' + str(round(attractive_force_nn,2)) + ' nN, ' + 'indentation length = ' + str(round(indentation_length_nm,2)) + ' nm.'
                            plt.figure()
                            plt.scatter(separation_distance_nm, force_nN, s=0.5, color='black')
                            plt.annotate(print_attractive_force, xy=(attractive_force_position_nm, 
                                        (-1)*attractive_force_nn), xytext=(0, attractive_force_nn-1),
                                        arrowprops=dict(arrowstyle="->", color='red'),
                                        horizontalalignment='left',verticalalignment='bottom')
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
                
                
                
                    
                    
                    
                    
