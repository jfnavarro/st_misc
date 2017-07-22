#! /usr/bin/env python
""" Script for merging json ST-data files.

The major point is to merge (feature, gene, expression) triples from several
json files so that (f, g, e_1) + (f, g, e_2 ) = (f, g, e_1 + e_2).
"""
import argparse
from collections import defaultdict

from st_toolbox.data import json_iterator

import cjson


def serialize(feature_gene, hits):
    doc = {}
    doc['y'], doc['x'], doc['gene'], doc['barcode'] = feature_gene
    doc['hits'] = hits
    return cjson.encode(doc)


def main(files, out):
    hits = defaultdict(int)

    for f in files:
        it = json_iterator(f)
        for doc in it:
            feature_gene = (doc['y'], doc['x'], doc['gene'], doc['barcode'])
            hits[feature_gene] += doc['hits']

    with open(out, 'w') as out_file:
        for k, v in hits.iteritems():
            out_file.write('{}\n'.format(serialize(k, v)))
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('json_files', nargs='+', type=str,
                        help='Space seperated list of json ST files to merge.')
    parser.add_argument('-o', '--out', type=str,
                        help='Name of merged output file')

    args = parser.parse_args()
    main(args.json_files, args.out)
