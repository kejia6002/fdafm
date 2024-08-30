#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May  8 14:51:16 2019

@author: yuezhang
"""

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os
import sys
# Provide directory and baseline region as input
data_directory = sys.argv[1]
output_dir = sys.argv[2]
bsl = int(sys.argv[3])

# Create a .txt file to store the summary
sample_summary = os.path.join(output_dir, f"{data_directory}_rpllen.txt")
# Make directories for plot and corrected data output
output_directory = os.path.join(output_dir, f"{data_directory}_rpllen_plots")

os.makedirs(output_directory, exist_ok=True)

# Ensure that it exists
assert os.path.exists(data_directory)
assert os.path.exists(output_directory)

# Read in .txt files in the data directory
data_file_list = sorted([i for i in os.listdir(data_directory) if i.endswith(".txt")])

# Modify names of output and corrected data files
output_file_list = [f"{a[:-4]}_rpllen_plt.png" for a in data_file_list]

# Modify absolute paths
input_paths = [os.path.join(data_directory, i) for i in data_file_list]
output_paths = [os.path.join(output_directory, i) for i in output_file_list]

sample_name_list, rpl_len_list = [], []
baseline_std_list = []


def rpllen(x, y, bsl):
    # This algorithm automatically finds the position where the first dot
    # has a y value lower than mean(y[-bsl:]) + 3*std(y[-bsl:])
    baseline_y = np.mean(y[-bsl:])
    baseline_y_std = np.std(y[-bsl:])
    counter = 0

    for i in range(len(x)):
        if counter < 1:
            if y[i] <= baseline_y + 3 * baseline_y_std:
                counter += 1
            else:
                counter = 0
        else:
            break

    if counter == 1:
        rpl_len_x = x[i - 1]
        rpl_len_y = y[i - 1]
    else:
        rpl_len_x = False
        rpl_len_y = False

    if rpl_len_x is not False and rpl_len_x < 0:
        rpl_len_x = False
        rpl_len_y = False

    return rpl_len_x, rpl_len_y, baseline_y_std


for in_file, out_file in zip(input_paths, output_paths):

    df = pd.read_csv(in_file, delimiter='\t')
    distance = df[df.columns[0]]
    force = df[df.columns[1]]

    rpl_len_x, rpl_len_y, baseline_y_std = rpllen(distance, force, bsl)

    if rpl_len_x is False:
        continue
    else:
        sample_name_list.append(in_file)
        rpl_len_list.append(rpl_len_x)
        baseline_std_list.append(baseline_y_std)

        with open(out_file, "w") as out_file_handle:
            print_rpl_len = f"Repulsion length = {round(rpl_len_x, 2)} nm"
            plt.figure()
            plt.scatter(distance, force, s=0.5, color='black')
            plt.annotate(print_rpl_len, xy=(rpl_len_x, rpl_len_y),
                         xytext=(100, 2),
                         arrowprops=dict(arrowstyle="->", color='red'),
                         horizontalalignment='left', verticalalignment='bottom')
            plt.axhline(0, color='blue')
            plt.axvline(0, color='blue')
            axes = plt.gca()
            axes.set_xlim([min(distance) - 100, max(distance) + 100])
            axes.set_ylim([min(force) - 1.5, max(force) + 0.5])
            plt.ylabel('Interaction Force (nN)')
            plt.xlabel('Separation Distance (nm)')
            plt.savefig(out_file)
            plt.close()

        rpl_len_x, rpl_len_y = False, False

with open(sample_summary, "w") as summary:
    header = 'Sample_Name\tRepulsion_Length_nm\tBaseline_y_std_nN'
    summary.write(header + '\n')

    for i in range(len(sample_name_list)):
        content = f"{sample_name_list[i]}\t{rpl_len_list[i]}\t{baseline_std_list[i]}"
        summary.write(content + '\n')

print('Finished with approach_rpllen')
