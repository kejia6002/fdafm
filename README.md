# fdafm

Analyzing atomic force microscopy (Multimode NanoScrope IIId AFM Bruker) force-distance curve raw data to extrapolate adhesive force, adhesive energy, rupture length, repulsive energy, repulsive distance and sample indentation length.

# Inventory
1. library:
	all of the python scripts related are included in library
2. test_data:
	some examplary standard input files that one can learn: 1. what a standard input file looks like; 2. run it through the pipeline and compare it to the test_run_result_example
3. test_run_result_example:
	the examplary output of fdafm 
	
# Installation

The algorithms were written in Python 2.7. Several packages might be required. Install the packages by running:

pip install matplotlib
pip install pandas
pip install numpy
pip install scipy
pip install sys
pip install os
pip install math
pip install seaborn

#Usage

1.  data prep
	1. raw data 
	The raw data output by Multimode NanoScrope IIId AFM (Bruker) were imported to software NanoScope Analysis (32 bit, version 1.5) in order to convert the raw data file to ASCII format. Under "ASCII Export" interface, choose "Native" as Units and  "Extend", "Retract" and "Ramp" as Force Curve Options. By doing so, the output file now is a tab-deliminated .txt file with four columns in order -- "Calc_Ramp_Ex_nm", "Cal_Ramp_Rt_nm", "Defl_V_Ex", "Defl_V_Rt", which is the standard input file of fdafm.
	2. input data prep
	Put the standard input files in a folder and change directory to the folder contains this folder.

	The columns of "Cal_Ramp_Rt_nm" and "Defl_V_Ex" are in reversed order. To make the order right, run:
	python afm_original_data_prep.py input_directory output directory/
	
	example:
	cd fdafm
	mkdir test_run
	cd test_data *please note that this step is necessary*
	test_data$ python ../library/afm_original_data_prep.py sensitivity_calibration ../test_run/
	test_data$ python ../library/afm_original_data_prep.py sample ../test_run/
	

2.  sensitivity calculation
	1. change directory to the output directory in last step
	2. Pass the input data as a folder to sens_cal.py. This script outputs a .txt file (output_directory + input_directory + senscal.txt), which records both extending sensitivity and retracting sensitivity (the unit of both sensitivity is V/nm) of the probe extrapolated by each measurement.
	run: python sens_cal.py input_directory output_directory

	example:
	test_data$ cd ../test_run/
	test_run$ python ../library/sens_cal.py sensitivity_calibration_reversed .

3.  retraction curve analysis
	to transform the original deflection-displacement raw data recorded during retracting the probe to interaction force-separation distance curve, run retract_data_indlen_adhfor_fd_transform.py

	This script produces:
	 1. a summary file that records the indentation length and adhesive force of each measurement
	 2. a folder of all the interaction force-separation distance plots for retraction data
	 3. a folder of force_distance data (.txt files) where each file records the separation distance and interaction force for each measurement for downstream analysis
	run: 
	python retract_data_indlen_adhfor_fd_transform.py input_directory output_directory probe_extending_sensitivity(V/nm) probe_retracting_sensitivity(V/nm) probe_spring_constant(N/m)

	example:

	test_run$ python ../library/retract_data_indlen_adhfor_fd_transform.py sample_reversed ./ 0.04 0.04 0.318


4.  extending curve analysis
	transform the raw data of extending curve to interaction force-separation distance curve by running approach_data_fd_transformation.py
	 This script produces:
	 1. a folder of all the interaction force-separation distance plots for extending data
	 2. a folder of force-distance data (.txt files) where each file records the separation distance and interaction force for each measurement for downstream analysis
	run:
	python approach_data_fd_transformation.py input_directory output_directory probe_extending_sensitivity probe_spring_constants

	example:
	test_run$ python ../library/approach_data_fd_transformation.py sample_reversed ./ 0.04 0.3188

5.  analyze the adhesive energy of all retracting data 
	Passing the folder of force_distance data (produced from step 3.3) to retract_adh_eng.py to analyze the adhesive energy from retracting data. 

	This script produces:
	1. a folder of all interaction force-separation distance plots denoted with the number of adhesive energy.
	2. a summary file that documents adhesive energy of all files in the input_directory
	run:
	python retract_adh_eng.py input_directory output_directory

	example:
	python ../library/retract_adh_eng.py sample_reversed_retract_data_force_distance_curve_data retract_adheng/

6.  analyze the repulsive energy of all extending data
	Passing the folder of force_distance data (produced from step 4.3) to approach_rpl_energy.py to analyze the repulsive energy from the extending data.

	This script produces:
	1. a folder of all interaction force-separation distance plots denoted with the number of repulsive energy.
	2. a summary file that documents repulsive energy of all files in the input_directory
	run:
	python approach_rpl_energy.py input_directory output_directory

	example:
	ub/test_run$ python ../library/approach_rpl_energy.py sample_reversed_extending_force_distance_curve_data approach_rpleng/

7.  analyze the rupture length of all retracting curves
	Passing the folder of force_distance data (produced from step 3.3) to retract_ruplen_v2.py to analyze the rupture length from retracting data. 

	This script produces:
	1. a folder of all interaction force-separation distance plots denoted with the number of rupture length.
	2. a summary file that documents rupture length of all files in the input_directory
	run:
	python retract_ruplen_v2.py input_directory output_directory

	example:
	test_run$ python ../library/retract_ruplen_v2.py sample_reversed_retract_data_force_distance_curve_data retract_ruplen/

8.  analyze the repulsive distance of all extending curves
	Passing the folder of force_distance data (produced from step 4.3) to approach_rpl_energy.py to analyze the repulsive distance from the extending data.

	This script produces:
	1. a folder of all interaction force-separation distance plots denoted with the number of repulsive distance.
	2. a summary file that documents repulsive distance of all files in the input_directory	
	run:
	python approach_rpllen_v2.py input_directory output_directory

	example:
	test_run$ python ../library/approach_rpllen_v2.py sample_reversed_extending_force_distance_curve_data approach_rpllen/





 







