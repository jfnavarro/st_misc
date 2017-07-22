/*
    filter - Just more qa tools.
    Copyright (C) 2011  P. Costea(paul.igor.costea@scilifelab.se)

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

#include <stdio.h>
#include <string>
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
    fprintf(stderr, "Program: filterMappings \n");
    fprintf(stderr, "Contact: Paul Costea <CosteaPaul@gmail.com>\n\n");
    fprintf(stderr, "Usage:   filterMappings [options] <paired.bam/sam> <out.bam/sam>\n\n");
    fprintf(stderr, "Options: --- none ---\n");
    fprintf(stderr, "\n");
    fprintf(stderr, "Note: Files should have the same number of entries on the same positions.!\n\n");
    return 1;
}

/**
 * Open a .sam/.bam file.
 * @returns NULL is open failed.
 */
samfile_t * open_alignment_file(std::string path, void* aux = NULL)
{
  samfile_t * fp = NULL;
  std::string flag = (aux==NULL) ? "r" : "w";
  if (path.substr(path.size()-3).compare("bam") == 0) {
    //BAM file!
    flag += "b";
  } else {
    flag += "h"; //Force write header!
  }
  if ((fp = samopen(path.c_str(), flag.c_str() , aux)) == 0) {
    fprintf(stderr, "Failed to open file %s\n", path.c_str());
  }
  return fp;
}

int main(int argc, char *argv[])
{
    samfile_t *pair;
    samfile_t *out;

    long possibleBadMappings = 0;
    long bothEndsMapped = 0;

    if (argc != 3) {
      print_usage();
      //Give up
      return 1;
    }

    pair = open_alignment_file(argv[1]);
    EXIT_IF_NULL(pair);

	//Keep header of forward mapping.
    out = open_alignment_file(argv[2],pair->header);
    samfile_t *wrong = open_alignment_file("wrong.sam",pair->header);
    EXIT_IF_NULL(out);

    bam1_t *fw_entry = bam_init1();
    bam1_t *rw_entry = bam_init1();

    while (samread(pair,fw_entry) >= 0) {
      int res = samread(pair,rw_entry);
      if (res < 0) {//This can't be good!
    	  fprintf(stderr,"Encountered premature end of file!\n");
    	  return -1;
      }
		std::string fw_name = bam1_qname(fw_entry);
		std::string rw_name = bam1_qname(rw_entry);
		//Trim the names. If they are illumina, there will be a #0/1.2 in the end
		fw_name = fw_name.substr(0,fw_name.find(' '));
		rw_name = rw_name.substr(0,rw_name.find(' '));
		if (fw_name.find('#') != std::string::npos) {//Trim this too
		  fw_name = fw_name.substr(0,fw_name.find('#'));
		  rw_name = rw_name.substr(0,rw_name.find('#'));
		}
		if ( fw_name.compare(rw_name) != 0 ) {
			fprintf(stderr,"Wrong alignment in file!\n");
			fprintf(stderr,"%s\n%s\n",fw_name.c_str(),rw_name.c_str());
			return -1;
		}
		if (is_mapped(&fw_entry->core) && is_mapped(&rw_entry->core)) {//Both ends have mapped
			//Are both mapped on the same chromosome?
			if (fw_entry->core.tid != rw_entry->core.tid) {
			  samwrite(wrong,fw_entry);
			  samwrite(wrong,rw_entry);
			  ++possibleBadMappings;
			} else {
				//Kepp forward, but compute insert size!
				int iSize = abs(fw_entry->core.pos - rw_entry->core.pos);
				fw_entry->core.isize = iSize;
				++bothEndsMapped;
				samwrite(out,fw_entry);
			}
		} else if (is_mapped(&fw_entry->core)) {
			//Just print it
			samwrite(out,fw_entry);
		} else if (is_mapped(&rw_entry->core)) {
			samwrite(out,rw_entry);
		}
	}
	samclose(out);
	samclose(pair);
	fprintf(stdout,"Number of possible bad mappings: %ld\n",possibleBadMappings);
	fprintf(stdout,"Mapped both ends: %ld\n",bothEndsMapped);
}
