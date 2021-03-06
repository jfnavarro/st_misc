/* 
    join - Parallel genomic region joining tool.
    Copyright (C) 2012  P. Costea(paul.igor.costea@scilifelab.se)

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as
    published by the Free Software Foundation, either version 3 of the
    License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of 
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.                  

    For a copy of the GNU Affero General Public License
    see <http://www.gnu.org/licenses/>.
*/


#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <vector>
#include <map>
#include <string>
#include <omp.h>
#include <time.h>


//TODO getopt() seems to not work in OSX, default values are a bad yet quick workaround
//TODO openmp seems to not work in OSX, neither, unactivating for APPLE is a bad yet quick workaround
//NOTE Fixed to be run on MAC OSX : Jose Fernandez Navarro <jose.fernandez.navarro@scilifelab.se>

//#define DEBUG

using namespace std;

typedef struct value {
  int iStart,iEnd;
}position;

typedef struct colDef {
  int chr,start,end;
}columnDef;

#define max(a,b) (((a) > (b)) ? (a) : (b))
#define min(a,b) (((a) < (b)) ? (a) : (b))

/**                                                                                                                                                                                                                                        
 * @brief Proper tokanizer!                                                                                                                                                                                                                
 */
const char *toksplit(
		     const char *src, /* Source of tokens */
		     char tokchar, /* token delimiting char */
		     char *token, /* receiver of parsed token */
		     size_t lgh) /* length token can receive */
{
  if (src) {
    while (' ' == *src) *src++;
    while (*src && (tokchar != *src)) {
      if (lgh) {
	*token++ = *src;
	--lgh;
      }
      ++src;
    }
    if (*src && (tokchar == *src)) ++src;
  }
  *token = '\0';
  return src;
}

class CRecord{
 public:
  /**
   ** @brief Null constructor
   */
  CRecord()
    :chr(NULL)
    ,coherent(false) {};

  /**
   ** @brief Copy constructor
   */
  CRecord(const CRecord& r) {
    start = r.start;
    end = r.end;
    chr = new char[strlen(r.chr)];
    coherent = r.coherent;
    strcpy(chr,r.chr);
  }
  
  /**
   ** @brief Proper constructor
   */
  CRecord(const char* line, columnDef colDef)
    :chr(NULL)
    ,coherent(false)
    {
      if (line == NULL) {
	fprintf(stderr,"Bad pointer\n");
	return;
      }
    const char *t = line;
    char *tok = new char[1000];
    int pos = 0;
    int found = 0;
    while (*t) {
      t = toksplit(t,'\t',tok,1000);
      if (colDef.chr == pos) {
	chr = new char[strlen(tok)+1];
	strcpy(chr,tok);
	++found;
      } else if (colDef.start == pos) {
	start = atoi(tok);
	++found;
      } else if (colDef.end == pos) {
	end = atoi(tok);
	++found;
      }
      if (found == 3) {
	coherent = true;
	break;
      }
      ++pos;
    }
    if (start > end) {//This should be a properly formatted interval
      fprintf(stderr,"Sorry...wrong interval formation!\nSwapping start %d and end %d\n",start,end);
      //Switch them!
      int tmp = start;
      start = end;
      end = tmp;
    }
    delete[] tok;

  };

  ~CRecord() {
    delete[] chr;
  };


  int overlap(const CRecord *other) const{    
    if (strcmp(chr,other->chr) != 0)
      return 0;
    else
      return max(0, min(end, other->end)) - max(start, other->start);
  };

  char* chr;
  int start;
  int end;
  bool coherent;
};

static int print_usage()
{
  fprintf(stderr, "\n");
  fprintf(stderr, "Program: join \n");
  fprintf(stderr, "Contact: Paul Costea <paul.igor.costea@scilifelab.se>\n\n");
  fprintf(stderr, "Usage:   join <in1.txt> <in2.txt> <output.out> -1 N,N,N -2 N,N,N -e\n");
  fprintf(stderr, "         N,N,N = chr_Column, start, end \n");
  fprintf(stderr, "Option:  e      Only print out one match\n");
  fprintf(stderr, "Note:    N,N,N are all 0 based\n");
  fprintf(stderr, "         'in2' must have a header line. If 'in2' is chromosome sorted, joining will be a lot faster\n");
  return 0;
}

#define LINE_MAX_ 500000

int main(int argc, char* argv[])
{
  if (argc < 8) {
    print_usage();
    return -1;
  }

  string inFile1,inFile2,output;
  columnDef col1;
  columnDef col2;

#ifdef __APPLE__
  /* defaul values */

  col1.chr = 0;
  col1.start = 1;
  col1.end = 2;

  col2.chr = 2;
  col2.start = 4;
  col2.end = 5;

#endif
  
  inFile1 = argv[1];
  inFile2 = argv[2];
  output = argv[3];
  
  int arg;
  bool writeOnlyOne = false;
  char* tok;
  string parameters = ":1:2:e";
  
  //Get arguments
  while ((arg = getopt(argc, argv, parameters.c_str())) != -1) {
    
    switch(arg) {
        case '1':
            printf("Reading parameter -1 %s \n",optarg);
            tok = strtok(optarg,",");
            col1.chr = atoi(tok);
            tok = strtok(NULL,",");
            col1.start = atoi(tok);
            tok = strtok(NULL,",");
            col1.end = atoi(tok);
            break;
        case '2':
            printf("Reading parameter -2 %s \n",optarg);
            tok = strtok(optarg,",");
            col2.chr = atoi(tok);
            tok = strtok(NULL,",");
            col2.start = atoi(tok);
            tok = strtok(NULL,",");
            col2.end = atoi(tok);
            break;
        case 'e':
            writeOnlyOne = true;
            break;
        case ':':
            printf("Missing operand for %c\n", optopt);
            break;
        case '?':
            printf("Unknown option %c\n", optopt);
            print_usage();
            break;
    }
  }
  
#ifdef DEBUG
  printf("Arguments\n%s\n%s\n%s\n%i\n%i\n%i\n%i\n%i\n%i\n",
         inFile1.c_str(),inFile2.c_str(),output.c_str(),col1.chr,col1.start,col1.end,col2.chr,col2.start,col2.end);
#endif
  
  //Open files
  FILE *in1 = fopen(inFile1.c_str(),"r");
  if (in1 == NULL) {
    printf("Unable to open file %s\n", inFile1.c_str());
    return -1;
  }
  FILE* in2 = fopen(inFile2.c_str(),"rb");
  if (in2 == NULL) {
    printf("Unable to open file %s\n", inFile2.c_str());
    return -1;
  }
  FILE *out = fopen(output.c_str(),"w");
  if (out == NULL) {
    printf("Unable to create output file %s\n", output.c_str());
    return -1;
  }

  char line1[LINE_MAX_],line2[LINE_MAX_];

  char fail[1000]=".";
  fseek(in2,0,SEEK_END);
  long lSize = ftell(in2);
  rewind(in2);
  //Determine nr of columns in 2'nd file from file header
  //HEADER IS A MUST!
  fgets(line2,LINE_MAX_,in2);
  lSize -= strlen(line2);
  tok = strtok(line2,"\t");
  tok = strtok(NULL,"\t");
  while (tok != NULL) {
    strcat(fail,"\t.");
    tok = strtok(NULL,"\t");
  }

#ifdef DEBUG
  clock_t tStart,tEnd;
  tStart = clock();
#endif
  //Read second file into memory!
  std::vector <char*> file2;
  //Do fast read
  char* buffer = new char[lSize];
  if (buffer == NULL) {
    fprintf(stderr,"Unable to allocate needed memory. Need about %d bytes\n",lSize);
    return -1;
  }
  //Read all of it!
  long res = fread(buffer,1,lSize,in2);
  if (res != lSize) {
    fprintf(stderr,"Reading error!\n");
    return -1;
  }
  fclose(in2);
  
  map <std::string,position> chrMap;

  std::string chr = "";
  //Assume file is packed
  bool isPacked = true;

  position pos;
  bool hasStart = false;
  tok = strtok(buffer,"\n");
  //Split from buffer!
  while (tok != NULL) {
    file2.push_back(tok);
    if (isPacked) {
      CRecord* rec = new CRecord(tok,col2);
      if (!rec->coherent) {
	fprintf(stderr,"Chr,Start and End positions seem to be wrong in \n%s\n!\nCannot continue\n",tok);
	return (-1);
      }
      string c(rec->chr);
      if (c != chr) {
	if (!hasStart){
	  pos.iStart = file2.size()-1;
	  chr = c;
	  hasStart = true;
	} else {
	  pos.iEnd = file2.size()-1;
#ifdef DEBUG
	  printf("Adding %s\n",chr.c_str());
#endif
	  if (chrMap.find(chr) != chrMap.end()) {
	    //This isn't packed! Forget this optimization
	    isPacked = false;
	    fprintf(stdout,"%s\n",chr.c_str());
	  }
	  chrMap.insert(std::pair<string,position>(chr,pos));
	  chr = c;
	  pos.iStart = file2.size()-1;
	}
	delete rec;
      }
    }
    tok = strtok(NULL,"\n");
  }
#ifdef DEBUG
  tEnd = clock();
  double diff = double(tEnd-tStart)/CLOCKS_PER_SEC;
  fprintf(stdout,"It took %3.2f sec to read second file\n",diff);
#endif

  if (isPacked) {
    pos.iEnd = file2.size();
    chrMap.insert(std::pair<string,position>(chr,pos));
  } else {
    fprintf(stdout,"Consider sorting the file you are joining with by chromosome!\n");
  }
#ifdef DEBUG
  printf("Done 1\n");
#endif
  position all;
  all.iStart = 0;
  all.iEnd = file2.size();
  int chrMissCount = 0;
  int total = 0;
#ifndef __APPLE__
    #pragma omp parallel shared(in1,total,chrMissCount,chrMap,file2,out) private(line1)
#endif
  {
    while (true) {
      void *ret = NULL;
#ifndef __APPLE__
      #pragma omp critical
#endif
      ret = fgets(line1,LINE_MAX_,in1);

      if (ret == NULL)
        break;

      if (line1[0] == '#') {
        //This is either a header of a commented line, skip!
        continue;
      }
      
      int sP,eP;
      std::string outBuffer = "";
      CRecord* rec = new CRecord(&line1[0],col1);
      if (!rec->coherent) {
        fprintf(stderr,"Wrong position definitions\nGiving up...\n");
        break;
      }
      char final[2*LINE_MAX_] = "";
      //Remove \n from line1
      line1[strlen(line1)-1] = '\0';
      strcat(final,line1);
      strcat(final,"\t");
      bool found = false;
#ifndef __APPLE__
      #pragma omp critical
#endif
      ++total;
      map<string,position>::iterator iter;
      iter = chrMap.find(rec->chr);
      if ((iter != chrMap.end()) || (!isPacked)) {
        position pos = (isPacked) ? iter->second : all;
        int it;
        bool done = false;
        sP = pos.iStart;
        eP = pos.iEnd;
        for(it=sP; it<eP; ++it)
        {
	  if (!done) {
	    CRecord *rec2 = new CRecord(file2[it],col2);
	    if (rec->overlap(rec2) > 0) {
	      found = true;
	      outBuffer += final;
	      outBuffer += file2[it];
	      outBuffer += '\n';
	      {
	        if (writeOnlyOne) 
		  done = true;
	      }
	    }
	    //Cleanup
	    delete rec2;
	  }
        }
        if (!found) {
	
	  strcat(final,fail);
	  strcat(final,"\n");
#ifndef __APPLE__
	  #pragma omp critical
#endif
	  fputs(final,out);
        } else {//Dump buffer
#ifndef __ALPPLE__
	  #pragma omp critical
#endif
	  fputs(outBuffer.c_str(),out);
        }
      } else {//Chromosome not present!
        //Still write it out thought
        strcat(final,fail);
        strcat(final,"\n");
        fputs(final,out);
        ++chrMissCount;
      }
#ifdef DEBUG
      printf("Done: %s, %d, %d\n",rec->chr,rec->start,rec->end);
#endif
      delete rec;
    
    }
  }
  
  if (chrMissCount != 0)
    fprintf(stdout,"Missed %d out of %d because chromosome name did not match!\nMake sure the two files you are joining have the same chr name definitions\n",chrMissCount,total);
  fclose(in1);
  delete[] buffer;
  fclose(out);
  return 0;
}
