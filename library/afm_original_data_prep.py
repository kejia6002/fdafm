#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sun Oct 15 22:40:47 2017

@author: yuezhang

"""

import sys, os

# provide directory as argument on command line 
data_directory = sys.argv[1]
output_dir = sys.argv[2]
os.mkdir(output_dir + data_directory + '_reversed')
out_directory = output_dir + data_directory + '_reversed'
# ensure that it exists
assert os.path.exists(data_directory)
assert os.path.exists(out_directory)
# read in .txt files in data directory
'''
Return a list containing the names of the entries in the directory given by 
path. The list is in arbitrary order. It does not include the special entries
 '.' and '..' even if they are present in the directory.
'''
data_file_list = sorted([i for i in os.listdir(data_directory) if i.endswith(".txt")])

# modify names of output files
output_file_list = [a[:-3]+"out.txt" for a in data_file_list]

# modify absolute paths 
output_paths = [os.path.join(out_directory, i) for i in output_file_list]
input_paths = [os.path.join(data_directory, i) for i in data_file_list]

# you can modify the previous line to output the results to a different file
# you would just need to add another command line argument for the output


# process each pair of input & output files in a loop 
for in_file, out_file in zip(input_paths, output_paths):
    
    # open the file and readlines 
    with open(in_file, "r") as in_file_handle:
        org = list(in_file_handle)
        
    # process the data with 4 columns
    cutted_org = []
    for i in org:
        if i[0] != ' ':
            cutted_org.append(i)
    org_file = zip(*(line.strip().split('\t') for line in cutted_org))
    
    #in case some columns are empty
    uncutted_org = org[len(cutted_org):]
    uncutted_org_file = zip(*(line.strip().split('\t') for line in uncutted_org))
    
    calc_ramp_ex_nm_with_tit = org_file[0]
    defl_v_ex_with_tit = org_file[2]
    if uncutted_org_file != []:
        calc_ramp_rt_nm_with_tit = org_file[1] + uncutted_org_file[0]
        defl_v_rt_with_tit = org_file[3] + uncutted_org_file[2]
    else:
        calc_ramp_rt_nm_with_tit = org_file[1]
        defl_v_rt_with_tit = org_file[3]

    calc_ramp_ex_nm = calc_ramp_ex_nm_with_tit[1:]
    calc_ramp_rt_nm = calc_ramp_rt_nm_with_tit[1:]
    defl_v_ex = defl_v_ex_with_tit[1:]
    defl_v_rt = defl_v_rt_with_tit[1:]
    
    ramp_ex, ramp_rt, defl_ex, defl_rt = [],[],[],[]
    
    for i in calc_ramp_ex_nm:
        ramp_ex.append(float(i))
     
    for i in calc_ramp_rt_nm:
        ramp_rt.append(float(i))
    
    for i in defl_v_ex:
        defl_ex.append(float(i))
    
    for i in defl_v_rt:
        defl_rt.append(float(i))
    
    #reverse ramp_rt and defl_ex
    
    ramp_rt.reverse()
    defl_ex.reverse()
    
    #give the short columns some ' ' just for letting them have the same length as
    #the long ones so we can output them
    
    length_long = len(ramp_rt)
    length_short = len(ramp_ex)
    if length_long - length_short != 0:
        for i in range(length_long - length_short):
            ramp_ex.append(' ')
            defl_ex.append(' ')
    
    l = len(ramp_ex)
    header = 'Calc_Ramp_Ex_nm '+"\t"
    header2 = header+'Defl_V_Ex '+"\t"
    header3 = header2+'Calc_Ramp_Rt_nm '+"\t"+'Defl_V_Rt'
    
    with open(out_file, "w") as out_file_handle:
        out_file_handle.write(header3)
        out_file_handle.write("\n")
    
        for i in range(l):
            part1 = str(ramp_ex[i])+" \t"
            part2 = str(defl_ex[i])+" \t"
            part3 = str(ramp_rt[i])+" \t"+ str(defl_rt[i])
            out_line = part1+part2+part3
            out_file_handle.write(out_line)
            out_file_handle.write("\n")
    
print "Processed {}".format(os.path.basename(data_directory))
