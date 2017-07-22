#include <stdio.h>
#include <iostream>
#include <stdlib.h>
#include <string.h>
#include <string>
#include <list>
#include <vector>
#include <time.h>

#ifdef __APPLE__
//  #include <tr1/unordered_map>
//  using namespace std::tr1;
  #include "boost/unordered_map.hpp"
#else
//  #include <unordered_map>
  #include <boost/unordered_map.hpp>
#endif

#include "boost/lexical_cast.hpp"

#include <pthread.h>
#include "pol_fastq.h"

static int print_usage()
{
	fprintf(stderr, "\n");
	fprintf(stderr, "Program: findIndexes \n");
	fprintf(stderr, "Core Developer Paul, then modified by Pelin Akan <pelin.akan@scilifelab.se> and final changes by Zinat Sultana\n\n");
	fprintf(stderr, "findIndexeWpairEnd keeps the pair reads,findout the barcode and writes the barcodes and x,y coordinates in the optional line in forward fastq file.");
	fprintf(stderr, "Usage:   findIndexWpairEnd [options] <ids.txt> <in.fastq> <reverse.fastq> <outPair.fastq> <out.fastq> <statistics.txt>\n\n");
	fprintf(stderr, "Options: \n");
	fprintf(stderr, "         -m INT     allowed mismatches [2]\n");
	fprintf(stderr, "         -k INT     kMer length [1/3*length]\n");
	fprintf(stderr, "         -s INT     start position of ID [0]\n");
	fprintf(stderr, "         -l INT     length of ID [0]\n");
	fprintf(stderr, "         -e INT     id positional error [0]\n");
	fprintf(stderr, "\n");
	return 1;
}

/*
 * Structure for ID definition. May be augmented with additional information.
 */

typedef struct{
  int  x,y;

}Location;
class IdStruct {
public:
	IdStruct() {
	};

	IdStruct(const IdStruct &other) {
		id = other.id;
		loc = other.loc;
};
        Location loc;
	std::string id;

};

int probeDeletions;
int probeInsertions;
long int count = 0;
long int perfectMatch = 0;
long int hasPolyTAferID = 0;
long int hasPolyTFurtherDown = 0;
long int hasManyPolyT = 0;
long int hasManyPolyA = 0;
long int hasPolyAAfterID = 0;
long int totalReads = 0;

long int ambiguous = 0;
long int editDistanceTooBig = 0;

//Parameter
int mismatch = 2;
int kLen = 8;
int probeStartPos = 0;
int probeLength = 18;
int positionalError = 0;

int qualMin = 1000;
int qualMax = 0;

std::string pairFile=" ";

pthread_mutex_t readMutex = PTHREAD_MUTEX_INITIALIZER;
pthread_mutex_t writeMutex = PTHREAD_MUTEX_INITIALIZER;
pthread_mutex_t countersMutex = PTHREAD_MUTEX_INITIALIZER;

#define GUARDED_INC(x) \
		pthread_mutex_lock(&countersMutex); \
		++x; \
		pthread_mutex_unlock(&countersMutex);

/////////////////Hash declaration//////////////////////
//std::unordered_map<std::string,Location> mainIds_map;
//std::unordered_map<std::string,std::list<IdStruct>> kIds_map;

boost::unordered_map<std::string,Location> mainIds_map;
boost::unordered_map<std::string,std::list<IdStruct> > kIds_map;
///////////////////////////////////////////////////////

#define MATRIX_X 700
#define MATRIX_Y 700

int posMatrix[MATRIX_X][MATRIX_Y];
int perfectMatchMatrix[MATRIX_X][MATRIX_Y];
int uniqueIdMatrix[MATRIX_X][MATRIX_Y];
int scoreDistr[1000];

bool loadIds(FILE* snpFile, boost::unordered_map<std::string,Location>& map /*std::unordered_map<std::string,Location>& map*/ , int mat [][MATRIX_Y])
{
	char line[100000];
	char *tok = new char[10000];
	for (int i=0; i<10000; ++i)
		tok[i]='\0';
        int unique =0;
	while (fgets(line,100000,snpFile)) {
		//Replace new line with \0
		//line[strlen(line)-1] = '\0';
                ++unique;
		const char *t = line;
		int pos = 0;
		std::string id = "";
                Location p;
		p.x=-1;p.y=-1;
		while (*t) {
			t = pol_util::toksplit(t, '\t', tok, 10000);
			if (pos == 0) {//ID
				id= tok;
			}
			else if (pos == 1) {//x                               
			  p.x=atoi( tok);
                        }
			else if (pos == 2) {//y                           
                                                                           
                          p.y = atoi(tok);
                        }
                        ++pos;
		}
			mat[p.x][p.y] =unique; 
			map[id]=p;
		}		

	
	delete[] tok;

return true;
}

/*
 * Edit distance computation
 */
//int editDistance(unsigned int **d, std::string s1, std::string s2, std::string qual="", int* alignScore=NULL, int maxDist=1000)
int editDistance(std::string s1, std::string s2, std::string qual="", int* alignScore=NULL, int maxDist=1000)
{
	int xLen = s1.size();
	int yLen = s2.size();
        unsigned int **d = new unsigned int*[xLen+1];

	//if (d == NULL) {
		//The matrix given has not been initialized
	//	fprintf(stdout,"Null computation matrix!\n");
	//	return NULL;
	//}
        for (int i=0;i<=xLen;++i) {                                                                                                                                                
	  d[i] = new unsigned int[yLen+1];                                                                                                                                   
        }                                                                                                                                                                          
        d[0][0] = 0;                                                                                                                                                               
        for(int x = 1; x <= xLen; ++x) d[x][0] = 0;                                                                                                                                
        for(int x = 1; x <= yLen; ++x) d[0][x] = x; 

	for(int x = 1; x <= xLen; ++x)
		for(int y = 1; y <= yLen; ++y) {
		  if(qual[x-1]>qualMax){
		    qualMax = qual[x-1];}
                  else if(qual[x-1]<qualMin){
                    qualMin = qual[x-1];}
			d[x][y] = std::min( std::min(d[x - 1][y] + 1,d[x][y - 1] + 1),d[x - 1][y - 1] + (s1[x - 1] == s2[y - 1] ? 0 : 1) );
		}

	//Find min for sub-global alignment
	int min = 1000;
	int iPos = 0;
	for (int i=xLen;i>1/*xLen-extraBases-2*/;--i) {
		if (d[i][yLen] < min) {
			min = d[i][yLen];
			iPos = i;
		}
	}

	if ((alignScore != NULL) && (min <= maxDist)){//Do traceback
		//Compute score!
		*alignScore = 0;

		int i = iPos;
		int j = yLen;

		while ((i > 0) && (j > 0))
		{
			int Score = d[i][j];
			int ScoreDiag = d[i - 1][j - 1];
			int ScoreUp = d[i][j - 1];
			int ScoreLeft = d[i - 1][j];
			if (Score == ScoreDiag + (s1[i-1] == s2[j-1] ? 0 : 1))
			{
				if (s1[i-1] != s2[j-1])
					*alignScore -= qual[i-1]-33;
				else
					*alignScore += qual[i-1]-33;
				i = i - 1;
				j = j - 1;
			}
			else if (Score == ScoreLeft + 1)
			{
				//Add deletion score
				*alignScore -= 100;
				i = i - 1;
			}
			else if (Score == ScoreUp + 1)
			{
				//Add insertions score
				*alignScore -= 100;
				j = j - 1;
			}
		}
		
	       
	}
	for (int i =0;i<=xLen;++i){
	  delete [] d[i];
       }
	delete [] d;
	//Fake
        *alignScore = 0;

	return min;
}

void createKmerMap(int kLen)
{
	//std::unordered_map<std::string,Location>::const_iterator it;
	boost::unordered_map<std::string,Location>::const_iterator it;
	for (it = mainIds_map.begin(); it != mainIds_map.end(); ++it) {//For each, introduce only part of it into the new map!
		for (unsigned int i=0; i<=(it->first.size()-kLen); ++i) {
			std::string newKey = it->first.substr(i,kLen);
			IdStruct idS;
			idS.id = it->first;
			idS.loc = it->second;
			kIds_map[newKey].push_back(idS);
		}
	}

}

typedef struct {
  FILE *inFile,*outFile,*pairFile,*pairFileOut;
} threadArgs;

/**
 * Thread entry
 */
void* idSearch(void* arguments)
{
// 	std::unordered_map<std::string,Location>::iterator it;
// 	std::unordered_map<std::string,int> kMerHitMap;
	boost::unordered_map<std::string,Location>::iterator it;
	boost::unordered_map<std::string,int> kMerHitMap;
	//Get longer sequence!!!!
	/*
        int leftShift = (probeStartPos-positionalError >= 0)? positionalError : 0;
	int rightShift = positionalError;
	int maxKmerHits = (probeLength+rightShift) + (leftShift);
	std::list<std::string>* orderedIds = new std::list<std::string>[maxKmerHits+1];

	//create matrix for alignment
	int xLen = probeLength+rightShift+leftShift;
	int yLen = probeLength;

	unsigned int **d = new unsigned int*[xLen+1];
	for (int i=0;i<=xLen;++i) {
		d[i] = new unsigned int[yLen+1];
	}
	d[0][0] = 0;
	for(int x = 1; x <= xLen; ++x) d[x][0] = 0;
	for(int x = 1; x <= yLen; ++x) d[0][x] = x;
        */
	pol_util::FastqEntry* e,*e1;
        e1 = NULL;
	threadArgs args = *(threadArgs*)arguments;
	while (true) {
		//Lock file mutex
		pthread_mutex_lock(&readMutex);
		e = pol_util::FastqEntry::readEntry(args.inFile);
		if(args.pairFile!=NULL )
		  e1 = pol_util::FastqEntry::readEntry(args.pairFile);
		pthread_mutex_unlock(&readMutex);
		if (e == NULL)
			break;
		int pos = probeStartPos+probeLength;
		bool has_seq = true;
		if (has_seq) {
			GUARDED_INC(totalReads)
			std::string id = e->getSequence(pos-probeLength,pos);
			std::string qual = e->getQuality(pos-probeLength,pos);
			//Search ID in map!
			it = mainIds_map.find(id);			
			if (it != mainIds_map.end()) {//Found!
                     
			  GUARDED_INC(count)
			  GUARDED_INC(perfectMatch)
			    int tempP = 0;
			  bool hasT = pol_util::find_substring(e->getSequence(18,39),"TTTTTTTTTTTTTTTTTTTT",tempP,8);
			  if (hasT) {
			    //hasT = (e->getSequence(pos+20,pos+21).compare("T")==0) ? false : true ;                                                                  
			  }
			  bool hasManyT = pol_util::find_substring(e->getSequence(39,59),"TTTTTTTTTTTTTTTTTTTT",tempP,5);
			  bool hasManyA = pol_util::find_substring(e->getSequence(39,59),"AAAAAAAAAAAAAAAAAAAA",tempP,5);
			  bool hasA = pol_util::find_substring(e->getSequence(18,49),"AAAAAAAAAAAAAAAAAAAA",tempP,3);
			  if (hasT && !hasManyT) {
			    GUARDED_INC(hasPolyTAferID)
			      } else if (hasT && hasManyT) {
			    GUARDED_INC(hasManyPolyT)
			      } else if (hasManyT) {
			    GUARDED_INC(hasPolyTFurtherDown)
			      }
			  if (hasA) {
			    GUARDED_INC(hasPolyAAfterID)
			      }
			  if (hasManyA) {
			    GUARDED_INC(hasManyPolyA)
			      }
			  GUARDED_INC(posMatrix[it->second.x][it->second.y]);
			  GUARDED_INC(perfectMatchMatrix[it->second.x][it->second.y]);
			    //Print this to output Map
				if (args.outFile != NULL) {
                                  long double xx,yy;
                                  xx = it->second.x;
				  
				  std::string sx= boost::lexical_cast<std::string>(xx);
				  
				  yy = it->second.y;

				  std::string sy= boost::lexical_cast<std::string>(yy);
				  				  				  
				  e->setOptional("barcode="+id); // Print the Barcode
				  e->setOptional("\t"+sx); //Print x coord
				  e->setOptional("\t"+sy); // Print y coord
				  //std::cout<<"\n"<<id<<"\t"<<it->second.x<<"\t"<<it->second.y;
					pthread_mutex_lock(&writeMutex);
					e->write(args.outFile);
					if (e1!=NULL)
					   e1->write(args.pairFileOut);
					pthread_mutex_unlock(&writeMutex);
				}
			} else {//Probably with mismatch!
				//////////////////////////////////////////////////////////////////////////
				////////////////////////////Do kmer search////////////////////////////////
                                //Get longer sequence!!!!                                                                                                                                                  
			                                                                                                                                                              
                                int leftShift = (probeStartPos-2 >= 0)? 2: 0;                                                                                                 
                                int rightShift = 2;
				id = e->getSequence(probeStartPos-leftShift,probeStartPos+probeLength+rightShift);
				qual = e->getQuality(probeStartPos-leftShift,probeStartPos+probeLength+rightShift);

// 				std::unordered_map<std::string,std::list<IdStruct>>::iterator splitIt;
				boost::unordered_map<std::string,std::list<IdStruct> >::iterator splitIt;
				std::list<IdStruct>::const_iterator it;
// 				std::unordered_map<std::string,int>::iterator kIt;
				boost::unordered_map<std::string,int>::iterator kIt;
                                int x =0;
				//for (int displace=0; displace <= leftShift; ++displace) {
				//int x = displace;
					bool forced = false;
					while ( (x <= id.size()-kLen) && (!forced)) {
						std::string id1 = id.substr(x,kLen);
						splitIt = kIds_map.find(id1);
						if (splitIt != kIds_map.end()) {
							//Add to counted map
							std::list<IdStruct>* l = &(splitIt->second);
							for (it = l->begin(); it != l->end(); ++it) {
								std::string locId = it->id;
								kIt = kMerHitMap.find(locId);
								if (kIt != kMerHitMap.end()) {
									kMerHitMap[locId]+=1;
								} else {//Add
									kMerHitMap[locId]=1;
								}
							}
						}
						//Make sure we get the last overlapping k-mer
						x+=kLen;

						if (x > id.size()-kLen) {
							x = id.size()-kLen;
							forced = true;
						}
					}
				

				///////////////////////////////////////////////////////////////////////////
				//////////////////////////////////////////////////////////////////////////
				bool goodHit = false;
				int min_ed = 1000;
				int max_score = 0;
				std::string found_id = "";
                                Location l;
				l.x=0;l.y=0;
				//Go through map and find maximum.
                                int maxKmerHits = (probeLength + rightShift)-leftShift;
				std::list<std::string>* orderedIds = new std::list<std::string>[maxKmerHits];
				//Order hits
				for (kIt = kMerHitMap.begin(); kIt != kMerHitMap.end(); ++kIt) {
					orderedIds[kIt->second].push_back(kIt->first);
				}
				int goOn = 0;
				int score = 0;
				int searching = 0;
				//Take only first x most kMer containing Id's
				for (int i=maxKmerHits-1;i>=0;--i) {
					if (orderedIds[i].size() != 0 && (goOn <= 5) ) {//This is the list of most hits
						for (std::list<std::string>::const_iterator it=orderedIds[i].begin(); it != orderedIds[i].end(); ++it) {
							double ed = editDistance(id,(*it),qual,&score,mismatch);
							++searching;
							if (ed < min_ed) {//New min
								min_ed = ed;
								max_score = score;
								goodHit = true;
								found_id = (*it);
                                                                l=mainIds_map[found_id];
							} else if (ed == min_ed) {//Two with same min :(
								//Discriminate by score!
								if (score == max_score) {
									goodHit = false;
									goOn = 0;
								} else if (score > max_score) {
									goodHit = true;
									max_score = score;
									found_id = (*it);
									l=mainIds_map[found_id];
								}
							}
						}
						++goOn;
					}
					orderedIds[i].clear();
				}

				if (goodHit && min_ed<= mismatch) {
					//We have a "best" hit!
				  GUARDED_INC(count)
				  GUARDED_INC(scoreDistr[score])
				    int tempP = 0;
				  bool hasT = pol_util::find_substring(e->getSequence(18,39),"TTTTTTTTTTTTTTTTTTTT",tempP,8);
				  bool hasManyT = pol_util::find_substring(e->getSequence(39,59),"TTTTTTTTTTTTTTTTTTTT",tempP,3);
				  bool hasManyA = pol_util::find_substring(e->getSequence(39,59),"AAAAAAAAAAAAAAAAAAAA",tempP,5);
				  bool hasA = pol_util::find_substring(e->getSequence(18,49),"AAAAAAAAAAAAAAAAAAAA",tempP,3);
				  if (hasT && !hasManyT) {
				    GUARDED_INC(hasPolyTAferID)
				      } else if (hasT && hasManyT) {
				    GUARDED_INC(hasManyPolyT)
				      } else if (hasManyT) {
				    GUARDED_INC(hasPolyTFurtherDown)
				      }
				  if (hasA) {
				    GUARDED_INC(hasPolyAAfterID)
				      }

				  if (hasManyA) {
				    GUARDED_INC(hasManyPolyA)
				      }

				  GUARDED_INC(posMatrix[l.x][l.y])
					if (args.outFile != NULL) {
					  long double xx,yy;
					  xx = l.x;
					  std::string sx= boost::lexical_cast<std::string>(xx);
					  
					  yy = l.y;

					  std::string sy= boost::lexical_cast<std::string>(yy);
					  
					  e->setOptional("barcode="+found_id);
					  e->setOptional("\t"+sx);
                                          e->setOptional("\t"+sy);
						
					  //std::cout<<"\n"<<id<<"\t"<<l.x<<"\t"<<l.y;
						pthread_mutex_lock(&writeMutex);
						e->write(args.outFile);
						if(e1!=NULL)

						   e1->write(args.pairFileOut);
						  
                                                pthread_mutex_unlock(&writeMutex);
					}
				} else {
					//Still print this!
					pthread_mutex_lock(&writeMutex);
					e->write(args.outFile);
					if(e1!=NULL)
					  e1->write(args.pairFileOut);
					pthread_mutex_unlock(&writeMutex);
					if (!goodHit) {
					  GUARDED_INC(ambiguous);
					} else {
					  GUARDED_INC(editDistanceTooBig);
					}
				}
				delete [] orderedIds;

				kMerHitMap.clear();

			}
		}
		delete e;
                if (e1 != NULL)
		  delete e1;
	}

	
	return NULL;
}

/**
 * Main of app
 */
int main(int argc, char *argv[])
{

  probeDeletions = 0;
  probeInsertions = 0;

  for (int i=0; i<MATRIX_X; ++i)
    for (int j=0; j<MATRIX_Y; ++j){
      posMatrix[i][j]=0;
      uniqueIdMatrix[i][j]=0;
      perfectMatchMatrix[i][j]=0;
    }
	int arg;
	//Get args
	while ((arg = getopt(argc, argv, "m:k:s:l:e:")) >= 0) {
		switch (arg) {
		case 'm': mismatch = atoi(optarg); break;
		case 'k': kLen = atoi(optarg);
		break;
		case 's': probeStartPos = atoi(optarg); break;
		case 'l':
			probeLength = atoi(optarg);
			if (kLen == 0) {//If not otherwise set
				kLen = probeLength / 3;
			}
			break;
		case 'e': positionalError = atoi(optarg); break;
		  //case 'p': pairFile = optarg; break;  
		default:
			fprintf(stderr,"Read wrong arguments! \n");
			break;
		}
	}

	if (argc-optind != 6) {
		//Not enough paramters!
		print_usage();
		return 1;
	}
	if (probeLength <= 0) {
		fprintf(stderr,"You must input the length of the ID\n");
		return 1;
	}
	//Seed rand
	srand((unsigned)time(0));
	//Open files!
	FILE *ids,*inF,*pairF,*pairFOut,*statFile;
	pairF = NULL;
	pairFOut = NULL;  
	FILE *out = NULL;//indexed forward fastq file
	if ((ids = fopen(argv[optind], "r")) == 0) {
		fprintf(stderr, "Failed to open file %s\n", argv[optind]);
		return 1;
	}
	if ((inF = fopen(argv[optind+1], "r")) == 0) {
		fprintf(stderr, "Failed to open file %s\n", argv[optind+1]);
		return 1;
	}
        
       if ((pairF = fopen(argv[optind+2], "r")) == 0) {
	  fprintf(stderr, "Failed to open file %s\n", argv[optind+2]);
	  return 1;
        }

	if ((pairFOut = fopen(argv[optind+3], "w")) == 0) {
          fprintf(stderr, "Failed to open file %s\n", argv[optind+3]);
          return 1;
        }

        if ((out = fopen(argv[optind+4], "w")) == 0) {
	  fprintf(stderr, "Failed to open for writing: %s\n", argv[optind+4]);
	  return 1;
        }

        if ((statFile = fopen(argv[optind+5], "w")) == 0) {
          fprintf(stderr, "Failed to open for writing: %s\n", argv[optind+5]);
          return 1;
        }

	

	//Load IDS!
	loadIds(ids,mainIds_map,uniqueIdMatrix);
	//Create kMer map
	createKmerMap(kLen);
	pthread_t threadList[8];
	threadArgs args;
	args.inFile = inF;
	args.outFile = out;

	args.pairFile = pairF;
	args.pairFileOut = pairFOut;

	/*DO THREAD STUFF*/
	for (int i=0; i<8; ++i) {
		pthread_create( &threadList[i], NULL, idSearch, (void*) &args);
	}
	//Now join them...
	for (int i=0; i<8; ++i) {
		pthread_join(threadList[i],NULL);
	}
        
	fprintf(stdout,"\nFound: %ld\n",count);
	fprintf(stdout, "Perfect match: %ld\n",perfectMatch);
	fprintf(stdout, "Ambiguous ID's: %ld\n",ambiguous);
	fprintf(stdout, "Edit distance exceeding limit: %ld\n",editDistanceTooBig);
	fprintf(stdout, "Total reads: %ld\n",totalReads);
        
        fprintf(statFile, "Total ID found: %ld",count);
        fprintf(statFile, "\nPerfect match ID's: %ld",perfectMatch);
        fprintf(statFile, "\nAmbiguous ID's: %ld",ambiguous);
        fprintf(statFile, "\nEdit distance exceeding limit: %ld",editDistanceTooBig);
        fprintf(statFile, "\nTotal reads: %ld",totalReads);
        
        fclose(statFile);
	fclose(ids);
	fclose(inF);
	if (out != NULL)
	  fclose(out);
        if (pairF != NULL)
	  fclose(pairF);
	if (pairFOut!= NULL)
	  fclose(pairFOut);

	return 0;
}


