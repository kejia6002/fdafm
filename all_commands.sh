
#To run your own data, disable the section 2 first and run this bash script to obtain probe sensitivity values.

#section 1
mkdir test_run

cd test_data 

python ../library/afm_original_data_prep.py sensitivity_calibration ../test_run/
python ../library/afm_original_data_prep.py sample ../test_run/

cd ../test_run/
python ../library/sens_cal.py sensitivity_calibration_reversed ./

#Disable section 1, modify the required values as instructed down below, and re-run this bash script to obtain the full analysis.

#section 2

#modify the sensitivity values of both approach phase and retract phase here with the one you obtained from the last step, and change the example spring constant value to yours as well. 
#The syntex for this command is 
#python retract_data_indlen_adhfor_fd_transform.py input_directory output_directory/ probe_extending_sensitivity(V/nm) probe_retracting_sensitivity(V/nm) probe_spring_constant(N/m)
python ../library/retract_data_indlen_adhfor_fd_transform.py sample_reversed ./ 0.041423406 0.04043781 0.3188

#modify the sensitivity value of the approach phase and spring constant here as well. 
#The syntex for this command is 
#python approach_data_fd_transformation.py input_directory output_directory/ probe_extending_sensitivity probe_spring_constants
python ../library/approach_data_fd_transformation.py sample_reversed ./ 0.041423406 0.3188


python ../library/retract_adh_eng.py sample_reversed_retract_data_force_distance_curve_data retract_adheng/
python ../library/approach_rpl_energy.py sample_reversed_extending_force_distance_curve_data approach_rpleng/
python ../library/retract_ruplen_v2.py sample_reversed_retract_data_force_distance_curve_data retract_ruplen/ 150
python ../library/approach_rpllen_v2.py sample_reversed_extending_force_distance_curve_data approach_rpllen/ 150
python ../library/summary.py