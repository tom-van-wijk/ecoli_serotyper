#!/usr/bin/env python


# Name:		multi_serotyper.py
# Date:		23-03-2018
# Licence:	GNU General Public License v3.0 (copy provided in directory)
# Author:	Tom van Wijk - RIVM Bilthoven
# Contact:	tom_van_wijk@hotmail.com / tom.van.wijk@rivm.nl

############################## DESCRIPTION ##############################

# Script for performing automated serotyping on larger datasets using
# ecoli_serotyper.py

############################## REQUIREMENTS #############################

# - Linux operating system. This script is developed on Linux Ubuntu
#   16.04, experiences when using different operating systems may vary.
# - python 2.7.x
# - python libraries as listed in the import section
# - ncbi BLAST 2.6.0+
# - ecoli_serotyper.py and it's dependencies

############################# INSTALLATION ##############################

# - Add the location of the multi_serotyper.py to you path variable:
#   > export PATH=$PATH:/path/to/multi_serotyper.py
#   (it is recommended to add this command to your ~/.bashrc file

################################# USAGE #################################

# Start the script with the following command:
# > multi_ES.py -i <inputdir> -o <outputdir>

# inputfile:		location of input directory. Should contain
#			assembled ecoli	genomes in .fasta/.fsa format.

# outputdir:		location of output directory. If none is specified,
#			an output directory will be created in the directory
#			containing the inputfile.


# import python libraries
from argparse import ArgumentParser
import logging
import logging.handlers
import os
import sys


# Function to parse the command-line arguments
# Returns a namespace with argument keys and values
def parse_arguments(args, log):
	log.info("Parsing command line arguments...")
	parser = ArgumentParser(prog="ecoli_serotyper.py")
	parser.add_argument("-i", "--indir", dest = "input_dir",
		action = "store", default = None, type = str,
		help = "Location of input directory (required)",
		required = True)
	parser.add_argument("-o", "--outdir", dest = "output_dir",
		action = "store", default = 'inputdir', type = str,
		help = "Location of output directory (default=inputfile)")
	#TODO: add max cpu option
	return parser.parse_args()


# Function creates logger with handlers for both logfile and console output
# Returns logger
def create_logger():
	# create logger
	log = logging.getLogger()
	log.setLevel(logging.INFO)
	# create file handler
	fh = logging.FileHandler('multi_serotyper.log')
	fh.setLevel(logging.DEBUG)
	fh.setFormatter(logging.Formatter('%(message)s'))
	log.addHandler(fh)
	# create console handler
	ch = logging.StreamHandler()
	ch.setLevel(logging.INFO)
	ch.setFormatter(logging.Formatter('%(message)s'))
	log.addHandler(ch)
	return log


# Function creates a list of files or directories in <inputdir>
# on the specified directory depth
def list_directory(input_dir, obj_type, depth):
	dir_depth = 1
	for root, dirs, files in os.walk(input_dir):
		if dir_depth == depth:
			if obj_type ==  'files':
				return files
			elif obj_type == 'dirs':
				return dirs
		dir_depth += 1


# Function parses logfile of ecoli_serotyper.py and extracts H-type and O-type
# Input: filepath to logfile
# output: H and O types as string
def parse_logfile(filepath):
	H = "NA"
	O = "NA"
	with open(filepath,  "r") as logfile:
		for line in logfile:
			if line.startswith("'H-type':\t"):
				H = line.split("\t")[1].replace("\n", "").replace("\r", "")
			elif line.startswith("'O-type':\t"):
				O = line.split("\t")[1].replace("\n", "").replace("\r", "")
	logfile.close()
	return H, O

# Function closes logger handlers
def close_logger(log):
	for handler in log.handlers:
		handler.close()
		log.removeFilter(handler)


# MAIN function
def main():
	# create logger
	log = create_logger()
	# parse command line arguments
	args = parse_arguments(sys.argv, log)
	# TODO: check parameters, indir ect.
	# creating output directory
	if args.output_dir == 'inputdir':
		outdir = os.path.dirname(os.path.abspath(args.input_dir))+"/"+args.input_dir+"/multi_serotyper_output"
	else:
		outdir = os.path.abspath(args.output_dir)
	log.info("Creating output directory: "+outdir)
	os.system("mkdir "+outdir)
	with open(outdir+"/multi_serotyper_output.txt",  "w") as outfile:
		outfile.write("File:\tH-type:\tO-type:")
		# iterating over .fasta/.fsa files in input directory:
		for file in list_directory(args.input_dir, 'files', 1):
			if file.endswith(".fasta") or file.endswith(".fsa"):
				path = os.path.dirname(os.path.abspath(args.input_dir))+"/"+args.input_dir+file
				# run the ecoli_serotyper.py
				log.info("\nstarting ecoli.serotyper for file:\n"+path)
				os.system("ecoli_serotyper.py -i "+path)
				# get the H- and O- type from the logfile and write to output file
				H, O = parse_logfile(path.replace(".fasta", "_ecoli_serotyper_output/ecoli_serotyper.log"))
				outfile.write("\n"+file+"\t"+H+"\t"+O)
				# move ecoli_serotyper_output dir to multi_serotyper_output/
				os.system("mv "+path.replace(".fasta", "_ecoli_serotyper_output")+" "+outdir+"/")
	outfile.close()	
	# close logger handlers
	log.info("\nClosing logger and finalising multi_serotyper.py")
	close_logger(log)
	# move logfile and outputfile to output directory
	os.system("mv multi_serotyper.log "+outdir+"/")
	#os.system("mv multi_serotyper_output.txt "+outdir+"/")


main()
