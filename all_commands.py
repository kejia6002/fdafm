
import os
import subprocess

def run_command(command):
    result = subprocess.run(command, shell=True)
    if result.returncode != 0:
        print(f"Error running command: {command}")
    return result.returncode

# Section 1: Create directories and run initial processing scripts
os.makedirs("test_run", exist_ok=True)
os.chdir("test_data")

run_command("python ../library/afm_original_data_prep.py sensitivity_calibration ../test_run/")
run_command("python ../library/afm_original_data_prep.py sample ../test_run/")

os.chdir("../test_run/")
run_command("python ../library/sens_cal.py sensitivity_calibration_reversed ./")

# Section 2: Modify sensitivity values and run further analysis scripts
# Modify the values below as per your requirements before running this section
probe_extending_sensitivity = 0.041423406
probe_retracting_sensitivity = 0.04043781
probe_spring_constant = 0.3188

run_command(f"python ../library/retract_data_indlen_adhfor_fd_transform.py sample_reversed ./ {probe_extending_sensitivity} {probe_retracting_sensitivity} {probe_spring_constant}")
run_command(f"python ../library/approach_data_fd_transformation.py sample_reversed ./ {probe_extending_sensitivity} {probe_spring_constant}")
run_command("python ../library/retract_adh_eng.py sample_reversed_retract_data_force_distance_curve_data retract_adheng/")
run_command("python ../library/approach_rpl_energy.py sample_reversed_extending_force_distance_curve_data approach_rpleng/")
run_command("python ../library/retract_ruplen_v2.py sample_reversed_retract_data_force_distance_curve_data retract_ruplen/ 150")
run_command("python ../library/approach_rpllen_v2.py sample_reversed_extending_force_distance_curve_data approach_rpllen/ 150")
run_command("python ../library/summary.py")
