/*
    Copyright (C) 2013 Spatial Transcriptomics

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as
    published by the Free Software Foundation, either version 3 of the
    License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
*/

/* Contact  Jose Fernandez Navarro (jose.fernandez.navarro@scilifelab.se)
            or Mauricio Barrientos Somarribas (mauricio.barrientos@scilifelab.se)

            Original written by : Paul Costea(paul.igor.costea@scilifelab.se)
            redesigned by Mauricio Barrientos to make it work for un-aligned mates
            and extra functionalities
            

    Merges Forward and Reverse mapped files sorted by queryname.
    If -q is activated when read1 and read2 map, the highest scored will be selected.
    Otherwise, read2 will be selected.
*/

#include <stdio.h>
#include <string>
#include <iostream>
#include "sam.h"

using namespace std;

#define EXIT_IF_NULL(P) \
  if (P == NULL) \
    return 1;

/**
 * Check if read is properly mapped
 * @return true if read mapped, false otherwise
 */
static bool is_mapped(const bam1_core_t *core, int minQual=0)
{
    if ((core->flag&BAM_FUNMAP) || (core->qual < minQual)) {
        return false;
    }
    return true;
}

static int print_usage()
{
    fprintf(stderr, "\n");
    fprintf(stderr, "Program: mergeMappings \n");
    fprintf(stderr, "Contact: Mauricio Barrientos <mauricio.barrientos@scilifelab.se>\n");
    fprintf(stderr, "         Jose Fernandez <jose.fernandez.navarro@scilifelab.se>\n\n");
    fprintf(stderr, "Usage:   mergeMappings [options] <fw.bam/sam> <rw.bam/sam> <out.bam/sam>\n\n");
    fprintf(stderr, "Options:\n");
    fprintf(stderr, "     -q\t\tUse mapping qualities to chose fw or rw read when both map \n");
    fprintf(stderr, "     -f\t\tExclude unpaired forward reads\n");
    fprintf(stderr, "     -r\t\tExclude unpaired reverse reads\n");
    fprintf(stderr, "\n");
    fprintf(stderr, "Note: Files should be sorted by read name\n\n");
    return 1;

}

/**
 * Open a .sam/.bam file.
 * @returns NULL is open failed.
 */
samfile_t * open_alignment_file(std::string path, void* aux = NULL)
{
    samfile_t * fp = NULL;
    std::string flag = (aux==NULL) ? "r" : "wh";
    if (path.substr(path.size()-3).compare("bam") == 0) {
    //BAM file!
        flag += "b";
    }
    if ((fp = samopen(path.c_str(), flag.c_str() , aux)) == 0) {
        fprintf(stderr, "Failed to open file %s\n", path.c_str());
    }
    return fp;
}

/**
 * Trim the names. If they reads are from Illumina there will be a #0/1.2 in the end.
 * @returns trimmed read name.
 */
std::string trimName(std::string readName){
    readName = readName.substr(0,readName.find(' '));
    if ( readName.find ( '#' ) != std::string::npos ) //Trim this too
        readName = readName.substr ( 0,readName.find ( '#' ) );
    if ( readName.find ( '_' ) != std::string::npos ) //Trim this too from now on (_RW and _FW)
        readName = readName.substr ( 0,readName.find ( '_' ) );
    return readName;
}

void assert(bool condition, const string errormsg){
    if(!condition){
        fprintf(stderr,"%s\n",errormsg.c_str());
        exit(1);
    }
}

int main(int argc, char *argv[]){
    char arg;

    bool excludeUnpairedForward = false;
    bool excludeUnpairedReverse = false;
    bool useQualities = false;

    //Get args
    while ((arg = getopt(argc, argv, "frq")) >= 0) {
        switch (arg){
            case 'f': excludeUnpairedForward=true; break;
            case 'r': excludeUnpairedReverse=true; break;
            case 'q': useQualities = true; break;
            default: fprintf(stderr,"Wrong parameter input: %s\n",optarg); exit(1); break;
        }
    }

    if (argc-optind != 3) {
        print_usage();
        return 1;
    }
    //Index to access filename arguments
    int p = optind;

    //Statistics
    long totalOutput = 0;

    long bothEndsMapped = 0;
    long concordantEnds = 0;
    long discordantEnds = 0;
    long reverseOnlyReads= 0;
    long forwardOnlyReads = 0;
    long bothEndsUnmapped = 0;

    //Open files to read
    samfile_t *fw,*rw;
    fw = open_alignment_file(argv[p]);
    EXIT_IF_NULL(fw);
    rw = open_alignment_file(argv[p+1]);
    EXIT_IF_NULL(rw);

    //Open files to write output
    samfile_t *out = open_alignment_file(argv[p+2],fw->header);
    samfile_t *wrong = open_alignment_file("wrong.sam",fw->header);
    EXIT_IF_NULL(out);

    bam1_t *fw_entry = bam_init1();
    bam1_t *rw_entry = bam_init1();

    int statusFw = samread(fw,fw_entry);
    int statusRw = samread(rw,rw_entry);
    std::string fw_name = trimName( bam1_qname ( fw_entry ));
    std::string rw_name = trimName( bam1_qname ( rw_entry ));

    do{
        int qname_cmp = fw_name.compare ( rw_name );

        //Case 1: FW and Rv reads name match
        if(qname_cmp == 0){
            //If both ends are mapped
            if ( is_mapped ( &fw_entry->core ) && is_mapped ( &rw_entry->core ) ) {
                //Check concordancy for statistics/labeling
                //TODO: Add extra concordancy checks.
                if ( fw_entry->core.tid == rw_entry->core.tid ){
                    //int iSize = fw_entry->core.pos - rw_entry->core.pos );
                    ++concordantEnds;
                }
                else{ //Discordant pairs
                    ++discordantEnds;
                }
                 //Keep best quality read(if quality flag active) or the reverse read by default
                if(!useQualities || fw_entry->core.qual <= rw_entry->core.qual){
                    samwrite(out,rw_entry);
                }
                else{
                    samwrite(out,fw_entry);
                }
                ++totalOutput;
                ++bothEndsMapped;
            }
            else if ( is_mapped ( &fw_entry->core ) && !excludeUnpairedForward ) { // Only Fw is mapped
                ++totalOutput;
                ++forwardOnlyReads;
                samwrite ( out,fw_entry );
            }
            else if ( is_mapped ( &rw_entry->core ) && !excludeUnpairedReverse ) {//Only Rw is mapped
                ++totalOutput;
                ++reverseOnlyReads;
                samwrite ( out,rw_entry );
            }
            //None of both ends is mapped
            else if( !is_mapped ( &fw_entry->core ) && !is_mapped( &rw_entry->core )){
                samwrite(wrong,fw_entry);
                samwrite(wrong,rw_entry);
                ++bothEndsUnmapped;
            }
            //Load next reads from files
            statusFw = samread(fw,fw_entry);
            statusRw = samread(rw,rw_entry);
            if(statusFw >= 0)fw_name = trimName( bam1_qname ( fw_entry ));
            if(statusRw >= 0)rw_name = trimName( bam1_qname ( rw_entry ));
        }
        //Case 2: Only forward read is present (Reverse was removed by quality trimming)
        else if( qname_cmp < 0 ){
            if(is_mapped ( &fw_entry->core ) && !excludeUnpairedForward){
                //fw_name < rw_name
                ++totalOutput;
                ++forwardOnlyReads;
                samwrite ( out,fw_entry );
            }
            statusFw = samread(fw,fw_entry);
            if(statusFw >= 0) fw_name = trimName( bam1_qname ( fw_entry ));
        }
        //Case 3: Only reverse read is present( Forward was removed by quality trimming)
        else if(qname_cmp > 0 ){
            //rw_name < fw_name
            //The Forward read was removed by Quality Trimming. Only the reverse read remains
            if(is_mapped ( &rw_entry->core ) && !excludeUnpairedReverse){
                ++totalOutput;
                ++reverseOnlyReads;
                samwrite ( out,rw_entry );
            }
            statusRw = samread(rw,rw_entry);
            if (statusRw >= 0)
                rw_name = trimName( bam1_qname ( rw_entry ));
        }
    }while(statusFw >= 0 && statusRw >= 0);

    //If one file ended , add the rest of the other file
    if(statusFw >= 0 && !excludeUnpairedForward){
        do{
            if( is_mapped(&fw_entry->core) ){
                ++totalOutput;
                ++forwardOnlyReads;
                samwrite ( out,fw_entry );
            }
            statusFw = samread(fw,fw_entry);
            if(statusFw >=0)
                fw_name = trimName( bam1_qname ( fw_entry ));
        }while(statusFw >= 0);
    }

    if(statusRw >= 0 && !excludeUnpairedReverse){
        do{
            if( is_mapped(&rw_entry->core) ){
                ++totalOutput;
                ++reverseOnlyReads;
                samwrite ( out,rw_entry );
            }
            statusRw = samread(rw,rw_entry);
            if (statusRw>=0)
                rw_name = trimName( bam1_qname ( rw_entry ));
        }while(statusRw >= 0);
    }
    //Close all file handles
    samclose(fw);
    samclose(rw);

    samclose(out);
    samclose(wrong);

    //Print stats
    fprintf(stdout,"Mapped both ends: %ld\n",bothEndsMapped);
    fprintf(stdout,"Number of concordant mappings(ends mapped to the same chromosome): %ld\n",concordantEnds);
    fprintf(stdout,"Number of discordant mappings(ends mapped to the different chromosomes): %ld\n",discordantEnds);
    fprintf(stdout,"Forward-only reads:  %ld\n",forwardOnlyReads);
    fprintf(stdout,"Reverse-only reads:  %ld\n",reverseOnlyReads);
    fprintf(stdout,"Total mapped either fw or rw or both: %ld\n",totalOutput);
}
