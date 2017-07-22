
class Predictions
{
	unsigned long long int NofSeqs_setGC;

public:
	unsigned long int PredictStartingNofSeqs(void);
	unsigned long int partialfactorial(unsigned int,unsigned int);
	unsigned long int combination(unsigned int,unsigned int);
	double CalculateNofDiffSeqsat1ED(int);
	double CalculateNofDiffSeqs(void);
	unsigned long long int CalculateNofAllPairs(unsigned long int);
	double CalcuateNofUniqueEdges(unsigned long int);
	unsigned long int CalculateUniqueNofNodes(unsigned long int);	
};


unsigned long int Predictions::partialfactorial(unsigned int n,unsigned int r){

	unsigned int i=0;
	unsigned long int factorial;

	factorial=1;
	if(r==0){
		for(i=n;i>0;--i)
			factorial*=i;
		return factorial;
	}
	else{
		for(i=n;i>r;--i)
		factorial*=i;
	}

	return factorial;
}
unsigned long int Predictions::combination(unsigned int n, unsigned int r){

	unsigned long int comb,diff; //combination
	diff=n-r;
	if((n-r)>r){
		comb=partialfactorial(n,(n-r));
		if(r==0)
			return comb;
		else
			comb/=partialfactorial(r,0);
	}
	else{
		comb=partialfactorial(n,r);
		comb/=partialfactorial((n-r),0);
	}
	return comb;
}
double Predictions::CalculateNofDiffSeqsat1ED(int editdistance){

	double x;

	x=combination(SeqLen,editdistance)*(pow(0.75,editdistance))*(pow(0.25,(SeqLen-editdistance)));
	
	return x;
}

double Predictions::CalculateNofDiffSeqs(void){

	double sumx=0;
	unsigned int i=0;

	for(i=0;i<EditDistanceThreshold;i++)
		sumx+=CalculateNofDiffSeqsat1ED(i);



	return sumx;

}

unsigned long long int Predictions::CalculateNofAllPairs(unsigned long int nofnodes)
{
unsigned long long int nofedges=0;

nofedges=combination(nofnodes,2);

return nofedges;

}
double Predictions::CalcuateNofUniqueEdges(unsigned long int NofPutBarcodes)
{
	double nofuniqueedges=0;

	nofuniqueedges=CalculateNofAllPairs(NofPutBarcodes);
	nofuniqueedges*=CalculateNofDiffSeqs();

	nofuniqueedges*=NofPutBarcodes;

	return nofuniqueedges;
}
unsigned long int Predictions::CalculateUniqueNofNodes(unsigned long NofPutBarcodes)
{
	unsigned long long int nofuniqueedges=0;
	double a=1, b=-1,c,d=0,x1=0,x2=0;
	c=CalcuateNofUniqueEdges(NofPutBarcodes);
	c=c/(-2);
	d=(b*b)-(4*a*c);
	x1=(-1*b-(sqrt(d)))/(2*a);
	x2=(-1*b+(sqrt(d)))/(2*a);

	return x2;
}



unsigned long int Predictions::PredictStartingNofSeqs(){

	unsigned long int uniquesize;
	double startsize,size,fold=2.0,increment=0.5;

	startsize=DesiredNofBarcodes*fold;
	size=startsize;
	do{
		uniquesize=CalculateUniqueNofNodes(size);
		fold+=increment;
		size=fold*startsize;
	}while(uniquesize<=DesiredNofBarcodes);
		
	return size;
}
