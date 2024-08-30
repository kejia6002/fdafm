#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sun Oct 15 22:40:47 2017

@author: yuezhang, Kejia Hu

"""

import os
import sys
# Prompt user for the input directory and output directory
data_directory = sys.argv[1]
output_dir = sys.argv[2]

# Create the output directory
output_dir_path = os.path.join(output_dir, f"{os.path.basename(data_directory)}_reversed")
os.makedirs(output_dir_path, exist_ok=True)

# Ensure that the input directory exists
if not os.path.exists(data_directory):
    raise FileNotFoundError(f"Input directory '{data_directory}' does not exist.")

# Get a list of .txt files in the data directory
data_file_list = sorted([f for f in os.listdir(data_directory) if f.endswith(".txt")])

# Modify names of output files
output_file_list = [f"{os.path.splitext(f)[0]}_out.txt" for f in data_file_list]

# Modify absolute paths
output_paths = [os.path.join(output_dir_path, f) for f in output_file_list]
input_paths = [os.path.join(data_directory, f) for f in data_file_list]

# Process each pair of input and output files
for in_file, out_file in zip(input_paths, output_paths):

    # Open the input file and read the lines
    with open(in_file, "r") as in_file_handle:
        lines = in_file_handle.readlines()

    # Process the data by filtering out lines that start with a space
    cutted_lines = [line for line in lines if not line.startswith(' ')]
    uncutted_lines = lines[len(cutted_lines):]

    # Split the lines into columns and zip them to transpose
    org_file = list(zip(*(line.strip().split('\t') for line in cutted_lines)))
    uncutted_org_file = list(zip(*(line.strip().split('\t') for line in uncutted_lines)))

    calc_ramp_ex_nm_with_tit = org_file[0]
    defl_v_ex_with_tit = org_file[2]

    if uncutted_org_file:
        calc_ramp_rt_nm_with_tit = org_file[1] + uncutted_org_file[0]
        defl_v_rt_with_tit = org_file[3] + uncutted_org_file[2]
    else:
        calc_ramp_rt_nm_with_tit = org_file[1]
        defl_v_rt_with_tit = org_file[3]

    calc_ramp_ex_nm = calc_ramp_ex_nm_with_tit[1:]
    calc_ramp_rt_nm = calc_ramp_rt_nm_with_tit[1:]
    defl_v_ex = defl_v_ex_with_tit[1:]
    defl_v_rt = defl_v_rt_with_tit[1:]

    # Convert the columns to lists of floats
    ramp_ex = [float(value) for value in calc_ramp_ex_nm]
    ramp_rt = [float(value) for value in calc_ramp_rt_nm]
    defl_ex = [float(value) for value in defl_v_ex]
    defl_rt = [float(value) for value in defl_v_rt]

    # Reverse the ramp_rt and defl_ex lists
    ramp_rt.reverse()
    defl_ex.reverse()

    # Pad the shorter lists with spaces to match the length of the longest list
    length_long = len(ramp_rt)
    length_short = len(ramp_ex)
    ramp_ex.extend(' ' for _ in range(length_long - length_short))
    defl_ex.extend(' ' for _ in range(length_long - length_short))

    # Write the output file
    header = "Calc_Ramp_Ex_nm\tDefl_V_Ex\tCalc_Ramp_Rt_nm\tDefl_V_Rt\n"
    with open(out_file, "w") as out_file_handle:
        out_file_handle.write(header)
        for ex, de, rt, dr in zip(ramp_ex, defl_ex, ramp_rt, defl_rt):
            out_file_handle.write(f"{ex}\t{de}\t{rt}\t{dr}\n")

print(f"Processed {os.path.basename(data_directory)}")

