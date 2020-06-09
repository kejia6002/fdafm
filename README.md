# fdafm version 2.0

Analyzing atomic force microscopy (Multimode NanoScrope IIId AFM Bruker) force-distance curve raw data to extrapolate adhesive force, adhesive energy, rupture length, repulsive energy, repulsive distance and sample indentation length.

#This version of fdafm made several key updates including:
1. implement a more rigorous algorithm to transform original deflection-displacement curved to force-distance curves for both approach and separation phases
2. implement a more rigorous algorithm to calculate the repulsive energy
3. allow users to customize the baseline region when calculate repulsive length and rupture length
4. provided more details regarding how repulsive length and rupture length are calculated
5. provided a bash file named all_commands.sh that includes all commands in the data analysis pipeline to reduce the workload of data analysis procedure

# Contact

If you have any questions, please feel free to reach out to Yue Zhang (yuezhang@jhu.edu)

# Implementation

All the scripts were implemented in python 2.7.16. 

If you are using windows system to run the scripts, please make sure that you have this line in the front for all the scripts using matplotlib:
matplotlib.use('Agg')

# Inventory
1. library:

	all of the python scripts related are included in library
2. test_data:

	some examplary standard input files that one can learn: 1. what a standard input file looks like; 2. how to run it through the pipeline and compare it to the test_run_result_example
3. test_run_result_example:

	the examplary output of fdafm, which was the output from running the pipeline descirbed down below 
4. all_commands.sh
	this is a bash file that included all commands in the data analysis pipeline described under section #usage. For re-running the whole pipeline with the provided test_data as input, you can simply run this file in command line under fd_afm directory, or you can follow the instructions under #usage section to run each command step by step. If you are running your own data, you will need to run the first two steps one by one in the pipeline to obtain your own probe sensitivity values, and revise all_commands.sh with your own sensitivity values and probe spring constant before you run the rest of the bash script (I provided instructions in all_commands.sh)
	
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
	
	python ../library/afm_original_data_prep.py sensitivity_calibration ../test_run/
	
	python ../library/afm_original_data_prep.py sample ../test_run/
	

2.  sensitivity calculation

	1. change directory to the output directory in last step
	
	2. Pass the input data as a folder to sens_cal.py. This script outputs a .txt file (output_directory + input_directory + senscal.txt), which records both extending sensitivity and retracting sensitivity (the unit of both sensitivity is V/nm) of the probe extrapolated by each measurement.
	
	run: python sens_cal.py input_directory output_directory/

	example:
	
	cd ../test_run/
	
	python ../library/sens_cal.py sensitivity_calibration_reversed ./

3.  retraction curve analysis

	to transform the original deflection-displacement raw data recorded during retracting the probe to interaction force-separation distance curve, run retract_data_indlen_adhfor_fd_transform.py

	This script produces:
	
	 1. a summary file that records the indentation length and adhesive force of each measurement 

	 	Please note that although a slight fluctuation of indentation length around zero were observed for measurements on stiff samples (sc) of test_data, that might be resulted from measurement errors (e.g. slight probe sensitivity change potentially due to a variation of laser reflection or interference from environment) or data analysis artifacts (e.g. artifacts from analyzing undulating sensitivity line), the indentation length of soft samples (all samples other than sc, which were biofilm modified coverslips) were significantly higher than the ones of stiff samples, suggesting that indentation length is effective in distinguishing between soft and stiff samples.
	 
	 2. a folder of all the interaction force-separation distance plots for retraction data
	 
	 3. a folder of force_distance data (.txt files) where each file records the separation distance and interaction force for each measurement for downstream analysis
	 
	run: 
	
	python retract_data_indlen_adhfor_fd_transform.py input_directory output_directory/ probe_extending_sensitivity(V/nm) probe_retracting_sensitivity(V/nm) probe_spring_constant(N/m)

	example:

	python ../library/retract_data_indlen_adhfor_fd_transform.py sample_reversed ./ 0.041423406 0.04043781 0.3188


4.  extending curve analysis

	transform the raw data of extending curve to interaction force-separation distance curve by running approach_data_fd_transformation.py
	
	 This script produces:
	 
	 1. a folder of all the interaction force-separation distance plots for extending data
	 
	 2. a folder of force-distance data (.txt files) where each file records the separation distance and interaction force for each measurement for downstream analysis
	 
	run:
	
	python approach_data_fd_transformation.py input_directory output_directory/ probe_extending_sensitivity probe_spring_constants

	example:
	
	python ../library/approach_data_fd_transformation.py sample_reversed ./ 0.041423406 0.3188

5.  analyze the adhesive energy of all retracting data (an integration of the area in the fourth quadrant and above the force distance curve)

	Passing the folder of force_distance data (produced from step 3.3) to retract_adh_eng.py to analyze the adhesive energy from retracting data. 

	This script produces:
	
	1. a folder of all interaction force-separation distance plots denoted with the number of adhesive energy.
	
	2. a summary file that documents adhesive energy of all files in the input_directory
	
	run:
	
	python retract_adh_eng.py input_directory output_directory/

	example:
	
	python ../library/retract_adh_eng.py sample_reversed_retract_data_force_distance_curve_data retract_adheng/

6.  analyze the repulsive energy of all extending data (an integration of the area in the first quadrant that below the force distance curve)

	Passing the folder of force_distance data (produced from step 4.3) to approach_rpl_energy.py to analyze the repulsive energy from the extending data.

	This script produces:
	
	1. a folder of all interaction force-separation distance plots denoted with the number of repulsive energy.
	
	2. a summary file that documents repulsive energy of all files in the input_directory
	
	run:
	
	python approach_rpl_energy.py input_directory output_directory/

	example:
	
	python ../library/approach_rpl_energy.py sample_reversed_extending_force_distance_curve_data approach_rpleng/

7.  analyze the rupture length of all retracting curves 

	This algorithm finds and outputs the x-value of the first point in a force-distance curve that has y-value inside the range of baseline, that was defined as the mean of y-value of the user-defined baseline region minus 3 times of standard deviation of the baseline region y-value.  

	Passing the folder of force_distance data (produced from step 3.3) to retract_ruplen_v2.py to analyze the rupture length from retracting data. 

	This script produces:
	
	1. a folder of all interaction force-separation distance plots denoted with the number of rupture length.
	
	2. a summary file that documents rupture length of all files in the input_directory
	
	run:
	
	python retract_ruplen_v2.py input_directory output_directory/ 150

	example:
	
	python ../library/retract_ruplen_v2.py sample_reversed_retract_data_force_distance_curve_data retract_ruplen/ 150

8.  analyze the repulsive distance of all extending curves
	
	This algorithm finds and outputs the x-value of the first point in a force-distance curve that has y-value inside the range of baseline, that was defined as the mean of y-value of the user-defined baseline region plus 3 times of standard deviation of the baseline region y-value.

	Passing the folder of force_distance data (produced from step 4.3) to approach_rpl_energy.py to analyze the repulsive distance from the extending data.

	This script produces:
	
	1. a folder of all interaction force-separation distance plots denoted with the number of repulsive distance.
	
	2. a summary file that documents repulsive distance of all files in the input_directory	
	
	run:
	
	python approach_rpllen_v2.py input_directory output_directory/ 150

	example:
	
	python ../library/approach_rpllen_v2.py sample_reversed_extending_force_distance_curve_data approach_rpllen/ 150

9. merge the summary files output from step 3 to 8 together as a tab-deliminated txt file

   run:
   python ../library/summary.py



 







