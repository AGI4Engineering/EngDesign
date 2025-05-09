#########################################
#########################################
# Testbench Setup Script
# For Student Use
#
# UIUC, ECE483
# Spring 2023
#
# Andy Ng
# Jan 16, 2023
#
# Updated Spring 2025
# 
# Luke Granger
# Feb 21, 2025
#########################################
#########################################

import os
import fileinput
import csv

wd = os.getcwd() # get current working directory
wd_strs = wd.split('/', -1) # split path string

USERNAME = wd_strs[2] # get username
LIB_NAME = 'ece483_sp25_AG' #wd_strs[-2] # get library name
CELL_NAME = wd_strs[-1] # get testbench name

PARENT_DIR = wd + '/'
NETLIST_DIR = (
	PARENT_DIR + 'maestro/results/maestro/ExplorerRun.0/1/'
	+ LIB_NAME + '_' + CELL_NAME + '_1/' + 'netlist/'
	)
DUT_NETLIST_DIR = PARENT_DIR + 'dut_netlist/'

NETLIST_PATH =  NETLIST_DIR + 'netlist' # path to netlist file
INPUT_PATH = NETLIST_DIR + 'input.scs' # path to input.scs file

DUT_TARGET = '// DUT GOES HERE' # to be replaced in input.scs and netlist files
NETIDS_TARGET = '; NETLIST_IDS'
NAMES_TARGET = '; NAMES'
LIB_TARGET = '; LIB_NAME'
TB_TARGET = '; TB_NAME'
USERNAME_TARGET = '; USERNAME'

# Path to the pins.txt file (update this if needed)
PINS_PATH = PARENT_DIR + 'pins.txt'

# Read the pin order from pins.txt
with open(PINS_PATH, 'r') as pin_file:
    pin_order = pin_file.readline().strip().split()

# Check if the pin_order list has exactly 5 elements (as expected)
#if len(pin_order) != 5:
#    raise ValueError("The pin order file should have exactly 5 pins")

# roster = open(PARENT_DIR + 'roster_' + CELL_NAME + '.csv', 'r')

# # creating dictreader object
# file = csv.DictReader(roster)

# creating empty list
netids = [USERNAME]
netids_str = '"' + USERNAME + '"'

# # iterating over each row and append
# # values to empty list
# for col in file:
# 	curr_id = col['Net ID']
# 	netids.append(curr_id)
# 	netids_str += '"' + curr_id + '"' + ' '
# netids_str += ')'

# generates a project-specific "run.mp<i>_<CELL_NAME>.ocn" OCEAN script
with open(PARENT_DIR + 'run_master_' + CELL_NAME + '.ocn', 'r') as ocean_in, open(PARENT_DIR + 'run_' + CELL_NAME + '.ocn', 'w') as ocean_out:
    for line in ocean_in:
        if line.strip() == NETIDS_TARGET:
            ocean_out.write('NETLIST_IDS = list( ' + netids_str + ')\n')
        elif line.strip() == LIB_TARGET:
            ocean_out.write('LIB_NAME = "' + LIB_NAME + '"\n')
        elif line.strip() == TB_TARGET:
            ocean_out.write('TB_NAME = "' + CELL_NAME + '"\n')
        elif line.strip() == USERNAME_TARGET:
            ocean_out.write('USERNAME = "' + USERNAME + '"\n')
        else:
            ocean_out.write(line)

cmd = 'mv -f ' + PARENT_DIR + 'run_' + CELL_NAME + '.ocn ~/ece483.work/'
os.system(cmd)

# clean up old netlist_<netID> directories
cmd = (
    'rm -r -f ' + PARENT_DIR + 'maestro/results/maestro/ExplorerRun.0/1/'
    + LIB_NAME + '_' + CELL_NAME + '_1/netlist_*'
    )
os.system(cmd)

for n in netids:
    DUT_NETLIST_PATH = DUT_NETLIST_DIR + 'netlist_' + n

    # store DUT netlist if it exists
    if os.path.exists(DUT_NETLIST_PATH):
        
        file_n = open(DUT_NETLIST_PATH, 'r')
        lines = file_n.readlines()
        lines = lines[:-4]  # remove DUT top level definition
        dut_netlist = ''
        pins_updated = 0
        # Loop through the lines of the netlist and update the subcircuit definition
        for line in lines:# Update the pin order in the subcircuit definition
            if pins_updated == 0:	
                if line.strip().startswith("subckt"):
                    line_parts = line.strip().split()
                    line_parts[2:] = pin_order  # Replace the old pin order with the new one
                    line = " ".join(line_parts) + "\n"
                    pins_updated = 1
            dut_netlist += line
        file_n.close()

        curr_path = (
            PARENT_DIR + 'maestro/results/maestro/ExplorerRun.0/1/'
            + LIB_NAME + '_' + CELL_NAME + '_1/' + 'netlist_' + n + '/'
            )

        # create new netlist directory if it doesn't exist
        if not os.path.exists(curr_path):
            os.mkdir(curr_path)

        # copy contents of netlist directory to netlist_<netID> directory
        cmd = 'cp -r ' + NETLIST_DIR + '/* ' + curr_path
        os.system(cmd)

        # insert updated DUT netlist into new input.scs and netlist files
        with open(INPUT_PATH, 'r') as input_file, open(curr_path + '/input.scs', 'w') as output_file:
            for line in input_file:
                if line.strip() == DUT_TARGET:
                    output_file.write(dut_netlist + '\n')
                else:
                    output_file.write(line)

        with open(NETLIST_PATH, 'r') as input_file, open(curr_path + '/netlist', 'w') as output_file:
            for line in input_file:
                if line.strip() == DUT_TARGET:
                    output_file.write(dut_netlist + '\n')
                else:
                    output_file.write(line)




