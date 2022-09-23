# fdafm version 2.0
This software enables a user with basic knowledge in command line tools to analyze atomic force microscopy (Multimode NanoScrope IIId AFM Bruker) force-distance curve raw data to extrapolate adhesive force, adhesive energy, rupture length, repulsive energy, repulsive distance and sample indentation length.

# Contact
If you have any questions, please feel free to reach out to Yue Zhang (yuezhang@jhu.edu)

# Implementation
All the scripts were written in python 2.7.16. 

# Notes
If you are using the windows system, please make sure to include this line in front of all scripts using matplotlib:
matplotlib.use('Agg')

# Inventory
1. library:

	This directory contains all of the AFM data analysis modules implemented in Python
2. test_data:

	This directory contains some exemplary input files. It is recommended to run the whole pipeline with these test data step-by-step as a test run to check if all modules are running properly
3. test_run_result_example:

	The exemplary output of fdafm, which was produced by running the pipeline described down below 
4. all_commands.sh
	
	This bash script records all commands in the data analysis pipeline described under section #usage. If you are running your data, you will need to run the first two steps one by one in the pipeline to calculate your own probe sensitivity values first. After that, you may revise all_commands.sh with your own sensitivity values and probe spring constant before running the rest of the commands (I have provided instructions in all_commands.sh)
	
# Installation
Several libraries are required. Install the packages by running:

pip install matplotlib pandas numpy scipy sys os math seaborn

# Usage
1. data preprocessing
	1. raw data 
	
	The raw data output by Multimode NanoScrope IIId AFM (Bruker) should be imported to software NanoScope Analysis (32-bit, version 1.5) to convert into ASCII format. In specific, under "ASCII Export" interface, choose "Native" as Units and "Extend", "Retract", and "Ramp" as Force Curve Options. By doing so, the output file now is a tab-delimited .txt file having four columns in order -- "Calc_Ramp_Ex_nm", "Cal_Ramp_Rt_nm", "Defl_V_Ex", "Defl_V_Rt". This is the standard input file format.
	
	2. input data preparation

	Currently, the data in the columns of "Cal_Ramp_Rt_nm" and "Defl_V_Ex" are in reversed order. Therefore, the first step is to correct this, run:
	Python afm_original_data_prep.py input_directory output directory/
	
	Example:
	
	cd fdafm
	
	mkdir test_run
	
	cd test_data *Please note that this step is necessary*
	
	python ../library/afm_original_data_prep.py sensitivity_calibration ../test_run/
	
	python ../library/afm_original_data_prep.py sample ../test_run/
	

2. sensitivity calculation

	1. change directory to the output directory in the last step
	
	2. Pass the input data directory to sens_cal.py. This script outputs a .txt file that records the calculated probe sensitivity for both approaching and retraction phases (the unit of both sensitivities is V/nm).
	
	Run: python sens_cal.py input_directory output_directory/

	Example:
	
	cd ../test_run/
	
	python ../library/sens_cal.py sensitivity_calibration_reversed ./

3. retraction curve analysis

	To transform the original deflection-displacement data under the retraction phase into interaction force-separation distance curves, run retract_data_indlen_adhfor_fd_transform.py

	This step produces:
	
	 1. a summary file that records the extrapolated indentation length and adhesive force for each measurement 
	 
	 2. a folder of all the interaction force-separation distance plots. Users should visually check many plots, if not all, to evaluate if the data transformation is satisfactory
	 
	 3. a folder of all the interaction force-separation distance data (.txt files). This folder will be used for downstream analysis
	 
	Run: 
	
	python retract_data_indlen_adhfor_fd_transform.py input_directory output_directory/ probe_extending_sensitivity(V/nm) probe_retracting_sensitivity(V/nm) probe_spring_constant(N/m)

	Example:

	python ../library/retract_data_indlen_adhfor_fd_transform.py sample_reversed ./ 0.041423406 0.04043781 0.3188


4. extending (approaching) curve analysis

	Transform the raw data of the extending curve into interaction force-separation distance curves by running approach_data_fd_transformation.py
	
	 This step produces:
	 
	 1. a folder of all the interaction force-separation distance plots. Users should visually check many plots, if not all, to evaluate if the data transformation is satisfactory
	 
	 2. a folder of all the interaction force-separation distance data (.txt files). This folder will be used for downstream analysis
	 
	Run:
	
	python approach_data_fd_transformation.py input_directory output_directory/ probe_extending_sensitivity probe_spring_constants

	Example:
	
	python ../library/approach_data_fd_transformation.py sample_reversed ./ 0.041423406 0.3188

5. calculate the adhesive energy of all retracting curves (an integration of the approximate area in the fourth quadrant and is above the force-distance curve)

	Pass the folder of force_distance data (produced from step 3.3) to retract_adh_eng.py to calculate the adhesive energy. 

	This step produces:
	
	1. a folder of all interaction force-separation distance plots denoted with the associated adhesive energy.
	
	2. a summary file that documents the adhesive energy of all files in the input directory
	
	Run:
	
	python retract_adh_eng.py input_directory output_directory/

	Example:
	
	python ../library/retract_adh_eng.py sample_reversed_retract_data_force_distance_curve_data retract_adheng/

6. calculate the repulsive energy of all extending data (an integration of the approximate area in the first quadrant and is below the force-distance curve)

	Pass the folder of force_distance data (produced from step 4.3) to approach_rpl_energy.py to calculate the repulsive energy of the extending curves.

	This step produces:
	
	1. a folder of all interaction force-separation distance plots denoted with the associated repulsive energy.
	
	2. a summary file that documents the repulsive energy of all files in the input directory
	
	Run:
	
	python approach_rpl_energy.py input_directory output_directory/

	Example:
	
	python ../library/approach_rpl_energy.py sample_reversed_extending_force_distance_curve_data approach_rpleng/

7. extrapolate the rupture length of all retracting curves 

	This algorithm finds the approximate location where a retraction curve returns to the baseline range from the adhesive region (below the x-axis). Specifically, it outputs the x-axis value of the first point on a force-distance curve with a y-value higher than the lower bound of the baseline region (i.e., the mean of the y-axis value of the user-defined baseline region minus 3 times the standard deviation).  

	Pass the folder of the force_distance data (produced from step 3.3) to retract_ruplen_v2.py to extrapolate the rupture length from retracting data. 

	This step produces:
	
	1. a folder of all interaction force-separation distance plots denoted with the associated rupture length.
	
	2. a summary file that documents the rupture length of all files in the input directory
	
	Run:
	
	python retract_ruplen_v2.py input_directory output_directory/ user-defined baseline region (i.e., the number of data points counting from the end should be considered as the baseline region ; for example, "150" in the following example tells the program that the last 150 points should be considered as the baseline region in each curve)

	Example:
	
	python ../library/retract_ruplen_v2.py sample_reversed_retract_data_force_distance_curve_data retract_ruplen/ 150

8. extrapolate the repulsive distance of all extending curves
	
	This algorithm finds the approximate location where an extending curve returns to the baseline range from the repulsive region (above the x-axis). Specifically, it outputs the x-axis value of the first point on an extending curve with a y-axis value lower than the upper bound of the baseline region (i.e., the mean of the y-axis value of the user-defined baseline region plus 3 times the standard deviation).

	Pass the folder of the force_distance data (produced from step 4.3) to approach_rpl_energy.py to extrapolate the repulsive distance from the extending data.

	This step produces:
	
	1. a folder of all interaction force-separation distance plots denoted with the associated repulsive distance.
	
	2. a summary file that documents the repulsive distance of all files in the input directory	
	
	Run:
	
	python approach_rpllen_v2.py input_directory output_directory/ user-defined baseline region (i.e., the number of data points counting from the end should be considered as the baseline region ; for example, "150" in the following example tells the program that the last 150 points should be considered as the baseline region in each curve)

	Example:
	
	python ../library/approach_rpllen_v2.py sample_reversed_extending_force_distance_curve_data approach_rpllen/ 150

9. merge the summary files output from steps 3 to 8 as a single .txt file with each characteristics as one column 

   Run:
   python ../library/summary.py
