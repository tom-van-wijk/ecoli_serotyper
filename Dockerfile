FROM python:2

ARG INPUT_FILE
WORKDIR /app

#Copy python scripts
COPY ecoli_serotyper.py .
COPY multi_serotyper.py .
COPY /reference ./reference

#Install wget to download BLAST dependency
RUN apt-get update
RUN apt-get install -y wget

#Download and install BLAST
RUN wget -q https://ftp.ncbi.nlm.nih.gov/blast/executables/blast+/LATEST/ncbi-blast-2.13.0+-x64-linux.tar.gz
RUN tar zxpf ncbi-blast-2.13.0+-x64-linux.tar.gz
RUN rm -r ncbi-blast-2.13.0+-x64-linux.tar.gz
ENV PATH=$PATH:ncbi-blast-2.13.0+/bin

#Setup BLAST DB
RUN mkdir blastdb
ENV BLASTDB=blastdb
RUN perl ncbi-blast-2.13.0+/bin/update_blastdb.pl --passive --decompress 16S_ribosomal_RNA

#Setup Serotyper
ENV PATH=$PATH:.
ENV SERO_REF=reference

#Run Serotyper
RUN mkdir multi_serotyper_output
CMD python2 multi_serotyper.py -i 'data'
