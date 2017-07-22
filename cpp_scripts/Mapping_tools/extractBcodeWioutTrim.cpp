#include <iostream>
#include <stdlib.h>
#include <unistd.h>
#include<stdio.h>

#include <iostream>
#include<string.h>
using namespace std;



//merge two fastq files

static int print_usage()
{
  fprintf(stderr,"\n");
  fprintf(stderr,"Program: merge \n");
  fprintf(stderr,"Contact: zinat@scilifelab.se>\n\n");
  fprintf(stderr, "Usage: <fw_with_indexes.fastq> <rw_paired.fastq> <fw_WithBarcode.fastq> <fw_NoBarcode.fastq> <rw_pairedForbcode.fastq> <rw_NoBarcode.fastq> <Stat.txt>\n");
  return 1;
}

int main (int argc, char * const argv[]) {
    
	
	FILE *fw_IndFile, *rw_PairFile, *fw_WBFile, *fw_NBFile, *rw_WBFile, *rw_NBFile, *stFile;
	
	char rw_string [1000];
	char fw_string [1000];
	char rw_str[1000];
	char fw_str[1000];
	
	char header_fw[53];
	char sequence_fw[151];
	char optional_fw[38];
	char quality_fw[151];
	
	char header_rw[53];
	char sequence_rw[151];
	char optional_rw[38];
	char quality_rw[151];
	
	int  numberofBar =0;
	int len_fw, len_rw;
	
	int TRIM_FW =0;
	int TRIM_RW = 0;
	
	int f_trm,r_trm,arg;
	
	while ((arg = getopt(argc, argv, "f:r")) >= 0) {
	  switch (arg) {
	  case 'f': f_trm = atoi(optarg); break;
	  case 'r': r_trm = atoi(optarg); break;

	  default:
	    fprintf(stderr,"Read wrong arguments! \n");
	    break;
	  }
	}
	
	if (argc-optind != 7) {
	  //Not enough paramters!
	  print_usage();
	  return 1;
	}
	
		
	fw_IndFile = fopen(argv[optind], "r"); 
		
	if ((rw_PairFile = fopen(argv[optind+1], "r")) == 0) {
	  fprintf(stderr, "Failed to open for writing: %s\n", argv[optind+1]);
		return 1;
	}
	if ((fw_WBFile = fopen(argv[optind+2], "w")) == 0) {
		fprintf(stderr, "Failed to open File %s\n", argv[optind+2]);
		return 1;
	}
	if ((fw_NBFile = fopen(argv[optind+3], "w")) == 0) {
		fprintf(stderr, "Failed to open for writing: %s\n", argv[optind+3]);
		return 1;
	}
	if ((rw_WBFile = fopen(argv[optind+4], "w")) == 0) {
		fprintf(stderr, "Failed to open File %s\n", argv[optind+4]);
		return 1;
	}
	if ((rw_NBFile = fopen(argv[optind+5], "w")) == 0) {
		fprintf(stderr, "Failed to open for writing: %s\n", argv[optind+5]);
		return 1;
	}
	
	if ((stFile = fopen(argv[optind+6], "w")) == 0) {
		fprintf(stderr, "Failed to open for writing: %s\n", argv[optind+6]);
		return 1;
	}
	
	int line_number = 0;
	int wi=0,no=0;
	
	while( fgets (fw_string	,153, fw_IndFile) != NULL )
	{	
		strcpy(fw_str,fw_string);
		
		
		fgets (rw_string ,153, rw_PairFile);
		
		strcpy(rw_str,rw_string);
				
		
		fw_string[strlen(fw_string)-1] = '\0';
		len_fw =strlen(fw_string);
		
		rw_string[strlen(rw_string)-1] = '\0';
		len_rw =strlen(rw_string);
		
		/* header */
		if(line_number%4==0)
		{   int i;
			for(i=0;i<len_fw;i++)
				header_fw[i]=fw_string[i];	
			
			for(i=0;i<len_rw;i++)
				header_rw[i]=rw_string[i];  }	
		
		/*Sequence */

		if(line_number%4==1)
		{   int i,j=0;
			int d = len_fw-TRIM_FW;
			for(i=0;i<d;i++){
				sequence_fw[i]=fw_string[TRIM_FW+j];	
				j++;
			    }
			
			
			int k=0;
			int r =len_rw-TRIM_RW;
			for(i=0;i<r ;i++){
				sequence_rw[i]=rw_string[k+TRIM_RW];k++;}
						
		}
		
		/*Optional*/

		if(line_number%4==2)
		{
			int i;
			for(i=0;i<len_fw;i++)
				optional_fw[i]=fw_string[i];	
			
			for(i=0;i<len_rw;i++)
				optional_rw[i]=rw_string[i];
						
		}
		
		/*Quality */

		if(line_number%4==3)
		{
			int i,j=0;
			int d = len_fw-TRIM_FW;
			for(i=0;i<d;i++){
				quality_fw[i]=fw_str[ j + TRIM_FW];
				j++;}
			
			int m=0;
			int r = len_rw-TRIM_RW;
			for(i=0;i<r;i++){
				quality_rw[i]=rw_str[ m + TRIM_RW];
				
			
				m++;
			}}
		
			
		    // now check if there is any barcode
		
		if (line_number%4==3)
		{
			 if(strlen(optional_fw)>30)	
				
			 {   //forward read saving
				numberofBar++;
				fwrite(header_fw,   strlen(header_fw), 1, fw_WBFile);
				fprintf(fw_WBFile, "\n");
				
				fwrite(sequence_fw, strlen(sequence_fw), 1, fw_WBFile);
				fprintf(fw_WBFile, "\n");
				
				fwrite(optional_fw,    strlen(optional_fw), 1, fw_WBFile);
				fprintf(fw_WBFile, "\n");
				
				fwrite(quality_fw,  strlen(quality_fw), 1, fw_WBFile);
				fprintf(fw_WBFile, "\n");
				
				//reverse read saving
				fwrite(header_rw,   strlen(header_rw), 1, rw_WBFile);
				fprintf(rw_WBFile, "\n");
				
				fwrite(sequence_rw, strlen(sequence_rw), 1, rw_WBFile);
				fprintf(rw_WBFile, "\n");
				
				fwrite(optional_rw,    strlen(optional_rw), 1, rw_WBFile);
				fprintf(rw_WBFile, "\n");
				
				fwrite(quality_rw,  strlen(quality_rw), 1, rw_WBFile);
				fprintf(rw_WBFile, "\n");
				
				
			   }
			
			else if(strlen(optional_fw)==1){
				//reads having no barcodes
				//forward read saving
				wi=wi+1;
				
				fwrite(header_fw,   strlen(header_fw), 1, fw_NBFile);
				fprintf(fw_NBFile, "\n");
				
				fwrite(sequence_fw, strlen(sequence_fw), 1, fw_NBFile);
				fprintf(fw_NBFile, "\n");
				
				fwrite(optional_fw,    strlen(optional_fw), 1, fw_NBFile);
				fprintf(fw_NBFile, "\n");
				
				fwrite(quality_fw,  strlen(quality_fw), 1, fw_NBFile);
				fprintf(fw_NBFile, "\n");
				
				
				//reverse read saving
				fwrite(header_rw,   strlen(header_rw), 1, rw_NBFile);
				fprintf(rw_NBFile, "\n");
				
				fwrite(sequence_rw, strlen(sequence_rw), 1, rw_NBFile);
				fprintf(rw_NBFile, "\n");
				
				fwrite(optional_rw,    strlen(optional_rw), 1, rw_NBFile);
				fprintf(rw_NBFile, "\n");
				
				fwrite(quality_rw,  strlen(quality_rw), 1, rw_NBFile);
				fprintf(rw_NBFile, "\n");
			}
			else { 
                              no++;
			      cout << "no"<<no;
			}

			
		
			
		
		//clear all temporay memory
		int k;
		for(k=0; k<151; k++) {
			sequence_rw[k] ='\0';}
			
			for(k=0; k<126; k++){	
			quality_rw[k]  = '\0';  
		}
		
		for(k=0; k<151; k++) {
		  sequence_fw[k] ='\0';}
			for(k=0; k<91; k++) {
			
			quality_fw[k]  = '\0';  
		}
		
		for(k=0; k<38; k++) {
			optional_fw[k]='\0'; 
			optional_rw[k]='\0';
		}
		
		for(k=0; k<53; k++) {
			header_fw[k]='\0';	
			header_rw[k]='\0';
		}
		}// end of line3  
		
		
				
		line_number++;
		
	}//end of reading files
	
	//cout <<"Barcodes with reads:"<< numberofBar;
	
	//cout << "\n"<<line_number/4<< "\n";
	//cout << "read with no narcodes"<<wi;
        
        int total_reads,reads_withoutBarcode;
        float perc;
	total_reads= line_number/4;
        perc = ((float)numberofBar*100.00)/(float)total_reads;
        reads_withoutBarcode = total_reads-numberofBar;

	fprintf(stFile,"\nTotal read=%d",total_reads);
	fprintf(stFile,"\nTotal read with Barcode = %d (%f percent)",numberofBar,perc);
        
        perc = ((float)reads_withoutBarcode*100.00)/(float)total_reads;
	fprintf(stFile,"\nTotal read without Barcode = %d (%f percent)",reads_withoutBarcode,perc);
	
        /*
	fclose(fw_IndFile);
	fclose(rw_PairFile);
	fclose(fw_WBFile);
	fclose(fw_NBFile);
	fclose(rw_WBFile);
	fclose(rw_NBFile);
	fclose(stFile);*/
	
	
	
    return 0;
}
