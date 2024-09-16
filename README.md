# In Silico E. Coli serotyping tool

**Licence:	GNU General Public License v3.0 (copy provided in directory)**<br />
Author:		Tom van Wijk<br />
Contact:	tom_van_wijk@hotmail.com<br />

#### DESCRIPTION

Blast-based tool for in silico serotyping of e. coli assemblies.
The reference database used for typing is a blast database created using the database of serotypefinder from CGE (Center for Genomic Epidemiology).
When using this tool, please also cite the authors of that database as:<br /><br />
*Joensen, K. G., A. M. Tetzschner, A. Iguchi, F. M. Aarestrup, and F. Scheutz. 2015. Rapid and easy in silico serotyping of Escherichia coli using whole genome sequencing (WGS) data. J.Clin.Microbiol. 53(8):2410-2426. doi:JCM.00008-15 [pii];10.1128/JCM.00008-15 [doi]*

#### DOCKER
You may execute this program in a docker container using the provided `Dockerfile`. In this case, follow these instructions, otherwise continue to the next section.

*The docker image is based on the `multi_serotyper.py` therefore it can process one or more FASTA files at the same time*

Instructions to build and run the docker container:
-	Clone the ecoli_serotyper repository to the desired location on your system.<br />
	`git clone https://github.com/tom-van-wijk/ecoli_serotyper.git`
-	Build the docker image running the following command inside the location in which you downloaded the repo. This may take a short while and requires internet access.<br />
	`docker build -t serotyper .`
-	Run the image, you pass the input FASTA files with the `-v` argument. For that you must put all your input FASTA files inside a folder which will be the first part of the `-v` argument, and then keep the second part of the argument as is: `:/app/data`. When finished you'll see the console output of the `multi_serotyper.py` program.<br/>
	`docker run -ti -v /input_data/fasta_files:/app/data serotyper:latest`

#### REQUIREMENTS

-	Linux operating system. This software is developed on Linux Ubuntu v16.04<br />
	**WARNING: Experiences when using different operating systems may vary.**
-	python v2.7.x
-	python libraries as listed in the import section of ecoli_serotyper.py
-	Blast v2.6.0+
-	The reference directory supplied with this repository contaning the H-database and O-database

#### INSTALLATION

-	Clone the ecoli_serotyper repository to the desired location on your system.<br />
	`git clone https://github.com/tom-van-wijk/ecoli_serotyper.git`
-	Add the location of the ecoli_serotyper directory to the PATH variable:<br />
	`export PATH=$PATH:/path/to/ecoli_serotyper.py`<br />
	(It is recommended to add this command to your ~/.bashrc file)
-	Create path variable ECOLI_REF to the reference subdirectory:<br />
	`export SERO_REF=/path/to/ecoli_serotyper/reference`<br />
	(It is recommended to add this command to your ~/.bashrc file)

#### USAGE

Start ecoli_serotyper.py with the following command:

`ecoli_serotyper.py -i 'inputfile' -o 'outputdir'`

-	**'inputfile':**	location of input file.<br />
			This should be a fully assembled genome in .fasta/.fsa/.fna/.fa format.

-	**'outputdir':**	location of output directory.<br />
			If none is specified, an output directory will be created in the directory containing the inputfile.

## Multi Serotyper

Added in this repository is `multi_serotyper.py`.
This script allows for large batches of data to be typed with a single command.
When the installation of ecoli_serotyper is complete, no additional dependencies have to be installed and no additional steps have to be taken,
you are ready to go.<br /><br />
This script will create an output directory with a subdirectory for each genome containing the ecoli_serotyper.py output.
Additionally `multy_serotyper_output.txt` will be created with an overview of all typed genomes.

#### USAGE

Start multi_serotyper with the following command:

`multi_serotyper.py -i 'inputdir' -o 'outputdir'`

-	**'inputdir':**	location of input directory.<br />
			This should only contain fully assembled genomes in .fasta/.fsa/.fna/.fa format.

-	**'outputdir':**	location of output directory.<br />
			If none is specified, an output directory will be created in input directory.
