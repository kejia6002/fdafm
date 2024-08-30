# -*- coding: utf-8 -*-
"""
Created on Mon May  6 17:22:12 2019

@author: yuezhang
"""
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os, sys

# Set these variables manually
# provide directory as argument on command line
data_directory = sys.argv[1]
output_dir = sys.argv[2]

bsl = 150  # Set the baseline region manually, e.g., the last 150 points

# Create a summary .txt file
sample_summary = os.path.join(output_dir, f"{data_directory}_ruplen_version1.txt")

# Create directories for plot output
output_directory = os.path.join(output_dir, f"{data_directory}_ruplen_plots-version1")

os.makedirs(output_dir, exist_ok=True)
os.makedirs(output_directory, exist_ok=True)

# Ensure the directories exist
assert os.path.exists(data_directory)
assert os.path.exists(output_directory)

# Read in .txt files in the data directory
data_file_list = sorted([i for i in os.listdir(data_directory) if i.endswith(".txt")])

# Modify names of output files
output_file_list = [a[:-3] + "ruplen_plt.png" for a in data_file_list]

# Modify absolute paths
input_paths = [os.path.join(data_directory, i) for i in data_file_list]
output_paths = [os.path.join(output_directory, i) for i in output_file_list]

sample_name_list, rupture_len_list = [], []
baseline_std_list = []


def rupturelen(x, y, bsl):
    # This algorithm automatically finds the position where the first dot
    # has a y-value higher than mean(y[-bsl:]) - 3*std(y[-bsl:])
    baseline_y = np.mean(y[-bsl:])
    baseline_y_std = np.std(y[-bsl:])
    adfor_idx = y.idxmin()
    adfor_y = y[adfor_idx]
    counter = 0

    if adfor_y >= baseline_y - 3 * baseline_y_std:
        rup_len_x = False
        rup_len_y = False
    else:
        for i in range(adfor_idx, len(x)):
            if counter < 1:
                if y[i] >= baseline_y - 3 * baseline_y_std:
                    counter += 1
                else:
                    counter = 0
            else:
                break
        if counter == 1:
            rup_len_x = x[i - 1]
            rup_len_y = y[i - 1]
        else:
            rup_len_x = False
            rup_len_y = False

    return rup_len_x, rup_len_y, baseline_y_std


for in_file, out_file in zip(input_paths, output_paths):

    df = pd.read_csv(in_file, sep='\t')

    distance = df[df.columns[0]]
    force = df[df.columns[1]]

    rupture_len_x, rupture_len_y, baseline_y_std = rupturelen(distance, force, bsl)

    if rupture_len_x:
        sample_name_list.append(in_file)
        rupture_len_list.append(rupture_len_x)
        baseline_std_list.append(baseline_y_std)

        with open(out_file, "w") as out_file_handle:
            print_rupture_len = f'rupture length = {round(rupture_len_x, 2)} nm'
            plt.figure()
            plt.scatter(distance, force, s=0.5, color='black')
            plt.annotate(print_rupture_len, xy=(rupture_len_x, rupture_len_y),
                         xytext=(100, 2), arrowprops=dict(arrowstyle="->", color='red'),
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

with open(sample_summary, "w") as summary:
    header = 'Sample_Name\tRupture_Length_nm\tBaseline_y_std_nN'
    summary.write(header)
    summary.write('\n')

    for name, rup_len, baseline_std in zip(sample_name_list, rupture_len_list, baseline_std_list):
        content = f'{name}\t{rup_len}\t{baseline_std}'
        summary.write(content)
        summary.write('\n')

print('Finished with retract_ruplen')
