#!/usr/bin/env python


# Name:		ecoli_serotyper.py
# Date:		20-04-2018
# Licence:	GNU General Public License v3.0 (copy provided in directory)
# Author:	Tom van Wijk - RIVM Bilthoven
# Contact:	tom_van_wijk@hotmail.com / tom.van.wijk@rivm.nl

############################## DESCRIPTION ##############################

# Script for in silico serotyping of e. Coli.

############################## REQUIREMENTS #############################

# - Linux operating system. This script is developed on Linux Ubuntu
#   16.04, experiences when using different operating systems may vary.
# - python 2.7.x
# - python libraries as listed in the import section
# - ncbi BLAST 2.6.0+

############################# INSTALLATION ##############################

# - Add the location of the ecoli_serotyper.py to you path variable:
#   > export PATH=$PATH:/path/to/ecoli_serotyper.py
#   (it is recommended to add this command to your ~/.bashrc file
# - Create path variable SERO_REF to the reference subdirectory:
#   > export SERO_REF=/path/to/ecoli_serotyper/reference
#   (it is recommended to add this command to your ~/.bashrc file

################################# USAGE #################################

# Start the script with the following command:
# > ecoli_serotyper.py -i <inputfile> -o <outputdir>

# inputfile:		location of input file. This should be a fully
#			assembled ecoli	genome in .fasta/.fsa/.fna/.fa format.

# outputdir:		location of output directory. If none is specified,
#			an output directory will be created in the directory
#			containing the inputfile.


# import python libraries
from argparse import ArgumentParser
import logging
import logging.handlers
import os
import sys
import subprocess
import operator
import random


# Function to parse the command-line arguments
# Returns a namespace with argument keys and values
def parse_arguments(args, log):
	log.info("Parsing command line arguments...")
	parser = ArgumentParser(prog="ecoli_serotyper.py")
	parser.add_argument("-i", "--infile", dest = "input_file",
		action = "store", default = None, type = str,
		help = "Location of input .fasta file (required)",
		required = True)
	parser.add_argument("-o", "--outdir", dest = "output_dir",
		action = "store", default = 'inputfile', type = str,
		help = "Location of output directory (default=inputfile)")
	#TODO: add max cpu thread parameter for BLAST
	return parser.parse_args()


# Function creates logger with handlers for both logfile and console output
# Returns logger
def create_logger(logid):
	# create logger
	log = logging.getLogger()
	log.setLevel(logging.INFO)
	# create file handler
	fh = logging.FileHandler(str(logid)+'_ecoli_serotyper.log')
	fh.setLevel(logging.DEBUG)
	fh.setFormatter(logging.Formatter('%(message)s'))
	log.addHandler(fh)
	# create console handler
	ch = logging.StreamHandler()
	ch.setLevel(logging.INFO)
	ch.setFormatter(logging.Formatter('%(message)s'))
	log.addHandler(ch)
	return log


# Function that parses a blastn output, filteres the hits and returns the best antigen hit
# Input: blast result file, location to database used in blastn and logger
# Returns a string containing the name of the antigen variant or if not available: 'NA'
def parse_blastn_output(blast_results, database, log):
	# Create list for individual blast hits
	all_blast_hits = []
	filtered_blast_hits = []
	result = "NA"
	blastn_outfmt6_header = "id:\tquery seq:\treference seq:\t% identity:\talignment length:\tmismatches:\tgap opens:\tq start:\tq end:\ts start:\ts end:\te-value:\tscore:"
	with open(blast_results,  "r") as blast_results_file:
		for line in blast_results_file:
			all_blast_hits.append(line.replace("\n", "").replace("\r", ""))
	blast_results_file.close()
	if len(all_blast_hits) < 1:
		log.info("0 hits found with identity > 85 %...")
	else:
		log.info(str(len(all_blast_hits))+" hits found with identity > 85 %:\n"+blastn_outfmt6_header)
		hit_ids = {}
		counter = 1
		# coupling blast hits to an id and logging hits
		for hit in all_blast_hits:
			hit_ids[hit] = str(counter)
			counter += 1
			log.info(hit_ids.get(hit)+"\t"+hit)
		# calculating coverage and filter hits
		log.info("\nCalculating coverage of alignments...\n\nid:\tgene name:\tgene size:\talignment size:\t% coverage:\tstatus:")
		for hit in all_blast_hits:
			hit_properties = hit.split("\t")
			reference_gene_size = int(subprocess.check_output(('blastdbcmd -db %s -entry %s -outfmt "%s"'
				% (database, hit_properties[1], "%l")), shell=True))
			coverage = float(hit_properties[3])/reference_gene_size*100
			if coverage < 60.0:
				log.info(hit_ids.get(hit)+"\t"+hit_properties[1]+"\t"+str(reference_gene_size)+"\t"+
						 hit_properties[3]+"\t"+str(coverage)+"\tdiscarded (due to low coverage)")
			else:
				log.info(hit_ids.get(hit)+"\t"+hit_properties[1]+"\t"+str(reference_gene_size)+"\t"+
						 hit_properties[3]+"\t"+str(coverage)+"\taccepted")
				filtered_blast_hits.append(hit)
		# dealing with filtered blast hits
		if len(filtered_blast_hits) < 1:
			log.info("\nNo hit found with identity > 85 % and coverage > 60 %...")
		elif len(filtered_blast_hits) == 1:
			log.info("\nExactly 1 hit found with identity > 85 % and coverage > 60 %:\n"+blastn_outfmt6_header)
			log.info(hit_ids.get(filtered_blast_hits[0])+"\t"+filtered_blast_hits[0])
			result = filtered_blast_hits[0].split("\t")[1].split("_")[3]+" ("+filtered_blast_hits[0].split("\t")[1].split("_")[0]+")"
		else:
			log.info("\n"+str(len(filtered_blast_hits))+" hits found with identity > 85 % and coverage > 60 %:\n"+blastn_outfmt6_header)
			for hit in filtered_blast_hits:
				log.info(hit_ids.get(hit)+hit)
			log.info("\nselecting best hit based on blast score:\n"+blastn_outfmt6_header)
			hit_scores = {}
			for hit in filtered_blast_hits:
				hit_scores[hit] = int(hit.split("\t")[11])
			best_hit = max(hit_scores.iteritems(), key=operator.itemgetter(1))[0]
			log.info(hit_ids.get(best_hit)+"\t"+best_hit)
			result = (best_hit.split("\t")[1].split("_")[3]+" ("+best_hit.split("\t")[1].split("_")[0]+")")
	return result


# Function closes logger handlers
def close_logger(log):
	for handler in log.handlers:
		handler.close()
		log.removeFilter(handler)


# MAIN function
def main():
	# create logger
	logid = random.randint(99999, 9999999)
	log = create_logger(logid)
	# parse command line arguments
	args = parse_arguments(sys.argv, log)
	# TODO: add function to validate parameters, data ect.
	# creating output directory
	if args.output_dir == 'inputfile':
		outdir = os.path.abspath(args.input_file).replace(".fasta", "").replace(".fna", "").replace(".fsa", "").replace(".fa", "")+"_ecoli_serotyper_output"
	else:
		outdir = os.path.abspath(args.output_dir)
	log.info("Creating output directory: "+outdir)
	os.system("mkdir -p "+outdir)
	# blasting target genome to H and O databases
	for type in ["H_type", "O_type"]:
		log.info("________________________________________________________________________________\n")
		log.info("Blasting query to: '%s'...\n" % (type))
		os.system("blastn -query %s -db %s -perc_identity 85 -outfmt 6 -num_threads 4 | sort -u -k1,1 --merge > %s"
		% (args.input_file, os.environ['SERO_REF']+"/"+type.replace("type", "database")+"/"+type, outdir+"/blastn_results_"+type+".txt"))
		# parse and filter blastn output
		antigen = parse_blastn_output(outdir+"/blastn_results_"+type+".txt", os.environ['SERO_REF']+"/"+type.replace("type", "database")+"/"+type, log)
		log.info("\n'"+type.replace("_", "-")+"':\t"+antigen)
	# close logger handlers
	log.info("\nClosing logger and finalising ecoli_serotyper.py")
	close_logger(log)
	# move logfile to output directory
	os.system("mv "+str(logid)+"_ecoli_serotyper.log "+outdir+"/ecoli_serotyper.log")


main()
