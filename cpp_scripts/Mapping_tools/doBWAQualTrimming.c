/*
    qaTools - Just more qa tools.
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


/* NOTE : Updated by Jose Fernandez Navarro (jose.fernandez.navarro@scilifelab.se) */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include "include/pol_fastq.h"

static void usage()
{
  fprintf(stderr, "\nVersion: 1.4\n");
  fprintf(stderr, "Contact: Paul Costea <paul.igor.costea@scilifelab.se>\n\n");
  fprintf(stderr, "Usage: ");
  fprintf(stderr, "doBWAQualTrimming [Options] <in.fastq> <out.fastq>\n");
  fprintf(stderr, "Options:\n");
  fprintf(stderr, "         -p            Input is a paierd library\n");
  fprintf(stderr, "                       Use: doBWAQualTrimming [Options] <in1.fastq> <in2.fastq> <out1.fastq> <out2.fastq>\n");
  fprintf(stderr, "         -s            Use phred33 based qualities (default phred64)\n");
  fprintf(stderr, "         -v            Write discarded sequences\n");
  fprintf(stderr, "         -f            Replace discarded sequences with N's\n");
  fprintf(stderr, "         -n [Char]     Only remove 'Char' nucleotides from sequence ['N']. -q will be ignored.\n");
  fprintf(stderr, "         -q [INT]      Quality threshold [20]\n");
  fprintf(stderr, "         -l [INT]      Lenght cutoff [54]\n\n");
}

int main(int argc, char* argv[])
{
  char arg;
  int qual = 20;
  int min_length = 54;
  char nucleotide_remove = 'N';
  bool onlyN = false;
  bool isPairedLib = false;
  bool writeDropped = false;
  bool isSolexa = false;
  bool replaceWithFake = false;
  //Get args
  while ((arg = getopt(argc, argv, "q:l:psfvn")) >= 0) {
    switch (arg) {
    case 'q': qual = atoi(optarg); break;
    case 'l': min_length = atoi(optarg); break;
    case 'p': isPairedLib = true; break;
    case 'n': nucleotide_remove = (char)*optarg;onlyN = true; break;
    case 'v': writeDropped = true; break;
    case 's': isSolexa = true; break;
    case 'f': replaceWithFake = true; break;
    default: fprintf(stderr,"Wrong parameter input: %s\n",optarg); break;
    }
  }

  if (argc-optind != ((isPairedLib) ? 4 : 2)) {
    usage();
    return 1;
  }

  int p = optind;

  FILE* fast_q1 = fopen(argv[p],"r");
  if (fast_q1 == NULL) {
    printf("Cannot open file %s\n", argv[p]);
    return 1;
  }
  p++;
  FILE* fast_q2 = NULL;
  if (isPairedLib) {
    fast_q2 = fopen(argv[p],"r");
    if (fast_q2 == NULL) {
      printf("Cannot open file %s\n", argv[p]);
      return 1;
    }
    p++;
  }
  FILE* fast_q_out1 = fopen(argv[p],"w");
  if (fast_q_out1 == NULL) {
    printf("Cannot create output file %s\n", argv[p]);
    return 1;
  }
  p++;

  FILE* drop1 = NULL;
  FILE* drop2 = NULL;

  FILE* fast_q_out2 = NULL;
  if (isPairedLib) {
    fast_q_out2 = fopen(argv[p],"w");
    if (fast_q_out2 == NULL) {
      printf("Cannot create output file %s\n", argv[p]);
    }
  }

  if (writeDropped) {//Open files for writing dropped reads
    if (isPairedLib) {
      drop1 = fopen("dropped1.out","w");
      drop2 = fopen("dropped2.out","w");
    } else {
      drop1 = fopen("dropped.out","w");
    }
  }

  long dropped_fw = 0;
  long dropped_rw = 0;
  long count = 0;

  pol_util::FastqEntry* entry1 = NULL;
  pol_util::FastqEntry* entry2 = NULL;
  
  while (true) { //assumes fw and rw same number of reads

    ++count;
    entry1 = pol_util::FastqEntry::readEntry(fast_q1);
    if (isPairedLib) entry2 = pol_util::FastqEntry::readEntry(fast_q2);
    
    if ((entry1 == NULL) || (isPairedLib && entry2 == NULL)) break; //finishes when either fw or rw reaches ends

    if (onlyN == true) {
      bool rem1,rem2;
      rem1 = entry1->removePoly(nucleotide_remove,min_length);
      if(!rem1){
          ++dropped_fw;
          if (writeDropped) entry1->write(drop1);
          delete entry1;
          entry1 = NULL;
      }
      if (isPairedLib){
          rem2 = entry2->removePoly(nucleotide_remove,min_length);
          if(!rem2){
              ++dropped_rw;
              if(writeDropped) entry2->write(drop1);
              delete entry2;
              entry2 = NULL;
          }
      }
      
    }else {
      bool trim1,trim2;
      trim1 = entry1->trim(qual,min_length,isSolexa);
      if (!trim1) { //drop fw
            ++dropped_fw;
            if (writeDropped) entry1->write(drop1);
            if (replaceWithFake) entry1->writeFake(fast_q_out1);
            delete entry1;
            entry1 = NULL;
      }
      if (isPairedLib) {
          trim2 = entry2->trim(qual,min_length,isSolexa);
          if (!trim2) { //drop rw
              ++dropped_rw;
              if (writeDropped) entry2->write(drop2);
              if (replaceWithFake) entry2->writeFake(fast_q_out2);
              delete entry2;
              entry2 = NULL;
          }
      }
    }

    //Write them to the output files if they have not been dropped.
    if(entry1 != NULL){
        entry1->write(fast_q_out1);
        entry1 = NULL;
    }
    if (isPairedLib && entry2 != NULL){
        entry2->write(fast_q_out2);
        delete entry2;
        entry2 = NULL;
    }
  }

  fclose(fast_q1);
  fclose(fast_q_out1);
  if (isPairedLib) {
    fclose(fast_q2);
    fclose(fast_q_out2);
  }
  if (writeDropped) {
    fclose(drop1);
    if (isPairedLib) fclose(drop2);
  }

  if(isPairedLib){
      printf("\n");
      printf("%ld reads have been dropped on the forward read!\n",dropped_fw);
      printf("You just lost about %3.2f procent of your data on the forward read!\n",(double(dropped_fw)/count)*100);
      printf("%ld reads have been dropped on the reverse read!\n",dropped_rw);
      printf("You just lost about %3.2f procent of your data on the reverse read!\n",(double(dropped_rw)/count)*100);
  }
  else{
      printf("\n");
      printf("%ld reads have been dropped!\n",dropped_fw);
      printf("You just lost about %3.2f procent of your data!\n",(double(dropped_fw)/count)*100);     
  }

}