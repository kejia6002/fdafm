#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec  1 18:43:13 2017

@author: ZhangYue
"""

import os, sys
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from scipy import stats

data_directory, output_dir = sys.argv[1], sys.argv[2]
ex_true_sensitivity_value, spr_con = float(sys.argv[3]), float(sys.argv[4])

# Create directories for plot and corrected data output
output_directory = os.path.join(output_dir, f"{os.path.basename(data_directory)}_extending_force_distance_curve_plots")
corrected_data_directory = os.path.join(output_dir,
                                        f"{os.path.basename(data_directory)}_extending_force_distance_curve_data")
os.makedirs(output_directory, exist_ok=True)
os.makedirs(corrected_data_directory, exist_ok=True)

# Ensure that the input directory exists
if not os.path.exists(data_directory):
    raise FileNotFoundError(f"Input directory '{data_directory}' does not exist.")

# Get a list of .txt files in the data directory
data_file_list = sorted([f for f in os.listdir(data_directory) if f.endswith(".txt")])

# Modify names of output and corrected_data files
output_file_list = [f"{os.path.splitext(f)[0]}_plt.png" for f in data_file_list]
corrected_data_file_list = [f"READSTART_{os.path.splitext(f)[0]}_corrected.txt" for f in data_file_list]

# Modify absolute paths
input_paths = [os.path.join(data_directory, f) for f in data_file_list]
output_paths = [os.path.join(output_directory, f) for f in output_file_list]
corrected_data_paths = [os.path.join(corrected_data_directory, f) for f in corrected_data_file_list]


# Define a function to find the sensitivity line and calculate sensitivity number (V/nm)
def calc_sensitivity(end, intv, x, y):
    sens_x, sens_y = [], []
    lr = stats.linregress  # create linear regression object
    for i in range(0, end, intv):
        r = lr(sens_x + x[i:i + intv], sens_y + y[i:i + intv]).rvalue
        if r * r > 0.999:
            sens_x += x[i:i + intv]
            sens_y += y[i:i + intv]
        else:
            for j in reversed(range(intv)):
                tem_x, tem_y = x[i:i + intv], y[i:i + intv]
                del tem_x[j], tem_y[j]
                r = lr(sens_x + tem_x, sens_y + tem_y).rvalue
                if r * r > 0.999:
                    sens_x += tem_x
                    sens_y += tem_y
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
    window_x = x[-least_length - 1:-1]
    window_y = y_sens_crct[-least_length - 1:-1]
    lr = stats.linregress  # create linear regression object
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


# Process each pair of input and output files
for in_file, out_file, corrected_data_file in zip(input_paths, output_paths, corrected_data_paths):

    df = pd.read_csv(in_file, sep='\t')
    lr = stats.linregress
    exr = df[df.columns[0]].to_list()
    exv = df[df.columns[1]].to_list()

    ##########################################################################
    ##################### Analyzing the approach curve #######################

    undulating_baseline = False

    ex_sensitivity_results = calc_sensitivity(200, 4, exr, exv)
    if ex_sensitivity_results[
        2] is None:  # if no sensitivity line was found, that presents the failure of this retracting measurement
        continue
    else:
        ex_baseline_results = find_baseline2(150, ex_true_sensitivity_value, exr, exv)
        if ex_baseline_results[0] is None:
            undulating_baseline = True  # no baseline found represents the failure of this measurement
            continue
        else:
            x = exr
            y = exv
            baseline = ex_baseline_results[0]
            baseline_start_position = ex_baseline_results[1]
            sensitivity = ex_sensitivity_results[2]

            # Calculation on y axis
            new_defl_v = [i - baseline for i in y]
            new_defl_length_nm = [i / ex_true_sensitivity_value for i in new_defl_v]
            force_nN = [i * spr_con for i in new_defl_length_nm]

            # Calculation on x axis
            x_of_zero_position_nm = lr(ex_sensitivity_results[0],
                                       [(i - baseline) / sensitivity for i in ex_sensitivity_results[1]]).intercept
            new_z_nm = [i - x_of_zero_position_nm for i in x]

            separation_distance_nm = []
            for i in range(len(new_z_nm)):
                sd = new_z_nm[i] + new_defl_v[i] / sensitivity
                separation_distance_nm.append(sd)

            # Record the corrected data individually
            with open(corrected_data_file, "w") as corrected_data_file_handle:
                corrected_data_file_handle.write('separation_distance_nm\tforce_nN\n')
                for distance_item, force_item in zip(separation_distance_nm, force_nN):
                    corrected_data_file_handle.write(f"{distance_item}\t{force_item}\n")

            # Save the plot
            plt.figure()
            plt.scatter(separation_distance_nm, force_nN, s=0.5, color='black')
            plt.axhline(0, color='blue')
            plt.axvline(0, color='blue')
            axes = plt.gca()
            axes.set_xlim([min(separation_distance_nm) - 100, max(separation_distance_nm) + 100])
            axes.set_ylim([min(force_nN) - 1.5, max(force_nN) + 0.5])
            plt.ylabel('Interaction Force (nN)')
            plt.xlabel('Separation Distance (nm)')
            plt.savefig(out_file)
            plt.close()

print(f"Finished processing {data_directory}")
