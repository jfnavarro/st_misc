import sys
import numpy
import os

def usage():
    print "Usage:"
    print "python countCoughtTranscripts.py mapped_with_gene.txt"

def getAllMappedReads(mapWithGeneFile):
    nameToGene = dict()
    exonHit = dict()
    exonGeneDict = dict()
    utrHit = dict()
    GeneDict = dict()
    c = 0
    total = 0
    inF = open(mapWithGeneFile,'r')
    insertSize = []
    for line in inF:
        cols = line.rstrip().split('\t')
        start = int(cols[1])
        end = int(cols[2])
        if cols[18] != '.':
            #print "Gene: " + cols[18]
            total += 1
            isThere = False
            if '@'+cols[3] in nameToGene:
                isThere = True
            nameToGene['@'+cols[3]] = cols[18]
            if cols[18] in GeneDict:
                if not isThere:
                    GeneDict[cols[18]] += 1
            else:
                if not isThere:
                    GeneDict[cols[18]] = 1
            #Is it actually exonic?
            gStart = int(cols[10])
            gEnd = int(cols[11])
            starts = cols[15].split(',')
            ends = cols[16].split(',')
            #Check if UTR hit!
            #5'
            overlap_5 = max(0, min(end, int(starts[0])) - max(start, int(gStart)))
            #3'
            overlap_3 = max(0, min(end, int(gEnd)) - max(start, int(ends[-1-1])))
            if overlap_5 > 0 or overlap_3 > 0:
                utrHit['@'+cols[3]] = 'Yes'
            else:
                for i in range(len(starts)-1):
                    overlap = max(0, min(end, int(ends[i])) - max(start, int(starts[i])))   
                    if overlap > 0:
                        if cols[18] in exonGeneDict:
                            exonGeneDict[cols[18]] += 1
                        else:
                            exonGeneDict[cols[18]] = 1
                        intronLen = 0;
                        if i != 0 and i != len(starts)-2:
                            if gEnd-end < start-gStart:
                                #Closer to the right!
                                for j in range(len(starts)-2,i,-1):
                                    intronLen += int(starts[j])-int(ends[j-1])
                            else:
                                #Closer to the left
                                for j in range(i):
                                    intronLen += int(starts[j+1])-int(ends[j])
                        dist = min(gEnd-end,start-gStart)-intronLen
                        if '@'+cols[3] in exonHit:
                            exonHit['@'+cols[3]] = min(dist,exonHit['@'+cols[3]])
                        else:
                            exonHit['@'+cols[3]] = dist
                        
    inF.close()
    print "Total hitting exon: " + str(len(exonHit.keys()))
    for k in exonHit.keys():
        insertSize.append(exonHit[k])
    #    print k +" " +str(exonHit[k])
    print "Mean distance to end of gene: " + str(numpy.mean(insertSize))
    print "Median distance to end of gene: " + str(numpy.median(insertSize))
    print "Total hitting UTR's: " + str(len(utrHit.keys()))
    genesOut = open("exon_genes.out","w")
    for k in exonGeneDict.keys():
        genesOut.write("%s\t%d\n"%(k,exonGeneDict[k]))
    genesOut.close()
    allgenesOut = open("all_genes.out","w")
    for k in GeneDict.keys():
        allgenesOut.write("%s\t%d\n"%(k,GeneDict[k]))
    allgenesOut.close()
    print "Total different genes: " + str(len(GeneDict.keys()))
    print "Total diff genes hit on exon: " +str(len(exonGeneDict.keys()))
    return nameToGene

def main(mapWithGene):
    #Find all mapped!
    nameToGene = getAllMappedReads(mapWithGene)
    print "Total hits: " + str(len(nameToGene.keys()))
    
if __name__ == "__main__":
    #Should have two inputs.
    if len(sys.argv) != 2:
        usage()
        sys.exit(1)
    main(sys.argv[1])
                                
