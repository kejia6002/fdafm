#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May  6 17:22:12 2019

@author: yuezhang
"""
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os, sys

# Provide directory paths and settings directly in the script
# provide directory as argument on command line
data_directory = sys.argv[1]
output_dir = sys.argv[2]

# Create a .txt file to store the summary
sample_summary = os.path.join(output_dir, f"{data_directory}_adh_eng.txt")

# Make a directory to store the force-distance curves with noted adhesive energy
output_directory = os.path.join(output_dir, f"{data_directory}_adh_eng_plots")

os.makedirs(output_dir, exist_ok=True)
os.makedirs(output_directory, exist_ok=True)

# Ensure that the directories exist
assert os.path.exists(data_directory)
assert os.path.exists(output_directory)

# Read in .txt files in data directory
data_file_list = sorted([i for i in os.listdir(data_directory) if i.endswith(".txt")])

# Modify names of output and corrected_data files
output_file_list = [f"{os.path.splitext(a)[0]}_adh_eng.png" for a in data_file_list]

# Modify absolute paths
input_paths = [os.path.join(data_directory, i) for i in data_file_list]
output_paths = [os.path.join(output_directory, i) for i in output_file_list]

sample_name_list, adh_eng_list = [], []


def transform(x, y):
    new_x, new_y = [], []
    for i in y:
        new_y.append(min(i, 0))  # Set positive values to 0
    for i in x:
        new_x.append(max(i, 0))  # Set negative values to 0
    return new_x, new_y


def cal_adh_eng(x, y):
    total_area = sum(abs(((y[i] + y[i + 1]) * (x[i + 1] - x[i])) / 2) for i in range(len(x) - 1))
    return total_area


for in_file, out_file in zip(input_paths, output_paths):
    df = pd.read_csv(in_file, sep='\t')
    distance = df.iloc[:, 0]
    force = df.iloc[:, 1]

    transformed_distance, transformed_force = transform(distance, force)

    if len(transformed_distance) != len(transformed_force):
        print("Transform distance/force failed")
        continue

    adh_eng_aj = cal_adh_eng(transformed_distance, transformed_force)
    sample_name_list.append(in_file)
    adh_eng_list.append(adh_eng_aj)

    print_adh_eng = f'adhesive energy = {round(adh_eng_aj, 2)} aJ'
    plt.figure()
    plt.scatter(distance, force, s=0.5, color='black')
    plt.annotate(print_adh_eng, xy=(0, 0), xytext=(100, 2))
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
    header = 'Sample_Name\tAdhesive_Energy_aJ\n'
    summary.write(header)

    for name, energy in zip(sample_name_list, adh_eng_list):
        summary.write(f"{name}\t{energy}\n")

print('Finished with retract_adh_eng')
