#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec  1 18:43:13 2017

@author: ZhangYue
"""

import os
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from scipy import stats
import sys
# Manually set the directory and other variables
# provide directory as argument on command line
data_directory = sys.argv[1]
output_dir = sys.argv[2]
ex_true_sensitivity_value, rt_true_sensitivity_value, spr_con = float(sys.argv[3]), float(sys.argv[4]), float(sys.argv[5])

# Create a .txt file to store the summary
sample_summary = os.path.join(output_dir, data_directory + '_retract_data_adhforce_indlen_summary.txt')

# Make directories for plot and corrected data output
output_directory = os.path.join(output_dir, data_directory + '_retract_data_force_distance_curve_plots')
corrected_data_directory = os.path.join(output_dir, data_directory + '_retract_data_force_distance_curve_data')

os.makedirs(output_directory, exist_ok=True)
os.makedirs(corrected_data_directory, exist_ok=True)

# Ensure that the data directory exists
assert os.path.exists(data_directory)

# Read in .txt files in the data directory
data_file_list = sorted([i for i in os.listdir(data_directory) if i.endswith(".txt")])

# Modify names of output and corrected_data files
output_file_list = [a[:-3] + "plt.png" for a in data_file_list]
corrected_data_file_list = ["READSTART" + a[:-3] + "corrected.txt" for a in data_file_list]

# Modify absolute paths
input_paths = [os.path.join(data_directory, i) for i in data_file_list]
output_paths = [os.path.join(output_directory, i) for i in output_file_list]
corrected_data_paths = [os.path.join(corrected_data_directory, i) for i in corrected_data_file_list]

# Define a function to find the sensitivity line and calculate sensitivity number (V/nm)
def calc_sensitivity(end, intv, x, y):
    sens_x, sens_y = [], []
    for i in range(0, end, intv):
        r = lr(sens_x + x[i:i + intv], sens_y + y[i:i + intv]).rvalue
        if r ** 2 > 0.999:
            sens_x = sens_x + x[i:i + intv]
            sens_y = sens_y + y[i:i + intv]
        else:
            for j in reversed(range(intv)):
                tem_x, tem_y = x[i:i + intv], y[i:i + intv]
                del tem_x[j], tem_y[j]
                r = lr(sens_x + tem_x, sens_y + tem_y).rvalue
                if r ** 2 > 0.999:
                    sens_x = sens_x + tem_x
                    sens_y = sens_y + tem_y
                    break
    if not sens_x or not sens_y:
        return [sens_x, sens_y, None]
    else:
        sensitivity = (-1) * lr(sens_x, sens_y).slope  # sensitivity of deflection
        return [sens_x, sens_y, sensitivity]

# Define a function to find the baseline
def find_baseline2(least_length, sensitivity, x, y):
    y_sens_crct = [i / sensitivity for i in y]
    base_x, base_y = [], []
    window_x = x[-least_length-1:-1]
    window_y = y_sens_crct[-least_length-1:-1]
    slp = lr(window_x, window_y).slope
    std = lr(window_x, window_y).stderr
    if abs(slp) < 0.001 and std < 0.005:
        base_x = window_x
        base_y = [item * sensitivity for item in window_y]
        baseline_start_position = len(x) - least_length
    if not base_y:
        return [None, None]
    else:
        baseline = sum(base_y) / len(base_y)
        return [baseline, baseline_start_position]

# Record the attractive force in a list
sample_name = []
attractive_force_list = []
indentation_length_list = []

# Main processing loop
for in_file, out_file, corrected_data_file in zip(input_paths, output_paths, corrected_data_paths):
    # df = pd.read_csv(in_file, '\t')
    df = pd.read_csv(in_file, sep='\t')
    lr = stats.linregress
    exr = df[df.columns[0]].to_list()
    exv = df[df.columns[1]].to_list()
    rtr = df[df.columns[2]].to_list()
    rtv = df[df.columns[3]].to_list()

    # Find the sensitivity line when approaching the surface
    ex_sensitivity_results = calc_sensitivity(200, 4, exr, exv)
    if ex_sensitivity_results[2] is not None:
        ex_piezo_distance = abs(ex_sensitivity_results[0][0] - ex_sensitivity_results[0][-1])
        ex_deflection_length = abs(ex_sensitivity_results[1][0] - ex_sensitivity_results[1][-1]) / ex_true_sensitivity_value
        indentation_length_nm = ex_piezo_distance - ex_deflection_length

        ##########################################################################
        ##################### Analyzing the retraction curve #####################
        undulating_baseline = False

        rt_sensitivity_results = calc_sensitivity(200, 4, rtr, rtv)
        if rt_sensitivity_results[2] is not None:
            rt_baseline_results = find_baseline2(150, rt_true_sensitivity_value, rtr, rtv)
            if rt_baseline_results[0] is not None:
                x, y = rtr, rtv
                baseline = rt_baseline_results[0]
                baseline_start_position = rt_baseline_results[1]
                sensitivity = rt_sensitivity_results[2]

                new_defl_v = [i - baseline for i in y]
                new_defl_length_nm = [i / rt_true_sensitivity_value for i in new_defl_v]
                force_nN = [i * spr_con for i in new_defl_length_nm]

                x_of_zero_position_nm = lr(rt_sensitivity_results[0], [(i-baseline)/sensitivity for i in rt_sensitivity_results[1]]).intercept
                new_z_nm = [i - x_of_zero_position_nm for i in x]
                separation_distance_nm = [new_z_nm[i] + new_defl_v[i] / sensitivity for i in range(len(new_z_nm))]

                # Attractive Force (most negative force)
                attractive_force_nn = min(force_nN[:baseline_start_position])
                if attractive_force_nn >= 0:
                    attractive_force_nn = 0
                    no_attractive_force = True
                else:
                    no_attractive_force = False

                for i in range(len(force_nN)):
                    if force_nN[i] == attractive_force_nn:
                        attractive_force_position_number = i
                        break

                for i in range(attractive_force_position_number, baseline_start_position):
                    if force_nN[i] > 0.3:
                        undulating_baseline = True
                        break

                # Start to output scatter plot
                if not undulating_baseline:
                    with open(corrected_data_file, "w") as corrected_data_file_handle:
                        corrected_data_file_handle.write('separation_distance_nm' + '\t' + 'force_nN\n')
                        for distance_item, force_item in zip(separation_distance_nm, force_nN):
                            corrected_data_file_handle.write(f"{distance_item}\t{force_item}\n")

                    attractive_force_nn *= -1
                    if '/' not in in_file:
                        n1 = -1
                    else:
                        n1 = in_file.find('/')
                    sample_name.append(in_file[n1+1:-4])
                    attractive_force_list.append(attractive_force_nn)
                    indentation_length_list.append(indentation_length_nm)

                    with open(sample_summary, "w") as summary:
                        summary.write('Sample_Name\tIndentation_Length_nm\tAttractive_Force_nN\n')
                        for name, length, force in zip(sample_name, indentation_length_list, attractive_force_list):
                            summary.write(f"{name}\t{length}\t{force}\n")

                    if no_attractive_force:
                        with open(out_file, "w") as out_file_handle:
                            plt.figure()
                            plt.scatter(separation_distance_nm, force_nN, s=0.5, color='black')
                            plt.text(max(force_nN)/2, max(separation_distance_nm)/2, 'No attractive force')
                            plt.axhline(0, color='blue')
                            plt.axvline(0, color='blue')
                            axes = plt.gca()
                            axes.set_xlim([min(separation_distance_nm) - 100, max(separation_distance_nm) + 100])
                            axes.set_ylim([min(force_nN) - 1.5, max(force_nN) + 0.5])
                            plt.ylabel('Interaction Force (nN)')
                            plt.xlabel('Separation Distance (nm)')
                            plt.savefig(out_file)
                            plt.close()
print('Finished ' + data_directory)
