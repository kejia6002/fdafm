#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May  6 17:22:12 2019

@author: yuezhang
"""

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from scipy import stats
import os
import sys
# provide directory as arguments
data_directory = sys.argv[1]
output_dir = sys.argv[2]

# Create a .txt file to store the summary
sample_summary = os.path.join(output_dir, f"{data_directory}_rpl_eng.txt")

# Make a directory to store the force-distance curves with noted adhesive energy
output_directory = os.path.join(output_dir, f"{data_directory}_rpl_eng_plots")

os.makedirs(output_directory, exist_ok=True)

# Ensure that the directories exist
assert os.path.exists(data_directory)
assert os.path.exists(output_directory)

# Read in .txt files in the data directory
data_file_list = sorted([i for i in os.listdir(data_directory) if i.endswith(".txt")])

# Modify names of output files
output_file_list = [f"{a[:-4]}_rpl_eng.png" for a in data_file_list]

# Modify absolute paths
input_paths = [os.path.join(data_directory, i) for i in data_file_list]
output_paths = [os.path.join(output_directory, i) for i in output_file_list]

sample_name_list, rpl_eng_list = [], []


def transform(y):
    new_y = []
    for i in y:
        if i < 0:
            i = 0
        new_y.append(i)
    return new_y


def cal_rpl_eng(x, y):
    total_area = 0
    for i in range(len(x) - 1, 0, -1):
        if x[i - 1] < 0:
            total_area += (y[i] + y[i - 1]) * x[i] / 2
            break
        total_area += abs(((y[i] + y[i - 1]) * (x[i] - x[i - 1])) / 2)
    return i, total_area


for in_file, out_file in zip(input_paths, output_paths):

    df = pd.read_csv(in_file, delimiter='\t')

    distance = df[df.columns[0]]
    force = df[df.columns[1]]

    transformed_force = transform(force)

    if len(distance) != len(transformed_force):
        print("Transform distance/force failed")
        continue
    else:
        x_stop, rpl_eng_aj = cal_rpl_eng(distance, transformed_force)
        sample_name_list.append(in_file)
        rpl_eng_list.append(rpl_eng_aj)
        with open(out_file, "w") as out_file_handle:
            print_rpl_eng = f"Repulsive energy = {round(rpl_eng_aj, 2)} aJ"
            plt.figure()
            plt.scatter(distance[0:x_stop], force[0:x_stop], s=3, color='red')
            plt.scatter(distance[x_stop:], force[x_stop:], s=0.5, color='black')
            plt.annotate(print_rpl_eng, xy=(0, 0), xytext=(100, 2))
            plt.axhline(0, color='blue')
            plt.axvline(0, color='blue')
            axes = plt.gca()
            axes.set_xlim([min(distance) - 100, max(distance) + 100])
            axes.set_ylim([min(force) - 1.5, max(force) + 0.5])
            plt.ylabel('Interaction Force (nN)')
            plt.xlabel('Separation Distance (nm)')
            plt.savefig(out_file)
            plt.close()

with open(sample_summary, "w") as summary:
    header = 'Sample_Name\tRepulsive_Energy_aJ'
    summary.write(header + '\n')

    for i in range(len(sample_name_list)):
        content = f"{sample_name_list[i]}\t{rpl_eng_list[i]}"
        summary.write(content + '\n')

print('Finished with approach_rpl_energy')
