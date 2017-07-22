#! /usr/bin/env python
""" Script for merging json ST-data files.

It splits a json file containing barcodes into two (the one with ambiguous genes and the one without them)
it allows to use a cut off of number of reads per transcript
"""
import argparse
from collections import defaultdict

from st_toolbox.data import json_iterator

import cjson


def serialize(feature):
    doc = {}
    doc['y'], doc['x'], doc['gene'], doc['barcode'], doc['hits'] = feature
    return cjson.encode(doc)


def main(file, out_ambigous, out, cutoff):
    
    hits = defaultdict(int)
    hitsambigous = defaultdict(int)
    
    total_hits = 0
    total_hits_ambiguous = 0
    
    total_barcodes = 0
    total_barcodes_ambiguous = 0
    
    unique_barcodes = set()
    unique_genes = set()
    unique_barcodes_ambiguous = set()
    unique_genes_ambiguous = set()
    
    features = list()
    features_ambiguous = list()
    
    it = json_iterator(file)
    
    for doc in it:
        
        feature_gene = (doc['y'], doc['x'], doc['gene'], doc['barcode'], doc['hits'])
        
        if(int(doc['hits']) < int(cutoff)):
            continue
        
        total_barcodes +=1
        total_hits += int(doc['hits'])
        unique_genes.add(str(doc['gene']))
        unique_barcodes.add(str(doc['barcode']))
        
        if(doc['gene'].find("ambiguous") == -1):
            features.append(feature_gene)
        else:
            total_barcodes_ambiguous +=1
            total_hits_ambiguous += int(doc['hits'])
            unique_genes_ambiguous.add(str(doc['gene']))
            unique_barcodes_ambiguous.add(str(doc['barcode']))
            features_ambiguous.append(feature_gene)
            
    with open(out, 'w') as out_file:
        for feature in features:
            out_file.write('{}\n'.format(serialize(feature)))

    with open(out_ambigous, 'w') as out_file:
        for feature_ambiguous in features_ambiguous:
            out_file.write('{}\n'.format(serialize(feature_ambiguous)))
    
    print "Total reads mapping to barcodes " + str(total_hits)
    print "Total barcodes " + str(total_barcodes)
    print "Total unique barcodes " + str(len(unique_barcodes))
    print "Total unique genes " + str(len(unique_genes))
    
    print "Total reads mapping to barcodes with ambiguous genes " + str(total_hits_ambiguous)
    print "Total barcodes with ambiguous genes " + str(total_barcodes_ambiguous)
    print "Total unique barcodes with ambiguous genes " + str(len(unique_barcodes_ambiguous))
    print "Total unique ambiguous genes " + str(len(unique_genes_ambiguous))  

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('json_file', type=str,
                        help='Json file with barcodes to be splitted.')
    parser.add_argument('--out_ambiguous', type=str,
                        help='Name of the outfile for barcodes with ambigous genes')
    parser.add_argument('--out', type=str,
                        help='Name of the outfile for barcodes with no ambigous genes')
    parser.add_argument('--cutoff', type=int,
                        help='Cut off of number of transcripts to filter',default=1)

    args = parser.parse_args()
    main(args.json_file, args.out_ambiguous, args.out, args.cutoff)
