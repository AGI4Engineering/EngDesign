#!/bin/bash

# Prompt user for school year
#echo "Enter the class semester (e.g., sp25 for spring 2025)"
#read class_sem

# Prompt user for MP number
echo "Enter the MP number (e.g., mp1, mp2, etc.):"
mp_number="${1:-mp1}"

# Load Python3 module
module load python3

# Navigate to the appropriate directory based on the input
#cd ~/cadence/simulation/ece483_${class_sem}_AG/tb_${mp_number}
cd ~/cadence/simulation/ece483_sp25_AG/tb_${mp_number}

echo "Updating netlist..."

# Run the Python script
python3 update_dut_student.py

# Inform the user
echo -e "\nNetlist Updated for ${mp_number}"

# Load ece483 module to run virtuoso
module load ece483

cd ~/ece483.work

# Define the destination log file path
LOG_DIR=~/cadence/simulation/ece483_sp25_AG/tb_${mp_number}
LOG_FILE="$LOG_DIR/CDS_${mp_number}.log"

echo -e "\nStarting Cadence and running autograder for ${mp_number}\n"

# Get the timestamp before running Virtuoso
START_TIME=$(date +%s)

# Run Virtuoso
virtuoso -replay "$LOG_DIR/autograde.tcl"

# Wait for Virtuoso to complete
wait

# Find the latest CDS log file after Virtuoso runs
LATEST_LOG=$(ls -t ~/CDS.log* 2>/dev/null | head -n 1)

# Move the correct log file to the desired location
if [ -n "$LATEST_LOG" ]; then
    mv "$LATEST_LOG" "$LOG_FILE"
    echo "Virtuoso log saved as $LOG_FILE"
else
    echo "Warning: No CDS log file found!"
fi

echo -e "\n${mp_number} autograding complete!\nSee results in $LOG_DIR/spec_data_tb_${mp_number}.csv\n\n"
echo -e "The Cadence log file can be found at $LOG_FILE if there are any irregularities.\n"

